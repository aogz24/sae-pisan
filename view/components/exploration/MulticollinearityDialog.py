
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QCheckBox, QTextEdit, QGroupBox, QMessageBox, QMessageBox, QSpacerItem, QSizePolicy, QToolButton
)
from PyQt6.QtGui import QIcon
import polars as pl
from PyQt6.QtCore import Qt, QStringListModel, QSize
from model.Multicollinearity import Multicollinearity
from controller.Eksploration.EksplorationController import MulticollinearityController
from service.utils.utils import display_script_and_output
from view.components.DragDropListView import DragDropListView

class MulticollinearityDialog(QDialog):
    """
    A dialog for handling multicollinearity analysis in a dataset.
    
    Attributes:
        parent (QWidget): The parent widget.
        model1 (Any): The first data model.
        model2 (Any): The second data model.
        all_columns_model1 (list): List of all columns in model1.
        all_columns_model2 (list): List of all columns in model2.
        selected_status (dict): Dictionary to store the status of selected variables.
        data_editor_label (QLabel): Label for the data editor section.
        data_editor_model (QStringListModel): Model for the data editor list view.
        data_editor_list (QListView): List view for the data editor.
        data_output_label (QLabel): Label for the data output section.
        data_output_model (QStringListModel): Model for the data output list view.
        data_output_list (QListView): List view for the data output.
        remove_button1 (QPushButton): Button to remove selected variables.
        add_dependent_variable_button (QPushButton): Button to add a dependent variable.
        add_independent_variable_button (QPushButton): Button to add independent variables.
        dependent_variable_label (QLabel): Label for the dependent variable section.
        dependent_variable_model (QStringListModel): Model for the dependent variable list view.
        dependent_variable_list (QListView): List view for the dependent variable.
        independent_variable_label (QLabel): Label for the independent variable section.
        independent_variable_model (QStringListModel): Model for the independent variable list view.
        independent_variable_list (QListView): List view for the independent variable.
        regression_line_checkbox (QCheckBox): Checkbox to show regression model.
        script_label (QLabel): Label for the R script section.
        icon_label (QLabel): Label to show running icon.
        script_box (QTextEdit): Text edit box to display the generated R script.
        run_button (QPushButton): Button to run the analysis.
    
    Methods:
        __init__(self, parent): Initializes the dialog with the given parent.
        set_model(self, model1, model2): Sets the data models for the dialog.
        get_column_with_dtype(self, model): Returns columns with their data types.
        add_dependent_variable(self): Adds a selected variable as the dependent variable.
        add_independent_variables(self): Adds selected variables as independent variables.
        remove_variable(self): Removes selected variables from the dependent or independent lists.
        get_selected_dependent_variable(self): Returns the selected dependent variable.
        get_selected_independent_variables(self): Returns the selected independent variables.
        accept(self): Runs the multicollinearity analysis and displays the results.
        closeEvent(self, event): Clears selected variables and script when the dialog is closed.
        generate_r_script(self): Generates the R script for Variance Inflation Factor (VIF) calculation.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Multicollinearity")

        # Store the status of selected variables
        self.selected_status = {}

        # Main layout
        self.main_layout = QVBoxLayout(self)

        # Main content layout
        content_layout = QHBoxLayout()

        # Left layout: Data Editor and Data Output
        left_layout = QVBoxLayout()

        # Data Editor
        self.data_editor_label = QLabel("Data Editor", self)
        self.data_editor_model = QStringListModel()
        self.data_editor_list = DragDropListView(parent=self)
        self.data_editor_list.setModel(self.data_editor_model)
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_editor_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_editor_label)
        left_layout.addWidget(self.data_editor_list)

        # Data Output
        self.data_output_label = QLabel("Data Output", self)
        self.data_output_model = QStringListModel()
        self.data_output_list = DragDropListView(parent=self)
        self.data_output_list.setModel(self.data_output_model)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_output_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_output_label)
        left_layout.addWidget(self.data_output_list)

        content_layout.addLayout(left_layout)

        # Central Layout: Buttons
        button_layout1 = QVBoxLayout()
        self.remove_button1 = QPushButton("🡄", self)
        self.remove_button1.clicked.connect(self.remove_variable) 
        self.remove_button1.setStyleSheet("font-size: 24px;") 
        self.remove_button1.setFixedSize(50,35)
        button_layout1.addStretch(3)
        button_layout1.addWidget(self.remove_button1)
        button_layout1.addStretch(7)

        button_layout2 = QVBoxLayout()
        self.add_dependent_variable_button = QPushButton("🡆", self)
        self.add_dependent_variable_button.clicked.connect(self.add_dependent_variable)
        self.add_dependent_variable_button.setStyleSheet("font-size: 24px;")
        self.add_dependent_variable_button.setFixedSize(50,35)

        self.add_independent_variable_button = QPushButton("🡆", self)  
        self.add_independent_variable_button.clicked.connect(self.add_independent_variables)
        self.add_independent_variable_button.setStyleSheet("font-size: 24px;")
        self.add_independent_variable_button.setFixedSize(50,35)

        button_layout2.addStretch(1)
        button_layout2.addWidget(self.add_dependent_variable_button)
        button_layout2.addStretch(5)
        button_layout2.addWidget(self.add_independent_variable_button)
        button_layout2.addStretch(6)

        # Add both button layouts to content_layout
        content_layout.addLayout(button_layout1)
        content_layout.addLayout(button_layout2)

        # Right layout: Selected variables, methods, and graphs
        right_layout = QVBoxLayout()

        # Dependent variable Axis
        dependent_variable_layout = QVBoxLayout()
        self.dependent_variable_label = QLabel("Dependent Variable", self)
        self.dependent_variable_model = QStringListModel()
        self.dependent_variable_list = DragDropListView(parent=self)
        self.dependent_variable_list.setModel(self.dependent_variable_model)
        self.dependent_variable_list.setSelectionMode(QListView.SelectionMode.MultiSelection)

        # Limit height 
        item_height = 30  
        self.dependent_variable_list.setFixedHeight(item_height + 4)  

        dependent_variable_layout.addWidget(self.dependent_variable_label)
        dependent_variable_layout.addWidget(self.dependent_variable_list)
        right_layout.addLayout(dependent_variable_layout)

        # Independent variable Axis
        independent_variable_layout = QVBoxLayout()
        self.independent_variable_label = QLabel("Independent Variable", self)
        self.independent_variable_model = QStringListModel()
        self.independent_variable_list = DragDropListView(parent=self)
        self.independent_variable_list.setModel(self.independent_variable_model)
        self.independent_variable_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        independent_variable_layout.addWidget(self.independent_variable_label)
        independent_variable_layout.addWidget(self.independent_variable_list)
        right_layout.addLayout(independent_variable_layout, 1)  # Set stretch factor to 1 to fill remaining space

        # Model options group
        model_options_group = QGroupBox("Model Options")  # Change the name of the model options group
        model_options_layout = QVBoxLayout()
        self.regression_line_checkbox = QCheckBox("Show Regression Model", self)  # New checkbox for regression line
        self.regression_line_checkbox.stateChanged.connect(self.generate_r_script)
        model_options_layout.addWidget(self.regression_line_checkbox)  # Add the regression line checkbox to the layout
        model_options_group.setLayout(model_options_layout)
        right_layout.addWidget(model_options_group)

        content_layout.addLayout(right_layout)
        self.main_layout.addLayout(content_layout)

        # Script box
        self.script_layout = QHBoxLayout() 
        self.script_label = QLabel("R Script:", self)

        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight)

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
        self.independent_variable_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.dependent_variable_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

    def handle_drop(self, target_widget, items):
        # Peta widget ke model dan daftar kolom asal
        widget_model_map = {
            self.data_editor_list: (self.data_editor_model, self.all_columns_model1),
            self.data_output_list: (self.data_output_model, self.all_columns_model2),
            self.dependent_variable_list: (self.dependent_variable_model, None),
            self.independent_variable_list: (self.independent_variable_model, None),
        }

        if target_widget not in widget_model_map:
            return

        target_model, allowed_columns = widget_model_map[target_widget]
        current_items = target_model.stringList()

        # Validasi: hanya 1 variabel untuk dependent
        if target_widget == self.dependent_variable_list:
            if len(items) > 1 or len(current_items) >= 1:
                QMessageBox.warning(self, "Warning", "You can only add one variable to the dependent_variable Axis!")
                return

        filtered_items = []
        contains_invalid = False

        for item in items:
            # Tolak jika [String] atau [None] untuk dependent/independent
            if target_widget in [self.dependent_variable_list, self.independent_variable_list]:
                if "[String]" in item or "[None]" in item:
                    contains_invalid = True
                    continue
                filtered_items.append(item)
            else:
                # Editor/output hanya cocokkan dengan kolom aslinya
                column_name = item.split(" ")[0]
                if allowed_columns and any(column_name == col.split(" ")[0] for col in allowed_columns):
                    filtered_items.append(item)

        if contains_invalid:
            QMessageBox.warning(self, "Warning", "Selected variables must be of type Numeric.")
            return

        # Hapus dari semua model lain
        for widget, (model, _) in widget_model_map.items():
            if model == target_model:
                continue
            other_items = model.stringList()
            for item in filtered_items:
                if item in other_items:
                    other_items.remove(item)
            model.setStringList(other_items)

        # Tambahkan ke target jika belum ada
        for item in filtered_items:
            if item not in current_items:
                current_items.append(item)

        # Urutkan kembali jika editor atau output
        if target_widget in [self.data_editor_list, self.data_output_list]:
            if target_widget == self.data_editor_list:
                original_order = self.all_columns_model1
            else:
                original_order = self.all_columns_model2

            reference_map = {col: i for i, col in enumerate(original_order)}
            current_items = sorted(current_items, key=lambda x: reference_map.get(x, float('inf')))

        target_model.setStringList(current_items)
        self.generate_r_script()

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
        """
        Returns a list of columns with simplified data types:
        String, Numeric, or None.
        """
        self.columns = []
        for col, dtype in zip(model.get_data().columns, model.get_data().dtypes):
            if dtype == pl.Utf8:
                tipe = "String"
            elif dtype == pl.Null:
                tipe = "None"
            else:
                tipe = "Numeric"
            self.columns.append(f"{col} [{tipe}]")
        return self.columns
    
    def add_dependent_variable(self):
        if len(self.dependent_variable_model.stringList()) >= 1:
            QMessageBox.warning(self, "Warning", "You can only add one variable to the dependent_variable Axis!")
            return

        selected_indexes = self.data_editor_list.selectedIndexes() + self.data_output_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]

        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a variable first!")
            return

        if len(selected_items) > 1:
            QMessageBox.warning(self, "Warning", "Please select only one variable!")
            return

        item = selected_items[0]

        if "[String]" in item or "[None]" in item:
            QMessageBox.warning(self, "Warning", "Selected variable must be of type Numeric.")
            return

        if item in self.data_editor_model.stringList():
            editor_list = self.data_editor_model.stringList()
            editor_list.remove(item)
            self.data_editor_model.setStringList(editor_list)
        elif item in self.data_output_model.stringList():
            output_list = self.data_output_model.stringList()
            output_list.remove(item)
            self.data_output_model.setStringList(output_list)

        self.dependent_variable_model.setStringList([item])
        self.generate_r_script()

    
    def add_independent_variables(self):
        selected_indexes = self.data_editor_list.selectedIndexes() + self.data_output_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]
        selected_list = self.independent_variable_model.stringList()

        contains_invalid = any("[String]" in item or "[None]" in item for item in selected_items)
        selected_items = [item for item in selected_items if "[String]" not in item and "[None]" not in item]

        if contains_invalid:
            QMessageBox.warning(None, "Warning", "Selected variables must be of type Numeric.")

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

        self.independent_variable_model.setStringList(selected_list)
        self.generate_r_script()

    def remove_variable(self):
        # Get selected indexes from dependent and independent lists
        selected_dependent_variable_indexes = self.dependent_variable_list.selectedIndexes()
        selected_independent_variable_indexes = self.independent_variable_list.selectedIndexes()

        # Get selected items
        selected_items = [index.data() for index in selected_dependent_variable_indexes + selected_independent_variable_indexes]

        # Get current variable lists
        dependent_variable_list = self.dependent_variable_model.stringList()
        independent_variable_list = self.independent_variable_model.stringList()
        editor_list = self.data_editor_model.stringList()
        output_list = self.data_output_model.stringList()

        for item in selected_items:
            # Check if it comes from model1 or model2 based on column name only (without type)
            column_name = item.split(" ")[0]

            if column_name in [col.split(" ")[0] for col in self.all_columns_model1]:
                if item not in editor_list:
                    editor_list.append(item)
            elif column_name in [col.split(" ")[0] for col in self.all_columns_model2]:
                if item not in output_list:
                    output_list.append(item)

            # Remove from dependent and independent lists if present
            if item in dependent_variable_list:
                dependent_variable_list.remove(item)
            if item in independent_variable_list:
                independent_variable_list.remove(item)
            
        # Sort ulang agar urutannya konsisten seperti semula
        editor_list.sort(key=lambda x: self.all_columns_model1.index(x) if x in self.all_columns_model1 else float('inf'))
        output_list.sort(key=lambda x: self.all_columns_model2.index(x) if x in self.all_columns_model2 else float('inf'))

        # Update model-model
        self.data_editor_model.setStringList(editor_list)
        self.data_output_model.setStringList(output_list)
        self.dependent_variable_model.setStringList(dependent_variable_list)
        self.independent_variable_model.setStringList(independent_variable_list)

        # Perbarui script
        self.generate_r_script()

    def get_selected_dependent_variable(self):
        return [
            item.rsplit(" [String]", 1)[0].rsplit(" [Numeric]", 1)[0]
            for item in self.dependent_variable_model.stringList()
        ]
    
    def get_selected_independent_variables(self):
        return [
            item.rsplit(" [String]", 1)[0].rsplit(" [Numeric]", 1)[0]
            for item in self.independent_variable_model.stringList()
        ]
    
    def accept(self):
        r_script = self.script_box.toPlainText()
        if not r_script:
            QMessageBox.warning(self, "Empty Script", "Please generate a script before running.")
            return

        if len(self.get_selected_independent_variables()) < 2:
            QMessageBox.warning(self, "Invalid Independent Variables", "Please select at least two independent variables.")
            return
        
        self.run_button.setText("Running...")
        self.icon_label.setVisible(True)

        multicollinearity = Multicollinearity(self.model1, self.model2)
        
        if self.regression_line_checkbox.isChecked():
            multicollinearity.reg_model = True
        
        controller = MulticollinearityController(multicollinearity)
        controller.run_model(r_script)

        if multicollinearity.error:
            QMessageBox.critical(self, "Multicollinearity", multicollinearity.result)
        else:
            QMessageBox.information(self, "Multicollinearity", "Exploration has been completed.")
        # self.parent.add_output(script_text=r_script, result_text=multicollinearity.result)
        display_script_and_output(self.parent, r_script, multicollinearity.result)
        self.icon_label.setVisible(False)
        self.run_button.setText("Run")
        self.close()

    def closeEvent(self, event):
        """Menghapus variabel yang dipilih ketika dialog ditutup."""
        self.dependent_variable_model.setStringList([]) 
        self.independent_variable_model.setStringList([])
        self.script_box.setPlainText("")  
        event.accept()

    def generate_r_script(self):
        """Function to generate R script for Variance Inflation Factor (VIF) calculation"""
        # Get selected dependent and independent variables
        dependent_var = self.get_selected_dependent_variable()
        independent_vars = self.get_selected_independent_variables()

        # Check if dependent_var and independent_vars are empty
        if not dependent_var or not independent_vars:
            self.script_box.setPlainText("") 
            return

        # Pastikan dependent_var adalah string dan bersihkan tanda kutip
        if isinstance(dependent_var, list):
            dependent_var = dependent_var[0]  
        dependent_var = str(dependent_var).strip("[]'\"")  

        # Format independent variables dengan backticks jika mengandung karakter khusus
        formatted_independent_vars = " + ".join(
            [f"`{var}`" for var in independent_vars]
        )
        
        # Buat script R yang valid
        r_script = (
            f"regression_model <- lm(`{dependent_var}` ~ {formatted_independent_vars}, data=data)\n"
            f"vif_values <- vif(regression_model)\n"
        )

        # Display the generated R script
        self.script_box.setPlainText(r_script)
