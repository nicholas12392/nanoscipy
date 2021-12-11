import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from statsmodels.graphics.gofplots import qqplot
from scipy.optimize import curve_fit
import nanoscipy.help as nsh
from itertools import chain
import csv

def global_help_prompt(prompt_id):
    global nanoscipy_help_prompt_global_output
    nanoscipy_help_prompt_global_output = prompt_id
    return

global_help_prompt(True)

def plot_grid(nr=0,r=1,s=1,share=None,set_dpi=300):
    global figure_global_output
    global ax_global_output
    global figure_number_global_output
    global share_axis_bool_output
    global boundary_ax_global_fix
    
    boundary_ax_global_fix = r*s
    figure_number_global_output = nr
    share_axis_bool_output = share
    
    if r == 1 and s == 1:
        figure_global_output, _ax_global_output = plt.subplots(num=nr, dpi=set_dpi)
        ax_global_output = [_ax_global_output]
    if r > 1 or s > 1:
        if share == 'x' or share == 1:
            figure_global_output, ax_global_output = plt.subplots(r,s,num=nr,sharex=True, dpi=set_dpi)
        elif share == 'y' or share == 2:
            figure_global_output, ax_global_output = plt.subplots(r,s,num=nr,sharey=True, dpi=set_dpi)
        elif share == 'xy' or share == 'yx' or share == 'both' or share == 3:
            figure_global_output, ax_global_output = plt.subplots(r,s,num=nr,sharex=True,sharey=True, dpi=set_dpi)
        elif share == None or share == 0 or not share:
            figure_global_output, ax_global_output = plt.subplots(r,s,num=nr,sharex=False,sharey=False, dpi=set_dpi)
        else: 
            print('Wrong <share> key, check _help() for more information')
            return nsh._help_runner(nanoscipy_help_prompt_global_output)
    elif r == 0 or s == 0: 
        print('Wrong <r> or <s> key, check _help() for more information')
        return nsh._help_runner(nanoscipy_help_prompt_global_output)
    return

def plot_data(p=0,xs=[],ys=[],ttl=None,dlab=[],xlab=None,ylab=None,ms=[],lw=[],ls=[],dcol=[],
                  plt_type=0,tight=True,mark=[],trsp=[],v_ax=None,
                  h_ax=None,no_ticks=False,share_ttl=False):
    if len(ax_global_output) != boundary_ax_global_fix:
        axs = ax_global_output.flatten()
    else:
        axs = ax_global_output
    
    # chek for correct list input, and try fix if data-list is not in list
    if not isinstance(xs,(list,np.ndarray)):
        print('Error: Wrong <xs> key, check _help() for more information')
        return nsh._help_runner(nanoscipy_help_prompt_global_output)
    elif any(isinstance(i, (list,np.ndarray)) for i in xs) and any(isinstance(i, (float,int,np.integer,np.float)) for i in xs):
        print('Error: <xs> key only takes uniform input types, check _help() for more information')
        return nsh._help_runner(nanoscipy_help_prompt_global_output)
    elif not all(isinstance(i, (list,np.ndarray)) for i in xs):
        xs_fix = [xs]
    else: 
        xs_fix = xs
    if plt_type == 0 or plt_type == 'plot' or plt_type == 1 or plt_type == 'scatter':
        if not isinstance(ys,(list,np.ndarray)):
            print('Error: Wrong <ys> key, check _help() for more information')
            return nsh._help_runner(nanoscipy_help_prompt_global_output)
        elif any(isinstance(i, (list,np.ndarray)) for i in ys) and any(isinstance(i, (float,int,np.integer,np.float)) for i in ys):
            print('Error: <ys> key only takes uniform input types, check _help() for more information')
            return nsh._help_runner(nanoscipy_help_prompt_global_output)
        elif not all(isinstance(i, (list,np.ndarray)) for i in ys):
            ys_fix = [ys]
        else: 
            ys_fix = ys
    
    datas = len(xs_fix)
    non = np.repeat(None,datas)
    ones = np.repeat(1,datas)
    
    opt_vars = [dlab,mark,ms,lw,dcol,ls,trsp]
    opt_vars_default = [non,['.']*datas,ones,ones,['black']*datas,['solid']*datas,ones]
    opt_vars_fix = []
    for i,j in zip(opt_vars,opt_vars_default):
        if not i:
            opt_vars_fix.append(j)
        elif not isinstance(i, (list,np.ndarray)):
            opt_vars_fix.append([i])
        else:
            opt_vars_fix.append(i)
            
    # set title according to share_ttl
    if share_ttl == False:
        axs[p].set_title(ttl) 
    elif share_ttl == True:
        figure_global_output.suptitle(ttl)
        
    ds = range(datas) 
    if plt_type == 0 or plt_type == 'plot': 
        [axs[p].plot(xs_fix[n],ys_fix[n],c=opt_vars_fix[4][n],label=opt_vars_fix[0][n],linewidth=opt_vars_fix[3][n],markersize=opt_vars_fix[2][n],
                     marker=opt_vars_fix[1][n],linestyle=opt_vars_fix[5][n],alpha=opt_vars_fix[6][n]) for n in ds]  
    if plt_type == 1 or plt_type == 'scatter':
        [axs[p].scatter(xs_fix[n],ys_fix[n],c=opt_vars_fix[4][n],label=opt_vars_fix[0][n],s=opt_vars_fix[2][n],alpha=opt_vars_fix[6][n]) for n in ds]  
    if plt_type == 2 or plt_type == 'qqplot':
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
        [qqplot(np_xs_fix[n],line=line_type[n],ax=axs[p],marker=opt_vars_fix[1][n],color=opt_vars_fix[4][n],label=opt_vars_fix[0][n],alpha=opt_vars_fix[6][n]) for n in ds]
    
    # fix labels according to share_axis_bool_output
    if share_axis_bool_output == 'x' or share_axis_bool_output == 1:
        axs[-1].set_xlabel(xlab)
        axs[p].set_ylabel(ylab)
    elif share_axis_bool_output == 'y' or share_axis_bool_output == 2: 
        axs[p].set_xlabel(xlab)
        axs[0].set_ylabel(ylab)
    elif share_axis_bool_output == 'xy' or share_axis_bool_output == 'yx' or share_axis_bool_output == 'both' or share_axis_bool_output == 3:
        axs[-1].set_xlabel(xlab)
        axs[0].set_ylabel(ylab) 
    elif share_axis_bool_output == 'no' or share_axis_bool_output == 0:
        axs[p].set_xlabel(xlab)
        axs[p].set_ylabel(ylab) 
    
    # set fitted layout according to tight
    if tight == True:
        plt.tight_layout()
        
    # set axis tics according to no_ticks
    if no_ticks == True:
        axs[p].set_yticks([])
        axs[p].set_xticks([])
    
    if h_ax == 0:
        axs[p].axhline(y=0,xmin=0,xmax=1,color='black',linestyle='solid',linewidth=0.5,alpha=1)
    elif h_ax == 1:
        axs[p].axhline(y=0,xmin=0,xmax=1,color='black',linestyle='dashed',linewidth=1,alpha=0.5)
    elif h_ax == 2: 
        axs[p].axhline(y=0,xmin=0,xmax=1,color='black',linestyle='dotted',linewidth=1,alpha=1)
    if v_ax == 0:
        axs[p].axhline(x=0,ymin=0,ymax=1,color='black',linestyle='solid',linewidth=0.5,alpha=1)
    elif v_ax == 1:
        axs[p].axvline(x=0,ymin=0,ymax=1,color='black',linestyle='dashed',linewidth=1,alpha=0.5) 
    elif v_ax == 2:
        axs[p].axhline(x=0,ymin=0,ymax=1,color='black',linestyle='dotted',linewidth=1,alpha=1)
    
    # set legends
    axs[p].legend() 
    return
        
def file_select(path=None,set_cols=[0,1],cut_rows=0,separator=None,py_axlist=False,as_matrix=False): 
    if path == None: 
        print('Error: No path selected')
        return
    else:
        filename, file_extension = os.path.splitext(path)
    
    # try to define standard delimiter, if none is defined
    if separator == None: 
        if file_extension == '.csv':
            separator = ','
        elif file_extension == '.txt':
            if as_matrix == True:
                separator = None
            elif as_matrix == False:
                separator = '\t'
    if file_extension == '.excel' or file_extension == '.xlsx':
        data = pd.read_excel(path,header=cut_rows,usecols=set_cols).to_numpy()
    elif file_extension == '.csv' or file_extension == '.txt':
        if as_matrix == True:
            data = np.loadtxt(fname=path,delimiter=separator,skiprows=cut_rows)
        elif as_matrix == False:
            data = pd.read_csv(path,header=cut_rows,usecols=set_cols, sep=separator).to_numpy()
    else:
        print('Error: Selected file type is not valid (use help function to see allowed file types)')
        return nsh._help_runner(nanoscipy_help_prompt_global_output)
    if py_axlist == True: 
        data_axlist = [data[:,i].tolist() for i in range(len(data[0]))]
        return data, data_axlist
    elif py_axlist == False: 
        return data

def fit_data(function=None,x_list=[],y_list=[],g_list=[],rel_var=False,N=100,mxf=1000):
    popt, pcov = curve_fit(f=function,xdata=x_list,ydata=y_list,p0=g_list,absolute_sigma=rel_var,maxfev=mxf)
    pcov_fix = [pcov[i][i] for i in range(len(popt))]
    pstd = [np.sqrt(pcov_fix[i]) for i in range(len(popt))]
    xs_fit = np.linspace(np.min(x_list),np.max(x_list),N)
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
        ys_fit = function(xs_fit,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])
    elif len(popt) == 7:
        ys_fit = function(xs_fit,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5],popt[6])
    else: 
        print('Error: Too many constants to fit (max is 7)')
        return
    return popt, pcov_fix, pstd, xs_fit, ys_fit

def data_extrema(function,pos_index=False): 
    data = function
    max_id = np.where(max(data[:,1]) == data)[0][0] # index max val
    max_val = [data[max_id,0],data[max_id,1]] # find max val coord
    min_id = np.where(min(data[:,1]) == data)[0][0] # index min val
    min_val = [data[min_id,0],data[min_id,1]] # find min val coord
    if pos_index == False:
        return [min_val,max_val]
    elif pos_index == True:
        index_raw = [np.where(data[:,0] == min_val[0]),np.where(data[:,0] == max_val[0])] # index extremas
        index_list = [[index_raw[0][0][0]],[index_raw[1][0][0]]]
        return [min_val,max_val], index_list
