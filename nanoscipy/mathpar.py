import nanoscipy.util as nsu
import numpy as np
import sympy as sp
import scipy.constants as spc
import mpmath
from itertools import chain

supported_natural_constants = ('pi', '_hbar', '_NA', '_c', '_h', '_R', '_k', '_e', '_me', '_mp')
natural_constant_values = tuple([str(i) for i in (spc.pi, spc.hbar, spc.N_A, spc.c, spc.h, spc.R, spc.k, spc.e,
                                                  spc.electron_mass, spc.proton_mass)])
supported_functions = ('sinh(', 'cosh(', 'tanh(', 'exp(', 'sin(', 'cos(', 'tan(', 'ln(', 'rad(', 'deg(', 'log(',
                       'sqrt(', 'arcsin(', 'arccos(', 'arctan(', 'arcsinh(', 'arccosh(', 'arctanh(')
supported_symbols = ('(', ')', '+', '-', '/', '*', '^', '!')


def basic_operations(operator, fir_int, sec_int=None):
    """
    Perform basic operations on two numeric values.

    Parameters
        operator : str
            The operator representing, which operation is to be performed on the two values. Options: '+', '-', '+-',
            '*', '*-', '/', '/-', '^', '^-', '!'.
        fir_int : float
            The first value.
        sec_int : float, optional
            The second value. The default is None.

    Returns
        Product of the operation.
    """

    # check if any of the variables are of type nan
    if 'n' in (fir_int, sec_int):
        # if true, output nan result
        return np.float64('nan')
    elif isinstance(fir_int, str):
        raise ValueError(f'No value found for \'{fir_int}\'.')
    elif isinstance(sec_int, str):
        raise ValueError(f'No value found for \'{sec_int}\'.')

    if operator == '+':
        opr_res = fir_int + sec_int
    elif operator in ('-', '+-'):
        opr_res = fir_int - sec_int
    elif operator == '*':
        opr_res = fir_int * sec_int
    elif operator == '*-':
        opr_res = fir_int * - sec_int
    elif operator == '/':
        opr_res = fir_int / sec_int
    elif operator == '/-':
        opr_res = fir_int / - sec_int
    elif operator == '^':
        opr_res = fir_int ** sec_int
    elif operator == '^-':
        opr_res = fir_int ** - sec_int
    elif operator == '!':
        try:
            opr_res = np.math.factorial(nsu.float_to_int(fir_int, 'error'))
        except TypeError:
            opr_res = sp.gamma(fir_int + 1)
    else:
        opr_res = None
    return opr_res


def basic_parser(math_string_float, math_ops, direction='ltr', steps=False):
    """
    Operation parser that will perform operations according to the set operators.

    Parameters
        math_string_float : list
            Contains all the values of the mathematical 'string' as floats, whilst the operators are all strings.
        math_ops : tuple
            Contains all the operators that should be recognized in the particular mathematical 'string'.
        direction : str, optional
            Determines in which direction the while loop iterates. Options are from left to right (ltr), and from right
            to left (rtl). The default is 'ltr'.
        steps : bool, optional
            If True, displays balances from the script, whilst performing the operations. The default is False.

    Returns
        Updated string with the performed operations appended in the correct positions.
    """
    if any(i in math_string_float for i in math_ops):
        pre_index_chain = nsu.indexer(math_string_float)  # define index chain
        opr_id = [i for i, e in pre_index_chain if e in math_ops]  # find the index for the given operations

        # iterate over operators and execute in the set direction with the set initial iteration
        if direction == 'ltr':
            iterative = 0
        elif direction == 'rtl':
            iterative = len(math_string_float) - 1
        else:
            raise ValueError(f'Undefined direction {direction}.')
        temp_operations = math_string_float  # define temporary string
        temp_index_chain = pre_index_chain  # define temporary index
        temp_opr_id = opr_id  # define temporary operation index
        while iterative in (i for i, e in pre_index_chain):
            if iterative in temp_opr_id:  # if the iterator is an operator, perform operation, append and update string
                if math_ops == ('!',):  # if the given operation is a factorial

                    # perform operation and define exclusion
                    opr_res_temp = basic_operations(temp_operations[iterative], temp_operations[iterative - 1])
                    int_excl = [iterative - 1]
                else:
                    opr_res_temp = basic_operations(temp_operations[iterative], temp_operations[iterative - 1],
                                                    temp_operations[iterative + 1])  # perform operation
                    int_excl = [iterative - 1, iterative + 1]  # define exclusions

                # update temporary string according to exclusions and iterative index
                temp_operations = [opr_res_temp if k == iterative else j for k, j in temp_index_chain if k not in
                                   int_excl]
                temp_index_chain = nsu.indexer(temp_operations)  # update temporary index
                temp_opr_id = [i for i, e in temp_index_chain if e in math_ops]  # update temporary operation index
                if steps:
                    print(nsu.list_to_string(temp_operations))
                continue

            # update iterator depending on the direction
            if direction == 'ltr':
                iterative += 1
            if direction == 'rtl':
                iterative -= 1
        opr_string = temp_operations  # define a new string post operations
    else:
        opr_string = math_string_float  # if no operations were done, define post string as input string
    return opr_string


def number_parser(math_string):
    """
    Separates numbers in a list from a string. Supports scientific notation.

    Parameters
        math_string : str
            The mathematical string to perform separation on.

    Returns
        List containing the elements from the string, with the numbers separated.
    """
    # collect all values to split around and insert
    collective_items = supported_natural_constants + supported_functions + supported_symbols
    true_inserts = natural_constant_values + supported_functions + supported_symbols

    # sort items and split-replace
    sorted_items = nsu.list_sorter(collective_items + ('e+', 'e'), true_inserts + (['*', '10', '^'], ['*', '10', '^']),
                                   reverse=True, otype='tuple')
    split_input_string = nsu.multi_split(math_string, sorted_items[0], reps=sorted_items[1])
    return split_input_string


def ordered_parser(math_string, steps=False):
    """
    Performs operations on the given string in an ordered way. Firstly, powers are executed, secondly, products and
    divisions and at last additions and subtractions.

    Parameters
        math_string : str
            Contains the mathematical expression in a string.
        steps : bool, optional
            If True, displays balances from the script, whilst performing the operations. The default is False.

    Returns
        A float representing the result of the executed operations.
    """

    # if the first value of the fixed list is a '-', append to the next value, preventing interpretation as an operator
    fir_elem = math_string[0]
    if fir_elem == '-':
        sec_elem = math_string[1]
        if isinstance(sec_elem, str):
            post_float_string = ['-' + sec_elem] + math_string[2:]
        else:
            post_float_string = [-1 * sec_elem] + math_string[2:]
    else:
        post_float_string = math_string
    post_index_chain = nsu.indexer(post_float_string)  # define index for the fixed string

    # fix negative numbers by creating a negative operator. Note that this prevents powers from interpreting all values
    #   with a negative operator in front as a negative number; hence allows for -2^2=-4 and (-2)^2=4
    # empty lists for appending
    elem_index = []
    elem_excl = []
    for i, j in post_index_chain:
        i_next = i + 1
        j_next = None
        try:  # try to find the next values, if no such value, pass
            j_next = post_float_string[i_next]
        except IndexError:
            pass

        # if two elements are x and y, make a collective xy element, in place of x, and define exclusion index of y
        if (j, j_next) == ('*', '-'):
            elem = '*-'
            elem_excl.append(i_next)
        elif (j, j_next) == ('/', '-'):
            elem = '/-'
            elem_excl.append(i_next)
        elif (j, j_next) == ('^', '-'):
            elem = '^-'
            elem_excl.append(i_next)
        elif (j, j_next) == ('+', '-') or (j, j_next) == ('-', '+'):
            elem = '+-'
            elem_excl.append(i_next)
        elif (j, j_next) == ('-', '-'):
            elem = '+'
            elem_excl.append(i_next)
        else:  # for all other elements, define current iterative as value
            elem = j
        elem_index.append([i, elem])

    # define new list of strings: replace elements that should be collective elements, and remove excess defined by
    #   elem_excl
    float_string_str = [i[1] if i != j else j[1] for i, j in zip(elem_index, post_index_chain) if j[0] not in elem_excl]
    float_string = [nsu.string_to_float(i) for i in float_string_str]  # convert string to float if possible

    # check for 1. default operation order
    o1_opr_string = basic_parser(float_string, ('^', '^-'), 'rtl', steps)

    # check for 2. default operation order
    o2_opr_string = basic_parser(o1_opr_string, ('!',), 'ltr', steps)

    # check for 3. default operation order
    o3_opr_string = basic_parser(o2_opr_string, ('*', '/', '*-', '/-'), 'ltr', steps)

    # check for 4. default operation order
    o4_opr_string = basic_parser(o3_opr_string, ('+', '-', '+-'), 'ltr', steps)

    return o4_opr_string[0]


def product_parser(string, items, exclusions=None):
    """
        Parser that detects implicit multiplication and adds multiplication operator in those positions. Note
        importantly that this script works by splitting the string around every exclusion (the largest exclusion first -
        once an exclusion has been split, it cannot be further split), and then adding an operator in every gap in the
        new list, if the last value of the current string is not a mathematical symbol, and the first value of the next
        string is not a mathematical symbol.

        Parameters
            string : str
                The mathematical string to search for implicit multiplication.
            items : str, tuple
                Items that implicit multiplication will be done around if appropriate.
            exclusions : str, tuple
                Elements that should not be considered to have fixed products.

        Returns
            Updated string with the implicit multiplication as explicit.
        """

    if exclusions:  # fix exclusions to tuple
        exclusions = nsu.nest_checker(exclusions, 'tuple')
    else:
        exclusions = tuple([])

    # split the given string around the given items, making sure that the largest items are iterated through first
    math_ops = ('(', ')', '+', '-', '/', '*', '^', '!')
    sorted_items = nsu.list_sorter(items + math_ops + exclusions, reverse=True)
    split_list = nsu.multi_split(string, sorted_items)

    # remove any blank fields if present
    no_blanks_itr_str = [i for i in split_list if i != '']

    # add implicit multiplication for every gap in list, if the adjacent elements are not mathematical symbols
    i0 = 0
    temp_list = no_blanks_itr_str
    while i0 < len(temp_list):

        # define initial values
        ip1 = i0 + 1
        i0_val = temp_list[i0]

        # try to define real values, and break if not possible (as there is then no more elements)
        try:
            ip1_val = temp_list[ip1]
        except IndexError:
            break

        # if i0_val and ip1_val does not have conflicting mathematical symbols, add '*' to i0_val and update i0
        if ip1_val not in math_ops[1:] and ip1_val not in exclusions and i0_val not in exclusions and i0_val not in \
                math_ops[2:] and i0_val[-1] != '(':
            temp_list[i0] = i0_val + '*'
        i0 += 1

    # revert list to a string
    result_string = nsu.list_to_string(temp_list)

    return result_string


def parser(math_string, steps=False, cprint=True, **kwargs):
    """
    Takes care of the additional rules and conventions of mathematical operations. Handles parentheses along with
    operators that require parentheses, such as trigonometric functions (sin, cos, tan, ...) and log, exp, etc. This is
    strictly meant to be a back-end function, and thus, for a user-friendly experience use modules.NumAn instead to
    calculate.

    Parameters
        math_string : str
            The mathematical string to parse through the interpreter.
        steps : bool, optional
            If True, displays balances from the script, whilst performing the operations. The default is False.
        cprint : bool
            Prints the result in the console along with the input expression reformatted to reflect how it was read by
            the parser. The default is True.

    Keyword Arguments
        sf : int
            Sets the significant figures of the result. Uses mpmath to do so. If set to None (which is default) no
            attempt will be made to set significant figures. Note that this only affects the result printed in the
            console, it does not whatsoever alter the return value.

    Returns
        The result from the performed operations on the given mathematical string as a float.
    """

    #  define items for product_parser
    collective_items = supported_natural_constants + supported_functions  # collect items to place product around

    # make products explicit, removing spaces in expression at the same time
    product_string = product_parser(math_string.replace(' ', ''), collective_items)
    decom_string = number_parser(product_string)  # decompose string into bits that can be handled by basic parser

    # make sure that brackets are done correctly in the right order
    temp_decom_string = decom_string.copy()
    temp_index = nsu.indexer(temp_decom_string)
    temp_bracket_idx = [[j] + [e] for j, e in temp_index if e[-1] in ('(', ')')]  # find and index open/close brackets

    i0 = 0  # set initial iteration
    while temp_bracket_idx:
        # if two consecutive brackets are a pair, execute operations through ordered_parser(), append the result to the
        #   given string, update it and reiterate. This ensures that the parentheses are read in the correct order

        open_bracket = temp_bracket_idx[i0][1]
        try:  # check for missing closing parenthesis
            close_bracket = temp_bracket_idx[i0 + 1][1]
        except IndexError:
            raise ValueError('Missing closing bracket somewhere.')

        if open_bracket[-1] == '(' and close_bracket == ')':
            cur_open_id, cur_close_id = temp_bracket_idx[i0][0], temp_bracket_idx[i0 + 1][0]
            bracket_excl = list(range(cur_open_id + 1, cur_close_id + 1))  # define the bracket clause as an exclusion
            bracket_decom = temp_decom_string[cur_open_id + 1: cur_close_id]
            pre_temp_result = ordered_parser(bracket_decom, steps)  # execute operations on the clause

            if open_bracket == 'arcsinh(':
                temp_result = np.arcsinh(pre_temp_result)
            elif open_bracket == 'arccosh(':
                temp_result = np.arccosh(pre_temp_result)
            elif open_bracket == 'arctanh(':
                temp_result = np.arctanh(pre_temp_result)
            elif open_bracket == 'arcsin(':
                temp_result = np.arcsin(pre_temp_result)
            elif open_bracket == 'arccos(':
                temp_result = np.arccos(pre_temp_result)
            elif open_bracket == 'arctan(':
                temp_result = np.arctan(pre_temp_result)
            elif open_bracket == 'sinh(':
                temp_result = np.sinh(pre_temp_result)
            elif open_bracket == 'cosh(':
                temp_result = np.cosh(pre_temp_result)
            elif open_bracket == 'tanh(':
                temp_result = np.tanh(pre_temp_result)
            elif open_bracket == 'sqrt(':
                temp_result = pre_temp_result ** (1 / 2)
            elif open_bracket == 'exp(':
                temp_result = np.exp(pre_temp_result)
            elif open_bracket == 'log(':
                temp_result = np.log(pre_temp_result)
            elif open_bracket == 'sin(':
                temp_result = np.sin(pre_temp_result)
            elif open_bracket == 'cos(':
                temp_result = np.cos(pre_temp_result)
            elif open_bracket == 'tan(':
                temp_result = np.tan(pre_temp_result)
            elif open_bracket == 'deg(':
                temp_result = 360 / (2 * np.pi) * pre_temp_result
            elif open_bracket == 'rad(':
                temp_result = (2 * np.pi) / 360 * pre_temp_result
            elif open_bracket == 'ln(':
                if pre_temp_result == 0:
                    raise ValueError('Parser does not support infinity values, ln(0) = -inf.')
                else:
                    temp_result = np.log(pre_temp_result)
            else:
                temp_result = pre_temp_result

            # update the temporary string, index, and bracket index and reiterate
            temp_decom_string = [temp_result if k == cur_open_id else j for k, j in temp_index if k not in bracket_excl]
            temp_index = nsu.indexer(temp_decom_string)
            temp_bracket_idx = [[j] + [e] for j, e in temp_index if str(e)[-1] in ('(', ')')]
            i0 -= 1  # reset iteration
            continue
        i0 += 1
    else:  # if no brackets are present in iterated string, perform operations as usual per ordered_parser()
        parsed_string = ordered_parser(temp_decom_string, steps)
        int_fixed_string = nsu.float_to_int(parsed_string)

    # auto-print if prompted
    if cprint:

        # check if significant figures was set
        sf = None
        if 'sf' in kwargs.keys():
            sf = kwargs.get('sf')

        # define specific set of replacement keys/values to prettify constants in expression
        replacement_keys = ('pi', '_hbar', '_NA', '_c', '_h', '*', '_R', '_k', '_e', '_me', '_mp')
        replacement_vals = ('π', 'ħ', 'Nᴀ', 'cᵥ', 'hₚ', '·', 'Rᶢ', 'kᴮ', 'eᶜ', 'mₑ', 'mₚ')

        # sort the replacements with their keys, replace them and print
        sorted_replacements = nsu.list_sorter(replacement_keys, replacement_vals, reverse=True, otype='tuple')
        pretty_string = nsu.replace(sorted_replacements[0], sorted_replacements[1], product_string)

        if sf:
            with mpmath.workdps(sf):
                res = mpmath.mpf(int_fixed_string)
                print(f'Result: {pretty_string} = {nsu.float_to_int(res)}')
        else:
            print(f'Result: {pretty_string} = {int_fixed_string}')
    return int_fixed_string
