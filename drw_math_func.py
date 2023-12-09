import numpy as np
import math
from drw_classes import Point

def distance2points(p1, p2):
    point1 = np.array(p1.xy)
    point2 = np.array(p2.xy)
    vector = point2 - point1
    # Calculate the Euclidean distance between the two points

    return math.dist(p2.xy, p1.xy)
    # return np.linalg.norm(vector)


def angle2points(p1, p2):
    # point1 = np.array(p1.xy)
    # point2 = np.array(p2.xy)
    # vector = point2 - point1
    # # Calculate the angle in radians
    # angle_rad = np.arctan2(vector[1], vector[0])
    # # Convert the angle to degrees if needed
    # angle_deg = np.degrees(angle_rad)
    # # Ensure the angle is in the range [0, 360) degrees
    # return (angle_deg + 360) % 360

    vector = p2-p1
    rad = math.atan2(vector.y, vector.x)

    return math.degrees(rad)%360

def point_on_line(mouse_pt, a_pt, b_pt, precision=0.035, endpoint_threshold=0.05):
    # Check if the mouse point is on the line segment defined by a_pt and b_pt

    # Check if the mouse point is close to one of the endpoints
    # dist_to_a = np.linalg.norm((a_pt - mouse_pt).xy)
    # dist_to_b = np.linalg.norm((b_pt - mouse_pt).xy)

    dist_to_a = math.dist(a_pt.xy, mouse_pt.xy)
    dist_to_b = math.dist(b_pt.xy, mouse_pt.xy)


    if dist_to_a < endpoint_threshold:
        return True, 0  # Mouse point is close to the first endpoint

    if dist_to_b < endpoint_threshold:
        return True, 1  # Mouse point is close to the second endpoint

    # Vectors from line start to mouse point and along the line segment
    # ap = np.array((mouse_pt - a_pt).xy)
    # ab = np.array((b_pt - a_pt).xy)
    ap = mouse_pt - a_pt
    ab = b_pt - a_pt
    # Dot products
    # dot_ap_ab = np.dot(ap, ab)
    # dot_ab_ab = np.dot(ab, ab)
    dot_ap_ab = ap.dot2d(ab)
    dot_ab_ab = ab.dot2d(ab)

    # Check if the mouse point is close enough to the line segment
    if 0 <= dot_ap_ab <= dot_ab_ab and abs(ap.cross2d(ab)) < precision:
        return True, 2  # Mouse point is on the line segment
    
    
    return False, None # Mouse point is not on the line segment
