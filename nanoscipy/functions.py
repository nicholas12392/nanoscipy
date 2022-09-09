"""
All modular functions of nanoscipy.

Contains
----------
multi_plot()

plot_grid()

plot_data()

file_select()

fit_data()

stepFinder()
"""

import warnings
import statistics as sts
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from statsmodels.graphics.gofplots import qqplot
from scipy.optimize import curve_fit
import scipy.odr as sco
import FlowCal
import nanoscipy.util as nsu


# from https://www.designwizard.com/blog/design-trends/colour-combination

def multi_plot(grid, plotds, xs, ys, tight=True, **kwargs):
    """
    Create a multi-plot with different graphs designated to each plot.

    Parameters
        grid : str
            Define the grid of the multiplot. Has to be denoted as 'rows x columns' e.g., '3x2'.
        plotds : tuple
            Define where each plot should be designated, e.g., (2, 3) if the first graph should be placed in plot number
            2, and the second graph in plot number 3.
        xs : list
            X-values.
        ys : list
            Y-values.
        tight : bool, optional
            Set layout to be tight. The default is True.


    Kwargs
        num : int
            Set figure number. The default is automatically generated.
        dpi : float
            Set dpi of the figure. The default is 300.
        figsize : tuple
            Define the dimensions of the figure. The default is (6, 2.5).
        ttl : str or list
            Set the title for the plots. If str set an overall title. If list set titles for those subplots. The default
            is None.
        xlab : str or list
            Set the x label for the plots. If str set a single label for all subplots and share the x-axis. If list set
            labels for individual subplots and do not share axis.
        ylab : str or list
            Set the y label for the plots. If str set a single label for all subplots and share the x-axis. If list set
            labels for individual subplots and do not share axis.
        dcol : str or list
            Color of the data sets. A string value sets a color for all
        ms : str or list
            Set the marker style of the markers. If str set value for all markers. If list set value for only elements
            given. The default is 'o'.
        mz : float or list
            Set the size of the markers. If float set value for all markers. If list set value for only those elements.
            The default is 1.
        lw : float or list
            Set line width of the given data. The default is 0.
        ls : str or list
            Set line style of given data. The default is 'solid'.
        alpha : float
            Set the alpha of the depicted data.
        dlab : list
            Name the depicted data sets. The default is automatically generated.
        lfsize : float or list
            Set label font size. If float set value for all labels. If list set value for only those elements.
            The default is 8.
        lloc : str or list
            Set the location of the labels. The default is 'best'.


    """
    global __FIGURE_NUMBER_NANOSCIPY_PYPLOT__

    # define empty list if no figure number has previously been used
    if '__FIGURE_NUMBER_NANOSCIPY_PYPLOT__' not in globals():
        __FIGURE_NUMBER_NANOSCIPY_PYPLOT__ = [0]

    # determine figure number
    if 'num' in kwargs.keys():
        plot_number = kwargs.get('num')
    else:
        plot_number = max(__FIGURE_NUMBER_NANOSCIPY_PYPLOT__) + 1

    # update list of figure numbers if plot_number not already defined
    if plot_number not in __FIGURE_NUMBER_NANOSCIPY_PYPLOT__:
        __FIGURE_NUMBER_NANOSCIPY_PYPLOT__ += [plot_number]

    # define variables for sharing of axis
    x_share_key = y_share_key = False
    if isinstance(kwargs.get('xlab'), str):
        x_share_key = True
    if isinstance(kwargs.get('ylab'), str):
        y_share_key = True

    # if this option proves desirable, use optional parameter ax_share=None, and add to doc_string:
    #   ax_share : str, optional
    #       Define whether axis should be shared amongst the different plots. Options: 'x', 'y', 'xy'. The default is
    #       None.
    # if ax_share in ('x', 'xy', 'yx', 'both'):
    #     x_share_key = True
    # else:
    #     x_share_key = False
    # if ax_share in ('y', 'xy', 'yx', 'both'):
    #     y_share_key = True
    # else:
    #     y_share_key = False

    # define kwargs for the grid
    kwargs_std_keys = ('dpi', 'figsize')
    kwargs_std_vals = (300, (6, 4))
    kwargs_new_vals = [kwargs.get(i) if i in kwargs.keys() else j for i, j in zip(kwargs_std_keys, kwargs_std_vals)]

    # define rows and columns of the plots in the figure
    grid_rows, grid_columns = [int(i) for i in grid.split('x')]
    psize = grid_rows * grid_columns

    # construct the figure according to the defined grid
    fig, axs = plt.subplots(grid_rows, grid_columns, num=plot_number, sharex=x_share_key, sharey=y_share_key,
                            dpi=kwargs_new_vals[0], figsize=kwargs_new_vals[1])

    # define large dummy-plot for legends if necessary
    # if any(isinstance(kwargs.get(i), str) for i in ('xlab', 'ylab')):
    if x_share_key or y_share_key:
        ax = fig.add_subplot(111, frameon=False)
        ax.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)

    # fix x and y lists
    # check whether x-list data is of correct shape, otherwise try to fix, if failed, py dim error is raised
    #   first check whether the x_data and y_data has same dimensions
    if len(xs) == len(ys) and np.array(xs).shape == np.array(ys).shape:
        try:  # if they do, try to convert all data to a list, if data is list of lists
            xlist = [[i for i in j] for j in xs]
        except TypeError:  # if data is a list of floats pack list into list
            xlist = [[i for i in xs]]
    else:
        xlist = [[i for i in xs]] * len(ys)  # if x and y data have different dimensions, try convert

    # check whether y-list data is of correct shape, otherwise try to fix, if failed, py dim error is raised
    try:  # try to convert all data to a list, if data is list of lists
        ylist = [[i for i in j] for j in ys]
    except TypeError:  # if data is a list of floats pack list into list
        ylist = [[i for i in ys]]

    # define function to handle kwargs
    def __kwarg_handler__(kwarg_keys, kwarg_vals, ksize):
        kwarg_list_vals = [[i] * ksize if not isinstance(i, (list, tuple)) else i for i in kwarg_vals]
        handled_kwargs = []
        for i, j in zip(kwarg_keys, kwarg_list_vals):
            if i not in kwargs.keys():
                list_elem = j
            else:
                elem_val = kwargs.get(i)
                if not isinstance(elem_val, (tuple, list, np.ndarray)):
                    list_elem = [elem_val] * ksize
                else:
                    list_elem = [e for e in elem_val] + j[len(elem_val) - 1:]
            handled_kwargs.append(list_elem)
        return handled_kwargs

    # define plotting kwargs
    dsize = len(ylist)  # define the amount of data sets
    plots_std_keys = ('dcol', 'ms', 'mz', 'lw', 'ls', 'alpha', 'dlab')
    plots_std_vals = (nsu.standardColorsHex[: dsize], 'o', 1, 0, 'solid', 1, nsu.alphabetSequence[: dsize])
    lists_new_vals = __kwarg_handler__(plots_std_keys, plots_std_vals, dsize)

    # plot xs and ys in figure according to the plot id
    for pid, x, y, color, mks, mkz, lw, ls, aa, lab in zip(plotds, xlist, ylist, *lists_new_vals):
        axs[pid].plot(x, y, c=color, marker=mks, markersize=mkz, linewidth=lw, linestyle=ls, alpha=aa, label=lab)

    # define and execute legend parameters
    legs_std_keys = ('lfsize', 'lloc')
    legs_std_vals = (8, 'best')
    legs_new_vals = __kwarg_handler__(legs_std_keys, legs_std_vals, psize)

    for pid, lfs, lloc in zip(range(psize), *legs_new_vals):
        axs[pid].legend(fontsize=lfs, loc=lloc)

    # set axis labels dependent on share keys if in dict
    if 'xlab' in kwargs.keys():
        xlab_kwarg = kwargs.get('xlab')
        if x_share_key:
            ax.set_xlabel(xlab_kwarg)
        else:
            for pid, label in zip(range(psize), xlab_kwarg):
                axs[pid].set_xlabel(label)
    if 'ylab' in kwargs.keys():
        ylab_kwarg = kwargs.get('ylab')
        if y_share_key:
            ax.set_ylabel(ylab_kwarg)
        else:
            for pid, label in zip(range(psize), ylab_kwarg):
                axs[pid].set_ylabel(label)

    # set layout fit
    if tight:
        plt.tight_layout()

    # set plot titles according to given input
    if 'ttl' in kwargs.keys():
        title_kwarg = kwargs.get('ttl')
        if isinstance(title_kwarg, str):
            fig.suptitle(title_kwarg)
        else:
            for i, j in zip(title_kwarg, range(psize)):
                axs[j].set_title(i)

    plt.rcParams.update({'font.family': 'Times New Roman'})
    plt.show()


def plot_grid(plot_nr=None, plot_row=None, plot_col=None, share=0, set_dpi=300, fig_size=(6, 2.5)):
    """
    Defines a grid of figures to plot in with plot_data().

    Parameters
    ----------
    plot_nr : int, optional
        The specific figure-unit number (plot_data() inherits this value).
        The default is 0.
    plot_row : int, optional
        Defines the number of rows of plots within the figure. The default is
        1.
    plot_col : TYPE, optional
        Defines the number of columns of plots within the figure.
        The default is 1.
    share : int or string, optional
        0; shares no axis, 'x' or 1, shares x-axis amongst different plots,
        'y'; shares y-axis. 'xy', 'yx', 'both', 3; shares both axis.
        The default is 0.
    set_dpi : int, optional
        Sets dpi for the entire figure. The default is 300.
    fig_size : list, optional
        Set height and width for the figure. The default is (6,2.5).

    Returns
    -------
    Global variables used by plot_data().

    """
    global __FIGURE_GLOBAL_OUTPUT__
    global __AX_GLOBAL_OUTPUT__
    global __FIGURE_NUMBER_GLOBAL_OUTPUT__
    global __SHARE_AXIS_BOOL_OUTPUT__
    global __BOUNDARY_AX_GLOBAL_FIX__

    if share not in ('x', 1, 'y', 2, 'xy', 'yx', 'both', 3, 0):
        raise ValueError(f'share={share} is invalid.')

    if plot_row == 0:
        raise ValueError(f'r={plot_row} is invalid.')

    if plot_col == 0:
        raise ValueError(f's={plot_col} is invalid.')

    if not plot_nr:
        plot_nr = 0

    if not plot_row:
        plot_row = 1

    if not plot_col:
        plot_col = 1

    if plot_row == 1 and plot_col == 1:
        __FIGURE_GLOBAL_OUTPUT__, temp_ax_global_output = plt.subplots(num=plot_nr, dpi=set_dpi, figsize=fig_size)
        __AX_GLOBAL_OUTPUT__ = [temp_ax_global_output]
    if plot_row > 1 or plot_col > 1:
        if share in ('x', 1):
            __FIGURE_GLOBAL_OUTPUT__, __AX_GLOBAL_OUTPUT__ = plt.subplots(plot_row, plot_col, num=plot_nr, sharex=True,
                                                                          dpi=set_dpi)
        elif share in ('y', 2):
            __FIGURE_GLOBAL_OUTPUT__, __AX_GLOBAL_OUTPUT__ = plt.subplots(plot_row, plot_col, num=plot_nr, sharey=True,
                                                                          dpi=set_dpi)
        elif share in ('xy', 'yx', 'both', 3):
            __FIGURE_GLOBAL_OUTPUT__, __AX_GLOBAL_OUTPUT__ = plt.subplots(plot_row, plot_col, num=plot_nr, sharex=True,
                                                                          sharey=True, dpi=set_dpi)
        elif share == 0:
            __FIGURE_GLOBAL_OUTPUT__, __AX_GLOBAL_OUTPUT__ = plt.subplots(plot_row, plot_col, num=plot_nr, sharex=False,
                                                                          sharey=False, dpi=set_dpi)
    __BOUNDARY_AX_GLOBAL_FIX__ = plot_row * plot_col
    __FIGURE_NUMBER_GLOBAL_OUTPUT__ = plot_nr
    __SHARE_AXIS_BOOL_OUTPUT__ = share


def plot_data(p, xs, ys, ttl=None, dlab=None, xlab=None, ylab=None, ms=None, lw=None, ls=None, dcol=None,
              plt_type=0, tight=True, mark=None, trsp=None, v_ax=None,
              h_ax=None, no_ticks=False, share_ttl=False, legend_size=7,
              x_scale=None, y_scale=None, x_lim=None, y_lim=None):
    if len(__AX_GLOBAL_OUTPUT__) != __BOUNDARY_AX_GLOBAL_FIX__:
        axs = __AX_GLOBAL_OUTPUT__.flatten()
    else:
        axs = __AX_GLOBAL_OUTPUT__

    # check for correct list input, and try fix if data-list is not in list
    if not isinstance(xs, (list, np.ndarray)):
        raise ValueError('xs must be a list or numpy.ndarray.')

    if (any(isinstance(i, (list, np.ndarray)) for i in xs) and
            any(isinstance(i, (float, int, np.integer, np.float64)) for i in xs)):
        raise ValueError(
            'Values of x-list must be of type: int, float, numpy.integer, or numpy.float.')

    if not all(isinstance(i, (list, np.ndarray)) for i in xs):
        xs_fix = [xs]
    else:
        xs_fix = xs

    if plt_type in (0, 'plot', 1, 'scatter'):
        if not isinstance(ys, (list, np.ndarray)):
            raise ValueError('xs must be a list or numpy.ndarray.')
        if (any(isinstance(i, (list, np.ndarray)) for i in ys) and
                any(isinstance(i, (float, int, np.integer, np.float64))
                    for i in ys)):
            raise ValueError(
                'Values of y-list must be of type: int, float, numpy.integer, or numpy.float.')
        if not all(isinstance(i, (list, np.ndarray)) for i in ys):
            ys_fix = [ys]
        else:
            ys_fix = ys
        if len(xs_fix) != len(ys_fix):
            raise ValueError('len(xs) and len(ys) does not match.')

    data_length = len(xs_fix)
    non = np.repeat(None, data_length)
    ones = np.repeat(1, data_length)

    if len(nsu.standardColorsHex) <= data_length:
        raise AssertionError(
            'Too many standard colors needed, use custom colors via dcol.')

    color_list = nsu.standardColorsHex[0:data_length]
    opt_vars = [dlab, mark, ms, lw, dcol, ls, trsp]
    opt_vars_default = [non, ['.'] * data_length, ones, ones, color_list,
                        ['solid'] * data_length, ones]
    opt_vars_fix = []
    for i, j in zip(opt_vars, opt_vars_default):
        if not i:
            opt_vars_fix.append(j)
        elif not isinstance(i, (list, np.ndarray)):
            opt_vars_fix.append([i])
        else:
            opt_vars_fix.append(i)

    # set title according to share_ttl
    if share_ttl is False:
        axs[p].set_title(ttl)
    elif share_ttl is True:
        __FIGURE_GLOBAL_OUTPUT__.suptitle(ttl)

    ds = range(data_length)
    if plt_type in (0, 'plot'):
        [axs[p].plot(xs_fix[n], ys_fix[n], c=opt_vars_fix[4][n],
                     label=opt_vars_fix[0][n], linewidth=opt_vars_fix[3][n],
                     markersize=opt_vars_fix[2][n], marker=opt_vars_fix[1][n],
                     linestyle=opt_vars_fix[5][n],
                     alpha=opt_vars_fix[6][n]) for n in ds]
    if plt_type in (1, 'scatter'):
        [axs[p].scatter(xs_fix[n], ys_fix[n], c=opt_vars_fix[4][n],
                        label=opt_vars_fix[0][n], s=opt_vars_fix[2][n],
                        alpha=opt_vars_fix[6][n]) for n in ds]
    if plt_type in (2, 'qqplot'):
        if isinstance(xs_fix, list):
            np_xs_fix = np.asarray(xs_fix)
        elif isinstance(xs_fix, np.ndarray):
            np_xs_fix = xs_fix
        if not ls:
            line_type = ['r'] * data_length
        elif not isinstance(ls, list):
            line_type = [ls]
        else:
            line_type = ls
        [qqplot(np_xs_fix[n], line=line_type[n], ax=axs[p],
                marker=opt_vars_fix[1][n], color=opt_vars_fix[4][n],
                label=opt_vars_fix[0][n], alpha=opt_vars_fix[6][n]) for n in ds]
        # axs[p].boxplot([xs_fix[n] for n in ds],labels=[opt_vars_fix[0][n] for n in ds])

    # fix labels according to __SHARE_AXIS_BOOL_OUTPUT__
    if __SHARE_AXIS_BOOL_OUTPUT__ in ('x', 1):
        axs[-1].set_xlabel(xlab)
        axs[p].set_ylabel(ylab)
    elif __SHARE_AXIS_BOOL_OUTPUT__ in ('y', 2):
        axs[p].set_xlabel(xlab)
        axs[0].set_ylabel(ylab)
    elif __SHARE_AXIS_BOOL_OUTPUT__ in ('xy', 'yx', 'both', 3):
        axs[-1].set_xlabel(xlab)
        axs[0].set_ylabel(ylab)
    elif __SHARE_AXIS_BOOL_OUTPUT__ in ('no', 0):
        axs[p].set_xlabel(xlab)
        axs[p].set_ylabel(ylab)

    # set fitted layout according to tight
    if tight is True:
        plt.tight_layout()

    # set axis tics according to no_ticks
    if no_ticks is True:
        axs[p].set_yticks([])
        axs[p].set_xticks([])

    if h_ax == 0:
        axs[p].axhline(y=0, xmin=0, xmax=1, color='black', linestyle='solid',
                       linewidth=0.5, alpha=1)
    elif h_ax == 1:
        axs[p].axhline(y=0, xmin=0, xmax=1, color='black', linestyle='dashed',
                       linewidth=1, alpha=0.5)
    elif h_ax == 2:
        axs[p].axhline(y=0, xmin=0, xmax=1, color='black', linestyle='dotted',
                       linewidth=1, alpha=1)
    if v_ax == 0:
        axs[p].axvline(x=0, ymin=0, ymax=1, color='black', linestyle='solid',
                       linewidth=0.5, alpha=1)
    elif v_ax == 1:
        axs[p].axvline(x=0, ymin=0, ymax=1, color='black', linestyle='dashed',
                       linewidth=1, alpha=0.5)
    elif v_ax == 2:
        axs[p].axvline(x=0, ymin=0, ymax=1, color='black', linestyle='dotted',
                       linewidth=1, alpha=1)

    # set legends
    if x_scale:
        axs[p].set_xscale(x_scale)
    if y_scale:
        axs[p].set_yscale(y_scale)

    if x_lim:
        plt.xlim(x_lim[0], x_lim[1])
    if y_lim:
        plt.ylim(y_lim[0], y_lim[1])
    axs[p].legend(fontsize=legend_size)
    plt.rcParams.update({'font.family': 'Times New Roman'})
    plt.show()


def file_select(path, set_cols=None, cut_rows=None, **kwargs):
    """
    This function selects and extracts data, from a file at a specified path. It can be useful to index multiple data 
    files in a way, that allows for easy extraction in a for-loop.

    Parameters
        path : string
            Defines the file path, note that you might want to do this as an r-string (and if for-loop; part as an 
            f-string).
        set_cols : list of ints, optional
            List of the column indexes you want extracted (note that this is not a range, but specific selection). The 
            default is [0,1].
        cut_rows : int or list, optional
            If integer; cut from row 0 to specified integer, if list; cut the specified rows from the list. The default 
            is 0.

    Keyword Arguments
        separator : string, optional
            Define the delimiter of the data set (if necessary). The default is if .csv; \',\', if .txt; \'\\t\'.
        py_axlist : bool, optional
            Constructs a regular python list, consisting of lists of all values of a certain variable, instead of
            gaining rows of value-sets. The default is False.
        as_matrix : bool, optional
            Allows for loading of data as a matrix via numpy.loadtxt; note that this is only valid for .txt files. The 
            default is False.

    Returns
        data : list
            The list (or list of lists) with the data from the selected file under the specified conditions.
        data_axlist : list
            Instead of containing data points from the data set, contains what corresponds to an x-, y-, z- etc. lists. 
            Only relevant if py_axlist = True; then the function yields both data and data_axlist.

    """
    assert path, 'Missing file path.'  # assert if missing path
    if not set_cols:  # define standard column selection if no custom selection is defined
        set_columns = [0, 1]
    else:
        if isinstance(set_cols, int):
            set_columns = [set_cols]
        else:
            set_columns = set_cols
    # if not cut_rows:
    #     try:
    #         cut_rows = 0
    #     except ValueError:
    #         while ValueError:
    #               cut_rows += 1

    # define list of passable extensions
    allowed_extensions = ('.csv', '.txt', '.excel', '.xlsx', '.dat', '.fcs')
    file_extension = os.path.splitext(path)[1]  # split input file name and save extension

    # check if passed extension can be handled
    if file_extension not in allowed_extensions:
        raise ValueError(f'Selected file type {file_extension} is not supported.')

    # try to define standard delimiter, if none is defined
    if 'separator' not in kwargs.keys():
        if file_extension == '.csv':
            separator = ','
        elif file_extension in ('.txt', '.dat'):
            if 'as_matrix' in kwargs.keys() and kwargs.get('as_matrix'):
                separator = None
            else:
                separator = '\t'
    else:
        separator = kwargs.get('separator')
    if file_extension in ('.excel', '.xlsx'):
        data = pd.read_excel(path, header=cut_rows, usecols=set_columns).to_numpy()
    elif file_extension in ('.csv', '.txt', '.dat'):
        if 'as_matrix' in kwargs.keys() and kwargs.get('as_matrix'):
            data = np.loadtxt(fname=path, delimiter=separator, skiprows=cut_rows)
        else:
            data = pd.read_csv(path, header=cut_rows, usecols=set_columns, sep=separator).to_numpy()
    elif file_extension == '.fcs':
        data = FlowCal.io.FCSData(path)
    if 'py_axlist' not in kwargs.keys() or ('py_axlist' in kwargs.keys() and kwargs.get('py_axlist')):
        data_axlist = [data[:, i].tolist() for i in range(len(data[0]))]
        data_axlist_fix = [[nsu.string_to_float(i) for i in data_axlist[j]]
                           for j in range(len(data_axlist))]
        result = data_axlist_fix
    else:
        result = data
    return result


def fit_data(func, x_list, y_list, g_list, method='curve_fit', **kwargs):
    """
    Fits data to the given general function, and outputs the parameters for
    the specific function.

    Parameters
        func : function
            The specific function data is to be fitted to
        x_list : list
            x-list data.
        y_list : list
            y-list data.
        g_list : list
            Guess-list. These are initial guesses at the parameters in the
            function to fit.
        method : str, optional
            Specific method of fitting. Currently, options are curve_fit and odr. The default is curve_fit.

    Keyword Arguments
        f_num : int
            The number of constructed data-points. The default is 300.
        mxf : int
            The maximum amount of iterations. The default is 1000.
        extrp : float, int or list
            Extrapolate fitted x and y lists. If a value is given, it is determined whether it is a minimum or maximum
            extrapolation, if list, the first element will be minimum and the second element the maximum.

    Returns
        popt : list
            Fitted parameters in the same order as defined in the provided
            function.
        pcov : list
            The covariance for the determined parameters.
        pstd : list
            The standard deviation of the determined parameters.
        x_fit : list
            Fitted x-values.
        y_fit : list
            Fitted y-values.
        x_err_est : list, conditional
            Estimated input x-errors if odr is the method.
        y_err_est : list, conditional
            Estimated input y-errors if odr is the method.

    """

    # send warning if more than 15 different constants in function
    if len(g_list) > 15:
        warnings.warn('Fitting more than 15 constants may take a while.')

    # define standard params if none is set
    if 'f_num' in kwargs.keys():
        frame_number = kwargs.get('f_num')
    else:
        frame_number = 300
    if 'mxf' in kwargs.keys():
        mxf = kwargs.get('mxf')
    else:
        mxf = 1000

    x_min_temp = min(x_list)
    x_max_temp = max(x_list)

    if 'extrp' in kwargs.keys():
        extrp = kwargs.get('extrp')
        if isinstance(extrp, (int, float)):
            if extrp < x_min_temp:
                x_min = extrp
                x_max = x_max_temp
            elif extrp > x_max_temp:
                x_min = x_min_temp
                x_max = extrp
            else:
                raise ValueError('Use list to extrapolate inside data set.')
        elif isinstance(extrp, (list, np.ndarray)) and len(
                extrp) == 2:
            x_min = extrp[0]
            x_max = extrp[1]
        else:
            raise ValueError(
                'Extrapolation must be of type int, float or list.')
    else:
        x_min = x_min_temp
        x_max = x_max_temp

    # define x-fit list from defined x min and max values
    x_fit = np.linspace(x_min, x_max, frame_number)

    # perform fitting after given method
    if method == 'curve_fit':
        popt, pcov = curve_fit(f=func, xdata=x_list, ydata=y_list, p0=g_list, absolute_sigma=True, maxfev=mxf)
        pstd = np.sqrt(np.diag(pcov))

        # define output
        y_fit = func(x_fit, *popt)  # define y-list
        __out__ = (popt, pcov, pstd, x_fit, y_fit)
    elif method == 'odr':
        if 'x_err' in kwargs.keys():  # check for given x error
            x_err = kwargs.get('x_err')
        else:
            x_err = None
        if 'y_err' in kwargs.keys():
            y_err = kwargs.get('y_err')
        else:
            y_err = None
        odr_fit_function = sco.Model(func)  # define odr model
        odr_data = sco.RealData(x_list, y_list, sx=x_err, sy=y_err)  # define odr data
        odr_setup = sco.ODR(odr_data, odr_fit_function, beta0=g_list)  # define the ODR itself
        odr_out = odr_setup.run()  # run the ODR

        # define constants, along with covariance and deviation
        popt, pcov, pstd = odr_out.beta, odr_out.cov_beta, odr_out.sd_beta

        # define estimated x and y errors
        x_err_est, y_err_est = odr_out.delta, odr_out.eps

        # define output
        y_fit = func(popt, x_fit)
        __out__ = (popt, pcov, pstd, x_fit, y_fit, x_err_est, y_err_est)
    else:
        raise ValueError(f'Passed method, {method}, is not supported.')

    return __out__


def step_finder(x_data, y_data, delta=30, lin=0.005, err=0.005):
    """
    Determine averages of linear-horizontal data determined by delta, with a
    set horizontal linearity and maximum error.

    Parameters
    ----------
    x_data : list
        List of x-values in data set.
    y_data : list
        list of y-values in data set.
    delta : int, optional
        Range for amount of required points for the linear fit. The default is
        30.
    lin : float, optional
        Maximum slope of the linear fit. The default is 0.005.
    err : float, optional
        Maximum standard error for the linear fit. The default is 0.005.

    Returns
    -------
    xs_point : list
        x-values for determined points.
    ys_point : list
        y-values for determined points.

    """
    linear_fit = lambda x, a, b: a * x + b
    initial_point = 0
    final_point = initial_point + delta
    x_test, y_test = x_data[initial_point:final_point], y_data[initial_point:
                                                               final_point]
    popt, pcov_fix, pstd, xs_fit, ys_fit = fit_data(linear_fit, x_test, y_test, [0, 1])
    xs_point, ys_point = [], []
    while final_point < len(x_data):
        initial_point += 1
        final_point = initial_point + delta
        x_test, y_test = x_data[initial_point:final_point], y_data[
                                                            initial_point:final_point]
        popt, pcov_fix, pstd, xs_fit, ys_fit = fit_data(linear_fit, x_test, y_test, [0, 1])
        if abs(popt[0]) < lin and pstd[0] < err:
            xs_point.append(sts.mean(xs_fit))
            ys_point.append(sts.mean(ys_fit))
    return xs_point, ys_point

# def data_extrema(data,pos_index=False,pos_range=None):
#     """
#     Determines extremes in a selected region. Can also identify the
#     list-position of the extrema. Note that by extrema; it finds only the
#     global extremes, as these are the maximum and minimum values of the data
#     set.

#     Parameters
#     ----------
#     data : list
#         Data for determining extremes.
#     pos_index : bool, optional
#         Determines whether the extremes should have their list positions
#         indexed. This yields an additional output list; index_list.
#         The default is False.
#     pos_range : list of ints, optional
#         Needs a starting point and an ending point, defining the range.
#         The default is [0,-1].

#     Returns
#     -------
#     min_val : int
#         The minimum of the data_length (packed as a list with the maximum).
#     max_val : int
#         The maximum of the data set (packed as a list with the minimum).
#     index_list : list
#         Contains the index of the minimum and the maximum (in that order).

#     """

#     if not pos_range:
#         pos_range = [0,-1]
#     max_id = np.where(max(data[pos_range[0]:pos_range[1],1]) == data)[0][0] # index max val
#     max_val = [data[max_id,0],data[max_id,1]] # find max val coord
#     min_id = np.where(min(data[pos_range[0]:pos_range[1],1]) == data)[0][0] # index min val
#     min_val = [data[min_id,0],data[min_id,1]] # find min val coord
#     if pos_index is False:
#         return [min_val,max_val]
#     if pos_index is True:
#         index_raw = [np.where(data[:,0] == min_val[0]),np.where(data[:,0] == max_val[0])] # index extremes
#         index_list = [[index_raw[0][0][0]],[index_raw[1][0][0]]]
#         return [min_val,max_val], index_list
