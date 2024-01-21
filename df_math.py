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
    return math.degrees(rad) %360


def points_to_angle_abs(p1: Point, p2: Point):
    '''
    calculate absolute angle in degrees between the two points
    '''
    vector = p2-p1
    angle = math.degrees(math.atan2(vector.y, vector.x)) % 360
    complementary_angle = (angle + 180) % 360

    return min(angle, complementary_angle)


def point_on_line(mouse_pt: Point, a_pt: Point, b_pt: Point, precision=0.035, endpoint_threshold=0.05):
    '''
    checks if the mouse point lies approximately on the line segment defined by points a_pt and b_pt.

    Parameters:
    - mouse_pt (Point): The point to be checked.
    - a_pt (Point): The starting point of the line segment.
    - b_pt (Point): The ending point of the line segment.
    - precision (float): The maximum allowed perpendicular distance from the line.
    - endpoint_threshold (float): The maximum allowed distance from either endpoint for consideration.

    Returns:
    - bool: True if the mouse point is on the line segment within the specified precision.
    - int: which point is closest
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
    Clamp a value to be within the specified minimum and maximum range.
    '''

    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n