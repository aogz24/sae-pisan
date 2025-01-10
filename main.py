from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import sys
from controller.FileController import FileController
from view.MainWindow import MainWindow
from model.TableModel import TableModel
from view.components.CsvDialogOption import CSVOptionsDialog
import polars as pl
import os

def main():
    app = QApplication(sys.argv)

    # Inisialisasi model, view, dan controller
    columns = [f"Column {i+1}" for i in range(30)]
    data1 = pl.DataFrame({col: [""] * 10 for col in columns})
    data2 = pl.DataFrame({
        "Estimated Value": [""] * 10,
        "Standar Error": [""] * 10,
        "CV": [""] * 10
    })
    model1 = TableModel(data1)
    model2 = TableModel(data2)
    view = MainWindow()  # View (Tampilan utama)
    controller = FileController(model1, model2, view)
    
    def load_stylesheet(self):
        # Gunakan jalur relatif untuk mengakses style.qss
        stylesheet_path = os.path.join(os.path.dirname(__file__), 'assets','style', 'style.qss')
        with open(stylesheet_path, 'r') as file:
            return file.read()

    # icon aplication
    view.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'assets', 'icon.svg')))
    # Tampilkan window utama
    view.show()
    view.setStyleSheet(load_stylesheet(view))

    # Mulai aplikasi
    sys.exit(app.exec())
    


if __name__ == "__main__":
    main()
