import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from statsmodels.graphics.gofplots import qqplot
from scipy.optimize import curve_fit

def plot_grid(nr=0,r=1,s=1,share=0):
    global figure_global_output
    global ax_global_output
    global figure_number_global_output
    figure_number_global_output = nr
    
    if r == 1 and s == 1:
        figure_global_output, _ax_global_output = plt.subplots(num=nr)
        ax_global_output = [_ax_global_output]
    if r > 1 or s > 1:
        if share == 'x' or share == 1:
            figure_global_output, ax_global_output = plt.subplots(r,s,num=nr,sharex=True)
        if share == 'y' or share == 2:
            figure_global_output, ax_global_output = plt.subplots(r,s,num=nr,sharey=True)
        if share == 'xy' or share == 'yx' or share == 'both' or share == 3:
            figure_global_output, ax_global_output = plt.subplots(r,s,num=nr,sharex=True,sharey=True)
        if share == 'no' or share == 0:
            figure_global_output, ax_global_output = plt.subplots(r,s,num=nr,sharex=False,sharey=False)
    
    global boundary_ax_global_fix
    boundary_ax_global_fix = r*s

def plot_data(p=0,xs=[],ys=[],ttl=None,dlab=[],xlab=None,
                  ylab=None,ms=[],lw=[],ls=[],dcol=[],
                  plt_type=0,beta=0,tight=True,mark=[],v_ax=[True,'black','dashed',0.5],
                  h_ax=[True,'black','dashed',0.5],no_ticks=False):
    if len(ax_global_output) != boundary_ax_global_fix:
        axs = ax_global_output.flatten()
    else:
        axs = ax_global_output
    datas = len(xs)
    non = np.repeat(None,datas)
    one = np.repeat(1,datas)
    if not dlab:
        dlab = non
    if not mark:
        mark = non
    if not ms: 
        ms = one
    if not lw: 
        lw = one
    if not mark.any():
        mark = np.repeat('.',datas)
    if not dcol: 
        dcol = np.repeat('black',datas)
    if not ls:
        ls = np.repeat('solid',datas)
    axs[p].set_title(ttl) 
    ds = range(datas) 
    if plt_type == 0 or plt_type == 'plot': 
        [axs[p].plot(xs[n],ys[n],c=dcol[n],label=dlab[n],linewidth=lw[n],markersize=ms[n],
                     marker=mark[n],linestyle=ls[n]) for n in ds]  
    if plt_type == 1 or plt_type == 'scatter' or plt_type == 3 or plt_type == 'fit':
        [axs[p].scatter(xs[n],ys[n],c=dcol[n],label=dlab[n],s=ms[n]) for n in ds]  
    if plt_type == 2 or plt_type == 'qqplot':
        [qqplot(data=xs[n],line='r',ax=axs[p],marker=mark[n],color=dcol[n],label=dlab[n]) for n in ds]
        axs[p+1].boxplot([xs[n] for n in ds],labels=[dlab[n] for n in ds]) 
    if beta == 1:
        axs[p+beta].set_xlabel(xlab)
        axs[p].set_ylabel(ylab)
        axs[p+beta].set_ylabel(ylab)
    if beta == 0: 
        axs[p].set_xlabel(xlab)
        axs[p].set_ylabel(ylab)
    [axs[p+i].legend() for i in range(0,beta+1)]
    if tight == True:
        plt.tight_layout()
    if no_ticks == True:
        axs[p].set_yticks([])
        axs[p].set_xticks([])
    if h_ax == False:
        h_ax == [False]
    elif h_ax[0] == True:
        plt.axhline(y=0,xmin=0,xmax=1,color=h_ax[1],linestyle=h_ax[2],linewidth=1,alpha=v_ax[3])
    if v_ax == False:
        v_ax = [False]
    elif v_ax[0] == True:
        plt.axvline(x=0,ymin=0,ymax=1,color=v_ax[1],linestyle=v_ax[2],linewidth=1,alpha=v_ax[3]) 
    axs[p].figure(figure_number_global_output, dpi=300)
        
def file_select(path=None,set_cols=[0,1],cut_first_row=True): 
    if path == None: 
        print('Error: No path selected')
        return
    else:
        filename, file_extension = os.path.splitext(path)
    if file_extension == '.excel':
        data = pd.read_excel(path,usecols=set_cols).to_numpy()
    elif file_extension == '.csv':
        data = pd.read_csv(path,usecols=set_cols, sep=';').to_numpy()
    else:
        print('Error: Selected file type is not valid (use help function to see allowed file types)')
        return
    if cut_first_row == True:
        data_fix = data[1:,:]
    elif cut_first_row == False: 
        data_fix = data
    elif isinstance(cut_first_row,int) == True:
        data_fix = data[cut_first_row:,:]
    return data_fix

def fit_data(function=None,x_list=[],y_list=[],g_list=[],abs_var=True,N=100,mxf=5000):
    popt, pcov = curve_fit(f=function,xdata=x_list,ydata=y_list,p0=g_list,absolute_sigma=abs_var,maxfev=mxf)
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
        print('Error: Too many constants to fit')
        return
    return popt, pcov_fix, pstd, xs_fit, ys_fit
