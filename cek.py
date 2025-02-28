import sys
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QClipboard

class ClipboardImageApp(QWidget):
    def __init__(self):
        super().__init__()

        # Load gambar ke QPixmap
        self.pixmap = QPixmap("assets/icon.svg")

        # Label untuk menampilkan gambar
        self.label = QLabel()
        self.label.setPixmap(self.pixmap)

        # Tombol untuk menyalin ke clipboard
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.copy_button)
        self.setLayout(layout)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(self.pixmap, QClipboard.Mode.Clipboard)  # Menyalin gambar ke clipboard

        print("Image copied to clipboard!")

# Jalankan aplikasi
app = QApplication(sys.argv)
window = ClipboardImageApp()
window.show()
sys.exit(app.exec())
