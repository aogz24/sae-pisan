from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import sys
from controller.FileController import FileController
from view.MainWindow import MainWindow
from model.TableModel import TableModel
from view.CsvDialogOption import CSVOptionsDialog
import pandas as pd

def main():
    app = QApplication(sys.argv)

    # Inisialisasi model, view, dan controller
    data = pd.DataFrame([], columns=["Columns 1", "Columns 2", "Columns 3"])  # Dengan beberapa kolom
    model1 = TableModel(data)
    model2 = TableModel(data)
    view = MainWindow()  # View (Tampilan utama)
    controller = FileController(model1, model2, view)

    # icon aplication
    view.setWindowIcon(QIcon('resources/icons/icon.svg'))
    # Tampilkan window utama
    view.show()

    # Mulai aplikasi
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
