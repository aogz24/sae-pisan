from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QCheckBox, QTextEdit, QGroupBox, QSizePolicy, QMessageBox, QSpacerItem
)
from PyQt6.QtCore import Qt, QStringListModel, QSize
from PyQt6.QtGui import QIcon
import polars as pl
from model.NormalityTest import NormalityTest
from controller.Eksploration.EksplorationController import NormalityTestController


class NormalityTestDialog(QDialog):
    """
    A dialog for performing normality tests on selected variables from two data models.
    Attributes:
        parent (QWidget): The parent widget.
        model1 (Any): The first data model.
        model2 (Any): The second data model.
        all_columns_model1 (list): List of all columns in the first data model.
        all_columns_model2 (list): List of all columns in the second data model.
        selected_status (dict): Dictionary to store the status of selected variables.
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
        shapiro_checkbox (QCheckBox): Checkbox for the Shapiro-Wilk test.
        jarque_checkbox (QCheckBox): Checkbox for the Jarque-Bera test.
        lilliefors_checkbox (QCheckBox): Checkbox for the Lilliefors test.
        histogram_checkbox (QCheckBox): Checkbox for displaying histograms.
        qqplot_checkbox (QCheckBox): Checkbox for displaying Q-Q plots.
        script_layout (QHBoxLayout): Layout for the R script section.
        script_label (QLabel): Label for the R script section.
        icon_label (QLabel): Label for the running icon.
        script_box (QTextEdit): Text box for displaying the generated R script.
        run_button (QPushButton): Button to run the normality test.
    Methods:
        __init__(parent): Initializes the dialog and its components.
        set_model(model1, model2): Sets the data models and updates the data editor and output lists.
        get_column_with_dtype(model): Returns a list of columns with their data types from the given model.
        add_variable(): Adds selected variables to the selected list and updates the R script.
        remove_variable(): Removes selected variables from the selected list and updates the R script.
        get_selected_columns(): Returns a list of selected columns without their data types.
        generate_r_script(): Generates the R script based on selected variables, methods, and graph options.
        accept(): Runs the normality test using the generated R script and displays the results.
        closeEvent(event): Resets the dialog when it is closed.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Normality Test")

        # Store selected variable status
        self.selected_status = {}

        # Main layout
        main_layout = QVBoxLayout(self)

        # Main content layout
        content_layout = QHBoxLayout()

        # Left layout: Data Editor and Data Output
        left_layout = QVBoxLayout()

        # Data Editor
        self.data_editor_label = QLabel("Data Editor", self)
        self.data_editor_model = QStringListModel()
        self.data_editor_list = QListView(self)
        self.data_editor_list.setModel(self.data_editor_model)
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_editor_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_editor_label)
        left_layout.addWidget(self.data_editor_list)

        # Data Output
        self.data_output_label = QLabel("Data Output", self)
        self.data_output_model = QStringListModel()
        self.data_output_list = QListView(self)
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

        # Right layout: Selected variables, methods, and graphs
        right_layout = QVBoxLayout()
        self.selected_label = QLabel("Variables", self)
        self.selected_model = QStringListModel()
        self.selected_list = QListView(self)
        self.selected_list.setModel(self.selected_model)
        self.selected_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        # Method group with checkboxes
        method_group = QGroupBox("Methods")
        method_layout = QVBoxLayout()
        self.shapiro_checkbox = QCheckBox("Shapiro-Wilk")
        self.jarque_checkbox = QCheckBox("Jarque-Bera")
        self.lilliefors_checkbox = QCheckBox("Lilliefors")
        self.shapiro_checkbox.stateChanged.connect(self.generate_r_script)
        self.jarque_checkbox.stateChanged.connect(self.generate_r_script)
        self.lilliefors_checkbox.stateChanged.connect(self.generate_r_script)
        method_layout.addWidget(self.shapiro_checkbox)
        method_layout.addWidget(self.jarque_checkbox)
        method_layout.addWidget(self.lilliefors_checkbox)
        method_group.setLayout(method_layout)
        right_layout.addWidget(method_group)

        # Graph group
        graph_group = QGroupBox("Graph")
        graph_layout = QVBoxLayout()
        self.histogram_checkbox = QCheckBox("Histogram", self)
        self.histogram_checkbox.stateChanged.connect(self.generate_r_script)
        self.qqplot_checkbox = QCheckBox("Q-Q Plot", self)
        self.qqplot_checkbox.stateChanged.connect(self.generate_r_script)
        graph_layout.addWidget(self.histogram_checkbox)
        graph_layout.addWidget(self.qqplot_checkbox)
        graph_group.setLayout(graph_layout)
        right_layout.addWidget(graph_group)

        content_layout.addLayout(right_layout)
        main_layout.addLayout(content_layout)

        self.script_layout = QHBoxLayout() 
        self.script_label = QLabel("R Script:", self)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        spacer = QSpacerItem(40, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.script_layout.addWidget(self.script_label)
        self.script_layout.addItem(spacer)  
        self.script_layout.addWidget(self.icon_label)
        self.icon_label.setVisible(False)
        self.script_box = QTextEdit(self)

        # Add to main layout
        main_layout.addLayout(self.script_layout)  
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
        selected_vars = self.get_selected_columns()
        
        if len(selected_vars) == 0:
            self.script_box.setPlainText("")
            return
        
        selected_methods = []
        if self.shapiro_checkbox.isChecked():
            selected_methods.append("shapiro")
        if self.jarque_checkbox.isChecked():
            selected_methods.append("jarque_bera")
        if self.lilliefors_checkbox.isChecked():
            selected_methods.append("lilliefors")
        
        if not selected_methods:
            self.script_box.setPlainText("")
            return

        show_histogram = self.histogram_checkbox.isChecked()
        show_qqplot = self.qqplot_checkbox.isChecked()

        r_script = ''

        for var in selected_vars:
            safe_var = var.replace(" ", "_")  # Ganti spasi jadi underscore untuk nama variabel

            for method in selected_methods:
                if method == "shapiro":
                    r_script += f"normality_results_{safe_var}_shapiro <- shapiro.test(data$`{var}`)\n"
                elif method == "jarque_bera":
                    r_script += f"normality_results_{safe_var}_jarque <- tseries::jarque.bera.test(data$`{var}`)\n"
                elif method == "lilliefors":
                    r_script += f"normality_results_{safe_var}_lilliefors <- nortest::lillie.test(data$`{var}`)\n"

            if show_histogram:
                r_script += (
                    f"histogram_{safe_var} <- ggplot(data, aes(x = `{var}`)) +\n"
                    f"    geom_histogram(bins = 10, color = 'black', fill = 'blue') +\n"
                    f"    ggtitle('Histogram of {var}') +\n"
                    f"    xlab('{var}') +\n"
                    f"    ylab('Frequency')\n"
                )

            if show_qqplot:
                r_script += (
                    f"qqplot_{safe_var} <- ggplot(data, aes(sample = `{var}`)) +\n"
                    f"    stat_qq() +\n"
                    f"    stat_qq_line(color = 'red') +\n"
                    f"    ggtitle('Q-Q Plot of {var}') +\n"
                    f"    xlab('Theoretical Quantiles') +\n"
                    f"    ylab('Sample Quantiles')\n"
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
        normality_test = NormalityTest(self.model1, self.model2, self.get_selected_columns(), self.parent)
        controller = NormalityTestController(normality_test)
        controller.run_model(r_script)

        if not normality_test.error:
            QMessageBox.information(self, "Normality Test", "Exploration has been completed.")
        else:
            QMessageBox.critical(self, "Normality Test", normality_test.result) 

        self.parent.add_output(r_script, normality_test.result, normality_test.plot)
        self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)
        self.icon_label.setVisible(False)
        self.run_button.setText("Run")
        self.run_button.setEnabled(True)
        self.close()

    def closeEvent(self, event):
        self.selected_model.setStringList([]) 
        self.script_box.setPlainText("") 
        event.accept()
