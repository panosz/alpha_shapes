"""
This is a core module of package which contains exceptions, functions
and classes essential to creating and working with figures.
"""

from typing import Tuple, Union

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
    """Abstract class with useful interface.
    Visitor sublclass of matplotlib.tri.Triangulation.
    See similar idea on scipy.spatial.Delaunay solution.
    """

    def __init__(self, coords: NDArray) -> None:
        """Set the interface object and pass the coords into it.

        Args:
            coords(NDArray): raw coords at which preparation process will be performed.

        Raises:
        - NotEnoughPoints: If there are fewer than 3 points provided.
        - ValueError: For other value-related issues with the coordinates.
        """

        try:
            super().__init__(x=coords[:, 0], y=coords[:, 1])
        except ValueError as e:
            if "at least 3" in str(e):
                raise NotEnoughPoints("Need at least 3 points")
            else:
                raise

    @property
    def simplices(self) -> NDArray:
        """Return the collection of triangles."""
        return self.triangles

    def __len__(self) -> int:
        """Return amount of object's simplices."""
        return self.simplices.shape[0]


class Alpha_Shaper(Delaunay):
    """The class enables the creation of shapes and further operations on them."""

    mask: NDArray  # for type hinting

    def __init__(self, points: ArrayLike, normalize=True) -> None:
        """Pass points into shaper. Optionally perform normalization.

        Args:
            points(ArrayLike): points used to create shapes.

            normalize(bool): The flag determines whether the normalization process will be carried out.
            See more about normalization on https://github.com/panosz/alpha_shapes.

        """

        self.normalized = normalize

        points = np.array(points)

        if self.normalized:
            points, center, scale = _normalize_points(points)
            self._initialize(points)
            self._denormalize(center, scale)

        else:
            self._initialize(points)

    def _initialize(self, points: NDArray) -> None:
        """_initialize the alpha shaper.

        Args:
            points(NDArray): points at which normalization will be performed.

        """

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
        """Return the collection of simplices, sorted by their circumradius."""
        return self.simplices[self.argsort]

    def _sorted_circumradii_sw(self) -> NDArray[np.float64]:
        """Return sorted values of squares circumradiuses of internal triangles."""
        return self.circumradii_sq[self.argsort]

    def _shape_from_simplices(self, simplices: ArrayLike) -> ArrayLike:
        """Return the shape from simplices.
        Output is in unary_union form which makes further operations on a shape easier. """

        triangles = [_simplex_to_triangle(smpl, self) for smpl in simplices]

        return unary_union(triangles)

    def get_mask(self, alpha: float) -> NDArray:
        """Return mask, based on squares of circumradiuses of internal triangles.
        Mask specifies which elements should be considered for triangulation."""
        return self.circumradii_sq > 1 / alpha**2

    def get_shape(self, alpha: float) -> ArrayLike:
        """Return shape, based on the given alpha.
        If alpha is less or equal to 0, the shape creation will be based on external points.
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
        """Return the minimum index of simplices needed to cover all vertices.
        The set of all simplices up to this index is fully covering.

        Raises:
            - OptimizationFailure: For issues when the conditions for optimization are not met.
            A common issue is duplicate points in the dataset.

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
        """Return the alpha value that allows plotting the shape with the minimum number of triangles.
        Vertices of initial triangulation aren't left uncovered.

        Returns:
            alpha_opt(NDArray): optimized alpha value.
            shape(ArrayLike): shape based on the optimized alpha value.

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


def _circumradius_sq(lengths: NDArray) -> Union[float, np.inf]:
    """Calculate the squared circumradius `r_c^2` where r_c = \frac {abc}{4{\sqrt {s(s-a)(s-b)(s-c)}}}.
    See more about it on: `https://en.wikipedia.org/wiki/Circumscribed_circle`.

    Args:
        lengths(NDArray): contains lengths of triangle's sides.

    Returns:
        Union[float, np.inf]: value of squared circumradius.

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
        x, y: array-like, shape(3,)
        coordinates of the triangle

    Returns:
         NDArray: squared circumradius of internal triangle.

    """

    dx = x - np.roll(x, shift=-1)
    dy = y - np.roll(y, shift=-1)

    lengths = np.hypot(dx, dy)
    return _circumradius_sq(lengths)


def _simplex_to_triangle(smpl: slice, tri) -> Polygon:
    """Return triangle points.

    Args:
        smpl(slice): value of simplex.
        tri: particular triangle.

    Returns:
        Polygon: contains points values of triangle.

    """

    x = tri.x[smpl]
    y = tri.y[smpl]

    return Polygon(zip(x, y))
