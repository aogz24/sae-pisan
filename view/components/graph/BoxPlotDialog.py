from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QTextEdit, QGroupBox, QComboBox, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, QStringListModel, QSize
from PyQt6.QtGui import QIcon
import polars as pl
from model.BoxPlot import BoxPlot
from controller.Graph.GraphController import BoxPlotController

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

        self.script_layout = QHBoxLayout()  # Tambahkan self. di sini
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

        # Tambahkan ke layout utama
        main_layout.addLayout(self.script_layout)  # Sekarang script_layout adalah atribut kelas
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
   
    def generate_r_script(self):
        # Get selected columns
        selected_columns = self.get_selected_columns()
        if not selected_columns:
            self.script_box.setPlainText("")
            return

        # Get selected method
        method = self.method_combo.currentText()
        formatted_columns = ', '.join(f'"{col}"' for col in selected_columns)
        r_script = ""

        # Single Box Plot: If there are multiple variables, create separate plots
        if method == "Single Box plot":
            for col in selected_columns:
                r_script += (
                    f"# Box plot for {col}\n"
                    f"boxplot_{col} <- ggplot(data, aes(y = {col})) +\n"
                    f"    geom_boxplot(fill = sample(colors(), 1)) +\n"
                    f"    ggtitle('Box Plot: {col}') +\n"
                    f"    ylab('{col}') +\n"
                    f"    theme_minimal()\n\n"
                )

        # Multiple Box Plot: Combine all selected variables into a single plot
        elif method == "Multiple Box Plot":
            r_script += (
                f"# Convert to long format for ggplot compatibility\n"
                f"data_long <- pivot_longer(data, cols = c({formatted_columns}), \n"
                f"    names_to = 'variable', values_to = 'value')\n\n"
                f"# Create multiple box plot\n"
                f"boxplot_multiple <- ggplot(data_long, aes(x = variable, y = value, fill = variable)) +\n"
                f"    geom_boxplot() +\n"
                f"    ggtitle('Multiple Box Plot') +\n"
                f"    xlab('Variable') +\n"
                f"    ylab('Value') +\n"
                f"    theme_minimal()\n"
            )
        # Show script in text box
        self.script_box.setPlainText(r_script)


    def is_selected_empty(self):
        return len(self.selected_model.stringList()) == 0
    
    def accept(self):
        r_script = self.script_box.toPlainText()
        if not r_script:
            QMessageBox.warning(self, "Empty Script", "Please generate a script before running.")
            return
        if self.is_selected_empty():
            QMessageBox.warning(self, "No Variables Selected", "Please select at least one variable.")
            return
        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")
        self.icon_label.setVisible(True)
        box_plot = BoxPlot(self.model1, self.model2, self.parent)
        controller = BoxPlotController(box_plot)
        controller.run_model(r_script)

        self.parent.add_output(script_text = r_script, plot_paths = box_plot.plot)
        self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)

        self.icon_label.setVisible(False)
        self.run_button.setText("Run")
        QMessageBox.information(self, "Success", "Box plot has been generated successfully.")
        self.run_button.setEnabled(True)
        self.close()

    def closeEvent(self, event):
        self.selected_model.setStringList([])
        self.script_box.setPlainText("")
        event.accept()
