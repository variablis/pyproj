import numpy as np

# n = 100
# V = np.zeros((n,4), dtype=[('p0', np.float32, 2),
#                            ('p1', np.float32, 2),
#                            ('uv', np.float32, 2),
#                            ('thickness', np.float32, 1)])
# V["p0"] = np.dstack((np.linspace(100,1100,n),np.ones(n)* 50)).reshape(n,1,2)
# V["p1"] = np.dstack((np.linspace(110,1110,n),np.ones(n)*350)).reshape(n,1,2)
# V["uv"] = (0,0), (0,1), (1,0), (1,1)
# V["thickness"] = np.linspace(0.1, 8.0, n).reshape(n,1)

# V.ravel()

# print(V[-1])
# print(V.ravel())


# I = np.zeros((n,6), dtype=np.uint32)
# I[:] = [0,1,2,1,2,3]
# I += 4*np.arange(n,dtype=np.uint32).reshape(n,1)


# print(I)



# import math
# import numpy as np
# import timeit

# point1 = (1, 2, 3)
# point2 = (4, 5, 6)

# # Using math.dist
# def using_math_dist():
#     return math.dist(point1, point2)

# # Using np.linalg.norm
# def using_np_linalg_norm():
#     return np.linalg.norm(np.array(point1) - np.array(point2))

# # Timing both functions
# math_dist_time = timeit.timeit(using_math_dist, number=1000000)
# np_linalg_norm_time = timeit.timeit(using_np_linalg_norm, number=1000000)

# print(f"math.dist time: {math_dist_time:.6f} seconds")
# print(f"np.linalg.norm time: {np_linalg_norm_time:.6f} seconds")




import numpy as np
import timeit
import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xy = [x,y]

    def __sub__(self, other_point):
        """Overloaded subtraction operator for Point instances."""
        return Point(self.x - other_point.x, self.y - other_point.y)
    
    def __add__(self, other_point):
        """Overloaded addition operator for Point instances."""
        return Point(self.x + other_point.x, self.y + other_point.y)
    
    def dot2d(self, other_point):
        return self.x*other_point.x + self.y*other_point.y
    
    def cross2d(self, other_point):
        return self.x*other_point.y - self.y*other_point.x


    def get(self):
        return [self.x, self.y]
    



def point_on_line(mouse_pt, a_pt, b_pt, precision=0.035, endpoint_threshold=0.05):
    # Check if the mouse point is on the line segment defined by a_pt and b_pt


    # print(a_pt.xy)
    # Check if the mouse point is close to one of the endpoints
    dist_to_a = math.dist(a_pt.xy, mouse_pt.xy)
    dist_to_b = math.dist(b_pt.xy, mouse_pt.xy)

    if dist_to_a < endpoint_threshold:
        return True, 0  # Mouse point is close to the first endpoint

    if dist_to_b < endpoint_threshold:
        return True, 1  # Mouse point is close to the second endpoint

    # Vectors from line start to mouse point and along the line segment
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
    
    return False, None  # Mouse point is not on the line segment




def linalg(mouse_pt, a_pt, b_pt, precision=0.035, endpoint_threshold=0.05):
    ap = np.array((mouse_pt - a_pt).xy)
    ab = np.array((b_pt - a_pt).xy)
    dist_to_a = np.linalg.norm((a_pt - mouse_pt).xy)
    dist_to_b = np.linalg.norm((b_pt - mouse_pt).xy)
    
    if dist_to_a < endpoint_threshold:
        return True, 0  # Mouse point is close to the first endpoint

    if dist_to_b < endpoint_threshold:
        return True, 1  # Mouse point is close to the second endpoint
    
    dot_ap_ab = np.dot(ap, ab)
    dot_ab_ab = np.dot(ab, ab)

    if 0 <= dot_ap_ab <= dot_ab_ab and abs(np.cross(ap, ab)) < precision:
        return True, 2  # Mouse point is on the line segment

    return False, None  # Mouse point is not on the line segment



def third(xp3, xp1, xp2):
    p1=np.array([xp1.x,xp1.y])
    p2=np.array([xp2.x,xp2.y])
    p3=np.array([xp3.x,xp3.y])

    # return np.linalg.norm(np.cross((p2-p1).xy, (p1-p3).xy))/np.linalg.norm((p2-p1).xy)
    np.cross(p2-p1,p1-p3)/np.linalg.norm(p2-p1)


# Generate some test data
np.random.seed(42)
# mouse_pt = Point(np.random.rand(), np.random.rand())

# Benchmarking
num_iterations = 5

vals=np.random.random((1000, 6))
# print(vals)

def using_pol():
    # # mouse_pt = Point(np.random.rand(), np.random.rand())
    # a_pt = Point(np.random.rand(), np.random.rand())
    # b_pt = Point(np.random.rand(), np.random.rand())
    # point_on_line(mouse_pt, a_pt, b_pt)

    for i in vals:
        mouse_pt = Point(i[0], i[1])
        a_pt = Point(i[2], i[3])
        b_pt = Point(i[4], i[5])

        point_on_line(mouse_pt, a_pt, b_pt)

def using_linalg():
    # mouse_pt = Point(np.random.rand(), np.random.rand())
    # a_pt = Point(np.random.rand(), np.random.rand())
    # b_pt = Point(np.random.rand(), np.random.rand())
    # linalg(mouse_pt, a_pt, b_pt)

    for i in vals:
        mouse_pt = Point(i[0], i[1])
        a_pt = Point(i[2], i[3])
        b_pt = Point(i[4], i[5])

        linalg(mouse_pt, a_pt, b_pt)

def using_tr():
    # mouse_pt = Point(np.random.rand(), np.random.rand())
    # a_pt = Point(np.random.rand(), np.random.rand())
    # b_pt = Point(np.random.rand(), np.random.rand())
    # third(mouse_pt, a_pt, b_pt)

    for i in vals:
        mouse_pt = Point(i[0], i[1])
        a_pt = Point(i[2], i[3])
        b_pt = Point(i[4], i[5])

        third(mouse_pt, a_pt, b_pt)



point_on_line_time = timeit.timeit(using_pol, number=num_iterations)
linalg_time = timeit.timeit(using_linalg, number=num_iterations)
t3_time = timeit.timeit(using_tr, number=num_iterations)

print(f"point_on_line time: {point_on_line_time:.6f} seconds")
print(f"linalg time: {linalg_time:.6f} seconds")
print(f"tr time: {t3_time:.6f} seconds")
