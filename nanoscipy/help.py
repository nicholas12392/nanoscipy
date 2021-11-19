def _help_terminator():
    print('≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡ HELP FUNCTION INACTIVE ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡')
    return

def _help_plot_grid():
    print()
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
        print('-- Input: numeral values of both integer and non-integer type (integers recommended)')
        print('-- Default: int(0)')
        print('<r> defines the number of rows of plots in the figure')
        print('-- Input: integers >= 1')
        print('-- Default: int(1)')
        print('<s> defines the number of columns of plots in the figure')
        print('-- Input: integers')
        print('-- Default: int(1) >= 1')
        print('<share> defines which axis´ should be shared')
        print('-- Input: if int(1) or string(x), x-axis´ are shared, if int(2) or string(y), y-axis´ are shared, if int(3), string(xy), string(yx) or string(both), xy-axis´ are shared, if int(0) or string(no),  no axis´ are shared')
        print('-- Default: int(0)')
        help_terminator = input('Terminate _help(): 0, back to parent: -1: ')
        if help_terminator == '0':
            _help_terminator()
        elif help_terminator == '-1':
            _help_plot_grid()
    elif help_id_inner == '2':
        print('-------- Output --------')
        print('<figure_global_output> (global) defined by matplotlib.pyplot.subplots() figure')
        print('<ax_global_output> (global) defined by matplotlib.pyplot.subplots() axis')
        print('<figure_number_global_output> (global) defined by <nr>')
        print('<share_axis_bool_output> (global) defined by <share>')
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
    print()
    print('================ plot_data() ================')
    print('This function plots input data according to the grid defined by plot_grid(), and can plot multiple data sets in multiple different ways.')
    print('More options below:')
    print('1: Variables')
    print('2: Output')
    print('0: Terminate _help()')
    print('-1: Go back')
    help_id_inner = input('Choose from list: ')
    if help_id_inner == '1': 
        print('-------- Variables --------')
        print('<p> defines the plot indexing number')
        print('-- Input: integers >= 0')
        print('-- Default: int(0)')
        print('<xs> defines the lists (this variable is a list consisting of lists), thus if only one x-list is ')
        print('-- Input: integers')
        print('-- Default: int(1)')
        print('<s> defines the number of columns of plots in the figure')
        print('-- Input: integers')
        print('-- Default: int(1)')
        print('<share> defines which axis´ should be shared')
        print('-- Input: if int(1) or string(x), x-axis´ are shared, if int(2) or string(y), y-axis´ are shared, if int(3), string(xy), string(yx) or string(both), xy-axis´ are shared, if int(0) or string(no),  no axis´ are shared')
        print('-- Default: int(0)')
        help_terminator = input('Terminate _help(): 0, back to parent: -1: ')
        if help_terminator == '0':
            _help_terminator()
        elif help_terminator == '-1':
            _help_plot_grid()
    elif help_id_inner == '2':
        print('-------- Output --------')
        print('<figure_global_output> (global) defined by matplotlib.pyplot.subplots() figure')
        print('<ax_global_output> (global) defined by matplotlib.pyplot.subplots() axis')
        print('<figure_number_global_output> (global) defined by <nr>')
        print('<share_axis_bool_output> (global) defined by <share>')
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

def _help(x=0):
    print()
    if x == 0:
        print('≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡ HELP FUNCTION ACTIVE ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡')
    print('1: plot_grid()')
    print('2: plot_data()')
    print('0: Terminate function')
    help_id_outer = input('Choose from list above: ')
    if help_id_outer == '1':
        _help_plot_grid()
        return
    elif help_id_outer == '2':
        _help_plot_data()
        return
    elif help_id_outer == '0':
        _help_terminator()
