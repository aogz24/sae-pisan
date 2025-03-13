from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtGui import QPixmap
from PyQt6 import QtCore

class AboutDialog(QDialog):
    """AboutDialog is a custom QDialog that provides information about the SAE Pisan application.
    Attributes:
        parent (QWidget): The parent widget of the dialog.
    Methods:
        __init__(parent):
            Initializes the AboutDialog with the given parent widget."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("About SAE Pisan")
        self.setFixedSize(500, 400)
        self.setStyleSheet("background-color: white; font-family: Arial; font-size: 12px;")
        
        layout = QVBoxLayout()
        
        # Logo
        logo_label = QLabel(self)
        pixmap = QPixmap("assets/icon.svg")
        logo_label.setPixmap(pixmap.scaled(80, 80, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # SAE Pisan Title
        title_label = QLabel("SAE Pisan")
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
        layout.addWidget(title_label)

        # Information and Description Frame
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Box)
        info_frame.setFrameShadow(QFrame.Shadow.Sunken)
        info_layout = QVBoxLayout()
        
        
        version_label = QLabel("<b>Version:</b> SAE Pisan 1.0.0")
        version_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(version_label)
        
        built_label = QLabel("<b>Built on:</b> 2024 (Indonesian)")
        built_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(built_label)
        
        download_label = QLabel("<b>Download:</b> <a href='https://sae-pisan-web.vercel.app/downloads'>Click here</a>")
        download_label.setOpenExternalLinks(True)
        download_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(download_label)
        
        desc_label = QLabel(
            """SAE Pisan (Small Area Estimation Programming for Statistical Analysis) is a GUI-based desktop application designed to perform small area estimation (SAE) using statistical methods based on R.
            """
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(desc_label)
        
        institution_label = QLabel("""<b>Sae Pisan is suported by Politeknik Statistika STIS</b>""")
        institution_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(institution_label)
        
        support_label = QLabel(
            """<b>Support:</b> For more information, please contact <a href='mailto: '></a>""")
        support_label.setOpenExternalLinks(True)
        support_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(support_label)
        
        copyright_label = QLabel(
            """<b>© 2024 SAE Pisan. All rights reserved.</b>
            """
        )
        copyright_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(copyright_label)

        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)

        # OK Button
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet("padding: 8px; background-color: #005a9e; color: white; border-radius: 5px; min-width: 100px;")
        ok_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)


