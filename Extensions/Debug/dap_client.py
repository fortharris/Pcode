"""Minimal Debug Adapter Protocol client for debugpy (attach / wait-for-client)."""

from __future__ import annotations

import json
import logging

from PyQt6.QtCore import QByteArray, QObject, QTimer, pyqtSignal
from PyQt6.QtNetwork import QAbstractSocket, QTcpSocket


class DapClient(QObject):
    """Async DAP client using QTcpSocket (Qt event loop)."""

    statusChanged = pyqtSignal(str)
    stopped = pyqtSignal(str, int)  # path, line (1-based)
    continued = pyqtSignal()
    terminated = pyqtSignal()
    failed = pyqtSignal(str)
    ready = pyqtSignal()  # configurationDone acknowledged; session live

    def __init__(self, parent=None):
        super().__init__(parent)
        self._socket = QTcpSocket(self)
        self._socket.readyRead.connect(self._on_ready_read)
        self._socket.errorOccurred.connect(self._on_socket_error)
        self._socket.connected.connect(self._on_connected)
        self._socket.disconnected.connect(self._on_disconnected)

        self._buffer = QByteArray()
        self._seq = 0
        self._pending = {}
        self._breakpoints = {}  # path -> [1-based lines]
        self._thread_id = None
        self._phase = "idle"
        self._host = "127.0.0.1"
        self._port = 5678
        self._connect_attempts = 0
        self._connect_timer = QTimer(self)
        self._connect_timer.setSingleShot(True)
        self._connect_timer.timeout.connect(self._try_connect)

    @property
    def is_active(self):
        return self._phase not in ("idle",)
    def start(self, host, port, breakpoints):
        """Connect and run the late-case DAP handshake with debugpy."""
        self.stop()
        self._host = host
        self._port = int(port)
        self._breakpoints = {
            path: sorted(set(int(line) for line in lines if int(line) > 0))
            for path, lines in (breakpoints or {}).items()
            if lines
        }
        self._phase = "connecting"
        self._connect_attempts = 0
        self.statusChanged.emit("Debug: connecting…")
        self._try_connect()

    def stop(self):
        self._connect_timer.stop()
        self._phase = "idle"
        self._pending.clear()
        self._buffer.clear()
        self._thread_id = None
        if self._socket.state() != QAbstractSocket.SocketState.UnconnectedState:
            if self._socket.state() == QAbstractSocket.SocketState.ConnectedState:
                try:
                    self._send_request("disconnect", {
                        "restart": False,
                        "terminateDebuggee": True,
                    })
                except Exception:
                    pass
            self._socket.disconnectFromHost()
            if self._socket.state() != QAbstractSocket.SocketState.UnconnectedState:
                self._socket.abort()

    def continue_(self):
        if self._thread_id is None:
            return
        self._send_request("continue", {"threadId": self._thread_id})

    def step_over(self):
        if self._thread_id is None:
            return
        self._send_request("next", {"threadId": self._thread_id})

    def step_into(self):
        if self._thread_id is None:
            return
        self._send_request("stepIn", {"threadId": self._thread_id})

    def step_out(self):
        if self._thread_id is None:
            return
        self._send_request("stepOut", {"threadId": self._thread_id})

    # --- connection ---------------------------------------------------------

    def _try_connect(self):
        if self._phase != "connecting":
            return
        self._connect_attempts += 1
        if self._connect_attempts > 40:
            self._phase = "idle"
            self.failed.emit(
                "Could not connect to debugpy on {0}:{1}".format(
                    self._host, self._port))
            return
        if self._socket.state() != QAbstractSocket.SocketState.UnconnectedState:
            self._socket.abort()
        self._socket.connectToHost(self._host, self._port)

    def _on_connected(self):
        self._phase = "initialize"
        self.statusChanged.emit("Debug: initializing…")
        self._send_request("initialize", {
            "clientID": "pcode",
            "clientName": "Pcode",
            "adapterID": "python",
            "pathFormat": "path",
            "linesStartAt1": True,
            "columnsStartAt1": True,
            "supportsVariableType": False,
            "supportsVariablePaging": False,
            "supportsRunInTerminalRequest": False,
        })

    def _on_disconnected(self):
        if self._phase not in ("idle",):
            self._phase = "idle"
            self.terminated.emit()
            self.statusChanged.emit("")

    def _on_socket_error(self, _error):
        if self._phase == "connecting":
            self._connect_timer.start(250)
            return
        if self._phase != "idle":
            msg = self._socket.errorString()
            logging.debug("DAP socket error: %s", msg)
            self.failed.emit(msg)

    # --- framing ------------------------------------------------------------

    def _next_seq(self):
        self._seq += 1
        return self._seq

    def _send_request(self, command, arguments=None):
        seq = self._next_seq()
        message = {
            "seq": seq,
            "type": "request",
            "command": command,
        }
        if arguments is not None:
            message["arguments"] = arguments
        self._pending[seq] = command
        self._write_message(message)
        return seq

    def _write_message(self, message):
        body = json.dumps(message).encode("utf-8")
        header = "Content-Length: {0}\r\n\r\n".format(len(body)).encode("ascii")
        self._socket.write(header + body)
        self._socket.flush()

    def _on_ready_read(self):
        self._buffer.append(self._socket.readAll())
        while True:
            message = self._read_one_message()
            if message is None:
                break
            self._dispatch(message)

    def _read_one_message(self):
        data = bytes(self._buffer)
        sep = data.find(b"\r\n\r\n")
        if sep < 0:
            return None
        header = data[:sep].decode("ascii", errors="replace")
        length = None
        for line in header.split("\r\n"):
            if line.lower().startswith("content-length:"):
                try:
                    length = int(line.split(":", 1)[1].strip())
                except ValueError:
                    length = None
        if length is None:
            self._buffer.remove(0, sep + 4)
            return None
        total = sep + 4 + length
        if len(data) < total:
            return None
        body = data[sep + 4:total]
        self._buffer.remove(0, total)
        try:
            return json.loads(body.decode("utf-8"))
        except Exception:
            logging.debug("Invalid DAP JSON", exc_info=True)
            return None

    # --- dispatch -----------------------------------------------------------

    def _dispatch(self, message):
        mtype = message.get("type")
        if mtype == "response":
            self._handle_response(message)
        elif mtype == "event":
            self._handle_event(message)
        elif mtype == "request":
            # Reverse requests (e.g. runInTerminal) — decline politely.
            self._write_message({
                "seq": self._next_seq(),
                "type": "response",
                "request_seq": message.get("seq"),
                "success": False,
                "command": message.get("command"),
                "message": "not supported",
            })

    def _handle_response(self, message):
        command = self._pending.pop(message.get("request_seq"), message.get("command"))
        if not message.get("success", False):
            err = message.get("message") or "DAP {0} failed".format(command)
            if command in ("initialize", "attach", "configurationDone"):
                self.failed.emit(err)
            else:
                logging.debug("DAP response error (%s): %s", command, err)
            return

        if command == "initialize":
            self._phase = "attach"
            self._send_request("attach", {
                "name": "Pcode",
                "type": "python",
                "request": "attach",
                "justMyCode": True,
                "host": self._host,
                "port": self._port,
            })
        elif command == "attach":
            # Wait for initialized event before setBreakpoints.
            self._phase = "await_initialized"
        elif command == "setBreakpoints":
            pass
        elif command == "configurationDone":
            self._phase = "running"
            self.statusChanged.emit("Debug: running")
            self.ready.emit()
        elif command == "stackTrace":
            self._handle_stack_trace(message.get("body") or {})
        elif command == "continue":
            self.continued.emit()
            self.statusChanged.emit("Debug: running")

    def _handle_event(self, message):
        event = message.get("event")
        body = message.get("body") or {}
        if event == "initialized":
            self._phase = "configure"
            self.statusChanged.emit("Debug: setting breakpoints…")
            self._send_all_breakpoints()
            self._send_request("configurationDone", {})
        elif event == "stopped":
            self._thread_id = body.get("threadId")
            reason = body.get("reason") or "stopped"
            self.statusChanged.emit("Debug: {0}".format(reason))
            if self._thread_id is not None:
                self._send_request("stackTrace", {
                    "threadId": self._thread_id,
                    "startFrame": 0,
                    "levels": 1,
                })
        elif event == "continued":
            self.continued.emit()
            self.statusChanged.emit("Debug: running")
        elif event in ("terminated", "exited"):
            self._phase = "idle"
            self.terminated.emit()
            self.statusChanged.emit("")
        elif event == "output":
            logging.debug("DAP output: %s", body.get("output", ""))

    def _send_all_breakpoints(self):
        if not self._breakpoints:
            # Still need an empty setBreakpoints for the main file? optional.
            return
        for path, lines in self._breakpoints.items():
            self._send_request("setBreakpoints", {
                "source": {"path": path},
                "breakpoints": [{"line": line} for line in lines],
            })

    def _handle_stack_trace(self, body):
        frames = body.get("stackFrames") or []
        if not frames:
            return
        frame = frames[0]
        source = frame.get("source") or {}
        path = source.get("path") or ""
        line = int(frame.get("line") or 0)
        if path and line > 0:
            self.stopped.emit(path, line)
