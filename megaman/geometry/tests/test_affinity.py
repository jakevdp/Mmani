# <<<<<<< HEAD
from __future__ import division ## removes integer division

import os
import numpy as np
from scipy import sparse
from numpy.testing import assert_array_equal
from scipy.spatial.distance import pdist, squareform
from megaman.geometry.distance import compute_adjacency_matrix
from megaman.geometry.affinity import compute_affinity_matrix

random_state = np.random.RandomState(36)
n_sample = 10
d = 2
X = random_state.randn(n_sample, d)
D = squareform(pdist(X))
D[D > 1/d] = 0
# =======
import os

import numpy as np
from numpy.testing import assert_allclose, assert_equal

from scipy.spatial.distance import cdist
from scipy.sparse import csr_matrix
from scipy import io

from megaman.geometry.adjacency_new import compute_adjacency_matrix
from megaman.geometry.affinity_new import compute_affinity_matrix, Affinity

# >>>>>>> distance_refactor

TEST_DATA = os.path.join(os.path.dirname(__file__),
                        'testmegaman_laplacian_rad0_2_lam1_5_n200.mat')

# <<<<<<< HEAD
def test_affinity_sparse_vs_dense():
    """
    Test that A_sparse is the same as A_dense for a small A matrix
    """
    rad = 2.
    n_samples = 6
    X = np.arange(n_samples)
    X = X[ :,np.newaxis]
    X = np.concatenate((X,np.zeros((n_samples,1),dtype=float)),axis=1)
    X = np.asarray( X, order="C" )
    test_dist_matrix = compute_adjacency_matrix( X, method = 'auto', radius = rad )
    A_dense = compute_affinity_matrix(test_dist_matrix.toarray(), method = 'auto',
                                      radius = rad, symmetrize = False )
    A_sparse = compute_affinity_matrix(sparse.csr_matrix(test_dist_matrix),
                                       method = 'auto', radius = rad, symmetrize = False)
    A_spdense = A_sparse.toarray()
    A_spdense[ A_spdense == 0 ] = 1.
    assert_array_equal( A_dense, A_spdense )
# =======

def test_affinity_vs_matlab():
    """Test that the affinity calculation matches the matlab result"""
    matlab = io.loadmat(TEST_DATA)

    D = np.sqrt(matlab['S'])  # matlab outputs squared distances
    A_matlab = matlab['A']
    radius = matlab['rad'][0]

    # check dense affinity computation
    A_dense = compute_affinity_matrix(D, radius=radius)
    assert_allclose(A_dense, A_matlab)

    # check sparse affinity computation
    A_sparse = compute_affinity_matrix(csr_matrix(D), radius=radius)
    assert_allclose(A_sparse.toarray(), A_matlab)


def test_affinity():
    rand = np.random.RandomState(42)
    X = np.random.rand(20, 3)
    D = cdist(X, X)

    def check_affinity(adjacency_radius, affinity_radius, symmetrize):
        adj = compute_adjacency_matrix(X, radius=adjacency_radius)
        aff = compute_affinity_matrix(adj, radius=affinity_radius,
                                      symmetrize=True)

        A = np.exp(-(D / affinity_radius) ** 2)
        A[D > adjacency_radius] = 0
        assert_allclose(aff.toarray(), A)

    for adjacency_radius in [0.5, 1.0, 5.0]:
        for affinity_radius in [0.1, 0.5, 1.0]:
            for symmetrize in [True, False]:
                yield (check_affinity, adjacency_radius,
                       affinity_radius, symmetrize)


def test_custom_affinity():
    class CustomAffinity(Affinity):
        name = "custom"
        def affinity_matrix(self, adjacency_matrix):
            return np.exp(-abs(adjacency_matrix.toarray()))

    rand = np.random.RandomState(42)
    X = rand.rand(10, 2)
    D = compute_adjacency_matrix(X, radius=10)
    A = compute_affinity_matrix(D, method='custom', radius=1)
    assert_allclose(A, np.exp(-abs(D.toarray())))

    Affinity._remove_from_registry("custom")
# >>>>>>> distance_refactor