# OSDU Command Line Interface (osducli)
=======================================

Command-line interface for interacting with OSDU.

Usage
=====

The first time you use the CLI you should run the configure command to provide connection information and other important configuration.

.. code-block:: bash

  osducli config update

Once configured use the CLI as shown below. Omitting a command will display a list of available options.

.. code-block:: bash

  osducli <command>

For more information, specify the `-h` flag:

.. code-block:: bash

  osducli -h
  osducli <command> -h

Change Log
==========

0.0.3
-----

- Bulk upload commands (file upload still missing)
- Interactive login
- Config improvements
- Additional testing

0.0.2
-----

- Cleanup and diverse fixes
  
0.0.1
-----

- Initial release.
