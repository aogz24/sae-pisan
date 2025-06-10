from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QPushButton, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont

class CustomToast(QWidget):
    """
    Custom Toast Notification Widget
    This widget displays a toast notification with a title, text, icon, and a progress bar.
    It can be customized with different positions, colors, and icons.
    The toast will automatically close after a specified duration, but can be paused by hovering over it.
    It supports various customization options such as border radius, icon size, background color, title color,
    close button icon color, duration bar color, and text color.
    Parameters:
        parent (QWidget): The parent widget for the toast.
        title (str): The title of the toast notification.
        text (str): The text content of the toast notification.
        duration (int): Duration in milliseconds before the toast automatically closes. Default is 3000 ms.
        position (str): Position of the toast on the screen. Options are "top-right", "top-left", "bottom-right", "bottom-left". Default is "top-right".
        icon_path (str): Path to the icon image to be displayed on the left side of the toast. Default is None, which uses a default icon.
    """
    def __init__(self, parent=None, title="", text="", duration=3000, position="top-right", icon_path=None):
        """Initialize the CustomToast widget."""
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
            pixmap = QPixmap("assets/information.svg")
            icon_label.setPixmap(pixmap.scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
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
        self.title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
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
        self.text_label.setFont(QFont("Arial", 8))
        self.text_label.setStyleSheet("color: #333; background: transparent;")
        self.text_label.setWordWrap(True)
        self.text_label.setMinimumWidth(250)
        self.text_label.setMaximumWidth(400)
        top_grid.addWidget(self.text_label, 1, 2, 1, 3, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        card_layout.addLayout(top_grid)
        card_layout.addSpacing(8)

        # Duration bar di paling bawah, tanpa space kosong
        self.progress = QProgressBar()
        self.progress.setMaximum(duration)
        self.progress.setValue(duration)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(9)
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
        """Handle the show event to adjust size and position."""
        super().showEvent(event)
        self.adjustSize()
        self.move_to_position()

    def move_to_position(self):
        """_summary_
        Move the toast to the specified position relative to its parent widget.
        If the parent widget is not set, it will center the toast on the screen.
        If the parent widget is set, it will position the toast at the specified corner with a margin.
        Supported positions are "top-right", "top-left", "bottom-right", "bottom-left", and "center".
        If the position is not recognized, it defaults to centering the toast on the parent widget.
        """
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
        """Pause the toast when the mouse enters."""
        self.is_paused = True
        self.timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Resume the toast when the mouse leaves."""
        self.is_paused = False
        self.timer.start(15)
        super().leaveEvent(event)

    def update_progress(self):
        """Update the progress bar and check if the toast should close."""
        if self.is_paused:
            return
        self.elapsed += 15
        remaining = max(0, self.duration - self.elapsed)
        self.progress.setValue(remaining)
        if self.elapsed >= self.duration:
            self.timer.stop()
            self.close()
    
    def set_border_radius(self, radius: int):
        """
        Set the border radius of the toast card.

        Args:
            radius (int): The desired border radius in pixels to be applied to the toast card.

        This method updates the stylesheet of the widget named "toastCard" to reflect the specified border radius.
        """
        style = f"""
            QWidget#toastCard {{
                background: #eaf6fd;
                border: 1.5px solid #90caf9;
                border-radius: {radius}px;
            }}
        """
        self.findChild(QWidget, "toastCard").setStyleSheet(style)
        
    def set_icon_size(self, width: int, height: int):
        """Atur ukuran icon pada toast."""
        icon_label = self.findChild(QLabel)
        if icon_label:
            pixmap = icon_label.pixmap()
            if pixmap:
                icon_label.setPixmap(pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            icon_label.setFixedSize(width, height)

    def set_background_color(self, color: str):
        """Atur warna background card toast."""
        card = self.findChild(QWidget, "toastCard")
        style = f"""
            QWidget#toastCard {{
                background: {color};
                border: 1.5px solid #90caf9;
                border-radius: 0px;
            }}
        """
        card.setStyleSheet(style)

    def set_title_color(self, color: str):
        """Atur warna teks title."""
        self.title_label.setStyleSheet(f"color: {color}; background: transparent;")

    def set_close_button_icon_color(self, color: str):
        """Atur warna icon tombol close."""
        close_btn = self.findChildren(QPushButton)[0]
        close_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background: transparent;
                font-size: 16px;
                color: {color};
            }}
            QPushButton:hover {{
                color: #d00;
                background: #e3f1fa;
            }}
        """)

    def set_duration_bar_color(self, color: str):
        """Atur warna progress bar durasi."""
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background: #e0e0e0;
                border-radius: 3px;
                margin-bottom: 5px;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 3px;
            }}
        """)

    def set_text_color(self, color: str):
        """Atur warna teks isi toast."""
        self.text_label.setStyleSheet(f"color: {color}; background: transparent;")
