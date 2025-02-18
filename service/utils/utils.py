from PyQt6.QtWidgets import QLabel, QTextEdit, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox

def check_script(r_script):
    if r_script == "":
        QMessageBox.warning(None, "Warning", "R sript cannot empty")
        return False
    return True
        

def display_script_and_output(parent, r_script, result):
    """Fungsi untuk menambahkan output baru ke layout dalam bentuk card"""
    # Membuat frame sebagai card
    card_frame = QFrame()
    card_frame.setStyleSheet("""
        QFrame {
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
        }
    """)

    # Layout vertikal untuk card
    card_layout = QVBoxLayout(card_frame)
    card_layout.setSpacing(8)

    # Bagian Script
    label_script = QLabel("<b>R Script:</b>")
    label_script.setStyleSheet("color: #333; margin-bottom: 5px;")
    script_box = QTextEdit()
    script_box.setPlainText(r_script)
    script_box.setReadOnly(True)
    script_box.setStyleSheet("""
        QTextEdit {
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 5px;
            font-family: Consolas, Courier New, monospace;
        }
    """)
    script_box.setFixedHeight(script_box.fontMetrics().lineSpacing() * (r_script.count('\n') + 3))

    # Tambahkan elemen teks ke layout card
    card_layout.addWidget(label_script)
    card_layout.addWidget(script_box)

    # Bagian Output (jika ada)
    if result:
        label_output = QLabel("<b>Output:</b>")
        label_output.setStyleSheet("color: #333; margin-top: 10px; margin-bottom: 5px;")
        result_box = QTextEdit()
        result_box.setPlainText(result)
        result_box.setReadOnly(True)
        result_box.setStyleSheet("""
            QTextEdit {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                font-family: Consolas, Courier New, monospace;
            }
        """)
        max_height = 400
        calculated_height = result_box.fontMetrics().lineSpacing() * (result.count('\n') + 3)
        result_box.setFixedHeight(min(calculated_height, max_height))
        if calculated_height > max_height:
            result_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        else:
            result_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        card_layout.addWidget(label_output)
        card_layout.addWidget(result_box)

    # Tambahkan card ke layout utama
    parent.output_layout.addWidget(card_frame)
    parent.output_layout.addStretch()
    parent.tab_widget.setCurrentWidget(parent.tab3)