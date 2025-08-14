"""
main.py

Application entry point for the RWR Tweak Image Editor.

This module initializes the Tkinter main window, creates the AppController (which manages application logic and state),
and instantiates the MainWindow GUI, connecting it to the controller. It then starts the Tkinter event loop.

Usage:
- Run this script directly to launch the image editor GUI.
- The AppController is responsible for all image processing, file operations, and tool management.
- The MainWindow provides the graphical interface and user interaction.

Dependencies:
- tkinter for the GUI
- gui.main_window for the main window class
- app_controller for application logic

This module is not intended to be imported; it should be run as the main script.
"""

import tkinter as tk
from gui.main_window import MainWindow
from app_controller import AppController

if __name__ == "__main__":
    # Create the main application window
    root = tk.Tk()
    
    # Create the controller
    controller_instance = AppController() 
    
    # Create the main window (view) and pass the controller to it
    main_view = MainWindow(root, controller_instance)
    
    # Give the controller a reference to the view
    controller_instance.set_view(main_view)
    
    # Start the Tkinter event loop
    root.mainloop()