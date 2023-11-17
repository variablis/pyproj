from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar
from PyQt6.QtGui import QPainter, QPen, QColor, QTransform
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QAction


class Dot:
    def __init__(self, pos):
        self.pos = pos

class Canvas(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.dots = []
        self.lines = []
        self.dragging = False
        self.last_pos = QPointF()
        self.create_line = False
        self.grid_size = 20
        self.grid_color = QColor(200, 200, 200)
        self.translation = QTransform()
        self.can_drag_canvas = False  # Flag to control canvas dragging
        self.selected_dot = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.begin(self)
        painter.fillRect(event.rect(), QColor("white"))

        self.draw_grid(painter)

        pen = QPen()
        pen.setWidth(2)
        pen.setColor(QColor("black"))
        painter.setPen(pen)

        transform = self.translation
        painter.setTransform(transform)

        for dot in self.dots:
            painter.drawEllipse(dot.pos, 3, 3)

        if self.create_line:
            for i in range(1, len(self.dots)):
                painter.drawLine(self.dots[i - 1].pos, self.dots[i].pos)
            if len(self.dots) > 2:
                painter.drawLine(self.dots[0].pos, self.dots[-1].pos)

        painter.end()

    def draw_grid(self, painter):
        # Adjust drawing the grid based on translation
        grid_transform = QTransform()
        grid_transform.translate(self.translation.dx(), self.translation.dy())

        for x in range(0, self.width(), self.grid_size):
            painter.setTransform(grid_transform)
            painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.DashLine))
            painter.drawLine(x, 0-200, x, self.height())

        for y in range(0, self.height(), self.grid_size):
            painter.setTransform(grid_transform)
            painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.DashLine))
            painter.drawLine(0-200, y, self.width(), y)


    def mousePressEvent(self, event):

        pos = event.position()
        if not self.create_line and not self.can_drag_canvas:
            for dot in self.dots:
                if (dot.pos - pos).manhattanLength() < 8:
                    self.selected_dot = dot
                    break

        if self.create_line:
            # pos = event.position()
            self.dots.append(Dot(pos))

            if len(self.dots) % 2 == 0:
                self.lines.append([len(self.dots) - 2, len(self.dots) - 1])

            self.update()
            return

        if self.can_drag_canvas:
            self.last_pos = event.position()
            self.dragging = True

    def mouseMoveEvent(self, event):


        if not self.create_line and not self.can_drag_canvas and self.selected_dot:
            new_pos = event.position()
            self.selected_dot.pos = new_pos
            self.update()

        if self.can_drag_canvas and self.dragging:
            delta = event.position() - self.last_pos
            self.translation.translate(delta.x(), delta.y())
            self.last_pos = event.position()
            self.update()

    def mouseReleaseEvent(self, event):
    
        if not self.create_line and not self.can_drag_canvas:
            self.selected_dot = None

        if self.can_drag_canvas:
            self.dragging = False

    def enable_create_line(self, enable):
        self.create_line = enable
        # if not enable:
        #     self.dots.clear()
        #     self.lines.clear()
        self.update()

    def enable_drag(self, enabled):
        self.can_drag_canvas = enabled

    def point_close_to_dot(self, point, dot_pos):
        return (point - dot_pos).manhattanLength() < 5

    def remove_dot_at(self, pos):
        for i, dot in enumerate(self.dots):
            if self.point_close_to_dot(pos, dot.pos):
                del self.dots[i]
                self.update()
                return

    def resizeEvent(self, event):
        self.translation.translate(self.width() / 2, self.height() / 2)
        self.update()

    def create_line_action(canvas):
        canvas.create_line = not canvas.create_line
        canvas.update()

    def join_dots_action(self):
        if len(self.dots) == 2:
            # Calculate the average center
            avg_pos = QPointF((self.dots[0].pos.x() + self.dots[1].pos.x()) / 2,
                             (self.dots[0].pos.y() + self.dots[1].pos.y()) / 2)
            self.dots[0].pos = avg_pos
            self.dots.pop(1)
            self.update()

    def toggle_line_action(self):
        self.create_line = not self.create_line
        self.update()


def run_app():
    app = QApplication([])
    window = QMainWindow()
    canvas = Canvas()
    window.setCentralWidget(canvas)
    window.setGeometry(100, 100, 400, 400)

    toolbar = QToolBar()
    window.addToolBar(toolbar)

    create_line = QAction("Create Line", window)
    create_line.setCheckable(True)
    create_line.triggered.connect(lambda checked: canvas.enable_create_line(checked))
    toolbar.addAction(create_line)

    join_dots = QAction("Join Dots", window)
    join_dots.triggered.connect(canvas.join_dots_action)
    toolbar.addAction(join_dots)

    toggle_line = QAction("Toggle lines", window)
    toggle_line.triggered.connect(canvas.toggle_line_action)
    toolbar.addAction(toggle_line)

    drag_action = QAction("Drag", window)
    drag_action.setCheckable(True)
    drag_action.triggered.connect(lambda checked: canvas.enable_drag(checked))
    toolbar.addAction(drag_action)

    exit_action = QAction("Exit", window)
    exit_action.triggered.connect(app.quit)
    menu = window.menuBar()
    file_menu = menu.addMenu("File")
    file_menu.addAction(exit_action)

    window.show()
    app.exec()

if __name__ == "__main__":
    run_app()
