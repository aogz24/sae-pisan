from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QPushButton, QProgressBar
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
        self.is_paused = False

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Card container for solid background
        card = QWidget(self)
        card.setObjectName("toastCard")
        # Bawah 0 agar progressbar nempel ke bawah card
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 14, 18, 0)
        card_layout.setSpacing(0)

        # Top area: icon kiri, garis, title & text kanan (pakai grid)
        top_grid = QGridLayout()
        top_grid.setHorizontalSpacing(12)
        top_grid.setVerticalSpacing(2)
        top_grid.setContentsMargins(0, 0, 0, 0)

        # Icon kiri
        icon_label = QLabel()
        if icon_path:
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText("ℹ️")
            icon_label.setFont(QFont("Arial", 22))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        icon_label.setStyleSheet("background: transparent;")
        top_grid.addWidget(icon_label, 0, 0, 2, 1, Qt.AlignmentFlag.AlignTop)

        # Garis vertikal pembatas
        line = QWidget()
        line.setFixedWidth(1)
        line.setStyleSheet("background: #b0bec5; margin-top: 2px; margin-bottom: 2px;")
        top_grid.addWidget(line, 0, 1, 2, 1)

        # Title kanan atas
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #222; background: transparent;")
        self.title_label.setWordWrap(True)
        top_grid.addWidget(self.title_label, 0, 2, 1, 2, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Close button kanan atas
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
        top_grid.addWidget(close_btn, 0, 4, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # Text kanan bawah
        self.text_label = QLabel(text)
        self.text_label.setFont(QFont("Arial", 10))
        self.text_label.setStyleSheet("color: #333; background: transparent;")
        self.text_label.setWordWrap(True)
        self.text_label.setMinimumWidth(250)
        self.text_label.setMaximumWidth(400)
        top_grid.addWidget(self.text_label, 1, 2, 1, 3, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        card_layout.addLayout(top_grid)

        # Duration bar di paling bawah, tanpa space kosong
        self.progress = QProgressBar()
        self.progress.setMaximum(duration)
        self.progress.setValue(duration)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(7)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #e0e0e0;
                border-radius: 3px;
                margin-bottom: 5px;
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
                border-radius: 0px;
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

    def enterEvent(self, event):
        self.is_paused = True
        self.timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_paused = False
        self.timer.start(15)
        super().leaveEvent(event)

    def update_progress(self):
        if self.is_paused:
            return
        self.elapsed += 15
        remaining = max(0, self.duration - self.elapsed)
        self.progress.setValue(remaining)
        if self.elapsed >= self.duration:
            self.timer.stop()
            self.close()