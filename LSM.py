import numpy as np
from matrix import Matrix

def LSM(arr):
    n, m = arr.shape
    m -= 1

    M = Matrix(n, m + 1)
    N = Matrix(m, m + 1)

    M.data = arr

    f = M[:, m]

    for i in range(m):
        e_i = M[:, i]
        N[i, m] = np.dot(f, e_i)
        for j in range(m):
            e_j = M[:, j]
            N[i, j] = np.dot(e_i, e_j)

    N.diag()
    return N.solution()