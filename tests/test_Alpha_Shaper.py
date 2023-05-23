"""
tests for Alpha_Shaper.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
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


@pytest.fixture(scope="class")
def dataset_issue_3() -> pd.DataFrame:
    """
    returns the dataset referenced in issue #3
    A standard triangulation may not cover all vertices.
    """
    current_dir = Path(__file__).parent.absolute()

    datafile = current_dir / "data" / "decade_points_2020.csv"

    df = pd.read_csv(datafile)

    return df.drop_duplicates()   # type: ignore


class TestAlphaShaperIssue3:
    def test_optimization_with_possibly_missing_points(self, dataset_issue_3):
        """
        Test with a dataset for which the triangulation may not cover all vertices.
        A naive implementation would raise an error.
        issue #3
        """
        shaper = Alpha_Shaper(dataset_issue_3)
        _ = shaper.optimize()

    def test_some_points_are_missing_from_triangulation(self, dataset_issue_3):
        """
        Test that indeed some points are not included as vertices
        issue #3
        """
        shaper = Alpha_Shaper(dataset_issue_3)

        all_uncovered_vertices = set(range(shaper.x.size)) - set(
            np.ravel(shaper.simplices)
        )

        assert len(all_uncovered_vertices) != 0
