from dc_linedata import LineData, SceneData
from dc_text import TextData

from df_math import *


class LineSegment:
    '''
    line segment class definition
    '''
    def __init__(self):
        pass


    def start_line(self, mouse_pt):
        '''
        start new line, starting new line segment
        '''
        LineData.add_startpoint(mouse_pt)

        distance = LineData.get_last_elem().distance *SceneData.units
        angle = LineData.get_last_elem().angle
        text = f'{round(distance,4):.2f} {round(angle,2):.2f}°'
        TextData.add(text, LineData.get_last_elem().points, LineData.get_last_elem().line_id)


    def end_line(self, mouse_pt):
        '''
        line segment complete - end line
        '''
        LineData.add_endpoint(mouse_pt)
        # print('segment done')


    def update_line(self, mouse_pt):
        '''
        update line data
        '''
        LineData.live_point(mouse_pt)

        distance = LineData.get_last_elem().distance *SceneData.units
        angle = LineData.get_last_elem().angle

        text = f'{round(distance,4):.2f} {round(angle,2):.2f}°'
        TextData.update(text, LineData.get_last_elem().points, LineData.get_last_elem().line_id)


    def check_point(self, mouse_pt):
        '''
        checks all lines against mouse point to detect if mouse hovers any of them
        '''
        for line in LineData.get_all_lines():
            a_pt = line.points[0]
            b_pt = line.points[1]

            test, _ = point_on_line(mouse_pt, a_pt, b_pt)

            if test == True:
                line.hovered = True

                if line.selected:
                    # line.color = [1,1,0,1]
                    pass
                else:
                    line.color = [1,0,1,1]
            else:
                line.hovered = False

                if line.selected:
                    # line.color = [1,1,0,1]
                    pass
                else:
                    line.color = [1,1,1,1]


    def check_clicked_point(self, mouse_pt):
        '''
        checks all lines against mouse point to detect if user has clicked on any of them
        '''
        for line in LineData.get_all_lines():
            a_pt = line.points[0]
            b_pt = line.points[1]

            test, _ = point_on_line(mouse_pt, a_pt, b_pt)
            
            if test == True:
                line.selected = True
                line.color = [0,1,.3,1]
            else:
                line.selected = False


    def check_drag_point(self, mouse_pt):
        '''
        checks all lines against mouse point to detect if user drags any of them
        '''
        for line in LineData.get_all_lines():
            a_pt = line.points[0]
            b_pt = line.points[1]

            test, dragtype = point_on_line(mouse_pt, a_pt, b_pt)

            if test == True:
                line.drag = True
                line.mousepos = line.prev_mousepos = mouse_pt
                line.dragtype = dragtype
            else:
                line.dragtype = None


    def line_drag(self, mouse_pt):
        '''
        checks all lines for drag and dragtype attribute, if any is draggable, update its position
        '''
        for line in LineData.get_all_lines():
            if line.drag:
                line.mousepos = mouse_pt
                line.update_point_data(line.dragtype)

                distance = line.distance *SceneData.units
                angle = line.angle
                text = f"{round(distance,4):.2f} {round(angle,2):.2f}°"
                TextData.update( text, line.points, line.line_id)


    def line_stop_drag(self, mouse_pt):
        '''
        drag ends. resetset all draggable line drag attribute
        '''
        for line in LineData.get_all_lines():
            if line.drag:
                line.drag = False
                line.mousepos = mouse_pt
                # print("drag end")

