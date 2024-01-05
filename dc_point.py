# point class definition
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xy = [x,y]

    # overloaded subtraction operator for Point instances.
    def __sub__(self, other_point):
        return Point(self.x - other_point.x, self.y - other_point.y)
    
    # overloaded addition operator for Point instances.
    def __add__(self, other_point):
        return Point(self.x + other_point.x, self.y + other_point.y)
    
    # 2d dot product - skalarais reizinajums
    def dot2d(self, other_point):
        return self.x*other_point.x + self.y*other_point.y
    
    # 2d cross product - vektorialais reizinajums
    def cross2d(self, other_point):
        return self.x*other_point.y - self.y*other_point.x

    def get(self):
        return [self.x, self.y]