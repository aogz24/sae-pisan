from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListView, QPushButton, QHBoxLayout, 
    QAbstractItemView, QTextEdit, QSizePolicy, QScrollArea, QWidget
)
from PyQt6.QtCore import QStringListModel, QTimer, Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from service.modelling.SaeEblupUnit import *
from controller.modelling.SaeEblupUnitController import SaeEblupUnitController
from model.SaeEblupUnit import SaeEblupUnit
from PyQt6.QtWidgets import QMessageBox
import polars as pl
from service.utils.utils import display_script_and_output, check_script
from service.utils.enable_disable import enable_service, disable_service
import threading
import contextvars

class ModelingSaeUnitDialog(QDialog):
    """
    A dialog for modeling SAE Eblup Unit.
    Signals:
        run_model_finished (object, object, object, object): Emitted when the model run is finished.
    Attributes:
        parent (QWidget): The parent widget.
        model2 (object): The second model from the parent.
        columns (list): List of column names.
        variables_label (QLabel): Label for the variables list.
        variables_list (QListView): List view for selecting variables.
        variables_model (QStringListModel): Model for the variables list.
        unassign_button (QPushButton): Button to unassign variables.
        assign_of_interest_button (QPushButton): Button to assign variable of interest.
        assign_aux_button (QPushButton): Button to assign auxiliary variables.
        assign_as_factor_button (QPushButton): Button to assign as factor of auxiliary variables.
        assign_domains_button (QPushButton): Button to assign domains.
        assign_index_button (QPushButton): Button to assign index number of area.
        assign_aux_mean_button (QPushButton): Button to assign auxiliary variable means.
        assign_population_sample_size_button (QPushButton): Button to assign population sample size.
        of_interest_label (QLabel): Label for the variable of interest list.
        of_interest_list (QListView): List view for the variable of interest.
        of_interest_model (QStringListModel): Model for the variable of interest list.
        auxilary_label (QLabel): Label for the auxiliary variables list.
        auxilary_list (QListView): List view for the auxiliary variables.
        auxilary_model (QStringListModel): Model for the auxiliary variables list.
        as_factor_label (QLabel): Label for the as factor of auxiliary variables list.
        as_factor_list (QListView): List view for the as factor of auxiliary variables.
        as_factor_model (QStringListModel): Model for the as factor of auxiliary variables list.
        domain_label (QLabel): Label for the domain list.
        domain_list (QListView): List view for the domain.
        domain_model (QStringListModel): Model for the domain list.
        index_label (QLabel): Label for the index number of area list.
        index_list (QListView): List view for the index number of area.
        index_model (QStringListModel): Model for the index number of area list.
        auxilary_vars_mean (QLabel): Label for the auxiliary variable means list.
        auxilary_vars_mean_list (QListView): List view for the auxiliary variable means.
        aux_mean_model (QStringListModel): Model for the auxiliary variable means list.
        population_sample_size (QLabel): Label for the population sample size list.
        population_sample_size_list (QListView): List view for the population sample size.
        population_sample_size_model (QStringListModel): Model for the population sample size list.
        option_button (QPushButton): Button to show options.
        text_script (QLabel): Label for the R script.
        icon_label (QLabel): Label for the running icon.
        r_script_edit (QTextEdit): Text edit for displaying and editing the R script.
        ok_button (QPushButton): Button to run the model.
        of_interest_var (list): List of variables of interest.
        auxilary_vars (list): List of auxiliary variables.
        index_var (list): List of index variables.
        as_factor_var (list): List of as factor variables.
        domain_var (list): List of domain variables.
        aux_mean_vars (list): List of auxiliary mean variables.
        population_sample_size_var (list): List of population sample size variables.
        selection_method (str): Selection method.
        method (str): Method used for modeling.
        bootstrap (str): Number of bootstrap samples.
        finnish (bool): Flag indicating if the model run is finished.
        stop_thread (threading.Event): Event to stop the thread.
    Methods:
        closeEvent(event): Handles the close event of the dialog.
        set_model(model): Sets the model and updates the variables list.
        accept(): Validates the input and runs the model.
        on_run_model_finished(result, error, sae_model, r_script): Handles the completion of the model run.
    """
    
    run_model_finished = pyqtSignal(object, object, object, object)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model2 = parent.model2
        self.setWindowTitle("SAE Eblup")
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
        self.unassign_button = QPushButton("🡄")
        self.unassign_button.setObjectName("arrow_button")
        middle_layout1.addWidget(self.unassign_button)

        # Layout tengah untuk tombol panah
        middle_layout = QVBoxLayout()
        self.assign_of_interest_button = QPushButton("🡆")
        self.assign_of_interest_button.setObjectName("arrow_button")
        self.assign_aux_button = QPushButton("🡆")
        self.assign_aux_button.setObjectName("arrow_button")
        self.assign_as_factor_button = QPushButton("🡆")
        self.assign_as_factor_button.setObjectName("arrow_button")
        self.assign_domains_button = QPushButton("🡆")
        self.assign_domains_button.setObjectName("arrow_button")
        self.assign_index_button = QPushButton("🡆")
        self.assign_index_button.setObjectName("arrow_button")
        self.assign_aux_mean_button = QPushButton("🡆")
        self.assign_aux_mean_button.setObjectName("arrow_button")
        self.assign_population_sample_size_button = QPushButton("🡆")
        self.assign_population_sample_size_button.setObjectName("arrow_button")

        self.assign_of_interest_button.clicked.connect(lambda: assign_of_interest(self))
        self.assign_aux_button.clicked.connect(lambda: assign_auxilary(self))
        self.assign_index_button.clicked.connect(lambda: assign_index(self))
        self.assign_as_factor_button.clicked.connect(lambda: assign_as_factor(self))
        self.assign_domains_button.clicked.connect(lambda: assign_domains(self))
        self.assign_aux_mean_button.clicked.connect(lambda: assign_aux_mean(self))
        self.assign_population_sample_size_button.clicked.connect(lambda: assign_population_sample_size(self))
        self.unassign_button.clicked.connect(lambda: unassign_variable(self))
        middle_layout.addWidget(self.assign_of_interest_button)
        middle_layout.addWidget(self.assign_aux_button)
        middle_layout.addWidget(self.assign_as_factor_button)
        middle_layout.addWidget(self.assign_domains_button)
        middle_layout.addWidget(self.assign_index_button)
        middle_layout.addWidget(self.assign_aux_mean_button)
        middle_layout.addWidget(self.assign_population_sample_size_button)

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
        
        self.auxilary_vars_mean = QLabel("Auxilary Variable(s) Mean:")
        self.auxilary_vars_mean_list = QListView()
        self.aux_mean_model = QStringListModel()
        self.auxilary_vars_mean_list.setMinimumHeight(80)
        self.auxilary_vars_mean_list.setModel(self.aux_mean_model)
        self.auxilary_vars_mean_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.auxilary_vars_mean)
        right_layout.addWidget(self.auxilary_vars_mean_list)
        
        self.population_sample_size = QLabel("Population Sample Size:")
        self.population_sample_size_list = QListView()
        self.population_sample_size_model = QStringListModel()
        self.population_sample_size_list.setModel(self.population_sample_size_model)
        self.population_sample_size_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.population_sample_size)
        right_layout.addWidget(self.population_sample_size_list)
        
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
        self.aux_mean_vars = []
        self.population_sample_size_var = []
        self.selection_method = "None"
        self.method = "REML"
        self.bootstrap = "50"
        self.finnish = False
        
        self.run_model_finished.connect(self.on_run_model_finished)
        
        self.stop_thread = threading.Event()
        
    def closeEvent(self, event):
        threads = threading.enumerate()
        for thread in threads:
            if thread.name == "Unit Level" and thread.is_alive():
                reply = QMessageBox.question(self, 'Run in Background', 'Do you want to run the model in the background?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                if reply != QMessageBox.StandardButton.Yes and not self.finnish:
                    self.stop_thread.set()
                    self.run_model_finished.emit("Threads are stopped", True, "sae_model", "")
        event.accept()
        

    def set_model(self, model):
        self.model = model
        self.columns = [f"{col} [{dtype}]" if dtype == pl.Utf8 else f"{col} [Numeric]" for col, dtype in zip(self.model.get_data().columns, self.model.get_data().dtypes)]
        self.variables_model.setStringList(self.columns)
        self.aux_mean_model.setStringList([])
        self.auxilary_model.setStringList([])
        self.of_interest_model.setStringList([])
        self.domain_model.setStringList([])
        self.index_model.setStringList([])
        self.population_sample_size_model.setStringList([])
        self.as_factor_model.setStringList([])
        self.of_interest_var = []
        self.auxilary_vars = []
        self.index_var = []
        self.as_factor_var = []
        self.domain_var = []
        self.aux_mean_vars = []
        self.population_sample_size_var = []
        self.selection_method = "None"
        self.method = "REML"
        self.bootstrap = "50"
    
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
        sae_model = SaeEblupUnit(self.model, self.model2, view)
        controller = SaeEblupUnitController(sae_model)
        
        current_context = contextvars.copy_context()
        
        def run_model_thread():
            result, error, df = None, None, None
            try:
                result, error, df = current_context.run(controller.run_model, r_script)
                if not error:
                    sae_model.model2.set_data(df)
            except Exception as e:
                error = e
            finally:
                if not self.stop_thread.is_set():
                    self.run_model_finished.emit(result, error, sae_model, r_script)
                    self.finnish = True

        def check_run_time():
            if thread.is_alive():
                reply = QMessageBox.question(self, 'Warning', 'Run has been running for more than 1 minute. Do you want to continue?')
                if reply == QMessageBox.StandardButton.No:
                    self.stop_thread.set()
                    QMessageBox.information(self, 'Info', 'Run has been stopped.')
                    enable_service(self, False, "")


        thread = threading.Thread(target=run_model_thread, name="Unit Level")
        thread.start()

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(check_run_time)
        timer.start(60000)
    
    def on_run_model_finished(self, result, error, sae_model, r_script):
        if not error:
            self.parent.update_table(2, sae_model.get_model2())
        display_script_and_output(self.parent, r_script, result)
        enable_service(self, error, result)
        self.finnish = True
        self.close()