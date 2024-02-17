from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QSurfaceFormat
import moderngl


class ModernGLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__() 
        fmt = QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setSamples(4) # multi-sampling
        self.setFormat(fmt)

    def initializeGL(self):
        self.ctx = moderngl.create_context()
        self.init()

    def resizeGL(self, width, height):
        self.screen = self.ctx.detect_framebuffer()

    def paintGL(self):
        self.render()
