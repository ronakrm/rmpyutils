import numpy as np
import ot

from rmpyutils.plt import SingleHist

np.random.seed(3450)
n = 1000
n_bins = 100
d = n_bins


m_1 = 0.2
m_2 = 0.7
s_1 = 0.3
s_2 = 0.1

ot1 = ot.datasets.make_1D_gauss(n_bins, m_1 * n_bins, s_1 * n_bins)
ot2 = ot.datasets.make_1D_gauss(n_bins, m_2 * n_bins, s_2 * n_bins)

# combine them as a single dist by just averaging
A = (ot1 + ot2) / 2 + (np.random.rand(n_bins) - 1) / 200
A = A - min(A)
A = A / sum(A)
S = np.zeros(n_bins)
S[86] = max(A)


SingleHist(A, S)
