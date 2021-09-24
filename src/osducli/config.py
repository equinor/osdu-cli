# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Read and modify configuration settings related to the CLI"""

import configparser
import os
import stat

from osducli.util.file import ensure_directory_exists

_UNSET = object()


# Default names
CLI_NAME = "osducli"
CLI_CONFIG_DIR = os.path.expanduser(os.path.join("~", ".{0}".format(CLI_NAME)))
CLI_ENV_VAR_PREFIX = CLI_NAME

CONFIG_SERVER = "server"
CONFIG_ENTITLEMENTS_URL = "entitlements_url"
CONFIG_FILE_URL = "file_url"
CONFIG_LEGAL_URL = "legal_url"
CONFIG_SCHEMA_URL = "schema_url"
CONFIG_SEARCH_URL = "search_url"
CONFIG_STORAGE_URL = "storage_url"
CONFIG_UNIT_URL = "unit_url"
CONFIG_WORKFLOW_URL = "workflow_url"

CONFIG_DATA_PARTITION_ID = "data_partition_id"
CONFIG_LEGAL_TAG = "legal_tag"
CONFIG_ACL_VIEWER = "acl_viewer"
CONFIG_ACL_OWNER = "acl_owner"

CONFIG_AUTHENTICATION_MODE = "authentication_mode"

CONFIG_AUTHENTICATION_AUTHORITY = "authority"
CONFIG_AUTHENTICATION_SCOPES = "scopes"

CONFIG_TOKEN_ENDPOINT = "token_endpoint"
CONFIG_REFRESH_TOKEN = "refresh_token"
CONFIG_CLIENT_ID = "client_id"
CONFIG_CLIENT_SECRET = "client_secret"

# TO DO: Add the below back in
# pylint: disable=C0115, C0116


class CLIConfig:
    _BOOLEAN_STATES = {
        "1": True,
        "yes": True,
        "true": True,
        "on": True,
        "0": False,
        "no": False,
        "false": False,
        "off": False,
    }

    _DEFAULT_CONFIG_FILE_NAME = "config"
    _CONFIG_DEFAULTS_SECTION = "defaults"

    def __init__(
        self,
        config_dir,
        config_env_var_prefix,
        config_file_name=None,
    ):
        """Manages configuration options available in the CLI

        :param config_dir: The directory to store config files
        :type config_dir: str
        :param config_env_var_prefix: The prefix for config environment variables
        :type config_env_var_prefix: str
        :param config_file_name: The name given to the config file to be created
        :type config_file_name: str
        """
        # ensure_dir(config_dir)
        env_var_prefix = "{}_".format(config_env_var_prefix.upper())
        default_config_dir = os.path.expanduser(config_dir)
        self.config_dir = os.environ.get("{}CONFIG_DIR".format(env_var_prefix), default_config_dir)
        self.config_file_name = config_file_name or CLIConfig._DEFAULT_CONFIG_FILE_NAME
        self.config_path = os.path.join(self.config_dir, self.config_file_name)
        self._env_var_format = "{}{}".format(env_var_prefix, "{section}_{option}")
        self.defaults_section_name = CLIConfig._CONFIG_DEFAULTS_SECTION

        self.config_parser = configparser.ConfigParser()
        if os.path.exists(self.config_path):
            self.config_parser.read(self.config_path)

    def env_var_name(self, section, option):
        return self._env_var_format.format(section=section.upper(), option=option.upper())

    def has_option(self, section, option):
        if self.env_var_name(section, option) in os.environ:
            return True
        return self.config_parser.has_option(section, option) if self.config_parser else False

    def get(self, section, option, fallback=_UNSET):
        env = self.env_var_name(section, option)
        if env in os.environ:
            return os.environ[env]
        last_ex = None
        try:
            if self.config_parser:
                return self.config_parser.get(section, option)
            raise configparser.NoOptionError(option, section)
        except (configparser.NoSectionError, configparser.NoOptionError) as ex:
            last_ex = ex

        if fallback is _UNSET:
            raise last_ex  # pylint:disable=raising-bad-type
        return fallback

    def sections(self):
        return self.config_parser.sections() if self.config_parser else []

    def items(self, section):
        import re

        # Only allow valid env vars, in all caps: CLI_SECTION_TEST_OPTION, CLI_SECTION__TEST_OPTION
        pattern = self.env_var_name(section, "([0-9A-Z_]+)")
        env_entries = []
        for k in os.environ:
            # Must be a full match, otherwise CLI_SECTION_T part in CLI_MYSECTION_Test_Option will match
            matched = re.fullmatch(pattern, k)
            if matched:
                # (name, value, ENV_VAR_NAME)
                item = (matched.group(1).lower(), os.environ[k], k)
                env_entries.append(item)

        # Prepare result with env entries first
        result = {c[0]: c for c in env_entries}
        # Add entries from config file if they do not exist yet
        try:
            entries = self.config_parser.items(section) if self.config_parser else []
            for name, value in entries:
                if name not in result:
                    result[name] = (name, value, self.config_path)
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass
        return [
            {"name": name, "value": value, "source": source}
            for name, value, source in result.values()
        ]

    def getint(self, section, option, fallback=_UNSET):
        return int(self.get(section, option, fallback))

    def getfloat(self, section, option, fallback=_UNSET):
        return float(self.get(section, option, fallback))

    def getboolean(self, section, option, fallback=_UNSET):
        val = str(self.get(section, option, fallback))
        if val.lower() not in CLIConfig._BOOLEAN_STATES:
            raise ValueError("Not a boolean: {}".format(val))
        return CLIConfig._BOOLEAN_STATES[val.lower()]

    def set(self, config):
        ensure_directory_exists(self.config_dir)
        with open(self.config_path, "w") as configfile:
            # if self.config_comment:
            #     configfile.write(self.config_comment + '\n')
            config.write(configfile)
        os.chmod(self.config_path, stat.S_IRUSR | stat.S_IWUSR)
        self.config_parser.read(self.config_path)

    def set_value(self, section, option, value):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        try:
            config.add_section(section)
        except configparser.DuplicateSectionError:
            pass
        config.set(section, option, value)
        self.set(config)


# def get_config_value(name, section=CLI_NAME, fallback=_UNSET):
#     """Gets a config by name.

#     In the case where the config name is not found, will use fallback value."""

#     cli_config = CLIConfig(CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX)

#     return cli_config.get(section, name, fallback)


# def get_config_bool(name, section=CLI_NAME, fallback=_UNSET):
#     """Checks if a config value is set to a valid bool value."""

#     cli_config = CLIConfig(CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX)
#     return cli_config.getboolean(section, name, fallback)


# def get_config_int(name, section=CLI_NAME, fallback=_UNSET):
#     """Checks if a config value is set to a valid int value."""

#     cli_config = CLIConfig(CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX)
#     return cli_config.getint(section, name, fallback)


# def set_config_value(name, value, section=CLI_NAME):
#     """Set a config by name to a value."""

#     cli_config = CLIConfig(CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX)
#     cli_config.set_value(section, name, value)


def get_default_from_config(config, section, option, fallback=1):
    """Get the default value from configuration, replacing with fallback if not found"""
    try:
        return config.get(section, option)
    except (IndexError, configparser.NoSectionError, configparser.NoOptionError):
        return fallback


def get_default_choice_index_from_config(config, section, option, choice_list, fallback=1):
    """Get index + 1 of the current choice value from cong, replacing with fallback if not found"""
    try:
        config_val = config.get(section, option)
        return [i for i, x in enumerate(choice_list) if "name" in x and x["name"] == config_val][
            0
        ] + 1
    except (IndexError, configparser.NoSectionError, configparser.NoOptionError):
        return fallback


# def client_endpoint():
#     """Cluster HTTP gateway endpoint address and port, represented as a URL."""

#     return get_config_value("endpoint", None)
