import math

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
    
    def __truediv__(self, scalar):
        return Point(self.x / scalar, self.y / scalar)
    
    # 2d dot product - skalarais reizinajums
    def dot2d(self, other_point):
        return self.x*other_point.x + self.y*other_point.y
    
    # 2d cross product - vektorialais reizinajums
    def cross2d(self, other_point):
        return self.x*other_point.y - self.y*other_point.x

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)