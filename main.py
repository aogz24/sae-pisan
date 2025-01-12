from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QIcon, QPixmap
import sys
from controller.FileController import FileController
from view.MainWindow import MainWindow
from model.TableModel import TableModel
from view.components.CsvDialogOption import CSVOptionsDialog
import polars as pl
import os
import time

def main():
    os.environ['R_HOME'] = 'C:\\Program Files\\R\\R-4.4.2'
    
    app = QApplication(sys.argv)
    
    # Create and display the splash screen
    splash_pix = QPixmap(os.path.join(os.path.dirname(__file__), 'assets', 'splash.png'))
    splash = QSplashScreen(splash_pix)
    splash.show()
    
    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri
    pandas2ri.activate()
    ro.r('library(sae)')
    splash.showMessage("Loading R libraries...", 1)
    
    view = MainWindow()  # View (Tampilan utama)
    controller = FileController(view.model1, view.model2, view)
    
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
    
    # Close the splash screen
    splash.finish(view)

    # Mulai aplikasi
    sys.exit(app.exec())
    

if __name__ == "__main__":
    main()
