"""Tool to create test PMML models"""
# INFO: Tool to create test PMML models
# pylint: disable=R0903,R0913,C0103
from abc import ABC, abstractmethod
import numpy as np  # type: ignore
from scipy import interpolate  # type: ignore
from flask import Flask, request, make_response, jsonify
import pandas as pd  # type: ignore


def create_continuous_series(start: int, end: int, data, size: int, noise: float = 0.0):
    """Create a continuous series"""
    x = [p[0] for p in data]
    y = [p[1] for p in data]

    f = interpolate.interp1d(x, y, fill_value="extrapolate", kind="cubic")

    xnew = np.linspace(start, end, size)
    ynew = f(xnew)
    result = np.empty([size, 2])
    result[:, 0] = xnew
    result[:, 1] = ynew

    if noise > 0.0:
        noise_values = np.random.normal(loc=0.0, scale=noise, size=size)
        result[:, 1] += noise_values

    return result


def create_discrete_series(start: int, end: int, data, size: int, noise: float = 0.0):
    """Create a discrete series"""
    result = create_continuous_series(
        start=start, end=end, data=data, size=size, noise=noise
    )
    result[:, 1] = result[:, 1].astype(int)

    return result


def create_categorical_series(data, size: int, noise: float = 0.0):
    """Create a categorical series"""
    x = [p[0] for p in data]
    y = [p[1] for p in data]

    func = interpolate.interp1d(
        x,
        range(len(y)),
        kind="nearest",
        fill_value=(0, len(y) - 1),
        bounds_error=False,
    )

    xnew = np.arange(size)
    yidx = func(xnew)

    n_unique = len(set(y))

    def _bound(x):
        """Check if the varible is out of bounds"""
        if x > n_unique - 1:
            return n_unique - 1
        if x < 0:
            return 0
        return x

    if noise > 0.0:
        noise_values = np.random.normal(loc=0.0, scale=noise, size=size)
        yidx += noise_values
        yidx = np.array([_bound(x) for x in yidx])

    ynew = [data[int(i)][1] for i in yidx]
    return np.vstack((xnew, ynew)).T


class Variable(ABC):
    """Variable abstract class"""

    def __init__(self, name, size, points, noise):
        self.name = name
        self.points = points
        self.size = size
        self.noise = noise

    @abstractmethod
    def generate_data(self):
        """Generate the data associated with this variable"""


class ContinuousVariable(Variable):
    """Continuous variable"""

    def __init__(self, name, size, points, noise, start, end):
        super().__init__(name, size, points, noise)
        self.start = start
        self.end = end

    def generate_data(self):
        return create_continuous_series(
            start=self.start,
            end=self.end,
            data=self.points,
            size=self.size,
            noise=self.noise,
        )

    def __repr__(self):
        return f"""ContinuousVariable{{
            name={self.name}, start={self.start}, end={self.end}, size={self.size}, noise={self.noise}
            }}"""


class DiscreteVariable(Variable):
    """Continuos variable"""

    def __init__(self, name, size, points, noise, start, end):
        super().__init__(name, size, points, noise)
        self.start = start
        self.end = end

    def generate_data(self):
        return create_discrete_series(
            start=0, end=0, data=self.points, size=1000, noise=self.noise
        )

    def __repr__(self):
        return f"""DiscreteVariable{{
            name={self.name}, start={self.start}, end={self.end}, size={self.size}, noise={self.noise}
            }}"""


class CategoricalVariable(Variable):
    """Continuos variable"""

    def generate_data(self):
        return create_categorical_series(data=self.points, size=1000, noise=self.noise)

    def __repr__(self):
        return f"CategoricalVariable{{name={self.name}, size={self.size}, noise={self.noise}}}"


# Model generation


def generate_linear_regression(inputs):
    """Generate a linear regression from the supplied variables"""
    data = pd.DataFrame()
    for variable in inputs:
        # drop indices
        data[variable.name] = variable.generate_data()[:, 1]
    # encode categorical variables

    print(data)


# REST server
app = Flask(__name__)


@app.route("/model", methods=["POST"])
def model():
    """Model endpoint"""
    content = request.json
    data_size = int(content["data"]["size"])
    print(content)
    # get inputs
    variables = []
    for variable in content["data"]["inputs"]:
        print(variable)
        name = variable["name"]
        points = variable["points"]
        noise = variable.get("noise", 0.0)
        variable_type = variable["type"]
        if variable_type != "categorical":
            start = variable.get("start", min([p[0] for p in points]))
            end = variable.get("end", max([p[0] for p in points]))

        if variable_type == "continuous":
            variable_obj = ContinuousVariable(
                name=name,
                start=start,
                end=end,
                size=data_size,
                points=points,
                noise=noise,
            )
        elif variable_type == "discrete":
            variable_obj = DiscreteVariable(
                name=name,
                start=start,
                end=end,
                size=data_size,
                points=points,
                noise=noise,
            )
        elif variable_type == "categorical":
            variable_obj = CategoricalVariable(
                name=name,
                size=data_size,
                points=points,
                noise=noise,
            )

        variables.append(variable_obj)
    generate_linear_regression(variables)

    return make_response(jsonify({"data": [1]}), 200)


if __name__ == "__main__":
    app.run()
