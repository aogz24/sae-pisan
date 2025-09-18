from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QTableView, QDialogButtonBox, QPushButton, QFileDialog, QComboBox
import polars as pl
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import QSize, Qt

class ExcelOptionsDialog(QDialog):
    """
    Dialog to select an Excel file, sheet, and preview data.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Excel Options")
        
        # Apply styling from style.qss
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border: 1px solid #BFBEBE;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: #5A5759;
                padding: 5px 0;
            }
            QPushButton {
                background-color: #95C843;
                color: #FFFFFF;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7AB432;
            }
            QPushButton:pressed {
                background-color: #5E8E2B;
            }
            QTableView {
                background-color: #FFFFFF;
                gridline-color: #BFBEBE;
                color: #5A5759;
                selection-background-color: #A1D9F3;
                selection-color: #FFFFFF;
                border: 1px solid #EAEAEA;
            }
            QTableView::item:selected {
                background-color: #A1D9F3;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #BFBEBE;
                color: #5A5759;
                border: 1px solid #EAEAEA;
                padding: 5px;
                font-weight: bold;
            }
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #BFBEBE;
                border-radius: 4px;
                padding: 5px;
                color: #5A5759;
            }
            QComboBox:drop-down {
                border: 0px;
                width: 20px;
            }
            QComboBox:down-arrow {
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #EAEAEA;
                selection-background-color: #A1D9F3;
                selection-color: #FFFFFF;
            }
            QCheckBox {
                color: #5A5759;
            }
            QCheckBox::indicator:checked {
                background-color: #95C843;
                border: 1px solid #95C843;
            }
        """)
        
        self.file_path = None
        self.sheet_names = []
        self.header = True
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # File picker - create horizontal layout for label and button
        file_layout = QHBoxLayout()
        
        # File label
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("font-weight: bold;")
        file_layout.addWidget(self.file_label)
        
        # Icon-only button - exactly match label font height
        self.file_button = QPushButton()
        self.file_button.setIcon(QIcon("assets/folder.svg"))
        self.file_button.setStyleSheet("""
            QPushButton {
                background-color: #95C843;
                color: #FFFFFF;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7AB432;
            }
            QPushButton:pressed {
                background-color: #5E8E2B;
            }
        """)
        
        # Calculate proper sizing based on font metrics
        font_height = self.file_label.fontMetrics().height()
        button_size = font_height + 8  # Add a bit of padding
        icon_size = font_height - 2  # Make icon slightly smaller than text
        
        self.file_button.setIconSize(QSize(icon_size, icon_size))
        self.file_button.setFixedSize(button_size, button_size)
        self.file_button.setToolTip("Select Excel File")
        self.file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_button)
        file_layout.addStretch()
        
        # Add the file layout to the main layout
        layout.addLayout(file_layout)

        # Sheet selector
        sheet_label = QLabel("Select Sheet")
        sheet_label.setStyleSheet("margin-top: 10px;")
        layout.addWidget(sheet_label)
        
        self.sheet_combo = QComboBox()
        self.sheet_combo.addItems(self.sheet_names)
        self.sheet_combo.currentIndexChanged.connect(self.update_preview)
        layout.addWidget(self.sheet_combo)
        
        # Header checkbox
        self.header_checkbox = QCheckBox("First row as header")
        self.header_checkbox.setChecked(True)  # Default header True
        self.header_checkbox.toggled.connect(self.update_preview)
        layout.addWidget(self.header_checkbox)

        # Preview Table
        self.preview_label = QLabel("Preview")
        self.preview_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
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
            self.file_label.setStyleSheet("font-weight: bold; color: #2BA3E2;")
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
                self.file_label.setStyleSheet("font-weight: bold; color: #FF3B30;")

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