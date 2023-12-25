
import timeit
import random

class LineData:
    lines = []

    def __init__(self, line_id):
        self.line_id = line_id

    @classmethod
    def initialize_lines(cls, num_lines):
        cls.lines = [LineData(line_id) for line_id in range(num_lines)]

    @classmethod
    def linear_search(cls, target_id):
        for elem in cls.lines:
            if elem.line_id == target_id:
                return elem
        return None

    @classmethod
    def next_search(cls, target_id):
        return next((x for x in cls.lines if x.line_id == target_id), None)
    
target_id = random.randint(0, 9999)

def benchmark_linear_search():
    setup_code = """
import random
from __main__ import LineData
LineData.initialize_lines(10000)  # or provide your own number of lines

"""
    stmt = f"LineData.linear_search({target_id})"
    execution_time = timeit.timeit(stmt, setup=setup_code, number=1000)
    print(f"Linear Search - Execution time: {execution_time:.6f} seconds")

def benchmark_next_search():
    setup_code = """
import random
from __main__ import LineData
LineData.initialize_lines(10000)  # or provide your own number of lines

"""
    stmt = f"LineData.next_search({target_id})"
    execution_time = timeit.timeit(stmt, setup=setup_code, number=1000)
    print(f"Next Search - Execution time: {execution_time:.6f} seconds")

if __name__ == "__main__":
    benchmark_linear_search()
    benchmark_next_search()
