from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QSurfaceFormat

class MyOpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        format = QSurfaceFormat()
        format.setVersion(3, 3)  # Set OpenGL version
        format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)  # Set profile
        format.setDepthBufferSize(24)  # Set depth buffer size
        format.setSamples(4)  # Set number of samples for multisampling
        self.setFormat(format)

    def initializeGL(self):
        # Your OpenGL initialization code here
        pass

    def paintGL(self):
        # Your rendering code here
        pass

def run_app():
    app = QApplication([])
    window = QMainWindow()
    widget = MyOpenGLWidget()
    window.setCentralWidget(widget)
    window.setGeometry(100, 100, 800, 600)
    window.show()
    app.exec()

if __name__ == "__main__":
    run_app()
