import scipy.constants as spc
import nanoscipy.util as nsu
import nanoscipy.mathpar as nsp

SI_base_units = ('s', 'm', 'kg', 'A', 'K', 'mol')  # the absolute SI units base

# list over base units, with their derived SI units and accompanying scalars
from_derivative_to_SI = (('g', 'N', 'C', 'kat', 'Hz', 'Bq', 'J', 'Pa', 'W', 'Gy', 'Sv', 'V', 'Wb', 'Ω', 'F', 'S', 'H',
                          'T', 'eV', 'Å', 'u', 'amu', 'Da', 'L', 'cal', 'atm', 'min', 'bar', 'Torr'),
                         ('10^-3*kg', 'kg*m*s^-2', 'A*s', 'mol*s^-1', 's^-1', 's^-1', 'kg*m^2*s^-2', 'kg*m^-1*s^-2',
                          'kg*m^2*s^-3', 'm^2*s^-2', 'm^2*s^-2', 'kg*m^2*s^-3*A^-1', 'kg*m^2*s^-2*A^-1',
                          'kg*m^2*s^-3*A^-2', 'kg^-1*m^-2*s^4*A^2', 'm^-2*kg^-1*s^3*A^2', 'm^2*kg*s^-2*A^-2',
                          'kg*s^-2*A^-1', str(spc.e) + '*kg*m^2*s^-2', '10^-10*m', str(spc.atomic_mass) + '*kg',
                          str(spc.u) + '*kg', str(spc.u) + '*kg', '10^-3*m^3', '4.18400*kg*m^2*s^-2',
                          '101325*kg*m^-1*s^-2', '60*s', '10^5*kg*m^-1*s^-2', '133.322368421*kg*m^-1*s^-2'))
from_SI_to_derivative = ((('kg', 'm', 's^-2'), ('A', 's'), ('mol', 's^-1'), ('kg', 'm^2', 's^-2'),
                          ('kg', 'm^-1', 's^-2'), ('kg', 'm^2', 's^-3'), ('kg', 'm^2', 's^-3', 'A^-1'),
                          ('kg', 'm^2', 's^-2', 'A^-1'), ('kg', 'm^2', 's^-3', 'A^-2'),
                          ('kg^-1', 'm^-2', 's^4', 'A^2'), ('m^-2', 'kg^-1', 's^3', 'A^2'), ('m^2', 'kg', 's^-2, A^-2'),
                          ('kg', 's^-2', 'A^-1')),
                         ('N', 'C', 'kat', 'J', 'Pa', 'W', 'V', 'Wb', 'Ω', 'F', 'S', 'H', 'T'))

# print(list(zip(*from_derivative_to_SI)))  # check derived unit against base
# these are the base units that the script supports
supported_base_units = ('s', 'm', 'g', 'A', 'K', 'mol', 'N', 'C', 'kat', 'Hz', 'Bq', 'J', 'Pa', 'W', 'Gy', 'Sv', 'V',
                        'Wb', 'Ω', 'F', 'S', 'H', 'T', 'eV', 'Da', 'L', 'cal', 'bar', 'Torr')
supported_special_units = ('Å', 'u', 'amu', 'atm', 'min')

prefix_scalars = ('Y', 'Z', 'E', 'P', 'T', 'G', 'M', 'k', 'h', 'da', '', 'd', 'c', 'm', 'µ', 'n', 'p', 'f', 'a', 'z',
                  'y')
prefix_values = ('10^24', '10^21', '10^18', '10^15', '10^12', '10^9', '10^6', '10^3', '10^2', '10^1', '1', '10^-1',
                 '10^-2', '10^-3', '10^-6', '10^-9', '10^-12', '10^-15', '10^-18', '10^-21', '10^-24')
math_ops = ('-', '+', '/', '*', '^', '(', ')', '^-')  # valid unit math operations


# WILL NOT SUPPORT UNITS AS POWERS; AS THIS HAS NO PHYSICAL MEANING


def unit_separator(math_string, supported_values, unit_identifier=' '):
    """
    This function separates the supported units along with the supported mathematical operations into a unit expression
    that may be processed.

    Parameters
        math_string : str
            The raw mathematical expression with units.
        supported_values : list
            The packed supported units along with the supported mathematical operations.
        unit_identifier : str, optional
            The specific identifier set for notifying a unit. E.g. if set to '~', all units must be denoted as '~cm',
            '~kg', etc. The default is ' '.

    Returns
        A list containing all the supported units from the expression along with all the mathematical operators
        surrounding them.
    """

    # split the given string around the supported units and mathematical operators
    split_list = nsu.multi_split(math_string, supported_values, True)

    # find all powers and connect power and operator
    i0 = 0
    temp_split_list = split_list
    unit_powers = []  # collect all found powers
    while i0 < len(temp_split_list):

        # define initial values
        i0_val = temp_split_list[i0]

        # if the current iterative is a power, try to collect/pack it
        if i0_val in ('^', '^-'):
            ip1 = i0 + 1  # define right value index
            ip1_val = temp_split_list[ip1]  # define right value

            # if the power is a closed expression, grab the entire expression and save it as power
            if ip1_val == '(':
                end_parenthesis_position = temp_split_list[ip1:].index(')') + len(temp_split_list[:ip1])
                power_list = temp_split_list[i0:end_parenthesis_position + 1]
                end_pos = end_parenthesis_position + 1

            # if the power is a value, grab this value and save it as power
            elif isinstance(nsu.string_to_float(ip1_val), float):
                power_list = temp_split_list[i0:ip1 + 1]
                end_pos = ip1 + 1
            else:
                raise ValueError(f'Power \'{ip1_val}\' cannot be used in unit parsing.')

            # update the temp lists
            power_string = nsu.list_to_string(power_list)
            unit_powers += [power_string]
            temp_split_list[i0:end_pos] = [power_string]
        i0 += 1  # update iterative

    # clean-up symbols from scientific notation and remove excess math symbols at the end
    unit_expression = split_list.copy()
    i0 = 0
    while i0 < len(unit_expression):
        i0_val = unit_expression[i0]  # define current value
        ip1 = i0 + 1  # define right value index
        try:  # try to define real right value, otherwise set to None
            ip1_val = unit_expression[ip1]
        except IndexError:
            ip1_val = None

        if i0_val[0] != unit_identifier and i0_val[-1] == 'e' and ip1_val in ('+', '-'):
            del unit_expression[i0:ip1 + 1]  # remove scientific notation, so that it does not act as operators
        elif i0_val in supported_values + tuple(unit_powers):
            if i0_val == unit_expression[-1] and i0_val in ('-', '+', '/', '*'):
                del unit_expression[-1]  # if last element is an operator, remove and check previous value
                i0 -= 1
            else:  # else keep the value and update
                i0 += 1
        else:  # reaching this clause means that the value is not supported, and should not be contained in expression
            if i0_val == unit_expression[-1]:  # if the element is the last, remove and go back one step
                del unit_expression[i0]
                i0 -= 1
            else:  # else just remove element and continue
                del unit_expression[i0]
    return unit_expression


def unit_converter(unit_expression, unit_identifier=' '):
    """
    This function finds the specific units contained within the unit expression, isolates them and identifies possible
    prefixes, logs the prefix scalars in a list, and logs the SI unit composition in another separate list.

    Parameters
        unit_expression : list
            A list in which the unit expression has been split, so that every unit and mathematical operator is
            isolated.
        unit_identifier : str, optional
            The specific identifier set for notifying a unit. E.g. if set to '~', all units must be denoted as '~cm',
            '~kg', etc. The default is ' '.

    Returns
        A list of the identified units, a list of the accompanying prefix scalars, along with a list of the SI unit
        decompositions.
    """

    # first find out what units are actually in the string, and remove duplicates simultaneously
    unit_list = [*set([i for i in unit_expression if i not in math_ops and i[0] != '^'])]

    # pack units next to a power in a clause, making sure they are ready correctly by a parser
    i0 = 0
    while i0 < len(unit_expression):
        i0_val = unit_expression[i0]  # define current value
        try:  # define real right value
            ip1_val = unit_expression[i0 + 1]
        except IndexError:
            ip1_val = None
        if i0_val in unit_list and ip1_val and ip1_val[0] == '^':
            unit_expression.insert(i0 + 1, ')')
            unit_expression.insert(i0, '(')
        i0 += 1

    # define lists based on base unit length, so that prefixes are grabbed correctly
    collected_base_units = supported_base_units + supported_special_units  # collect all supported base units
    len_4_base_units = [i for i in collected_base_units if len(i) == 4]
    len_3_base_units = [i for i in collected_base_units if len(i) == 3]
    len_2_base_units = [i for i in collected_base_units if len(i) == 2]

    # change units to a scalar
    iterative_list = unit_list.copy()
    unit_scalar_list = []
    fixed_unit_list = []
    while iterative_list:

        # define iterative value
        i0 = iterative_list[0]
        id_len = len(unit_identifier)  # length of unit identifier
        i0_nid = i0[id_len:]  # i0 value with no unit identifier

        # find scalars conditionally
        # if the unit length is 1, the unit can only be a base unit
        if len(i0_nid) == 1:
            unit_scalar_list += ['1']
            fixed_unit_list += [i0]

        # if the unit length is 2:
        if len(i0_nid) == 2:
            if i0_nid in len_2_base_units:  # the unit can be a 2-length base unit
                unit_scalar_list += ['1']
                fixed_unit_list += [i0]
            else:  # or the unit can be a 1-length base unit with a 1-length prefix
                prefix = i0_nid[0]
                solved_prefix = [v for i, v in zip(prefix_scalars, prefix_values) if i == prefix]
                unit_scalar_list += solved_prefix
                fixed_unit_list += [i0[0] + i0_nid[1]]

        # if the unit length is 3:
        if len(i0_nid) == 3:
            if i0_nid in len_3_base_units:  # the unit can be a 3-length base unit,
                unit_scalar_list += ['1']
                fixed_unit_list += [i0]
            elif i0_nid[1:] in len_2_base_units:  # the unit can be a 2-length base unit with a 1-length prefix
                prefix = i0_nid[0]
                solved_prefix = [v for i, v in zip(prefix_scalars, prefix_values) if i == prefix]
                unit_scalar_list += solved_prefix
                fixed_unit_list += [i0[0] + i0_nid[1:]]
            else:  # or the unit can be a 1-length base unit with a 2-length prefix
                prefix = i0_nid[:2]
                solved_prefix = [v for i, v in zip(prefix_scalars, prefix_values) if i == prefix]
                unit_scalar_list += solved_prefix
                fixed_unit_list += [i0[0] + i0_nid[2]]

        # if the unit length is 4:
        if len(i0_nid) == 4:
            if i0_nid in len_4_base_units:  # the unit can be a 4-length base unit,
                unit_scalar_list += ['1']
                fixed_unit_list += [i0]
            elif i0_nid[1:] in len_3_base_units:  # the unit can be a 3-length base unit with a 1-length prefix
                prefix = i0_nid[0]
                solved_prefix = [v for i, v in zip(prefix_scalars, prefix_values) if i == prefix]
                unit_scalar_list += solved_prefix
                fixed_unit_list += [i0[0] + i0_nid[1:]]
            else:  # or the unit can be a 2-length base unit with a 2-length prefix
                prefix = i0_nid[:2]
                solved_prefix = [v for i, v in zip(prefix_scalars, prefix_values) if i == prefix]
                unit_scalar_list += solved_prefix
                fixed_unit_list += [i0[0] + i0_nid[2:]]

        # if the unit length is 5:
        if len(i0_nid) == 5:
            if i0_nid[1:] in len_4_base_units:  # the unit can be a 4-length base unit with a 1-length prefix
                prefix = i0_nid[0]
                solved_prefix = [v for i, v in zip(prefix_scalars, prefix_values) if i == prefix]
                unit_scalar_list += solved_prefix
                fixed_unit_list += [i0[0] + i0_nid[1:]]
            else:  # otherwise, the unit can only be a 3-length base unit with a 2-length prefix
                prefix = i0_nid[:2]
                solved_prefix = [v for i, v in zip(prefix_scalars, prefix_values) if i == prefix]
                unit_scalar_list += solved_prefix
                fixed_unit_list += [i0[0] + i0_nid[2:]]

        # if the unit length is 6, the unit can only a 4-length base with a 2-length prefix
        if len(i0_nid) == 6:
            prefix = i0_nid[:2]
            solved_prefix = [v for i, v in zip(prefix_scalars, prefix_values) if i == prefix]
            unit_scalar_list += solved_prefix
            fixed_unit_list += [i0[0] + i0_nid[2:]]

        # update iterative list
        iterative_list.remove(i0)

    # substitute fixed units for SI fixed units in a new list
    SI_unit_list = []
    i0 = 0
    while i0 < len(fixed_unit_list):
        i0_val = fixed_unit_list[i0]  # define current value
        derivative_ids = [unit_identifier + i for i in from_derivative_to_SI[0]]  # list of derived units with unit id
        i0_nid = i0_val[1:]  # remove ID by now

        # if the current value is already SI, do not change the unit
        if i0_val in [unit_identifier + i for i in SI_base_units]:
            SI_unit_list += [i0_nid]
        else:  # if not, then change the unit to SI
            if i0_val in derivative_ids:
                SI_unit_list += [from_derivative_to_SI[1][derivative_ids.index(i0_val)]]
        i0 += 1
    return unit_list, unit_scalar_list, SI_unit_list


def unit_operations(opr, left, right):
    """
    Solves units for supported mathematical operations: +, - and *. This requires the units to be normalized to powers.
    E.g. 'm' needs to be 'm^1'. It can handle multiplication with 1. If it cannot reduce the given operands, it will
    return a list with the units around '*' (only for multiplication).

    Parameters
        opr : str
            The operator to be used for the two given units. Supports +, - and *.
        left : str
            The left operand.
        right : str
            The right operand.

    Returns
        The result from the operation in a list.
    """

    # define operation results for each of the supported operators
    if opr in ('+', '-'):
        if left == right:
            operation_result = [left]
        else:
            raise ValueError(f'Unit operation \'{left} {opr} {right}\' is invalid.')
    elif opr == '*':
        # check if the given left and right values have already been parsed, resulting in a product out
        if '*' not in left:
            left_values = left.split('^')
        else:
            left_values = left
        if '*' not in right:
            right_values = right.split('^')
        else:
            right_values = right

        # if left and right values are the same, reduce expression
        if left_values[0] == right_values[0] and len(left_values) == 2 and len(right_values) == 2:
            power_result = nsu.float_to_int(float(left_values[1]) + float(right_values[1]))
            string_result = str(power_result)
            if string_result == '0':  # if the power result is 0, then the product equates to 1
                operation_result = ['1']
            else:  # else, just update the power
                operation_result = [left_values[0] + '^' + string_result]
        elif left == '1':  # if left operand is zero, output right operand
            operation_result = [right]
        elif right == '1':
            operation_result = [left]
        else:  # else just return input as list
            operation_result = [left, '*', right]
    else:  # raise error if the operator is not supported
        raise ValueError(f'Operator \'{opr}\' is not supported.')
    return operation_result


def unit_replacer(math_string, unit_list, unit_scalar_list, SI_unit_list):
    """
    Replaces the unit prefixes in a mathematical expression with the scalar values. In addition, insert special unit
    conversion scalars, e.g. '10^-10' from 'Å' to 'm'.

    Parameters
        math_string : str
            The mathematical expression in which units should be replaced.
        unit_list : list
            The units contained in the expression.
        unit_scalar_list : list
            The scalars corresponding to the prefixes of the units in unit_list, if no prefix, set value to '1' for each
            such unit.
        SI_unit_list : list
            The SI-unit-expressions that the units in unit_list can be decomposed to.

    Returns
        The fixed mathematical expression, a list containing the SI-units (size-sorted), and another list containing the
        size-sorted units that were found in the given expression.
    """

    # size-sort both the SI units, found units and scalars depending on size of the found units
    sorted_units = nsu.string_sorter(unit_list, unit_scalar_list, SI_unit_list, reverse=True)

    # check whether the base/SI-unit conversions contain further scalars, and add those if that is the case
    sorted_scalars = []
    sorted_names = []
    sorted_SI = []
    for i, j, k in zip(*sorted_units):
        temp_sorted_scalars = []
        temp_sorted_SI = []
        k_split = k.split('*')  # split around '*', to identify scalars
        if any(e not in supported_base_units for e in k_split):
            for h in k_split:
                if isinstance(nsu.string_to_int(h[0]), int):  # if a scalar is found, append to scalars
                    temp_sorted_scalars.append('*' + h)
                else:  # else append the unit to the SI unit list
                    temp_sorted_SI.append('*' + h)
        else:
            temp_sorted_SI = '*' + k

        # fix all temporary values to their respective lists
        sorted_scalars.append('*(' + j + nsu.list_to_string(temp_sorted_scalars) + ')')
        sorted_SI.append(nsu.list_to_string(temp_sorted_SI)[1:])
        sorted_names.append(i)

    # replace units in the given expression, and remove any spacings in the expression
    replaced_unit_list = nsu.replace(sorted_names, sorted_scalars, math_string)
    replaced_unit_string = nsu.list_to_string([i for i in replaced_unit_list if i != ' '])

    # fix potential doubles of multiplication from insertion
    fixed_math_unit_string = []
    temp_string_list = [i for i in replaced_unit_string]
    while temp_string_list:
        i0_val = temp_string_list[0]
        try:
            ip1_val = temp_string_list[1]
        except IndexError:
            ip1_val = None

        if i0_val in ('*', '/') and ip1_val == '*':
            del temp_string_list[1]
        else:
            fixed_math_unit_string += [i0_val]
            del temp_string_list[0]
    fixed_math_unit_string = nsu.list_to_string(fixed_math_unit_string)
    return fixed_math_unit_string, sorted_SI, sorted_names


def unit_solver(unit_expression, unit_list, fixed_unit_list):
    """
    Solve the units in the unit expression so that units that are not SI units are correctly replaced with the
    SI-unit decomposition, and fix the correct powers to the units.

    Parameters
        unit_expression : list
            Contains the unit expression split around the units and mathematical operators.
        unit_list : list
            Contains all the different units that are found in the unit expression.
        fixed_unit_list : list
            Contains all the SI-unit decompositions (without scalars).

    Returns
        List that contains a power-normalized unit expression, ready to be computed.

    """

    # first swap units in unit expression to base units
    base_units_expression = []
    max_iteration = len(unit_expression)
    i0 = 0
    while i0 < max_iteration:
        i0_val = unit_expression[i0]  # define current value
        if i0_val in unit_list:

            # at the same time expand expression around multiplication, and place it in parentheses if not already
            try:
                im1_val = unit_expression[i0 - 1]
            except IndexError:
                im1_val = None
            try:
                ip1_val = unit_expression[i0 + 1]
            except IndexError:
                ip1_val = None

            if im1_val == '(' and ip1_val == ')':
                base_units_expression += nsu.split([fixed_unit_list[unit_list.index(i0_val)]][0], '*')
            else:
                base_units_expression += ['('] + nsu.split([fixed_unit_list[unit_list.index(i0_val)]][0], '*') + [')']
        else:
            base_units_expression += [i0_val]
        i0 += 1

    # check for missing multiplication (implicit multiplication) and remove some invalid math symbols
    i0 = 0
    while i0 < len(base_units_expression):
        i0_val = base_units_expression[i0]  # define current value
        ip1 = i0 + 1  # define right index
        ip1_val = None  # standardize the right value

        try:  # try to define the real values
            ip1_val = base_units_expression[ip1]
        except IndexError:
            pass

        if i0 == 0 and (i0_val in ('*', '+', '-') or i0_val[0] == '^'):
            del base_units_expression[0]  # delete invalid symbols up front
            i0 -= 1  # reset iterative
        elif i0_val == '(' and ip1_val == ')':
            del base_units_expression[i0: ip1 + 1]  # delete empty parentheses
            i0 -= 1  # reset iterative
        elif i0_val == '(' and (ip1_val in ('*', '+', '-') or ip1_val[0] == '^'):
            del base_units_expression[ip1]  # delete invalid symbols right of opening parenthesis
            i0 -= 1  # reset iterative
        elif i0_val in SI_base_units + (')',):
            if ip1_val in SI_base_units + ('(',):
                base_units_expression = base_units_expression[:ip1] + ['*'] + base_units_expression[ip1:]
        elif i0_val == '/':  # check also if a unit is divided and rewrite expression
            if ip1_val in SI_base_units:
                base_units_expression[i0] = '*'
                base_units_expression = base_units_expression[:ip1 + 1] + ['^-1'] + base_units_expression[ip1 + 1:]
        i0 += 1  # update iterative

    # can probably be incorporated in the upper loop for increased efficiency
    power_fixed_expression = []
    remaining_expression = base_units_expression.copy()
    while remaining_expression:

        # define initial values
        i0_val = remaining_expression[0]
        ip1_val = ip2_val = None

        try:  # try to find the real value for the adjacent right iterative
            ip1_val = remaining_expression[1]
            ip2_val = remaining_expression[2]
        except IndexError:
            pass

        if i0_val in SI_base_units:  # if the current value is a default SI unit
            if ip1_val and ip1_val[0] == '^':  # and the adjacent right value is a power, concatenate the two
                power_fixed_unit = i0_val + ip1_val

                # update the rest of the list
                power_fixed_expression += [power_fixed_unit]
                del remaining_expression[0:2]
            else:  # if the adjacent right value is not a power, standardize the power of the SI unit
                power_fixed_expression += [i0_val + '^1']
                del remaining_expression[0]
        elif i0_val == ')':

            # check whether adjacent right value is a power
            if ip1_val and ip1_val[0] == '^':
                power_fixed_expression += [i0_val, ip1_val]
                del remaining_expression[0:2]
            else:  # just update the list
                power_fixed_expression += [i0_val]
                del remaining_expression[0]
        else:

            # if the adjacent right value is a power, this means that this quantity is unit-less, thus, replace the
            #   power with a 1 for easy computation of a unit-less quantity
            if ip1_val and ip1_val[0] == '^':
                if ip2_val in SI_base_units:  # unless the consecutive adjacent value is an SI unit
                    power_fixed_expression += [i0_val]
                    del remaining_expression[0:2]
                else:
                    power_fixed_expression += [i0_val, '1']
                    del remaining_expression[0:2]
            else:
                power_fixed_expression += [i0_val]
                del remaining_expression[0]
    return power_fixed_expression


def unit_handler(unit_expression):
    """
    Handles/computes the units. This assumes that some other script makes sure that if the unit expression contains
    parentheses, these are all passed separately through this handler. Thus, it does not account for parentheses.

    Parameters
    unit_expression : list
        The unit expression (separated around units and math operators) that is to be solved.

    Returns
        The solved expression.
    """

    i0 = 0
    temp_expression = unit_expression.copy()
    while i0 < len(temp_expression):
        i0_val = temp_expression[i0]  # define current value
        ip1, im1 = i0 + 1, i0 - 1  # define right and left indexes
        ip1_val = None  # set standard value
        try:  # try to find real right value
            ip1_val = temp_expression[ip1]
        except IndexError:
            pass

        # cleanup the expression for consecutive symbols and invalid symbols up front, and start computing units
        # if the first iterative is a math symbol, delete and continue
        if i0 == 0 and (i0_val in ('+', '-', '/', '*') or i0_val[0] == '^'):  # might not be needed due to L436-444
            if ip1_val == '1':
                del temp_expression[1]
            del temp_expression[0]
            i0 = 0
        elif i0_val == '/' and ip1_val in ('+', '-', '/'):
            del temp_expression[ip1]
        elif i0_val == '/' and ip1_val == '*':
            del temp_expression[i0]
        elif i0_val == '*':
            if ip1_val in ('+', '-', '*', '1'):
                del temp_expression[ip1]
            elif ip1_val == '/' or not ip1_val:
                del temp_expression[i0]
            elif i0 != 0:
                # if i0 != 0 this must mean that i0 - 1 is not a symbol, thus:
                im1 = i0 - 1
                im1_val = temp_expression[i0 - 1]
                stop_list = [i for i in math_ops if i != '*']
                j0 = ip1  # define new iterative, to check for any valid products in product line
                j0_val = temp_expression[j0]
                while j0_val not in stop_list:
                    left_values, right_values = im1_val.split('^'), j0_val.split('^')

                    # if an iteration is the same unit, solve that value and the initial value together
                    if left_values[0] == right_values[0] and len(left_values) == 2 and len(right_values) == 2:
                        prod_val = unit_operations('*', im1_val, j0_val)[0]

                        # update temporary variables
                        temp_expression[im1] = prod_val
                        del temp_expression[j0 - 1:j0 + 1]
                        j0 -= 1
                    else:  # else just update values
                        j0 += 1
                    im1_val = temp_expression[im1]  # ensure that the i0_val is updated, corresponding to the new value

                    # try to update j0_val, set to '+' if fail
                    try:
                        j0_val = temp_expression[j0]
                    except IndexError:
                        j0_val = '+'
                i0 += 1  # update main iterative
            else:
                i0 += 1
        elif i0_val in ('+', '-') and ip1_val in ('+', '-'):
            del temp_expression[ip1]
        elif i0_val in ('+', '-', '/', '*') and not ip1_val:
            del temp_expression[i0]
        else:
            i0 += 1

    # if temporary expression is without unit, terminate computation
    if temp_expression == ['1']:
        return temp_expression

    # fix the rest of the multiplication after reducing expression
    i0 = 0
    while i0 < len(temp_expression):
        i0_val = temp_expression[i0]  # define current value
        ip1 = i0 + 1  # define right value
        try:  # try to define real values
            ip1_val = temp_expression[ip1]
        except IndexError:
            ip1_val = None

        if ip1_val == '*':
            ip2_val = temp_expression[i0 + 2]
            product_result = unit_operations('*', i0_val, ip2_val)
            temp_expression[i0] = nsu.list_to_string(product_result)
            del temp_expression[ip1:i0 + 3]
        else:
            i0 += 1

    # fix all addition/subtraction elements
    # note here that due to the functionality of units in general, if two summed elements does not have the same unit
    #   the operation is invalid; therefore, the script can be simplified greatly
    i0 = 0
    while i0 < len(temp_expression):

        # define initial values
        i0_val = temp_expression[i0]
        ip1 = i0 + 1
        ip1_val = None

        try:  # try to define real values
            ip1_val = temp_expression[ip1]
        except IndexError:
            pass

        if ip1_val in ('+', '-'):
            ip2_val = temp_expression[i0 + 2]
            i0_list = i0_val.split('*')
            ip2_list = ip2_val.split('*')
            if set(i0_list) == set(ip2_list):
                temp_expression[i0] = i0_val
                del temp_expression[ip1:i0 + 3]
            else:
                raise ValueError(f'Unit operation \'{i0_val} {ip1_val} {ip2_val}\' is invalid.')
        else:
            i0 += 1
    return temp_expression


def unit_abbreviator(unit, delim='*'):
    """
    Abbreviates an SI unit expression to a simple derived unit if easily recognizable.

    Parameters
        unit : str
            Input unit expression.
        delim : str, optional
            Delimiter that splits the SI unit into a list containing the SI units. The default is '*'.

    Returns
        A derived unit if successful abbreviation, else returns the input expression.
    """

    supported_abbreviations = [list(i) for i in from_SI_to_derivative]

    # invert abbreviations
    inverted_abbreviations = [], []
    for i, j in zip(*supported_abbreviations):
        inverted_abbreviations[1].append(j + '^-1')
        temp_res = []
        for k in i:
            k_split = k.split('^')
            if len(k_split) == 1:
                temp_res.append(k + '^-1')
            else:
                if k_split[1][0] == '-':
                    if k_split[1][1:] == '1':
                        temp_res.append(k_split[0])
                    else:
                        temp_res.append(k_split[0] + '^' + k_split[1][1:])
                else:
                    temp_res.append(k_split[0] + '^-' + k_split[1])
        inverted_abbreviations[0].append(temp_res)

    # collect all abbreviations and sort them, so that the largest one is first, trying to reduce the expression most
    abbreviations = supported_abbreviations[0] + inverted_abbreviations[0], supported_abbreviations[1] + \
                    inverted_abbreviations[1]
    sorted_abbreviations = nsu.string_sorter(*abbreviations, reverse=True)

    # replace matching abbreviations in given unit set
    split_unit = [i for i in unit.split(delim) if i != '']  # fix blank elements
    replaced_unit_set = [e for i, e in zip(*sorted_abbreviations) if set(i) == set(split_unit)]

    try:  # check if a unit replacement occurred, otherwise output initial unit
        replaced_unit = replaced_unit_set[0]
    except IndexError:
        replaced_unit = unit
    return replaced_unit


def unit_parser(math_string, unit_identifier=' ', result='math', **kwargs):
    """
    Process a mathematical string containing units, with units defined by an identifier.

    Parameters
        math_string : str
            The mathematical string to parse.
        unit_identifier : str, optional
            The specific identifier set for notifying a unit. E.g. if set to '~', all units must be denoted as '~cm',
            '~kg', etc. The default is ' '.
        result : str, optional
            Set the specific result output. If 'math', simply returns the float result of the computation (without
            units). If 'math + unit', returns a string with the final units appended to the float. If 'math, unit',
            gives a list that contains the math result as float and the unit result. The default is 'math'.

    Keyword Arguments
        true_string : str
            Kwarg for mathpar.parser(), which is the script used to compute the numerical value of the expression.
            Check mathpar.parser() for more information.
        cprint : str
            Sets the printing mode for mathpar.parser(). Again, check mathpar.parser() for more information.
        supp_units : tuple
            A specific list of supported units can be given here. Note that it may not contain any units that are not
            natively supported by this script.
        abb_unit : bool
            Specify whether the script should attempt to condense the resulting unit into a derived SI unit.

    Returns
        The computed result as set by the result parameter.
    """

    # check and fix kwargs
    parser_true_string, parser_print, abb_unit = math_string, 'num', True
    if 'true_string' in kwargs.keys():
        parser_true_string = kwargs.get('true_string')
    if 'cprint' in kwargs.keys():
        parser_print = kwargs.get('cprint')
    if 'abb_unit' in kwargs.keys():
        abb_unit = kwargs.get('abb_unit')
    if 'supp_units' in kwargs.keys():
        supported_units = kwargs.get('supp_units')
    else:
        supported_units = []
        for i in supported_base_units:
            for j in [unit_identifier + i for i in prefix_scalars]:
                supported_units.append(j + i)
        supported_units += [unit_identifier + i for i in supported_special_units]

    # define list of all supported values for the unit isolated list
    supported_units_and_mo = tuple(nsu.string_sorter(supported_units + list(math_ops), reverse=True))
    separated_units = unit_separator(math_string, supported_units_and_mo, unit_identifier)
    unit_list_contained, unit_list_scalars, unit_list_SI = unit_converter(separated_units, unit_identifier)

    # if no units are found in the expression, run expression through .parser() and exit
    if not unit_list_SI:
        unit_result = ''
        math_result = nsp.parser(math_string, steps=False, cprint=parser_print, true_string=parser_true_string)
        comp_result = str(math_result) + unit_result
        if result == 'math':
            return math_result
        elif result == 'math + unit':
            return comp_result
        elif result == 'math, unit':
            return math_result, unit_result
        else:
            raise ValueError(f'Result type \'{result}\' is invalid.')

    replaced_unit_string, fixed_unit_list_SI, contained_units = unit_replacer(math_string, unit_list_contained,
                                                                              unit_list_scalars, unit_list_SI)
    solved_unit_expression = unit_solver(separated_units, contained_units, fixed_unit_list_SI)

    temp_index = nsu.indexer(solved_unit_expression)  # index initial unit expression
    temp_bracket_idx = [[k] + [e] for k, e in temp_index if e in ('(', ')')]  # find and index open/close brackets

    # solve units in parentheses first
    i0 = 0
    while temp_bracket_idx:

        # find and solve innermost parentheses first and work outwards
        ip1 = i0 + 1
        try:  # check for missing closing parenthesis
            closing_bracket = temp_bracket_idx[ip1][1]
        except IndexError:
            raise ValueError(f'Missing closing bracket for open bracket at \'{temp_bracket_idx[i0][0]}\'.')

        if temp_bracket_idx[i0][1] == '(' and closing_bracket == ')':
            ob_id, cb_id = temp_bracket_idx[i0][0], temp_bracket_idx[ip1][0]  # define current bracket id
            bracket_expression = solved_unit_expression[ob_id + 1: cb_id]  # string consisting only of the clause

            if bracket_expression:  # check if bracket clause is empty
                bracket_result = unit_handler(bracket_expression)
                if bracket_result:
                    bracket_result = nsu.split(bracket_result[0], '*')
            else:
                bracket_result = []

            # try to find left and right values in respect to the parentheses
            try:
                right_val = solved_unit_expression[cb_id + 1]
            except IndexError:
                right_val = None
            try:
                left_val = solved_unit_expression[ob_id - 1]
            except IndexError:
                left_val = ''

            if left_val == '/':
                div_par_start = ob_id - 1
                div_value = -1
                if bracket_result:  # check if there is an actual result from the clause
                    div_change_value = '*'  # define multiplication if that is the case
                else:
                    div_change_value = None
            else:
                div_par_start = ob_id
                div_value = 1
                div_change_value = None

            if right_val and right_val[0] == '^':
                power_end = cb_id + 1
                try:  # try to grab direct float value, else send to .parser() and try to solve the power
                    pow_value = float(right_val[1:])
                except ValueError:
                    pow_value = nsp.parser(right_val[1:], cprint=False)
            else:
                power_end = cb_id
                pow_value = 1

            # if a power is taken to the parenthesis, solve this power
            if right_val and right_val[0] == '^' or left_val == '/':
                j0 = 0
                while j0 < len(bracket_result):

                    # check if current element is a power value
                    j0_val = bracket_result[j0]
                    j0_power_split = nsu.split(j0_val, '^')
                    if '^' in j0_power_split:  # if so, solve the power with the parenthesis power
                        unit_power_product = float(j0_power_split[-1]) * pow_value * div_value
                        unit_power_string = str(nsu.float_to_int(unit_power_product))
                        j0_power_split[-1] = unit_power_string  # fix new power to the current element
                        bracket_result[j0] = nsu.list_to_string(j0_power_split)  # fix the new unit value to the result
                    j0 += 1

            # update input list
            if div_change_value:
                solved_unit_expression = solved_unit_expression[:div_par_start] + [div_change_value] + bracket_result + \
                                         solved_unit_expression[power_end + 1:]
            else:
                solved_unit_expression = solved_unit_expression[:div_par_start] + bracket_result + \
                                         solved_unit_expression[power_end + 1:]
            temp_index = nsu.indexer(solved_unit_expression)
            temp_bracket_idx = [[k] + [e] for k, e in temp_index if e in ('(', ')')]
            i0 -= 1  # reset iteration
            continue
        i0 += 1

    # when all parentheses have been dissolved, solve the final equation
    if solved_unit_expression:
        solved_unit_expression = unit_handler(solved_unit_expression)

    if solved_unit_expression and solved_unit_expression != ['1']:  # if any expression is left, prettify result
        if solved_unit_expression[0] == '*':
            del solved_unit_expression[0]

        # prettify the unit result
        solved_unit_expression_split = solved_unit_expression[0].split('*')

        # sort the units so that negative powers are last
        power_split_units = [i.split('^') for i in solved_unit_expression_split]
        relist_split_unit = list(zip(*power_split_units))
        sorted_unit_expression = nsu.string_sorter(relist_split_unit[1], relist_split_unit[0])
        sorted_unit_expression_split = [i + '^' + j for i, j in zip(sorted_unit_expression[1],
                                                                    sorted_unit_expression[0])]

        # prettify the units so that ^1 units are normalized to just the unit
        solved_unit_expression_final = []
        for i in sorted_unit_expression_split:
            i_split = i.split('^')
            if i_split[0] in SI_base_units:
                if i_split[1] == '1':  # check if the power is ^1, and reduce expression accordingly
                    solved_unit_expression_final.append(' ' + i_split[0])
                else:
                    solved_unit_expression_final.append(' ' + i)
    else:  # else just set default 'no unit' as 'a.u.'
        solved_unit_expression_final = [' a.u.']

    # pass through the replaced expression in .parser()
    unit_result = nsu.list_to_string(solved_unit_expression_final)
    if abb_unit:  # abbreviate unit result, if called
        abb_res = unit_abbreviator(unit_result, ' ')
        if abb_res[0] == ' ':  # fix spacing after abbreviation
            unit_result = abb_res
        else:
            unit_result = ' ' + abb_res
    math_result = nsp.parser(replaced_unit_string, steps=False, cprint=parser_print, true_string=parser_true_string,
                             unit_res=unit_result)
    comp_result = str(math_result) + unit_result
    if result == 'math':
        return math_result
    elif result == 'math + unit':
        return comp_result
    elif result == 'math, unit':
        return math_result, unit_result
    else:
        raise ValueError(f'Result type \'{result}\' is invalid.')
