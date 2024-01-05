from PyQt6.QtWidgets import QApplication
from dw_mywidget import *

def run_app():
    app = QApplication([])

    mywindow = MyMainWindow()
    mywindow.show()
    app.exec()

if __name__ == "__main__":
    run_app()
