from PyQt6.QtWidgets import QMessageBox

def enable_service(parent):
    parent.ok_button.setEnabled(True)
    parent.option_button.setEnabled(True)
    parent.icon_label.setVisible(False)
    parent.r_script_edit.clear()
    parent.r_script_edit.setReadOnly(False)
    if parent.error != '':
        QMessageBox.information(parent, "Success", "Modelling successfully!")
    parent.ok_button.setText("Run Model")
    
def disable_service(parent):
    parent.r_script_edit.setReadOnly(True)
    parent.icon_label.setVisible(True)
    parent.ok_button.setText("Running model...")
    parent.ok_button.setEnabled(False)
    parent.option_button.setEnabled(False)