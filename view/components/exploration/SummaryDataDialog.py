from PyQt6.QtCore import Qt, QStringListModel, QSize
from PyQt6.QtGui import QIcon
import polars as pl
from model.SummaryData import SummaryData
from controller.Eksploration.EksplorationController import SummaryDataController
from service.utils.utils import display_script_and_output
from view.components.DragDropListView import DragDropListView

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QTextEdit, QSizePolicy, QMessageBox, QToolButton
)

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
        data_editor_list (DragDropListView): List view for the data editor.
        data_output_label (QLabel): Label for the data output list.
        data_output_model (QStringListModel): Model for the data output list.
        data_output_list (DragDropListView): List view for the data output.
        add_button (QPushButton): Button to add variables to the selected list.
        remove_button (QPushButton): Button to remove variables from the selected list.
        selected_label (QLabel): Label for the selected variables list.
        selected_model (QStringListModel): Model for the selected variables list.
        selected_list (DragDropListView): List view for the selected variables.
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
        handle_drop(self, target_widget, items): Handles the drop event for the list views.
        toggle_r_script_visibility(self): Toggles the visibility of the R script text edit area.
    """
    
    def __init__(self, parent):
        super().__init__(parent) 
        self.parent = parent
        self.model1 = None
        self.model2 = None
        
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Data Summary")

        # Store selected variable status
        self.selected_status = {}

        # Main layout
        self.main_layout = QVBoxLayout(self)
        content_layout = QHBoxLayout()

        # Left layout for Data Editor and Data Output
        left_layout = QVBoxLayout()

        self.data_editor_label = QLabel("Data Editor", self)
        self.data_editor_model = QStringListModel()
        self.data_editor_list = DragDropListView(parent=self)
        self.data_editor_list.setModel(self.data_editor_model)
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_editor_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_editor_label)
        left_layout.addWidget(self.data_editor_list)

        self.data_output_label = QLabel("Data Output", self)
        self.data_output_model = QStringListModel()
        self.data_output_list = DragDropListView(parent=self)
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
        self.selected_list = DragDropListView(parent=self)
        self.selected_list.setModel(self.selected_model)
        self.selected_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        content_layout.addLayout(right_layout)
        self.main_layout.addLayout(content_layout)

        # Horizontal layout for label and icon
        self.script_label = QLabel("R Script:", self)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
        self.toggle_script_button = QToolButton()
        self.toggle_script_button.setIcon(QIcon("assets/more.svg"))
        self.toggle_script_button.setIconSize(QSize(16, 16))
        self.toggle_script_button.setCheckable(True)
        self.toggle_script_button.setChecked(False)
        self.toggle_script_button.clicked.connect(self.toggle_r_script_visibility)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.script_label)
        self.button_layout.addWidget(self.toggle_script_button)
        self.button_layout.setAlignment(self.script_label, Qt.AlignmentFlag.AlignLeft)
        self.button_layout.setAlignment(self.toggle_script_button, Qt.AlignmentFlag.AlignLeft)

        self.script_layout = QHBoxLayout()
        self.script_layout.addLayout(self.button_layout)
        self.script_layout.addStretch()
        self.script_layout.addWidget(self.icon_label)
        self.icon_label.setVisible(False)
        self.script_layout.setAlignment(self.script_label, Qt.AlignmentFlag.AlignLeft)

        self.main_layout.addLayout(self.script_layout)

        self.script_box = QTextEdit()
        self.script_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.script_box.setReadOnly(False)
        self.script_box.setVisible(False)
        self.main_layout.addWidget(self.script_box)

        # Run button
        button_row_layout = QHBoxLayout()
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.accept)
        button_row_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.main_layout.addLayout(button_row_layout)

        # Selection mode for list view
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.selected_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

    def handle_drop(self, target_widget, items):
        # Mapping widget to model
        widget_model_map = {
            self.data_editor_list: (self.data_editor_model, self.all_columns_model1),
            self.data_output_list: (self.data_output_model, self.all_columns_model2),
            self.selected_list: (self.selected_model, None),
        }

        if target_widget not in widget_model_map:
            return

        target_model, allowed_columns = widget_model_map[target_widget]
        current_items = target_model.stringList()

        filtered_items = []
        contains_none = False

        for item in items:
            if "[NULL]" in item:
                contains_none = True
                continue

            if target_widget == self.selected_list:
                filtered_items.append(item)
            else:
                column_name = item.split(" ")[0]
                if allowed_columns and column_name in [col.split(" ")[0] for col in allowed_columns]:
                    filtered_items.append(item)

        # ❗️Tampilkan peringatan jika ada item [NULL]
        if contains_none:
            QMessageBox.warning(self, "Warning", "Cannot drop variables with type None.")

        # Tambahkan item yang lolos ke model target
        for item in filtered_items:
            if item not in current_items:
                current_items.append(item)

        # Hapus dari model lain
        for other_widget, (model, _) in widget_model_map.items():
            if model == target_model:
                continue
            other_items = model.stringList()
            for item in filtered_items:
                if item in other_items:
                    other_items.remove(item)
            model.setStringList(other_items)

        # Atur ulang urutan
        if target_widget == self.data_editor_list:
            ordered = [col for col in self.all_columns_model1 if col in current_items]
            target_model.setStringList(ordered)
        elif target_widget == self.data_output_list:
            ordered = [col for col in self.all_columns_model2 if col in current_items]
            target_model.setStringList(ordered)
        else:
            target_model.setStringList(current_items)

        self.generate_r_script()


    def toggle_r_script_visibility(self):
        """
        Toggles the visibility of the R script text edit area and updates the toggle button icon.
        """
        is_visible = self.script_box.isVisible()
        self.script_box.setVisible(not is_visible)
        if not is_visible:
            self.toggle_script_button.setIcon(QIcon("assets/less.svg"))
        else:
            self.toggle_script_button.setIcon(QIcon("assets/more.svg"))
    
    def set_model(self, model1, model2):
        """
        Sets the data models and updates the lists in the dialog.
        
        Args:
            model1 (Any): The first data model.
            model2 (Any): The second data model.
        """
        self.model1 = model1
        self.model2 = model2
        self.data_editor_model.setStringList(self.get_column_with_dtype(model1))
        self.data_output_model.setStringList(self.get_column_with_dtype(model2))
        self.all_columns_model1 = self.get_column_with_dtype(model1)
        self.all_columns_model2 = self.get_column_with_dtype(model2)

    def get_column_with_dtype(self, model):
        """
        Returns a list of columns with simplified data types:
        String, Numeric, or None.
        """
        self.columns = []
        for col, dtype in zip(model.get_data().columns, model.get_data().dtypes):
            if dtype == pl.Utf8:
                tipe = "String"
            elif dtype == pl.Null:
                tipe = "NULL"
            else:
                tipe = "Numeric"
            self.columns.append(f"{col} [{tipe}]")
        return self.columns

    def add_variable(self):
        """
        Adds selected variables to the selected list and generates the R script.
        Variables of type None are not allowed.
        """
        selected_indexes = self.data_editor_list.selectedIndexes() + self.data_output_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]

        contains_none = any("[NULL]" in item for item in selected_items)
        if contains_none:
            QMessageBox.warning(self, "Warning", "Selected variables must not be of type None.")
            return

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
        """
        Removes selected variables from the selected list and generates the R script.
        """
        selected_indexes = self.selected_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]

        selected_list = self.selected_model.stringList()
        editor_list = self.data_editor_model.stringList()
        output_list = self.data_output_model.stringList()

        for item in selected_items:
            column_name = item.split(" ")[0]

            # Check if the item belongs to model1 (editor) or model2 (output)
            if column_name in [col.split(" ")[0] for col in self.all_columns_model1]:
                if item not in editor_list:
                    editor_list.append(item)
                    # Re-sort according to all_columns_model1
                    editor_list = [col for col in self.all_columns_model1 if col in editor_list]

            elif column_name in [col.split(" ")[0] for col in self.all_columns_model2]:
                if item not in output_list:
                    output_list.append(item)
                    # Re-sort according to all_columns_model2
                    output_list = [col for col in self.all_columns_model2 if col in output_list]

            # Remove from selected
            if item in selected_list:
                selected_list.remove(item)

        self.selected_model.setStringList(selected_list)
        self.data_editor_model.setStringList(editor_list)
        self.data_output_model.setStringList(output_list)
        self.generate_r_script()

    def get_selected_columns(self):
        """
        Returns a list of selected columns without data types.
        
        Returns:
            list: A list of selected column names.
        """
        return [item.rsplit(" [String]", 1)[0].rsplit(" [Numeric]", 1)[0] for item in self.selected_model.stringList()]

    def generate_r_script(self):
        """
        Generates the R script based on selected variables and updates the script box.
        """
        selected_columns = self.get_selected_columns()
        if not selected_columns:
            self.script_box.setPlainText("")
            return
        formatted_columns = ', '.join(f'"{col}"' for col in selected_columns)
        script = f"summary_results <- summary(data[, c({formatted_columns})])"
        self.script_box.setPlainText(script)

    def accept(self):
        """
        Runs the R script and handles the result, displaying messages based on success or failure.
        """
        r_script = self.script_box.toPlainText()
        selected_columns = self.get_selected_columns()
        if not r_script:
            if not selected_columns:
                QMessageBox.warning(self, "No Variables", "Please select at least one numeric variable.")
                return
            else:
                QMessageBox.warning(self, "Empty Script", "Please generate a script before running.")
                return
        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")
        self.icon_label.setVisible(True)
        summary_data = SummaryData(self.model1, self.model2)

        controller = SummaryDataController(summary_data)
        controller.run_model(r_script)

        if summary_data.error:
            QMessageBox.critical(self, "Summary Data", summary_data.result)
        #     QMessageBox.information(self, "Summary Data", "Exploration has been completed.")
        # else:
            
            
        # self.parent.add_output(r_script, summary_data.result)
        print(r_script)
        display_script_and_output(self.parent, r_script, summary_data.result)
        self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)
        self.icon_label.setVisible(False)
        self.run_button.setText("Run")
        self.run_button.setEnabled(True)
        self.close()

    def closeEvent(self, event):
        """
        Resets the dialog when it is closed.
        
        Args:
            event (QCloseEvent): The close event.
        """
        self.selected_model.setStringList([])
        self.script_box.setPlainText("")
        event.accept()
