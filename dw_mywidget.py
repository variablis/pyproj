from PyQt6.QtGui import QAction, QCursor, QIcon
from PyQt6.QtCore import Qt, QTimer

from pathlib import Path

from dw_qtmoderngl import ModernGLWidget
from dc_renderer import Renderer, PanTool

from dc_point import Point

from dc_linedata import LineData, Group
from dc_text import TextData
from df_math import *

from dc_linesegment import LineSegment, linedrag, linestopdrag, check_dr_point, checkclickedpoint, checkpoint


# absolute path needed for pyinstaller
bundle_dir = Path(__file__).parent
path_to_img = Path.cwd() / bundle_dir / "img"


pan_tool = PanTool()
lseg = LineSegment()

uds=None


# convert mouse screen pixel coordinates to normalized coordinates -1.0 to 1.0
def normalized_coordinates(mouse_pt, window_size, zoom_factor):
    screen_width = window_size[0] / 512 / zoom_factor
    screen_height = window_size[1] / 512 / zoom_factor
    normalized_x = mouse_pt.x * 2 - 1 * screen_width + pan_tool.value[0]
    normalized_y = -mouse_pt.y * 2 + 1 * screen_height + pan_tool.value[1]

    return normalized_x, normalized_y


class MyWidget(ModernGLWidget):
    def __init__(self):
        super(MyWidget, self).__init__()

        self.scene = None
        self.zoomy = 0
        self.zfakt  =1

        self.createlineactive=False
        self.clickcount=0
        self.user_drag_start=None
        self.startDragDistance=0.001

    def init(self):
        # self.resize(512, 512) shis ir qt mainwindow resizers
        self.ctx.viewport = (0, 0, 512, 512)
        self.scene = Renderer(self.ctx)


    def render(self):
        self.ctx.viewport = (0, 0, self.size().width(), self.size().height())
        self.screen.use()
        self.scene.clear()

        # self.scene.textgen(str(lseg.distance)+'...'+str(lseg.degrees), lseg.startpoint)
        
        self.scene.updateMvp(self.zfakt)

        self.scene.textrender(TextData.makeBuffer())
        self.scene.linerender(LineData.makeBuffer())
        # self.scene.circl(np.array(livecircles))
        

    def mycoord(self):
        # origin ir main windowa kreisais augsejais sturis 0,0
        # pozicija tiek nolasita pa visu ekranu!!
        local_pos = self.mapFromGlobal(QCursor.pos())
 
        mousepos = Point(local_pos.x()/ 512/self.zfakt, 
                         local_pos.y()/ 512/self.zfakt)
        return mousepos
    
    def createlinetool(self, checked):
        self.createlineactive = checked
        self.clickcount=0
        lseg.tool_active(checked)


    # def resizeEvent(self, event):
        # print("resize")
        # if self.scene:
            # self.scene.updateMvp(self.zfakt)

        
    def wheelEvent(self, event):
        self.zoomy +=event.angleDelta().y()/120
        self.zfakt=pow(1.4, self.zoomy)
        self.scene.zom(self.zfakt)

        # self.scene.updateMvp(self.zfakt)

        self.update()
        self.render()
        

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            pan_tool.start_drag(self.mycoord())
            self.scene.pan(pan_tool.value)
        
        if event.button() == Qt.MouseButton.LeftButton:
            # self.scene.chcol( random.uniform(1, 1))



            if self.createlineactive:
                lseg.create_points(self.mycoord(), self.clickcount, self.size(), pan_tool.value, self.zfakt)
                self.clickcount+=1
                lseg.point_add(self.clickcount)
            else:
                checkclickedpoint( *normalized_coordinates(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt) )

                # stulbs workarounds lai izslegtu selekcibju bez peles  kustinasanas
                checkpoint( *normalized_coordinates(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt) )
                # Store the initial mouse position for drag calculation
                global uds
                self.user_drag_start = self.mycoord()
                uds = self.user_drag_start
       
        self.update()

    def mouseMoveEvent(self, event):
        pan_tool.dragging(self.mycoord())
        self.scene.pan(pan_tool.value)

        

        if self.user_drag_start:
            # Check for ongoing drag operation
            drag_distance = points_to_distance(self.mycoord(), self.user_drag_start)
            # print(drag_distance)
            if drag_distance > self.startDragDistance:
                # Drag has started
                print("Drag Started")
                # Reset the drag start position
                check_dr_point( *normalized_coordinates(self.user_drag_start, (self.size().width(), self.size().height()), self.zfakt) )
                global uds
                self.user_drag_start = None
                uds = self.user_drag_start 

        if self.createlineactive:
            

            lseg.update_points(self.mycoord(), self.clickcount, self.size(), pan_tool.value, self.zfakt)
        else:
            checkpoint( *normalized_coordinates(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt) )
            linedrag( *normalized_coordinates(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt) )
            

        self.update()
        self.render()

    def mouseReleaseEvent(self, event):
        pan_tool.stop_drag(self.mycoord())
        self.scene.pan(pan_tool.value)

        linestopdrag( *normalized_coordinates(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt) )

        global uds
        self.user_drag_start = None
        uds = self.user_drag_start 

        self.update()




            

