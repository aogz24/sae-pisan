from PyQt6.QtWidgets import QLabel, QTextEdit, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox
import os
from PyQt6.QtGui import QPixmap

def check_script(r_script):
    """
    Checks if the provided R script string is not empty.
    Parameters:
    r_script (str): The R script string to check.
    Returns:
    bool: True if the R script string is not empty, False otherwise.
    """
    
    if r_script == "":
        QMessageBox.warning(None, "Warning", "R sript cannot empty")
        return False
    return True
        

from PyQt6.QtWidgets import QTableView, QAbstractItemView, QVBoxLayout, QHeaderView
from PyQt6.QtGui import QStandardItemModel, QStandardItem

import polars as pl  # Pastikan Anda sudah mengimpor polars

def display_script_and_output(parent, r_script, results, plot_paths=None):
    """
    Adds a new output card to the layout displaying the provided R script and its result.
    Parameters:
    parent (object): The parent widget containing the layout to which the card will be added.
    r_script (str): The R script to be displayed in the card.
    results (dict or str): The output result of the R script to be displayed in the card. If empty or None, only the script will be displayed.
    plot_paths (list): List of paths to plot images to be displayed.
    Returns:
    None
    """
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
    if isinstance(results, dict):
        label_output = QLabel("<b>Output:</b>")
        label_output.setStyleSheet("color: #333; margin-top: 10px; margin-bottom: 5px;")
        card_layout.addWidget(label_output)
        
        if "Model" in results:
            model_value = results["Model"]
            model_label = QLabel(f"Summary of Modelling {model_value}")
            model_label.setStyleSheet("font-size: 20px; color: #333; margin-top: 5px;")
            card_layout.addWidget(model_label)

        for key, value in results.items():
            # Skip displaying if the key is "Model"
            if key == "Model":
                continue

            # Tambahkan header untuk setiap key
            key_label = QLabel(f"<b>{key}:</b>")
            key_label.setStyleSheet("color: #333; margin-top: 5px;")
            card_layout.addWidget(key_label)

            if isinstance(value, pl.DataFrame):
                # Tampilkan DataFrame polars ke dalam QTableView
                table_view = QTableView()
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels(value.columns)

                for row in value.iter_rows(named=True):
                    items = [QStandardItem(str(row[col])) for col in value.columns]
                    model.appendRow(items)

                table_view.setModel(model)
                table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                table_view.horizontalHeader().setFixedHeight(50)

                # Hitung tinggi tabel berdasarkan jumlah baris
                row_height = table_view.verticalHeader().defaultSectionSize()
                header_height = table_view.horizontalHeader().height()
                total_height = row_height * model.rowCount() + header_height + 20  # Tambahkan margin
                table_view.setFixedHeight(total_height)

                table_view.setStyleSheet("""
                    QTableView {
                        background-color: #fff;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                        padding: 5px;
                        font-family: Consolas, Courier New, monospace;
                    }
                """)
                card_layout.addWidget(table_view)
            else:
                # Tampilkan nilai biasa sebagai teks
                value_label = QLabel(str(value))
                value_label.setStyleSheet("color: #333; margin-left: 10px;")
                card_layout.addWidget(value_label)
    elif results:
        label_output = QLabel("<b>Output:</b>")
        label_output.setStyleSheet("color: #333; margin-top: 10px; margin-bottom: 5px;")
        result_box = QTextEdit()
        result_box.setPlainText(results)
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
        

        card_layout.addWidget(label_output)
        card_layout.addWidget(result_box)

    if plot_paths is not None:
        label_plot = QLabel("<b>Plot:</b>")
        label_plot.setStyleSheet("color: #333; margin-top: 10px; margin-bottom: 5px;")
        card_layout.addWidget(label_plot)

        for plot_path in plot_paths:
            if os.path.exists(plot_path):
                pixmap = QPixmap(plot_path)
                label = QLabel()
                label.setPixmap(pixmap)
                label.setFixedSize(500, 350)
                label.setScaledContents(True)
                label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
                card_layout.addWidget(label)
                # Remove the plot file after displaying it
                os.remove(plot_path)

    # Tambahkan card ke layout utama
    parent.output_layout.addWidget(card_frame)
    parent.output_layout.addStretch()
    parent.tab_widget.setCurrentWidget(parent.tab3)