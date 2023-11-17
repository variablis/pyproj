import numpy as np

from qtmoderngl import QModernGLWidget
import sys

from PyQt6 import QtWidgets

from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction, QCursor
import random
import math

from renderer_example import HelloWorld2D, PanTool


def vertices():
    x = np.linspace(-1.0, 1.0, 50)
    y = np.random.rand(50) - 0.5
    r = np.random.rand(50)
    g = np.random.rand(50)
    b = np.random.rand(50)
    a = np.ones(50)
    return np.dstack([x, y, r, g, b, a])


verts = vertices()

verts = np.array([[0,0, 1,1,1,1],[1,1, 1,1,1,1], [3,2, 1,1,1,1], [2,2, 1,1,1,1]])
# print(verts)

pan_tool = PanTool()

cc = np.array(  [[0,0, 0,1,1,1],[1,1, 1,1,1,1], [-1,-.1, 1,1,1,1]])

circles = []

def drawCircle( radius,  x1,  y1):
    # angle = 0
    # x2=0
    # y2=0
    circle_dots = []  # Array to store dots for the current circle

    # for angle in range(0, 360, 60):
    #     rad_angle = angle * 3.14 / 180
    #     x2 = x1+radius * math.sin(rad_angle)
    #     y2 = y1+radius * math.cos(rad_angle)

    #     # Append the vertices to the circle_dots array
    #     circle_dots.append([x2, y2])

    # circle_dots.append([x1,y1, 1,1,1,1])

    for angle in range(0, 360, 60):
    # for(double i = 0; i < 2 * M_PI; i += 2 * M_PI / NUMBER_OF_VERTICES):
        rad_angle = angle * 3.14 / 180
        circle_dots.append([x1+radius*math.sin(rad_angle), y1+radius*math.cos(rad_angle), 1,1,1,1])
        # circle_dots.append(math.sin(angle) * radius)
        # print(circle_dots)
    


    # Append the circle_dots array to the circles list
    global circles
    circles.append(circle_dots)
    # print (circles)

# drawCircle(0.2, 12, 22)
# drawCircle(0.2, 3, 44)

# my_np_array = np.array(circles)

class MyWidget(QModernGLWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        self.scene = None

    def init(self):
        # self.resize(512, 512)
        self.ctx.viewport = (0, 0, 512, 512)
        self.scene = HelloWorld2D(self.ctx)

    def render(self):
        self.screen.use()
        self.scene.clear()
        # self.scene.plot(verts, type='line')
        self.scene.kuku(verts)

        self.scene.dodo(np.array(circles))
        # self.scene.dodo(cc)
        

    def linecreate(self, x,y):
        # local_pos = self.mapFromGlobal(QCursor.pos())
        # mx = local_pos.x()
        # my = local_pos.y()

        global verts

        px=pan_tool.value[0]
        py=pan_tool.value[1]

        cx = (x*2 -1)
        cy =(-y*2 +1)
        myvert = np.array([[0,0, 1,1,1,1],
                          [cx+px, cy+py, 1, random.uniform(0, 1) ,1,1]])
        verts = np.concatenate((verts, myvert), axis=0)

        # print(mx,my)
        # print(cx, cy, px,py)

        drawCircle(0.02, cx+px, cy+py)

    def mycoord(self):
        local_pos = self.mapFromGlobal(QCursor.pos())
        wsize= (
            local_pos.x() / self.size().width(),
            local_pos.y() / self.size().height()
            )
        return wsize
        

    def mousePressEvent(self, event):
        # global verts
        # verts = vertices()

        self.linecreate(*self.mycoord())


        self.scene.chcol( random.uniform(0, 1))

        # self.scene.mcoord(event.position().x() / self.wsizex, event.position().y() / 512)


        pan_tool.start_drag(*self.mycoord())
        self.scene.pan(pan_tool.value)
        self.update()

    def mouseMoveEvent(self, event):

        # local_pos = self.mapFromGlobal(QCursor.pos())
        # print(local_pos.x(), local_pos.y())

        pan_tool.dragging(*self.mycoord())
        self.scene.pan(pan_tool.value)
        self.update()

    def mouseReleaseEvent(self, event):
        pan_tool.stop_drag(*self.mycoord())
        self.scene.pan(pan_tool.value)
        self.update()


# app = QApplication(sys.argv)
# widget = MyWidget()
# widget.show()
# sys.exit(app.exec())

def run_app():
    app = QApplication([])
    
    mywidget = MyWidget()
    mywidget.setMouseTracking(True)

    window = QMainWindow()
    window.setCentralWidget(mywidget)
    window.setGeometry(100, 100, 512, 512)

    toolbar = QToolBar()
    window.addToolBar(toolbar)





    create_line = QAction("Create Line", window)
    create_line.setCheckable(True)
    # create_line.triggered.connect()
    toolbar.addAction(create_line)

    join_dots = QAction("Join Dots", window)
    # join_dots.triggered.connect()
    toolbar.addAction(join_dots)

    toggle_line = QAction("Toggle lines", window)
    # toggle_line.triggered.connect()
    toolbar.addAction(toggle_line)

    drag_action = QAction("Drag", window)
    drag_action.setCheckable(True)
    # drag_action.triggered.connect()
    toolbar.addAction(drag_action)

    window.show()
    app.exec()

if __name__ == "__main__":
    run_app()