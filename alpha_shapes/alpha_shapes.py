"""
Utility module for the calculation of alpha shapes
"""

from functools import wraps
import numpy as np
from matplotlib.tri import Triangulation
from shapely.ops import unary_union
from shapely.geometry import Polygon
from shapely.ops import transform


class AlphaException(Exception):
    pass


class NotEnoughPoints(AlphaException):
    pass


class OptimizationFailure(AlphaException):
    pass


class Delaunay(Triangulation):
    """
    Visitor sublclass of matplotlib.tri.Triangulation.
    Mimics scipy.spatial.Delaunay interface.
    """

    def __init__(self, coords):
        coords = np.unique(coords, axis=0)  # ignore duplicate points
        try:
            super().__init__(x=coords[:, 0], y=coords[:, 1])
        except ValueError as e:
            if 'at least 3' in str(e):
                raise NotEnoughPoints("Need at least 3 points")
            else:
                raise

    @property
    def simplices(self):
        return self.triangles

    def __len__(self):
        return self.simplices.shape[0]


class Alpha_Shaper_Base(Delaunay):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        circumradii_sq = [_circumradius_sq_simplex(smpl, self)
                          for smpl in self.simplices]

        self.circumradii_sq = np.array(circumradii_sq)
        self.argsort = np.argsort(self.circumradii_sq)

    def _sorted_simplices(self):
        return self.simplices[self.argsort]

    def _sorted_circumradii_sw(self):
        return self.circumradii_sq[self.argsort]

    def _shape_from_simplices(self, simplices):
        triangles = [_simplex_to_triangle(smpl, self) for smpl in simplices
                     ]

        return unary_union(triangles)

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
        provided simplices.
        """
        n_points = self.x.size
        return set(range(n_points)) - set(np.ravel(simplices))

    def optimize(self):
        # At least N//3 triangles are needed to connect N points.
        for n in range(len(self)//3, len(self)+1):
            simplices = self._sorted_simplices()[:n]
            uncovered_vertices = self._uncovered_vertices(simplices)
            if not uncovered_vertices:
                alpha_opt = 1/np.sqrt(self._sorted_circumradii_sw()[n])
                shape = self._shape_from_simplices(simplices)
                return alpha_opt, shape

        raise OptimizationFailure()


def _denormalize(method):
    """
    decorator for denormalizing geometries, if needed.
    Applies to methods that only return geometries or geometries bunched with
    other staff in tuples (stuff,..., geometry)
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        if isinstance(result, tuple):
            *other, geom = result
        else:
            other = []
            geom = result
        if self.normalize:
            def d_trasf(x, y):
                x_out = x * self.scale[0] + self.center[0]
                y_out = y * self.scale[1] + self.center[1]
                return x_out, y_out
            geom = transform(d_trasf, geom)

        if other:
            return (*other, geom)
        else:
            return geom
    return wrapper


class Alpha_Shaper(Alpha_Shaper_Base):

    def __init__(self, points, *args, normalize=False, **kwargs):

        self.normalize = normalize

        if self.normalize:
            points = np.copy(points)
            self.center = points.mean(axis=0)
            self.scale = np.ptp(points, axis=0)  # peak to peak distance
            points = (points - self.center)/self.scale

        super().__init__(points, *args, **kwargs)

    @_denormalize
    def get_shape(self, *args, **kwargs):
        return super().get_shape(*args, **kwargs)

    @_denormalize
    def optimize(self, *args, **kwargs):
        return super().optimize(*args, **kwargs)


def _circumradius_sq(lengths):
    r"""
    Calculate the squared circumradius `r_c^2`,
    where
    r_c = \frac {abc}{4{\sqrt {s(s-a)(s-b)(s-c)}}}
    See: `https://en.wikipedia.org/wiki/Circumscribed_circle`
    """
    lengths = np.asarray(lengths)
    s = np.sum(lengths)/2

    num = np.prod(lengths) ** 2

    denom = 16 * s * np.prod(s-lengths)

    return num/denom


def _circumradius_sq_simplex(smpl, tri):
    r"""
    Calculate the squared circumradius `r_c^2` of a simplex `smpl` in a given
    triangulation `tri`, where
    r_c = \frac {abc}{4{\sqrt {s(s-a)(s-b)(s-c)}}}
    See: `https://en.wikipedia.org/wiki/Circumscribed_circle`
    """
    x = tri.x[smpl]
    y = tri.y[smpl]

    dx = x - np.roll(x, shift=-1)
    dy = y - np.roll(y, shift=-1)

    lengths = np.hypot(dx, dy)
    return _circumradius_sq(lengths)


def _should_include_simplex(smpl, alpha, tri):
    """
    Determine if a simplex `smpl` of a given triangulation `tri` should
    be included in the alpha complex with parameter `alpha`.
    """
    return _circumradius_sq_simplex(smpl, tri) <= 1 / alpha**2


def _simplex_to_triangle(smpl, tri):
    x = tri.x[smpl]
    y = tri.y[smpl]

    return Polygon(zip(x, y))


def _alpha_shape(points, alpha, tri=None, report_tri=False):
    if tri is None:
        tri = Delaunay(points)

    if (alpha <= 0):
        def include_simplex(smpl):
            return True
    else:
        def include_simplex(smpl):
            return _should_include_simplex(smpl, alpha, tri)

    triangles = [_simplex_to_triangle(smpl, tri) for smpl in tri.simplices
                 if include_simplex(smpl)
                 ]

    return unary_union(triangles)
