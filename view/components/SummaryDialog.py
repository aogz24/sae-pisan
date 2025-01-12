from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel
)
from PyQt6.QtCore import Qt


class SummaryDialog(QDialog):
    def __init__(self, model1, model2, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Summary Data")
        self.setMinimumSize(500, 400)

        # Gabungkan kolom dari model1 dan model2
        self.model1_columns = model1.get_data().columns
        self.model2_columns = model2.get_data().columns
        self.all_columns_model1 = list(self.model1_columns)  # Data Output
        self.all_columns_model2 = list(self.model2_columns)  # Output

        # Layout utama
        main_layout = QVBoxLayout(self)

        # Layout konten utama
        content_layout = QHBoxLayout()

        # Layout kiri untuk Data Output dan Output
        left_layout = QVBoxLayout()

        # Data Output
        self.data_output_label = QLabel("Data Output", self)
        self.data_output_list = QListWidget(self)
        self.data_output_list.addItems(self.all_columns_model1)
        left_layout.addWidget(self.data_output_label)
        left_layout.addWidget(self.data_output_list)

        # Output
        self.output_label = QLabel("Output", self)
        self.output_list = QListWidget(self)
        self.output_list.addItems(self.all_columns_model2)
        left_layout.addWidget(self.output_label)
        left_layout.addWidget(self.output_list)

        content_layout.addLayout(left_layout)

        # Layout tengah untuk tombol
        button_layout = QVBoxLayout()
        self.add_button = QPushButton("→", self)
        self.add_button.clicked.connect(self.add_variable)
        self.remove_button = QPushButton("←", self)
        self.remove_button.clicked.connect(self.remove_variable)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        content_layout.addLayout(button_layout)

        # Layout kanan untuk daftar variabel yang dipilih
        right_layout = QVBoxLayout()
        self.selected_label = QLabel("Variabel", self)
        self.selected_list = QListWidget(self)
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        content_layout.addLayout(right_layout)

        main_layout.addLayout(content_layout)

        # Tombol "Run"
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.accept)
        main_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)


    def add_variable(self):
        """Pindahkan variabel dari salah satu daftar ke 'selected'."""
        selected_items = self.data_output_list.selectedItems() + self.output_list.selectedItems()
        for item in selected_items:
            if not self.selected_list.findItems(item.text(), Qt.MatchFlag.MatchExactly):
                self.selected_list.addItem(item.text())
            if item in self.data_output_list.selectedItems():
                self.data_output_list.takeItem(self.data_output_list.row(item))
            elif item in self.output_list.selectedItems():
                self.output_list.takeItem(self.output_list.row(item))

    def remove_variable(self):
        """Pindahkan variabel dari daftar 'selected' kembali ke asalnya."""
        selected_items = self.selected_list.selectedItems()
        for item in selected_items:
            if item.text() in self.all_columns_model1:
                self.data_output_list.addItem(item.text())
            elif item.text() in self.all_columns_model2:
                self.output_list.addItem(item.text())
            self.selected_list.takeItem(self.selected_list.row(item))

    def get_selected_columns(self):
        """Ambil daftar variabel yang dipilih."""
        return [self.selected_list.item(i).text() for i in range(self.selected_list.count())]

    I
