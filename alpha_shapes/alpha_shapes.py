"""
This is a core module of package, which contains exceptions, functions
and classes essential to printing figures.
"""

import numpy as np
from matplotlib.tri import Triangulation
from numpy.typing import ArrayLike, NDArray
from shapely.geometry import Polygon
from shapely.ops import unary_union


class AlphaException(Exception):
    """Abstract class for all exceptions which will be raised within Alpha_Shaper class
     directly or through Delaunay class"""
    pass


class NotEnoughPoints(AlphaException):
    """If instance of class Delaunay has less than 3 points, this exception will be raised"""
    pass


class OptimizationFailure(AlphaException):
    """If Alpha_Shaper instance can't cover all vertices, this exception will be raised"""
    pass


class OptimizationWarning(UserWarning):
    """Warns user without interrupting the program"""
    pass


class Delaunay(Triangulation):
    """
    Delaunay is abstract class, which derives from matplotlib.tri.Triangulation.
    It adds set of coordinates and essential methods.
    """

    def __init__(self, coords: NDArray):
        """In try block function invokes __init__ method of class
        Triangulation from matplotlib package and sends
        to it default set of coordinates. If ValueError occurs,
        function will tackle it."""
        try:
            super().__init__(x=coords[:, 0], y=coords[:, 1])
        except ValueError as e:
            if "at least 3" in str(e):
                raise NotEnoughPoints("Need at least 3 points")
            else:
                raise

    @property
    def simplices(self):
        """Creates simplices property essential to further operations"""
        return self.triangles

    def __len__(self):
        """Returns amount of object's edges"""
        return self.simplices.shape[0]


class Alpha_Shaper(Delaunay):
    """Crucial class to creating alpha-shapes"""
    def __init__(self, points: ArrayLike, normalize=True):
        """Assings points to instance, creates basic properties and denormalizes points"""
        self.normalized = normalize

        points = np.array(points)

        if self.normalized:
            points, center, scale = _normalize_points(points)

        super().__init__(points)

        self.circumradii_sq = self._calculate_cirumradii_sq_of_internal_triangles()
        self.argsort = np.argsort(self.circumradii_sq)

        if self.normalized:
            self._denormalize(center, scale)

    def _denormalize(self, center: ArrayLike, scale: ArrayLike):
        """Transforms back points into their orginal scale"""
        self.x = self.x * scale[0] + center[0]
        self.y = self.y * scale[1] + center[1]

    def _calculate_cirumradii_sq_of_internal_triangles(self) -> NDArray:
        """Main-line method, which calculates circumradius squares of all internal triangles
         and saves them into numpy.array. It's important during initialization of object."""
        circumradii_sq = [
            self._get_circumradius_sq_of_internal_simplex(smpl)
            for smpl in self.simplices
        ]
        return np.array(circumradii_sq)

    def _get_circumradius_sq_of_internal_simplex(self, smpl: ArrayLike) -> NDArray:
        """Reads values of simplices and then
        sends it to _calculate_cirumradius_sq_of_triangle function."""
        x = self.x[smpl]
        y = self.y[smpl]
        return _calculate_cirumradius_sq_of_triangle(x, y)

    def _sorted_simplices(self) -> NDArray:
        """Returns all simplices of instance, sorted before by given axis"""
        return self.simplices[self.argsort]

    def _sorted_circumradii_sw(self) -> NDArray:
        """Returns sorted values of squares circumraiduses of internal triangles"""
        return self.circumradii_sq[self.argsort]

    def _shape_from_simplices(self, simplices: ArrayLike) -> ArrayLike:
        """Sends values of simplices to _simplex_to_triangle
        function and saves triangles. Function shapely.ops.unary_union can receive and return many types of objects,
        its output depends on input types. In this case function will return array of ints."""
        triangles = [_simplex_to_triangle(smpl, self) for smpl in simplices]

        return unary_union(triangles)

    def get_mask(self, alpha: float) -> NDArray:
        """Creates mask, based on squares circumradiuses of internal triangles"""
        return self.circumradii_sq > 1 / alpha**2

    def get_shape(self, alpha: float) -> ArrayLike:
        """Returns shape, constrained by aplha in form of array.
        If aplha is less than 0, function will use original array of simplices"""
        if alpha > 0:
            select = self.circumradii_sq <= 1 / alpha**2
            simplices = self.simplices[select]
        else:
            simplices = self.simplices

        return self._shape_from_simplices(simplices)

    def _nth_shape(self, n: int) -> ArrayLike:
        """Returns the shape formed by the amount of n-smallest simplices"""
        simplices = self._sorted_simplices()[:n]
        return self._shape_from_simplices(simplices)

    def all_vertices(self) -> set:
        """Returns all vertices of object by set"""
        return set(np.ravel(self.simplices))

    def _uncovered_vertices(self, simplices: ArrayLike) -> set:
        """Returns a set of vertices, which is not covered by the specified simplices."""
        return self.all_vertices() - set(np.ravel(simplices))

    def _get_minimum_fully_covering_index_of_simplices(self) -> ArrayLike:
        """Returns the minimum amount of simplices essential to cover all vertices.
        If function face problem with vertices, it will raise OptimizationFailure exception."""
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

        if uncovered_vertices:
            raise OptimizationFailure("Maybe there are duplicate points?")

    def optimize(self) -> (NDArray, ArrayLike):
        """Eliminates redundant simplices and then sets appropriate mask.

        Returns:
            alpha_opt: themost accurate alpha value based on minimal amount of simplices
            shape: shape after optimization
        """
        # We have to use at least N//3 triangles to connect N points
        n_min = self._get_minimum_fully_covering_index_of_simplices()
        alpha_opt = 1 / np.sqrt(self._sorted_circumradii_sw()[n_min]) - 1e-10
        simplices = self._sorted_simplices()
        shape = self._shape_from_simplices(simplices[: n_min + 1])
        self.set_mask_at_alpha(alpha_opt)
        return alpha_opt, shape

    def set_mask_at_alpha(self, alpha: float):
        """Sets the mask for the alpha shape based on the appropriate alpha value."""
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


def _calculate_cirumradius_sq_of_triangle(x: ArrayLike, y: ArrayLike) -> NDArray:
    """Calculates the squared circumradius of a triangle with coordinates x, y"""
    dx = x - np.roll(x, shift=-1)
    dy = y - np.roll(y, shift=-1)

    lengths = np.hypot(dx, dy)
    return _circumradius_sq(lengths)


def _simplex_to_triangle(smpl, tri) -> Polygon:
    """Creates internal triangles from given simplices.

    Returns:

    """
    x = tri.x[smpl]
    y = tri.y[smpl]

    return Polygon(zip(x, y))
