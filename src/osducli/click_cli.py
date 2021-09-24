# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Entry or launch point for CLI.

Handles creating and launching a CLI to handle a user command."""

import collections
import functools
import json
import logging
from os import path

import click

from osducli.config import CLI_ENV_VAR_PREFIX, CLIConfig
from osducli.log import get_logger
from osducli.state import get_default_config

# from osducli.util import is_help_command


class State:  # pylint: disable=too-few-public-methods
    """Global state passed to all click commands"""

    def __init__(self):
        self.debug = False
        self.config_path = None
        self.config = None
        self.output = None
        self.jmes = None

    def __repr__(self):
        return f"State=Debug: {self.debug}, Config path: {self.config_path}"


def global_params(func):
    """Handle global parameters setting to setup state and remove parameters from those passed
    to the decorated function call."""

    def debug_callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.debug = value
        logging.basicConfig()
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        if value:
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            logger = get_logger(__name__)
            # logger.setLevel(logging.DEBUG)
            # requests_log = logging.getLogger("urllib3")
            # requests_log.setLevel(logging.DEBUG)
            # requests_log.propagate = True
            logger.debug("Debugging enabled")
        return value

    def config_callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.config_path = value
        if value:
            config_path, config_file = path.split(value)
            state.config = CLIConfig(config_path, CLI_ENV_VAR_PREFIX, config_file)
        else:
            state.config = get_default_config(True)
        return value

    pass_state = click.make_pass_decorator(State)

    @click.option(
        "--debug/--no-debug",
        default=False,
        envvar="REPO_DEBUG",
        help="Increase logging verbosity to show all debug logs.",
        callback=debug_callback,
    )
    @click.option(
        "-c",
        "--config",
        envvar="OSDU_CONFIG",
        help="Path to a configuration file. You can configure the default file using 'osducli config default'.",
        type=click.Path(readable=True),
        callback=config_callback,
    )
    @functools.wraps(func)
    @pass_state
    def wrapper(*args, **kwargs):
        kwargs.pop("debug")
        kwargs.pop("config")
        return func(*args, **kwargs)

    return wrapper


def command_with_output(table_transformer=None):
    """Handle global parameters setting to setup state and remove parameters from those passed
    to the decorated function call."""

    def wrapper_for_params(func):
        def output_callback(ctx, _, value):
            state = ctx.ensure_object(State)
            state.output = value
            return value

        def jmes_callback(ctx, _, value):
            state = ctx.ensure_object(State)
            state.jmes = value
            return value

        @click.option(
            "-o",
            "--output",
            envvar="OSDU_CONFIG",
            type=click.Choice(["json"], case_sensitive=False),
            help="Output format (default is a user friendly table format).",
            callback=output_callback,
        )
        @click.option(
            "--query",
            help="JMESPath query string. See http://jmespath.org/ for more information and examples.",
            callback=jmes_callback,
        )
        @functools.wraps(func)
        @global_params
        def func_wrapper(*args, **kwargs):
            state = args[0]
            kwargs.pop("output")
            kwargs.pop("query")
            result = func(*args, **kwargs)
            if result is not None:
                if type(result) in [dict, list]:
                    if state.jmes is not None or (
                        table_transformer is not None and state.output is None
                    ):
                        jmes = state.jmes if state.jmes is not None else table_transformer
                        try:
                            from jmespath import Options
                            from jmespath import compile as compile_jmespath

                            query_expression = compile_jmespath(jmes)
                            result = query_expression.search(
                                result, Options(collections.OrderedDict)
                            )
                        except KeyError as ex:
                            # Raise a ValueError which argparse can handle
                            raise ValueError from ex

                    if state.output == "json":
                        print(json.dumps(result, indent=2))
                    else:
                        result_list = result if isinstance(result, list) else [result]
                        # should_sort_keys = not state.jmes
                        table_output = _TableOutput(False)  # should_sort_keys)
                        print(table_output.dump(result_list))

        return func_wrapper

    return wrapper_for_params


class _TableOutput:  # pylint: disable=too-few-public-methods

    SKIP_KEYS = []

    def __init__(self, should_sort_keys=False):
        self.should_sort_keys = should_sort_keys

    @staticmethod
    def _capitalize_first_char(text: str):
        return text[0].upper() + text[1:] if text else text

    def _auto_table_item(self, item):
        new_entry = collections.OrderedDict()
        try:
            keys = sorted(item) if self.should_sort_keys and isinstance(item, dict) else item.keys()
            for k in keys:
                if k in _TableOutput.SKIP_KEYS:
                    continue
                if item[k] is not None and not isinstance(item[k], (list, dict, set)):
                    new_entry[_TableOutput._capitalize_first_char(k)] = item[k]
        except AttributeError:
            # handles odd cases where a string/bool/etc. is returned
            if isinstance(item, list):
                for col, val in enumerate(item):
                    new_entry["Column{}".format(col + 1)] = val
            else:
                new_entry["Result"] = item
        return new_entry

    def _auto_table(self, result):
        if isinstance(result, list):
            new_result = []
            for item in result:
                new_result.append(self._auto_table_item(item))
            return new_result
        return self._auto_table_item(result)

    def dump(self, data):
        """Dump table data to a tabulated string

        Args:
            data ([type]): [description]

        Raises:
            ValueError: [description]

        Returns:
            [type]: [description]
        """
        from tabulate import tabulate

        table_data = self._auto_table(data)
        table_str = (
            tabulate(table_data, headers="keys", tablefmt="simple", disable_numparse=True)
            if table_data
            else ""
        )
        if table_str == "\n":
            raise ValueError("Unable to extract fields for table.")
        return table_str + "\n"
