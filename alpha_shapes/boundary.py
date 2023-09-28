"""
Classes and functions for accessing the boundary of a shape.
"""

from typing import List, Union

import numpy as np
from shapely import MultiPolygon, Polygon


class Boundary:
    """
    A class for easy access of the coordinates of the boundary of a polygon
    """

    def __init__(self, poly: Polygon):
        self.poly = poly
        self._exterior = np.array(poly.exterior.coords)
        self._holes = [np.array(hole.coords) for hole in poly.interiors]

    @property
    def exterior(self) -> np.ndarray:
        """
        The exterior boundary of the shape.

        Returns
        -------
        np.ndarray, shape (n, 2)
            The coordinates of the exterior boundary
        """
        return self._exterior

    @property
    def holes(self) -> List[np.ndarray]:
        """
        The holes of the shape.

        Returns
        -------
        List[np.ndarray], shape (n, 2)
            The coordinates of the holes
        """
        return self._holes


def get_boundaries(alpha_shape: Union[Polygon, MultiPolygon]) -> List[Boundary]:
    """
    Returns a list of compound objects containing the coordinates of the boundaries of the alpha shape.

    Each member of the list defines an `exterior` attribute which is an ndarray whose columns contain the x and y
    coordinates of the exterior boundary and a `holes` attribute which is a list of ndarrays whose columns contain the
    x and y coordinates of the holes.

    As the alpha shape may consist of multiple polygons, the list may contain multiple elements.

    Parameters
    ----------
    alpha_shape : Polygon or MultiPolygon
        The alpha shape

    Returns
    -------
    list of Boundary
        The boundaries of the alpha shape
    """

    if isinstance(alpha_shape, Polygon):
        return [Boundary(alpha_shape)]
    elif isinstance(alpha_shape, MultiPolygon):
        return [Boundary(poly) for poly in alpha_shape.geoms]
    else:
        raise TypeError(
            f"alpha_shape must be a Polygon or MultiPolygon, not {type(alpha_shape)}"
        )
