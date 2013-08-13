from PyQt4 import QtCore, QtGui

# import plugins
from Xtra.Exporters.HTMLGenerator import HTMLGenerator
from Xtra.Exporters.ExporterRTF import ExporterRTF
from Xtra.Exporters.ExporterTEX import ExporterTEX
from Xtra.Exporters.ExporterPDF import ExporterPDF
from Extensions.ProgressWidget import ProgressWidget


class ExportThread(QtCore.QThread):
    # exporting takes time so it's only appropriate that it be implemented
    # in a thread

    def run(self):
        try:
            if self.extension == '.html':
                generator = HTMLGenerator(self.editor,
                                          self.progressIndicatorWidget)
                html = generator.generate(4, False, True, False, True,
                                          self.location)
                file = open(self.location, 'w')
                file.write(html)
                file.close()
            elif self.extension == '.odt':
                # generate HTML of the source
                generator = HTMLGenerator(self.editor,
                                          self.progressIndicatorWidget)
                html = generator.generate(4, False, True, False, True,
                                          self.location)
                # convert HTML to ODT
                doc = QtGui.QTextDocument()
                doc.setHtml(html)
                writer = QtGui.QTextDocumentWriter(self.location)
                ok = writer.write(doc)
            elif self.extension == '.pdf':
                pdf = ExporterPDF(self.editor,
                                  self.progressIndicatorWidget)
                pdf.exportSource(self.location)
            elif self.extension == '.rtf':
                rtf = ExporterRTF(self.editor,
                                  self.progressIndicatorWidget)
                rtf.exportSource(self.location)
            elif self.extension == '.tex':
                tex = ExporterTEX(self.editor,
                                  self.progressIndicatorWidget)
                tex.exportSource(self.location)
        except Exception as err:
            self.error = str(err)

    def export(self, ext, location, editor, progressIndicatorWidget):
        self.extension = ext
        self.location = location
        self.editor = editor
        self.progressIndicatorWidget = progressIndicatorWidget
        self.error = None
        self.start()


class Exporter(QtGui.QWidget):

    def __init__(self, editor, parent=None):
        super().__init__(parent)

        self.editor = editor
        self.progressWidget = ProgressWidget()
        self.exportThread = ExportThread()

        self.exportThread.finished.connect(self.exportCleanUp)

    def export(self, ext, fileName):
        self.exportThread.export(
            ext, fileName, self.editor, self.progressWidget)
        self.progressWidget.exec_()

    def exportCleanUp(self):
        self.progressWidget.reset()
        self.progressWidget.hide()

        if self.exportThread.error != None:
            message = QtGui.QMessageBox.critical(self, "Export",
                                                 "Error exporting file!\n\n" + self.exportThread.error)
