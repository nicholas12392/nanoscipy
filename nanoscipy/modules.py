import warnings

import matplotlib.pyplot as plt
import mpmath
import numpy as np
import scipy.optimize as spo
from scipy.optimize import curve_fit
import scipy.odr as sco
from itertools import chain
import nanoscipy.mathpar as nsp
import nanoscipy.util as nsu
import scipy.constants as spc
import nanoscipy.unitpar as nup


class DatAn:
    """
    Class that can determine fit via either curve_fit or odr, plot the result, and perform mathematical operations on
    the resulting fit.

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
        mathop() : function
            Performs a mathematical operation on the found fit for all fitted functions.

    """

    def __init__(self, x_data, y_data, func, g_list, method='curve_fit', **kwargs):
        # check whether x-list data is of correct shape, otherwise try to fix, if failed, py dim error is raised
        #   first check whether the x_data and y_data has same dimensions
        if len(x_data) == len(y_data) and np.array(x_data).shape == np.array(y_data).shape:
            try:  # if they do, try to convert all data to a list, if data is list of lists
                x_list_fix = [[i for i in j] for j in x_data]
            except TypeError:  # if data is a list of floats pack list into list
                x_list_fix = [[i for i in x_data]]
        else:
            x_list_fix = [[i for i in x_data]] * len(y_data)  # if x and y data have different dimensions, try convert

        # check whether y-list data is of correct shape, otherwise try to fix, if failed, py dim error is raised
        try:  # try to convert all data to a list, if data is list of lists
            y_list_fix = [[i for i in j] for j in y_data]
        except TypeError:  # if data is a list of floats pack list into list
            y_list_fix = [[i for i in y_data]]

        # define the number of lists in the x-list (serving as the number of data sets packaged in the class call)
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
                x_err = [None] * self.data_length
            if 'y_err' in kwargs.keys():
                y_err = kwargs.get('y_err')
                if isinstance(y_err, (int, float)):
                    self.y_error = [y_err] * self.data_length
                else:
                    self.y_error = y_err
            else:
                y_err = [None] * self.data_length
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

    def mathop(self, operation, exp_val=1, sec_opr=None, oprint='all'):
        """
        Performs a mathematical operation on the fitted function(s).

        Parameters
            operation : str
                Perform set operation on the fitted function. Supported operations are: roots, yintercept.
            exp_val : float or list, optional
                Set an expected value for the operation. This may not be needed, but some operations utilize
                scipy.optimize.fsolve, where it is required. Therefore, if multiple results are expected, this may be a 
                list of lists. The default is 1.
            sec_opr : str, optional
                Perform a secondary operation on the primary operation. This type is denoted as a string, with the 
                primary operation denoted as 'x', e.g., 'x^-1'. Supported operations: '^', '*', '/', '+', '-', 'ln',
                'log' (this is log10), 'exp', 'sin', 'cos', 'tan', 'pi'. The default is None.
            oprint : str, optional
                Print the results from the operation. If 'all', print results for operation on all fitted functions.
                Else, has to be a string containing the data label of the particular graph (set in .plot). The default
                is 'all'.

        Return
            oprRes : list
                Depending on the operation this may be a list of numpy arrays or a list of values.
        """

        # define variables for easy utilization
        varConstants = self.constants
        dataLength = len(varConstants)
        fitType = self.__fit_type__
        functionType = self.function

        # set expected values
        try:
            if len(exp_val) == dataLength:
                expVal = exp_val
            else:
                raise ValueError(f'Amount of expected values, {len(exp_val)}, must equal amount of data sets, '
                                 f'{dataLength}.')
        except TypeError:
            expVal = [exp_val] * dataLength

        # fix function depending on whether it is coming from curve_fit or odr
        def __function_fixer__(x, variables):
            if fitType == 'curve_fit':
                return functionType(x, *variables)
            elif fitType == 'odr':
                return functionType(variables, x)

        # perform operations for all fitted functions
        if operation in ('yintercept', 'y_intercept', 'yinter'):
            oprResPre = [__function_fixer__(0, i) for i in varConstants]
        elif operation in ('xintercept', 'root', 'roots', 'x_intercept', 'xinter'):
            oprResPre = [spo.fsolve(__function_fixer__, i, tuple([j])) for i, j in zip(expVal, varConstants)]
        else:
            raise TypeError(f'Operation, {operation}, is invalid.')

        # perform secondary operation if any is given
        if sec_opr:
            decomposed_sec_opr = [i for i in sec_opr]  # decompose string into list
            prim_opr_id = nsu.find(decomposed_sec_opr, 'x')  # find indexes for 'x'

            # determine whether the found 'x' is part of 'exp'
            fixed_opr_id = []
            for i in prim_opr_id:
                ip1 = im1 = None
                try:
                    ip1 = decomposed_sec_opr[i + 1]
                except IndexError:
                    pass
                try:
                    im1 = decomposed_sec_opr[i - 1]
                except IndexError:
                    pass

                if im1 != 'e' and ip1 != 'p':
                    fixed_opr_id.append(i)

            # replace 'x' with the primary operation result
            replaced_decom_string = [
                [[k if i in fixed_opr_id else j for i, j in nsu.indexer(decomposed_sec_opr)] for
                 k in l] for l in oprResPre]

            # convert list back to a string, and execute operations in parser
            oprRes = [[nsp.parser(nsu.list_to_string(j)) for j in i] for i in replaced_decom_string]
            finalOperation = nsu.list_to_string([operation if i in fixed_opr_id else e for i, e in
                                                 nsu.indexer(decomposed_sec_opr)])
        else:
            finalOperation = operation
            oprRes = oprResPre

        # print results if oprint is set to valid value
        #   first, check if custom data labels have been defined from .plot()

        # define list of the standard labels, corresponding to fed data sets
        standardLabels = nsu.alphabetSequence[0:dataLength]

        try:
            dataLabels = self.__data_labels__
            all_labels = dataLabels
        except AttributeError:
            dataLabels = []
            all_labels = standardLabels

        # determine what to print, and check if passed oprint is valid
        if not oprint:
            pass
        else:
            print(f':::Result from operation: {finalOperation}:::')
            if oprint == 'all':
                for i, j in zip(all_labels, oprRes):  # iterate through all computations and print
                    print(f'{i}): {j}')
            elif nsu.elem_checker(nsu.nest_checker(oprint), [standardLabels, dataLabels])[0]:
                # else find selected values and display those only, sorted by lowest index
                unsorted_values, unsorted_indexes = nsu.elem_checker(nsu.nest_checker(oprint),
                                                                     [dataLabels, standardLabels], overwrite=True)
                sorted_values = [v for i, v in sorted(zip(unsorted_indexes, unsorted_values))]
                sorted_indexes = [i for i, v in sorted(zip(unsorted_indexes, unsorted_values))]
                for i, j in zip(sorted_values, sorted_indexes):
                    print(f'{i}): {oprRes[j]}')
            else:
                raise ValueError(f'There is no corresponding function/graph \'{oprint}\'.')
        return oprRes

    def locate(self, x, oprint='all'):
        """
        Locate the corresponding y-value, for an input x value, for all fitted functions.

        Parameters
            x : float or list
                Locate y-value based on this value.
            oprint: str, optional
                Print the results from the operation. If 'all', print results for operation on all fitted functions, if
                a letter, print result for that particular fitted function, else does not print. Note that if the
                functions has customized labels, these can be called as well to specify. The default is 'all'.

        Return
            locValue : list
                The resulting y-values.
        """

        varConstants = self.constants
        dataLength = len(varConstants)
        fitType = self.__fit_type__
        functionType = self.function

        # check dimensions for x's, and fix to list
        try:
            position = [i for i in x]
        except TypeError:
            position = [x]

        # locate values depending on which function type is used
        if fitType == 'curve_fit':
            locVal = [[functionType(i, *j) for i in position] for j in varConstants]
        elif fitType == 'odr':
            locVal = [[functionType(j, i) for i in position] for j in varConstants]
        else:
            raise ValueError(f'Fit-type undefined: \'{fitType}\'')

        # print results if oprint is set to valid value
        #   first, check if custom data labels have been defined from .plot()

        # define list of the standard labels, corresponding to fed data sets
        standardLabels = nsu.alphabetSequence[0:dataLength]

        try:
            dataLabels = self.__data_labels__
            all_labels = dataLabels
        except AttributeError:
            dataLabels = []
            all_labels = standardLabels

        # determine what to print, and check if passed oprint is valid
        if not oprint:
            pass
        else:
            print(f':::Located y-values from x-values: {x}:::')
            if oprint == 'all':
                for i, j in zip(all_labels, locVal):
                    print(f'{i}): {j}')
            elif nsu.elem_checker(nsu.nest_checker(oprint), [standardLabels, dataLabels])[0]:
                unsorted_values, unsorted_indexes = nsu.elem_checker(nsu.nest_checker(oprint),
                                                                     [dataLabels, standardLabels], overwrite=True)
                sorted_values = [v for i, v in sorted(zip(unsorted_indexes, unsorted_values))]
                sorted_indexes = [i for i, v in sorted(zip(unsorted_indexes, unsorted_values))]
                for i, j in zip(sorted_values, sorted_indexes):
                    print(f'{i}): {locVal[j]}')
            else:
                raise ValueError(f'There is no corresponding function/graph \'{oprint}\'.')
        return locVal

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
            save_to : str
                String with a path and filename to save figure to.


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
                color_match_list = nsu.standardColorsHex[0:data_length] * 2
        else:
            color_match_list = nsu.standardColorsHex[0:data_length] * 2

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
            data_labels = [r'$' + f'{i}' + r'_{dat}$' for i in nsu.alphabetSequence[0:data_length]] + [
                r'$' + f'{i}' + r'_{fit}$' for i in nsu.alphabetSequence[0:data_length]]
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
            self.__data_labels__ = data_labels

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
        if 'save_to' in kwargs.keys():  # if save_to key, save to that path
            save_to = kwargs.get('save_to')
            plt.savefig(save_to, dpi=set_dpi)
        plt.show()


class NumAn:
    """
    This class acts as a numerical calculator, in which one may define constants and use them for computations.

    Parameters
        cons : str, optional
            Constants are defined here, either in the format 'x = 3, y = 1/2' or 'x : 3; y : 1/2' (or any mixture of
            the two types). The same natural constants supported in mathpar.parser() are supported. The default is None.
        unit_identifier : str, optional
            A prefix of sorts that is used to indicate, when a combination of letters should be interpreted as a unit.
            The default is ' '.
        units : bool, optional
            This will force the module to use no units if set to False. This mainly affects natural constants, as these
            will otherwise be used with units. The default is True.
        cprint : str, optional
            This will set the global printing method for all .calc() instances. There are six
                options: 'num' will display input string with constants replaced with values, 'sym' will display input
                string with constants as symbols, 'symc' has same functionality as the latter, but also prints the
                given constants, 'sym_ex' and 'symc_ex' will do the same as the respective options mentioned, but with
                the multiplication as explicit, False will disable result print. The default is inherited from
                'symc_ex'.
        sf : int, optional
            Sets the significant figures for all displayed calculations and constants from the cprint. If None, no
            change to the significant figures is made. The default is 4.

    Attributes
        ans : float
            Gives the result from the previous computation when called.
        add_cns() : function
            Adds a constant to the class, which may be used in calculations. Note importantly, for this attribute,
            constants that have already been defined either in init or previous add_cns() instances may be used.
        calc() : function
            Takes a mathematical expression and computes it via mathpar.parser(). Pre-defined constants are meant to be
            used here.
        add_res() : function
            Adds the previously computed result via calc() as a constant with the given name.
        del_cns() : function
            Deletes specified constants.
        constants() : function
            Displays all the currently defined constants.
    """

    def __init__(self, cons=None, unit_identifier=' ', units=True, cprint='symc_ex', sf=4):

        # define lists mapping constant keys and constant values
        con_vals, con_keys, con_disp = [], [], []
        if cons:
            for k in [h.replace('=', ':').split(':') for h in nsu.replace(';', ',', cons).split(',')]:
                con_keys.append(k[0].replace(' ', ''))
                cur_val = k[1]
                if cur_val[0] == '(' and cur_val[-1] == ')':  # ensure that no parentheses doubles are inserted
                    con_vals.append(cur_val)
                    con_disp.append(cur_val[1:-1])
                else:
                    con_vals.append('(' + cur_val + ')')
                    con_disp.append(cur_val)

        # define constant exclusions, which cannot be replaced as a constant
        function_exclusions = ('pi', 'sinh(', 'cosh(', 'tanh(', 'exp(', 'sin(', 'cos(', 'tan(', 'ln(', 'rad(',
                               'deg(', 'log(', 'sqrt(', 'arcsin(', 'arccos(', 'arctan(', 'arcsinh(', 'arccosh(',
                               'arctanh(')
        # first define which units are to be used for natural constants depending on 'units'
        supported_physical_constants = ('_hbar', '_NA', '_c', '_h', '_R', '_k', '_e', '_me', '_mp')
        scipy_values = (spc.hbar, spc.N_A, spc.c, spc.h, spc.R, spc.k, spc.e, spc.electron_mass, spc.proton_mass)
        if units:
            physical_constants_values = []
            physical_constants_SI_units = ('J*Hz^-1', 'mol^-1', 'm*s^-1', 'J*s', 'J*mol^-1*K^-1', 'J*K^-1', 'C', 'kg',
                                           'kg')
            physical_constants_SI_units_uid = [nsu.list_to_string([unit_identifier + j for j in nsu.split(i, '*')
                                                                   if j != '*']) for i in physical_constants_SI_units]
            for i, j in zip(scipy_values, physical_constants_SI_units_uid):
                physical_constants_values.append('(' + str(i) + j + ')')
        else:
            physical_constants_values = [str(i) for i in scipy_values]

        # define list of supported units (this needs to match the supported units in
        supported_base_units = (
            's', 'm', 'g', 'A', 'K', 'mol', 'N', 'C', 'kat', 'Hz', 'Bq', 'J', 'Pa', 'W', 'Gy', 'Sv', 'V',
            'Wb', 'Ω', 'F', 'S', 'H', 'T', 'eV', 'Da', 'L', 'cal', 'bar', 'Torr')

        supported_unit_prefix_scalars = (
            'Y', 'Z', 'E', 'P', 'T', 'G', 'M', 'k', 'h', 'da', '', 'd', 'c', 'm', 'µ', 'n', 'p', 'f', 'a', 'z',
            'y')

        supported_special_units = ('Å', 'u', 'amu', 'atm', 'min')

        special_units = [unit_identifier + i for i in supported_special_units]

        supported_units = []
        for i in supported_base_units:
            for j in [unit_identifier + i for i in supported_unit_prefix_scalars]:
                supported_units.append(j + i)

        # define attributes
        self.__exclusions__ = function_exclusions
        self.__cns_vals__ = con_vals
        self.__cns_keys__ = con_keys
        self.__cns_disp__ = con_disp
        self.__unit_id__ = unit_identifier
        self.__phys_cns_vals__ = tuple(physical_constants_values)
        self.__phys_cns_keys__ = supported_physical_constants
        self.__units__ = units
        self.__cprint__ = cprint
        self.__sig_fig__ = sf
        self.supported_units = supported_units + special_units
        self.supported_physical_constants = tuple([i + '=' + j for i, j in zip(supported_physical_constants,
                                                                               physical_constants_values)])

    def add_cns(self, cons):
        """

        Parameters
            cons : str
                Additional constants are defined here, either in the format 'x = 3, y = 1/2' or 'x : 3; y : 1/2' (or any
                mixture of the two types). The same natural constants supported in mathpar.parser() are supported.

        Returns
            An updated value table with the new constants.

        """

        # save previous defined constants as easily accessible variable
        old_con_vals = self.__cns_vals__
        old_con_keys = self.__cns_keys__
        old_con_disp = self.__cns_disp__
        supported_units = self.supported_units
        phys_cns_keys = self.__phys_cns_keys__
        phys_cns_vals = self.__phys_cns_vals__
        base_exclusions = self.__exclusions__

        # map new constants
        add_con_vals, add_con_keys = [], []
        for k in [h.replace('=', ':').split(':') for h in nsu.replace(';', ',', cons).split(',')]:
            add_con_keys.append(k[0].replace(' ', ''))
            add_con_vals.append(k[1])

        # check if attempting to add a constant that is already defined
        old_con_keys_re, old_con_vals_re, old_con_disp_re = [], [], []
        for i, j, k in zip(old_con_keys, old_con_vals, old_con_disp):
            if i not in add_con_keys:
                old_con_keys_re.append(i)
                old_con_vals_re.append(j)
                old_con_disp_re.append(k)
            else:
                cur_val = add_con_vals[add_con_keys.index(i)]
                old_val = j[1:-1]
                if cur_val != old_val:
                    print(
                        f'Constant \'{i} = {j[1:-1]}\' has been changed to \'{add_con_vals[add_con_keys.index(i)]}\'.')

        # check for implicit multiplication and replace previously defined constants
        collective_items = base_exclusions + tuple(old_con_keys_re) + phys_cns_keys
        product_fixed_string = [nsp.product_parser(i, collective_items, tuple(supported_units)) for i in add_con_vals]

        # replace constants prior to parsing with .parser()
        replacements_sorted = nsu.list_sorter(
            old_con_keys_re + list(phys_cns_keys), old_con_vals_re + list(phys_cns_vals), reverse=True)
        replaced_strings = [nsu.replace(replacements_sorted[0], replacements_sorted[1], i,
                                        base_exclusions + tuple(supported_units)) for i in product_fixed_string]

        # fix additions to display values and computational values
        re_con_vals, re_con_disp = [], []
        for i in replaced_strings:
            if i[0] == '(' and i[-1] == ')':  # ensure that no parentheses doubles are inserted
                re_con_vals.append(i)
                re_con_disp.append(i[1:-1])
            else:
                re_con_vals.append('(' + i + ')')
                re_con_disp.append(i)

        # update the attributes concerning the constants
        self.__cns_vals__ = old_con_vals_re + re_con_vals
        self.__cns_keys__ = old_con_keys_re + add_con_keys
        self.__cns_disp__ = old_con_disp_re + re_con_disp

    def calc(self, math_string, add_res=False, **kwargs):
        """
        This is the computational part of the script. Computations are based on the mathpar.parser(). For any defined
        constants, these will be used. Note that implicit multiplication only works between constants and numbers. The
        expression '2x' will be read as '2*x', whereas '2xy' will be read as '2*xy'. This is done to allow constants of
        multiple letters to be defined.

        Parameters
            math_string : str
                The mathematical expression needed to be computed. See doc-string for mathpar.parser() for more
                information.
            add_res : str (or False)
                Add the computational result as a constant to the table with the specified name. If False, do not add
                result as a constant. The default is False.

        Keyword Arguments
            cprint : str, False or None
                Determines whether the computational result should be printed in the python console. There are six
                options: 'num' will display input string with constants replaced with values, 'sym' will display input
                string with constants as symbols, 'symc' has same functionality as the latter, but also prints the
                given constants, 'sym_ex' and 'symc_ex' will do the same as the respective options mentioned, but with
                the multiplication as explicit, False (or None) will disable result print. The default is inherited from
                __init__().
            sf : int or None
                Sets the significant figures for displayed calculation and constants from the cprint. If None, no
                change to the significant figures is made. The default is set by the global default from __init__().

        Returns
            The result of the computation.
        """

        # replace constants with their values, without replacing functions
        con_vals = self.__cns_vals__
        con_keys = self.__cns_keys__
        con_disp = self.__cns_disp__
        unit_id = self.__unit_id__
        supported_units = self.supported_units
        phys_cns_keys = self.__phys_cns_keys__
        phys_cns_vals = self.__phys_cns_vals__
        base_exclusions = self.__exclusions__

        if 'cprint' in kwargs.keys():  # set default cprint if nothing was defined
            cprint = kwargs.get('cprint')
        else:
            cprint = self.__cprint__
        if 'sf' in kwargs.keys():  # set default significant figures if nothing was defined
            sf = kwargs.get('sf')
        else:
            sf = self.__sig_fig__

        # respond with proper error, if no expression is given, when .calc is called
        if not math_string:
            raise ValueError('Provide an expression for calculation.')

        # check if constants are defined as equations or floats (if any constants)
        re_con_vals, re_con_disp = [], []
        for i, d in zip(con_vals, con_disp):
            checker_list = nsu.replace(
                [k + '^' for k in supported_units], '', i.replace('^-', '^').replace('e-', 'e').replace('e+', 'e'))
            opr_list = ('+', '-', '*', '/', '^', '!') + base_exclusions
            if any(j in opr_list for j in nsu.multi_split(checker_list, opr_list)):  # compute if math expression
                math_res, unit_res = nup.unit_parser(i, unit_identifier=unit_id, cprint=False, result='math, unit',
                                                     supp_units=supported_units)
                if unit_res == 'a.u.':
                    unit_res = ''
                if unit_res:  # ensure that unit ids are only added, if the result has a unit
                    re_con_vals.append('(' + str(math_res) + unit_id + unit_res[1:] + ')')
                    re_con_disp.append(str(math_res) + unit_res)
                else:
                    re_con_vals.append('(' + str(math_res) + ')')
                    re_con_disp.append(str(math_res))
            else:
                if i[0] == '(' and i[-1] == ')':  # ensure that no parentheses doubles are inserted
                    re_con_vals.append(i)
                    re_con_disp.append(i[1:-1])
                else:
                    re_con_vals.append('(' + i + ')')
                    re_con_disp.append(i)

        # update constant value list and display value lists according to the computed values to avoid performing more
        # computations than necessary
        self.__cns_vals__ = re_con_vals
        self.__cns_disp__ = re_con_disp

        # add implicit multiplication symbols
        collective_items = base_exclusions + tuple(con_keys) + phys_cns_keys
        product_fixed_string = nsp.product_parser(math_string, collective_items, tuple(supported_units))

        # replace the constants with their values, respecting the exclusions
        replacements_sorted = nsu.list_sorter(
            con_keys + list(phys_cns_keys), re_con_vals + list(phys_cns_vals), reverse=True)
        replaced_string = nsu.replace(replacements_sorted[0], replacements_sorted[1], product_fixed_string,
                                      base_exclusions + tuple(supported_units))

        # ensure that there are no undefined constants, otherwise raise error
        checkers_sorted = nsu.list_sorter(base_exclusions + tuple(supported_units) + ('e-', 'e', 'e+'), reverse=True)
        replaced_string_checker = nsu.replace(checkers_sorted, '', replaced_string, out_type='list')
        for i in replaced_string_checker:
            if i in nsu.alphabetSequenceCap + nsu.alphabetSequence:
                raise ValueError(f'Constant \'{i}\' is not defined.')

        # fix the display of the input expression
        math_string_print = math_string
        parser_cprint = cprint
        if cprint in ('symc_ex', 'sym_ex'):
            math_string_print = product_fixed_string
            parser_cprint = 'sym'
        elif cprint == 'symc':
            parser_cprint = 'sym'
        elif cprint == 'num':
            math_string_print = replaced_string

        # compute the expression with mathpar.parser(), with fixed cprint value
        computation, unit_result = nup.unit_parser(replaced_string, unit_identifier=unit_id, cprint=parser_cprint,
                                                   result='math, unit', true_string=math_string_print,
                                                   supp_units=supported_units, sf=sf)
        self.ans = computation
        if unit_result == 'a.u.':
            self.__ans_unit__ = ''
        else:
            self.__ans_unit__ = unit_result

        # if add result as constant is called, check if name is indeed a string and not a float or int
        if add_res:

            # check if indeed a unit result, and set unit id accordingly
            if not unit_result:
                unit_id = ''

            # check if name is indeed a string and not a float or int
            if not isinstance(add_res, str):
                raise ValueError(f'Constant name must be a type str, not \'{type(add_res)}\'.')
            elif isinstance(nsu.string_to_float(add_res), float):
                raise ValueError('Constant must not be a value.')

            # add name and result to the constant keys and values, respectively
            if add_res in con_keys:  # if the constant is already defined, then overwrite
                res_id = con_keys.index(add_res)
                res_val = '(' + str(computation) + unit_id + unit_result[1:] + ')'
                res_disp = str(computation) + unit_result
                old_disp = con_disp[res_id]
                if res_disp != old_disp:  # inform about overwritten constant if necessary
                    print(f'Constant \'{add_res} = {old_disp}\' has been changed to \'{res_disp}\'.')
                self.__cns_vals__[res_id] = res_val
                self.__cns_disp__[res_id] = res_disp
            else:  # otherwise just add the constant
                self.__cns_keys__ += [add_res]
                self.__cns_vals__ += ['(' + str(computation) + unit_id + unit_result[1:] + ')']
                self.__cns_disp__ += [str(computation) + unit_result]

        # if cprint is set to symbolic with constants, rewrite input string and constants to symbols and
        if cprint in ('symc', 'symc_ex') and con_keys:

            # check which constants are being used in the expression, and collect
            sort_keys_disp = nsu.list_sorter(con_keys, re_con_disp, reverse=True)
            used_keys, used_disp = [], []
            temp_expression = math_string
            for i, j in zip(sort_keys_disp[0], sort_keys_disp[1]):

                # if key is in expression, map it and display value to list, and remove key from expression to prevent
                #   overlap of constants
                if i in nsu.replace(base_exclusions, '', temp_expression):
                    used_keys.append(i)
                    try:
                        used_disp.append(' '.join(j.split(unit_id)))
                    except ValueError:
                        used_disp.append(j)
                    temp_expression = temp_expression.replace(i, '')
                if not temp_expression:  # break if temporary expression becomes empty
                    break

            if used_keys:  # if any constants were used in the expression, prettify and print them
                con_string = ';'.join(con_keys)  # make con_keys into an easily splittable string

                # replace symbols with identifier
                replacement_keys = nsu.alphabetSequenceGreekLetters + nsu.alphabetSequenceGreekLettersCap
                replacement_vals = nsu.alphabetSequenceGreek + nsu.alphabetSequenceGreekCap
                sorted_replacements = nsu.list_sorter(replacement_keys, replacement_vals, reverse=True, otype='tuple')
                pretty_constants = nsu.replace(sorted_replacements[0], sorted_replacements[1], con_string)

                # re-list con_keys with replaced symbols and print
                rep_con_keys = pretty_constants.split(';')
                for i, j in zip(rep_con_keys, used_disp):
                    if sf:  # fix significant figures for printing
                        j_split = j.split(' ')
                        with mpmath.workdps(sf):
                            try:
                                cur_disp = str(nsu.float_to_int(mpmath.mpf(j_split[0]))) + ' ' + j_split[1]
                            except IndexError:
                                cur_disp = str(nsu.float_to_int(mpmath.mpf(j)))
                            print(f'| {i} = {cur_disp}')
                    else:
                        print(f'| {i} = {j}')
        return computation

    def add_res(self, name):
        """
        Simple attribute that allows for just computed result to immediately be added to the table of constants.

        Parameters
            name : str
                Provide a name for the constant.
        """

        # define the previous computation result from attribute
        con_keys = self.__cns_keys__
        con_disp = self.__cns_disp__
        prev_comp_res = self.ans
        prev_comp_unit = self.__ans_unit__
        unit_id = self.__unit_id__

        # check if indeed a unit result, and set unit id accordingly
        if not prev_comp_unit:
            unit_id = ''

        # check if name is indeed a string and not a float or int
        if not isinstance(name, str):
            raise ValueError(f'Constant name must be a type str, not \'{type(name)}\'.')
        elif isinstance(nsu.string_to_float(name), float):
            raise ValueError('Constant must not be a value.')

        # add name and result to the constant keys and values, respectively
        res_val = '(' + str(prev_comp_res) + unit_id + prev_comp_unit[1:] + ')'  # set result value
        res_disp = str(prev_comp_res) + prev_comp_unit  # set result display value
        if name in con_keys:  # if the constant is already defined, then overwrite
            res_id = con_keys.index(name)
            old_disp = con_disp[res_id]
            if res_disp != old_disp:
                print(f'Constant \'{name} = {old_disp}\' has been changed to \'{res_disp}\'.')
            self.__cns_vals__[res_id] = res_val
            self.__cns_disp__[res_id] = res_disp
        else:  # otherwise just add the constant
            self.__cns_keys__ += [name]
            self.__cns_vals__ += [res_val]
            self.__cns_disp__ += [res_disp]

    def del_cns(self, *names):
        """
        Remove a constant from the defined library.

        Parameters
            *names : str
                The name of the constant that is to be removed.
        """

        current_keys = self.__cns_keys__
        current_vals = self.__cns_vals__
        current_disp = self.__cns_disp__

        if len(names) == 1:  # check if constants are given in a single string and fix to list from delimiter
            names = names[0].replace(';', ',').replace(' ', '').split(',')

        # construct a new list with the deleted constants excluded
        new_keys, new_vals, new_disp = [], [], []
        for i, j, k in zip(current_keys, current_vals, current_disp):
            if i not in names:
                new_keys.append(i)
                new_vals.append(j)
                new_disp.append(k)

        self.__cns_keys__ = new_keys
        self.__cns_vals__ = new_vals
        self.__cns_disp__ = new_disp

    def constants(self):
        """
        Get an overview of the currently defined constants.
        """

        current_keys = self.__cns_keys__
        current_disp = self.__cns_disp__
        unit_id = self.__unit_id__

        print('Currently defined constants:')
        for i, j in zip(current_keys, current_disp):
            print(f"| {i} = {' '.join(j.split(unit_id))}")
