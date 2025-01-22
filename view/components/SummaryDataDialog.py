from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, QAbstractItemView, QTextEdit
)
from PyQt6.QtCore import Qt


class SummaryDataDialog(QDialog):
    def __init__(self, model1, model2, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Summary Data")
        self.setMinimumSize(500, 500)  # Tinggi diperbesar untuk ruang script box

        # Gabungkan kolom dari model1 dan model2
        # self.model1_columns = model1.get_data().columns
        self.model2_columns = model2.get_data().columns
        # self.all_columns_model1 = list(self.model1_columns)  # Data Editor
        self.all_columns_model2 = list(self.model2_columns)  # Data Output

        # Layout utama
        main_layout = QVBoxLayout(self)

        # Layout konten utama
        content_layout = QHBoxLayout()

        # Layout kiri untuk Data Editor dan Data Output
        left_layout = QVBoxLayout()

        # Data Editor
        self.data_editor_label = QLabel("Data Editor", self)
        self.data_editor_list = QListWidget(self)
        self.data_editor_list.addItems(self.all_columns_model2)
        self.data_editor_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        left_layout.addWidget(self.data_editor_label)
        left_layout.addWidget(self.data_editor_list)

        # Data Output
        self.data_output_label = QLabel("Data Output", self)
        self.data_output_list = QListWidget(self)
        self.data_output_list.addItems(self.all_columns_model2)
        self.data_output_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        left_layout.addWidget(self.data_output_label)
        left_layout.addWidget(self.data_output_list)

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
        self.selected_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        content_layout.addLayout(right_layout)

        main_layout.addLayout(content_layout)

        # Box untuk menampilkan script di bawah variabel
        self.script_label = QLabel("Script:", self)
        self.script_box = QTextEdit(self)
        self.script_box.setPlaceholderText("")
        self.script_box.setReadOnly(True)  # Kosong dan hanya untuk menampilkan output
        main_layout.addWidget(self.script_label)
        main_layout.addWidget(self.script_box)

        # Layout horizontal untuk tombol Update dan Run
        button_row_layout = QHBoxLayout()
        self.update_script_button = QPushButton("Update R Script", self)
        self.update_script_button.clicked.connect(self.update_script)
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.accept)

        # Tambahkan tombol ke layout horizontal
        button_row_layout.addWidget(self.update_script_button, alignment=Qt.AlignmentFlag.AlignLeft)
        button_row_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Tambahkan layout tombol ke layout utama
        main_layout.addLayout(button_row_layout)

    def add_variable(self):
        selected_items = self.data_editor_list.selectedItems() + self.data_output_list.selectedItems()
        for item in selected_items:
            if not self.selected_list.findItems(item.text(), Qt.MatchFlag.MatchExactly):
                self.selected_list.addItem(item.text())
            if item in self.data_editor_list.selectedItems():
                self.data_editor_list.takeItem(self.data_editor_list.row(item))
            elif item in self.data_output_list.selectedItems():
                self.data_output_list.takeItem(self.data_output_list.row(item))

    def remove_variable(self):
        selected_items = self.selected_list.selectedItems()
        for item in selected_items:
            if item.text() in self.all_columns_model1:
                self.data_editor_list.addItem(item.text())
            elif item.text() in self.all_columns_model2:
                self.data_output_list.addItem(item.text())
            self.selected_list.takeItem(self.selected_list.row(item))

    def get_selected_columns(self):
        return [self.selected_list.item(i).text() for i in range(self.selected_list.count())]

    def update_script(self):
        selected_columns = self.get_selected_columns()

        if not selected_columns:
            # Jika tidak ada kolom yang dipilih
            self.script_box.setPlainText("Tidak ada kolom yang dipilih.")
            return

        # Gabungkan kolom dengan format yang sesuai untuk R
        formatted_columns = ', '.join(f'"{col}"' for col in selected_columns)
        script = f"summary_data <- summary(dataset[, c({formatted_columns})])"

        # Tampilkan script di script_box
        self.script_box.setPlainText(script)

