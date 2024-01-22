import numpy as np


class SceneData:
    '''
    global scene data storage class
    '''
    # filename = 'untitled' TODO:
    units = 10
    grid = 1
    zoom_factor = 1.0
    # saved = False TODO:


class LineData:
    '''
    line data storage class
    '''
    g_index = 0 # global line index
    lines = []

    @classmethod
    def add_new_line(cls, line):
        '''
        add new line to array and increase global index
        '''
        cls.lines.append(line)
        cls.g_index += 1

    @classmethod
    def deselect_all(cls):
        '''
        clear all line selection attribute to false
        '''
        for elem in cls.lines:
            elem.color = [1,1,1,1]
            elem.selected = False
    
    @classmethod
    def get_all_lines(cls):
        '''
        return all lines in array
        '''
        return cls.lines
    
    @classmethod
    def get_last_line(cls):
        '''
        return last line from array
        '''
        if cls.lines:
            return cls.lines[-1]
    
    @classmethod
    def get_line_by_id(cls, id):
        '''
        return line by id
        '''
        for line in cls.lines:
            if line.line_id == id:
                return line
        return None

    @classmethod
    def get_selected_ids(cls):
        '''
        return array of line ids which have selected set to true
        '''
        tmp = [elem.line_id for elem in cls.lines if elem.selected]
        return tmp

    @classmethod
    def delete_selected(cls):
        '''
        delete lines that have selected attribute set to true, 
        by making new array, and removing from group
        '''
        tmp2 = [elem for elem in cls.lines if elem.selected]
        for elem in tmp2:
            elem.parent.root.delete_child(elem)
    
        tmp = [elem for elem in cls.lines if not elem.selected]
        cls.lines = tmp
    
    @classmethod
    def make_buffer(cls):
        '''
        return line points and color as numpy array for render buffer
        '''
        tmp_list = []
        for elem in cls.lines:
            tmp_list.append([ 
                elem.points[0].xy + elem.color,
                elem.points[1].xy + elem.color
            ])
        return np.array(tmp_list)

    @classmethod
    def add_line(cls, line):
        '''
        add line to array
        '''
        if cls.g_index < line.line_id:
            cls.g_index = line.line_id + 1

        cls.lines.append(line)

    @classmethod
    def print_data(cls):
        '''
        print all lines in array
        '''
        print(len(cls.lines))
        for elem in cls.lines:
            print(f"Line ID: {elem.line_id}, Point1: {elem.points[0].xy}, Point2: {elem.points[1].xy}, color: {elem.color}")
