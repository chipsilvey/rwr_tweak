# main.py
# Application entry point for the Image Editor

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