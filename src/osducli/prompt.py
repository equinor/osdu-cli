# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Read and modify configuration settings related to the CLI"""

import getpass
import sys

from osducli.log import get_logger

logger = get_logger(__name__)

_INVALID_PASSWORD_MSG = "Passwords do not match."


class NoTTYException(Exception):
    """Exception if no interactive console available

    Args:
        Exception ([type]): [description]
    """


def _input(msg: str) -> str:
    """[summary]

    Args:
        msg (str): [description]

    Returns:
        str: [description]
    """
    result = input(msg)
    return result


def verify_is_a_tty():
    """[summary]

    Raises:
        NoTTYException: [description]
    """
    if not sys.stdin.isatty():
        logger.debug("No tty available.")
        raise NoTTYException()


def prompt(
    msg: str, default: str = None, default_value_display_length: int = None, help_string: str = None
) -> str:
    """Prompt the user for input with support for default value and help

    If the msg string contains []: and default is specified then the msg string is
    expanded to indlude default.

    If the user input is '?' then help text is displayed if specified.

    Args:
        msg (str): Message to display to the user
        default (str): Default value if nothing entered
        default_value_display_length (int): Max length for displayed default text
        help_string (str, optional): Help string shown if the user enters ?. Defaults to None.

    Returns:
        str: [description]
    """
    verify_is_a_tty()

    if default is not None:
        displayed_default = default
        if default_value_display_length and len(default) > default_value_display_length:
            displayed_default = (
                displayed_default[0 : default_value_display_length - 2] + ".."  # noqa: E203
            )

        msg = msg.replace("[]:", f"[{displayed_default}]:")

    while True:
        val = _input(msg)
        if val == "?" and help_string is not None:
            print(help_string)
            continue
        if val == "" and default is not None:
            return default

        return val


def prompt_int(msg: str, help_string: str = None) -> int:
    """[summary]

    Args:
        msg (str): [description]
        help_string (str, optional): [description]. Defaults to None.

    Returns:
        int: [description]
    """
    verify_is_a_tty()

    while True:
        value = _input(msg)
        if value == "?" and help_string is not None:
            print(help_string)
            continue
        try:
            return int(value)
        except ValueError:
            logger.warning("%s is not a valid number", value)


def prompt_pass(msg: str = "Password: ", confirm: bool = False, help_string: str = None):
    """[summary]

    Args:
        msg (str, optional): [description]. Defaults to 'Password: '.
        confirm (bool, optional): [description]. Defaults to False.
        help_string (str, optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    verify_is_a_tty()
    while True:
        password = getpass.getpass(msg)
        if password == "?" and help_string is not None:
            print(help_string)
            continue
        if confirm:
            password2 = getpass.getpass("Confirm " + msg)
            if password != password2:
                logger.warning(_INVALID_PASSWORD_MSG)
                continue
        return password


def prompt_y_n(msg: str, default: bool = None, help_string: str = None):
    """[summary]

    Args:
        msg (str): [description]
        default (bool, optional): [description]. Defaults to None.
        help_string (str, optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    return _prompt_bool(msg, "y", "n", default=default, help_string=help_string)


def prompt_t_f(msg: str, default: str = None, help_string: str = None):
    """[summary]

    Args:
        msg (str): [description]
        default (str, optional): [description]. Defaults to None.
        help_string (str, optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    return _prompt_bool(msg, "t", "f", default=default, help_string=help_string)


def _prompt_bool(
    msg: str, true_str: str, false_str: str, default: str = None, help_string: str = None
):
    """[summary]

    Args:
        msg (str): [description]
        true_str (str): [description]
        false_str (str): [description]
        default (str, optional): [description]. Defaults to None.
        help_string (str, optional): [description]. Defaults to None.

    Raises:
        ValueError: [description]

    Returns:
        [type]: [description]
    """
    verify_is_a_tty()
    if default not in [None, true_str, false_str]:
        raise ValueError("Valid values for default are {}, {} or None".format(true_str, false_str))
    _yes = true_str.upper() if default == true_str else true_str
    _no = false_str.upper() if default == false_str else false_str
    while True:
        ans = _input("{} ({}/{}): ".format(msg, _yes, _no))
        if ans == "?" and help_string is not None:
            print(help_string)
            continue
        if ans.lower() == _no.lower():
            return False
        if ans.lower() == _yes.lower():
            return True
        if default and not ans:
            return default == _yes.lower()


def prompt_choice_list(msg, a_list, default=1, help_string=None):
    """Prompt user to select from a list of possible choices.

    :param msg:A message displayed to the user before the choice list
    :type msg: str
    :param a_list:The list of choices (list of strings or list of dicts with 'name' & 'desc')
    "type a_list: list
    :param default:The default option that should be chosen if user doesn't enter a choice
    :type default: int
    :returns: The list index of the item chosen.
    """
    verify_is_a_tty()
    options = "\n".join(
        [
            " [{}] {}{}".format(
                i + 1,
                x["name"] if isinstance(x, dict) and "name" in x else x,
                " - " + x["desc"] if isinstance(x, dict) and "desc" in x else "",
            )
            for i, x in enumerate(a_list)
        ]
    )
    allowed_vals = list(range(1, len(a_list) + 1))
    while True:
        val = _input(
            "{}\n{}\nPlease enter a choice [Default choice({})]: ".format(msg, options, default)
        )
        if val == "?" and help_string is not None:
            print(help_string)
            continue
        if not val:
            val = "{}".format(default)
        try:
            ans = int(val)
            if ans in allowed_vals:
                # array index is 0-based, user input is 1-based
                return ans - 1
            raise ValueError
        except ValueError:
            logger.warning("Valid values are %s", allowed_vals)
