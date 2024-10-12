import numpy as np

class Matrix:

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.data = np.zeros(shape=(rows, cols))

    def __str__(self):
        s = ''
        for row in self.data:
            s += ' '.join(map(lambda x: str(np.round(x, 2)).ljust(5), row)) + '\n'
        return s        
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value

    def input(self):
        for i in range(self.rows):
            s = input().split()
            for j in range(self.cols):
                self.data[i, j] = float(s[j])

    def P_ij(self, i, j):
        self.data[[i, j]] = self.data[[j, i]]

    def M_ij(self, i, j, c):
        self.data[i] += self.data[j] * c

    def diag(self):
        i = 0
        j = 0
        while i < self.rows and j < self.cols:
            if self.data[i, j] == 0:
                for k in range(i + 1, self.rows):
                    if self.data[k, j] != 0:
                        self.P_ij(i, k)
            
            if self.data[i, j] != 0:
                for k in range(self.rows):
                    if k != i:
                        self.M_ij(k, i, -self.data[k, j]/self.data[i, j])
            else:
                i -= 1
            i += 1
            j += 1   

    def solution(self):
        self.diag()

        res = []
        for i in range(self.rows):
            x_i = self.data[i, -1] / self.data[i, i]
            res.append(x_i)

        return res