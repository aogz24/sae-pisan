from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox

class EditColumnDialog(QDialog):
    """
    A dialog for editing column details such as column name and data type.
    Attributes:
        column_name (str): The name of the column to be edited.
        data_type (str): The data type of the column to be edited.
        column_name_label (QLabel): Label displaying the current column name.
        data_type_label (QLabel): Label displaying the current data type.
        edit_name_input (QLineEdit): Input field for editing the column name.
        edit_data_type_input (QLineEdit): Input field for editing the data type.
        buttons (QDialogButtonBox): Dialog buttons for accepting or rejecting changes.
    Methods:
        __init__(column_name, data_type, parent=None):
            Initializes the dialog with the given column name and data type.
        init_ui():
            Initializes the user interface components of the dialog.
        display():
            Displays the dialog and pre-fills the input fields with the current column details.
        edit_name(new_name):
            Updates the column name with the given new name.
        edit_data_type(new_data_type):
            Updates the data type with the given new data type.
    """
    
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
