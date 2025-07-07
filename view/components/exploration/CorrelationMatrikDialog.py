from PyQt6.QtCore import Qt, QStringListModel, QSize
from PyQt6.QtGui import QIcon
import polars as pl
from model.CorrelationMatrix import CorrelationMatrix
from controller.Eksploration.EksplorationController import CorrelationMatrixController
from service.utils.utils import display_script_and_output
from view.components.DragDropListView import DragDropListView

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QTextEdit, QGroupBox, QCheckBox, QSizePolicy, QMessageBox, QSpacerItem, QToolButton
)

class CorrelationMatrixDialog(QDialog):
    """A dialog for selecting variables and generating a correlation matrix using R script.
    
    Attributes:
        parent (QWidget): The parent widget.
        model1 (Any): The first data model.
        model2 (Any): The second data model.
        all_columns_model1 (list): List of all columns in the first data model.
        all_columns_model2 (list): List of all columns in the second data model.
        selected_status (dict): Dictionary to store the selected variable status.
        data_editor_label (QLabel): Label for the data editor section.
        data_editor_model (QStringListModel): Model for the data editor list view.
        data_editor_list (QListView): List view for the data editor.
        data_output_label (QLabel): Label for the data output section.
        data_output_model (QStringListModel): Model for the data output list view.
        data_output_list (QListView): List view for the data output.
        add_button (QPushButton): Button to add selected variables.
        remove_button (QPushButton): Button to remove selected variables.
        selected_label (QLabel): Label for the selected variables section.
        selected_model (QStringListModel): Model for the selected variables list view.
        selected_list (QListView): List view for the selected variables.
        correlation_plot_checkbox (QCheckBox): Checkbox to show correlation plot.
        script_layout (QHBoxLayout): Layout for the R script section.
        script_label (QLabel): Label for the R script section.
        icon_label (QLabel): Label to show running icon.
        script_box (QTextEdit): Text box to display the generated R script.
        run_button (QPushButton): Button to run the generated R script.
    
    Methods:
        __init__(self, parent): Initializes the dialog with the given parent.
        set_model(self, model1, model2): Sets the data models for the dialog.
        get_column_with_dtype(self, model): Returns the columns with their data types.
        add_variable(self): Adds selected variables to the selected list.
        remove_variable(self): Removes selected variables from the selected list.
        get_selected_columns(self): Returns the selected columns without data types.
        generate_r_script(self): Generates the R script for the correlation matrix.
        accept(self): Runs the generated R script and handles the result.
        closeEvent(self, event): Handles the close event of the dialog.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None
        
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Correlation")

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

        # Middle layout: Buttons
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
        self.selected_label = QLabel("Variables", self)
        self.selected_model = QStringListModel()
        self.selected_list = DragDropListView(parent=self)
        self.selected_list.setModel(self.selected_model)
        self.selected_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        # Method group with checkboxes
        method_group = QGroupBox("Methods")
        method_layout = QVBoxLayout()
        self.pearson_checkbox = QCheckBox("Pearson")
        self.spearman_checkbox = QCheckBox("Spearman")
        self.kendall_checkbox = QCheckBox("Kendall")
        self.pearson_checkbox.stateChanged.connect(self.generate_r_script)
        self.spearman_checkbox.stateChanged.connect(self.generate_r_script)
        self.kendall_checkbox.stateChanged.connect(self.generate_r_script)
        method_layout.addWidget(self.pearson_checkbox)
        method_layout.addWidget(self.spearman_checkbox)
        method_layout.addWidget(self.kendall_checkbox)
        method_group.setLayout(method_layout)
        right_layout.addWidget(method_group)
        
        # Graph group
        graph_group = QGroupBox("Visualization")
        graph_layout = QVBoxLayout()
        self.correlation_plot_checkbox = QCheckBox("Show Correlation Plot", self)
        self.correlation_plot_checkbox.stateChanged.connect(self.generate_r_script)
        graph_layout.addWidget(self.correlation_plot_checkbox)
        graph_group.setLayout(graph_layout)
        right_layout.addWidget(graph_group)

        content_layout.addLayout(right_layout)
        self.main_layout.addLayout(content_layout)

        self.script_layout = QHBoxLayout()  
        self.script_label = QLabel("R Script:", self)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        spacer = QSpacerItem(40, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

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

        self.data_editor_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.selected_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

    def handle_drop(self, target_widget, items):
        # Mapping widget to model
        widget_model_map = {
            self.data_editor_list: (self.data_editor_model, self.all_columns_model1),
            self.data_output_list: (self.data_output_model, self.all_columns_model2),
            self.selected_list: (self.selected_model, None),  # selected_list can accept all
        }

        if target_widget not in widget_model_map:
            return

        target_model, allowed_columns = widget_model_map[target_widget]
        current_items = target_model.stringList()

        filtered_items = []

        for item in items:
            # If dropped to selected, accept all
            if target_widget == self.selected_list:
                filtered_items.append(item)
            else:
                # Dropped to editor/output? Only accept those from its own column
                column_name = item.split(" ")[0]
                if allowed_columns and column_name in [col.split(" ")[0] for col in allowed_columns]:
                    filtered_items.append(item)

        # Add to target_model
        for item in filtered_items:
            if item not in current_items:
                current_items.append(item)

        # Remove from other models (except target)
        for other_widget, (model, _) in widget_model_map.items():
            if model == target_model:
                continue
            other_items = model.stringList()
            for item in filtered_items:
                if item in other_items:
                    other_items.remove(item)
            model.setStringList(other_items)

        # Add & sort according to initial position (if editor/output)
        if target_widget == self.data_editor_list:
            ordered = [col for col in self.all_columns_model1 if col in current_items]
            target_model.setStringList(ordered)
        elif target_widget == self.data_output_list:
            ordered = [col for col in self.all_columns_model2 if col in current_items]
            target_model.setStringList(ordered)
        else:
            target_model.setStringList(current_items)

    def set_model(self, model1, model2):
        self.model1 = model1
        self.model2 = model2
        self.data_editor_model.setStringList(self.get_column_with_dtype(model1))
        self.data_output_model.setStringList(self.get_column_with_dtype(model2))
        self.all_columns_model1 = self.get_column_with_dtype(model1)
        self.all_columns_model2 = self.get_column_with_dtype(model2)

    def toggle_r_script_visibility(self):
        """
        Toggles the visibility of the R script text edit area and updates the toggle button text.
        """
        is_visible = self.script_box.isVisible()
        self.script_box.setVisible(not is_visible)
        if not is_visible:
            self.toggle_script_button.setIcon(QIcon("assets/less.svg"))
        else:
            self.toggle_script_button.setIcon(QIcon("assets/more.svg"))

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
        
        contains_string = any("[String]" in item for item in selected_items)   
        selected_items = [item for item in selected_items if "[String]" not in item] 

        if contains_string:
            QMessageBox.warning(self, "Warning", "Selected variables must be of type Numeric.")

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
        return [item.rsplit(" [String]", 1)[0].rsplit(" [Numeric]", 1)[0] for item in self.selected_model.stringList()]

    def generate_r_script(self):
        """Function to generate R script for Correlation Matrix using ggcorrplot"""
        selected_columns = self.get_selected_columns()
        if not selected_columns:
            self.script_box.setPlainText("")
            return

        formatted_columns = ', '.join(f'"{col}"' for col in selected_columns)
        r_script = ""

        # Step 1: Generate the correlation matrix
        for method, checkbox in [("pearson", self.pearson_checkbox), ("spearman", self.spearman_checkbox), ("kendall", self.kendall_checkbox)]:
            if checkbox.isChecked():
                correlation_matrix_method = f"correlation_matrix_{method}"
                r_script += f"{correlation_matrix_method} <- cor(data[, c({formatted_columns})], use='complete.obs', method='{method}')\n"

            if self.correlation_plot_checkbox.isChecked():
                r_script += (
                    f"correlation_plot_{method} <- ggcorrplot({correlation_matrix_method}, "
                    f"method = 'square', type = 'upper', lab = TRUE) + "
                    f"ggtitle('{method.title()} Correlation Matrix')\n\n"
                )
        self.script_box.setPlainText(r_script)

    def accept(self):
        r_script = self.script_box.toPlainText()
        if not r_script:
            QMessageBox.warning(self, "Empty Script", "Please generate a script before running.")
            return
        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")
        self.icon_label.setVisible(True)
        correlation_matrix = CorrelationMatrix(self.model1, self.model2)
        controller = CorrelationMatrixController(correlation_matrix)
        controller.run_model(r_script)

        if not correlation_matrix.error:
            QMessageBox.information(self, "Correlation Matrix", "Exploration has been completed.")
        else:
            QMessageBox.warning(self, "Correlation Matrix", correlation_matrix.result)

        # self.parent.add_output(script_text = r_script, result_text =  correlation_matrix.result ,plot_paths = correlation_matrix.plot)
        display_script_and_output(self.parent, r_script, correlation_matrix.result, correlation_matrix.plot)
        self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)

        self.icon_label.setVisible(False)
        self.run_button.setText("Run")
        self.run_button.setEnabled(True)
        self.close()

    def closeEvent(self, event):
        self.selected_model.setStringList([])
        self.script_box.setPlainText("")
        event.accept()
