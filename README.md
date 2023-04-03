# PLAN-TOOLS

Tooling to help with Pip Links And Nonsense

:)

Basically a very lightweight set of helpers to create links to pip installed Python packages.
There are other packages to do similar things, but they did not work well for me, and or were too broad.
This specifically fits my Python package structure and installation needs.

The primary purpose is to create user-friendly links on the system for pip installed packages that include entry_points
in the setup.py setup() call.  (console_scripts or gui_scripts)

- On Windows this should create desktop icons or start menu entries
- On Linux this should create .desktop files that can be picked up by the desktop environment

This tool will expose a CLI and an API which can control what gets installed and where.
