from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QTextEdit, QMessageBox, QInputDialog
from service.compute import run_compute
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
import os

class ComputeVariableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.model = parent.model1
        self.column_names = self.model.get_data().columns
        self.templates = self.load_templates()

        self.setWindowTitle("Compute New Variable")
        self.init_ui()

    def load_templates(self):
        templates = {}
        template_file = os.path.join(self.parent.path, 'file-data', 'template.dat')
        with open(template_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                name, script = line.strip().split('=', 1)
                templates[name] = script
        return templates

    def save_template(self):
        self.save_template_button.setText("Saving...")
        self.save_template_button.setEnabled(False)
        template_name, ok = QInputDialog.getText(self, "Save Template", "Enter template name:")
        if ok and template_name:
            script = self.get_script()
            self.templates[template_name] = script
            template_file = os.path.join(self.parent.path, 'file-data', 'template.dat')
            with open(template_file, 'a') as file:
                file.write(f"{template_name}={script}\n")
            self.template_selection.addItem(template_name)
            QMessageBox.information(self, "Success", "Template saved successfully!")

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.column_label = QLabel("Enter new column name:")
        self.layout.addWidget(self.column_label)
        self.column_name_input = QLineEdit()
        self.column_name_input.setPlaceholderText("Enter column name here")
        self.layout.addWidget(self.column_name_input)

        self.template_label = QLabel("Select template:")
        self.layout.addWidget(self.template_label)
        self.template_selection = QComboBox()
        self.template_selection.addItems(self.templates.keys())
        self.template_selection.setCurrentIndex(0)
        self.layout.addWidget(self.template_selection)

        self.variable1_label = QLabel("Select Nominator:")
        self.variable1_label.setVisible(False)
        self.layout.addWidget(self.variable1_label)
        self.variable1_selection = QComboBox()
        self.variable1_selection.addItems(self.column_names)
        self.variable1_selection.setVisible(False)
        self.layout.addWidget(self.variable1_selection)

        self.variable2_label = QLabel("Select Denominator:")
        self.variable2_label.setVisible(False)
        self.layout.addWidget(self.variable2_label)
        self.variable2_selection = QComboBox()
        self.variable2_selection.addItems(self.column_names)
        self.variable2_selection.setVisible(False)
        self.layout.addWidget(self.variable2_selection)

        self.script_label = QLabel("R Script:")

        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.icon_label.setVisible(False)

        # Create a horizontal layout to place the script_label and icon_label in one row
        script_layout = QHBoxLayout()
        script_layout.addWidget(self.script_label)
        script_layout.addWidget(self.icon_label)

        self.layout.addLayout(script_layout)
        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("Write r script here...")
        self.layout.addWidget(self.script_input)

        # Tombol OK dan Cancel
        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.button_layout.addWidget(self.ok_button)
        self.save_template_button = QPushButton("Save Template")
        self.save_template_button.clicked.connect(self.save_template)
        self.button_layout.addWidget(self.save_template_button)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

        # Event handler untuk perubahan template
        self.template_selection.currentIndexChanged.connect(self.update_script_input)
        self.variable1_selection.currentIndexChanged.connect(self.update_script_input)
        self.variable2_selection.currentIndexChanged.connect(self.update_script_input)

        # Initialize script input with the first template
        self.update_script_input(0)

    def update_script_input(self, index):
        template_name = self.template_selection.currentText()
        script = self.templates.get(template_name, "")
        if template_name == "Compute RSE":
            self.variable1_label.setVisible(True)
            self.variable1_selection.setVisible(True)
            self.variable2_label.setVisible(True)
            self.variable2_selection.setVisible(True)
            variable1 = self.variable1_selection.currentText()
            variable2 = self.variable2_selection.currentText()
            script = script.replace("{variable1}", variable1).replace("{variable2}", variable2)
        else:
            self.variable1_label.setVisible(False)
            self.variable1_selection.setVisible(False)
            self.variable2_label.setVisible(False)
            self.variable2_selection.setVisible(False)
        self.script_input.setPlainText(script)

    def set_model(self, model):
        self.model = model
        self.column_names = [col.replace(" ", "_") for col in self.model.get_data().columns]
        self.variable1_selection.clear()
        self.variable1_selection.addItems(self.column_names)
        self.variable2_selection.clear()
        self.variable2_selection.addItems(self.column_names)

    def get_script(self):
        return self.script_input.toPlainText()

    def accept(self):
        if self.column_name_input.text() == "":
            QMessageBox.warning(self, "Error", "Column name cannot be empty!")
            return
        self.ok_button.setText("Computing...")
        self.ok_button.setEnabled(False)
        self.icon_label.setVisible(True)
        df = self.model.get_data()
        new_column_series = run_compute(self)
        self.model.set_data(df.with_columns(new_column_series))
        self.parent.update_table(1, self.model)
        self.icon_label.setVisible(False)
        self.ok_button.setText("OK")
        self.ok_button.setEnabled(False)
        super().accept()