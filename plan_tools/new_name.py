from os import chmod, path, stat
from pathlib import Path
from platform import system
from site import USER_BASE
from sys import exit
from sysconfig import get_path

r"""
# Installation

Make sure you have Python installed.
Then install this tool via Pip.
On Linux/Mac, the Pip binary should be on PATH, on Windows, it might be, but it might not, so I will assume it is not.
So on Windows, the Pip binary will be at %PythonInstall%\Scripts\pip.exe;
(that directory will be used as %scripts_dir% in the following steps):

- Library install
  - Windows: Run `%scripts_dir%\pip install energyplus_regressions`
  - Mac/Linux: Run `pip install energyplus_regressions`
  - You can optionally add a `--user` argument to pip install it into your local user without admin privileges
- At this point, the regression tool can be run from a terminal:
  - Windows: Run `%scripts_dir%\energyplus_regressions_runner`
  - Mac/Linux: Run `energyplus_regressions_runner`
- Configuration
  - On Windows, configure the install to create a desktop shortcut to the main GUI by running the following:
    - `%scripts_dir%\pip install energyplus_regressions_configure`
  - On Linux, configure the install to create a `.desktop` entry in the user profile
  - For most distributions, this will allow finding the application from the shell and adding it to the taskbar/dock
    - `pip install energyplus_regressions_configure`
  - On Mac, we currently don't support adding an entry to the Dock because it requires creating an .app bundle.
    - You can run the regression tool directly from the command line as above, or create your own method for execution
"""


class SingleScript:
    """
    This class represents a single executable that is packaged up by setuptools using the entry_points method.
    The entry points may live in either the console_scripts or the gui_scripts subsections.
    Either way, when the package is pip installed, it results in a binary blob in a bin/ or Scripts/ directory
    """
    def __init__(self, icon_ico: str, icon_png: str, exe_name: str, nice_name: str, description: str, wm_class: str):
        """
        Construct a single script instance, using arguments.

        :param icon_ico: The name of a windows .ico file to use, ideally at the root of the package folder
        :param icon_png: The name of a .png icon file to use, ideally at the root of the package folder
        :param exe_name: The name of a resulting executable file (without the exe extension)
        :param nice_name: The "nice" name to use to reference the tool in links and menus
        :param description: The description to show up in Linux .desktop files
        :param wm_class: The wm-class for the Tk GUI (assigned in Tk(className='energyplus_regression_runner'))
        """
        self.icon_file_name_ico = icon_ico  # ideally just a filename at the package root folder
        self.icon_file_name_png = icon_png  # ideally just a filename at the package root folder
        self.pretty_link_name = nice_name  # don't include the .lnk extension
        self.description = description
        self.wm_class = wm_class
        self.installed_binary_name = exe_name
        if system() == 'Windows':
            self.installed_binary_name += '.exe'


class InstallConfigure:
    def __init__(self):
        self.this_package_root = Path(__file__).parent

    def add_desktop_icon(self, script: SingleScript):
        if system() == 'Windows':
            self._add_desktop_icon_on_windows(script)
        elif system() == 'Linux':
            self._add_desktop_file_on_linux(script)

    def _add_desktop_icon_on_windows(self, script: SingleScript):
        from winreg import OpenKey, QueryValueEx, CloseKey, HKEY_CURRENT_USER as HKCU, KEY_READ as READ
        scripts_dir = Path(get_path('scripts'))
        icon_file = self.this_package_root / script.icon_file_name_ico
        target_exe = scripts_dir / script.installed_binary_name
        link_name = f"{script.pretty_link_name}.lnk"
        key = OpenKey(HKCU, r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders', 0, READ)
        desktop_value, _ = QueryValueEx(key, 'Desktop')
        CloseKey(key)
        desktop = Path(path.expandvars(desktop_value))
        path_link = desktop / link_name
        # noinspection PyUnresolvedReferences
        from win32com.client import Dispatch
        shell = Dispatch('WScript.Shell')
        s = shell.CreateShortCut(str(path_link))
        s.Targetpath = str(target_exe)
        s.WorkingDirectory = str(scripts_dir)
        s.IconLocation = str(icon_file)
        s.save()

    def _add_desktop_file_on_linux(self, script: SingleScript):
        # try assuming user install
        user_exe = Path(get_path('scripts')) / script.installed_binary_name
        global_exe = Path(USER_BASE) / 'bin' / script.installed_binary_name
        if user_exe.exists() and global_exe.exists():
            print(f"Detected the {script.installed_binary_name} binary in both user and global locations.")
            print("Due to this ambiguity, I cannot figure out to which one I should link.")
            print(f"User install location: {user_exe}")
            print(f"Global install location: {global_exe}")
            print("If you pip uninstall one of them, I can create a link to the remaining one!")
            return 1
        elif user_exe.exists():
            target_exe = user_exe
        elif global_exe.exists():
            target_exe = global_exe
        else:
            print(f"Could not find {script.installed_binary_name} binary at either user or global location.")
            print("This is weird since you are running this script...did you actually pip install this tool?")
            print("Make sure to pip install the tool and then retry")
            return 1
        icon_file = self.this_package_root / script.icon_file_name_png
        desktop_file = Path.home() / '.local' / 'share' / 'applications' / f'{script.installed_binary_name}.desktop'
        with open(desktop_file, 'w') as f:
            f.write(f"""[Desktop Entry]
Name={script.pretty_link_name}
Comment={script.description}
Exec={target_exe}
Icon={icon_file}
Type=Application
Terminal=false
StartupWMClass={script.wm_class}""")
        mode = stat(desktop_file).st_mode
        mode |= (mode & 0o444) >> 2  # copy R bits to X
        chmod(desktop_file, mode)  # make it executable


def configure_function() -> int:
    name = "energyplus_regression_runner"
    nice_name = "EnergyPlus Regression Tool"
    s = SingleScript("ep.ico", "ep.png", name, nice_name, "An EnergyPlus test suite utility", name)
    con = InstallConfigure()
    con.add_desktop_icon(s)
    return 0


def configure_cli() -> None:
    exit(configure_function())


if __name__ == '__main__':
    exit(configure_function())
