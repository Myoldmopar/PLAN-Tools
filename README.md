# PLAN-TOOLS

[![Flake8](https://github.com/Myoldmopar/PLAN-Tools/actions/workflows/flake8.yml/badge.svg)](https://github.com/Myoldmopar/PLAN-Tools/actions/workflows/flake8.yml)
[![Run Tests](https://github.com/Myoldmopar/PLAN-Tools/actions/workflows/test.yml/badge.svg)](https://github.com/Myoldmopar/PLAN-Tools/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/Myoldmopar/PLAN-Tools/badge.svg?branch=main)](https://coveralls.io/github/Myoldmopar/PLAN-Tools?branch=main)
[![PyPIRelease](https://github.com/Myoldmopar/PLAN-Tools/actions/workflows/release.yml/badge.svg)](https://github.com/Myoldmopar/PLAN-Tools/actions/workflows/release.yml)
[![Documentation Status](https://readthedocs.org/projects/plan-tools/badge/?version=latest)](https://plan-tools.readthedocs.io/en/latest/?badge=latest)

Tooling to help with PLAN: Pip Links And Nonsense

## Introduction

This library is a very lightweight set of helpers to improve the user-friendliness of entry points installed with Pip.
There are other packages that help do some of this, but I struggled to get them configured exactly how I wanted, which led to this new package.
This specifically fits my Python package structure and installation needs, and may not fit anyone else's, and that's OK.
Packages that use this library should fit the following pattern:

 - Let's assume the package has these attributes:
   - Setup name: "cool_python_stuff" -- this is the name on PyPi, and the string that you Pip install
   - Package directory name: "cool" -- this is the source directory once Pip installed, and what you import in your Python
   - A Python function with no arguments called `gui_function()` declared in a file located at `cool/gui.py`
 - The `setup.py` file should declare a `setup()` function call from the `setuptools` library
 - Entry points should be declared using the `setup(entry_points={'gui_scripts': ['cool_gui=cool.gui:gui_function']})` argument form
   - The `console_scripts` key is also fine here, but this library is more likely useful for GUI applications  
 - Icons should be placed in the library, ideally for all platforms, and should be named as the following:
   - `cool/icon.png` - this will be used on Linux systems
   - `cool/icon.ico` - this will be used on Windows systems
   - `cool/icon.icns` - this will be used on MacOS systems
   - The GUI code itself should set the titlebar icon programmatically, although this won't address the taskbar icon. 

## Background and Problem Statement

OK, so `cool_python_stuff` is a Python library with some functionality exposed through an executable interface.
Pip provided executable entry points and placed them in the Python environment.
The final location of these executables is different on each platform, and also depends on whether it is a "user" or "global" install.

How do you best make use of this library and these entry points?

- Of course, you'll need to have Python installed, so you follow any directions [on Python's website](https://www.python.org/).
- In general, you'll also get the Pip package management tool, but if not, then you'll need to get that as well.
- You then Pip install this cool library, which:
  - downloads the source and dependencies,
  - places it in the current Python environment directory structure,
  - generates executable shims for each entry point,
  - and places them in the current Python environment directory structure as well.

Depending on the platform and configuration, the executable entry points _may_ be available directly from the shell, but it depends.
The Pip install process will also not create any shortcuts on the desktop or start menu, so the executables are not easily accessible.

That's where this library comes in to help.

## Usage

This helper library is "used" by both the package creator **and** the end using client.
The package manager includes this helper library as a dependency, and creates an executable entry point whose purpose is to call functions in the helper code.
Once the `cool_python_stuff` package is pip installed, the client runs this extra configuration step, which will polish up the installation.

### Developer Responsibility

- Import this library: `from plan_tools import EntryPoint`
- Create a new function `def gui_configure()`
- Inside this function, create a new `EntryPoint` instance for each `entry_point` that should get configured
- The only required EntryPoint argument is the name of the binary, which is the name declared in the `gui_scripts` string spec
- There are several optional arguments which can be found in the full library documentation.
- The `gui_configure` function can take command line arguments as desired to provide custom functionality, such as not producing certain icons.
- The configuration function could also be a GUI itself that allows users to select options before running.
- Either way, the responsibility of documenting this belongs with the package manager. 
- Once instantiated and set up properly, the EntryPoint instances have a `run()` method that should be called to actually take action. 
- This new `gui_configure` function should be declared as an entry point in the package `setup()` call with a name like `{package_name}_configure`

In addition to setting up this nice launch process, there is more polishing that can be done to enhance the user experience.
When these links are executed, and the Pip installed executable opens, the taskbar icon will just be the Python logo.
This is due to how Pip prepares these executable shims, and it is difficult to figure out how to correctly apply a taskbar icon.
This library provides a worker function that should address this problem.
In the GUI code, (Tkinter, etc.), simply import this library (`from plan_tools.runtime import fixup_taskbar_icon_on_windows`),
and then call that function with a program name (`fixup_taskbar_icon_on_windows('This Cool GUI')`).
The taskbar should now show the same icon that was registered as the program icon using the GUI library. 

### Testing

Steps to Test:

- Note which Python executable is being used
- If you are running a virtual environment, you should activate the environment or be ready to use full paths to the binaries inside the virtual environment
- Pip install the test project `pip install plan_tools_test`
- The folder name that Pip uses to place the executable shims is "Scripts" on Windows and "bin" on Mac/Linux, we'll say `{bin}` for now.
- You should be able to test run the test executable if desired: 
  - If your Python Scripts folder is on PATH, you can run it directly: `plan_tools_test_run`
  - If not, you may need to provide the path: `{path/to/venv}/{bin}/plan_tools_test_run` 
- Next run the configuration executable:
  - If your Python Scripts folder is on PATH, you can run it directly: `plan_tools_test_configure`
  - If not, you may need to provide the path: `{path/to/venv}/{bin}/plan_tools_test_configure`
- The outcome depends on the operating system:
  - On Windows, by default this should add a new desktop icon for the test package and also a start menu entry for it
  - On Linux, specifically Ubuntu (Gnome Shell), you should now be able to open the applications browser and search for Plan, and find the test executable
  - On Mac, unfortunately, we don't yet support generating an .app bundle, but that should come soon, in which case the application could be found in the Spotlight

These tests have been completed:

- Windows Virtual Environment:
  - OS: Windows
  - Python Install Location: C:\Python38
  - Python Environment: venv
  - Virtual Environment Location: C:\tmp\venv
  - Desktop Links
