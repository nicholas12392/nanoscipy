def _help_terminator():
    print('≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡ HELP FUNCTION INACTIVE ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡')
    return

def _help_plot_grid():
    print('================ plot_grid() ================')
    print('This function serves the purpose of defining a "grid" for the plot_data() function, which allows for plotting of multiple data sets in however many different plots desired.')
    print('More options below:')
    print('1: Variables')
    print('2: Output')
    print('0: Terminate _help()')
    print('-1: Go back')
    help_id_inner = input('Choose from list: ')
    if help_id_inner == '1': 
        print('-------- Variables --------')
        print('<nr> defines the figure number')
        print('--- Input: numeral values of both integer and non-integer type (integers recommended)')
        print('--- Default: 0')
        print()
        print('<r> defines the number of rows of plots in the figure')
        print('--- Input: integers >= 1')
        print('--- Default: 1')
        print()
        print('<s> defines the number of columns of plots in the figure')
        print('--- Input: integers >= 1')
        print('--- Default: 1')
        print()
        print('<share> defines which axis´ should be shared')
        print('--- Input: if 1 or ´\'x\', x-axis´ are shared, if 2 or \'y\', y-axis´ are shared, if 3, \'xy\', \'yx\' or \'both\', xy-axis´ are shared, if 0 or None,  no axis´ are shared')
        print('--- Default: None')
        help_terminator = input('Terminate _help(): 0, back to parent: -1: ')
        if help_terminator == '0':
            _help_terminator()
        elif help_terminator == '-1':
            _help_plot_grid()
    elif help_id_inner == '2':
        print('-------- Output --------')
        print('<figure_global_output> (global) defined by matplotlib.pyplot.subplots() figure')
        print()
        print('<ax_global_output> (global) defined by matplotlib.pyplot.subplots() axis')
        print()
        print('<figure_number_global_output> (global) defined by <nr>')
        print()
        print('<share_axis_bool_output> (global) defined by <share>')
        print()
        print('<boundary_ax_global_fix> (global) defined as product of <r> and <s>')
        help_terminator = input('Terminate _help(): 0, back to parent: -1: ')
        if help_terminator == '0':
            _help_terminator()
        elif help_terminator == '-1':
            _help_plot_grid()
    elif help_id_inner == '-1':
        _help(1)
    elif help_id_inner == '0':
        _help_terminator()

def _help_plot_data():
    print('================ plot_data() ================')
    print('This function plots input data according to the grid defined by plot_grid(), and can plot multiple data sets in multiple different ways.')
    print('More options below:')
    print('1: Variables')
    print('2: Output')
    print('3: Notes')
    print('0: Terminate _help()')
    print('-1: Go back')
    help_id_inner = input('Choose from list: ')
    if help_id_inner == '1': 
        print('-------- Variables --------')
        print('<p> defines the plot indexing number')
        print('--- Input: integers >= 0')
        print('--- Default: 0')
        print()
        print('<xs> defines the lists (this variable is a list consisting of lists), thus if only one x-list is the script will try to construct a parent list')
        print('--- Input: if single xs-list, input just that list, if multiple x-lists, input those lists in a list')
        print('--- Default: N/A')
        print()
        print('<ys> defines the lists (this variable is a list consisting of lists), thus if only one y-list is the script will try to construct a parent list')
        print('--- Input: if single y-list, input just that list, if multiple y-lists, input those lists in a list')
        print('--- Default: N/A')
        print()
        print('<ttl> defines the title of the subplots (or figure title if share_ttl=True)')
        print('--- Input: string')
        print('--- Default: None')
        print()
        print('<dlab> defines data-labels')
        print('--- Input: list of strings corresponding to number of plotted data sets (len(xs))')
        print('--- Default: N/A')
        print()
        print('<xlab> defines common x-label for all plots')
        print('--- Input: string')
        print('--- Default: None')
        print()
        print('<ylab> defines common y-label for all plots')
        print('--- Input: string')
        print('--- Default: None')
        print()
        print('<ms> defines marker size if needed')
        print('--- Input: numeral values >= 0')
        print('--- Default: 1')
        print()
        print('<lw> defines line width if needed')
        print('--- Input: numeral values >= 0')
        print('--- Default: 1')
        print()
        print('<ls> defines line style if needed')
        print('--- Input: list of strings corresponding to number of plotted data sets (len(xs)) according to matplotlib.pyplot´s line styles: https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html')
        print('--- Default: \'solid\'')
        print()
        print('<dcol> data color; defines color of plotted data points or lines')
        print('--- Input: list of color strings corresponding to number of plotted data sets (len(xs)) according to matplotlib.pyplot´s colors: https://matplotlib.org/stable/gallery/color/named_colors.html')
        print('--- Default: \'black\'')
        print()
        print('<plt_type> defines the plot type')
        print('--- Input: if 0 or \'plot\'; plots data as axs[].plot(), if 1 or \'scatter\' plots as axs.scatter(), 3 or \'qqplot\' plots a qqplot in axs[], and a axs[+1].boxplot()')
        print('--- Default: 0')
        print()
        print('<tight> fixes tight layout according to bool')
        print('--- Input: bool')
        print('--- Default: True')
        print()
        print('<mark> defines marker type of plotted data if needed')
        print('--- Input: list of marker type strings corresponding to number of plotted data sets (len(xs)) according to https://matplotlib.org/stable/api/markers_api.html')
        print('--- Default: \'.\'')
        print()
        print('<trsp> determmines the transparency of the data dots or lines (the alpha of the data-plot)')
        print('--- Input: list of numerical values from 0 to 1 corresponding to number of plotted data sets (len(xs))')
        print('--- Default: 1')
        print()
        print('<v_ax> defines a preset vertical axis')
        print('--- Input: if None; display no axis, if 0; display solid standard axis line, if 1; display dashed axis line, if 2; display dotted axis line')
        print('--- Default: None')
        print()
        print('<h_ax> defines a preset horisontal axis')
        print('--- Input: if None; display no axis, if 0; display solid standard axis line, if 1; display dashed axis line, if 2; display dotted axis line')
        print('--- Default: None')
        print()
        print('<no_ticks> determines whether or not axis ticks are visible')
        print('--- Input: if False; visible ticks, if True; invisible ticks')
        print('--- Default: False')
        print()
        print('<share_ttl> determines if the plot titles should be shared as a figure title')
        print('--- Input: bool')
        print('--- Default: False')
        help_terminator = input('Terminate _help(): 0, back to parent: -1: ')
        if help_terminator == '0':
            _help_terminator()
        elif help_terminator == '-1':
            _help_plot_data()
    elif help_id_inner == '2':
        print('-------- Output --------')
        print('A simple or advanced plot of data with the corresponding inputs, in one or multiple plots')
        help_terminator = input('Terminate _help(): 0, back to parent: -1: ')
        if help_terminator == '0':
            _help_terminator()
        elif help_terminator == '-1':
            _help_plot_data()
    elif help_id_inner == '3':
        print('-------- Notes --------')
        print('It is important to note that this function is based on matplotlib.pyplot, and will therefore work with additions such as .set_xlim or .vlines etc.')
        help_terminator = input('Terminate _help(): 0, back to parent: -1: ')
        if help_terminator == '0':
            _help_terminator()
        elif help_terminator == '-1':
            _help_plot_data()
    elif help_id_inner == '-1':
        _help(1)
    elif help_id_inner == '0':
        _help_terminator()

def _help_file_select():
    print('================ file_select() ================')
    print('This function selects and extracts data, from a file at a specified path. It can be useful to index multiple data files in a way, that allows for easy extration in a for-loop.')
    print('More options below:')
    print('1: Variables')
    print('2: Output')
    print('3: Notes')
    print('0: Terminate _help()')
    print('-1: Go back')
    help_id_inner = input('Choose from list: ')
    if help_id_inner == '1': 
        print('-------- Variables --------')
        print('<path> defines the file path, note that you might want to do this as an r-string (and if for-loop; part as an f-string)')
        print('--- Input: string')
        print('--- Default: None')
        print()
        print('<set_cols> defines which columns should be extracted from the file')
        print('--- Input: list of the column indexes you want extracted (note that this is not a range, but specific selection)')
        print('--- Default: [0,1]')
        print()
        print('<cut_rows> cuts the set number of rows from the data set')
        print('--- Input: if integer; cut from row 0 to specified integer, if list; cut the specified rows from the list')
        print('--- Default: 1')
        print()
        print('<separator> define the deliminter of the data set (if nescessary)')
        print('--- Input: string')
        print('--- Default: if .csv; \',\', if .txt; \'\\t\'')
        help_terminator = input('Terminate _help(): 0, back to parent: -1: ')
        if help_terminator == '0':
            _help_terminator()
        elif help_terminator == '-1':
            _help_file_select()
    elif help_id_inner == '2':
        print('-------- Output --------')
        print('<data> (local) the data gained from the file to lists')
        help_terminator = input('Terminate _help(): 0, back to parent: -1: ')
        if help_terminator == '0':
            _help_terminator()
        elif help_terminator == '-1':
            _help_file_select()
    elif help_id_inner == '3':
        print('-------- Notes --------')
        print('In the current patch, there is an issue, where if you are to import data from a file that contains a string as the first row, every list-element will be a string. Thus, if this issue occurs, simply set cut_rows >= 1')
        print('If the error type: \'Usecols do not match columns, columns expected but not found:\' occur, then the function is most likely using the wrong separator/delimiter (assuming values exist in these columns initially)')
        help_terminator = input('Terminate _help(): 0, back to parent: -1: ')
        if help_terminator == '0':
            _help_terminator()
        elif help_terminator == '-1':
            _help_file_select()
    elif help_id_inner == '-1':
        _help(1)
    elif help_id_inner == '0':
        _help_terminator()

def _help(x=0):
    if x == 0:
        print('≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡ HELP FUNCTION ACTIVE ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡')
    print('1: plot_grid()')
    print('2: plot_data()')
    print('3: file_select()')
    print('0: Terminate function')
    help_id_outer = input('Choose from list above: ')
    if help_id_outer == '1':
        _help_plot_grid()
        return
    elif help_id_outer == '2':
        _help_plot_data()
        return
    elif help_id_outer == '3':
        _help_file_select()
        return
    elif help_id_outer == '0':
        _help_terminator()
