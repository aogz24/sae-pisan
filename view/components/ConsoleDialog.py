from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtGui import QMovie, QTextCursor, QFont
from PyQt6.QtCore import Qt, QSize

class ConsoleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("R Console Output")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title label
        title_label = QLabel("R Console Output")
        title_label.setObjectName("console_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Loading animation
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_movie = QMovie("assets/loading.gif")
        self.loading_movie.setScaledSize(QSize(30, 30))
        self.loading_label.setMovie(self.loading_movie)
        layout.addWidget(self.loading_label)
        self.loading_movie.start()
        
        # Console text area
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            background-color: #F8F8F8;
            border: 1px solid #EAEAEA;
            color: #5A5759;
            padding: 10px;
            font-family: 'Courier New', monospace;
        """)
        layout.addWidget(self.console)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border: 1px solid #BFBEBE;
                border-radius: 8px;
            }
            
            QLabel#console_title {
                color: #5A5759;
                padding: 5px 0;
            }
        """)

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
        
    def keyPressEvent(self, event):
        # Allow Escape key to close the dialog
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)