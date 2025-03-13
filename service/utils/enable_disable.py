from PyQt6.QtWidgets import QMessageBox

def enable_service(parent, error, result):
    """
    Enables and updates the UI elements of the parent widget based on the result of a modelling process.
    Args:
        parent (QWidget): The parent widget containing the UI elements to be updated.
        error (bool): A flag indicating whether an error occurred during the modelling process.
        result (str): The result message to be displayed in case of an error.
    Updates:
        - Enables the 'ok_button' and 'option_button' of the parent widget.
        - Hides the 'icon_label' of the parent widget.
        - Clears and makes the 'r_script_edit' editable.
        - Displays a success message if no error occurred, otherwise displays an error message.
        - Sets the text of the 'ok_button' to "Run Model".
    """
    
    parent.ok_button.setEnabled(True)
    parent.option_button.setEnabled(True)
    parent.icon_label.setVisible(False)
    parent.r_script_edit.clear()
    parent.r_script_edit.setReadOnly(False)
    if not error:
        QMessageBox.information(parent, "Success", "Modelling finished!")
    else:
        QMessageBox.critical(parent, "Error", result)
    parent.ok_button.setText("Run Model")
    
def disable_service(parent):
    """
    Disables various UI components of the given parent object.
    This function sets the following properties of the parent object:
    - Sets the r_script_edit component to read-only.
    - Makes the icon_label component visible.
    - Changes the text of the ok_button to "Running model...".
    - Disables the ok_button.
    - Disables the option_button.
    Args:
        parent: The parent object containing the UI components to be modified.
    """
    
    parent.r_script_edit.setReadOnly(True)
    parent.icon_label.setVisible(True)
    parent.ok_button.setText("Running model...")
    parent.ok_button.setEnabled(False)
    parent.option_button.setEnabled(False)