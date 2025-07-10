from PyQt6.QtWidgets import QApplication, QSplashScreen, QLabel, QVBoxLayout, QProgressBar
from PyQt6.QtCore import Qt, QPropertyAnimation

class SplashScreen(QSplashScreen):
    """
    A custom splash screen class that displays a series of messages during application startup.
    Attributes:
        label (QLabel): A label to display the current message.
        progress_bar (QProgressBar): Progress bar to show progress.
        layout (QVBoxLayout): A vertical box layout to manage the label's position.
        messages (list): A list of messages to be displayed sequentially.
        current_message_index (int): The index of the current message being displayed.
    Methods:
        update_message():
            Updates the label and progress bar to display the next message in the sequence.
    """
    
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        self.label = QLabel("Checking environment...", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: black; font-size: 14px;")

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_anim = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_anim.setDuration(400)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 5px;
                background: #eee;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 5px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress_bar)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.messages = [
            "Checking environment...",
            "Checking and Loading R...",
            "Loading R Packages...",
            "Setup Environment...",
            "Loading Completed!"
        ]
        self.current_message_index = 0

    def update_message(self):
        self.current_message_index = (self.current_message_index + 1) % len(self.messages)
        self.label.setText(self.messages[self.current_message_index])
        progress = int((self.current_message_index / (len(self.messages) - 1)) * 100)
        self.progress_anim.stop()
        self.progress_anim.setStartValue(self.progress_bar.value())
        self.progress_anim.setEndValue(progress)
        self.progress_anim.start()
        QApplication.processEvents()