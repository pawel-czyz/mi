import numpy as np
import pytest
from jax import random

from bmi.estimators.histogram import HistogramEstimator
from bmi.samplers.splitmultinormal import SplitMultinormal


@pytest.mark.parametrize("n_points", [2000])
@pytest.mark.parametrize("correlation", [0.0, 0.5, 0.8])
@pytest.mark.parametrize("n_bins", [6, 8, 10])
def test_estimate_mi_ksg_2d(n_points: int, correlation: float, n_bins: int) -> None:
    """Simple tests for the KSG estimator with 2D Gaussian with known correlation."""
    covariance = np.array(
        [
            [1.0, correlation],
            [correlation, 1.0],
        ]
    )
    distribution = SplitMultinormal(
        dim_x=1,
        dim_y=1,
        mean=np.zeros(2),
        covariance=covariance,
    )
    rng = random.PRNGKey(19)
    points_x, points_y = distribution.sample(n_points, rng=rng)

    estimator = HistogramEstimator(n_bins_x=n_bins)
    estimated_mi = estimator.estimate(points_x, points_y)

    true_mi = distribution.mutual_information()

    assert estimated_mi == pytest.approx(true_mi, rel=0.15, abs=0.12)
