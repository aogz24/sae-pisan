from PyQt6.QtWidgets import QApplication, QSplashScreen, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class SplashScreen(QSplashScreen):
    """
    A custom splash screen class that displays a series of messages during application startup.
    Attributes:
        label (QLabel): A label to display the current message.
        layout (QVBoxLayout): A vertical box layout to manage the label's position.
        messages (list): A list of messages to be displayed sequentially.
        current_message_index (int): The index of the current message being displayed.
    Methods:
        update_message():
            Updates the label to display the next message in the sequence.
    """
    
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        self.label = QLabel("Checking environment...", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: black; font-size: 14px;")

        
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.messages = ["Checking environment...", "Checking and Loading R...", "Loading R Packages...", "Setup Environment...", "Loading Completed!"]
        self.current_message_index = 0

    def update_message(self):
        self.current_message_index = (self.current_message_index + 1) % len(self.messages)
        self.label.setText(self.messages[self.current_message_index])
        QApplication.processEvents()