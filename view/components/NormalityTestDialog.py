from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QCheckBox, QTextEdit, QGroupBox, QSizePolicy, QMessageBox, QSpacerItem
)
from PyQt6.QtCore import Qt, QStringListModel, QSize
from PyQt6.QtGui import QIcon
from model.NormalityTest import NormalityTest
from controller.Eksploration.EksplorationController import NormalityTestController


class NormalityTestDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Normality Test")

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

        # Layout tengah: Tombol
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

        # Layout kanan: Variabel yang dipilih, metode, dan grafik
        right_layout = QVBoxLayout()
        self.selected_label = QLabel("Variabel", self)
        self.selected_model = QStringListModel()
        self.selected_list = QListView(self)
        self.selected_list.setModel(self.selected_model)
        self.selected_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        # Grup metode dengan checkbox
        method_group = QGroupBox("Metode")
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

        # Grup grafik
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
        """Mengembalikan daftar nama kolom dengan tipe datanya"""
        return [
            f"{col} [numerik]" if dtype in ['int64', 'float64'] else f"{col} [{dtype}]"
            for col, dtype in zip(model.get_data().columns, model.get_data().dtypes)
        ]
    
    def add_variable(self):
        # Ambil semua indeks yang dipilih dari data editor dan data output
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
        # Ambil semua indeks yang dipilih dari daftar variabel yang dipilih
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
        # Mendapatkan nama variabel yang dipilih
        selected_vars = self.get_selected_columns()
        
        if len(selected_vars) == 0:
            self.script_box.setPlainText("stop('Select at least one variable to test.')")
            return
        
        # Determine the selected methods
        selected_methods = []
        if self.shapiro_checkbox.isChecked():
            selected_methods.append("shapiro")
        if self.jarque_checkbox.isChecked():
            selected_methods.append("jarque_bera")
        if self.lilliefors_checkbox.isChecked():
            selected_methods.append("lilliefors")
        
        if not selected_methods:
            self.script_box.setPlainText("stop('Select at least one testing method.')")
            return
        show_histogram = self.histogram_checkbox.isChecked()
        show_qqplot = self.qqplot_checkbox.isChecked()
        
        r_script = ''
        
        for var in selected_vars:
            for method in selected_methods:
                if method == "shapiro":
                    r_script += f"normality_results_{var}_shapiro <- shapiro.test(data${var})\n"
                elif method == "jarque_bera":
                    r_script += f"normality_results_{var}_jarque <- tseries::jarque.bera.test(data${var})\n"
                elif method == "lilliefors":
                    r_script += f"normality_results_{var}_lilliefors <- nortest::lillie.test(data${var})\n"
            
            # Menambahkan skrip untuk histogram jika dipilih
            if show_histogram:
                r_script += (
                    f"histogram_{var} <- ggplot(data, aes(x = {var})) +\n"
                    f"    geom_histogram(binwidth = 30, color = 'black', fill = 'blue') +\n"
                    f"    ggtitle('Histogram of {var}') +\n"
                    f"    xlab('{var}') +\n"
                    f"    ylab('Frequency')\n"
                )

            # Menambahkan skrip untuk Q-Q plot jika dipilih
            if show_qqplot:
                r_script += (
                    f"qqplot_{var} <- ggplot(data, aes(sample = {var})) +\n"
                    f"    stat_qq() +\n"
                    f"    stat_qq_line(color = 'red') +\n"
                    f"    ggtitle('Q-Q Plot of {var}') +\n"
                    f"    xlab('Theoretical Quantiles') +\n"
                    f"    ylab('Sample Quantiles')\n"
                )
        
        # Menampilkan skrip yang dihasilkan di kotak teks
        self.script_box.setPlainText(r_script)

    def accept(self):
        r_script = self.script_box.toPlainText()
        if not r_script:
            return
        self.run_button.setText("Running...")
        self.icon_label.setVisible(True)
        normality_test = NormalityTest(self.model1, self.model2, self.get_selected_columns(), self.parent)
        # normality_test = NormalityTest(self.model1, self.model2,  self.parent)
        controller = NormalityTestController(normality_test)
        if self.check_variable_selected() and self.check_method_selected():
            controller.run_model(r_script)
            self.parent.add_output(r_script, normality_test.result, normality_test.plot)
            self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)
            self.icon_label.setVisible(False)
            self.run_button.setText("Run")
            QMessageBox.information(self, "Normality Test", "Normality test has been completed.")
            self.close()
        else:
            self.run_button.setText("Run")
            self.icon_label.setVisible(False)
            QMessageBox.warning(self, "Error", "Please select at least one variable and one testing method.")

    def check_variable_selected(self):
        selected_vars = self.get_selected_columns()
        if len(selected_vars) > 0:
            return True
        return False

    def check_method_selected(self):
        if self.shapiro_checkbox.isChecked() or self.jarque_checkbox.isChecked() or self.lilliefors_checkbox.isChecked():
            return True
        return False

    def closeEvent(self, event):
        """Menghapus variabel yang dipilih ketika dialog ditutup."""
        self.selected_model.setStringList([])  # Mengosongkan daftar variabel yang dipilih
        self.script_box.setPlainText("")  # Mengosongkan kotak teks skrip
        event.accept()

