# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Entry or launch point for CLI.

Handles creating and launching a CLI to handle a user command."""

import collections
import functools
import importlib
import logging
from os import read
import os.path
import json
import pkgutil

import click
from click.core import Context
from click.formatting import HelpFormatter

from osducli.config import CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX, CLI_NAME, CLIConfig
from osducli.log import get_logger
from osducli.state import get_default_config

# from osducli.util import is_help_command


def get_commands_from_pkg(pkg) -> dict:
    keep_groups = ["osducli.commands.list", "osducli.commands.unit"]
    pkg_obj = importlib.import_module(pkg)

    pkg_path = os.path.dirname(pkg_obj.__file__)
    commands = {}
    for module in pkgutil.iter_modules([pkg_path]):
        module_obj = importlib.import_module(f"{pkg}.{module.name}")

        if not module.ispkg:
            if hasattr(module_obj, "_click_command"):
                commands[module.name] = module_obj._click_command
                # print(f"Add command {pkg}.{module.name}")

        else:
            group_commands = get_commands_from_pkg(f"{pkg}.{module.name}")
            if len(group_commands) == 1 and not f"{pkg}.{module.name}" in keep_groups:
                # print(f"Add command {pkg}.{module.name} - {module.name.replace('_', '-')}")
                click_command = list(group_commands.values())[0]
                click_command.context_settings["help_option_names"] = ["-h", "--help"]
                commands[module.name.replace("_", "-")] = click_command
            elif len(group_commands) >= 1:
                # print(f"Add group {module.name.replace('_', '-')}\n{group_commands}")
                commands[module.name.replace("_", "-")] = click.Group(
                    context_settings={"help_option_names": ["-h", "--help"]},
                    help=module_obj.__doc__,
                    commands=group_commands,
                )
            # else:
            #     print(f"Skip group {module.name.replace('_', '-')}")
    # if len(commands) > 0:
    #     print(f"return {len(commands)}")
    #     print(commands)
    return commands


class State(object):
    def __init__(self):
        self.debug = False
        self.config_path = None
        self.config = None
        self.output = None
        self.jmes = None

    def __repr__(self):
        return f"State=Debug: {self.debug}, Config path: {self.config_path}"


def cache(seconds=None):
    def callabl(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            cache_key = [func, args, kwargs]
            result = _cache.get(cache_key)
            if result:
                return result
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, timeout=seconds)
            return result

        return wrapped

    return callabl


def command_with_output(table_transformer=None):
    """Handle global parameters setting to setup state and remove parameters from those passed
    to the decorated function call."""

    def wrapper_for_params(func):
        # @wraps(func)
        # def wrapped(*args, **kwargs):
        #     cache_key = [func, args, kwargs]
        #     result = _cache.get(cache_key)
        #     if result:
        #         return result
        #     result = func(*args, **kwargs)
        #     _cache.set(cache_key, result, timeout=seconds)
        #     return result

        # return wrapped

        def debug_callback(ctx, _, value):
            state = ctx.ensure_object(State)
            state.debug = value
            if value:
                logging.basicConfig()
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
            return value

        def output_callback(ctx, _, value):
            state = ctx.ensure_object(State)
            state.output = value
            return value

        def jmes_callback(ctx, _, value):
            state = ctx.ensure_object(State)
            state.jmes = value
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
        @pass_state
        def func_wrapper(*args, **kwargs):
            state = args[0]
            kwargs.pop("debug")
            kwargs.pop("config")
            kwargs.pop("output")
            kwargs.pop("query")
            state.config = get_default_config(True)
            result = func(*args, **kwargs)

            if result is not None:
                if isinstance(result, dict):
                    if state.jmes is not None or (
                        table_transformer is not None and state.output is None
                    ):
                        jmes = state.jmes if state.jmes is not None else table_transformer 
                        try:
                            from jmespath import compile as compile_jmespath
                            from jmespath import Options

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
                        should_sort_keys = not state.jmes
                        to = _TableOutput(should_sort_keys)
                        print(to.dump(result_list))
            return

        return func_wrapper

    return wrapper_for_params




def global_params(func):
    """Handle global parameters setting to setup state and remove parameters from those passed
    to the decorated function call."""

    def debug_callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.debug = value
        if value:
            logging.basicConfig()
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
        return value

    def output_callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.output = value
        return value

    def jmes_callback(ctx, _, value):
        state = ctx.ensure_object(State)
        state.jmes = value
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
    @pass_state
    def wrapper(*args, **kwargs):
        state = args[0]
        kwargs.pop("debug")
        kwargs.pop("config")
        kwargs.pop("output")
        kwargs.pop("query")
        state.config = get_default_config(True)
        result, transformer = func(*args, **kwargs)

        if result is not None:
            if isinstance(result, dict):
                if state.jmes is not None or (transformer is not None and state.output is None):
                    if state.jmes is not None:
                        transformer = state.jmes
                    try:
                        from jmespath import compile as compile_jmespath
                        from jmespath import Options

                        query_expression = compile_jmespath(transformer)
                        result = query_expression.search(result, Options(collections.OrderedDict))
                    except KeyError as ex:
                        # Raise a ValueError which argparse can handle
                        raise ValueError from ex

                if state.output == "json":
                    print(json.dumps(result, indent=2))
                else:
                    result_list = result if isinstance(result, list) else [result]
                    should_sort_keys = not state.jmes
                    to = _TableOutput(should_sort_keys)
                    print(to.dump(result_list))
        return

    return wrapper


class _TableOutput(object):  # pylint: disable=too-few-public-methods

    SKIP_KEYS = ["id", "type", "etag"]

    def __init__(self, should_sort_keys=False):
        self.should_sort_keys = should_sort_keys

    @staticmethod
    def _capitalize_first_char(x):
        return x[0].upper() + x[1:] if x else x

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


class CustomHelpGroup(click.Group):
    def format_help(self, ctx, formatter):
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        # click.Command.format_options(self, ctx, formatter)
        self.format_commands(ctx, formatter)
        self.format_epilog(ctx, formatter)
        self.format_global_options(ctx, formatter)

    def format_global_options(self, ctx: Context, formatter: HelpFormatter) -> None:
        """Writes all the options into the formatter if they exist."""
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                opts.append(rv)

        if opts:
            with formatter.section("Global Options"):
                formatter.write_dl(opts)


@click.group(
    cls=CustomHelpGroup,
    commands=get_commands_from_pkg("osducli.commands"),
    context_settings={"help_option_names": ["-h", "--help"]},
)
# @click.group()
@click.pass_context
def cli(ctx):
    """
    \b
     ___  ___  ___  _ _
    | . |/ __]| . \| | |
    | | |\__ \| | || | |
    `___'[___/|___/ \__|

    Welcome to the OSDU CLI!
    Note: This is currently a work in progress. Please share ideas / issues on the git page.

    Use `osducli version` to display the current version.

    Usage:
    osdu [command]
    """
    ctx.obj = State()
