import math
from dc_point import Point


def points_to_distance(p1: Point, p2: Point):
    '''
    calculate the Euclidean distance between the two points
    '''
    return math.dist(p2.xy, p1.xy)


def points_to_angle(p1: Point, p2: Point):
    '''
    calculate angle in degrees between the two points
    '''
    vector = p2-p1
    rad = math.atan2(vector.y, vector.x)
    return math.degrees(rad)%360


def point_on_line(mouse_pt: Point, a_pt: Point, b_pt: Point, precision=0.035, endpoint_threshold=0.05):
    '''
    check if the mouse point is on the line segment defined by a_pt and b_pt
    '''
        
    # Check if the mouse point is close to one of the endpoints
    dist_to_a = math.dist(a_pt.xy, mouse_pt.xy)
    dist_to_b = math.dist(b_pt.xy, mouse_pt.xy)

    # Mouse point is close to the first endpoint
    if dist_to_a < endpoint_threshold:
        return True, 0  

    # Mouse point is close to the second endpoint
    if dist_to_b < endpoint_threshold:
        return True, 1  

    # Vectors from line start to mouse point and along the line segment
    ap = mouse_pt - a_pt
    ab = b_pt - a_pt

    # Dot products
    dot_ap_ab = ap.dot2d(ab)
    dot_ab_ab = ab.dot2d(ab)

    # Check if the mouse point is close enough to the line segment
    if 0 <= dot_ap_ab <= dot_ab_ab and abs(ap.cross2d(ab)) < precision:
        # Mouse point is on the line segment
        return True, 2  
    
    # Mouse point is not on the line segment
    return False, None



def clamp(n, min, max):
    '''
    clamp value to min max range
    '''

    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n