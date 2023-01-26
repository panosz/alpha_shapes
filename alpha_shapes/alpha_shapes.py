"""
Utility module for the calculation of alpha shapes
"""

import warnings

import numpy as np
from matplotlib.tri import Triangulation
from numpy.typing import ArrayLike, NDArray
from shapely.geometry import Polygon
from shapely.ops import transform, unary_union


class AlphaException(Exception):
    pass


class NotEnoughPoints(AlphaException):
    pass


class OptimizationFailure(AlphaException):
    pass


class OptimizationWarnging(UserWarning):
    pass


class Delaunay(Triangulation):
    """
    Visitor sublclass of matplotlib.tri.Triangulation.
    Mimics scipy.spatial.Delaunay interface.
    """

    def __init__(self, coords: NDArray):

        try:
            super().__init__(x=coords[:, 0], y=coords[:, 1])
        except ValueError as e:
            if "at least 3" in str(e):
                raise NotEnoughPoints("Need at least 3 points")
            else:
                raise

    @property
    def simplices(self):
        return self.triangles

    def __len__(self):
        return self.simplices.shape[0]


class Alpha_Shaper(Delaunay):
    def __init__(self, points: NDArray, normalize=True):

        self.normalized = normalize

        points = np.array(points)

        if self.normalized:
            points, center, scale = _normalize_points(points)

        super().__init__(points)

        self.circumradii_sq = (
            self._calculate_cirumradii_sq_of_internal_triangles()
        )
        self.argsort = np.argsort(self.circumradii_sq)

        if self.normalized:
            self._denormalize(center, scale)

    def _denormalize(self, center, scale):
        self.x = self.x * scale[0] + center[0]
        self.y = self.y * scale[1] + center[1]

    def _calculate_cirumradii_sq_of_internal_triangles(self):
        circumradii_sq = [
            self._get_circumradius_sq_of_internal_simplex(smpl)
            for smpl in self.simplices
        ]
        return np.array(circumradii_sq)

    def _get_circumradius_sq_of_internal_simplex(self, smpl):
        x = self.x[smpl]
        y = self.y[smpl]
        return _calculate_cirumradius_sq_of_triangle(x, y)

    def _sorted_simplices(self):
        return self.simplices[self.argsort]

    def _sorted_circumradii_sw(self):
        return self.circumradii_sq[self.argsort]

    def _shape_from_simplices(self, simplices):
        triangles = [_simplex_to_triangle(smpl, self) for smpl in simplices]

        return unary_union(triangles)

    def get_mask(self, alpha):
        return self.circumradii_sq > 1 / alpha**2

    def get_shape(self, alpha):
        if alpha > 0:
            select = self.circumradii_sq <= 1 / alpha**2
            simplices = self.simplices[select]
        else:
            simplices = self.simplices

        return self._shape_from_simplices(simplices)

    def _nth_shape(self, n):
        """
        return the shape formed by the n smallest simplices
        """
        simplices = self._sorted_simplices()[:n]
        return self._shape_from_simplices(simplices)

    def _uncovered_vertices(self, simplices):
        """
        Return a set of vertices that is not covered by the
        specified simplices.
        """
        n_points = self.x.size
        return set(range(n_points)) - set(np.ravel(simplices))

    def _get_minimum_fully_covering_index_of_simplices(self):
        """
        Return the minimum index of simplices needed to cover all vertices.
        The set of all simplices up to this index is fully covering.
        """
        # At least N//3 triangles are needed to connect N points.
        simplices = self._sorted_simplices()
        n_start = len(self) // 3
        n_finish = len(self)
        uncovered_vertices = self._uncovered_vertices(simplices[:n_start])
        if not uncovered_vertices:
            return n_start

        for n in range(n_start, n_finish):
            simplex = simplices[n]
            uncovered_vertices -= set(simplex)

            if not uncovered_vertices:
                return n

        if uncovered_vertices:
            raise OptimizationFailure("Maybe there are duplicate points?")

    def optimize(self):
        # At least N//3 triangles are needed to connect N points.
        n_min = self._get_minimum_fully_covering_index_of_simplices()
        print(n_min)
        print(f"{len(self)=}")
        alpha_opt = 1 / np.sqrt(self._sorted_circumradii_sw()[n_min]) - 1e-10
        simplices = self._sorted_simplices()
        shape = self._shape_from_simplices(simplices[: n_min + 1])
        self.set_mask_at_alpha(alpha_opt)
        return alpha_opt, shape

    def set_mask_at_alpha(self, alpha: float):
        """
        Set the mask for the alpha shape at the specified alpha value.
        """
        mask = self.get_mask(alpha)
        self.set_mask(mask)
        return self


def _normalize_points(points: NDArray):
    """
    Normalize points to the unit square, centered at the origin.

    Parameters:
    -----------
    points: array-like, shape(N,2)
        coordinates of the points

    Returns:
    --------
    points: array, shape(N,2)
        normalized coordinates of the points

    center: array, shape(2,)
        coordinates of the center of the points

    scale: array, shape(2,)
        scale factors for the normalization
    """
    center = points.mean(axis=0)
    scale = np.ptp(points, axis=0)  # peak to peak distance
    normalized_points = (points - center) / scale

    return normalized_points, center, scale


def _circumradius_sq(lengths):
    r"""
    Calculate the squared circumradius `r_c^2`,
    where
    r_c = \frac {abc}{4{\sqrt {s(s-a)(s-b)(s-c)}}}
    See: `https://en.wikipedia.org/wiki/Circumscribed_circle`
    """
    lengths = np.asarray(lengths)
    s = np.sum(lengths) / 2

    num = np.prod(lengths) ** 2

    denom = 16 * s * np.prod(s - lengths)

    if denom < 1e-16:
        return np.inf

    return num / denom


def _calculate_cirumradius_sq_of_triangle(x: ArrayLike, y: ArrayLike):
    """
    calculates the squared circumradius of a triangle with coordinates x, y

    Parameters:
    -----------
    x, y: array-like, shape(3,)
        coordinates of the triangle
    """
    dx = x - np.roll(x, shift=-1)
    dy = y - np.roll(y, shift=-1)

    lengths = np.hypot(dx, dy)
    return _circumradius_sq(lengths)


def _simplex_to_triangle(smpl, tri):
    x = tri.x[smpl]
    y = tri.y[smpl]

    return Polygon(zip(x, y))
