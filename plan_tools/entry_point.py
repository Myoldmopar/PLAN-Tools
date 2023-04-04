from os import chmod, path, stat
from pathlib import Path
from platform import system
from site import USER_BASE
from sys import argv
from sysconfig import get_path
from typing import List


class EntryPoint:
    """
    This class represents a single executable that is packaged up by setuptools using the entry_points method.
    The entry points may live in either the console_scripts or the gui_scripts subsections.
    Either way, when the package is pip installed, it results in a binary blob in a bin/ or Scripts/ directory
    """
    def __init__(self, package_source_dir: str, executable_name: str, nice_name: str, description: str, wm_class: str):
        """
        Construct a single script instance, using arguments.

        :param package_source_dir: The name of the source dir containing the package code
        :param executable_name: The name of a resulting executable file (without the exe extension)
        :param nice_name: The "nice" name to use to reference the tool in links and menus
        :param description: The description to show up in Linux .desktop files
        :param wm_class: The wm-class for the Tk GUI (assigned in Tk(className='energyplus_regression_runner'))
        """
        self.this_package_root = Path(__file__).parent.parent / package_source_dir
        self.pretty_link_name = nice_name  # don't include the .lnk extension
        self.description = description
        self.wm_class = wm_class
        self.installed_binary_name = executable_name
        if system() == 'Windows':
            self.installed_binary_name += '.exe'

    def run(self) -> int:
        """
        This function will perform all relevant actions to set up this installed entry point on the system.
        Currently, this simply sets up a desktop icon on Windows or installs a .desktop file on Linux.
        Moving forward, this will create an .app bundle on Mac and create start menu entries on Windows.
        A future addition will also allow options to be set to only do certain actions.

        :return: zero for success, nonzero otherwise
        """
        if system() == 'Windows':
            self._add_desktop_icon_on_windows()
        elif system() == 'Linux':
            self._add_desktop_file_on_linux()
        return 0  # for now

    def uninstall(self) -> int:
        """
        This function is not yet implemented, but will ultimately do the same set-up as the installation, and instead
        try to remove any artifacts that do exist.

        :return: zero for success, nonzero otherwise
        """
        pass

    def _add_desktop_icon_on_windows(self):
        from winreg import OpenKey, QueryValueEx, CloseKey, HKEY_CURRENT_USER as HKCU, KEY_READ as READ
        scripts_dir = Path(get_path('scripts'))
        icon_file = self.this_package_root / 'icons' / 'icon.ico'
        target_exe = scripts_dir / self.installed_binary_name
        link_name = f"{self.pretty_link_name}.lnk"
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

    def _add_desktop_file_on_linux(self):
        # try assuming user install
        user_exe = Path(get_path('scripts')) / self.installed_binary_name
        global_exe = Path(USER_BASE) / 'bin' / self.installed_binary_name
        if user_exe.exists() and global_exe.exists():
            print(f"Detected the {self.installed_binary_name} binary in both user and global locations.")
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
            print(f"Could not find {self.installed_binary_name} binary at either user or global location.")
            print("This is weird since you are running this script...did you actually pip install this tool?")
            print("Make sure to pip install the tool and then retry")
            return 1
        icon_file = self.this_package_root / 'icons' / 'icon.png'
        desktop_file = Path.home() / '.local' / 'share' / 'applications' / f'{self.installed_binary_name}.desktop'
        with open(desktop_file, 'w') as f:
            f.write(f"""[Desktop Entry]
Name={self.pretty_link_name}
Comment={self.description}
Exec={target_exe}
Icon={icon_file}
Type=Application
Terminal=false
StartupWMClass={self.wm_class}""")
        mode = stat(desktop_file).st_mode
        mode |= (mode & 0o444) >> 2  # copy R bits to X
        chmod(desktop_file, mode)  # make it executable


def example_package_usage(_argv: List[str]) -> int:
    """
    This is an example of the code that a packaged application should include to use this functionality.
    This function has an argument for options, so a wrapper function should be created to expose through an entry point.

    :return: zero for success, nonzero otherwise
    """
    # Could handle arguments here
    source_dir = "cool_library"
    exe_name = "name_of_executable"
    nice_name = "Cool Program Name"
    s = EntryPoint(source_dir, exe_name, nice_name, "A really great tool description here", exe_name)
    return s.run()


def example_package_usage_wrapper() -> int:
    """
    THis is an example of the wrapper function which is registered in the setup(entry_points...) section of setup.py.
    This function takes no Python arguments, but passes command line arguments to the worker function.

    :return: zero for success, nonzero otherwise
    """
    # Could handle argv here and pass them to example_package_usage(...)
    return example_package_usage(argv)


if __name__ == '__main__':
    exit(example_package_usage_wrapper())
