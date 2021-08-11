# OSDU Command Line Interface (osducli)

[![PyPi Version](https://img.shields.io/pypi/v/osducli.svg)](https://pypi.org/project/osducli/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/osducli.svg)](https://pypi.org/project/osducli/)

TODO: Other badges (build status, coverage, ..)

Command-line interface for interacting with OSDU.

![OSDU CLI](/documentation/osducli.png)

## Installation

Usage requires that you have a valid python 3.7+ installation on your machine. You might also consider creating a seperate python [virtual environment](https://docs.python.org/3/library/venv.html) for working with OSDU.

### Alternative 1 - Deploy from PyPi

For general usage this is the easiest and recommended method.

:warning: Until deployed to PyPi this alternative won't work.

```bash
pip install osducli
```

### Alternative 2 - Deploy from local copy

Download the contents of the repository and change into the root folder.

```bash
pip install .
```

### Alternative 3 - Developer setup

For those wanting to modify the code. 
See the
[corresponding wiki](https://github.com/equinor/osdu-cli/wiki) for
more information.

## Usage

The first time you use the CLI you should run the configure command to provide connection information and other important configuration.

```bash
osducli configure
```

Once configured use the CLI as shown below. Omitting a command will display a list of available options.

```bash
osducli <command>
```

For more information, specify the `-h` flag:

```bash
osducli -h
osducli <command> -h
```

## Contributing

We welcome any kind of contribution, whether it be reporting issues or sending pull requests.

When contributing to this repository abide by the
[Equinor Open Source Code of Conduct](https://github.com/equinor/opensource/blob/master/CODE_OF_CONDUCT.md).


### CLI specific issues and requests

If your issue is relevant to the OSDU CLI, please use this repositories [issue tracker](https://github.com/equinor/osdu-cli/issues).

Be sure to search for similar previously reported issues prior to creating a new one.
In addition, here are some good practices to follow when reporting issues:

- Add a `+1` reaction to existing issues that are affecting you
- Include verbose output (`--debug` flag) when reporting unexpected error messages
- Include the version of osducli installed, `pip show osducli` will report this
- Include the version of OSDU you are using

### Code changes

See the
[wiki page on contributing](https://github.com/equinor/osdu-cli/wiki) for
more information on submitting code changes.
