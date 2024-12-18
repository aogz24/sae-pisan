import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from view.MainWindow import MainWindow



app=QtWidgets.QApplication(sys.argv)
window=MainWindow()
window.show()
app.exec()