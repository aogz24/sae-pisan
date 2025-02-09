from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QTextEdit
from PyQt6.QtWidgets import QDialog
from service.compute import run_compute

class ComputeVariableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.model = parent.model1
        self.column_names = self.parent.model1.get_data().columns
        self.setWindowTitle("Compute Variable")

        self.layout = QVBoxLayout()

        self.label = QLabel("Enter new column name:")
        self.layout.addWidget(self.label)

        self.column_name_input = QLineEdit()
        self.layout.addWidget(self.column_name_input)

        self.label = QLabel("Select template:")
        self.layout.addWidget(self.label)

        self.template_selection = QComboBox()
        self.template_selection.addItems(["Sequence Number 1 to Last Data", "Compute RSE", "Custom"])  # Add your templates here
        self.template_selection.setCurrentIndex(2)
        self.layout.addWidget(self.template_selection)
        

        self.label = QLabel("Select variable 1:")
        self.layout.addWidget(self.label)

        self.variable1_selection = QComboBox()
        self.variable1_selection.addItems(self.column_names)
        self.layout.addWidget(self.variable1_selection)

        self.label = QLabel("Select variable 2:")
        self.layout.addWidget(self.label)

        self.variable2_selection = QComboBox()
        self.variable2_selection.addItems(self.column_names)
        self.layout.addWidget(self.variable2_selection)

        self.label = QLabel("Enter script:")
        self.layout.addWidget(self.label)

        self.script_input = QTextEdit()
        self.layout.addWidget(self.script_input)

        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

        self.template_selection.currentIndexChanged.connect(self.update_script_input)
        self.variable1_selection.currentIndexChanged.connect(lambda: self.update_script_input(self.template_selection.currentIndex()))
        self.variable2_selection.currentIndexChanged.connect(lambda: self.update_script_input(self.template_selection.currentIndex()))

    def update_script_input(self, index):
        if index == 0:
            self.script_input.setPlainText("new_column <- seq_len(nrow(data))")
        elif index == 1:
            variable1 = self.variable1_selection.currentText()
            variable2 = self.variable2_selection.currentText()
            self.script_input.setPlainText(f'new_column = sqrt({variable1}) / {variable2} * 100')
        else:
            self.script_input.clear()
    
    def set_model(self, model):
        self.model = model
        self.column_names = self.model.get_data().columns
        self.variable1_selection.clear()
        self.variable1_selection.addItems(self.column_names)
        self.variable2_selection.clear()
        self.variable2_selection.addItems(self.column_names)
    
    def get_script(self):
        return self.script_input.toPlainText()
    
    def accept(self):
        import polars as pl
        df = self.model.get_data()
        new_column_series = run_compute(self)
        self.model.set_data(df.with_columns(new_column_series))
        self.parent.update_table(1, self.model)
        super().accept()
    