from PyQt6.QtWidgets import QLabel, QTextEdit

def display_script_and_output(parent, r_script, result):
    label_script = QLabel("Script R:")
    label = QTextEdit()
    label.setPlainText(r_script)
    label.setReadOnly(True)
    label.setFixedHeight(100)
    
    label_output = QLabel("Output:")
    result_output = QTextEdit()
    result_output.setPlainText(result)
    result_output.setReadOnly(True)
    result_output.setFixedHeight(300)
    
    parent.output_layout.addWidget(label_script)
    parent.output_layout.addWidget(label)
    parent.output_layout.addWidget(label_output)
    parent.output_layout.addWidget(result_output)
    parent.tab_widget.setCurrentWidget(parent.output_tab)