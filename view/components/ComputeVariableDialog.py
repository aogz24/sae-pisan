
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, 
                         QComboBox, QTextEdit, QMessageBox, QInputDialog, QFrame)
from service.compute import run_compute
from PyQt6.QtGui import QIcon, QDoubleValidator, QFont
from PyQt6.QtCore import QSize, Qt
import os
import shutil

class ComputeVariableDialog(QDialog):
    """
    A dialog for computing new variables based on user-defined templates and R scripts.
    Attributes:
        parent (QWidget): The parent widget.
        model (QAbstractTableModel): The data model from the parent.
        column_names (list): List of column names from the model.
        templates (dict): Dictionary of templates loaded from a file.
    Methods:
        __init__(parent=None):
            Initializes the dialog with the given parent.
        load_templates():
            Loads templates from a file and returns them as a dictionary.
        save_template():
            Saves the current script as a new template.
        init_ui():
            Initializes the user interface components of the dialog.
        update_script_input(index):
            Updates the script input field based on the selected template and variables.
        set_model(model):
            Sets the data model and updates the column names.
        get_script():
            Returns the current script from the script input field.
        accept():
            Validates the input, computes the new variable, and updates the model.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.model = parent.model1
        self.column_names = self.model.get_data().columns
        self.templates = self.load_templates()

        # Set up window properties
        self.setWindowTitle("Compute New Variable")
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # Apply dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border: 1px solid #BFBEBE;
                border-radius: 8px;
            }
            
            QLabel {
                color: #5A5759;
                font-weight: bold;
                margin-top: 5px;
            }
            
            QLineEdit, QComboBox {
                background-color: #F8F8F8;
                border: 1px solid #EAEAEA;
                border-radius: 4px;
                padding: 8px;
                color: #5A5759;
            }
            
            QTextEdit {
                background-color: #F8F8F8;
                border: 1px solid #EAEAEA;
                color: #5A5759;
                padding: 10px;
                font-family: 'Courier New', monospace;
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
            
            QPushButton:disabled {
                background-color: #BFBEBE;
            }
        """)
        
        self.init_ui()

    def load_templates(self):
        app_data_dir = os.path.join(os.getenv("APPDATA"), "saePisan")
        os.makedirs(app_data_dir, exist_ok=True)
        templates = {}
        template_file = os.path.join(self.parent.path, 'file-data', 'template.dat')
        appdata_template_file = os.path.join(app_data_dir, 'template.dat')
        
        if not os.path.exists(appdata_template_file):
            # Copy template.dat to appdata_template_file if it doesn't exist
            shutil.copyfile(template_file, appdata_template_file)
            template_file = appdata_template_file
            
        with open(template_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                name, script = line.strip().split('=', 1)
                templates[name] = script
        return templates

    def save_template(self):
        self.save_template_button.setText("Saving...")
        self.save_template_button.setEnabled(False)
        
        # Setup a styled dialog
        input_dialog = QInputDialog(self)
        input_dialog.setWindowTitle("Save Template")
        input_dialog.setLabelText("Enter template name:")
        input_dialog.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border: 1px solid #BFBEBE;
                border-radius: 8px;
            }
            QLabel {
                color: #5A5759;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #F8F8F8;
                border: 1px solid #EAEAEA;
                border-radius: 4px;
                padding: 8px;
                color: #5A5759;
            }
        """)
        
        ok = input_dialog.exec()
        template_name = input_dialog.textValue()
        
        if ok and template_name:
            script = self.get_script()
            self.templates[template_name] = script
            
            # Save to template file
            app_data_dir = os.path.join(os.getenv("APPDATA"), "saePisan")
            template_file = os.path.join(app_data_dir, 'template.dat')
            with open(template_file, 'a') as file:
                file.write(f"{template_name}={script}\n")
            
            # Update template dropdown
            self.template_selection.addItem(template_name)
            
            # Show success message
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Success")
            msg_box.setText("Template saved successfully!")
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #FFFFFF;
                }
                QPushButton {
                    background-color: #95C843;
                    color: #FFFFFF;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #7AB432;
                }
            """)
            msg_box.exec()
        
        self.save_template_button.setText("Save Template")
        self.save_template_button.setEnabled(True)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        # Title
        title_label = QLabel("Compute New Variable")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #EAEAEA;")
        self.layout.addWidget(separator)
        
        # Column name section
        self.column_label = QLabel("Enter new column name:")
        self.layout.addWidget(self.column_label)
        self.column_name_input = QLineEdit()
        self.column_name_input.setPlaceholderText("Enter column name here")
        self.layout.addWidget(self.column_name_input)

        # Template section
        self.template_label = QLabel("Select template:")
        self.layout.addWidget(self.template_label)
        self.template_selection = QComboBox()
        self.template_selection.addItems(self.templates.keys())
        self.template_selection.setCurrentIndex(0)
        self.layout.addWidget(self.template_selection)

        # Variable selection section
        self.variable_selected_label = QLabel("Variable:")
        self.variable_selected_label.setVisible(False)
        self.layout.addWidget(self.variable_selected_label)

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

        # Lambda section
        self.lambda_label = QLabel("Lambda:")
        self.lambda_label.setVisible(False)
        self.layout.addWidget(self.lambda_label)

        self.lambda_selection = QLineEdit()
        self.lambda_selection.setVisible(False)
        self.lambda_selection.setValidator(QDoubleValidator())
        self.layout.addWidget(self.lambda_selection)

        # Script section
        script_header = QHBoxLayout()
        
        self.script_label = QLabel("R Script:")
        self.script_label.setFont(title_font)
        script_header.addWidget(self.script_label)
        
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.icon_label.setVisible(False)
        script_header.addStretch()
        script_header.addWidget(self.icon_label)

        self.layout.addLayout(script_header)
        
        # Script text editor
        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("Write R script here...")
        self.script_input.setMinimumHeight(150)
        self.layout.addWidget(self.script_input)

        # Button section
        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName("button_layout")
        
        self.save_template_button = QPushButton("Save Template")
        self.save_template_button.setIcon(QIcon("assets/save.svg"))
        self.save_template_button.clicked.connect(self.save_template)
        
        self.ok_button = QPushButton("Compute")
        self.ok_button.setIcon(QIcon("assets/compute.svg"))
        self.ok_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            background-color: #BFBEBE;
            color: #FFFFFF;
        """)
        
        self.button_layout.addWidget(self.save_template_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(cancel_button)
        self.button_layout.addWidget(self.ok_button)

        self.layout.addLayout(self.button_layout)

        # Connect events
        self.template_selection.currentIndexChanged.connect(self.update_script_input)
        self.variable1_selection.currentIndexChanged.connect(self.update_script_input)
        self.variable2_selection.currentIndexChanged.connect(self.update_script_input)
        self.lambda_selection.textChanged.connect(self.update_script_input)

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
            self.lambda_label.setVisible(False)
            self.lambda_selection.setVisible(False)
            variable1 = self.variable1_selection.currentText()
            variable2 = self.variable2_selection.currentText()
            script = script.replace("{variable1}", variable1).replace("{variable2}", variable2)

        elif template_name in ["Log Transformation", "Natural Log (ln) Transformation", "Logit Transformation"]:
            self.variable_selected_label.setVisible(True)
            self.variable1_label.setVisible(False)
            self.variable1_selection.setVisible(True)
            self.variable2_label.setVisible(False)
            self.variable2_selection.setVisible(False)
            self.lambda_label.setVisible(False)
            self.lambda_selection.setVisible(False)

            variable1 = self.variable1_selection.currentText()
            script = script.replace("{variable1}", variable1)

        elif template_name in ["Power Transformation", "Box-Cox Transformation"]:
            self.variable_selected_label.setVisible(True)
            self.variable1_label.setVisible(False)
            self.variable1_selection.setVisible(True)
            self.variable2_label.setVisible(False)
            self.variable2_selection.setVisible(False)

            self.lambda_label.setVisible(True)
            self.lambda_selection.setVisible(True)
            variable1 = self.variable1_selection.currentText()
            lambda_value = self.lambda_selection.text()
            script = script.replace("{variable1}", variable1).replace("{lambda}", lambda_value)

        else:
            self.variable1_label.setVisible(False)
            self.variable1_selection.setVisible(False)
            self.variable2_label.setVisible(False)
            self.variable2_selection.setVisible(False)
        self.script_input.setPlainText(script)

    def set_model(self, model):
        self.model = model
        # self.column_names = [col.replace(" ", "_") for col in self.model.get_data().columns]
        self.variable1_selection.clear()
        self.variable1_selection.addItems(self.column_names)
        self.variable2_selection.clear()
        self.variable2_selection.addItems(self.column_names)

    def get_script(self):
        return self.script_input.toPlainText()

    def accept(self):
        if self.column_name_input.text() == "":
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Error")
            msg_box.setText("Column name cannot be empty!")
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #FFFFFF;
                }
                QPushButton {
                    background-color: #95C843;
                    color: #FFFFFF;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #7AB432;
                }
            """)
            msg_box.exec()
            return
        
        # Update UI to show computing state
        self.ok_button.setText("Computing...")
        self.ok_button.setEnabled(False)
        self.icon_label.setVisible(True)
        
        # Run the computation
        df = self.model.get_data()
        new_column_series = run_compute(self)
        self.model.set_data(df.with_columns(new_column_series))
        self.parent.update_table(1, self.model)
        
        # Reset UI state
        self.icon_label.setVisible(False)
        self.ok_button.setText("Compute")
        self.ok_button.setEnabled(True)
        
        super().accept()
        
    def keyPressEvent(self, event):
        # Allow Escape key to close the dialog
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)