import numpy as np
import random
import math

from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QVBoxLayout, QWidget,QLabel
from PyQt6.QtGui import QAction, QCursor, QIcon
from PyQt6.QtCore import Qt, QTimer

from qtmoderngl import ModernGLWidget
from renderer_example import HelloWorld2D, PanTool

class LineSegment:
    def __init__(self):
        
        self.startcx=None
        self.startcy=None

        self.myvert = np.array([[]])
        self.mycircle =[]

        self.toolstate=False
        self.distance=0.0

    def toolactive(self, checked):
        self.toolstate = checked
        if not checked:
            print('exit tool')

            global circles
            global livecircles
            livecircles = circles


    def pressed(self, clicks):
        global verts
        global circles

        if self.toolstate:
            if not clicks %2:
                # print("end")
                verts = np.concatenate((verts, self.myvert), axis=0)
                circles.append(self.mycircle)
            else:
                # print("not end")
                circles.append(self.mycircle)
                pass

    def createpoints(self, mp, clicks, window, pan, zfakt):
        global verts
        global liveverts

        global circles
        global livecircles

        sw=window.width()/512/zfakt
        sh=window.height()/512/zfakt
        cx = (mp[0]*2 -1*sw+pan[0])
        cy =(-mp[1]*2 +1*sh+pan[1])


        if not clicks %2:
            self.startcx=cx
            self.startcy=cy
    
        self.mycircle = drawCircle(0.015, cx, cy)

        self.myvert = np.array([
            [self.startcx, self.startcy, 1,1,1,1],
            [cx, cy, 1,1,1,1]
        ])
        liveverts = np.concatenate((verts, self.myvert), axis=0)

        livecircles = circles + [self.mycircle]
        

        # Calculate the Euclidean distance between the two points
        self.distance = np.linalg.norm(np.array([self.startcx, self.startcy]) - np.array([cx, cy]))
        # print(self.distance)

def point_on_line(mouse_pt, a_pt, b_pt, precision=0.035):
    # Check if the mouse point is on the line segment defined by a_pt and b_pt

    # Vectors from line start to mouse point and along the line segment
    ap = np.array([mouse_pt[0] - a_pt[0], mouse_pt[1] - a_pt[1]])
    ab = np.array([b_pt[0] - a_pt[0], b_pt[1] - a_pt[1]])

    # Dot products
    dot_ap_ab = np.dot(ap, ab)
    dot_ab_ab = np.dot(ab, ab)

    # Check if the mouse point is close enough to the line segment
    if 0 <= dot_ap_ab <= dot_ab_ab and abs(np.cross(ap, ab)) < precision:
        return True  # Mouse point is on the line segment
    else:
        return False  # Mouse point is not on the line segment

def checkpoint(verts, mouse_pt, wsize, zf):
    sw=wsize[0]/512/zf
    sh=wsize[1]/512/zf
    cx = (mouse_pt[0]*2 -1*sw+pan_tool.value[0])
    cy =(-mouse_pt[1]*2 +1*sh+pan_tool.value[1])

    for i in range(0, len(verts), 2):
        a_pt =verts[i, :2]
        b_pt = verts[i + 1, :2]
        # print(x1, y1, x2, y2)
        verts[i, 3] = 1
        verts[i+1, 3] = 1

        if point_on_line((cx,cy), a_pt, b_pt):
            # print(f"Mouse coordinates are over the line segment ({a_pt}) to ({b_pt})")
            verts[i, 3] = 0
            verts[i+1, 3] = 0
            # pass

def checkclickedpoint(verts, mouse_pt, wsize, zf):
    sw=wsize[0]/512/zf
    sh=wsize[1]/512/zf
    cx = (mouse_pt[0]*2 -1*sw+pan_tool.value[0])
    cy =(-mouse_pt[1]*2 +1*sh+pan_tool.value[1])

    for i in range(0, len(verts), 2):
        a_pt =verts[i, :2]
        b_pt = verts[i + 1, :2]
        # print(x1, y1, x2, y2)
        verts[i, 2] = 1
        verts[i+1, 2] = 1

        if point_on_line((cx,cy), a_pt, b_pt):
            # print(f"Mouse coordinates are over the line segment ({a_pt}) to ({b_pt})")
            verts[i, 2] = 0
            verts[i+1, 2] = 0
            # pass

verts = np.array([[0,0, 1,1,1,1],[0,0, 1,1,1,1]])
liveverts =np.array([[0,0, 1,1,1,1],[0,0, 1,1,1,1]]) #verts+create line aktivais

pan_tool = PanTool()
l = LineSegment()

circles = []
livecircles =[]

def drawCircle( radius,  x1,  y1):
    circle_dots = []  # Array to store dots for the current circle

    for angle in range(0, 360, 60):
    # for(double i = 0; i < 2 * M_PI; i += 2 * M_PI / NUMBER_OF_VERTICES):
        rad_angle = angle * 3.14 / 180
        circle_dots.append([x1+radius*math.sin(rad_angle), y1+radius*math.cos(rad_angle), 1,1,1,1])
        # print(circle_dots)
    
    # Append the circle_dots array to the circles list
    # global circles
    # circles.append(circle_dots)
    # print (circles)
    return circle_dots

class MyWidget(ModernGLWidget):
    def __init__(self):
        super(MyWidget, self).__init__()

        self.scene = None
        self.zoomy = 0
        self.zfakt  =1

        self.createlineactive=False
        self.clickcount=0

    def init(self):
        # self.resize(512, 512) shis ir qt mainwindow resizers
        self.ctx.viewport = (0, 0, 512, 512)
        self.scene = HelloWorld2D(self.ctx)

    def render(self):
        self.ctx.viewport = (0, 0, self.size().width(), self.size().height())
        self.screen.use()
        self.scene.clear()

        self.scene.distancetext(str(l.distance))
        self.scene.linerender(liveverts, self.zfakt)
        self.scene.circl(np.array(livecircles))

    def mycoord(self):
        # origin ir main windowa kreisais augsejais sturis 0,0
        # pozicija tiek nolasita pa visu ekranu!!
        local_pos = self.mapFromGlobal(QCursor.pos())
        wsize=[
            local_pos.x()/ 512/self.zfakt, #self.size().width(),
            local_pos.y()/ 512/self.zfakt #self.size().height()
        ]
        return wsize
    
    def createlinetool(self, checked):
        self.createlineactive = checked
        self.clickcount=0
        l.toolactive(checked)

        
    def wheelEvent(self, event):
        self.zoomy +=event.angleDelta().y()/120
        self.zfakt=pow(1.4, self.zoomy)
        self.scene.zom(self.zfakt)
        self.update()
        self.render()
        

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            pan_tool.start_drag(*self.mycoord())
            self.scene.pan(pan_tool.value)
        
        if event.button() == Qt.MouseButton.LeftButton:
            # self.scene.chcol( random.uniform(1, 1))

            checkclickedpoint(liveverts, self.mycoord(),(self.size().width(), self.size().height()), self.zfakt)

            if self.createlineactive:
                l.createpoints(self.mycoord(), self.clickcount, self.size(), pan_tool.value, self.zfakt)
                self.clickcount+=1
                l.pressed(self.clickcount)

        self.update()

    def mouseMoveEvent(self, event):
        pan_tool.dragging(*self.mycoord())
        self.scene.pan(pan_tool.value)

        if self.createlineactive:
            l.createpoints(self.mycoord(), self.clickcount, self.size(), pan_tool.value, self.zfakt)

        
        # print(QCursor.pos())
        checkpoint(liveverts, self.mycoord(),(self.size().width(), self.size().height()), self.zfakt)

        self.update()

    def mouseReleaseEvent(self, event):
        pan_tool.stop_drag(*self.mycoord())
        self.scene.pan(pan_tool.value)
        self.update()


def run_app():
    app = QApplication([])

    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setSamples(4)  # if you want multi-sampling
    # QSurfaceFormat.setDefaultFormat(fmt)
    
    mywidget = MyWidget()
    mywidget.setMouseTracking(True)
    mywidget.setFormat(fmt)
    
    window = QMainWindow()
    window.setMouseTracking(True)
    window.setCentralWidget(mywidget)
    window.setGeometry(100, 100, 512, 512)

    toolbar = QToolBar()
    window.addToolBar(toolbar)

    create_line = QAction("Create Line", window)
    create_line.setCheckable(True)
    create_line.toggled.connect(mywidget.createlinetool)
    toolbar.addAction(create_line)

    join_dots = QAction("Join Dots", window)
    # join_dots.triggered.connect()
    toolbar.addAction(join_dots)

    toggle_line = QAction("Toggle lines", window)
    # toggle_line.triggered.connect()
    toolbar.addAction(toggle_line)

    drag_action = QAction(QIcon("msdf_gen/fonts.bmp"),"Drag", window)
    drag_action.setCheckable(True)
    # drag_action.triggered.connect()
    toolbar.addAction(drag_action)

    window.show()
    app.exec()


if __name__ == "__main__":
    run_app()
