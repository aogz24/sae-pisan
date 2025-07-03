from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QTableView, QDialogButtonBox, QPushButton, QFileDialog, QComboBox
import polars as pl
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class ExcelOptionsDialog(QDialog):
    """
    Dialog to select an Excel file, sheet, and preview data.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Excel Options")
        self.file_path = None
        self.sheet_names = []
        self.header = True
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # File picker
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)
        self.file_button = QPushButton("Select Excel File")
        self.file_button.clicked.connect(self.select_file)
        layout.addWidget(self.file_button)

        # Sheet selector
        self.sheet_combo = QComboBox()
        self.sheet_combo.addItems(self.sheet_names)
        self.sheet_combo.currentIndexChanged.connect(self.update_preview)
        layout.addWidget(QLabel("Select Sheet"))
        layout.addWidget(self.sheet_combo)
        
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
        """File picker to select an Excel file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"Selected: {file_path}")
            try:
                import pandas as pd
                xls = pd.ExcelFile(file_path)
                self.sheet_names = xls.sheet_names
                self.sheet_combo.clear()
                self.sheet_combo.addItems(self.sheet_names)
                self.update_preview()
            except Exception as e:
                self.sheet_combo.clear()
                self.preview_table.setModel(None)
                self.file_label.setText(f"Error: {e}")

    def update_preview(self):
        """Update the preview table based on the selected sheet."""
        if not self.file_path:
            self.preview_table.setModel(None)
            return
        
        sheet = self.sheet_combo.currentText()
        hdr = True if self.header_checkbox.isChecked() else False
        try:
            df = pl.read_excel(source=self.file_path, sheet_name=sheet, has_header=hdr).head(10)
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(df.columns)
            for row in df.to_numpy():
                items = [QStandardItem(str(cell)) for cell in row]
                model.appendRow(items)
            self.preview_table.setModel(model)
        except Exception as e:
            print(f"Error: {e}")
            self.preview_table.setModel(None)
    
    def get_excel_options(self):
        """Return path file dan name selected sheet"""
        if self.exec()== QDialog.DialogCode.Accepted and self.file_path and self.sheet_combo.currentText():
            return self.file_path, self.sheet_combo.currentText(), self.header_checkbox.isChecked()
        return None, None, None