import warnings

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import scipy.odr as sco
from itertools import chain

standardColorsHex = ['#5B84B1FF', '#FC766AFF', '#5F4B8BFF', '#E69A8DFF',
                     '#42EADDFF', '#CDB599FF', '#00A4CCFF', '#F95700FF',
                     '#00203FFF', '#ADEFD1FF', '#F4DF4EFF', '#949398FF',
                     '#ED2B33FF', '#D85A7FFF', '#2C5F2D', '#97BC62FF',
                     '#00539CFF', '#EEA47FFF', '#D198C5FF', '#E0C568FF']
alphabetSequence = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


class DatAn:
    """
    Attributes
        data_length : int
            Number of given data sets.
        function_type : str
            The specific function used for fitting (only available for predefined functions).
        x_error : list
            Input x errors for all data.
        y_error : list
            Input y errors for all data.
        x_error_est : list
            Estimated x errors by odr (only available when using odr).
        y_error_est : list
            Estimated y errors by odr (only available when using odr).
        constants : list
            Fitted constants for the provided function.
        covariance : list
            2D list of the covariance for the fitted constants.
        deviations : list
            Standard deviation for the fitted constants.
        x_list : list
            Provided x values packed into a list if not already.
        y_list : list
            Provided y values packed into a list if not already.
        function : function
            Specific function used for fitting.
        x_min : float
            The absolute minimum value of all x values given.
        x_max : float
            The absolute maximum value of all x values given.
        plot() : function
            Plots the given data along with a fit with standardized params if none given with matplotlib.

    """
    def __init__(self, x_data, y_data, func, g_list, method='curve_fit', **kwargs):
        """

        Parameters
            x_data : list
                x data for analysis. Can either be a single list or a list of lists (multiple data sets).
            y_data : list
                y data for analysis. Can either be a single list or a list of lists (multiple data sets). Must
                correspond in length to x data
            func : function or str
                Provided x and y data is fitted to this function. Note that if the method curve_fit is used, this must
                have x variable as first entry, and constants must not be returned as list element. The opposite is true
                if odr method is chosen. This can also be a str, in which case the provided string must correspond to
                one of the predefined functions: linear.
            g_list : list
                Guesses for the constants of the provided function.
            method : str, optional
                Fit method. Supported: curve_fit and odr. The default is curve_fit.

        Keyword Arguments
            x_err : list or float
                Errors of the input x values
            y_err : list or float
                Errors of the input y values
            odr_print : bool
                If set to True, runs the .pprint() from the odr
        """
        # check whether x-list data is of correct shape, otherwise try to fix, if fail, raise error
        if not isinstance(x_data, (list, np.ndarray)):  # check if x-list is a list
            raise ValueError('x-list must be a list or numpy.ndarray.')
        if (any(isinstance(i, (list, np.ndarray)) for i in x_data) and
                any(isinstance(i, (float, int, np.integer)) for i in x_data)):  # check if x-list is list of lists
            raise ValueError(
                'x-list must be list of lists or list of values.')
        if not all(isinstance(i, (list, np.ndarray)) for i in x_data):  # check if no list is inside x-list
            x_list_fix = [x_data]  # if true, make x-list a list of lists
        else:
            x_list_fix = x_data  # else, define x-list as is

        # check whether y-list data is of correct shape, otherwise try to fix, if fail, raise error
        if not isinstance(y_data, (list, np.ndarray)):  # check if y-list is a list
            raise ValueError('y-list must be a list or numpy.ndarray.')
        if (any(isinstance(i, (list, np.ndarray)) for i in y_data) and
                any(isinstance(i, (float, int, np.integer)) for i in y_data)):  # check if y-list is list of lists
            raise ValueError(
                'y-list must be list of lists or list of values.')
        if not all(isinstance(i, (list, np.ndarray)) for i in y_data):  # check if no list is inside y-list
            y_list_fix = [y_data]  # if true, make y-list a list of lists
        else:
            y_list_fix = y_data  # else, define y-list as is

        # define the numbner of lists in the x-list (serving as the number of data sets packaged in the class call)
        self.data_length = len(x_list_fix)

        # define empty lists for fitted constants and lists to be appended to
        popts, pcovs, pstds = [], [], []
        if method == 'curve_fit':
            if func in ('lin', 'linear', 'linfit', 'linreg'):
                def func(x, a, b):
                    return a * x + b
                self.function_type = 'a * x + b'
            for xs, ys in zip(x_list_fix, y_list_fix):
                popt_temp, pcov_temp = curve_fit(f=func, xdata=xs, ydata=ys, p0=g_list, absolute_sigma=True)
                pstd_temp = list(np.sqrt(np.diag(pcov_temp)))

                popts.append(popt_temp)
                pcovs.append(pcov_temp)
                pstds.append(pstd_temp)

        elif method == 'odr':
            est_x_err, est_y_err = [], []
            if func in ('lin', 'linear', 'linfit', 'linreg'):
                def func(b, x):
                    return b[0] * x + b[1]

                self.function_type = 'B[0] * x + B[1]'
            if 'x_err' in kwargs.keys():
                x_err = kwargs.get('x_err')
                if isinstance(x_err, (int, float)):
                    self.x_error = [x_err] * self.data_length
                else:
                    self.x_error = x_err
                # if isinstance(x_err, (list, np.ndarray)) and len(x_err) != self.data_length:
                #     raise ValueError('Length of x_err and x_list does not match.')
            else:
                x_err = None
            if 'y_err' in kwargs.keys():
                y_err = kwargs.get('y_err')
                if isinstance(y_err, (int, float)):
                    self.y_error = [y_err] * self.data_length
                else:
                    self.y_error = y_err
            else:
                y_err = None
            for xs, ys, xerrs, yerrs in zip(x_list_fix, y_list_fix, x_err, y_err):
                odr_fit_function = sco.Model(func)  # define odr model
                odr_data = sco.RealData(xs, ys, sx=xerrs, sy=yerrs)  # define odr data
                odr_setup = sco.ODR(odr_data, odr_fit_function, beta0=g_list)  # define the ODR itself
                odr_out = odr_setup.run()  # run the ODR

                if 'odr_print' in kwargs.keys() and kwargs.get('odr_print'):  # provide odr.pprint() option
                    odr_out.pprint()

                popts.append(odr_out.beta)
                pcovs.append(odr_out.cov_beta)
                pstds.append(odr_out.sd_beta)
                est_x_err.append(odr_out.delta)
                est_y_err.append(odr_out.eps)

            self.x_error_est = est_x_err
            self.y_error_est = est_y_err
        else:
            raise ValueError(f'Passed method, {method}, is not supported.')

        # these will be sorted per data set
        self.constants = popts
        self.covariance = pcovs
        self.deviations = pstds

        # x- and y-list values for both plot and data
        self.x_list = x_list_fix
        self.y_list = y_list_fix
        self.function = func

        # flatten x-list to find absolute minimum and absolute maximum for given data
        x_list_chained = list(chain.from_iterable(x_list_fix))
        self.x_min = min(x_list_chained)
        self.x_max = max(x_list_chained)

        self.__fit_type__ = method

    def plot(self, **kwargs):
        """

        Keyword Arguments
            f_num : int
                Set the frame number for the found fits. The default is 300.
            extrp : float or list
                Extrapolate fitted x and y lists. If a value is given, it is determined whether it is a minimum or
                maximum extrapolation, if list then the first element will be minimum and the second element the
                maximum.
            xlab : str
                Set label for horizontal axis.
            ylab : str
                Set label for vertical axis.
            dlab : list
                Labels for data points, thus a list of strings. If none is set, default to abc typesetting with fit
                subscript.
            dcol : list
                Colors for the data points of the plot along with the fits. Length must be mathing with either data sets
                or data sets with fit.
            mkz : list
                Marker size for the input data points.
            lw : list
                Line width for the found data fits.
            ls : list
                Set the line style of the fits.
            mks : list
                Marker style for the input data points.
            x_lim : list
                Set the limits of the horizontal axis.
            y_lim : list
                Set the limits of the vertical axis.
            x_scale : str or int
                Set the scale of the horizontal axis, according to the matplotlib scale nomeclature.
            y_scale : str or int
                Set the scale of the vertical axis, according to the matplotlib scale nomeclature.
            leg_size : float
                Set the size of the lengend panel.
            leg_log : str or int
                Set the position of the legend panel according to the matplotlib nomeclature.
            dpi : int
                Set dpi for plot.
            capsize : float
                Define cap size of the data errors.
            elinewidth : float
                Define width of the error lines for the data errors.
            errors : str
                Set whether displayed data error should be the input data error or output data error. That is the
                computed data error (only relavant for odr fit). The default is input.
            fit_err : bool
                Set whether uncertainties for the fits should be plotted. The default is True.
            axis : int
                Set whether plot should have axis marked. Three different styles: 0, 1, 2. The default is None.


        Returns
            Matplotlib plot with the passed params.

        """
        # redefine the data size from self
        data_length = self.data_length

        # define frame number if not in kwargs
        if 'f_num' in kwargs.keys():
            frame_number = kwargs.get('f_num')
        else:
            frame_number = 300

        # checking for extrapolation and extrapolation type. Note that if extrapolation is set, all data fits will be
        #   extrapolated to at least either the absolute minimum and maximum of the given x-data, along with the set
        #   either minumum or maximum.
        if 'extrp' in kwargs.keys():
            extrp = kwargs.get('extrp')
            if isinstance(extrp, (int, float)):  # if numeric value, check if given value is max or min
                if extrp < self.x_min:
                    x_min = extrp
                    x_max = self.x_max
                elif extrp > self.x_max:
                    x_min = self.x_min
                    x_max = extrp
                else:  # if the extrapolation is inside the x data set, raise error
                    raise ValueError('Use list to extrapolate inside data set.')
            elif isinstance(extrp, (list, np.ndarray)) and len(extrp) == 2:
                x_min = extrp[0]
                x_max = extrp[1]
            else:
                raise ValueError('Extrapolation must be of type int, float or list.')
            x_list_fit = [np.linspace(x_min, x_max, frame_number)] * data_length
        else:
            # if no extrapolation is made, find the minimum and maximum for each of the given x-data sets
            x_min_temp = [min(i) for i in self.x_list]
            x_max_temp = [max(i) for i in self.x_list]
            x_list_fit = [np.linspace(i, j, frame_number) for i, j in zip(x_min_temp, x_max_temp)]

        if self.__fit_type__ == 'curve_fit':
            y_list_fit = [self.function(x_list_fit[j], *[i for i in self.constants[j]]) for j in range(data_length)]
            try:  # check if passed function in class matches what curve_fit expects
                len(y_list_fit[0])
            except TypeError:
                raise RuntimeError('Plotting failed. Given function type may not work with curve_fit as intended, '
                                   'variables must not be packed into list. Check scipy.optimize.curve_fit for more '
                                   'details.')
        elif self.__fit_type__ == 'odr':
            y_list_fit = [self.function([i for i in self.constants[j]], x_list_fit[j]) for j in range(data_length)]

        # define x- and y-lists for plotting
        xs_plot = self.x_list + x_list_fit
        ys_plot = self.y_list + y_list_fit

        # define auto-coloring list if no colors are given
        if 'dcol' in kwargs.keys():
            data_colors = kwargs.get('dcol')
            if len(data_colors) == data_length:
                color_match_list = data_colors * 2
            elif len(data_colors) == data_length * 2:
                color_match_list = data_colors
            else:
                warnings.warn(
                    f'Color list length ({len(data_colors)}) does not match the data ({data_length}) or data and fit '
                    f'length ({data_length * 2}), reverting to standard colors.', stacklevel=2)
                color_match_list = standardColorsHex[0:data_length] * 2
        else:
            color_match_list = standardColorsHex[0:data_length] * 2

        # define standard plot params from kwargs and error handling

        # label parameters
        if 'xlab' in kwargs.keys():  # label for horizontal axis
            x_lab = kwargs.get('xlab')
        else:
            x_lab = None
        if 'ylab' in kwargs.keys():  # label for vertical axis
            y_lab = kwargs.get('ylab')
        else:
            y_lab = None
        if 'dlab' not in kwargs.keys():  # labels for data points
            data_labels = [r'$' + f'{i}' + r'_{dat}$' for i in alphabetSequence[0:data_length]] + [
                r'$' + f'{i}' + r'_{fit}$' for i in alphabetSequence[0:data_length]]
        else:
            if not isinstance(kwargs.get('dlab'), (list, np.ndarray)):  # error if not a list/array of labels are given
                raise ValueError('Data labels must be packed in type list.')
            elif len(kwargs.get('dlab')) not in (data_length, data_length * 2):  # error if not enough labels given
                raise ValueError('Data label list must match data sets.')
            else:
                if len(kwargs.get('dlab')) == data_length:  # auto generate fit labels if data labels are given
                    data_labels = kwargs.get('dlab') + [f'{i}' + r'$_{fit}$' for i in kwargs.get('dlab')]
                else:
                    data_labels = kwargs.get('dlab')

        # graph/data/plot params
        if 'mkz' not in kwargs.keys():
            marker_size_values = [2] * data_length + [0] * data_length
        else:
            if isinstance(kwargs.get('mkz'), str):
                try:
                    float(kwargs.get('mkz'))
                except ValueError:
                    raise ValueError('Marker size must be numerical.')
            elif not isinstance(kwargs.get('mkz'), (list, np.ndarray)):
                marker_size_values = [kwargs.get('mkz')] * data_length + [0] * data_length
            else:
                if len(kwargs.get('mkz')) != data_length:
                    raise ValueError('Marker list length must match data sets.')
                else:
                    marker_size_values = kwargs.get('mkz') + [0] * data_length
        if 'lw' not in kwargs.keys():
            line_width_values = [0] * data_length + [1] * data_length
        else:
            if isinstance(kwargs.get('lw'), str):
                try:
                    float(kwargs.get('lw'))
                except ValueError:
                    raise ValueError('Line width must be numerical.')
            elif not isinstance(kwargs.get('lw'), (list, np.ndarray)):
                line_width_values = [0] * data_length + [kwargs.get('lw')] * data_length
            else:
                if len(kwargs.get('lw')) != data_length:
                    raise ValueError('Line width list length must match data sets.')
                else:
                    line_width_values = [0] * data_length + kwargs.get('lw')
        if 'ls' in kwargs.keys():
            line_style_temp = kwargs.get('ls')
            if len(line_style_temp) == data_length:
                line_style = line_style_temp * 2
            elif len(line_style_temp) == data_length * 2:
                warnings.warn(f'Only a list length corresponding to the amount of fits ({data_length}) is needed.')
                line_style = line_style_temp
            else:
                warnings.warn(
                    f'Line style list length ({len(line_style_temp)}) does not match the data ({data_length}) or data '
                    f'and fit length ({data_length * 2}), reverting to standard colors.', stacklevel=2)
                line_style = ['solid'] * data_length * 2
        else:
            line_style = ['solid'] * data_length * 2
        if 'mks' not in kwargs.keys():
            marker_style_values = ['o'] * data_length * 2
        else:
            if isinstance(kwargs.get('mks'), str):
                marker_style_values = [kwargs.get('mks')] * data_length * 2
            elif isinstance(kwargs.get('mks'), (list, np.ndarray)) and len(
                    kwargs.get('mks')) == data_length:
                marker_style_values = kwargs.get('mks')
            else:
                raise ValueError('Marker style list length must match data sets.')
        if 'dpi' not in kwargs.keys():
            set_dpi = 300
        else:
            dpi = kwargs.get('dpi')
            if isinstance(dpi, str):
                try:
                    set_dpi = float(dpi)
                except ValueError:
                    raise ValueError('dpi must be numeric.')
            else:
                set_dpi = dpi

        fig = plt.figure(dpi=set_dpi, figsize=(6, 2.5))
        ax = fig.add_subplot(111)

        if self.__fit_type__ == 'curve_fit':
            plot_keys = (xs_plot, ys_plot, color_match_list, line_width_values, marker_size_values, marker_style_values,
                         data_labels, line_style)
            for x, y, colm, lwidth, mksize, mlstyle, dlbs, ls in zip(*plot_keys):
                ax.plot(x, y, c=colm, linewidth=lwidth, markersize=mksize, marker=mlstyle, label=dlbs, linestyle=ls)
        elif self.__fit_type__ == 'odr':
            # error params
            if 'capsize' in kwargs.keys():
                cap_size = kwargs.get('capsize')
            else:
                cap_size = 0
            if 'elinewidth' in kwargs.keys():
                e_line_width = kwargs.get('elinewidth')
            else:
                e_line_width = 1

            if 'errors' in kwargs.keys():
                error_type = kwargs.get('errors')
                if error_type in ('input', 'true') and self.x_error and self.y_error:
                    x_errors = self.x_error + [None] * data_length
                    y_errors = self.y_error + [None] * data_length
                elif error_type in ('estimated', 'est', 'output'):
                    x_errors = self.x_error_est + [None] * data_length
                    y_errors = self.y_error_est + [None] * data_length
                else:
                    raise ValueError('error_type is invalid.')
            else:
                x_errors = self.x_error_est + [None] * data_length
                y_errors = self.y_error_est + [None] * data_length

            # key packaging
            plot_keys = (xs_plot, ys_plot, color_match_list, line_width_values, marker_size_values, marker_style_values,
                         data_labels, x_errors, y_errors, line_style)

            # plotting loop
            for x, y, colm, lwidth, mksize, mlstyle, dlbs, xr, yr, ls in zip(*plot_keys):
                ax.errorbar(x, y, xerr=xr, yerr=yr, c=colm, linewidth=lwidth, markersize=mksize, label=dlbs,
                            elinewidth=e_line_width, capsize=cap_size, marker=mlstyle, linestyle=ls)

            if 'fit_err' not in kwargs.keys() or ('fit_err' in kwargs.keys() and kwargs.get('fit_err')):
                y_fit_err = [[self.function([k + h for k, h in zip(i, j)], l),
                              self.function([k - h for k, h in zip(i, j)], l)]
                             for i, j, l in zip(self.constants, self.deviations, x_list_fit)]
                for x, yr in zip(x_list_fit, y_fit_err):
                    ax.fill_between(x, *yr, alpha=.2, color='silver')
        ax.set_xlabel(x_lab)
        ax.set_ylabel(y_lab)

        # set axis params/scaling
        if 'x_scale' in kwargs.keys():
            ax.set_xscale(kwargs.get('x_scale'))
        if 'y_scale' in kwargs.keys():
            ax.set_xscale(kwargs.get('y_scale'))
        if 'x_lim' in kwargs.keys():
            plt.xlim(*kwargs.get('x_lim'))
        if 'y_lim' in kwargs.keys():
            plt.xlim(*kwargs.get('y_lim'))
        if 'ttl' in kwargs.keys():
            ax.set_title(kwargs.get('ttl'))

        # define different standard axis types to choose between. Note that there is only the option between showing
        #   no axis or both axis.
        if 'axis' in kwargs.keys():
            axis = kwargs.get('axis')
            if axis == 0:
                ax.axhline(y=0, xmin=0, xmax=1, color='black', linestyle='solid', linewidth=0.5, alpha=1)
                ax.axvline(x=0, ymin=0, ymax=1, color='black', linestyle='solid', linewidth=0.5, alpha=1)
            elif axis == 1:
                ax.axhline(y=0, xmin=0, xmax=1, color='black', linestyle='dashed', linewidth=1, alpha=0.5)
                ax.axvline(x=0, ymin=0, ymax=1, color='black', linestyle='dashed', linewidth=1, alpha=0.5)
            elif axis == 2:
                ax.axhline(y=0, xmin=0, xmax=1, color='black', linestyle='dotted', linewidth=1, alpha=1)
                ax.axvline(x=0, ymin=0, ymax=1, color='black', linestyle='dotted', linewidth=1, alpha=1)

        plt.tight_layout()

        # set legend params
        if 'leg_size' in kwargs.keys():
            legend_size = kwargs.get('leg_size')
        else:
            legend_size = 8
        if 'leg_loc' in kwargs.keys():
            legend_loc = kwargs.get('leg_loc')
        else:
            legend_loc = 'best'
        ax.legend(fontsize=legend_size, loc=legend_loc)
        plt.rcParams.update({'font.family': 'Times New Roman'})
        plt.show()
