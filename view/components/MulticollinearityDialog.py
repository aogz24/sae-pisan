from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QComboBox, QCheckBox, QTextEdit, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QStringListModel
from model.Multicollinearity import Multicollinearity
from controller.Eksploration.EksplorationController import MulticollinearityController


class MulticollinearityDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Multicollinearity")

        # Menyimpan status variabel yang dipilih
        self.selected_status = {}

        # Layout utama
        main_layout = QVBoxLayout(self)

        # Layout konten utama
        content_layout = QHBoxLayout()

        # Layout kiri: Data Editor dan Data Output
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
        self.add_dependent_variable_button.clicked.connect(self.add_variable_dependent_variable)
        self.add_dependent_variable_button.setStyleSheet("font-size: 24px;")
        self.add_dependent_variable_button.setFixedSize(50,35)


        self.add_independent_variable_button = QPushButton("🡆", self)  
        self.add_independent_variable_button.clicked.connect(self.add_variable_independent_variables)
        self.add_independent_variable_button.setStyleSheet("font-size: 24px;")
        self.add_independent_variable_button.setFixedSize(50,35)


        button_layout2.addStretch(2)
        button_layout2.addWidget(self.add_dependent_variable_button)
        button_layout2.addStretch(5)
        button_layout2.addWidget(self.add_independent_variable_button)
        button_layout2.addStretch(5)


        # Menambahkan kedua layout tombol ke content_layout
        content_layout.addLayout(button_layout1)
        content_layout.addLayout(button_layout2)

        # Layout kanan: Variabel yang dipilih, metode, dan grafik
        right_layout = QVBoxLayout()

        # dependent_variable Axis
        dependent_variable_layout = QVBoxLayout()
        self.dependent_variable_label = QLabel("Dependent Variable", self)
        self.dependent_variable_model = QStringListModel()
        self.dependent_variable_list = QListView(self)
        self.dependent_variable_list.setModel(self.dependent_variable_model)
        self.dependent_variable_list.setSelectionMode(QListView.SelectionMode.MultiSelection)

        # Batasi tinggi 
        item_height = 30  
        self.dependent_variable_list.setFixedHeight(item_height + 4)  

        dependent_variable_layout.addWidget(self.dependent_variable_label)
        dependent_variable_layout.addWidget(self.dependent_variable_list)
        right_layout.addLayout(dependent_variable_layout)


        # independent_variable Axis
        independent_variable_layout = QVBoxLayout()
        self.independent_variable_label = QLabel("Independent Variable", self)
        self.independent_variable_model = QStringListModel()
        self.independent_variable_list = QListView(self)
        self.independent_variable_list.setModel(self.independent_variable_model)
        self.independent_variable_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        independent_variable_layout.addWidget(self.independent_variable_label)
        independent_variable_layout.addWidget(self.independent_variable_list)
        right_layout.addLayout(independent_variable_layout)


        # Grup grafik
        model_options_group = QGroupBox("Model Options")  # Change the name of the model options group
        model_options_layout = QVBoxLayout()
        self.regression_line_checkbox = QCheckBox("Show Regression Model", self)  # New checkbox for regression line
        self.regression_line_checkbox.stateChanged.connect(self.generate_r_script)
        model_options_layout.addWidget(self.regression_line_checkbox)  # Add the regression line checkbox to the layout
        model_options_group.setLayout(model_options_layout)
        right_layout.addWidget(model_options_group)

        content_layout.addLayout(right_layout)
        main_layout.addLayout(content_layout)

        # Script box
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
        self.independent_variable_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.dependent_variable_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

    def set_model(self, model1, model2):
        self.model1 = model1
        self.model2 = model2
        self.data_editor_model.setStringList(self.get_column_with_dtype(model1))
        self.data_output_model.setStringList(self.get_column_with_dtype(model2))
        self.all_columns_model1 = self.get_column_with_dtype(model1)
        self.all_columns_model2 = self.get_column_with_dtype(model2)


    def get_column_with_dtype(self, model):
        """Mengembalikan daftar nama kolom dengan tipe datanya"""
        return [
            f"{col} [numerik]" if dtype in ['int64', 'float64'] else f"{col} [{dtype}]"
            for col, dtype in zip(model.get_data().columns, model.get_data().dtypes)
        ]
    

    def add_variable_dependent_variable(self):
        # Check if there is already a variable in the dependent_variable axis
        if len(self.dependent_variable_model.stringList()) >= 1:
            QMessageBox.warning(self, "Warning", "You can only add one variable to the dependent_variable Axis!")
            return  # Do not add if one variable is already present

        # Get all selected indexes from data editor and data output
        selected_indexes = self.data_editor_list.selectedIndexes() + self.data_output_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]

        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a variable first!")
            return  # Show a warning and exit if no variable is selected

        selected_list = self.dependent_variable_model.stringList()

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
                selected_list = [item]  # Ensure only one variable is in the dependent_variable axis
                break  # Exit loop after adding one item

        self.dependent_variable_model.setStringList(selected_list)
        self.generate_r_script()

    
    def add_variable_independent_variables(self):
        # Ambil semua indeks yang dipilih dari data editor dan data output
        selected_indexes = self.data_editor_list.selectedIndexes() + self.data_output_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]
        selected_list = self.independent_variable_model.stringList()

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
        # Ambil indeks yang dipilih dari daftar variabel dependent_variable dan independent_variable
        selected_dependent_variable_indexes = self.dependent_variable_list.selectedIndexes()
        selected_independent_variable_indexes = self.independent_variable_list.selectedIndexes()

        # Ambil nama variabel yang dipilih
        selected_dependent_variable_items = [index.data() for index in selected_dependent_variable_indexes]
        selected_independent_variable_items = [index.data() for index in selected_independent_variable_indexes]

        # Gabungkan kedua daftar variabel yang dipilih
        selected_items = selected_dependent_variable_items + selected_independent_variable_items

        # Ambil daftar semua variabel yang sedang dipilih
        dependent_variable_list = self.dependent_variable_model.stringList()
        independent_variable_list = self.independent_variable_model.stringList()

        # Periksa apakah variabel dikembalikan ke data editor atau data output
        for item in selected_items:
            column_name = item.split(' ')[0]  # Ambil nama kolom sebelum spasi

            if column_name in [col.split(' ')[0] for col in self.all_columns_model1]:
                editor_list = self.data_editor_model.stringList()
                if item not in editor_list:
                    editor_list.append(item)
                    self.data_editor_model.setStringList(editor_list)

            elif column_name in [col.split(' ')[0] for col in self.all_columns_model2]:
                output_list = self.data_output_model.stringList()
                if item not in output_list:
                    output_list.append(item)
                    self.data_output_model.setStringList(output_list)

            # Hapus item dari daftar dependent_variable atau independent_variable jika ada
            if item in dependent_variable_list:
                dependent_variable_list.remove(item)

            if item in independent_variable_list:
                independent_variable_list.remove(item)

        # Perbarui daftar variabel yang dipilih
        self.dependent_variable_model.setStringList(dependent_variable_list)
        self.independent_variable_model.setStringList(independent_variable_list)

        # Perbarui script R setelah perubahan
        self.generate_r_script()

    
    def get_selected_dependent_variable(self):
        return [
            item.split(" [")[0].replace(" ", "_")
            for item in self.dependent_variable_model.stringList()
        ]
    
    def get_selected_independent_variables(self):
        return [
            item.split(" [")[0].replace(" ", "_")
            for item in self.independent_variable_model.stringList()
        ]
    
    def accept(self):
        r_script = self.script_box.toPlainText()
        if not r_script:
            return
        
        multicollinearity = Multicollinearity(self.model1, self.model2, self.parent)
        
        if self.regression_line_checkbox.isChecked():
            multicollinearity.reg_model = True
        
        controller = MulticollinearityController(multicollinearity)
        controller.run_model(r_script)

        self.parent.add_output(script_text=r_script, result_text=multicollinearity.result)
        self.run_button.setEnabled(True)
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

        if not dependent_var:
            self.script_box.setPlainText("No dependent variable selected.")
            return
        if not independent_vars:
            self.script_box.setPlainText("No independent variables selected.")
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
