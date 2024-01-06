from PyQt6.QtOpenGLWidgets import QOpenGLWidget
import moderngl


class ModernGLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()

    def paintGL(self):
        self.ctx = moderngl.create_context()
        self.screen = self.ctx.detect_framebuffer()
        self.init()
        self.paintGL = self.render
