from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QIcon, QPixmap
import sys
from controller.FileController import FileController
from controller.ExplorationController import ExplorationController
from view.MainWindow import MainWindow
from model.TableModel import TableModel
from view.components.CsvDialogOption import CSVOptionsDialog
# from model.SummaryData import SummaryData
import polars as pl
import os
import subprocess

def main():
    path = os.path.join(os.path.dirname(__file__), 'R', 'R-4.4.2')
    if not os.path.exists(path):
        url = "https://cran.r-project.org/bin/windows/base/R-4.4.2-win.exe"
        installer_path = os.path.join(os.path.expanduser("~"), "R-latest.exe")

        subprocess.check_call(['curl', '-o', installer_path, url])

        # Define the relative path for the R installation directory
        relative_path = os.path.join(os.path.dirname(__file__), 'R', 'R-4.4.2')

        # Run the installer silently with the correct directory
        # Run the installer silently with the correct directory
        subprocess.check_call([installer_path, '/SILENT', f'/DIR={relative_path}'])
    os.environ['R_HOME'] = path
    from service.main.LoadingR import loadR
    app = QApplication(sys.argv)

    # Create and display the splash screen
    splash_pix = QPixmap(os.path.join(os.path.dirname(__file__), 'assets', 'splash.png'))
    splash = QSplashScreen(splash_pix)
    splash.show()

    loadR(splash)

    view = MainWindow()  # View (Tampilan utama)
    controller = FileController(view.model1, view.model2, view)
    ControllerExploration = ExplorationController(view.model1, view.model2, view)

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
