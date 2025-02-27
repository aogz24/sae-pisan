import sys
import time
from PyQt6.QtWidgets import QApplication, QSplashScreen, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt, QTimer

class SplashScreen(QSplashScreen):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        self.label = QLabel("Checking environment...", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: black; font-size: 14px;")

        
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.messages = ["Checking environment...", "Loading R an R Package...", "Setup Environment...", "Loading Completed!"]
        self.current_message_index = 0

    def update_message(self):
        self.current_message_index = (self.current_message_index + 1) % len(self.messages)
        self.label.setText(self.messages[self.current_message_index])
        QApplication.processEvents()