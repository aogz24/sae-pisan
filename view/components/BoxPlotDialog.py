from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QTextEdit, QGroupBox, QComboBox
)
from PyQt6.QtCore import Qt, QStringListModel
from model.BoxPlot import BoxPlot
from controller.Eksploration.EksplorationController import BoxPlotController

class BoxPlotDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None
        
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Box Plot")

        # Menyimpan status variabel yang dipilih
        self.selected_status = {}

        # Layout utama
        main_layout = QVBoxLayout(self)
        content_layout = QHBoxLayout()

        # Layout kiri untuk Data Editor dan Data Output
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

        # Layout tengah untuk tombol
        button_layout = QVBoxLayout()
        self.add_button = QPushButton("→", self)
        self.add_button.clicked.connect(self.add_variable)
        self.remove_button = QPushButton("←", self)
        self.remove_button.clicked.connect(self.remove_variable)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        content_layout.addLayout(button_layout)

        # Layout kanan
        right_layout = QVBoxLayout()
        self.selected_label = QLabel("Variabel", self)
        self.selected_model = QStringListModel()
        self.selected_list = QListView(self)
        self.selected_list.setModel(self.selected_model)
        self.selected_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        # Grup metode
        method_group = QGroupBox("Metode")
        method_layout = QVBoxLayout()
        self.method_combo = QComboBox(self)
        self.method_combo.addItems(["Single Box plot", "Multiple Box Plot"])
        self.method_combo.currentIndexChanged.connect(self.generate_r_script)
        method_layout.addWidget(self.method_combo)
        method_group.setLayout(method_layout)
        right_layout.addWidget(method_group)

        content_layout.addLayout(right_layout)
        main_layout.addLayout(content_layout)

        # Box untuk menampilkan script
        self.script_label = QLabel("Script:", self)
        self.script_box = QTextEdit(self)
        main_layout.addWidget(self.script_label)
        main_layout.addWidget(self.script_box)

        # Tombol Run
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
        return [
            f"{col} [numerik]" if dtype in ['int64', 'float64'] else f"{col} [{dtype}]"
            for col, dtype in zip(model.get_data().columns, model.get_data().dtypes)
        ]

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
        return [
            item.split(" [")[0].replace(" ", "_")
            for item in self.selected_model.stringList()
        ]

    def generate_r_script(self):
        # Get selected columns
        selected_columns = self.get_selected_columns()
        if not selected_columns:
            self.script_box.setPlainText("Tidak ada kolom yang dipilih.")
            return

        # Get selected method
        method = self.method_combo.currentText()
        formatted_columns = ', '.join(f'"{col}"' for col in selected_columns)
        r_script = ""

        # Single Box Plot: If there are multiple variables, create separate plots
        if method == "Single Box plot":
            for col in selected_columns:
                r_script += f"""
# Box plot for {col}
boxplot_{col} <- ggplot(data, aes(y = {col})) +
    geom_boxplot(fill = sample(colors(), 1)) +
    ggtitle("Box Plot: {col}") +
    ylab("{col}") +
    theme_minimal()
"""
    
        # Multiple Box Plot: Combine all selected variables into a single plot
        elif method == "Multiple Box Plot":
            r_script += f"""
# Multiple Box Plot for selected variables
        
# Convert to long format for ggplot compatibility
data_long <- pivot_longer(data, cols = c({formatted_columns}), 
    names_to = "variable", values_to = "value")

# Create multiple box plot
boxplot_multiple <- ggplot(data_long, aes(x = variable, y = value, fill = variable)) +
    geom_boxplot() +
    ggtitle("Multiple Box Plot") +
    xlab("Variable") +
    ylab("Value") +
    theme_minimal()
"""
        # Show script in text box
        self.script_box.setPlainText(r_script)


    def accept(self):
        r_script = self.script_box.toPlainText()
        if not r_script:
            return
        
        box_plot = BoxPlot(self.model1, self.model2, self.parent)
        controller = BoxPlotController(box_plot)
        controller.run_model(r_script)

        self.parent.add_output(script_text = r_script, plot_paths = box_plot.plot)
        self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)

        self.run_button.setEnabled(True)
        self.run_button.setText("Run")
        self.close()

    def closeEvent(self, event):
        self.selected_model.setStringList([])
        self.script_box.setPlainText("")
        event.accept()
