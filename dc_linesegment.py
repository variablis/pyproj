from dc_linedata import LineData, SceneData
from dc_text import TextData

from df_math import point_on_line


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
        line = LineData.get_last_elem()
        TextData.add(line)


    def end_line(self, mouse_pt):
        '''
        line segment complete - end line
        '''
        LineData.add_endpoint(mouse_pt)
        line = LineData.get_last_elem()
        TextData.update(line)

        # print('segment done')


    def update_live_point(self, mouse_pt):
        '''
        update live endpoint line creation tool is active 
        '''
        line = LineData.get_last_elem()
        line.mousepos = mouse_pt
        line.update_point_data(1)
        TextData.update(line)


    def check_point(self, mouse_pt):
        '''
        checks all lines against mouse point to detect if mouse hovers any of them
        '''
        for line in LineData.get_all_lines():
            a_pt = line.points[0]
            b_pt = line.points[1]

            test, _ = point_on_line(mouse_pt, a_pt, b_pt, 0.035 /SceneData.zoom_factor, 0.05 /SceneData.zoom_factor)

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
        val = None
        for line in LineData.get_all_lines():
            a_pt = line.points[0]
            b_pt = line.points[1]

            test, _ = point_on_line(mouse_pt, a_pt, b_pt, 0.035 /SceneData.zoom_factor, 0.05 /SceneData.zoom_factor)
            
            if test == True:
                line.selected = True
                line.color = [0,1,.3,1]
                # print(line)
                val= line # for constraint test

            else:
                line.selected = False
        
        return val


    def check_drag_point(self, mouse_pt):
        '''
        checks all lines against mouse point to detect if user drags any of them
        '''
        for line in LineData.get_all_lines():
            a_pt = line.points[0]
            b_pt = line.points[1]

            test, dragtype = point_on_line(mouse_pt, a_pt, b_pt, 0.035 /SceneData.zoom_factor, 0.05 /SceneData.zoom_factor)

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
                TextData.update(line)


    def line_stop_drag(self, mouse_pt):
        '''
        drag ends. resetset all draggable line drag attribute
        '''
        for line in LineData.get_all_lines():
            if line.drag:
                line.drag = False
                line.mousepos = mouse_pt
                # print("drag end")

