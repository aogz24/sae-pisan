from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QTableView, QDialogButtonBox, QPushButton, QFileDialog
from PyQt6.QtCore import Qt
import polars as pl
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class CSVOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSV Options")

        self.file_path = None
        self.separator = ","
        self.header = True

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # File picker
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)
        self.file_button = QPushButton("Select File")
        self.file_button.clicked.connect(self.select_file)
        layout.addWidget(self.file_button)

        # Separator input
        layout.addWidget(QLabel("Separator (e.g., , or ;)"))
        self.separator_input = QLineEdit(",")
        self.separator_input.textChanged.connect(self.update_preview)
        layout.addWidget(self.separator_input)

        # Header checkbox
        self.header_checkbox = QCheckBox("First row as header")
        self.header_checkbox.setChecked(True)  # Default header True
        self.header_checkbox.toggled.connect(self.update_preview)
        layout.addWidget(self.header_checkbox)

        # Preview Table
        self.preview_label = QLabel("Preview")
        layout.addWidget(self.preview_label)
        self.preview_table = QTableView()
        layout.addWidget(self.preview_table)

        # OK/Cancel buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    def select_file(self):
        """File picker untuk memilih file CSV."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"Selected: {file_path}")
            self.update_preview()

    def update_preview(self):
        """Perbarui preview tabel berdasarkan input."""
        if not self.file_path:
            self.preview_table.setModel(None)
            return

        sep = self.separator_input.text()
        hdr = 0 if self.header_checkbox.isChecked() else None
        try:
            preview_data = pl.read_csv(self.file_path, sep=sep, header=hdr, nrows=10).head()
            model = QStandardItemModel()
            
            if not self.header_checkbox.isChecked():
                preview_data.columns = [f"Column {i+1}" for i in range(preview_data.shape[1])]
            
            model.setHorizontalHeaderLabels(preview_data.columns.tolist())

            for row in preview_data.values:
                items = [QStandardItem(str(cell)) for cell in row]
                model.appendRow(items)

            self.preview_table.setModel(model)
        except Exception:
            self.preview_table.setModel(None)

    def get_csv_options(self):
        """Mengembalikan opsi CSV jika dialog diterima."""
        if self.exec() == QDialog.DialogCode.Accepted and self.file_path:
            return self.file_path, self.separator_input.text(), self.header_checkbox.isChecked()
        return None, None, None
