import matplotlib.pyplot as plt
import numpy as np
from disk import Disk


def visualize_2d_array_print(array):
    """
    Visualizes a 2D array with mixed data types by printing it in a readable format.

    Parameters:
    - array: A 2D list (or numpy array) containing mixed data types.
    """
    # Find the maximum width needed for each column
    max_width = max(len(str(item)) for row in array for item in row)

    for row in array:
        print(' '.join(f'{str(elem):{max_width}}' for elem in row))
# Example usage:
array = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],

]
d = Disk(100, 7)
visualize_2d_array_print(d.disk)
