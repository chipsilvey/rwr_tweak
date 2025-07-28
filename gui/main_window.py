# gui/main_window.py
# Defines the main GUI layout and widgets for the Image Editor.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk # For displaying images
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app_controller import AppController


class MainWindow:
    """
    Defines the main GUI layout and widgets, now with zoom and scroll functionality.
    """
    def __init__(self, root, controller: "AppController"):
        self.root = root
        self.controller = controller
        self.root.title("RWR Tweak")
        self.root.geometry("1024x768") # Increased default size
        # self.root.geometry("800x600") # Set a more manageable default size

        # --- Main Content Frame ---
        # This frame will hold the currently active view
        self.main_content_frame = ttk.Frame(self.root)
        self.main_content_frame.pack(fill=tk.BOTH, expand=True)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # --- View Management ---
        # A dictionary to hold instances of all available views
        self.views = {} 

        self.menubar = None
        self.create_menu()
        
        # The controller will create and register the views
        self.controller.register_views(self)

        # Show a default message or view on startup
        self.show_startup_message()

    def show_startup_message(self):
        """Displays a welcome message before any tool is selected."""
        self.startup_label = ttk.Label(
            self.main_content_frame, 
            text="Welcome! Please select a tool from the 'Tools' menu to begin.",
            font=("Arial", 18),
            justify=tk.CENTER,
            anchor=tk.CENTER
        )
        self.startup_label.pack(fill=tk.BOTH, expand=True)

    def register_view(self, view_name, view_instance):
        """Adds a view instance to the dictionary and places it in the content frame."""
        self.views[view_name] = view_instance
        # Place the view in the grid but hide it initially
        view_instance.grid(row=0, column=0, sticky="nsew", in_=self.main_content_frame)
        view_instance.grid_remove() # Hide it

    def switch_to_view(self, view_name):
        """Hides all other views and shows the requested one."""
        # Hide the startup message if it's visible
        if hasattr(self, 'startup_label') and self.startup_label.winfo_exists():
            self.startup_label.pack_forget()

        for key, view in self.views.items():
            if key == view_name:
                view.grid() # Show the selected view
                # If the view has a 'was_activated' method, call it.
                if hasattr(view, 'activated'):
                    view.activated(True)
            else:
                view.grid_remove() # Hide all other views
        
        # Update the window title to reflect the current tool
        self.root.title(f"Python Image Tools - {view_name}")

    def create_menu(self):
        """Creates the main menu bar for the application."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File Menu (now simpler)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools Menu (New)
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        # The controller will populate this menu