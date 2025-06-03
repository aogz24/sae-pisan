from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont

class CustomToast(QWidget):
    def __init__(self, parent=None, title="", text="", duration=3000, position="top-right", icon_path=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Card container for solid background
        card = QWidget(self)
        card.setObjectName("toastCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(10)

        # Top row: icon, title, close button
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        # Icon
        icon_label = QLabel()
        if icon_path:
            icon_label.setPixmap(QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText("ℹ️")
            icon_label.setFont(QFont("Arial", 16))
        icon_label.setFixedSize(28, 28)
        icon_label.setStyleSheet("background: transparent;")
        top_layout.addWidget(icon_label)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #222; background: transparent;")
        top_layout.addWidget(self.title_label, 1)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                font-size: 16px;
                color: #444;
            }
            QPushButton:hover {
                color: #d00;
                background: #e3f1fa;
            }
        """)
        close_btn.clicked.connect(self.close)
        top_layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignRight)

        card_layout.addLayout(top_layout)

        # Text
        self.text_label = QLabel(text)
        self.text_label.setFont(QFont("Arial", 10))
        self.text_label.setStyleSheet("color: #333; background: transparent;")
        self.text_label.setWordWrap(True)
        self.text_label.setMinimumWidth(250)
        self.text_label.setMaximumWidth(400)
        card_layout.addWidget(self.text_label)

        # Duration bar
        self.progress = QProgressBar()
        self.progress.setMaximum(duration)
        self.progress.setValue(duration)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #e0e0e0;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: #2196f3;
                border-radius: 3px;
            }
        """)
        card_layout.addWidget(self.progress)

        # Set card background and border
        card.setStyleSheet("""
            QWidget#toastCard {
                background: #eaf6fd;
                border: 1.5px solid #90caf9;
                border-radius: 12px;
            }
        """)

        main_layout.addWidget(card)

        self.adjustSize()
        self.duration = duration
        self.position = position

        # Timer for auto-close and progress bar
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(15)
        self.elapsed = 0

    def showEvent(self, event):
        super().showEvent(event)
        self.adjustSize()
        self.move_to_position()

    def move_to_position(self):
        parent = self.parentWidget()
        if parent:
            parent_rect = parent.geometry()
            margin = 32
            if self.position == "top-right":
                x = parent_rect.x() + parent_rect.width() - self.width() - margin
                y = parent_rect.y() + margin
            elif self.position == "top-left":
                x = parent_rect.x() + margin
                y = parent_rect.y() + margin
            elif self.position == "bottom-right":
                x = parent_rect.x() + parent_rect.width() - self.width() - margin
                y = parent_rect.y() + parent_rect.height() - self.height() - margin
            elif self.position == "bottom-left":
                x = parent_rect.x() + margin
                y = parent_rect.y() + parent_rect.height() - self.height() - margin
            else:
                x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
                y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)

    def update_progress(self):
        self.elapsed += 15
        remaining = max(0, self.duration - self.elapsed)
        self.progress.setValue(remaining)
        if self.elapsed >= self.duration:
            self.timer.stop()
            self.close()