"""
This is a core module of package, which contains exceptions, functions
and classes essential to printing figures.
"""

from typing import Tuple

import numpy as np
from matplotlib.tri import Triangulation
from numpy.typing import ArrayLike, NDArray
from shapely.geometry import Polygon
from shapely.ops import unary_union


class AlphaException(Exception):
    """Abstract class for exceptions which could be raised during the work of Alpha_Shaper class."""
    pass


class NotEnoughPoints(AlphaException):
    """Raised when an operation requires a certain number of points and that condition is not met."""
    pass


class OptimizationFailure(AlphaException):
    """Raised when the conditions for optimization are not met."""
    pass


class OptimizationWarning(UserWarning):
    """Warns user without interrupting the program."""
    pass


class Delaunay(Triangulation):
    """Abstract class, which provides useful interface. This idea is similar to scipy.spatial.Delaunay solution.
    Coordinates of future Alpha_Shaper object will be added via Delaunay class.
    If the coordinates do not meet the conditions, the class will raise an appropriate error.
    It also adds key methods.

    """

    def __init__(self, coords: NDArray) -> None:
        try:
            super().__init__(x=coords[:, 0], y=coords[:, 1])
        except ValueError as e:
            if "at least 3" in str(e):
                raise NotEnoughPoints("Need at least 3 points")
            else:
                raise

    @property
    def simplices(self) -> NDArray:
        """Create simplices property essential to further operations."""
        return self.triangles

    def __len__(self) -> int:
        """Return amount of object's edges."""
        return self.simplices.shape[0]


class Alpha_Shaper(Delaunay):
    mask: NDArray  # for type hinting
    """Crucial class to creating alpha-shapes. 
   The class handles points, creates internal triangles and generates shapes. 
    """

    def __init__(self, points: ArrayLike, normalize=True) -> None:
        self.normalized = normalize

        points = np.array(points)

        if self.normalized:
            points, center, scale = _normalize_points(points)
            self._initialize(points)
            self._denormalize(center, scale)

        else:
            self._initialize(points)

    def _initialize(self, points: NDArray) -> None:
        """_initialize the alpha shaper."""

        super().__init__(points)

        self.circumradii_sq = self._calculate_cirumradii_sq_of_internal_triangles()
        self.argsort = np.argsort(self.circumradii_sq)
        default_mask = np.full_like(self.circumradii_sq, False, dtype=bool)
        self.set_mask(default_mask)

    def _denormalize(self, center: NDArray, scale: NDArray) -> None:
        """Transform back points into their original scale."""
        self.x = self.x * scale[0] + center[0]
        self.y = self.y * scale[1] + center[1]

    def _calculate_cirumradii_sq_of_internal_triangles(self) -> NDArray:
        """Method calculates circumradiuses squares of all internal triangles."""

        circumradii_sq = [
            self._get_circumradius_sq_of_internal_simplex(smpl)
            for smpl in self.simplices
        ]
        return np.array(circumradii_sq)

    def _get_circumradius_sq_of_internal_simplex(self, smpl: slice) -> NDArray:
        """Read value of squared circumradius of internal triangle."""
        x = self.x[smpl]
        y = self.y[smpl]
        return _calculate_cirumradius_sq_of_triangle(x, y)

    def _sorted_simplices(self) -> NDArray[np.float64]:
        """Return all simplices of instance, sorted before by given axis."""
        return self.simplices[self.argsort]

    def _sorted_circumradii_sw(self) -> NDArray[np.float64]:
        """Return sorted values of squares circumradiuses of internal triangles."""
        return self.circumradii_sq[self.argsort]

    def _shape_from_simplices(self, simplices: ArrayLike) -> ArrayLike:
        """From given simplices create triangles. Then make union."""

        triangles = [_simplex_to_triangle(smpl, self) for smpl in simplices]

        return unary_union(triangles)

    def get_mask(self, alpha: float) -> NDArray:
        """Create mask, based on squares of circumradiuses of internal triangles."""
        return self.circumradii_sq > 1 / alpha**2

    def get_shape(self, alpha: float) -> ArrayLike:
        """Return shape, constrained by alpha.
        If alpha is less or equal to 0, function will use original array of simplices.
        """

        if alpha > 0:
            select = self.circumradii_sq <= 1 / alpha**2
            simplices = self.simplices[select]
        else:
            simplices = self.simplices

        return self._shape_from_simplices(simplices)

    def _nth_shape(self, n: int) -> ArrayLike:
        """Return the shape formed by the amount of n-smallest simplices."""
        simplices = self._sorted_simplices()[:n]
        return self._shape_from_simplices(simplices)

    def all_vertices(self) -> set:
        """Return all vertices of object."""
        return set(np.ravel(self.simplices))

    def _uncovered_vertices(self, simplices: ArrayLike) -> set:
        """Return a set of vertices, which is not covered by the specified simplices."""
        return self.all_vertices() - set(np.ravel(simplices))

    def _get_minimum_fully_covering_index_of_simplices(self) -> int:
        """Return the minimum amount of simplices essential to cover all vertices.
        The set of all simplices up to this index is fully covering.
        If function face problems, it will raise appropriate exceptions.

        """
        # We have to use at least N//3 triangles to connect N points.
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

        raise OptimizationFailure("Maybe there are duplicate points?")

    def optimize(self) -> Tuple[NDArray, ArrayLike]:
        """Eliminate redundant simplices and then set appropriate mask.

        Returns:
            alpha_opt: the most appropriate alpha value based on minimal amount of simplices.
            shape: shape after optimization.

        """
        # We have to use at least N//3 triangles to connect N points
        n_min = self._get_minimum_fully_covering_index_of_simplices()
        alpha_opt = 1 / np.sqrt(self._sorted_circumradii_sw()[n_min]) - 1e-10
        simplices = self._sorted_simplices()
        shape = self._shape_from_simplices(simplices[: n_min + 1])
        self.set_mask_at_alpha(alpha_opt)
        return alpha_opt, shape

    def set_mask_at_alpha(self, alpha: float):
        """Set the mask for the alpha shape based on the given alpha value."""
        mask = self.get_mask(alpha)
        self.set_mask(mask)
        return self


def _normalize_points(points: NDArray) -> Tuple[NDArray, NDArray, NDArray]:
    """Normalize points to the unit square, centered at the origin.

    Args:
    points: array-like, shape(N,2)
        coordinates of the points

    Returns:
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


def _circumradius_sq(lengths: NDArray) -> NDArray:
    """Calculate the squared circumradius of triangle.
    See more about it on: `https://en.wikipedia.org/wiki/Circumscribed_circle`.

    Args:
        lengths: contains lengths of triangle's sides.

    Returns:
        Contains values of squared circumradiuses.

    """

    lengths = np.asarray(lengths)
    s = np.sum(lengths) / 2

    num = np.prod(lengths) ** 2

    denom = 16 * s * np.prod(s - lengths)

    if denom < 1e-16:
        return np.inf

    return num / denom


def _calculate_cirumradius_sq_of_triangle(x: ArrayLike, y: ArrayLike) -> NDArray:
    """Calculate the squared circumradius of a triangle with coordinates x, y.

    Args:
        x: Contains all x values of triangle's points.
        y: Contains all y values of triangle's points.

    Returns:
         outcome:  Contains squared circumradius of internal triangle.

    """

    dx = x - np.roll(x, shift=-1)
    dy = y - np.roll(y, shift=-1)

    lengths = np.hypot(dx, dy)
    return _circumradius_sq(lengths)


def _simplex_to_triangle(smpl: slice, tri) -> Polygon:
    """Create internal triangle from given simplices.

    Args:
        smpl: value of simplex.
        tri: particular triangle.

    Returns:
        Polygon: contains points values of internal triangle.

    """

    x = tri.x[smpl]
    y = tri.y[smpl]

    return Polygon(zip(x, y))
