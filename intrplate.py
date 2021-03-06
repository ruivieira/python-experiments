"""Generate synthetic data using B-spline interpolation"""
# INFO: Generate synthetic data using B-spline interpolation
# pylint: disable=E0401
from typing import List, Union
import numpy as np  # type: ignore
import scipy.interpolate as interpolate  # type: ignore


def basis_spline(data, size: int = 100, degree: int = 3, periodic: bool = False):
    """Use B-Splines for interpolation"""
    data = np.asarray(data)
    n_points = len(data)

    if periodic:
        factor, fraction = divmod(n_points + degree + 1, n_points)
        data = np.concatenate((data,) * factor + (data[:fraction],))
        n_points = len(data)
        degree = np.clip(degree, 1, degree)
    else:
        degree = np.clip(degree, 1, n_points - 1)

    knot_vector = None
    if periodic:
        knot_vector = np.arange(0 - degree, n_points + degree + degree - 1, dtype="int")
    else:
        knot_vector = np.concatenate(
            (
                [0] * degree,
                np.arange(n_points - degree + 1),
                [n_points - degree] * degree,
            )
        )

    values = np.linspace(periodic, (n_points - degree), size)

    return np.array(interpolate.splev(values, (knot_vector, data.T, degree))).T


def noisy_basis_spline(
    data, size: int = 100, degree: int = 3, periodic: bool = False, std: float = 1.0
):
    """Generate a noisy B-spline dataset"""
    interpolated = basis_spline(data, size, degree, periodic)
    noise = np.random.normal(0, std, interpolated.shape)
    return interpolated + noise


def interpolate_categorical(
    indices: Union[List[int], List[float]], categories: List[str], size: int
) -> List[str]:
    """Interpolation for categorical variables"""
    func = interpolate.interp1d(
        indices,
        range(len(categories)),
        kind="nearest",
        fill_value=(0, len(categories) - 1),
        bounds_error=False,
    )
    x_new = np.linspace(indices[0], indices[-1], size)
    y_idx: List[float] = func(x_new)
    y_new: List[str] = [categories[int(i)] for i in y_idx]
    return np.vstack((x_new, y_new)).T
