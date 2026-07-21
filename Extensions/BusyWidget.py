from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QProgressBar, QPushButton, QVBoxLayout,
)

from Extensions import StyleSheet


class BusyWidget(QDialog):
    """Non-blocking busy overlay. Prefer Cancel for long jobs."""

    cancel = pyqtSignal()

    def __init__(self, app, useData, parent=None):
        QDialog.__init__(self, parent, Qt.WindowType.Window
                         | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setAccessibleName("Busy indicator")

        self.setFixedSize(280, 72)

        self.app = app
        self.useData = useData
        self._cancel_enabled = False

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        self.mainLabel = QLabel()
        mainLayout.addWidget(self.mainLabel)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(12, 10, 12, 10)
        vbox.setSpacing(8)
        self.mainLabel.setLayout(vbox)

        self.captionLabel = QLabel()
        self.captionLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.captionLabel.setWordWrap(True)
        vbox.addWidget(self.captionLabel)

        self.progressBar = QProgressBar()
        self.progressBar.setMaximumHeight(14)
        self.progressBar.setTextVisible(False)
        self.progressBar.setRange(0, 0)
        vbox.addWidget(self.progressBar)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setAccessibleName("Cancel busy operation")
        self.cancelButton.clicked.connect(self.stop)
        hbox.addWidget(self.cancelButton)
        hbox.addStretch(1)

        self._escape = QShortcut(QKeySequence("Esc"), self)
        self._escape.activated.connect(self._on_escape)

        self._apply_theme()

    def _apply_theme(self):
        p = StyleSheet.CURRENT_PALETTE
        self.mainLabel.setStyleSheet(
            "background: {bg}; border: 1px solid {border}; "
            "border-radius: 4px;".format(
                bg=p.get("busyBg", p["panel"]),
                border=p.get("busyBorder", p["border"])))
        self.captionLabel.setStyleSheet(
            "color: {text}; background: none; border: none;".format(
                text=p.get("busyText", p["text"])))
        self.progressBar.setStyleSheet(
            """
            QProgressBar {{
                border: 1px solid {border};
                text-align: center;
                padding: 1px;
                border-radius: 2px;
                background-color: {inputBg};
            }}
            QProgressBar::chunk {{
                border-radius: 2px;
                background-color: {accent};
            }}
            """.format(
                border=p["border"], inputBg=p["inputBg"], accent=p["accent"]))
        self.cancelButton.setStyleSheet(
            """
            QPushButton {{
                color: {buttonText};
                background: {button};
                border-radius: 2px;
                border: 1px solid {border};
                padding: 4px 12px;
            }}
            QPushButton:hover {{
                background: {buttonHover};
            }}
            QPushButton:pressed {{
                background: {buttonPressed};
            }}
            """.format(
                buttonText=p["buttonText"], button=p["button"],
                border=p["border"], buttonHover=p["buttonHover"],
                buttonPressed=p["buttonPressed"]))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._on_escape()
            return
        QDialog.keyPressEvent(self, event)

    def _on_escape(self):
        if self._cancel_enabled and self.isVisible():
            self.stop()

    def stop(self):
        self.cancel.emit()

    def showBusy(self, show, mess=None, enableCancel=False):
        if show:
            self._apply_theme()
            self.progressBar.setRange(0, 0)
            self.captionLabel.setText(mess or "Please wait\u2026")
            self._cancel_enabled = bool(enableCancel)
            if enableCancel:
                self.setFixedSize(280, 96)
                self.cancelButton.show()
            else:
                self.cancelButton.hide()
                self.setFixedSize(280, 72)
            parent = self.parentWidget()
            if parent is not None:
                geo = parent.geometry()
                x = geo.x() + (geo.width() - self.width()) // 2
                y = geo.y() + (geo.height() - self.height()) // 2
                self.move(x, y)
            self.show()
            self.raise_()
            self.activateWindow()
        else:
            self.progressBar.setRange(1, 1)
            self.hide()
            if self.useData.setting_bool('SoundsEnabled'):
                self.app.beep()
