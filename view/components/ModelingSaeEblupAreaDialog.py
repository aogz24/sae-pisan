from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, 
    QAbstractItemView, QTextEdit, QSizePolicy, QToolButton, QCheckBox
)
from PyQt6.QtCore import QStringListModel, QTimer, Qt, QSize, pyqtSignal, QItemSelectionModel
from PyQt6.QtGui import QIcon
from service.modelling.SaeEblupArea import *
from controller.modelling.SaeController import SaeController
from model.SaeEblup import SaeEblup
from PyQt6.QtWidgets import QMessageBox
from view.components.DragDropListView import DragDropListView
from view.components.ConsoleDialog import ConsoleDialog
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

class ModelingSaeDialog(QDialog):
    """
    A dialog for modeling SAE EBLUP (Small Area Estimation Empirical Best Linear Unbiased Prediction) area level.
    Attributes:
        run_model_finished (pyqtSignal): Signal emitted when the model run is finished.
        parent (QWidget): The parent widget.
        model2 (object): The second model from the parent.
        columns (list): List of column names.
        variables_label (QLabel): Label for the variables list.
        variables_list (QListView): List view for the variables.
        variables_model (QStringListModel): Model for the variables list.
        unassign_button (QPushButton): Button to unassign variables.
        assign_of_interest_button (QPushButton): Button to assign variable of interest.
        assign_aux_button (QPushButton): Button to assign auxiliary variables.
        assign_as_factor_button (QPushButton): Button to assign variables as factors.
        assign_vardir_button (QPushButton): Button to assign direct variance variables.
        of_interest_label (QLabel): Label for the variable of interest list.
        of_interest_list (QListView): List view for the variable of interest.
        of_interest_model (QStringListModel): Model for the variable of interest list.
        auxilary_label (QLabel): Label for the auxiliary variables list.
        auxilary_list (QListView): List view for the auxiliary variables.
        auxilary_model (QStringListModel): Model for the auxiliary variables list.
        as_factor_label (QLabel): Label for the factors of auxiliary variables list.
        as_factor_list (QListView): List view for the factors of auxiliary variables.
        as_factor_model (QStringListModel): Model for the factors of auxiliary variables list.
        vardir_label (QLabel): Label for the direct variance list.
        vardir_list (QListView): List view for the direct variance variables.
        vardir_model (QStringListModel): Model for the direct variance variables list.
        option_button (QPushButton): Button to show options.
        text_script (QLabel): Label for the R script.
        icon_label (QLabel): Label for the running icon.
        r_script_edit (QTextEdit): Text edit area for the R script.
        ok_button (QPushButton): Button to run the model.
        of_interest_var (list): List of variables of interest.
        auxilary_vars (list): List of auxiliary variables.
        vardir_var (list): List of direct variance variables.
        as_factor_var (list): List of factors of auxiliary variables.
        selection_method (str): Method of selection.
        method (str): Method for the model.
        finnish (bool): Flag to indicate if the model run is finished.
        stop_thread (threading.Event): Event to stop the thread.
    Methods:
        closeEvent(event): Handles the close event of the dialog.
        set_model(model): Sets the model and updates the variables list.
        accept(): Validates inputs and runs the model.
        on_run_model_finished(result, error, sae_model, r_script): Handles the completion of the model run.
    """
    
    run_model_finished = pyqtSignal(object, object, object, object)
    update_console = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model2 = parent.model2
        self.setWindowTitle("SAE Eblup")
        screen_height = self.parent.screen().size().height()
        self.setMinimumHeight(int(round(screen_height * 0.82)))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self.columns = []

        self.main_layout = QVBoxLayout()

        # Layout utama untuk membagi area menjadi dua bagian (kiri dan kanan)
        self.split_layout = QHBoxLayout()

        # Layout kiri untuk daftar variabel
        self.left_layout = QVBoxLayout()
        self.variables_label = QLabel("Select Variables:")
        self.variables_list = DragDropListView(parent=self)
        self.variables_model = QStringListModel(self.columns)
        self.variables_list.setModel(self.variables_model)
        self.variables_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.variables_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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
        self.of_interest_list = DragDropListView(parent=self)
        self.of_interest_model = QStringListModel()
        self.of_interest_list.setModel(self.of_interest_model)
        self.of_interest_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.right_layout.addWidget(self.of_interest_label)
        self.right_layout.addWidget(self.of_interest_list)

        self.auxilary_label = QLabel("Auxilary Variable(s):")
        self.auxilary_list = DragDropListView(parent=self)
        self.auxilary_model = QStringListModel()
        self.auxilary_list.setModel(self.auxilary_model)
        self.auxilary_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.auxilary_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.auxilary_label)
        self.right_layout.addWidget(self.auxilary_list)

        self.as_factor_label = QLabel("as Factor of Auxilary Variable(s):")
        self.as_factor_list = DragDropListView(parent=self)
        self.as_factor_model = QStringListModel()
        self.as_factor_list.setModel(self.as_factor_model)
        self.as_factor_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.as_factor_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.right_layout.addWidget(self.as_factor_label)
        self.right_layout.addWidget(self.as_factor_list)
        
        self.vardir_label = QLabel("Direct Variance:")
        self.vardir_list = DragDropListView(parent=self)
        self.vardir_model = QStringListModel()
        self.vardir_list.setModel(self.vardir_model)
        self.vardir_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

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
        self.option_button.clicked.connect(lambda: show_options(self))
        
        # Area teks untuk menampilkan dan mengedit skrip R
        self.r_script_edit = QTextEdit()
        self.r_script_edit.setFixedHeight(round(screen_height*0.20))
        self.r_script_edit.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.r_script_edit.setReadOnly(False)
        self.r_script_edit.setVisible(False)
        self.main_layout.addWidget(self.r_script_edit)
        
        

        # Tombol untuk tindakan dialog
        button_layout = QHBoxLayout()
        button_layout.setObjectName("button_layout")
        self.ok_button = QPushButton("Run Model")
        self.ok_button.setFixedWidth(150)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.option_button)
        button_layout.addWidget(self.ok_button)
        self.main_layout.addLayout(button_layout)
        


        self.setLayout(self.main_layout)

        self.of_interest_var = []
        self.auxilary_vars = []
        self.vardir_var = []
        self.as_factor_var = []
        self.selection_method = "None"
        self.method = "REML"
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
    

    def handle_drop(self, target_list, items):
        mapping = {
            self.variables_list: "variables",
            self.of_interest_list: "of_interest",
            self.auxilary_list: "auxilary",
            self.as_factor_list: "as_factor",
            self.vardir_list: "vardir"
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
            elif target_list == self.vardir_list:
                self.variables_list.clearSelection()
                for idx, val in enumerate(self.variables_model.stringList()):
                    if val in items:
                        self.variables_list.selectionModel().select(
                            self.variables_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                assign_vardir(self)
                
        
        # Drag dari kanan ke variables_list (unassign)
        elif target_list == self.variables_list:
            if source_list == self.of_interest_list:
                self.of_interest_list.clearSelection()
                for idx, val in enumerate(self.of_interest_model.stringList()):
                    if val in items:
                        self.of_interest_list.selectionModel().select(
                            self.of_interest_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                unassign_variable(self)
            elif source_list == self.auxilary_list:
                self.auxilary_list.clearSelection()
                for idx, val in enumerate(self.auxilary_model.stringList()):
                    if val in items:
                        self.auxilary_list.selectionModel().select(
                            self.auxilary_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                unassign_variable(self)
            elif source_list == self.as_factor_list:
                self.as_factor_list.clearSelection()
                for idx, val in enumerate(self.as_factor_model.stringList()):
                    if val in items:
                        self.as_factor_list.selectionModel().select(
                            self.as_factor_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                unassign_variable(self)
            elif source_list == self.vardir_list:
                self.vardir_list.clearSelection()
                for idx, val in enumerate(self.vardir_model.stringList()):
                    if val in items:
                        self.vardir_list.selectionModel().select(
                            self.vardir_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                unassign_variable(self)
        
        # Drag antar daftar di kanan
        elif target_list in [self.of_interest_list, self.auxilary_list, self.as_factor_list, self.vardir_list]:
            if source_list == target_list:
                return
            if source_list == self.of_interest_list:
                self.of_interest_list.clearSelection()
                for idx, val in enumerate(self.of_interest_model.stringList()):
                    if val in items:
                        self.of_interest_list.selectionModel().select(
                            self.of_interest_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
            elif source_list == self.auxilary_list:
                self.auxilary_list.clearSelection()
                for idx, val in enumerate(self.auxilary_model.stringList()):
                    if val in items:
                        self.auxilary_list.selectionModel().select(
                            self.auxilary_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
            elif source_list == self.as_factor_list:
                self.as_factor_list.clearSelection()
                for idx, val in enumerate(self.as_factor_model.stringList()):
                    if val in items:
                        self.as_factor_list.selectionModel().select(
                            self.as_factor_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
            elif source_list == self.vardir_list:
                self.vardir_list.clearSelection()
                for idx, val in enumerate(self.vardir_model.stringList()):
                    if val in items:
                        self.vardir_list.selectionModel().select(
                            self.vardir_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
            
            # Hapus dari source list
            unassign_variable(self)
            
            # Pindahkan ke target list yang sesuai
            if target_list == self.of_interest_list:
                # Pilih item di variables_list untuk assign
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
            elif target_list == self.vardir_list:
                self.variables_list.clearSelection()
                for idx, val in enumerate(self.variables_model.stringList()):
                    if val in items:
                        self.variables_list.selectionModel().select(
                            self.variables_model.index(idx),
                            QItemSelectionModel.SelectionFlag.Select
                        )
                assign_vardir(self)
                        

    def closeEvent(self, event):
        if self.console_dialog:
            self.console_dialog.close()
        threads = threading.enumerate()
        for thread in threads:
            if thread.name == "SAE EBLUP Area Level" and thread.is_alive():
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
        
    def set_model(self, model):
        self.model = model
        self.columns = [
            f"{col} [{dtype}]" if dtype == pl.Utf8 else
            f"{col} [NULL]" if dtype == pl.Null else
            f"{col} [Categorical]" if dtype == pl.Categorical else
            f"{col} [Boolean]" if dtype == pl.Boolean else
            f"{col} [Numeric]"
            for col, dtype in zip(self.model.get_data().columns, self.model.get_data().dtypes)
        ]
        self.variables_model.setStringList(self.columns)
        self.vardir_model.setStringList([])
        self.auxilary_model.setStringList([])
        self.as_factor_model.setStringList([])
        self.of_interest_model.setStringList([])
        self.of_interest_var = []
        self.auxilary_vars = []
        self.vardir_var = []
        self.as_factor_var = []
        self.selection_method = "None"
        self.method = "REML"
    
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
        
        r_script = get_script(self)
        if not check_script(r_script):
            return
        disable_service(self)

        view = self.parent
        sae_model = SaeEblup(self.model, self.model2, view)
        controller = SaeController(sae_model)
        
        current_context = contextvars.copy_context()
        
        show_console_first = self.show_console_first_checkbox.isChecked()
        if show_console_first:
            self.console_dialog = ConsoleDialog(self)
            self.console_dialog.show()
        
        def run_model_thread():
            result, error, df = None, None, None
            try:
                if self.console_dialog:
                    import sys
                    old_stdout = sys.stdout
                    sys.stdout = ConsoleStream(self.update_console)
                
                from rpy2.rinterface_lib import openrlib
                with openrlib.rlock:
                    result, error, df = current_context.run(controller.run_model, r_script)
                
                if self.console_dialog:
                    sys.stdout = old_stdout
                if not error:
                    sae_model.model2.set_data(df)
            except Exception as e:
                error = e
            finally:
                if not self.stop_thread.is_set():
                    self.finnish = True
                    self.run_model_finished.emit(result, error, sae_model, r_script)
                else:
                    return

        def check_run_time():
            if thread.is_alive():
                self.parent.autosave_data()
                reply = QMessageBox.question(self, 'Warning', 'Run has been running for more than 1 minute. Do you want to continue?')
                if reply == QMessageBox.StandardButton.No:
                    self.stop_thread.set()
                    QMessageBox.information(self, 'Info', 'Run has been stopped.')
                    enable_service(self, False, "")


        thread = threading.Thread(target=run_model_thread, name="SAE EBLUP Area Level")
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
        self.close()     