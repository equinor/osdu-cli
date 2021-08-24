# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Entry or launch point for CLI.

Handles creating and launching a CLI to handle a user command."""

import sys
from knack.invocation import CommandInvoker
from knack.util import CommandResultItem
from osducli.config import CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX, CLI_NAME
from osducli.osdu_cli import OsduCli
from osducli.osdu_command_loader import OsduCommandLoader
from osducli.osdu_command_help import OsduCommandHelp

# from osducli.util import is_help_command


class OsduInvoker(CommandInvoker):  # pylint: disable=too-few-public-methods
    """Extend Invoker to to handle when a system service is not installed (BRS/EventStore cases)."""
    def execute(self, args):
        try:
            return super(OsduInvoker, self).execute(args)

        # For exceptions happening while handling http requests, FabricErrorException is thrown with
        # 'Internal Server Error' message, but here we handle the case where gateway is unable
        # to find the service.
        except TypeError:
            if args[0] == 'events':
                from knack.log import get_logger
                logger = get_logger(__name__)
                logger.error('Service is not installed.')
                return CommandResultItem(None, exit_code=0)
            raise


def main():
    """Main entry point for OSDU CLI.

    Configures and invokes CLI with arguments passed during the time the python
    session is launched.

    This is run every time a osducli command is invoked.

    If you have a local error, say the command is not recognized, then the invoke command will
    raise an exception.
    If you have success, it will return error code 0.
    If the HTTP request returns an error, then an exception is not thrown, and error
    code is not 0."""
    try:

        args_list = sys.argv[1:]

        osducli = OsduCli(cli_name=CLI_NAME,
                          config_dir=CLI_CONFIG_DIR,
                          config_env_var_prefix=CLI_ENV_VAR_PREFIX,
                          invocation_cls=OsduInvoker,
                          commands_loader_cls=OsduCommandLoader,
                          help_cls=OsduCommandHelp)

        # osducli.register_event(OsduCli.events.EVENT_PARSER_GLOBAL_CREATE, lambda:  OutputProducer.on_global_arguments)
        # osducli.register_event(OsduCli.events.EVENT_INVOKER_POST_PARSE_ARGS, OutputProducer.handle_output_argument)

        # is_help_cmd = is_help_command(args_list)

        exit_code = osducli.invoke(args_list)

        sys.exit(exit_code)

    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
