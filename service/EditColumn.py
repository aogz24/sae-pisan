from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDialogButtonBox

class EditColumnDialog(QDialog):
    def __init__(self, column_name, data_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Column Dialog")

        self.column_name = column_name
        self.data_type = data_type

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Column name label
        self.column_name_label = QLabel(f"Column Name: {self.column_name}")
        layout.addWidget(self.column_name_label)

        # Data type label
        self.data_type_label = QLabel(f"Data Type: {self.data_type}")
        layout.addWidget(self.data_type_label)

        # Edit name input
        self.edit_name_input = QLineEdit()
        layout.addWidget(self.edit_name_input)

        # Edit data type input
        self.edit_data_type_input = QLineEdit()
        layout.addWidget(self.edit_data_type_input)

        # OK/Cancel buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    def display(self):
        self.edit_name_input.setText(self.column_name)
        self.edit_data_type_input.setText(self.data_type)
        self.exec()

    def edit_name(self, new_name):
        self.column_name = new_name

    def edit_data_type(self, new_data_type):
        self.data_type = new_data_type
