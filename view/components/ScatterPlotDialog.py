from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QStringListModel, QSize
import polars as pl
from model.Scatterplot import Scatterplot
from controller.Eksploration.EksplorationController import ScatterPlotController

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QSpacerItem,  QCheckBox, QTextEdit, QGroupBox,QSizePolicy, QMessageBox
)

class ScatterPlotDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Scatter Plot")

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

        # Graph group
        graph_group = QGroupBox("Graph Options") 
        graph_layout = QVBoxLayout()
        self.regression_line_checkbox = QCheckBox("Show Regression Line", self) 
        self.regression_line_checkbox.stateChanged.connect(self.generate_r_script)
        graph_layout.addWidget(self.regression_line_checkbox) 

        self.correlation_checkbox = QCheckBox("Show Correlation", self)  
        self.correlation_checkbox.stateChanged.connect(self.generate_r_script)
        graph_layout.addWidget(self.correlation_checkbox) 

        self.density_plot_checkbox = QCheckBox("Show Density Plot", self) 
        self.density_plot_checkbox.stateChanged.connect(self.generate_r_script)
        graph_layout.addWidget(self.density_plot_checkbox)

        graph_group.setLayout(graph_layout)
        right_layout.addWidget(graph_group)

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
        script_layout.addItem(spacer)  
        script_layout.addWidget(self.icon_label)
        self.icon_label.setVisible(False)
        # Box to display the script
        self.script_box = QTextEdit(self)

        # Add to the main layout
        main_layout.addLayout(script_layout)  
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
            QMessageBox.warning(None, "Warning", "Selected variables must be of type Numeric.")

        print(selected_items) 

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
        return [
            item.split(" [")[0].replace(" ", "_")
            for item in self.selected_model.stringList()
        ]
    

    def accept(self):
        selected_columns = self.get_selected_columns()
        if not r_script:
            QMessageBox.warning(self, "Empty Script", "Please generate a script before running.")
            return
        if len(selected_columns) < 2:
            QMessageBox.warning(self, "Scatter Plot", "Please select at least 2 variables.")
            return

        r_script = self.script_box.toPlainText()
        if not r_script:
            return
        self.run_button.setText("Running...")
        self.icon_label.setVisible(True)
        
        scatter_plot = Scatterplot(self.model1, self.model2, self.parent)
        controller = ScatterPlotController(scatter_plot)
        controller.run_model(r_script)

        self.parent.add_output(script_text=r_script, plot_paths=scatter_plot.plot)
        self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)

        self.icon_label.setVisible(False)
        self.run_button.setText("Run")
        QMessageBox.information(self, "Scatter Plot", "Scatter plot executed successfully.")
        self.close()

    def closeEvent(self, event):
        """Clear selected variables when the dialog is closed."""
        self.selected_model.setStringList([])
        self.script_box.setPlainText("")  
        event.accept()

    def generate_r_script(self):
        selected_columns = self.get_selected_columns()

        # Get checkbox status
        show_regression = self.regression_line_checkbox.isChecked()
        show_correlation = self.correlation_checkbox.isChecked()
        show_density = self.density_plot_checkbox.isChecked()

        # Check the number of selected variables
        if len(selected_columns) < 2:
            self.script_box.setPlainText("Please select at least 2 variables.")
            return

        # Start creating R script for scatterplot matrix
        r_script = (
            f"data_plot <- data[, c({', '.join(f'\"{col}\"' for col in selected_columns)})]\n\n"
            f"scatterplot_ <- ggpairs(\n"
            f"    data_plot,\n"
            f"    lower = list(continuous = {'wrap(\"smooth\", method=\"lm\")' if show_regression else '\"points\"'}),\n"
            f"    upper = list(continuous = {'\"cor\"' if show_correlation else '\"blank\"'}),\n"
            f"    diag = list(continuous = {'\"densityDiag\"' if show_density else '\"blankDiag\"'})\n"
            f")\n"
        )

        # Display the R script in the text box
        self.script_box.setPlainText(r_script)
