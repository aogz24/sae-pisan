from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QTextEdit, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, QStringListModel, QSize
from PyQt6.QtGui import QIcon
import polars as pl
from model.SummaryData import SummaryData
from controller.Eksploration.EksplorationController import SummaryDataController

class SummaryDataDialog(QDialog):
    """
    A dialog for summarizing data from two models and generating an R script.
    Attributes:
        parent (QWidget): The parent widget.
        model1 (Any): The first data model.
        model2 (Any): The second data model.
        all_columns_model1 (list): List of all columns in model1.
        all_columns_model2 (list): List of all columns in model2.
        selected_status (dict): Dictionary to store the status of selected variables.
        data_editor_label (QLabel): Label for the data editor list.
        data_editor_model (QStringListModel): Model for the data editor list.
        data_editor_list (QListView): List view for the data editor.
        data_output_label (QLabel): Label for the data output list.
        data_output_model (QStringListModel): Model for the data output list.
        data_output_list (QListView): List view for the data output.
        add_button (QPushButton): Button to add variables to the selected list.
        remove_button (QPushButton): Button to remove variables from the selected list.
        selected_label (QLabel): Label for the selected variables list.
        selected_model (QStringListModel): Model for the selected variables list.
        selected_list (QListView): List view for the selected variables.
        script_label (QLabel): Label for the R script.
        icon_label (QLabel): Label for the running icon.
        script_box (QTextEdit): Text box to display the generated R script.
        run_button (QPushButton): Button to run the R script.
    Methods:
        __init__(self, parent): Initializes the dialog with the given parent.
        set_model(self, model1, model2): Sets the data models and updates the lists.
        get_column_with_dtype(self, model): Returns a list of columns with their data types.
        add_variable(self): Adds selected variables to the selected list and generates the R script.
        remove_variable(self): Removes selected variables from the selected list and generates the R script.
        get_selected_columns(self): Returns a list of selected columns without data types.
        generate_r_script(self): Generates the R script based on selected variables.
        accept(self): Runs the R script and handles the result.
        closeEvent(self, event): Resets the dialog when it is closed.
    """
    
    def __init__(self, parent):
        super().__init__(parent) 
        self.parent = parent
        self.model1 = None
        self.model2 = None
        
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Summary Data")

        # Store selected variable status
        self.selected_status = {}

        # Main layout
        main_layout = QVBoxLayout(self)
        content_layout = QHBoxLayout()

        # Left layout for Data Editor and Data Output
        left_layout = QVBoxLayout()

        self.data_editor_label = QLabel("Data Editor", self)
        self.data_editor_model = QStringListModel()
        self.data_editor_list = QListView(self)
        self.data_editor_list.setModel(self.data_editor_model)
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_editor_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_editor_label)
        left_layout.addWidget(self.data_editor_list)

        self.data_output_label = QLabel("Data Output", self)
        self.data_output_model = QStringListModel()
        self.data_output_list = QListView(self)
        self.data_output_list.setModel(self.data_output_model)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_output_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_output_label)
        left_layout.addWidget(self.data_output_list)

        content_layout.addLayout(left_layout)

        # Middle layout for buttons
        button_layout = QVBoxLayout()
        self.add_button = QPushButton("🡆", self)
        self.add_button.clicked.connect(self.add_variable)
        self.add_button.setFixedSize(50, 35) 
        self.add_button.setStyleSheet("font-size: 24px;")  
        self.remove_button = QPushButton("🡄", self)
        self.remove_button.clicked.connect(self.remove_variable)
        self.remove_button.setFixedSize(50, 35)
        self.remove_button.setStyleSheet("font-size: 24px;") 
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        content_layout.addLayout(button_layout)

        # Right layout
        right_layout = QVBoxLayout()
        self.selected_label = QLabel("Variable", self)
        self.selected_model = QStringListModel()
        self.selected_list = QListView(self)
        self.selected_list.setModel(self.selected_model)
        self.selected_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        content_layout.addLayout(right_layout)
        main_layout.addLayout(content_layout)

        # Horizontal layout for label and icon
        script_layout = QHBoxLayout()
        self.script_label = QLabel("R Script:", self)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # Spacer to keep the icon_label on the right end
        spacer = QSpacerItem(40, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Add widgets to the horizontal layout
        script_layout.addWidget(self.script_label)
        script_layout.addItem(spacer)  # Add flexible space
        script_layout.addWidget(self.icon_label)
        self.icon_label.setVisible(False)
        # Box to display script
        self.script_box = QTextEdit(self)

        # Add to the main layout
        main_layout.addLayout(script_layout)  # Add horizontal layout to main layout
        main_layout.addWidget(self.script_box)

        # Run button
        button_row_layout = QHBoxLayout()
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.accept)
        button_row_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(button_row_layout)

        self.data_editor_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.selected_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

    def set_model(self, model1, model2):
        self.model1 = model1
        self.model2 = model2
        self.data_editor_model.setStringList(self.get_column_with_dtype(model1))
        self.data_output_model.setStringList(self.get_column_with_dtype(model2))
        self.all_columns_model1 = self.get_column_with_dtype(model1)
        self.all_columns_model2 = self.get_column_with_dtype(model2)

    def get_column_with_dtype(self, model):
        self.columns = [
            f"{col} [{dtype}]" if dtype == pl.Utf8 else f"{col} [Numeric]"
            for col, dtype in zip(model.get_data().columns, model.get_data().dtypes)
        ]
        return self.columns 

    def add_variable(self):
        selected_indexes = self.data_editor_list.selectedIndexes() + self.data_output_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]
        selected_list = self.selected_model.stringList()

        for item in selected_items:
            if item in self.data_editor_model.stringList():
                editor_list = self.data_editor_model.stringList()
                editor_list.remove(item)
                self.data_editor_model.setStringList(editor_list)
            elif item in self.data_output_model.stringList():
                output_list = self.data_output_model.stringList()
                output_list.remove(item)
                self.data_output_model.setStringList(output_list)

            if item not in selected_list:
                selected_list.append(item)

        self.selected_model.setStringList(selected_list)
        self.generate_r_script()

    def remove_variable(self):
        selected_indexes = self.selected_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]
        selected_list = self.selected_model.stringList()

        for item in selected_items:
            column_name = item.split(' ')[0]
            if column_name in [col.split(' ')[0] for col in self.all_columns_model1]:
                editor_list = self.data_editor_model.stringList()
                editor_list.append(item)
                self.data_editor_model.setStringList(editor_list)
            elif column_name in [col.split(' ')[0] for col in self.all_columns_model2]:
                output_list = self.data_output_model.stringList()
                output_list.append(item)
                self.data_output_model.setStringList(output_list)

            if item in selected_list:
                selected_list.remove(item)

        self.selected_model.setStringList(selected_list)
        self.generate_r_script()

    def get_selected_columns(self):
        return [item.rsplit(" [String]", 1)[0].rsplit(" [Numeric]", 1)[0] for item in self.selected_model.stringList()]


    def generate_r_script(self):
        selected_columns = self.get_selected_columns()
        if not selected_columns:
            self.script_box.setPlainText("")
            return
        formatted_columns = ', '.join(f'"{col}"' for col in selected_columns)
        script = f"summary_results <- summary(data[, c({formatted_columns})])"
        self.script_box.setPlainText(script)


    def accept(self):
        r_script = self.script_box.toPlainText()
        if not r_script:
            QMessageBox.warning(self, "Empty Script", "Please generate a script before running.")
            return
        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")
        self.icon_label.setVisible(True)
        summary_data = SummaryData(self.model1, self.model2, self.parent)
        controller = SummaryDataController(summary_data)
        controller.run_model(r_script)

        if not summary_data.error:
            QMessageBox.information(self, "Summary Data", "Exploration has been completed.")
        else:
            QMessageBox.critical(self, "Summary Data", summary_data.result)
            
        self.parent.add_output(r_script, summary_data.result)
        self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)
        self.icon_label.setVisible(False)
        self.run_button.setText("Run")
        self.run_button.setEnabled(True)
        self.close()

    def closeEvent(self, event):
        self.selected_model.setStringList([])
        self.script_box.setPlainText("")
        event.accept()
