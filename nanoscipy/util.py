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

string_sorter()

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
    Converts a list to a string.

    Parameters
        subject_list : list
            The list that is to be converted to a string.
        sep : str, optional
            Delimiter in between list elements in the string. The default value is ''.

    Returns
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


def replace(elems, reps, string, exclusions=None):
    """
    Replaces the element(s) inside the string, if the element(s) is(are) inside the string. Can replace sequences up to
    10 letters.

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

    Returns
        New string with the replaced element(s).
    """

    # make sure that elems and reps are indeed tuples
    elems = nest_checker(elems, 'tuple')
    reps = nest_checker(reps, 'tuple')

    fixed_index_excl_list = []  # set exclusions to be empty, and redefine if any are present
    if exclusions:

        # if only a single exclusion, make iterable
        exclusions = nest_checker(exclusions, 'tuple')

        exclusion_id_relist = []  # empty list for indexes of exclusions in string
        for exclusion in exclusions:  # iterate through all exclusions
            if exclusion in string:
                temp_string = string.split(exclusion)  # split string around exclusion

                # for each split (but the last), define an index for that list, and iterate through the lists
                for elem_id, list_elem in indexer(temp_string[:-1]):
                    # define first index for the exclusion
                    temp_insert_id = len(list(chain.from_iterable(temp_string[:elem_id + 1])))

                    # define index boundaries for the exclusion
                    lower_boundary = temp_insert_id + len(exclusion) * elem_id
                    upper_boundary = temp_insert_id + len(exclusion) * (1 + elem_id)

                    # append the found indexes to a list, with an index per element
                    exclusion_id_relist.append([[i] + [j] for i, j in
                                                zip(list(range(lower_boundary, upper_boundary)), exclusion)])

        # flatten the list, and remove all duplicate elements
        flat_index_excl_list = list(chain.from_iterable(exclusion_id_relist))
        flat_index_excl_list.sort()
        fixed_index_excl_list = list(k for k, _ in itertools.groupby(flat_index_excl_list))

        # define updated string, with the exclusions temporarily removed
        excl_string = [[i] + [e] if i not in [k[0] for k in fixed_index_excl_list] else [i] + [''] for i, e in
                       indexer(string)]
    else:
        excl_string = indexer(string)

    pre_float_string = [i[1] for i in excl_string]  # decompose input string into elements in a list
    decom_elems = [[i for i in j] for j in elems]  # decompose rep string

    i = 0  # define initial
    temp_string = pre_float_string
    while i < len(temp_string):  # iterate over the length of the 1-piece list

        # define surrounding iterates
        ip1, ip2, ip3, ip4, ip5, ip6, ip7, ip8, ip9 = i + 1, i + 2, i + 3, i + 4, i + 5, i + 6, i + 7, i + 8, i + 9
        packed_indexes = [ip1, ip2, ip3, ip4, ip5, ip6, ip7, ip8, ip9]  # pack integers for compaction
        i0_val = temp_string[i]  # define current iterative value

        # define fall-back values for iterates passed current
        ip1_val = ip2_val = ip3_val = ip4_val = ip5_val = ip6_val = ip7_val = ip8_val = ip9_val = None

        try:  # try to define values for the surrounding iterations, otherwise pass at position
            ip1_val = temp_string[ip1]
            ip2_val = temp_string[ip2]
            ip3_val = temp_string[ip3]
            ip4_val = temp_string[ip4]
            ip5_val = temp_string[ip5]
            ip6_val = temp_string[ip6]
            ip7_val = temp_string[ip7]
            ip8_val = temp_string[ip8]
            ip9_val = temp_string[ip9]
        except IndexError:
            pass

        # define a packed index
        packed_values = [i0_val, ip1_val, ip2_val, ip3_val, ip4_val, ip5_val, ip6_val, ip7_val, ip8_val, ip9_val]

        for es, o in zip(decom_elems, reps):

            # if the element is found within the provided string, replace with replacement at the current index, and
            # fill in blanks at any other index within the replacement frame
            if es == packed_values[:len(es)]:
                temp_string = [o if k == i else '' if k in packed_indexes[:len(es) - 1] else j for k, j in
                               indexer(temp_string)]
                break  # break out of the for loop, preventing overwriting
        i += 1  # update iterative

    # reintroduce the exclusions if any
    if fixed_index_excl_list:

        # index the string with the replacements in it, and remove all blanks
        index_rem_string = [[i] + [j] for i, j in indexer(temp_string) if j != '']

        # append the fixed new string with indexes, with the exclusion index list
        appended_string = index_rem_string + fixed_index_excl_list
        appended_string.sort()  # sort the string according to the index
        res = list_to_string([j for i, j in appended_string])  # remove the indexes and convert the list to a string
    else:
        res = list_to_string(temp_string)  # define result and convert to string
    return res


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


def split(string, delim, no_blanks=True):
    """
    Function that splits around a given delimiter, rather than at the given delimiter as the python .split() function.

    Parameters
        string : str
            The string in which the splitting should be made in.
        delim : str
            Identifier for which a split should be made around.
        no_blanks : bool, optional
            In some cases, blank list elements like ['', ''] may be created, if this parameter is True, those blanks
            are removed. The default is True.

    Returns
        A list containing the parts from the split.
    """
    temp_list = string.replace(delim, '𒐫𐩕𒐫').split('𒐫')
    pre_string = [delim if i == '𐩕' else i for i in temp_list]

    if no_blanks:
        try:
            result_string = [i for i in pre_string if i != '']
        except ValueError:
            result_string = pre_string
    else:
        result_string = pre_string

    return result_string


def multi_split(string, items, no_blanks=True):
    """
    An advanced version of the util.split() function. Splits the given string around every given item, and yields a
    list with the result. Splits around items in order of occurrence, thus, no items that have already been iterated
    through can be split again.

    Parameters
        string : str
            The string to split in.
        items : tuple
            String elements that the function should split the main string around. This is a tuple of string elements.
        no_blanks : bool, optional
            In some cases, blank list elements can appear, this removes those elements.

    Returns
        List of the separated string parts.
    """
    # set initial values for iteration
    temp_itr_str = [string]  # input string must be a list
    iterated_items = []
    remain_items = nest_checker(items, 'list')  # if items are not packed, pack them
    string_wo_item = string  # define checker string, to avoid iterations, if item is not in the string

    # while there are still items remaining, keep iterating
    while remain_items:
        item = remain_items[0]  # define the current item for checking as the first of the remaining

        # if an item string is found in the main string, split the string around the item IF the item
        #   has not already been iterated through
        if item in string_wo_item:
            temp_itr_str = [[i] if i in iterated_items else split(i, item, no_blanks=no_blanks) for
                            i in temp_itr_str]
            temp_itr_str = list(chain.from_iterable(temp_itr_str))

        # update temporary lists
        iterated_items += [item]
        remain_items.remove(item)  # remove the current item from the remaining items
        string_wo_item = list_to_string(string_wo_item.split(item))  # update checker string

    # return result list
    return temp_itr_str
