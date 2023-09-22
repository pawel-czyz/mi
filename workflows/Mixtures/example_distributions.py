"""The example distributions used in the paper."""
import dataclasses

import jax.numpy as jnp
import numpy as np

import bmi
from bmi.samplers import fine


@dataclasses.dataclass
class ExampleDistribution:
    """Binds base distribution and
    (potentially transformed)
    sampler together.

    Note: `dist` should not be used
    for sampling.
    It is used for PMI profile estimation.
    """

    dist: fine.JointDistribution
    sampler: bmi.ISampler


def create_x_distribution() -> ExampleDistribution:
    """The X distribution"""
    x_dist = fine.mixture(
        proportions=jnp.array([0.5, 0.5]),
        components=[
            fine.MultivariateNormalDistribution(
                covariance=0.3 * bmi.samplers.canonical_correlation([x * 0.9]),
                mean=jnp.zeros(2),
                dim_x=1,
                dim_y=1,
            )
            for x in [-1, 1]
        ],
    )
    x_sampler = fine.FineSampler(x_dist)
    return ExampleDistribution(dist=x_dist, sampler=x_sampler)


def create_galaxy_distribution() -> ExampleDistribution:
    """The Galaxy distribution."""
    balls_mixt = fine.mixture(
        proportions=jnp.array([0.5, 0.5]),
        components=[
            fine.MultivariateNormalDistribution(
                covariance=bmi.samplers.canonical_correlation([0.0], additional_y=1),
                mean=jnp.array([x, x, x]) * 1.5,
                dim_x=2,
                dim_y=1,
            )
            for x in [-1, 1]
        ],
    )

    base_balls_sampler = fine.FineSampler(balls_mixt)
    a = jnp.array([[0, -1], [1, 0]])
    spiral = bmi.transforms.Spiral(a, speed=0.5)

    sampler_balls_aux = bmi.samplers.TransformedSampler(base_balls_sampler, transform_x=spiral)
    sampler_balls_transformed = bmi.samplers.TransformedSampler(
        sampler_balls_aux,
        transform_x=lambda x: 0.3 * x,
    )
    return ExampleDistribution(dist=balls_mixt, sampler=sampler_balls_transformed)


def create_ai_distribution() -> ExampleDistribution:
    """The AI distribution."""
    corr = 0.95
    var_x = 0.04

    ai_dist = fine.mixture(
        proportions=jnp.full(6, fill_value=1 / 6),
        components=[
            # I components
            fine.MultivariateNormalDistribution(
                dim_x=1,
                dim_y=1,
                mean=jnp.array([1.0, 0.0]),
                covariance=np.diag([0.01, 0.2]),
            ),
            fine.MultivariateNormalDistribution(
                dim_x=1,
                dim_y=1,
                mean=jnp.array([1.0, 1]),
                covariance=np.diag([0.05, 0.001]),
            ),
            fine.MultivariateNormalDistribution(
                dim_x=1,
                dim_y=1,
                mean=jnp.array([1.0, -1]),
                covariance=np.diag([0.05, 0.001]),
            ),
            # A components
            fine.MultivariateNormalDistribution(
                dim_x=1,
                dim_y=1,
                mean=jnp.array([-0.8, -0.2]),
                covariance=np.diag([0.03, 0.001]),
            ),
            fine.MultivariateNormalDistribution(
                dim_x=1,
                dim_y=1,
                mean=jnp.array([-1.2, 0.0]),
                covariance=jnp.array(
                    [[var_x, jnp.sqrt(var_x * 0.2) * corr], [jnp.sqrt(var_x * 0.2) * corr, 0.2]]
                ),
            ),
            fine.MultivariateNormalDistribution(
                dim_x=1,
                dim_y=1,
                mean=jnp.array([-0.4, 0.0]),
                covariance=jnp.array(
                    [[var_x, -jnp.sqrt(var_x * 0.2) * corr], [-jnp.sqrt(var_x * 0.2) * corr, 0.2]]
                ),
            ),
        ],
    )
    ai_sampler = fine.FineSampler(ai_dist)
    return ExampleDistribution(dist=ai_dist, sampler=ai_sampler)


def create_waves_distribution(n_components: int = 12) -> ExampleDistribution:
    """The Waves distribution."""
    assert n_components > 0

    fence_base_dist = fine.mixture(
        proportions=jnp.ones(n_components) / n_components,
        components=[
            fine.MultivariateNormalDistribution(
                covariance=jnp.diag(jnp.array([0.1, 1.0, 0.1])),
                mean=jnp.array([x, 0, x % 4]) * 1.5,
                dim_x=2,
                dim_y=1,
            )
            for x in range(n_components)
        ],
    )
    base_sampler = fine.FineSampler(fence_base_dist)
    fence_aux_sampler = bmi.samplers.TransformedSampler(
        base_sampler,
        transform_x=lambda x: x + jnp.array([5.0, 0.0]) * jnp.sin(3 * x[1]),
    )
    fence_sampler = bmi.samplers.TransformedSampler(
        fence_aux_sampler, transform_x=lambda x: jnp.array([0.1 * x[0] - 0.8, 0.5 * x[1]])
    )
    return ExampleDistribution(dist=fence_base_dist, sampler=fence_sampler)
