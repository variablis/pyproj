from drw_test import *

def run_app():
    app = QApplication([])

    mywindow = MyMainWindow()
    mywindow.show()
    app.exec()

if __name__ == "__main__":
    run_app()
