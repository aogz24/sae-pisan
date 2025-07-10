from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton, QHBoxLayout, 
    QAbstractItemView, QTextEdit, QSizePolicy, QScrollArea, QWidget, QComboBox, QLineEdit, QToolButton
)
from PyQt6.QtCore import QStringListModel, QTimer, Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from service.modelling.ProjectionService import assign_as_factor, assign_auxilary, assign_domains, assign_index, assign_of_interest, assign_strata, assign_weight, get_script, show_options, unassign_variable
from controller.modelling.ProjectionController import ProjectionController
from view.components.DragDropListView import DragDropListView
from view.components.ConsoleDialog import ConsoleDialog
from model.ProjectionModel import Projection
from PyQt6.QtWidgets import QMessageBox
import polars as pl
from service.utils.utils import display_script_and_output, check_script
from service.utils.enable_disable import enable_service, disable_service
import threading
import contextvars

import sys

class ConsoleStream:
    def __init__(self, signal):
        self.signal = signal
    def write(self, text):
        if text.strip():
            self.signal.emit(text)
    def flush(self):
        pass

class ProjectionDialog(QDialog):
    """
    A dialog for configuring and running a projection model in a PyQt application.
    Attributes:
        run_model_finished (pyqtSignal): Signal emitted when the model run is finished.
        parent (QWidget): The parent widget.
        model2 (object): The second model from the parent.
        columns (list): List of column names.
        variables_label (QLabel): Label for the variables list.
        variables_list (QListView): List view for selecting variables.
        variables_model (QStringListModel): Model for the variables list.
        unassign_button (QPushButton): Button to unassign variables.
        assign_of_interest_button (QPushButton): Button to assign variable of interest.
        assign_aux_button (QPushButton): Button to assign auxiliary variables.
        assign_as_factor_button (QPushButton): Button to assign variables as factors.
        assign_domains_button (QPushButton): Button to assign domain variables.
        assign_index_button (QPushButton): Button to assign index variables.
        assign_aux_mean_button (QPushButton): Button to assign auxiliary mean variables.
        assign_weight_button (QPushButton): Button to assign weight variables.
        assign_strata_button (QPushButton): Button to assign strata variables.
        of_interest_label (QLabel): Label for the variable of interest list.
        of_interest_list (QListView): List view for the variable of interest.
        of_interest_model (QStringListModel): Model for the variable of interest list.
        auxilary_label (QLabel): Label for the auxiliary variables list.
        auxilary_list (QListView): List view for the auxiliary variables.
        auxilary_model (QStringListModel): Model for the auxiliary variables list.
        as_factor_label (QLabel): Label for the as factor variables list.
        as_factor_list (QListView): List view for the as factor variables.
        as_factor_model (QStringListModel): Model for the as factor variables list.
        domain_label (QLabel): Label for the domain variables list.
        domain_list (QListView): List view for the domain variables.
        domain_model (QStringListModel): Model for the domain variables list.
        index_label (QLabel): Label for the index variables list.
        index_list (QListView): List view for the index variables.
        index_model (QStringListModel): Model for the index variables list.
        weight_label (QLabel): Label for the weight variables list.
        weight_list (QListView): List view for the weight variables.
        weight_model (QStringListModel): Model for the weight variables list.
        strata_label (QLabel): Label for the strata variables list.
        strata_list (QListView): List view for the strata variables.
        strata_model (QStringListModel): Model for the strata variables list.
        option_button (QPushButton): Button to show options.
        text_script (QLabel): Label for the R script.
        icon_label (QLabel): Label for the running icon.
        r_script_edit (QTextEdit): Text edit for the R script.
        ok_button (QPushButton): Button to run the model.
        of_interest_var (list): List of variables of interest.
        auxilary_vars (list): List of auxiliary variables.
        index_var (list): List of index variables.
        as_factor_var (list): List of as factor variables.
        domain_var (list): List of domain variables.
        weight_var (list): List of weight variables.
        strata_var (list): List of strata variables.
        selection_method (str): Method of selection.
        projection_method (str): Method of projection.
        metric (str): Metric used.
        k_fold (str): Number of folds for k-fold cross-validation.
        grid (str): Grid size.
        epoch (str): Number of epochs.
        learning_rate (str): Learning rate.
        finnish (bool): Flag indicating if the process is finished.
        stop_thread (threading.Event): Event to stop the thread.
    Methods:
        closeEvent(event): Handles the close event of the dialog.
        show_prerequisites(): Shows the prerequisites dialog.
        set_model(model): Sets the model and updates the columns.
        accept(): Accepts the dialog and runs the model.
        on_run_model_finished(result, error, sae_model, r_script): Handles the completion of the model run.
    """
    
    run_model_finished = pyqtSignal(object, object, object, object)
    update_console = pyqtSignal(str)
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model2 = parent.model2
        self.setWindowTitle("Projection SAE")
        screen_height = self.parent.screen().size().height()
        self.setMinimumHeight(int(round(screen_height * 0.82)))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self.columns = []

        self.main_layout = QVBoxLayout()

        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        # Layout utama untuk membagi area menjadi dua bagian (kiri dan kanan)
        self.split_layout = QHBoxLayout()

        # Layout kiri untuk daftar variabel
        self.left_layout = QVBoxLayout()
        self.variables_label = QLabel("Select Variables:")
        self.variables_list = DragDropListView(parent=self)
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
        self.assign_domains_button = QPushButton("🡆")
        self.assign_domains_button.setObjectName("arrow_button")
        self.assign_index_button = QPushButton("🡆")
        self.assign_index_button.setObjectName("arrow_button")
        self.assign_aux_mean_button = QPushButton("🡆")
        self.assign_weight_button = QPushButton("🡆")
        self.assign_weight_button.setObjectName("arrow_button")
        self.assign_strata_button = QPushButton("🡆")
        self.assign_strata_button.setObjectName("arrow_button")

        self.assign_of_interest_button.clicked.connect(lambda: assign_of_interest(self))
        self.assign_aux_button.clicked.connect(lambda: assign_auxilary(self))
        self.assign_index_button.clicked.connect(lambda: assign_index(self))
        self.assign_as_factor_button.clicked.connect(lambda: assign_as_factor(self))
        self.assign_domains_button.clicked.connect(lambda: assign_domains(self))
        self.assign_weight_button.clicked.connect(lambda: assign_weight(self))
        self.assign_strata_button.clicked.connect(lambda: assign_strata(self))
        self.unassign_button.clicked.connect(lambda: unassign_variable(self))
        self.middle_layout.addWidget(self.assign_of_interest_button)
        self.middle_layout.addWidget(self.assign_aux_button)
        self.middle_layout.addWidget(self.assign_as_factor_button)
        self.middle_layout.addWidget(self.assign_domains_button)
        self.middle_layout.addWidget(self.assign_index_button)
        self.middle_layout.addWidget(self.assign_weight_button)
        self.middle_layout.addWidget(self.assign_strata_button)

        
        
        # Layout kanan untuk daftar dependen, independen, vardir, dan major area
        self.right_layout = QVBoxLayout()
        # right_layout.minimumSize(0, 650)
        self.of_interest_label = QLabel("Variable of interest:")
        self.of_interest_list = DragDropListView(parent=self)
        self.of_interest_list.setMinimumHeight(100)
        self.of_interest_model = QStringListModel()
        self.of_interest_list.setModel(self.of_interest_model)
        self.of_interest_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.of_interest_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.of_interest_label)
        self.right_layout.addWidget(self.of_interest_list)

        self.auxilary_label = QLabel("Auxilary Variable(s):")
        self.auxilary_list = DragDropListView(parent=self)
        self.auxilary_list.setMinimumHeight(100)
        self.auxilary_model = QStringListModel()
        self.auxilary_list.setModel(self.auxilary_model)
        self.auxilary_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.auxilary_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.auxilary_label)
        self.right_layout.addWidget(self.auxilary_list)

        self.as_factor_label = QLabel("as Factor of Auxilary Variable(s):")
        self.as_factor_list = DragDropListView(parent=self)
        self.as_factor_list.setMinimumHeight(100)
        self.as_factor_model = QStringListModel()
        self.as_factor_list.setModel(self.as_factor_model)
        self.as_factor_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.as_factor_label)
        self.right_layout.addWidget(self.as_factor_list)
        
        self.domain_label = QLabel("Domain:")
        self.domain_list = DragDropListView(parent=self)
        self.domain_list.setMinimumHeight(100)
        self.domain_model = QStringListModel()
        self.domain_list.setModel(self.domain_model)
        self.domain_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.domain_label)
        self.right_layout.addWidget(self.domain_list)
        
        self.index_label = QLabel("Index number of Area:")
        self.index_list = DragDropListView(parent=self)
        self.index_list.setMinimumHeight(100)
        self.index_model = QStringListModel()
        self.index_list.setModel(self.index_model)
        self.index_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.index_label)
        self.right_layout.addWidget(self.index_list)
        

        self.weight_label = QLabel("Weight:")
        self.weight_list = DragDropListView(parent=self)
        self.weight_list.setMinimumHeight(100)
        self.weight_model = QStringListModel()
        self.weight_list.setModel(self.weight_model)
        self.weight_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.weight_label)
        self.right_layout.addWidget(self.weight_list)

        self.strata_label = QLabel("Strata:")
        self.strata_list = DragDropListView(parent=self)
        self.strata_list.setMinimumHeight(100)
        self.strata_model = QStringListModel()
        self.strata_list.setModel(self.strata_model)
        self.strata_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.strata_label)
        self.right_layout.addWidget(self.strata_list)
        
        # Menambahkan layout kiri, tengah, dan kanan ke layout utama
        self.split_layout.addLayout(self.left_layout)
        self.split_layout.addLayout(self.middle_layout1)
        self.split_layout.addLayout(self.middle_layout)
        self.split_layout.addLayout(self.right_layout)

        self.scroll_layout.addLayout(self.split_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        # Tombol untuk menghasilkan skrip R
        self.option_button = QPushButton("Option")
        self.option_button.setFixedWidth(150)
        self.text_script = QLabel("R Script:")
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

        self.show_console_first_checkbox = QCheckBox("Show R Console")
        self.show_console_first_checkbox.setChecked(False)  # default: show before
        # Tambahkan ke layout sebelum tombol Option
        self.main_layout.addWidget(self.show_console_first_checkbox)
        
        self.main_layout.addLayout(self.script_layout)
        self.option_button.clicked.connect(lambda : show_options(self))
        
        # Area teks untuk menampilkan dan mengedit skrip R
        self.r_script_edit = QTextEdit()
        self.r_script_edit.setFixedHeight(round(screen_height*0.18))
        self.r_script_edit.setVisible(False)
        self.r_script_edit.setReadOnly(False)
        self.r_script_edit.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
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
        self.learning_rate = "0.01"
        self.finnish = False
        
        self.run_model_finished.connect(self.on_run_model_finished)
        
        self.stop_thread = threading.Event()
        self.reply=None
        
        self.console_dialog = None
        self.update_console.connect(self._append_console)

    def _append_console(self, text):
        if self.console_dialog:
            self.console_dialog.append_text(text)
        
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
        if self.console_dialog:
            self.console_dialog.close()
        threads = threading.enumerate()
        for thread in threads:
            if thread.name == "Projection" and thread.is_alive():
                if self.reply is None:
                    self.reply = QMessageBox(self)
                    self.reply.setWindowTitle('Run in Background')
                    self.reply.setText('Do you want to run the model in the background?')
                    self.reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    self.reply.setDefaultButton(QMessageBox.StandardButton.No)
                if self.reply.exec() != QMessageBox.StandardButton.Yes and not self.finnish:
                    self.stop_thread.set()
                    self.run_model_finished.emit("Threads are stopped", True, "sae_model", "")
        self.finnish=False
        self.reply=None
        event.accept()
    
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
        
    def handle_drop(self, target_list, items):
        from PyQt6.QtCore import QItemSelectionModel
        # Mirip dengan handle_drop di dialog lain, sesuaikan mapping dan aksi assign/unassign
        mapping = {
            self.variables_list: "variables",
            self.of_interest_list: "of_interest",
            self.auxilary_list: "auxilary",
            self.as_factor_list: "as_factor",
            self.domain_list: "domain",
            self.index_list: "index",
            self.weight_list: "weight",
            self.strata_list: "strata"
        }
        source_list = None
        for lst in mapping:
            if any(item in lst.model().stringList() for item in items):
                source_list = lst
                break

        # Drag dari variables_list ke kanan (assign)
        if source_list == self.variables_list:
            if target_list == self.of_interest_list:
                self.variables_list.clearSelection()
                for idx, val in enumerate(self.variables_model.stringList()):
                    if val in items:
                        self.variables_list.selectionModel().select(
                            self.variables_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                assign_of_interest(self)
            elif target_list == self.auxilary_list:
                self.variables_list.clearSelection()
                for idx, val in enumerate(self.variables_model.stringList()):
                    if val in items:
                        self.variables_list.selectionModel().select(
                            self.variables_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                assign_auxilary(self)
            elif target_list == self.as_factor_list:
                self.variables_list.clearSelection()
                for idx, val in enumerate(self.variables_model.stringList()):
                    if val in items:
                        self.variables_list.selectionModel().select(
                            self.variables_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                assign_as_factor(self)
            elif target_list == self.domain_list:
                self.variables_list.clearSelection()
                for idx, val in enumerate(self.variables_model.stringList()):
                    if val in items:
                        self.variables_list.selectionModel().select(
                            self.variables_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                assign_domains(self)
            elif target_list == self.index_list:
                self.variables_list.clearSelection()
                for idx, val in enumerate(self.variables_model.stringList()):
                    if val in items:
                        self.variables_list.selectionModel().select(
                            self.variables_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                assign_index(self)
            elif target_list == self.weight_list:
                self.variables_list.clearSelection()
                for idx, val in enumerate(self.variables_model.stringList()):
                    if val in items:
                        self.variables_list.selectionModel().select(
                            self.variables_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                assign_weight(self)
            elif target_list == self.strata_list:
                self.variables_list.clearSelection()
                for idx, val in enumerate(self.variables_model.stringList()):
                    if val in items:
                        self.variables_list.selectionModel().select(
                            self.variables_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                assign_strata(self)

        # Drag dari kanan ke variables_list (unassign)
        elif target_list == self.variables_list:
            for lst, model in [
                (self.of_interest_list, self.of_interest_model),
                (self.auxilary_list, self.auxilary_model),
                (self.as_factor_list, self.as_factor_model),
                (self.domain_list, self.domain_model),
                (self.index_list, self.index_model),
                (self.weight_list, self.weight_model),
                (self.strata_list, self.strata_model)
            ]:
                if source_list == lst:
                    lst.clearSelection()
                    for idx, val in enumerate(model.stringList()):
                        if val in items:
                            lst.selectionModel().select(
                                model.index(idx),
                                QItemSelectionModel.SelectionFlag.Select
                            )
                    unassign_variable(self)
    
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
        
        show_console_first = self.show_console_first_checkbox.isChecked()
        if show_console_first:
            self.console_dialog = ConsoleDialog(self)
            self.console_dialog.show()
        
        current_context = contextvars.copy_context()
        
        def run_model_thread():
            result, error, df = None, None, None
            try:
                old_stdout = sys.stdout
                sys.stdout = ConsoleStream(self.update_console)
                result, error, df = current_context.run(controller.run_model, r_script)
                sys.stdout = old_stdout
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
                self.parent.autosave_data()
                reply = QMessageBox.question(self, 'Warning', 'Run has been running for more than 1 minute. Do you want to continue?')
                if reply == QMessageBox.StandardButton.No:
                    self.stop_thread.set()
                    QMessageBox.information(self, 'Info', 'Run has been stopped.')
                    enable_service(self, False, "")


        thread = threading.Thread(target=run_model_thread, name="Projection")
        thread.start()

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(check_run_time)
        timer.start(60000)
    
    def on_run_model_finished(self, result, error, sae_model, r_script):
        if self.console_dialog:
            self.console_dialog.stop_loading()
            self.console_dialog.close()
        if not error:
            self.parent.update_table(2, sae_model.get_model2())
        if self.reply is not None:
            self.reply.reject()
        display_script_and_output(self.parent, r_script, result)
        enable_service(self, error, result)
        self.finnish = True
        self.close()