"""
tests for Alpha_Shaper.py
"""
import numpy as np
import pytest

from alpha_shapes import Alpha_Shaper


def test_optimization_with_strongly_shaped_points():
    """
    Test the optimization with strongly shaped points
    issue #1
    """
    points = [
        (363820.32, 5771887.69),
        (363837.36, 5771916.33),
        (363870.03, 5771951.57),
        (363859.3, 5771943.9),
        (363829.7, 5771861.92),
        (363821.03, 5771850.18),
        (363844.05, 5771928.69),
        (363828.75, 5771906.28),
    ]
    shaper = Alpha_Shaper(points)
    alpha_opt, alpha_shape = shaper.optimize()

    # check that no simplex is masked
    not_masked = np.logical_not(shaper.mask)
    assert np.all(not_masked)
