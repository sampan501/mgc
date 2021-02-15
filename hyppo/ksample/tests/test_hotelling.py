import numpy as np
import pytest
from numpy.testing import assert_almost_equal, assert_raises

from ...tools import rot_ksamp
from .. import Hotelling


class TestHotelling:
    @pytest.mark.parametrize(
        "n, obs_stat, obs_pvalue",
        [
            (1000, 0.00253015392620975, 0.997473047413008),
            (100, 8.24e-5, 0.953158769593477),
        ],
    )
    def test_linear_oned(self, n, obs_stat, obs_pvalue):
        np.random.seed(123456789)
        x, y = rot_ksamp("linear", n, 1, k=2, noise=False)
        stat, pvalue = Hotelling().test(x, y)

        assert_almost_equal(stat, obs_stat, decimal=1)
        assert_almost_equal(pvalue, obs_pvalue, decimal=1)
