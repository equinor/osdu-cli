# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Entry or launch point for CLI."""

import importlib
import os.path
import pkgutil

import click
from click.core import Context
from click.formatting import HelpFormatter

from osducli.click_cli import State


def get_commands_from_pkg(pkg) -> dict:
    """Dynamically and recursively get all click commands within the specified package

    Args:
        pkg ([type]): [description]

    Returns:
        dict: [description]
    """
    keep_groups = [
        "osducli.commands.legal",
        "osducli.commands.list",
        "osducli.commands.unit",
        "osducli.commands.schema",
        "osducli.commands.search",
        "osducli.commands.workflow",
    ]
    pkg_obj = importlib.import_module(pkg)

    pkg_path = os.path.dirname(pkg_obj.__file__)
    commands = {}
    for module in pkgutil.iter_modules([pkg_path]):
        module_obj = importlib.import_module(f"{pkg}.{module.name}")

        if not module.ispkg:
            if hasattr(module_obj, "_click_command"):
                commands[module.name] = module_obj._click_command  # pylint: disable= W0212
                # print(f"Add command {pkg}.{module.name}")

        else:
            group_commands = get_commands_from_pkg(f"{pkg}.{module.name}")
            if len(group_commands) == 1 and f"{pkg}.{module.name}" not in keep_groups:
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


class CustomHelpGroup(click.Group):
    """Custom help text for the base click command

    Args:
        click ([type]): [description]
    """

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
            _rv = param.get_help_record(ctx)
            if _rv is not None:
                opts.append(_rv)

        if opts:
            with formatter.section("Global Options"):
                formatter.write_dl(opts)


# Main entry point for OSDU CLI.
# noqa: W606,W605 pylint: disable=W1401
@click.group(
    # cls=CustomHelpGroup,
    commands=get_commands_from_pkg("osducli.commands"),
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.pass_context
def cli(ctx):
    """
    \b
     ___  ___  ___  _ _
    | . |/ __]| . \| | |
    | | |\__ \| | || | |
    `___'[___/|___/ \__|

    Welcome to the OSDU CLI!

    Note: This is currently a work in progress and may contain bugs or breaking changes.
    Please share ideas / issues on the git page.

    Use `osducli version` to display the current version.

    Usage:
    osdu [command]
    """
    ctx.obj = State()


def main():
    """Main entry point for OSDU CLI."""
    cli(None)


if __name__ == "__main__":
    main()
