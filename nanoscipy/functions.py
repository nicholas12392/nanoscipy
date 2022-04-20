'''
All modular functions of nanoscipy.

Contains
----------
plot_grid()

plot_data()

string_to_float()

file_select()

fit_data()

stepFinder()
'''

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import statistics as sts
import os
from statsmodels.graphics.gofplots import qqplot
from scipy.optimize import curve_fit
# from itertools import chain
# import csv

def plot_grid(plot_nr=None,plot_row=None,plot_col=None,share=0,set_dpi=300,fig_size=(6,2.5)):
    '''
    Defines a grid of figures to plot in with plot_data().

    Parameters
    ----------
    plot_nr : int, optional
        The specific figure-unit number (plot_data() inherits this value). The default is 0.
    plot_row : int, optional
        Defines the numnber of rows of plots within the figure. The default is 1.
    plot_col : TYPE, optional
        Defines the numnber of columns of plots within the figure. 
        The default is 1.
    share : int or string, optional
        0; shares no axis, 'x' or 1, shares x-axis amongst different plots, 'y'; 
        shares y-axis. 'xy', 'yx', 'both', 3; shares both axis. The default is 0.
    set_dpi : int, optional
        DESCRIPTION. The default is 300.
    fig_size : list, optional
        Set hight and width for the figure. The default is (6,2.5).

    Returns
    -------
    Global variables used by plot_data().

    '''
    global figure_global_output
    global ax_global_output
    global figure_number_global_output
    global share_axis_bool_output
    global boundary_ax_global_fix

    assert share in ('x',1,'y',2,'xy','yx','both',3,0), f'share={share} is invalid.'
    assert plot_row !=0, f'r={plot_row} is invalid.'
    assert plot_col !=0, f's={plot_col} is invalid.'
    if not plot_nr:
        plot_nr = 0
    if not plot_row:
        plot_row = 1
    if not plot_col:
        plot_col = 1
    if plot_row == 1 and plot_col == 1:
        figure_global_output, _ax_global_output = plt.subplots(num=plot_nr, dpi=set_dpi,figsize=fig_size)
        ax_global_output = [_ax_global_output]
    if plot_row > 1 or plot_col > 1:
        if share in ('x',1):
            figure_global_output,ax_global_output=plt.subplots(plot_row,plot_col,num=plot_nr,sharex=True, dpi=set_dpi)
        elif share in ('y',2):
            figure_global_output, ax_global_output = plt.subplots(plot_row,plot_col,num=plot_nr,sharey=True, dpi=set_dpi)
        elif share in ('xy','yx','both',3):
            figure_global_output, ax_global_output = plt.subplots(plot_row,plot_col,num=plot_nr,sharex=True,sharey=True, dpi=set_dpi)
        elif share == 0:
            figure_global_output, ax_global_output = plt.subplots(plot_row,plot_col,num=plot_nr,sharex=False,sharey=False, dpi=set_dpi)
    boundary_ax_global_fix = plot_row*plot_col
    figure_number_global_output = plot_nr
    share_axis_bool_output = share

def plot_data(p,xs,ys,ttl=None,dlab=None,xlab=None,ylab=None,ms=None,lw=None,ls=None,dcol=None,
                  plt_type=0,tight=True,mark=None,trsp=None,v_ax=None,
                  h_ax=None,no_ticks=False,share_ttl=False,legend_size=7):
    if len(ax_global_output) != boundary_ax_global_fix:
        axs = ax_global_output.flatten()
    else:
        axs = ax_global_output
    # chek for correct list input, and try fix if data-list is not in list
    assert isinstance(xs,(list,np.ndarray)), 'Wrong <xs> key, check _help() for more information.'
        # print('Error: ')
        # return nsh._help_runner(nanoscipy_help_prompt_global_output)
    if any(isinstance(i, (list,np.ndarray)) for i in xs) and any(isinstance(i, (float,int,np.integer,np.float)) for i in xs):
        print('Error: <xs> key only takes uniform input types, check _help() for more information')
        return
    if not all(isinstance(i, (list,np.ndarray)) for i in xs):
        xs_fix = [xs]
    else:
        xs_fix = xs
    if plt_type in (0,'plot',1,'scatter'):
        # if not isinstance(ys,(list,np.ndarray)):
        #     print('Error: Wrong <ys> key, check _help() for more information')
        #     return
        assert isinstance(ys,(list,np.ndarray)), 'Wrong <ys> key'
        if any(isinstance(i, (list,np.ndarray)) for i in ys) and any(isinstance(i, (float,int,np.integer,np.float)) for i in ys):
            print('Error: <ys> key only takes uniform input types, check _help() for more information')
            return
        if not all(isinstance(i, (list,np.ndarray)) for i in ys):
            ys_fix = [ys]
        else:
            ys_fix = ys
        # if len(xs_fix) != len(ys_fix):
        #     return print('<xs> and <ys> does not match. Please provide appropriate lists.')
        assert len(xs_fix) == len(ys_fix), '<xs> and <ys> does not match. Please provide appropriate lists.'

    datas = len(xs_fix)
    non = np.repeat(None,datas)
    ones = np.repeat(1,datas)

    opt_vars = [dlab,mark,ms,lw,dcol,ls,trsp]
    opt_vars_default = [non,['.']*datas,ones,ones,['black']*datas,
                        ['solid']*datas,ones]
    opt_vars_fix = []
    for i,j in zip(opt_vars,opt_vars_default):
        if not i:
            opt_vars_fix.append(j)
        elif not isinstance(i, (list,np.ndarray)):
            opt_vars_fix.append([i])
        else:
            opt_vars_fix.append(i)

    # set title according to share_ttl
    if share_ttl is False:
        axs[p].set_title(ttl)
    elif share_ttl is True:
        figure_global_output.suptitle(ttl)

    ds = range(datas)
    if plt_type in (0,'plot'):
        [axs[p].plot(xs_fix[n],ys_fix[n],c=opt_vars_fix[4][n],
                     label=opt_vars_fix[0][n],linewidth=opt_vars_fix[3][n],
                     markersize=opt_vars_fix[2][n],marker=opt_vars_fix[1][n],
                     linestyle=opt_vars_fix[5][n],
                     alpha=opt_vars_fix[6][n]) for n in ds]
    if plt_type in (1,'scatter'):
        [axs[p].scatter(xs_fix[n],ys_fix[n],c=opt_vars_fix[4][n],
                        label=opt_vars_fix[0][n],s=opt_vars_fix[2][n],
                        alpha=opt_vars_fix[6][n]) for n in ds]
    if plt_type in (2,'qqplot'):
        if isinstance(xs_fix,list):
            np_xs_fix = np.asarray(xs_fix)
        elif isinstance(xs_fix,np.ndarray):
            np_xs_fix = xs_fix
        if not ls:
            line_type = ['r']*datas
        elif not isinstance(ls, list):
            line_type = [ls]
        else:
            line_type = ls
        [qqplot(np_xs_fix[n],line=line_type[n],ax=axs[p],
                marker=opt_vars_fix[1][n],color=opt_vars_fix[4][n],
                label=opt_vars_fix[0][n],alpha=opt_vars_fix[6][n]) for n in ds]
        # axs[p].boxplot([xs_fix[n] for n in ds],labels=[opt_vars_fix[0][n] for n in ds])

    # fix labels according to share_axis_bool_output
    if share_axis_bool_output in ('x',1):
        axs[-1].set_xlabel(xlab)
        axs[p].set_ylabel(ylab)
    elif share_axis_bool_output in ('y',2):
        axs[p].set_xlabel(xlab)
        axs[0].set_ylabel(ylab)
    elif share_axis_bool_output in ('xy','yx','both',3):
        axs[-1].set_xlabel(xlab)
        axs[0].set_ylabel(ylab)
    elif share_axis_bool_output in ('no',0):
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
        axs[p].axhline(y=0,xmin=0,xmax=1,color='black',linestyle='solid',
                       linewidth=0.5,alpha=1)
    elif h_ax == 1:
        axs[p].axhline(y=0,xmin=0,xmax=1,color='black',linestyle='dashed',
                       linewidth=1,alpha=0.5)
    elif h_ax == 2:
        axs[p].axhline(y=0,xmin=0,xmax=1,color='black',linestyle='dotted',
                       linewidth=1,alpha=1)
    if v_ax == 0:
        axs[p].axvline(x=0,ymin=0,ymax=1,color='black',linestyle='solid',
                       linewidth=0.5,alpha=1)
    elif v_ax == 1:
        axs[p].axvline(x=0,ymin=0,ymax=1,color='black',linestyle='dashed',
                       linewidth=1,alpha=0.5)
    elif v_ax == 2:
        axs[p].axvline(x=0,ymin=0,ymax=1,color='black',linestyle='dotted',
                       linewidth=1,alpha=1)

    # set legends
    axs[p].legend(fontsize=legend_size)
    plt.rcParams.update({'font.family':'Times New Roman'})
    return

def string_to_float(potential_float):
    try:
        set_float = float(potential_float)
        return set_float
    except ValueError:
        return potential_float

def file_select(path,set_cols=None,cut_rows=None,separator=None,py_axlist=True,
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
        set_cols_fixed = [0,1]
    if isinstance(set_cols,int):
        set_cols_fixed = [set_cols]
    else:
        set_cols_fixed = set_cols
    # if not cut_rows:
    #     try:
    #         cut_rows = 1
    #     except ValueError:
    #         while ValueError:
                # cut_rows =+1
    allowed_extensions = ['.csv','.txt','.excel','.xlsx','.dat']
    file_extension = os.path.splitext(path)[1]

    assert file_extension in allowed_extensions, f'Selected file type {file_extension} is invalid'
    # try to define standard delimiter, if none is defined
    if not separator:
        if file_extension == '.csv':
            separator = ','
        elif file_extension in ('.txt','.dat'):
            if as_matrix is True:
                separator = None
            elif as_matrix is False:
                separator = '\t'
    if file_extension in ('.excel','.xlsx'):
        data = pd.read_excel(path,header=cut_rows,usecols=set_cols_fixed).to_numpy()
    elif file_extension in ('.csv','.txt','.dat'):
        if as_matrix is True:
            data = np.loadtxt(fname=path,delimiter=separator,skiprows=cut_rows)
        elif as_matrix is False:
            data = pd.read_csv(path,header=cut_rows,usecols=set_cols_fixed, sep=separator).to_numpy()
    if py_axlist is True:
        data_axlist = [data[:,i].tolist() for i in range(len(data[0]))]
        data_axlist_fix = [[string_to_float(i) for i in data_axlist[j]] for j in range(len(data_axlist))]
        return data_axlist_fix
    if py_axlist is False:
        return data

def fit_data(function,x_list,y_list,g_list,rel_var=False,N=None,mxf=1000,extMin=None,extMax=None):
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
    assert function, 'No function provided to fit.'
    assert x_list, 'No x-list provided.'
    assert y_list, 'No y-list provided.'
    assert g_list, 'No guess-list provided.'
    if not N:
        N = len(x_list)
    if not extMin:
        xMin = np.min(x_list)
    else:
        xMin = extMin
    if not extMax:
        xMax = np.max(x_list)
    else:
        xMax = extMax
    popt, pcov = curve_fit(f=function,xdata=x_list,ydata=y_list,p0=g_list,
                           absolute_sigma=rel_var,maxfev=mxf)
    pcov_fix = [pcov[i][i] for i in range(len(popt))]
    pstd = [np.sqrt(pcov_fix[i]) for i in range(len(popt))]

    xs_fit = np.linspace(xMin,xMax,N)
    if len(popt) == 1:
        ys_fit = function(xs_fit,popt[0])
    elif len(popt) == 2:
        ys_fit = function(xs_fit,popt[0],popt[1])
    elif len(popt) == 3:
        ys_fit = function(xs_fit,popt[0],popt[1],popt[2])
    elif len(popt) == 4:
        ys_fit = function(xs_fit,popt[0],popt[1],popt[2],popt[3])
    elif len(popt) == 5:
        ys_fit = function(xs_fit,popt[0],popt[1],popt[2],popt[3],popt[4])
    elif len(popt) == 6:
        ys_fit = function(xs_fit,popt[0],popt[1],popt[2],popt[3],popt[4],
                          popt[5])
    elif len(popt) == 7:
        ys_fit = function(xs_fit,popt[0],popt[1],popt[2],popt[3],popt[4],
                          popt[5],popt[6])
    assert len(popt)<8, 'Too many constants to fit (max is 7).'
    return popt, pcov_fix, pstd, xs_fit, ys_fit

def stepFinder(xData,yData,delta=30,lin=0.005,err=0.005):
    '''
    Determine averages of linear-horizontal data determined by delta, with a
    set horizontal liniarity and maximum error.

    Parameters
    ----------
    xData : list
        List of x-values in data set.
    yData : list
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
    xsPoint : list
        x-values for determined points.
    ysPoint : list
        y-values for determined points.

    '''
    linFit = lambda x,a,b: a*x+b
    i = 0
    f = i+delta
    x_test, y_test = xData[i:f], yData[i:f]
    popt, pcov_fix, pstd, xs_fit, ys_fit = fit_data(linFit,x_test,y_test,[0,1])
    xsPoint, ysPoint = [], []
    while f<len(xData):
        i += 1
        f = i+delta
        x_test, y_test = xData[i:f], yData[i:f]
        popt, pcov_fix, pstd, xs_fit, ys_fit = fit_data(linFit,x_test,y_test,
                                                        [0,1])
        if abs(popt[0])<lin and pstd[0]<err:
            xsPoint.append(sts.mean(xs_fit))
            ysPoint.append(sts.mean(ys_fit))
    return xsPoint, ysPoint

def data_extrema(data,pos_index=False,pos_range=None):
    """
    Determines extremas in a selected region. Can also identify the
    list-position of the extrema. Note that by extrema; it finds only the
    global extremas, as these are the maximum and minimum values of the data
    set.

    Parameters
    ----------
    data : list
        Data for determining extremas.
    pos_index : bool, optional
        Determines whether the extremas should have their list positions
        indexed. This yields an additional output list; index_list.
        The default is False.
    pos_range : list of ints, optional
        Needs a starting point and an ending point, defining the range.
        The default is [0,-1].

    Returns
    -------
    min_val : int
        The minimum of the dataset (packed as a list with the maximum).
    max_val : int
        The maximum of the data set (packed as a list with the minimum).
    indes_list : list
        Contains the index of the minimum and the maximum (in that order).

    """

    if not pos_range:
        pos_range = [0,-1]
    max_id = np.where(max(data[pos_range[0]:pos_range[1],1]) == data)[0][0] # index max val
    max_val = [data[max_id,0],data[max_id,1]] # find max val coord
    min_id = np.where(min(data[pos_range[0]:pos_range[1],1]) == data)[0][0] # index min val
    min_val = [data[min_id,0],data[min_id,1]] # find min val coord
    if pos_index is False:
        return [min_val,max_val]
    if pos_index is True:
        index_raw = [np.where(data[:,0] == min_val[0]),np.where(data[:,0] == max_val[0])] # index extremas
        index_list = [[index_raw[0][0][0]],[index_raw[1][0][0]]]
        return [min_val,max_val], index_list
