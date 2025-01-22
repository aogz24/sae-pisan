from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListView, QPushButton, QHBoxLayout, 
    QAbstractItemView, QTextEdit
)
from PyQt6.QtCore import QStringListModel, QTimer, Qt
from service.modelling.SAEHBArea import *
from controller.modelling.SaeHBcontroller import SaeHBController
from model.SaeHB import SaeHB

class ModelingSaeHBDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model2 = parent.model2
        self.setWindowTitle("SAE HB Area Modelling")

        self.columns = []

        main_layout = QVBoxLayout()

        # Layout utama untuk membagi area menjadi dua bagian (kiri dan kanan)
        split_layout = QHBoxLayout()

        # Layout kiri untuk daftar variabel
        left_layout = QVBoxLayout()
        self.variables_label = QLabel("Select Variables:")
        self.variables_list = QListView()
        self.variables_model = QStringListModel(self.columns)
        self.variables_list.setModel(self.variables_model)
        self.variables_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        left_layout.addWidget(self.variables_label)
        left_layout.addWidget(self.variables_list)
        
        middle_layout1 = QVBoxLayout()
        self.unassign_button = QPushButton("←")
        middle_layout1.addWidget(self.unassign_button)

        # Layout tengah untuk tombol panah
        middle_layout = QVBoxLayout()
        self.assign_dependent_button = QPushButton("→")
        self.assign_independent_button = QPushButton("→")
        self.assign_vardir_button = QPushButton("→")
        self.assign_major_area_button = QPushButton("→")
        self.assign_dependent_button.clicked.connect(lambda: assign_dependent(self))
        self.assign_independent_button.clicked.connect(lambda: assign_independent(self))
        self.assign_vardir_button.clicked.connect(lambda: assign_vardir(self))
        self.assign_major_area_button.clicked.connect(lambda: assign_major_area(self))
        self.unassign_button.clicked.connect(lambda: unassign_variable(self))
        middle_layout.addWidget(self.assign_dependent_button)
        middle_layout.addWidget(self.assign_independent_button)
        middle_layout.addWidget(self.assign_vardir_button)
        middle_layout.addWidget(self.assign_major_area_button)

        # Layout kanan untuk daftar dependen, independen, vardir, dan major area
        right_layout = QVBoxLayout()
        self.dependent_label = QLabel("Dependent Variable:")
        self.dependent_list = QListView()
        self.dependent_model = QStringListModel()
        self.dependent_list.setModel(self.dependent_model)
        self.dependent_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        right_layout.addWidget(self.dependent_label)
        right_layout.addWidget(self.dependent_list)

        self.independent_label = QLabel("Independent Variable(s):")
        self.independent_list = QListView()
        self.independent_model = QStringListModel()
        self.independent_list.setModel(self.independent_model)
        self.independent_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        right_layout.addWidget(self.independent_label)
        right_layout.addWidget(self.independent_list)

        self.vardir_label = QLabel("Varian Direct:")
        self.vardir_list = QListView()
        self.vardir_model = QStringListModel()
        self.vardir_list.setModel(self.vardir_model)
        right_layout.addWidget(self.vardir_label)
        right_layout.addWidget(self.vardir_list)

        self.major_area_label = QLabel("Major Area:")
        self.major_area_list = QListView()
        self.major_area_model = QStringListModel()
        self.major_area_list.setModel(self.major_area_model)
        right_layout.addWidget(self.major_area_label)
        right_layout.addWidget(self.major_area_list)

        # Menambahkan layout kiri, tengah, dan kanan ke layout utama
        split_layout.addLayout(left_layout)
        split_layout.addLayout(middle_layout1)
        split_layout.addLayout(middle_layout)
        split_layout.addLayout(right_layout)

        main_layout.addLayout(split_layout)

        # Tombol untuk menghasilkan skrip R
        self.option_button = QPushButton("Option")
        self.option_button.setFixedWidth(150)
        self.text_script = QLabel("Script R:")
        self.option_button.clicked.connect(lambda : show_options(self))
        main_layout.addWidget(self.text_script)
        
        # Area teks untuk menampilkan dan mengedit skrip R
        self.r_script_edit = QTextEdit()
        self.r_script_edit.setReadOnly(False)
        main_layout.addWidget(self.r_script_edit)

        # Tombol untuk tindakan dialog
        button_layout = QHBoxLayout()
        button_layout.setObjectName("button_layout")
        self.ok_button = QPushButton("Run Model")
        self.ok_button.setFixedWidth(150)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.option_button)
        button_layout.addWidget(self.ok_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.dependent_var = []
        self.independent_vars = []
        self.vardir_var = []
        self.major_area_var = []
        self.stepwise_method = "None"
        self.iter_update_input = "3"
        self.iter_mcmc_input = "10000"
        self.thin_input = "2"
        self.burn_in_input = "2000"
        self.tau_u_input = "1"

    def set_model(self, model):
        self.model = model
        self.columns = [f"{col} [numerik]" if dtype in ['int64', 'float64'] else f"{col} [{dtype}]" for col, dtype in zip(self.model.get_data().columns, self.model.get_data().dtypes)]
        self.variables_model.setStringList(self.columns)
    
    def accept(self):
        self.ok_button.setText("Running model...")
        self.ok_button.setEnabled(False)
        self.option_button.setEnabled(False)

        view = self.parent
        r_script = get_script(self)
        sae_model = SaeHB(self.model, self.model2, view)
        controller = SaeHBController(sae_model)
        
        controller.run_model(r_script)
        self.parent.update_table(2, sae_model.get_model2())
        label_script = QLabel("Script R:")
        label = QTextEdit()
        label.setPlainText(r_script)
        label.setReadOnly(True)
        label.setFixedHeight(100)
        label_output = QLabel("Output:")
        result_output = QTextEdit()
        result_output.setPlainText(sae_model.result)
        result_output.setReadOnly(True)
        result_output.setFixedHeight(300)
        self.parent.output_layout.addWidget(label_script)
        self.parent.output_layout.addWidget(label)
        self.parent.output_layout.addWidget(label_output)
        self.parent.output_layout.addWidget(result_output)
        self.ok_button.setEnabled(True)
        self.option_button.setEnabled(True)
        self.ok_button.setText("Run Model")
        self.close()