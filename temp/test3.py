import moderngl_window as mglw

from PyQt6.QtWidgets import QApplication, QMainWindow

# class Test(mglw.WindowConfig):
#     gl_version = (3, 3)

#     def render(self, time, frametime):
#         self.ctx.clear(1.0, 0.0, 0.0, 0.0)

# Test.run()

import moderngl_window
from moderngl_window.conf import settings

settings.WINDOW['class'] = 'moderngl_window.context.glfw.Window'
settings.WINDOW['gl_version'] = (3, 2)
# ... etc ...

# Creates the window instance and activates its context
canvas = moderngl_window.create_window_from_settings()


def run_app():
    app = QApplication([])
    window = QMainWindow()
    # canvas = Test()
    window.setCentralWidget(canvas)
    window.setGeometry(100, 100, 512, 512)


    window.show()
    app.exec()

if __name__ == "__main__":
    run_app()