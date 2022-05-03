"""
All modular functions of nanoscipy.

Contains
----------
plot_grid()

plot_data()

string_to_float()

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

# from itertools import chain
# import csv

standardColorsHex = ['#5B84B1FF', '#FC766AFF', '#5F4B8BFF', '#E69A8DFF',
                     '#42EADDFF', '#CDB599FF', '#00A4CCFF', '#F95700FF',
                     '#00203FFF', '#ADEFD1FF', '#F4DF4EFF', '#949398FF',
                     '#ED2B33FF', '#D85A7FFF', '#2C5F2D', '#97BC62FF',
                     '#00539CFF', '#EEA47FFF', '#D198C5FF', '#E0C568FF']


# from https://www.designwizard.com/blog/design-trends/colour-combination

def plot_grid(plot_nr=None, plot_row=None, plot_col=None, share=0, set_dpi=300, fig_size=(6, 2.5)):
    '''
    Defines a grid of figures to plot in with plot_data().

    Parameters
    ----------
    plot_nr : int, optional
        The specific figure-unit number (plot_data() inherits this value).
        The default is 0.
    plot_row : int, optional
        Defines the numnber of rows of plots within the figure. The default is
        1.
    plot_col : TYPE, optional
        Defines the numnber of columns of plots within the figure.
        The default is 1.
    share : int or string, optional
        0; shares no axis, 'x' or 1, shares x-axis amongst different plots,
        'y'; shares y-axis. 'xy', 'yx', 'both', 3; shares both axis.
        The default is 0.
    set_dpi : int, optional
        Sets dpi for the entire figure. The default is 300.
    fig_size : list, optional
        Set hight and width for the figure. The default is (6,2.5).

    Returns
    -------
    Global variables used by plot_data().

    '''
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

    # chek for correct list input, and try fix if data-list is not in list
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

    if len(standardColorsHex) <= data_length:
        raise AssertionError(
            'Too many standard colors needed, use costum colors via dcol.')

    color_list = standardColorsHex[0:data_length]
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


def string_to_float(potential_float):
    """
    Converts string to float if possible (that is unless ValueError is
                                          encountered).

    Parameters
    ----------
    potential_float : str
        String to be converted to float.

    Returns
    -------
    float or str
        If successful, input is now float, if unsuccessful, str is still str.

    """
    try:
        set_float = float(potential_float)
        return set_float
    except ValueError:
        return potential_float


def file_select(path, set_cols=None, cut_rows=None, separator=None, py_axlist=True,
                as_matrix=False):
    """
    This function selects and extracts data, from a file at a specified path.
    It can be useful to index multiple data files in a way, that allows for
    easy extration in a for-loop.

    Parameters
    ----------
    path : string
        Defines the file path, note that you might want to do this as an
        r-string (and if for-loop; part as an f-string).
    set_cols : list of ints, optional
        List of the column indexes you want extracted
        (note that this is not a range, but specific selection).
        The default is [0,1].
    cut_rows : int or list, optional
        If integer; cut from row 0 to specified integer, if list; cut the
        specified rows from the list. The default is 0.
    separator : string, optional
        Define the deliminter of the data set (if nescessary). The default is
        if .csv; \',\', if .txt; \'\\t\'.
    py_axlist : bool, optional
        Constructs a regular python list, consisting of lists of all values of
        a certian variable, instead of gaining rows of value-sets.
        The default is False.
    as_matrix : bool, optional
        Allows for loading of data as a matrix via numpy.loadtxt; note that
        this is only valid for .txt files. The default is False.

    Returns
    -------
    data : list
        List (or list of lists) with the data from the selected file under the
        specified conditions.
    data_axlist : list
        Instead of containing data points from the data set, contains what
        corresponds to an x-, y-, z- etc. lists. Only relavant if
        py_axlist = True; then the function yields both data and data_axlist.

    """
    assert path, 'No path selected.'
    if not set_cols:
        set_cols_fixed = [0, 1]
    if isinstance(set_cols, int):
        set_cols_fixed = [set_cols]
    else:
        set_cols_fixed = set_cols
    # if not cut_rows:
    #     try:
    #         cut_rows = 1
    #     except ValueError:
    #         while ValueError:
    # cut_rows =+1
    allowed_extensions = ['.csv', '.txt', '.excel', '.xlsx', '.dat']
    file_extension = os.path.splitext(path)[1]

    if file_extension not in allowed_extensions:
        raise ValueError(f'Selected file type {file_extension} is invalid.')
    # try to define standard delimiter, if none is defined
    if not separator:
        if file_extension == '.csv':
            separator = ','
        elif file_extension in ('.txt', '.dat'):
            if as_matrix is True:
                separator = None
            elif as_matrix is False:
                separator = '\t'
    if file_extension in ('.excel', '.xlsx'):
        data = pd.read_excel(path, header=cut_rows, usecols=set_cols_fixed
                             ).to_numpy()
    elif file_extension in ('.csv', '.txt', '.dat'):
        if as_matrix is True:
            data = np.loadtxt(fname=path, delimiter=separator, skiprows=cut_rows)
        elif as_matrix is False:
            data = pd.read_csv(path, header=cut_rows, usecols=set_cols_fixed,
                               sep=separator).to_numpy()
    if py_axlist is True:
        data_axlist = [data[:, i].tolist() for i in range(len(data[0]))]
        data_axlist_fix = [[string_to_float(i) for i in data_axlist[j]]
                           for j in range(len(data_axlist))]
        result = data_axlist_fix
    if py_axlist is False:
        result = data
    return result


def fit_data(function, x_list, y_list, g_list, rel_var=False, N=None, mxf=None,
             extMin=None, extMax=None, **kwargs):
    """
    Fits data to the given general function, and outputs the parameters for
    the specific function.

    Parameters
    ----------
    function : lambda/py function
        The specific function data is to be fitted to
    x_list : list
        x-list data.
    y_list : list
        y-list data.
    g_list : list
        Guess-list. These are initial guesses at the parameters in the
        function to fit.
    rel_var : bool, optional
        Determines whether the calculated variation should be relative or
        absolute.
        The default is False.
    N : int, optional
        The number of constructed data-points. The default is the size of the
        provided x-list.
    mxf : int, optional
        The maximum amount of iterations. The default is 1000.
    extMin : float, optional
        Extrapolate data points down to this limit.
    extMax : float, optional
        Extrapolate data points up to this limit.

    Returns
    -------
    popt : list
        Fitted parameters in the same order as defined in the provided
        function.
    pcov_fix : list
        The covariance for the determined parameters.
    pstd : lsit
        The standard deviation of the determined parameters.
    xs_fit : list
        List of fitted x-values.
    ys_fit : list
        List of fitted y-values.

    """

    # define allowed kwargs
    kwargs_list = ('rel_var', 'N', 'mxf', 'extrp')
    assert all(kwargs.keys()) not in kwargs_list, 'Passed kwarg is undefined.'

    if not N:
        N = len(x_list)
    if not mxf:
        mxf = 1000

    popt, pcov = curve_fit(f=function, xdata=x_list, ydata=y_list, p0=g_list,
                           absolute_sigma=rel_var, maxfev=mxf)
    pcov_fix = [pcov[i][i] for i in range(len(popt))]
    pstd = [np.sqrt(i) for i in pcov_fix]

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
        if not extMin:
            x_min = x_min_temp
        else:
            x_min = extMin
        if not extMax:
            x_max = x_max_temp
        else:
            x_max = extMax

    xs_fit = np.linspace(x_min, x_max, N)
    ys_fit = function(xs_fit, *[i for i in popt])

    if len(popt) > 15:
        warnings.warn('Fitting more than 15 constants may take a while.')
    return list(popt), pcov_fix, pstd, xs_fit, ys_fit


def step_finder(x_data, y_data, delta=30, lin=0.005, err=0.005):
    """
    Determine averages of linear-horizontal data determined by delta, with a
    set horizontal liniarity and maximum error.

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
    popt, pcov_fix, pstd, xs_fit, ys_fit = fit_data(linear_fit, x_test, y_test,
                                                    [0, 1])
    xs_point, ys_point = [], []
    while final_point < len(x_data):
        initial_point += 1
        final_point = initial_point + delta
        x_test, y_test = x_data[initial_point:final_point], y_data[
                                                            initial_point:final_point]
        popt, pcov_fix, pstd, xs_fit, ys_fit = fit_data(linear_fit, x_test,
                                                        y_test, [0, 1])
        if abs(popt[0]) < lin and pstd[0] < err:
            xs_point.append(sts.mean(xs_fit))
            ys_point.append(sts.mean(ys_fit))
    return xs_point, ys_point

# def data_extrema(data,pos_index=False,pos_range=None):
#     """
#     Determines extremas in a selected region. Can also identify the
#     list-position of the extrema. Note that by extrema; it finds only the
#     global extremas, as these are the maximum and minimum values of the data
#     set.

#     Parameters
#     ----------
#     data : list
#         Data for determining extremas.
#     pos_index : bool, optional
#         Determines whether the extremas should have their list positions
#         indexed. This yields an additional output list; index_list.
#         The default is False.
#     pos_range : list of ints, optional
#         Needs a starting point and an ending point, defining the range.
#         The default is [0,-1].

#     Returns
#     -------
#     min_val : int
#         The minimum of the data_lengthet (packed as a list with the maximum).
#     max_val : int
#         The maximum of the data set (packed as a list with the minimum).
#     indes_list : list
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
#         index_raw = [np.where(data[:,0] == min_val[0]),np.where(data[:,0] == max_val[0])] # index extremas
#         index_list = [[index_raw[0][0][0]],[index_raw[1][0][0]]]
#         return [min_val,max_val], index_list
