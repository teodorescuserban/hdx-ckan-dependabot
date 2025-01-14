Code Quality
============

Linter Configuration
++++++++++++++++++++
This section outlines how to configure the linter, Ruff, for your local development environment in PyCharm.

Installing Ruff Linter
----------------------

Since we utilize CKAN within a Docker container, you'll need Ruff installed locally on your development machine.

The PyCharm Ruff plugin doesn't know how to use the Ruff installation from the CKAN container. It needs a Ruff executable on the Docker host (the real machine). It also cannot execute Ruff from a Python virtual environment as there doesn't seem to be a way to activate a specific virtual env before running Ruff.

Please note that since Ruff is written in the Rust programming language, you don't necessarily need to install it as a Python package, although you can. Please see below the various options.

Ruff is available as ``ruff`` on PyPI:

::

    pip install ruff

Starting with version ``0.5.0``, Ruff can be installed using their standalone installers:

::

  # On macOS and Linux.
  curl -LsSf https://astral.sh/ruff/install.sh | sh

  # On Windows.
  powershell -c "irm https://astral.sh/ruff/install.ps1 | iex"

  # For a specific version.
  curl -LsSf https://astral.sh/ruff/0.5.0/install.sh | sh
  powershell -c "irm https://astral.sh/ruff/0.5.0/install.ps1 | iex"

For **macOS Homebrew** and **Linuxbrew** users, Ruff is also available as ``ruff`` on Homebrew:

::

    brew install ruff

Direct downloads of Ruff executables:

- `Linux x86_64 <https://github.com/astral-sh/ruff/releases/download/0.5.6/ruff-x86_64-unknown-linux-gnu.tar.gz>`_
- `Linux ARM64 <https://github.com/astral-sh/ruff/releases/download/0.5.6/ruff-aarch64-unknown-linux-gnu.tar.gz>`_
- `macOS x86_64 <https://github.com/astral-sh/ruff/releases/download/0.5.6/ruff-x86_64-apple-darwin.tar.gz>`_
- `macOS ARM64 <https://github.com/astral-sh/ruff/releases/download/0.5.6/ruff-aarch64-apple-darwin.tar.gz>`_
- `Windows x86_64 <https://github.com/astral-sh/ruff/releases/download/0.5.6/ruff-x86_64-pc-windows-msvc.zip>`_


Enabling Ruff Extension in PyCharm
----------------------------------

1. Open `File` > `Settings` (or `Preferences` on macOS) > `Plugins`.
2. Ensure the ``Marketplace`` tab is active.
3. Search for and install the ``Ruff`` extension.

Configuring Ruff Extension in PyCharm
-------------------------------------

1. Go to `File` > `Settings` (or `Preferences` on macOS) > `Tools` > `Ruff`.
2. Verify that only the following options are checked:

   * ``Run ruff when Reformat Code``
   * ``Show Rule Code on inspection message``

3. Set the Ruff executable path in the ``Global`` section if it is not already set.

Ruff Configuration File
-----------------------

The configuration for Ruff can be found in the project root directory in the ``pyproject.toml`` file.
