import numpy as np

n = 100
V = np.zeros((n,4), dtype=[('p0', np.float32, 2),
                           ('p1', np.float32, 2),
                           ('uv', np.float32, 2),
                           ('thickness', np.float32, 1)])
V["p0"] = np.dstack((np.linspace(100,1100,n),np.ones(n)* 50)).reshape(n,1,2)
V["p1"] = np.dstack((np.linspace(110,1110,n),np.ones(n)*350)).reshape(n,1,2)
V["uv"] = (0,0), (0,1), (1,0), (1,1)
V["thickness"] = np.linspace(0.1, 8.0, n).reshape(n,1)

print(V[-1])