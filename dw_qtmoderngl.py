# from PyQt6 import QtCore
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
# from PyQt6.QtGui import QSurfaceFormat

import moderngl

class ModernGLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()

        # fmt = QSurfaceFormat()
        # fmt.setVersion(3, 3)
        # fmt.setSamples(8)  # if you want multi-sampling
        # QSurfaceFormat.setDefaultFormat(fmt)

        # self.timer = QtCore.QElapsedTimer()

    # def initializeGL(self):
        # self.ctx = moderngl.create_context()
        # self.screen = self.ctx.detect_framebuffer()
        # self.init()
        # pass

    # def init(self):
        # pass  # Your initialization code here

    def paintGL(self):
        self.ctx = moderngl.create_context()

        self.screen = self.ctx.detect_framebuffer()
        self.init()
        # self.render()
        self.paintGL = self.render

    # def resizeGL(self, w, h):
        # print('resize', w,h)
        # self.ctx.viewport = (0, 0, w, h)

    # def render(self):
        # self.ctx.clear()  # Set appropriate clear color
        # pass
        # Your rendering code here