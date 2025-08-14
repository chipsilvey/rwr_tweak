"""
path_finder.py

This module provides utility functions for locating the Steam installation directory and the installation path
of a specific Steam game (by app ID) on Windows systems. It reads Windows registry keys to find the main Steam
directory, parses Steam's libraryfolders.vdf to enumerate all Steam library locations, and inspects appmanifest
files to determine the install directory of a given game.

Usage:
- Used by the GUI (main_window.py) to automatically locate the "Running With Rifles" (RWR) installation and its
  los.png file, enabling quick access for image editing.
- Can be reused for any Steam game by specifying a different app_id.

Functions:
- find_steam_install_path(): Returns the path to the Steam installation directory, or None if not found.
- find_game_install_path(app_id): Returns the install path for the specified Steam app ID, or None if not found.

Dependencies:
- winreg (Windows only), os, re

Intended for use as a backend utility to support game file discovery in the application's GUI.
"""

import winreg
import os

def find_steam_install_path():
    """
    Finds the Steam installation path on Windows.
    """
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Valve\\Steam")
        steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
        winreg.CloseKey(key)
        return steam_path
    except OSError:
        return None

# rwr_steam_id = 270150
def find_game_install_path(app_id=270150):
    """
    Finds the installation path of a game given its Steam app ID.

    Args:
        app_id (int): The Steam app ID of the game.

    Returns:
        str: The installation path of the game, or None if not found.
    """
    steam_path = find_steam_install_path()
    if not steam_path:
        print("Steam install path not found.")
        return None

    library_folders_vdf = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")

    try:
        with open(library_folders_vdf, "r", encoding="utf-8") as f:
            vdf_content = f.read()

        # Simple parsing of libraryfolders.vdf to find library paths.
        import re
        library_paths = []
        for match in re.finditer(r'"(?:path|installpath)"\s+"(.*?)"', vdf_content):
            library_paths.append(match.group(1).replace("\\\\", "\\")) # replace double backslashes which are escaped in the vdf.

        for library_path in library_paths:
            app_manifest_path = os.path.join(library_path, "steamapps", f"appmanifest_{app_id}.acf")
            if os.path.exists(app_manifest_path):
                # Simple parsing of appmanifest.acf to find install path.
                with open(app_manifest_path, "r", encoding="utf-8") as manifest_file:
                    manifest_content = manifest_file.read()

                install_dir_match = re.search(r'"installdir"\s+"(.*?)"', manifest_content)
                if install_dir_match:
                    return os.path.join(library_path, "steamapps", "common", install_dir_match.group(1))

        return None

    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
