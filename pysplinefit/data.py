"""
.. module:: data
    :platform: Unix, Windows
    :synopsis: Contains high level classes for containing point cloud boundary and surface data

.. moduleauthor:: Sam Potter <spotter1642@gmail.com>
"""

from . import spline
from . import np
from . import knots
from . import parameterize
from . import fitting


class Boundary(spline.Curve):
    """
    Class container for boundary data
    """

    def __init__(self):
        super().__init__()
        self._data = None
        self._start = None
        self._end = None
        self._num_ctrlpts = None
        self._init_curve = None
        self._parameterized_data = None
        self._fit_curve = None

    def __repr__(self):
        return f'{self.__class__.__name__}'

    @property
    def data(self):
        """
        Boundary data points

        :getter: Gets boundary point data
        :type: ndarray
        """
        return self._data

    @data.setter
    def data(self, data_array):
        # Sanitize inputs
        if not isinstance(data_array, np.ndarray):
            try:
                data_array = np.array(data_array)
            except Exception:
                print('Input data is not a numpy array and could not be cast')
                raise

        # Check dimension
        if data_array.ndim != 2:
            raise ValueError('Boundary data array must be 2D')

        # Check that data is either 2D or 3D
        if not (data_array.shape[-1] == 2 or data_array.shape[-1] == 3):
            raise ValueError('Boundary data must be in either R2 or R3')

        self._data = data_array

    @property
    def start(self):
        """
        Boundary data start point

        :getter: Gets curve start point
        :type: ndarray
        """
        return self._start

    @start.setter
    def start(self, point):
        # Sanitize inputs
        if not isinstance(point, np.ndarray):
            try:
                point = np.array(point)
            except Exception:
                print('Start point was not an array and could not be cast')
                raise

        # Check dimension
        if point.ndim != 1:
            raise ValueError('Start point array must be 1D')

        # Check point in 2D or 3D
        if not (len(point) == 2 or len(point) == 3):
            raise ValueError('Start point must be in R2 or R3')

        self._start = point

    @property
    def end(self):
        """
        Boundary data end point

        :getter: Gets curve end point
        :type: ndarray
        """
        return self._end

    @end.setter
    def end(self, point):
        # Sanitize inputs
        if not isinstance(point, np.ndarray):
            try:
                point = np.array(point)
            except Exception:
                print('End point was not an array and could not be cast')
                raise

        # Check dimension
        if point.ndim != 1:
            raise ValueError('End point array must be 1D')

        # Check point in 2D or 3D
        if not (len(point) == 2 or len(point) == 3):
            raise ValueError('End point must be in R2 or R3')

        self._end = point

    @property
    def num_ctrlpts(self):
        """
        Number of control points associated with boundary data curve

        :getter: Get number of control points
        :type: int
        """
        return self._num_ctrlpts

    @num_ctrlpts.setter
    def num_ctrlpts(self, num):
        # Sanitize input
        if not isinstance(num, int):
            try:
                num = int(num)
            except Exception:
                print('Number of control points was not an int and could not be cast')
                raise

        if num <= 3:
            raise ValueError('Number of control points must be 3 or more')

        self._num_ctrlpts = num

    @property
    def init_curve(self):
        """
        Initial curve between start and end points of boundary data


        :getter: Gets initial curve
        :type: spline.Curve()
        """
        return self._init_curve

    def set_init_curve(self):
        """
        Create and set an initial curve based on desired degree of boundary data curve fit
        :return: None
        """
        # Generate instance of curve class
        curve = spline.Curve()

        # Set degree
        curve.degree = self._degree

        # Set control points
        x_vals = np.linspace(self._start[0], self._end[0], self._degree + 1)
        y_vals = np.linspace(self._start[1], self._end[1], self._degree + 1)
        z_vals = np.linspace(self._start[2], self._end[2], self._degree + 1)

        init_ctrlpts = np.column_stack((x_vals, y_vals, z_vals))

        curve.control_points = init_ctrlpts

        # Generate knot vector
        init_knot_vector = knots.generate_uniform(self._degree, len(init_ctrlpts))

        curve.knot_vector = init_knot_vector

        self._init_curve = curve

    @property
    def parameterized_data(self):
        """
        Parameterized data points.

        [X1, X2, X3, u value]

        :getter: Gets parameterized point data
        :type: ndarray
        """
        return self._parameterized_data

    def parameterize(self):
        # Set the initial curve if not set, then parameterize
        if self._init_curve is None and self._fit_curve is None:
            self.set_init_curve()
            parameterized_data = parameterize.parameterize_curve(self._init_curve, self._data)
        # Parameterize to initial curve if not fit performed
        elif self._fit_curve is None:
            parameterized_data = parameterize.parameterize_curve(self._init_curve, self._data)
        # Parameterize to fit curve
        else:
            parameterized_data = parameterize.parameterize_curve(self._fit_curve, self._data)

        self._parameterized_data = parameterized_data

    @property
    def fit_curve(self):
        """
        Fit curve of specified degree and num_ctrlpts to data

        :getter: Gets fit_curve
        """
        return self._fit_curve

    def fit(self, logging=1):
        """
        Fit boundary data with curve.

        Set _final_curve and _parameterized_data properties

        :param logging: Option switch for log level. <=0 silent, =1 normal, >1 debug
        :type logging: int
        :return: None
        """
        # Check if init curve has been created. If not, create it
        if self._init_curve is None:
            self.set_init_curve()

        # Pass initial curve to fitting function
        final_fit = fitting.fit_curve_fixed_num_pts(self._init_curve, self._data, self._num_ctrlpts, logging=logging)

        # Set final curve property
        self._fit_curve = final_fit

        # Parameterize data
        self.parameterize()
