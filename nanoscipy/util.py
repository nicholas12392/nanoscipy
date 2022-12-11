"""
Utility functions for nanoscipy functions and classes.

Contains
--------
string_to_float()

string_to_int()

list_to_string()

indexer()

find()

nest_checker()

elem_checker()

float_to_int()

replace()

list_sorter()

"""
import warnings
import numpy as np
import itertools
from itertools import chain
from operator import itemgetter

standardColorsHex = ['#5B84B1FF', '#FC766AFF', '#5F4B8BFF', '#E69A8DFF', '#42EADDFF', '#CDB599FF', '#00A4CCFF',
                     '#F95700FF', '#00203FFF', '#ADEFD1FF', '#F4DF4EFF', '#949398FF', '#ED2B33FF', '#D85A7FFF',
                     '#2C5F2D', '#97BC62FF', '#00539CFF', '#EEA47FFF', '#D198C5FF', '#E0C568FF']
alphabetSequence = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
alphabetSequenceCap = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                       'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
alphabetSequenceGreek = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ',
                         'υ', 'φ', 'χ', 'ψ', 'ω']
alphabetSequenceGreekCap = ['Α', 'B', 'Γ', 'Δ', 'E', 'Ζ', 'H', 'Θ', 'Ι', 'K', 'Λ', 'M', 'N', 'Ξ', '	Ο', 'Π', 'P',
                            'Σ',
                            'T', 'Y', 'Φ', 'X', 'Ψ', 'Ω']
alphabetSequenceGreekLetters = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa',
                                'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi',
                                'chi', 'psi', 'omega']
alphabetSequenceGreekLettersCap = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota',
                                   'Kappa', 'Lambda', 'Mu', 'Nu', 'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau',
                                   'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega']


def string_to_float(potential_float):
    """
    Converts string to float if possible (that is unless ValueError is encountered).

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
    except (ValueError, TypeError):
        return potential_float


def string_to_int(potential_int):
    """
    Converts string to int if possible (that is unless ValueError is encountered).

    Parameters
    ----------
    potential_int : str
        String to be converted to int.

    Returns
    -------
    int or str
        If successful, input is now int, if unsuccessful, str is still str.

    """
    try:
        set_int = int(potential_int)
        return set_int
    except (ValueError, TypeError):
        return potential_int


def list_to_string(subject_list, sep=''):
    """
    Converts a list to a string regardless of element type.

    Parameters
        subject_list : list
            The list that is to be converted to a string.
        sep : str, optional
            Delimiter in between list elements in the string. The default value is ''.

    Returns
        String from the list elements with the set delimiter in between.

    """
    fixed_list = [str(i) if not isinstance(i, str) else i for i in subject_list]  # fix non-str elements to str type
    list_string = sep.join(fixed_list)  # construct string
    return list_string


def indexer(list_to_index):
    """
    When the built-in enumerate does not work as intended, this will.

    Parameters
        list_to_index : list
            Elements will be indexed starting from zero and from left to right.

    Returns
        The indexed list. A list containing each previous element as a list, consisting of the index/id as the first
        value, and the list-element as the second value.
    """
    indexed_list = []
    i0 = 0
    for i in list_to_index:
        indexed_list.append([i0, i])
        i0 += 1
    return indexed_list


def find(list_subject, index_item):
    """
    An improved version of the native index function. Finds all indexes for the given value if present.

    Parameters
        list_subject : list
            The input list in which the index item should be located.
        index_item : var
            Any variable desired to be found in the list. If not in the list, output will be empty.

    Returns
        A list of ints corresponding to the indexes of the given item in the list.
    """
    indexed_items = [i for i, e in indexer(list_subject) if e == index_item]
    if not indexed_items:  # warn user, if no such item is in the list
        warnings.warn(f'Index item {index_item} is not in the given list.', stacklevel=2)
    return indexed_items


def nest_checker(element, otype='list'):
    """
    Function to check whether an element cannot be looped through. If true, nest element in list, if false iterate items
    to a list.

    Parameters
        element :  variable
            The element for element of interest.
        otype : str, optional
            Set the output type. Supports: python 'list' and 'tuple', and numpy 'ndarray'.


    Returns
        Checked element as the selected output type.
    """

    # check whether element is a string. If true, pack into list, if false try iterate
    if isinstance(element, str):
        res_elem = [element]
    else:
        try:
            res_elem = [i for i in element]
        except (AttributeError, TypeError):  # if iteration fails (not a packaged type element), pack into list
            res_elem = [element]

    # convert the list into the desired output type
    if otype == 'list':
        res_nest = res_elem
    elif otype == 'tuple':
        res_nest = tuple(res_elem)
    elif otype == 'ndarray':
        res_nest = np.array(res_elem)
    else:
        raise ValueError(f'Output type \'{otype}\' is not supported.')
    return res_nest


def elem_checker(elems, lists, flat=False, overwrite=False):
    """
    If elements are in any of the lists index the elements and nest the indexes according to the given lists structure,
    and return a merged list with all the matched elements.

    Parameters
        elems : list
            Elements that are to be checked against the passed lists.
        lists : list
            Match lists to check for elements.
        flat : bool, optional
            Set whether the output indexes should be flattened to a 1D list or remain with the same structure as the
            input match lists. The default is False.
        overwrite : bool, optional
            Determine whether duplicate indexes between lists should be 'merged' into one element, overwriting the
            elements found from left to right, in the given match lists. Note that the index list will be flattened.
            The default is False.

    Returns
        List of all elements found in the provided lists, along with the indexes in the respective passed lists.
    """

    value_list = []
    index_list = []
    for j in lists:  # iterate over the given elements
        temp_index = []
        for i in elems:  # iterate through the current match list
            if i in j:  # if match, grab the value and index the position
                temp_index.append(j.index(i))
                value_list.append(i)
        index_list.append(temp_index)

    if overwrite:
        flat_index = list(chain.from_iterable(index_list))  # flatten the index list
        i = min(flat_index)  # define start of iteration
        temp_index = flat_index
        temp_value = value_list
        while i <= max(flat_index):  # iterate over every found index, to find duplicates
            if flat_index.count(i) > 1:
                duplicate_indexes = find(temp_index, i)[1:]
                temp_index = [e for j, e in indexer(temp_index) if j not in duplicate_indexes]
                temp_value = [e for j, e in indexer(temp_value) if j not in duplicate_indexes]
            i += 1
        value_list = temp_value
        index_list = temp_index

    # flatten the index list if flat
    if flat and not overwrite:
        index_list = list(chain.from_iterable(index_list))

    return value_list, index_list


def float_to_int(float_element, fail_action='pass'):
    """
    A more strict version of the standard int(). Also works for mpmath objects.

    Parameters
        float_element : float
            The element for checking, whether is an int or not.
        fail_action : str, optional
            The action upon failing. If 'pass', returns the float again. If 'error', raises TypeError. The default is
            'pass'.

    Returns
        Either the given float or the given float as int, along with the selected action upon error if any.
    """

    # if input is int, pass as float
    if isinstance(float_element, int):
        float_element = float(float_element)

    float_string = str(float_element)
    try:  # try to find the decimal dot in the float
        float_decimals = float_string[float_string.index('.'):]
    except ValueError:  # this should only fail, if the float_element is in scientific notation, with no decimals
        # this will then fail, as float_element is then a float without a decimal
        # upon this exception, float_element cannot be converted to an int, so the function stops and returns initial.
        return float_element

    # if all decimals are zero, then set the given float as an int
    if all(i == '0' for i in float_decimals[1:]):
        res = int(float_element)
    else:
        if fail_action == 'pass':  # if fail action is 'pass', then return the input float
            res = float_element
        elif fail_action == 'error':  # if fail action is 'error', then raise a TypeError
            raise TypeError(f'Float \'{float_element}\' cannot be converted to int.')
        else:
            raise ValueError(f'There is no such fail action, \'{fail_action}\'.')
    return res


def replace(elems, reps, string, exclusions=None, **kwargs):
    """
    Replaces the element(s) inside the string, if the element(s) is(are) inside the string.

    Parameters
        elem : str or tuple
            The element(s) to be replaced. If tuple, replaces those elements in the tuple.
        rep : str or tuple
            The element(s) to replace with.
        string : str
            The string in which an element is to be replaced.
        exclusions : str or tuple, optional
            If there is a particular sequence (or sequences) of the string, which should not be affected by the initial
            replacement, these should be specified here.

    Keyword Arguments
        out_type : str
            Determines how the replacement result should be as output. If 'str': uses list_to_string to convert to a str.
            If 'list': outputs the raw list obtained from replacement. The default is 'str'.

    Returns
        New string (or list) with the replaced element(s).
    """

    # define kwargs
    out_type = 'str'
    if 'out_type' in kwargs.keys():
        out_type = 'list'

    # make sure that elems and reps are indeed tuples and that there is an actual string
    elems = nest_checker(elems, 'tuple')
    reps = nest_checker(reps, 'tuple')
    if not string:
        raise ValueError(f'Provide expression to replace in; \'string\' is empty.')

    # check if replacements matches amount of elements, if not, try to extend replacements
    if len(elems) != len(reps):
        reps = tuple([reps[0] for i in range(len(elems))])

    # isolate exclusions from string to insert later
    if exclusions:
        excl_list = nest_checker(exclusions, 'list')
        sort_excl = list_sorter(excl_list, reverse=True)
        excl_split_list = multi_split(string, sort_excl, no_blanks=True)
        found_excl, pure_list = [], []
        for i, e in enumerate(excl_split_list):
            if e in excl_list:
                found_excl.append([i, e])
            else:
                pure_list.append([i, e])
    else:
        found_excl, pure_list = None, indexer([string])

    # perform replacements for each string element
    rep_list = []
    for i, e in pure_list:
        e_split = multi_split(e, elems)
        rep_elem = [reps[elems.index(j)] if j in elems else j for j in e_split]
        rep_list.append([i, list_to_string(rep_elem)])

    # insert exclusions back into the string, depending on whether exclusions were defined
    if found_excl:
        init_list = found_excl + rep_list
        init_list_fix = list(zip(*init_list))
        sort_list = list_sorter(init_list_fix[0], init_list_fix[1], stype='int_size')
    else:
        sort_list = list(zip(*rep_list))

    # determine the output type
    if out_type == 'str':
        string_list = list_to_string(sort_list[1])
    elif out_type == 'list':
        string_list = sort_list[1]
    else:
        raise ValueError(f'Output type \'{out_type}\' is invalid.')

    # return result list
    return string_list


def list_sorter(*lists, stype='str_size', reverse=False, otype='list'):
    """
    Sorts any amount of given lists, according to the first list given, depending on the sorting type.

    Parameters
        *lists : list
            The lists in need of being sorted. Sorts all lists according to the elements in the first list.
        stype : str, optional
            Determines which sorting type should be used. If 'str_size', sorts after size of strings (in order of
            smallest to largest). If 'alphabetic', sorts strings alphabetically. If 'int_size', sorts after integer size
            from smallest to largest. The default is 'str_size'.
        reverse : bool, optional
            Reverses the sorting order. The default is False.
        otype : str, optional
            Determines the output type. If 'list', a list of lists is created. If 'tuple' a tuple of tuples is created.
            The default is 'list'.

    Returns
        A list/tuple of lists/tuples with the sorted lists. The output list/tuple sequence matches input.
    """

    # if sorting type is string size, construct a uniform list including a corresponding size-list as first list
    if stype == 'str_size':
        uniform_list = list(zip([len(i) for i in lists[0]], *lists))
        sorted_lists_pre = sorted(uniform_list, key=itemgetter(0), reverse=reverse)  # sort lists
        sorted_lists = [i[1:] for i in sorted_lists_pre]  # remove size-list

    # if sorting type is int size, then assume the list to be of integers already
    elif stype == 'int_size':
        uniform_list = list(zip(*lists))
        sorted_lists = sorted(uniform_list, key=itemgetter(0), reverse=reverse)  # sort lists

    # if sorting type is alphabetic, construct a uniform list from the given lists and conduct sorting
    elif stype in ('alpha', 'alphabetic', 'alphabet'):
        uniform_list = list(zip(*lists))
        sorted_lists = sorted(uniform_list, key=itemgetter(0), reverse=reverse)  # sort lists
    else:  # raise error if sorting type is unknown
        raise ValueError(f'Sorting type {stype} is undefined.')

    # define the output according to the output type
    if otype == 'tuple':
        output_lists = tuple(zip(*sorted_lists))
    elif otype == 'list':
        output_lists = [list(i) for i in list(zip(*sorted_lists))]
    else:
        raise ValueError(f'Output type {otype} is undefined.')

    if len(output_lists) == 1:
        output_lists = output_lists[0]

    return output_lists


def string_sorter(*lists, stype='size', reverse=False, otype='list'):
    """
    Sorts any amount of given lists of strings, according to the first list given, depending on the sorting type.

    Parameters
        *lists : list
            The lists of strings in need of being sorted. Sorts all lists according to the strings in the first list.
        stype : str, optional
            Determines which sorting type should be used. If 'size', sorts after size of the string (in order of
            smallest to largest). If 'alphabetic', sorts strings alphabetically. The default is 'size'.
        reverse : bool, optional
            Reverses the sorting order. The default is False.
        otype : str, optional
            Determines the output type. If 'list', a list of lists is created. If 'tuple' a tuple of tuples is created.
            The default is 'list'.

    Returns
        A list/tuple of lists/tuples with the sorted strings. The output list/tuple sequence matches input.
    """

    warnings.warn('Use \'list_sorter()\' function instead. This function is outdated and will be removed in upcoming '
                  'patch.')

    # if sorting type is size, construct a uniform list including a corresponding size-list as first list
    if stype == 'size':
        uniform_list = list(zip([len(i) for i in lists[0]], *lists))
        sorted_lists_pre = sorted(uniform_list, key=itemgetter(0), reverse=reverse)  # sort lists
        sorted_lists = [i[1:] for i in sorted_lists_pre]  # remove size-list

    # if sorting type is alphabetic, construct a uniform list from the given lists and conduct sorting
    elif stype in ('alpha', 'alphabetic', 'alphabet'):
        uniform_list = list(zip(*lists))
        sorted_lists = sorted(uniform_list, key=itemgetter(0), reverse=reverse)  # sort lists
    else:  # raise error if sorting type is unknown
        raise ValueError(f'Sorting type \'{stype}\' is undefined.')

    # define the output according to the output type
    if otype == 'tuple':
        output_lists = tuple(zip(*sorted_lists))
    elif otype == 'list':
        output_lists = [list(i) for i in list(zip(*sorted_lists))]
    else:
        raise ValueError(f'Output type \'{otype}\' is undefined.')

    if len(output_lists) == 1:
        output_lists = output_lists[0]

    return output_lists


def split(string, delim, rep=None, no_blanks=True):
    """
    Function that splits around a given delimiter, rather than at the given delimiter as the python .split() function.

    Parameters
        string : str
            The string in which the splitting should be made in.
        delim : str
            Identifier for which a split should be made around.
        no_blanks : bool, optional
            When the delimiter is either the first or last element, blank list elements like ['', ''] are created, if
            this parameter is True, those blanks are removed. The default is True.
        rep : any, optional
            Allows for directly replacing the element splitting around, so that after splitting, the resulting list
            will contain the replacement rather than the delimiter at its position. This can be multiple elements in a
            list. The default is None.

    Returns
        A list containing the parts from the split.
    """

    if delim not in string:  # if the delimiter is not in the string, construct normalized output and exit
        return [string]

    # define re-insert depending on if replacement was set
    true_insert = delim
    if rep:
        if isinstance(rep, (list, tuple)):
            true_insert = '𒐫'.join(rep)
        else:
            true_insert = rep

    # construct split list based on the delimiter
    pre_string = string.replace(delim, '𒐫' + str(true_insert) + '𒐫').split('𒐫')

    if no_blanks:
        try:
            result_string = [i for i in pre_string if i != '']
        except ValueError:
            result_string = pre_string
    else:
        result_string = pre_string

    return result_string


def multi_split(string, items, reps=None, no_blanks=True):
    """
    An advanced version of the util.split() function. Splits the given string around every given item, and yields a
    list with the result. Splits around items in order of occurrence, thus, no items that have already been iterated
    through can be split again.

    Parameters
        string : str
            The string to split in.
        items : list
            String elements that the function should split the main string around. This is a tuple of string elements.
        no_blanks : bool, optional
            When the delimiter is either the first or last element, blank list elements like ['', ''] are created, if
            this parameter is True, those blanks are removed. The default is True.
        reps : list
            Allows for directly replacing the element splitting around, so that after splitting, the resulting list
            will contain the replacement rather than the delimiter at its position.

    Returns
        List of the separated string parts.
    """
    # set initial values for iteration
    temp_itr_str = [string]  # input string must be a list
    iterated_items = []
    remain_items = nest_checker(items, 'list')  # if items are not packed, pack them
    if reps:
        packed_reps = nest_checker(reps, 'list')  # if items are not packed, pack them
        pr_len = len(packed_reps)
        if pr_len != len(remain_items):
            true_inserts = packed_reps + remain_items[pr_len:]
        else:
            true_inserts = packed_reps
    else:
        true_inserts = remain_items.copy()
    string_wo_item = string  # define checker string, to avoid iterations, if item is not in the string

    # while there are still items remaining, keep iterating
    while remain_items:
        item = remain_items[0]  # define the current item for checking as the first of the remaining
        insert = true_inserts[0]

        # if an item string is found in the main string, split the string around the item IF the item
        #   has not already been iterated through
        if item in string_wo_item:
            temp_itr_str = [[i] if i in iterated_items else split(i, item, rep=insert, no_blanks=no_blanks) for
                            i in temp_itr_str]
            temp_itr_str = list(chain.from_iterable(temp_itr_str))

        # update temporary lists
        iterated_items += [insert]
        remain_items.remove(item)  # remove the current item from the remaining items
        true_inserts.remove(insert)
        string_wo_item = list_to_string(string_wo_item.split(item))  # update checker string

    # return result list
    return temp_itr_str
