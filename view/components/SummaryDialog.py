from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel
)
from PyQt6.QtCore import Qt

class SummaryDialog(QDialog):
    def __init__(self,data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Summary Data")
        self.setMinimumSize(300, 300)

        # Layout utama
        main_layout = QVBoxLayout(self)

        # Layout untuk daftar variabel dan tombol
        middle_layout = QHBoxLayout()
        print(data)
        # Daftar variabel yang tersedia
        self.available_list = QListWidget(self)
        self.available_list.addItems(data.columns)
        middle_layout.addWidget(self.available_list)

        # Tombol untuk memindahkan variabel
        button_layout = QVBoxLayout()
        self.add_button = QPushButton("→", self)
        self.add_button.clicked.connect(self.add_variable)
        self.remove_button = QPushButton("←", self)
        self.remove_button.clicked.connect(self.remove_variable)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        middle_layout.addLayout(button_layout)

        # Daftar variabel yang dipilih
        self.selected_list = QListWidget(self)
        middle_layout.addWidget(self.selected_list)

        main_layout.addLayout(middle_layout)

        # Tombol "Run"
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.accept)
        main_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

    def add_variable(self):
        """Pindahkan variabel dari daftar 'available' ke 'selected'."""
        selected_items = self.available_list.selectedItems()
        for item in selected_items:
            self.selected_list.addItem(item.text())
            self.available_list.takeItem(self.available_list.row(item))

    def remove_variable(self):
        """Pindahkan variabel dari daftar 'selected' ke 'available'."""
        selected_items = self.selected_list.selectedItems()
        for item in selected_items:
            self.available_list.addItem(item.text())
            self.selected_list.takeItem(self.selected_list.row(item))

    def get_selected_columns(self):
        """Ambil daftar variabel yang dipilih."""
        return [self.selected_list.item(i).text() for i in range(self.selected_list.count())]
