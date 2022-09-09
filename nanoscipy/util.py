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

"""
import warnings
import numpy as np
import sympy as sp
from itertools import chain


standardColorsHex = ['#5B84B1FF', '#FC766AFF', '#5F4B8BFF', '#E69A8DFF', '#42EADDFF', '#CDB599FF', '#00A4CCFF',
                     '#F95700FF', '#00203FFF', '#ADEFD1FF', '#F4DF4EFF', '#949398FF', '#ED2B33FF', '#D85A7FFF',
                     '#2C5F2D', '#97BC62FF', '#00539CFF', '#EEA47FFF', '#D198C5FF', '#E0C568FF']
alphabetSequence = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


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
    Converts a list to a string.

    Parameters
    ----------
    subject_list : list
        List to be converted to a string.
    sep : str, optional
        Delimiter in between list elements in the string. The default value is ''.

    Returns
    -------
    String from the list elements with the set delimiter in between.

    """
    fixed_list = [str(i) if not isinstance(i, str) else i for i in subject_list]  # fix non-str elements to str type
    stringified_list = sep.join(fixed_list)  # construct string
    return stringified_list


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
    indexed_list = [[k] + [j] for k, j in zip(list(range(len(list_to_index))), list_to_index)]
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
        resElem = [element]
    else:
        try:
            resElem = [i for i in element]
        except AttributeError:  # if iteration fails (not a packaged type element), pack into list
            resElem = [element]

    # convert the list into the desired output type
    if otype == 'list':
        resNest = resElem
    elif otype == 'tuple':
        resNest = tuple(resElem)
    elif otype == 'ndarray':
        resNest = np.array(resElem)
    else:
        raise ValueError(f'Output type \'{otype}\' is not supported.')
    return resNest


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
        List of all elements found in the passed lists, along with the indexes in the respective passed lists.
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
    A more strict version of the standard int().

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
    float_decimals = float_string[float_string.index('.'):]

    # if all decimals are zero, then set the given float as an int
    if all(i == '0' for i in float_decimals[1:]):
        res = int(float_element)
    else:
        if fail_action == 'pass':  # if fail action is 'pass', then return the input float
            res = float_element
        elif fail_action == 'error':  # if fail action is 'error', then raise a TypeError
            raise TypeError(f'Float \'{float_element}\' cannot be converted to int.')
    return res