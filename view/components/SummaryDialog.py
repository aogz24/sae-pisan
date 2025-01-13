from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListView, QTextEdit
from PyQt6.QtCore import Qt, QStringListModel


class SummaryDialog(QDialog):
    def __init__(self, model1, model2, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Summary Data")
        self.setMinimumSize(500, 500)  # Tinggi diperbesar untuk ruang script box

        # Gabungkan kolom dari model1 dan model2
        self.model1_columns = model1.get_data().columns
        self.model2_columns = model2.get_data().columns
        self.all_columns_model1 = list(self.model1_columns)  # Data Editor
        self.all_columns_model2 = list(self.model2_columns)  # Data Output

        # Layout utama
        main_layout = QVBoxLayout(self)

        # Layout konten utama
        content_layout = QHBoxLayout()

        # Layout kiri untuk Data Editor dan Data Output
        left_layout = QVBoxLayout()

        # Data Editor (menggunakan QListView untuk efisiensi)
        self.data_editor_label = QLabel("Data Editor", self)
        self.data_editor_list = QListView(self)
        self.data_editor_model = QStringListModel(self.all_columns_model1)
        self.data_editor_list.setModel(self.data_editor_model)
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)  # Shift + Arrow
        left_layout.addWidget(self.data_editor_label)
        left_layout.addWidget(self.data_editor_list)

        # Data Output (menggunakan QListView untuk efisiensi)
        self.data_output_label = QLabel("Data Output", self)
        self.data_output_list = QListView(self)
        self.data_output_model = QStringListModel(self.all_columns_model2)
        self.data_output_list.setModel(self.data_output_model)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)  # Shift + Arrow
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
        self.selected_list = QListView(self)
        self.selected_model = QStringListModel()
        self.selected_list.setModel(self.selected_model)
        self.selected_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)  # Shift + Arrow
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        content_layout.addLayout(right_layout)

        main_layout.addLayout(content_layout)

        # Box untuk menampilkan script di bawah variabel
        self.script_label = QLabel("Script:", self)
        self.script_box = QTextEdit(self)
        self.script_box.setPlaceholderText("Script akan ditampilkan di sini...")
        self.script_box.setReadOnly(True)  # Kosong dan hanya untuk menampilkan output
        main_layout.addWidget(self.script_label)
        main_layout.addWidget(self.script_box)

        # Tombol "Run"
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.accept)
        main_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

    def add_variable(self):
        selected_items = self.data_editor_list.selectedIndexes()
        for index in selected_items:
            item_text = self.data_editor_model.data(index)
            if all(self.selected_model.data(self.selected_model.index(i)) != item_text for i in range(self.selected_model.rowCount())):
                self.selected_model.insertRow(self.selected_model.rowCount())
                self.selected_model.setData(self.selected_model.index(self.selected_model.rowCount() - 1), item_text)

            self.data_editor_model.removeRows(index.row(), 1)


    def remove_variable(self):
        selected_items = self.selected_list.selectedIndexes()
        for index in selected_items:
            item_text = self.selected_model.data(index)
            if item_text in self.all_columns_model1:
                self.data_editor_model.insertRow(self.data_editor_model.rowCount())
                self.data_editor_model.setData(self.data_editor_model.index(self.data_editor_model.rowCount() - 1), item_text)
            elif item_text in self.all_columns_model2:
                self.data_output_model.insertRow(self.data_output_model.rowCount())
                self.data_output_model.setData(self.data_output_model.index(self.data_output_model.rowCount() - 1), item_text)

            self.selected_model.removeRows(index.row(), 1)

    def get_selected_columns(self):
        return [self.selected_model.data(self.selected_model.index(i)) for i in range(self.selected_model.rowCount())]
