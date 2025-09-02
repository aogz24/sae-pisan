import contextvars
import threading
from view.components.ModelingSaeEblupUnitDialog import ModelingSaeUnitDialog
from service.utils.utils import display_script_and_output, check_script
from service.utils.enable_disable import enable_service, disable_service
from view.components.ConsoleDialog import ConsoleDialog
from PyQt6.QtWidgets import (QMessageBox, QCheckBox)
from PyQt6.QtCore import QTimer, pyqtSignal
from model.SaeHBUnit import SaeHBUnit
from controller.modelling.SaeHBUnitController import SaeHBUnitController
import polars as pl
from service.modelling.SaeHBUnit import *
from PyQt6.QtCore import QItemSelectionModel
from PyQt6.QtGui import QIcon

import sys
class ConsoleStream:
    def __init__(self, signal):
        self.signal = signal
    def write(self, text):
        if text.strip():
            self.signal.emit(text)
    def flush(self):
        pass

class ModelingSaeHBNormalDialog(ModelingSaeUnitDialog):
    """
    A dialog class for modeling SAE HB with a normal distribution.
    Inherits from:
        ModelingSaeHBDialog: The base class for SAE HB modeling dialogs.
    Attributes:
        model_method (str): The method used for modeling, set to "Normal".
    Methods:
        __init__(parent): Initializes the dialog with the given parent.
    """
    
    run_model_finished = pyqtSignal(object, object, object, object, object)
    update_console = pyqtSignal(str)
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("SAE HB Normal")
        self.model_method = "Normal"
        self.Normal = True
        self.population_sample_size.setVisible(False)
        self.population_sample_size_list.setVisible(False)
        self.population_sample_size_model = None
        self.assign_population_sample_size_button.setVisible(False)
        try:
            self.option_button.clicked.disconnect()
        except Exception:
            pass
        self.option_button.clicked.connect(lambda : show_options_hb(self))
        
        self.iter_update="3"
        self.iter_mcmc="10000"
        self.thin="2"
        self.burn_in="2000"
        
        try:
           self.update_console.disconnect()
        except Exception:
            pass
        # Connect update_console signal to _append_console method
        self.update_console.connect(self._append_console)
        
    def closeEvent(self, event):
        if self.console_dialog:
            self.console_dialog.close()
        threads = threading.enumerate()
        for thread in threads:
            if thread.name == "Unit Level" and thread.is_alive():
                self.parent.autosave_data()
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
        

    import sys
    class ConsoleStream:
        def __init__(self, signal):
            self.signal = signal
        def write(self, text):
            if text.strip():
                self.signal.emit(text)
        def flush(self):
            pass

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
        self.aux_mean_model.setStringList([])
        self.auxilary_model.setStringList([])
        self.of_interest_model.setStringList([])
        self.domain_model.setStringList([])
        self.index_model.setStringList([])
        if self.population_sample_size_model is not None:
            self.population_sample_size_model.setStringList([])
        self.as_factor_model.setStringList([])
        self.of_interest_var = []
        self.auxilary_vars = []
        self.index_var = []
        self.as_factor_var = []
        self.domain_var = []
        self.aux_mean_vars = []
        self.iter_update="3"
        self.iter_mcmc="10000"
        self.thin="2"
        self.burn_in="2000"
    
    def _append_console(self, text):
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
    
    def has_null_values(self, items):
        """Helper method to check if any of the items contain NULL values."""
        return any("[NULL]" in item for item in items)

    def show_null_warning(self):
        """Show warning message for NULL values."""
        QMessageBox.warning(self, "Warning", "Cannot assign variables with NULL values. Please clean your data first.")

    def filter_non_null_items(self, items):
        """Filter out items with NULL values and return only valid items."""
        return [item for item in items if "[NULL]" not in item]

    def deselect_null_items(self, list_widget, model, null_items):
        """Deselect NULL items from the list widget."""
        string_list = model.stringList()
        for idx, val in enumerate(string_list):
            if val in null_items:
                list_widget.selectionModel().select(
                    model.index(idx),
                    QItemSelectionModel.SelectionFlag.Deselect
                )

    def get_selected_items_from_list(self, list_widget, model):
        """Helper method to get selected items from a list widget, filtering out NULL values."""
        selected_indexes = list_widget.selectionModel().selectedIndexes()
        all_selected = [model.data(index) for index in selected_indexes]
        
        # Filter out NULL values
        valid_items = self.filter_non_null_items(all_selected)
        null_items = [item for item in all_selected if "[NULL]" in item]
        
        # If there are NULL items selected, show warning and deselect them
        if null_items:
            self.show_null_warning()
            # Deselect NULL items
            self.deselect_null_items(list_widget, model, null_items)
        
        return valid_items
    
    def handle_assign(self, target_list):
        """
        Flexible assign method that works with any target list.
        Handles assignment from variables_list or between right lists.
        """
        # Define mapping for list identification
        list_mapping = {
            self.variables_list: ("variables", self.variables_model),
            self.of_interest_list: ("of_interest", self.of_interest_model),
            self.auxilary_list: ("auxilary", self.auxilary_model),
            self.as_factor_list: ("as_factor", self.as_factor_model),
            self.domain_list: ("domain", self.domain_model),
            self.index_list: ("index", self.index_model),
            self.auxilary_vars_mean_list: ("aux_mean", self.aux_mean_model)
            }
        
        # Define assignment functions mapping
        assignment_functions = {
            self.of_interest_list: assign_of_interest,
            self.auxilary_list: assign_auxilary,
            self.as_factor_list: assign_as_factor,
            self.domain_list: assign_domains,
            self.index_list: assign_index,
            self.auxilary_vars_mean_list: assign_aux_mean,
            self.population_sample_size_list: assign_population_sample_size
        }
        
        right_lists = {
            self.of_interest_list, self.auxilary_list, self.as_factor_list, 
            self.domain_list, self.index_list, self.auxilary_vars_mean_list, 
            self.population_sample_size_list
        }
        
        # First, try to get selected items from variables_list
        selected_from_variables = self.get_selected_items_from_list(self.variables_list, self.variables_model)
        
        if selected_from_variables and target_list in assignment_functions:
            # Assign from variables_list to target_list
            assignment_functions[target_list](self)
            return
        
        # If no selection in variables_list, check for selections in other right lists
        source_list = None
        selected_items = []
        
        for lst in right_lists:
            if lst != target_list:  # Don't check the target list itself
                items = self.get_selected_items_from_list(lst, list_mapping[lst][1])
                if items:
                    source_list = lst
                    selected_items = items
                    break
        
        if source_list and selected_items and target_list in assignment_functions:
            # Move between right lists
            # First unassign from source
            unassign_variable(self)
            
            # Then select items in variables_list and assign to target
            self.select_items_in_list(self.variables_list, self.variables_model, selected_items)
            assignment_functions[target_list](self)
        elif not selected_from_variables and not selected_items:
            # Show warning if no items are selected
            QMessageBox.information(self, "Information", "Please select items to assign.")

    def handle_unassign(self):
        """
        Flexible unassign method that works with any source list.
        Handles unassignment from any right list back to variables_list.
        """
        list_mapping = {
            self.of_interest_list: ("of_interest", self.of_interest_model),
            self.auxilary_list: ("auxilary", self.auxilary_model),
            self.as_factor_list: ("as_factor", self.as_factor_model),
            self.domain_list: ("domain", self.domain_model),
            self.index_list: ("index", self.index_model),
            self.auxilary_vars_mean_list: ("aux_mean", self.aux_mean_model)
        }

        # Find which list has selected items
        source_list = None
        selected_items = []
        
        for lst, (_, model) in list_mapping.items():
            items = self.get_selected_items_from_list(lst, model)
            if items:
                source_list = lst
                selected_items = items
                break
        
        if source_list and selected_items:
            # Unassign the selected items
            unassign_variable(self)
        else:
            # Show warning if no items are selected in any right list
            QMessageBox.information(self, "Information", "Please select items from assigned lists to unassign.")
    
    def handle_drop(self, target_list, items):
        """
        Handle drag and drop between variable lists.
        """

        # Mapping for lists and their corresponding models and assignment functions
        list_mapping = {
            self.variables_list: ("variables", self.variables_model, None),
            self.of_interest_list: ("of_interest", self.of_interest_model, assign_of_interest),
            self.auxilary_list: ("auxilary", self.auxilary_model, assign_auxilary),
            self.as_factor_list: ("as_factor", self.as_factor_model, assign_as_factor),
            self.domain_list: ("domain", self.domain_model, assign_domains),
            self.index_list: ("index", self.index_model, assign_index),
            self.auxilary_vars_mean_list: ("aux_mean", self.aux_mean_model, assign_aux_mean),
            }
        
        # Filter out NULL values and show warning if any
        valid_items = self.filter_non_null_items(items)
        null_items = [item for item in items if "[NULL]" in item]
        
        # Show warning if NULL items were attempted to be dropped
        if null_items:
            self.show_null_warning()
        
        # If no valid items, return early
        if not valid_items:
            return
        
        def select_items_in_list(list_widget, model, items):
            """Helper function to select items in a list widget."""
            list_widget.clearSelection()
            for idx, val in enumerate(model.stringList()):
                if val in items:
                    list_widget.selectionModel().select(
                        model.index(idx),
                        QItemSelectionModel.SelectionFlag.Select
                    )
        
        # Find source list
        source_list = None
        for lst in list_mapping:
            if any(item in lst.model().stringList() for item in items):
                source_list = lst
                break

        # Handle drag from variables_list to right lists (assign)
        if source_list == self.variables_list:
            if target_list in list_mapping and target_list != self.variables_list:
                select_items_in_list(self.variables_list, self.variables_model, items)
                assign_func = list_mapping[target_list][2]
                if assign_func:
                    assign_func(self)

        # Handle drag from right lists to variables_list (unassign)
        elif target_list == self.variables_list and source_list in list_mapping:
            source_model = list_mapping[source_list][1]
            select_items_in_list(source_list, source_model, items)
            unassign_variable(self)
                
        # Handle drag between right lists (unassign then assign)
        elif (target_list in list_mapping and source_list in list_mapping and 
            target_list != self.variables_list and source_list != self.variables_list):
            if source_list == target_list:
                return  # Same list, do nothing
            
            # First unassign from source
            source_model = list_mapping[source_list][1]
            select_items_in_list(source_list, source_model, items)
            unassign_variable(self)
            
            # Then assign to target
            select_items_in_list(self.variables_list, self.variables_model, items)
            assign_func = list_mapping[target_list][2]
            if assign_func:
                assign_func(self)
    
    def closeEvent(self, event):
        if self.console_dialog:
            self.console_dialog.close()
        threads = threading.enumerate()
        for thread in threads:
            if thread.name == "HB Unit Level" and thread.is_alive():
                self.parent.autosave_data()
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
        self.aux_mean_model.setStringList([])
        self.auxilary_model.setStringList([])
        self.of_interest_model.setStringList([])
        self.domain_model.setStringList([])
        self.index_model.setStringList([])
        if self.population_sample_size_model is not None:
            self.population_sample_size_model.setStringList([])
        self.as_factor_model.setStringList([])
        self.of_interest_var = []
        self.auxilary_vars = []
        self.index_var = []
        self.as_factor_var = []
        self.domain_var = []
        self.aux_mean_vars = []
        self.iter_update="3"
        self.iter_mcmc="10000"
        self.thin="2"
        self.burn_in="2000"
    
    def accept(self):
        if not self.of_interest_var or self.of_interest_var == [""]:
            QMessageBox.warning(self, "Warning", "Variable of interest cannot be empty.")
            self.ok_button.setEnabled(True)
            self.option_button.setEnabled(True)
            self.ok_button.setText("Run Model")
            return
        
        r_script = get_script_hb(self)
        if not check_script(r_script):
            return
        disable_service(self)

        view = self.parent
        sae_model = SaeHBUnit(self.model, self.model2, view)
        controller = SaeHBUnitController(sae_model)
        
        current_context = contextvars.copy_context()
        
        show_console_first = self.show_console_first_checkbox.isChecked()
        if show_console_first:
            self.console_dialog = ConsoleDialog(self)
            self.console_dialog.show()
        
        def run_model_thread():
            results, error, df, plot_paths = None, None, None, None
            try:
                if self.console_dialog:
                    import sys
                    old_stdout = sys.stdout
                    sys.stdout = ConsoleStream(self.update_console)
                from rpy2.rinterface_lib import openrlib
                with openrlib.rlock:
                    results, error, df, plot_paths = current_context.run(controller.run_model, r_script)
                if self.console_dialog:
                    sys.stdout = old_stdout
                if not error:
                    sae_model.model2.set_data(df)
            except Exception as e:
                error = e
            finally:
                if not self.stop_thread.is_set():
                    self.run_model_finished.emit(results, error, sae_model, r_script, plot_paths)
                    self.finnish = True

        def check_run_time():
            if thread.is_alive():
                reply = QMessageBox.question(self, 'Warning', 'Run has been running for more than 5 minute. Do you want to continue?')
                if reply == QMessageBox.StandardButton.No:
                    self.stop_thread.set()
                    QMessageBox.information(self, 'Info', 'Run has been stopped.')
                    enable_service(self, False, "")


        thread = threading.Thread(target=run_model_thread, name="HB Unit Level")
        thread.start()

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(check_run_time)
        timer.start(5*60*1000)
    
    def on_run_model_finished(self, results, error, sae_model, r_script, plot_paths):
        if self.console_dialog:
            self.console_dialog.stop_loading()
            self.console_dialog.close()
        if not error:
            self.parent.update_table(2, sae_model.get_model2())
        if self.reply is not None:
            self.reply.reject()
        display_script_and_output(self.parent, r_script, results, plot_paths)
        enable_service(self, error, results)
        self.finnish = True
        self.close()