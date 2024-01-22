
class Point:
    '''
    point class definition
    '''
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xy = [x,y]

    def __sub__(self, other_point):
        '''
        overloaded subtraction operator for Point instances.
        '''
        return Point(self.x - other_point.x, self.y - other_point.y)
    
    def __add__(self, other_point):
        '''
        overloaded addition operator for Point instances.
        '''
        return Point(self.x + other_point.x, self.y + other_point.y)
    
    def dot2d(self, other_point):
        '''
        2d dot product - skalarais reizinajums
        '''
        return self.x*other_point.x + self.y*other_point.y
    
    def cross2d(self, other_point):
        '''
        2d cross product - vektorialais reizinajums
        '''
        return self.x*other_point.y - self.y*other_point.x
