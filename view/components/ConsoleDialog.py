from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QTextCursor

class ConsoleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("R Console Output")
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_movie = QMovie("assets/loading.gif")
        self.loading_movie.setScaledSize(QSize(25, 25))
        self.loading_label.setMovie(self.loading_movie)
        layout.addWidget(self.loading_label)
        self.loading_movie.start()
        layout.addWidget(self.console)

    def append_text(self, text):
        doc = self.console.document()
        block_count = doc.blockCount()
        if block_count > 1:
            cursor = self.console.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()
            cursor.insertText(text)
        else:
            self.console.setPlainText(text)
        self.console.moveCursor(QTextCursor.MoveOperation.End)

    def stop_loading(self):
        self.loading_movie.stop()
        self.loading_label.setVisible(False)