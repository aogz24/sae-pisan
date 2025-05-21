from PyQt6.QtWidgets import QApplication
from view.components.SplashScreen import SplashScreen
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
import sys
import os
import pyuac
from controller.FileController import FileController
from service.main.CheckEnviroment import check_environment

def load_stylesheet():
    """
    Fungsi untuk memuat stylesheet dari file .qss.
    """
    stylesheet_path = os.path.join(os.path.dirname(__file__), 'assets', 'style', 'style.qss')
    if os.path.exists(stylesheet_path):
        with open(stylesheet_path, 'r') as file:
            return file.read()
    else:
        print(f"Stylesheet tidak ditemukan di {stylesheet_path}")
        return ""

def main():
    
    # Inisialisasi aplikasi PyQt
    app = QApplication(sys.argv)

    # Buat dan tampilkan splash screen
    splash_pix = QPixmap(os.path.join(os.path.dirname(__file__), 'assets', 'splash.png'))
    splash = SplashScreen(splash_pix)
    splash.show()
    
    # Cek dan siapkan lingkungan R
    path = os.path.join(os.path.dirname(__file__), 'R', 'R-4.4.2')
    original_path = os.path.dirname(__file__)
    check_environment(path, original_path)

    from service.main.LoadingR import loadR  # Load modul R setelah check_environment

    loadR(splash)
    
    from view.MainWindow import MainWindow
    splash.update_message()

    # Inisialisasi view dan controller
    view = MainWindow()  # Tampilan utama aplikasi
    view.setWindowFlags(view.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)  # Set window flag to be on top initially
    view.show()
    view.setWindowFlags(view.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)  # Remove the always on top flag
    controller = FileController(view.model1, view.model2, view)
    # ControllerExploration = ExplorationController(view.model1, view.model2, view)
    
    app.setStyleSheet(view.load_stylesheet_with_font_size(14))

    def load_stylesheet():
        # Gunakan jalur relatif untuk mengakses style.qss
        stylesheet_path = os.path.join(os.path.dirname(__file__), 'assets','style', 'style.qss')
        with open(stylesheet_path, 'r') as file:
            return file.read()

    # Muat dan terapkan stylesheet global untuk aplikasi
    app.setStyleSheet(load_stylesheet())  # Terapkan ke seluruh aplikasi

    app.styleHints().setColorScheme(Qt.ColorScheme.Light);
    
    # Set icon aplikasi
    view.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'assets', 'icon.svg')))

    # Muat stylesheet
    stylesheet = load_stylesheet()
    if stylesheet:
        view.setStyleSheet(stylesheet)

    # Tampilkan window utama
    view.show()

    # Tutup splash screen setelah aplikasi siap
    splash.finish(view)

    # Mulai aplikasi
    sys.exit(app.exec())


if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        # pyuac.runAsAdmin()
        main()
    else:
        main()
