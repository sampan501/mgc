"""A module containing convenient methods"""
from __future__ import print_function, division, unicode_literals, absolute_import

from builtins import zip, int, range
from future import standard_library
standard_library.install_aliases()
from past.utils import old_div
from builtins import object

import autograd.numpy as np
import time
from sklearn.metrics.pairwise import euclidean_distances

class NumpySeedContext(object):
    """
    A context manager to reset the random seed by numpy.random.seed(..).
    Set the seed back at the end of the block.

    From: https://github.com/wittawatj/fsic-test 
    """
    def __init__(self, seed):
        self.seed = seed 

    def __enter__(self):
        rstate = np.random.get_state()
        self.cur_state = rstate
        np.random.seed(self.seed)
        return self

    def __exit__(self, *args):
        np.random.set_state(self.cur_state)

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def meddistance(X, subsample=None, mean_on_fail=True):
    """
    Compute the median of pairwise distances (not distance squared) of points
    in the matrix.  Useful as a heuristic for setting Gaussian kernel's width.
    Parameters
    ----------
    X : n x d numpy array
    mean_on_fail: True/False. If True, use the mean when the median distance is 0.
        This can happen especially, when the data are discrete e.g., 0/1, and 
        there are more slightly more 0 than 1. In this case, the m
    Return
    ------
    median distance

    From: https://github.com/wittawatj/fsic-test
    """
    if subsample is None:
        D = euclidean_distances(X, X)
        Itri = np.tril_indices(D.shape[0], -1)
        Tri = D[Itri]
        med = np.median(Tri)
        if med <= 0:
            # use the mean
            return np.mean(Tri)
        return med

    else:
        assert subsample > 0
        rand_state = np.random.get_state()
        np.random.seed(9827)
        n = X.shape[0]
        ind = np.random.choice(n, min(subsample, n), replace=False)
        np.random.set_state(rand_state)
        # recursion just one
        return meddistance(X[ind, :], None, mean_on_fail)

def tr_te_indices(n, tr_proportion, seed=9282 ):
    """Get two logical vectors for indexing train/test points.
    Return (tr_ind, te_ind)

    From: https://github.com/wittawatj/fsic-test
    """
    rand_state = np.random.get_state()
    np.random.seed(seed)

    Itr = np.zeros(n, dtype=bool)
    tr_ind = np.random.choice(n, int(tr_proportion*n), replace=False)
    Itr[tr_ind] = True
    Ite = np.logical_not(Itr)

    np.random.set_state(rand_state)
    return (Itr, Ite)

def subsample_ind(n, k, seed=32):
    """
    Return a list of indices to choose k out of n without replacement

    """
    with NumpySeedContext(seed=seed):
        ind = np.random.choice(n, k, replace=False)
    return ind
    
def fit_gaussian_draw(X, J, seed=28, reg=1e-7, eig_pow=1.0):
    """
    Fit a multivariate normal to the data X (n x d) and draw J points 
    from the fit. 
    - reg: regularizer to use with the covariance matrix
    - eig_pow: raise eigenvalues of the covariance matrix to this power to construct 
        a new covariance matrix before drawing samples. Useful to shrink the spread 
        of the variance.
    
    From: https://github.com/wittawatj/fsic-test
    """
    with NumpySeedContext(seed=seed):
        d = X.shape[1]
        mean_x = np.mean(X, 0)
        cov_x = np.cov(X.T)
        if d==1:
            cov_x = np.array([[cov_x]])
        [evals, evecs] = np.linalg.eig(cov_x)
        evals = np.maximum(0, np.real(evals))
        assert np.all(np.isfinite(evals))
        evecs = np.real(evecs)
        shrunk_cov = evecs.dot(np.diag(evals**eig_pow)).dot(evecs.T) + reg*np.eye(d)
        V = np.random.multivariate_normal(mean_x, shrunk_cov, J)
    return V

def outer_rows(X, Y):
    """
    Compute the outer product of each row in X, and Y.
    X: n x dx numpy array
    Y: n x dy numpy array
    Return an n x dx x dy numpy array.
    """
    return np.einsum('ij,ik->ijk', X, Y)