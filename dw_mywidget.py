from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt

from pathlib import Path

from dw_qtmoderngl import ModernGLWidget
from dc_renderer import Renderer, PanTool
from dc_point import Point
from dc_linedata import LineData, SceneData
from dc_text import TextData
from df_math import points_to_distance
from dc_linesegment import LineSegment


# absolute path needed for pyinstaller
bundle_dir = Path(__file__).parent
path_to_img = Path.cwd() / bundle_dir / "img"


pan_tool = PanTool()
segment = LineSegment()


class MyWidget(ModernGLWidget):
    '''
    main opengl widget
    '''
    def __init__(self):
        super(MyWidget, self).__init__()

        self.scene = None
        self.zoom_wheel = 0
        self.zfact = 1

        self.line_tool_active = False
        self.clickcount = 0

        self.user_drag_start = None
        self.start_drag_threshold = 0.001

        self.mp = None # mouse point
        self.mpp = None # mouse point + pan


    def init(self):
        self.ctx.viewport = (0, 0, 512, 512)
        self.scene = Renderer(self.ctx)


    def render(self):
        self.mp = self.mouse_pt()
        self.mpp = self.mouse_pt_paned(self.mp)

        self.ctx.viewport = (0, 0, self.size().width(), self.size().height())
        self.screen.use()
        self.scene.clear()

        self.scene.update_mvp(self.zfact, pan_tool.value)
        self.scene.line_render(LineData.make_buffer())
        self.scene.text_render(TextData.make_buffer())


    def mouse_pt(self):
        '''
        convert mouse position from pixels to normalized coordinates relative to the screen size
        '''
        # origin is main window left upper corner 0,0. mouse position ir read from whole display
        local_pos = self.mapFromGlobal(QCursor.pos())
        # convert mouse pixel coordinates to normalized coordinates with the origin at the center, shift center to 0,0
        mouse_pos = Point(
            2*((local_pos.x() - self.size().width() /2) /512 /self.zfact),
            -2*((local_pos.y() - self.size().height() /2) /512 /self.zfact) # Negate y to match the coordinate system
            )
        return mouse_pos
    

    def mouse_pt_paned(self, mouse_pt):
        '''
        add paned value to mouse position
        '''
        x_paned = mouse_pt.x + pan_tool.value.x
        y_paned = mouse_pt.y + pan_tool.value.y
        return Point(x_paned, y_paned)
    

    def create_line_tool(self, checked):
        '''
        sets line creation tool status and resets click count
        '''
        self.line_tool_active = checked
        self.clickcount = 0


    def clear_input_focus(self):
        '''
        clear focus of input fields
        '''
        # mywidget -> qsplitter -> mainwindow
        self.parent().parent().input_gridsize.clearFocus()
        self.parent().parent().input_units.clearFocus()
        
        
    def wheelEvent(self, event):
        self.zoom_wheel += event.angleDelta().y()/120
        self.zfact = pow(1.4, self.zoom_wheel)

        self.start_drag_threshold /= self.zfact
        SceneData.zoom_factor = self.zfact
        TextData.rebuild_all(True)

        self.update()
        

    def mousePressEvent(self, event):
        self.clear_input_focus()
        
        if event.button() == Qt.MouseButton.MiddleButton:
            pan_tool.start_drag(self.mp)
        
        if event.button() == Qt.MouseButton.LeftButton:

            if self.line_tool_active:
                if not self.clickcount %2: #clicks in tool are even
                    segment.start_line(self.mpp)

                self.clickcount += 1

                if not self.clickcount %2: #clicks in tool are even
                    segment.end_line(self.mpp)
            else:
                segment.check_clicked_point(self.mpp)
                segment.check_point(self.mpp)

                # Store the initial mouse position for drag calculation
                self.user_drag_start = self.mp
       
        self.update()


    def mouseMoveEvent(self, event):
        pan_tool.dragging(self.mp)

        if self.user_drag_start:
            drag_distance = points_to_distance(self.mp, self.user_drag_start)
            if drag_distance > self.start_drag_threshold:
                # drag has started
                # print("Drag Started")

                segment.check_drag_point( self.mouse_pt_paned(self.user_drag_start) )

                # Reset the drag start position
                self.user_drag_start = None

        if self.line_tool_active:
            if self.clickcount %2: # 3 %2 = 1 = True
                segment.update_live_point(self.mpp)

        else:
            segment.check_point(self.mpp)
            segment.line_drag(self.mpp)

        self.update()


    def mouseReleaseEvent(self, event):
        self.user_drag_start = None
        
        pan_tool.stop_drag(self.mp)
        segment.line_stop_drag(self.mpp)

        self.update()

