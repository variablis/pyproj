from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt, QTimer

from pathlib import Path

from dw_qtmoderngl import ModernGLWidget
from dc_renderer import Renderer, PanTool
from dc_point import Point
from dc_linedata import LineData, SceneData
from dc_text import TextData
from df_math import *
from dc_linesegment import LineSegment, line_drag, line_stop_drag, check_drag_point, check_clicked_point, check_point


# absolute path needed for pyinstaller
bundle_dir = Path(__file__).parent
path_to_img = Path.cwd() / bundle_dir / "img"


pan_tool = PanTool()
lseg = LineSegment()



class MyWidget(ModernGLWidget):
    '''
    main opengl widget
    '''
    def __init__(self):
        super(MyWidget, self).__init__()

        self.scene = None
        self.zoomw = 0
        self.zfac = 1

        self.uds=None

        self.createlineactive=False
        self.clickcount=0
        self.user_drag_start=None
        self.startDragDistance=0.001


    def init(self):
        self.ctx.viewport = (0, 0, 512, 512)
        self.scene = Renderer(self.ctx)


    def render(self):
        self.ctx.viewport = (0, 0, self.size().width(), self.size().height())
        self.screen.use()
        self.scene.clear()

        self.scene.update_mvp(self.zfac)
        self.scene.line_render(LineData.makeBuffer())
        self.scene.text_render(TextData.makeBuffer())


    def mouse_pt(self):
        '''
        convert mouse position from pixels to normalized coordinates relative to the screen size
        '''
        # origin is main window left upper corner 0,0
        # mouse position ir read from whole display
        local_pos = self.mapFromGlobal(QCursor.pos())
 
        # convert mouse pixel coordinates to normalized coordinates with the origin at the center
        # shif center to 0,0
        mouse_pos = Point(
            2*((local_pos.x() - self.size().width() /2) /512 /self.zfac),
            -2*((local_pos.y() - self.size().height() /2) /512 /self.zfac) # Negate y to match the coordinate system
            )

        # print(mouse_pos.xy)
        return mouse_pos
    

    def mouse_pt_paned(self, mouse_pt):
        '''
        add paned value to mouse position
        '''
        x_paned = mouse_pt.x + pan_tool.value[0]
        y_paned = mouse_pt.y + pan_tool.value[1]
        return Point(x_paned, y_paned)
    

    def createlinetool(self, checked):
        self.createlineactive = checked
        self.clickcount=0
        lseg.tool_active(checked)


    # clear focus of QLineEdit
    def clear_input_focus(self):
        # mywidget -> qsplitter -> mainwindow
        self.parent().parent().input_gridsize.clearFocus()
        
        
    def wheelEvent(self, event):
        self.zoomw += event.angleDelta().y()/120
        self.zfac = pow(1.4, self.zoomw)

        SceneData.zoom_factor = self.zfac
        TextData.rebuildAll(True)

        self.update()
        # self.render()
        

    def mousePressEvent(self, event):
        self.clear_input_focus()
        
        if event.button() == Qt.MouseButton.MiddleButton:
            pan_tool.start_drag(self.mouse_pt())
        
        if event.button() == Qt.MouseButton.LeftButton:

            mpn = self.mouse_pt_paned(self.mouse_pt())

            if self.createlineactive:
                lseg.create_points(mpn, self.clickcount)
                self.clickcount+=1
                lseg.point_add(self.clickcount)
            else:
                check_clicked_point(mpn)

                # stulbs workarounds lai izslegtu selekcibju bez peles  kustinasanas
                check_point(mpn)
                # Store the initial mouse position for drag calculation

                self.user_drag_start = self.mouse_pt()
                self.uds = self.user_drag_start
       
        self.update()


    def mouseMoveEvent(self, event):
        pan_tool.dragging(self.mouse_pt())

        mpn = self.mouse_pt_paned(self.mouse_pt())

        if self.user_drag_start:
            # Check for ongoing drag operation
            drag_distance = points_to_distance(self.mouse_pt(), self.user_drag_start)
            # print(drag_distance)
            if drag_distance > self.startDragDistance:
                # Drag has started
                # print("Drag Started")
                # Reset the drag start position
                check_drag_point( self.mouse_pt_paned(self.user_drag_start) )
 
                self.user_drag_start = None
                self.uds = self.user_drag_start 

        if self.createlineactive:
            lseg.update_points(mpn, self.clickcount)
        else:
            check_point(mpn)
            line_drag(mpn)

        self.update()
        self.render()


    def mouseReleaseEvent(self, event):
        pan_tool.stop_drag(self.mouse_pt())

        mpn = self.mouse_pt_paned(self.mouse_pt())
        line_stop_drag(mpn)

        self.user_drag_start = None
        self.uds = self.user_drag_start 

        self.update()

