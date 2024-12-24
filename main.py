from PyQt6.QtWidgets import QApplication
import sys
from controller.FileController import FileController
from view.MainWindow import MainWindow
from model.TableModel import TableModel
from view.CsvDialogOption import CSVOptionsDialog
import polars as pl

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

    # Tampilkan window utama
    view.show()

    # Mulai aplikasi
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
