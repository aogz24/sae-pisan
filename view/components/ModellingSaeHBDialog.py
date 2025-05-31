from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListView, QPushButton, QHBoxLayout, 
    QAbstractItemView, QTextEdit, QSizePolicy, QToolButton
)
from PyQt6.QtCore import QStringListModel, QTimer, Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from service.modelling.SaeHBArea import assign_of_interest, assign_auxilary, assign_vardir, assign_as_factor, unassign_variable, show_options, get_script
from controller.modelling.SaeHBcontroller import SaeHBController
from model.SaeHB import SaeHB
from PyQt6.QtWidgets import QMessageBox
import polars as pl
from service.utils.utils import display_script_and_output, check_script
from service.utils.enable_disable import enable_service, disable_service
import threading
import contextvars

class ModelingSaeHBDialog(QDialog):
    """
    A dialog for configuring and running the SAE HB Beta model.
    Attributes:
        run_model_finished (pyqtSignal): Signal emitted when the model run is finished.
        parent (QWidget): The parent widget.
        model2 (Model): The secondary model from the parent.
        columns (list): List of column names.
        model_method (str): The method used for the model, default is "Beta".
        variables_label (QLabel): Label for the variables list.
        variables_list (QListView): List view for selecting variables.
        variables_model (QStringListModel): Model for the variables list.
        unassign_button (QPushButton): Button to unassign variables.
        assign_of_interest_button (QPushButton): Button to assign variable of interest.
        assign_aux_button (QPushButton): Button to assign auxiliary variables.
        assign_as_factor_button (QPushButton): Button to assign as factor of auxiliary variables.
        assign_vardir_button (QPushButton): Button to assign direct variance.
        of_interest_label (QLabel): Label for the variable of interest list.
        of_interest_list (QListView): List view for the variable of interest.
        of_interest_model (QStringListModel): Model for the variable of interest list.
        auxilary_label (QLabel): Label for the auxiliary variables list.
        auxilary_list (QListView): List view for the auxiliary variables.
        auxilary_model (QStringListModel): Model for the auxiliary variables list.
        as_factor_label (QLabel): Label for the factor of auxiliary variables list.
        as_factor_list (QListView): List view for the factor of auxiliary variables.
        as_factor_model (QStringListModel): Model for the factor of auxiliary variables list.
        vardir_label (QLabel): Label for the direct variance list.
        vardir_list (QListView): List view for the direct variance.
        vardir_model (QStringListModel): Model for the direct variance list.
        option_button (QPushButton): Button to show options.
        text_script (QLabel): Label for the R script.
        icon_label (QLabel): Label for the running icon.
        r_script_edit (QTextEdit): Text edit area for the R script.
        ok_button (QPushButton): Button to run the model.
        of_interest_var (list): List of variables of interest.
        auxilary_vars (list): List of auxiliary variables.
        vardir_var (list): List of direct variance variables.
        as_factor_var (list): List of factor of auxiliary variables.
        selection_method (str): Method of selection.
        iter_update (str): Number of update iterations.
        iter_mcmc (str): Number of MCMC iterations.
        burn_in (str): Number of burn-in iterations.
        stop_thread (threading.Event): Event to stop the thread.
        finnish (bool): Flag to indicate if the process is finished.
    Methods:
        closeEvent(event): Handles the close event of the dialog.
        set_model(model): Sets the model and updates the variables list.
        accept(): Validates inputs and runs the model.
        on_run_model_finished(result, error, sae_model, r_script): Handles the completion of the model run.
    """
    
    run_model_finished = pyqtSignal(object, object, object, object, object)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model2 = parent.model2
        self.setWindowTitle("SAE HB Beta")
        screen_height = self.parent.screen().size().height()
        self.setMinimumHeight(int(round(screen_height * 0.82)))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self.columns = []
        self.model_method = "Beta"

        self.main_layout = QVBoxLayout()

        # Layout utama untuk membagi area menjadi dua bagian (kiri dan kanan)
        self.split_layout = QHBoxLayout()

        # Layout kiri untuk daftar variabel
        self.left_layout = QVBoxLayout()
        self.variables_label = QLabel("Select Variables:")
        self.variables_list = QListView()
        self.variables_model = QStringListModel(self.columns)
        self.variables_list.setModel(self.variables_model)
        self.variables_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.left_layout.addWidget(self.variables_label)
        self.left_layout.addWidget(self.variables_list)
        
        self.middle_layout1 = QVBoxLayout()
        self.unassign_button = QPushButton("🡄")
        self.unassign_button.setObjectName("arrow_button")
        self.middle_layout1.addWidget(self.unassign_button)

        # Layout tengah untuk tombol panah
        self.middle_layout = QVBoxLayout()
        self.assign_of_interest_button = QPushButton("🡆")
        self.assign_of_interest_button.setObjectName("arrow_button")
        self.assign_aux_button = QPushButton("🡆")
        self.assign_aux_button.setObjectName("arrow_button")
        self.assign_as_factor_button = QPushButton("🡆")
        self.assign_as_factor_button.setObjectName("arrow_button")
        self.assign_vardir_button = QPushButton("🡆")
        self.assign_vardir_button.setObjectName("arrow_button")

        self.assign_of_interest_button.clicked.connect(lambda: assign_of_interest(self))
        self.assign_aux_button.clicked.connect(lambda: assign_auxilary(self))
        self.assign_vardir_button.clicked.connect(lambda: assign_vardir(self))
        self.assign_as_factor_button.clicked.connect(lambda: assign_as_factor(self))
        self.unassign_button.clicked.connect(lambda: unassign_variable(self))
        self.middle_layout.addWidget(self.assign_of_interest_button)
        self.middle_layout.addWidget(self.assign_aux_button)
        self.middle_layout.addWidget(self.assign_as_factor_button)
        self.middle_layout.addWidget(self.assign_vardir_button)

        # Layout kanan untuk daftar dependen, independen, vardir, dan major area
        self.right_layout = QVBoxLayout()
        self.of_interest_label = QLabel("Variable of interest:")
        self.of_interest_list = QListView()
        self.of_interest_model = QStringListModel()
        self.of_interest_list.setModel(self.of_interest_model)
        self.of_interest_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.of_interest_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.of_interest_label)
        self.right_layout.addWidget(self.of_interest_list)

        self.auxilary_label = QLabel("Auxilary Variable(s):")
        self.auxilary_list = QListView()
        self.auxilary_model = QStringListModel()
        self.auxilary_list.setModel(self.auxilary_model)
        self.auxilary_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.auxilary_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.auxilary_label)
        self.right_layout.addWidget(self.auxilary_list)

        self.as_factor_label = QLabel("as Factor of Auxilary Variable(s):")
        self.as_factor_list = QListView()
        self.as_factor_model = QStringListModel()
        self.as_factor_list.setModel(self.as_factor_model)
        self.as_factor_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.as_factor_label)
        self.right_layout.addWidget(self.as_factor_list)
        
        self.vardir_label = QLabel("Direct Variance:")
        self.vardir_list = QListView()
        self.vardir_model = QStringListModel()
        self.vardir_list.setModel(self.vardir_model)
        self.vardir_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.vardir_label)
        self.right_layout.addWidget(self.vardir_list)

        # Menambahkan layout kiri, tengah, dan kanan ke layout utama
        self.split_layout.addLayout(self.left_layout)
        self.split_layout.addLayout(self.middle_layout1)
        self.split_layout.addLayout(self.middle_layout)
        self.split_layout.addLayout(self.right_layout)

        self.main_layout.addLayout(self.split_layout)

        # Tombol untuk menghasilkan skrip R
        self.option_button = QPushButton("Option")
        self.option_button.setFixedWidth(150)
        self.text_script = QLabel("R Script:")
        self.option_button.clicked.connect(lambda : show_options(self))
        
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # Create a horizontal layout to place the text_script and icon_label in one row
        self.toggle_script_button = QToolButton()
        self.toggle_script_button.setIcon(QIcon("assets/more.svg"))
        self.toggle_script_button.setIconSize(QSize(16, 16))
        self.toggle_script_button.setCheckable(True)
        self.toggle_script_button.setChecked(False)
        self.toggle_script_button.clicked.connect(self.toggle_r_script_visibility)
        
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.text_script)
        self.button_layout.addWidget(self.toggle_script_button)
        self.button_layout.setAlignment(self.text_script, Qt.AlignmentFlag.AlignLeft)
        self.button_layout.setAlignment(self.toggle_script_button, Qt.AlignmentFlag.AlignLeft)
        
        # Create a horizontal layout to place the text_script and icon_label in one row
        self.script_layout = QHBoxLayout()
        self.script_layout.addLayout(self.button_layout)
        self.script_layout.addStretch()
        self.script_layout.addWidget(self.icon_label)
        self.icon_label.setVisible(False)
        self.script_layout.setAlignment(self.text_script, Qt.AlignmentFlag.AlignLeft)

        self.main_layout.addLayout(self.script_layout)
        
        # Area teks untuk menampilkan dan mengedit skrip R
        self.r_script_edit = QTextEdit()
        self.r_script_edit.setFixedHeight(round(screen_height*0.20))
        self.r_script_edit.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.r_script_edit.setReadOnly(False)
        self.r_script_edit.setVisible(False)
        self.main_layout.addWidget(self.r_script_edit)

        # Tombol untuk tindakan dialog
        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName("button_layout")
        self.ok_button = QPushButton("Run Model")
        self.ok_button.setFixedWidth(150)
        self.ok_button.clicked.connect(self.accept)
        self.button_layout.addWidget(self.option_button)
        self.button_layout.addWidget(self.ok_button)
        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

        self.of_interest_var = []
        self.auxilary_vars = []
        self.vardir_var = []
        self.as_factor_var = []
        self.selection_method = "None"
        self.iter_update="3"
        self.iter_mcmc="2000"
        
        self.burn_in="1000"
        
        self.run_model_finished.connect(self.on_run_model_finished)
        
        self.stop_thread = threading.Event()
        self.reply=None
        self.finnish = False
        
    def toggle_r_script_visibility(self):
        """
        Toggles the visibility of the R script text edit area and updates the toggle button text.
        """
        is_visible = self.r_script_edit.isVisible()
        self.r_script_edit.setVisible(not is_visible)
        if not is_visible:
            self.toggle_script_button.setIcon(QIcon("assets/less.svg"))
        else:
            self.toggle_script_button.setIcon(QIcon("assets/more.svg"))
    
    def closeEvent(self, event):
        threads = threading.enumerate()
        for thread in threads:
            if thread.name == "SAE HB" and thread.is_alive():
                self.parent.autosave_data()
                if self.reply is None:
                    self.reply = QMessageBox(self)
                    self.reply.setWindowTitle('Run in Background')
                    self.reply.setText('Do you want to run the model in the background?')
                    self.reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    self.reply.setDefaultButton(QMessageBox.StandardButton.No)
                if self.reply.exec() != QMessageBox.StandardButton.Yes and not self.finnish:
                    self.stop_thread.set()
                    print(self.stop_thread.is_set())
                    self.run_model_finished.emit("Threads are stopped", True, "sae_model", "", None)
        self.finnish=False
        self.reply=None
        event.accept()

    def set_model(self, model):
        self.model = model
        self.columns = [f"{col} [{dtype}]" if dtype == pl.Utf8 else f"{col} [Numeric]" for col, dtype in zip(self.model.get_data().columns, self.model.get_data().dtypes)]
        self.variables_model.setStringList(self.columns)
        self.of_interest_model.setStringList([])
        self.auxilary_model.setStringList([])
        self.as_factor_model.setStringList([])
        self.vardir_model.setStringList([])
        self.of_interest_var = []
        self.auxilary_vars = []
        self.vardir_var = []
        self.as_factor_var = []
        self.selection_method = "None"
        self.iter_update="3"
        self.iter_mcmc="2000"
        self.burn_in="1000"
    
    def accept(self):
        if (not self.vardir_var or self.vardir_var == [""]) and (not self.of_interest_var or self.of_interest_var == [""]):
            QMessageBox.warning(self, "Warning", "Varians Direct and variable of interest cannot be empty.")
            self.ok_button.setEnabled(True)
            self.option_button.setEnabled(True)
            self.ok_button.setText("Run Model")
            return
        if not self.of_interest_var or self.of_interest_var == [""]:
            QMessageBox.warning(self, "Warning", "Variable of interest cannot be empty.")
            self.ok_button.setEnabled(True)
            self.option_button.setEnabled(True)
            self.ok_button.setText("Run Model")
            return
        if not self.vardir_var or self.vardir_var == [""]:
            QMessageBox.warning(self, "Warning", "Varians Direct cannot be empty.")
            self.ok_button.setEnabled(True)
            self.option_button.setEnabled(True)
            self.ok_button.setText("Run Model")
            return
        
        data = self.model.get_data()
        variable = self.of_interest_var[0].split('[')[0].strip()
        if not (data[variable].dtype == pl.Float64 and (data[variable] >= 0).all() and (data[variable] <= 1).all()):
            QMessageBox.warning(self, "Warning", f"The '{variable}' column must be of type float and have values between 0 and 1.")
            return
        
        r_script = get_script(self)
        if not check_script(r_script):
            return
        
        disable_service(self)

        view = self.parent
        sae_model = SaeHB(self.model, self.model2, view)
        controller = SaeHBController(sae_model)
        
        current_context = contextvars.copy_context()
        
        def run_model_thread():
            result, error, df, plot_paths = None, None, None, None
            try:
                result, error, df, plot_paths = current_context.run(controller.run_model, r_script)
                if not error:
                    sae_model.model2.set_data(df)
            except Exception as e:
                error=True
                if result is None:
                    result = str(e)
            finally:
                if not self.stop_thread.is_set():
                    self.run_model_finished.emit(result, error, sae_model, r_script, plot_paths)
                    self.finnish = True
                    return
                else:
                    import os
                    temp_dir = os.path.join(os.getcwd(), "temp")
                    if os.path.exists(temp_dir):
                        for file in os.listdir(temp_dir):
                            file_path = os.path.join(temp_dir, file)
                            try:
                                if os.path.isfile(file_path):
                                    os.remove(file_path)
                            except Exception as e:
                                print(f"Error deleting file {file_path}: {e}")

        def check_run_time():
            if thread.is_alive():
                reply = QMessageBox.question(self, 'Warning', 'Run has been running for more than 1 minute. Do you want to continue?')
                if reply == QMessageBox.StandardButton.No:
                    self.stop_thread.set()
                    print(self.stop_thread.is_set())
                    QMessageBox.information(self, 'Info', 'Run has been stopped.')
                    enable_service(self, False, "")


        thread = threading.Thread(target=run_model_thread, name="SAE HB")
        thread.start()

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(check_run_time)
        timer.start(60000)
    
    def on_run_model_finished(self, result, error, sae_model, r_script, plot_paths):
        if not error:
            self.parent.update_table(2, sae_model.get_model2())
        if self.reply is not None:
            self.reply.reject()
        display_script_and_output(self.parent, r_script, result, plot_paths)
        enable_service(self, error, result)
        self.finnish = True
        self.close()