
import numpy as np
import timeit

# Your nested array
# data = np.array([[1, 1, 2, 3], [1, 1, 2, 3], [1, 2, 3, 4]])
# data2=[[1, 1, 2, 3], [1, 1, 2, 3], [1, 2, 3, 4]]

vals=np.random.random((1000, 4))

data=vals
data2=vals.tolist()


np.random.seed(42)
value_to_add =  np.random.randint(6)

# Benchmarking
num_iterations = 1

# print(data.shape)

# NumPy approach
def numpy_approach():
    # value_to_add =  np.random.randint(6)
    data[:, :2] += value_to_add
    # print(data)

# Native Python approach
# Native Python approach
def python_approach():
    global data2
    # value_to_add =  np.random.randint(6)
    da =[[x[0]+ value_to_add, x[1] + value_to_add]+x[2:]  for x in data2]
    data2=da
    # print(data2)

# Measure the time taken by each approach
numpy_time = timeit.timeit(numpy_approach, number=num_iterations)
python_time = timeit.timeit(python_approach, number=num_iterations)

print(f"NumPy Time: {numpy_time}")
print(f"Native Python Time: {python_time}")