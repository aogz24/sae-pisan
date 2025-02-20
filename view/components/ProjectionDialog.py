from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListView, QPushButton, QHBoxLayout, 
    QAbstractItemView, QTextEdit, QSizePolicy, QScrollArea, QWidget, QComboBox, QLineEdit
)
from PyQt6.QtCore import QStringListModel, QTimer, Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from service.modelling.ProjectionService import assign_as_factor, assign_auxilary, assign_domains, assign_index, assign_of_interest, assign_strata, assign_weight, get_script, show_options, unassign_variable
from controller.modelling.ProjectionController import ProjectionController
from model.ProjectionModel import Projection
from PyQt6.QtWidgets import QMessageBox
import polars as pl
from service.utils.utils import display_script_and_output, check_script
from service.utils.enable_disable import enable_service, disable_service

class ProjectionDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model2 = parent.model2
        self.setWindowTitle("Projection SAE")
        self.setFixedHeight(700)

        self.columns = []

        main_layout = QVBoxLayout()

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

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
        self.unassign_button.setObjectName("arrow_button")
        middle_layout1.addWidget(self.unassign_button)

        # Layout tengah untuk tombol panah
        middle_layout = QVBoxLayout()
        self.assign_of_interest_button = QPushButton("→")
        self.assign_of_interest_button.setObjectName("arrow_button")
        self.assign_aux_button = QPushButton("→")
        self.assign_aux_button.setObjectName("arrow_button")
        self.assign_as_factor_button = QPushButton("→")
        self.assign_as_factor_button.setObjectName("arrow_button")
        self.assign_domains_button = QPushButton("→")
        self.assign_domains_button.setObjectName("arrow_button")
        self.assign_index_button = QPushButton("→")
        self.assign_index_button.setObjectName("arrow_button")
        self.assign_aux_mean_button = QPushButton("→")
        self.assign_weight_button = QPushButton("→")
        self.assign_weight_button.setObjectName("arrow_button")
        self.assign_strata_button = QPushButton("→")
        self.assign_strata_button.setObjectName("arrow_button")

        self.assign_of_interest_button.clicked.connect(lambda: assign_of_interest(self))
        self.assign_aux_button.clicked.connect(lambda: assign_auxilary(self))
        self.assign_index_button.clicked.connect(lambda: assign_index(self))
        self.assign_as_factor_button.clicked.connect(lambda: assign_as_factor(self))
        self.assign_domains_button.clicked.connect(lambda: assign_domains(self))
        self.assign_weight_button.clicked.connect(lambda: assign_weight(self))
        self.assign_strata_button.clicked.connect(lambda: assign_strata(self))
        self.unassign_button.clicked.connect(lambda: unassign_variable(self))
        middle_layout.addWidget(self.assign_of_interest_button)
        middle_layout.addWidget(self.assign_aux_button)
        middle_layout.addWidget(self.assign_as_factor_button)
        middle_layout.addWidget(self.assign_domains_button)
        middle_layout.addWidget(self.assign_index_button)
        middle_layout.addWidget(self.assign_weight_button)
        middle_layout.addWidget(self.assign_strata_button)

        
        
        # Layout kanan untuk daftar dependen, independen, vardir, dan major area
        right_layout = QVBoxLayout()
        self.of_interest_label = QLabel("Variable of interest:")
        self.of_interest_list = QListView()
        self.of_interest_model = QStringListModel()
        self.of_interest_list.setModel(self.of_interest_model)
        self.of_interest_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.of_interest_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.of_interest_label)
        right_layout.addWidget(self.of_interest_list)

        self.auxilary_label = QLabel("Auxilary Variable(s):")
        self.auxilary_list = QListView()
        self.auxilary_model = QStringListModel()
        self.auxilary_list.setModel(self.auxilary_model)
        self.auxilary_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.auxilary_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.auxilary_label)
        right_layout.addWidget(self.auxilary_list)

        self.as_factor_label = QLabel("as Factor of Auxilary Variable(s):")
        self.as_factor_list = QListView()
        self.as_factor_model = QStringListModel()
        self.as_factor_list.setModel(self.as_factor_model)
        self.as_factor_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.as_factor_label)
        right_layout.addWidget(self.as_factor_list)
        
        self.domain_label = QLabel("Domain:")
        self.domain_list = QListView()
        self.domain_model = QStringListModel()
        self.domain_list.setModel(self.domain_model)
        self.domain_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.domain_label)
        right_layout.addWidget(self.domain_list)
        
        self.index_label = QLabel("Index number of Area:")
        self.index_list = QListView()
        self.index_model = QStringListModel()
        self.index_list.setModel(self.index_model)
        self.index_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.index_label)
        right_layout.addWidget(self.index_list)
        

        self.weight_label = QLabel("Weight:")
        self.weight_list = QListView()
        self.weight_model = QStringListModel()
        self.weight_list.setModel(self.weight_model)
        self.weight_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.weight_label)
        right_layout.addWidget(self.weight_list)

        self.strata_label = QLabel("Strata:")
        self.strata_list = QListView()
        self.strata_model = QStringListModel()
        self.strata_list.setModel(self.strata_model)
        self.strata_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.strata_label)
        right_layout.addWidget(self.strata_list)
        
        # Menambahkan layout kiri, tengah, dan kanan ke layout utama
        split_layout.addLayout(left_layout)
        split_layout.addLayout(middle_layout1)
        split_layout.addLayout(middle_layout)
        split_layout.addLayout(right_layout)

        scroll_layout.addLayout(split_layout)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Tombol untuk menghasilkan skrip R
        self.option_button = QPushButton("Option")
        self.option_button.setFixedWidth(150)
        self.text_script = QLabel("R Script:")
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # Create a horizontal layout to place the text_script and icon_label in one row
        script_layout = QHBoxLayout()
        script_layout.addWidget(self.text_script)
        script_layout.addWidget(self.icon_label)
        self.icon_label.setVisible(False)
        script_layout.setAlignment(self.text_script, Qt.AlignmentFlag.AlignLeft)
        script_layout.setAlignment(self.icon_label, Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(script_layout)
        self.option_button.clicked.connect(lambda : show_options(self))
        
        # Area teks untuk menampilkan dan mengedit skrip R
        self.r_script_edit = QTextEdit()
        self.r_script_edit.setFixedHeight(150)
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

        self.of_interest_var = []
        self.auxilary_vars = []
        self.index_var = []
        self.as_factor_var = []
        self.domain_var = []
        self.weight_var = []
        self.strata_var = []
        self.selection_method = "None"
        self.projection_method= "Linear"
        self.metric = "NULL"
        self.k_fold = "3"
        self.grid="10"
        self.epoch="10"
        self.hidden_unit = "5"
        self.learning_rate = "0.01"

    
    def show_prerequisites(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Prerequisites")
        dialog.setModal(True)  # Membuat dialog tetap di atas

        layout = QVBoxLayout(dialog)

        # Separator selection
        layout.addWidget(QLabel("Separator:"))
        self.separator_combo = QComboBox()
        self.separator_combo.addItems([".", ";", "|"])
        layout.addWidget(self.separator_combo)

        # Variable position selection
        layout.addWidget(QLabel("Variable position relative to separator:"))
        self.var_position_combo = QComboBox()
        self.var_position_combo.addItems(["Before", "After"])
        layout.addWidget(self.var_position_combo)

        layout.addWidget(QLabel("The difference between data projection and model (after separator)"))

        # Model name input
        layout.addWidget(QLabel("Model name:"))
        self.model_name_edit = QLineEdit()  # Menggunakan QLineEdit karena lebih cocok untuk input pendek
        layout.addWidget(self.model_name_edit)

        # Projection name input
        layout.addWidget(QLabel("Projection name:"))
        self.projection_name_edit = QLineEdit()  
        layout.addWidget(self.projection_name_edit)
        
        # Model selection
        layout.addWidget(QLabel("Select Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Linear", "Logistic", "SVM Linear", "SVM RBF", "Gradient Boost", "Neural Network"])
        layout.addWidget(self.model_combo)

        # Button Layout
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Execute the dialog and check if accepted
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.separator = self.separator_combo.currentText()
            self.var_position = self.var_position_combo.currentText()
            self.model_name = self.model_name_edit.text()
            self.projection_name = self.projection_name_edit.text()
            self.projection_method = self.model_combo.currentText()

            # Filtering unique columns based on separator position
            unique_columns = {}
            for col, dtype in zip(self.model.get_data().columns, self.model.get_data().dtypes):
                col_key = col.split(self.separator)[0] if self.var_position == "Before" else col.split(self.separator)[-1]

                # Format dengan tipe data
                col_key_formatted = f"{col_key} [{dtype}]" if dtype == pl.Utf8 else f"{col_key} [Numeric]"
                
                # Menyimpan hanya jika belum ada dalam unique_columns
                if col_key not in unique_columns:
                    unique_columns[col_key] = col_key_formatted

            self.columns_new = list(unique_columns.values())
            self.variables_model.setStringList(self.columns_new)
            
            return True

        return False
    
    def set_model(self, model):
        self.model = model
        self.columns = [f"{col} [{dtype}]" if dtype == pl.Utf8 else f"{col} [Numeric]" for col, dtype in zip(self.model.get_data().columns, self.model.get_data().dtypes)]
        self.of_interest_model.setStringList([])
        self.auxilary_model.setStringList([])
        self.as_factor_model.setStringList([])
        self.domain_model.setStringList([])
        self.index_model.setStringList([])
        self.weight_model.setStringList([])
        self.strata_model.setStringList([])
        
    
    def accept(self):
        if not self.of_interest_var or self.of_interest_var == [""]:
            QMessageBox.warning(self, "Warning", "Variable of interest cannot be empty.")
            self.ok_button.setEnabled(True)
            self.option_button.setEnabled(True)
            self.ok_button.setText("Run Model")
            return
        
        r_script = get_script(self)
        if not check_script(r_script):
            return
        disable_service(self)

        view = self.parent
        sae_model = Projection(self.model, self.model2, view)
        controller = ProjectionController(sae_model)
        
        controller.run_model(r_script)
        self.parent.update_table(2, sae_model.get_model2())
        display_script_and_output(self.parent, r_script, sae_model.result)
        enable_service(self)
        self.close()