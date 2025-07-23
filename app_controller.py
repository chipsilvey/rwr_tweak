# Handle file operations (open, save, backup, reset).
# Load and apply settings from config_manager.
# Tell image_processor to perform manipulations.
# Update the main_window with the new image.

# app_controller.py
# Handles application logic, state, and communication.

import shutil
import os
import cv2
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

import importlib
import pkgutil
import inspect

from numpy import save

from image_processor import ImageProcessor
from config_manager import ConfigManager

# Import the new view classes
from gui.views.los_tool_view import LineOfSightToolView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gui.main_window import MainWindow
    # from tools.base_tool import BaseTool


class AppController:
    def __init__(self):
        self.view = None
        self.image_path = None
        self.backup_path = None
        self.config_path = None

        self.original_image_cv = None
        self.processed_image_cv = None
        
        self.processor = ImageProcessor() 
        self.config_manager = ConfigManager()

        self.active_view = None
        self.settings = {}
        
        self.zoom_level = 1.0
        self.display_mode = 'fit' # 'fit' or 'actual'
        self.available_tools = {}

    def set_view(self, view: "MainWindow"):
        self.view = view
        # if self.view: # Update status bar with current (likely None) paths # new
        #     self.view.update_status_bar(self.image_path, self.config_path) # new

    def register_views(self, main_window):
        """Creates instances of all views and registers them with the MainWindow."""
        # Instantiate the Line of Sight tool view
        los_view = LineOfSightToolView(main_window.main_content_frame, self)
        main_window.register_view("Line of Sight Tool", los_view)

        # --- Add other top-level tools here in the future ---
        # some_other_view = SomeOtherView(main_window.main_content_frame, self)
        # main_window.register_view("Some Other Tool", some_other_view)

        # Populate the "Tools" menu in the MainWindow
        tools_menu = main_window.menubar.winfo_children()[1] # Assumes "Tools" is the 2nd menu
        for view_name in main_window.views.keys():
            tools_menu.add_command(
                label=view_name,
                command=lambda v=view_name: self.switch_view(v)
            )
        
        # Add the image-specific commands to the tools menu as well
        tools_menu.add_separator()
        tools_menu.add_command(label="Open Image for LoS Tool...", command=self.open_image_dialog)

    def switch_view(self, view_name):
        """Tells the main window to display a specific view."""
        if self.view:
            self.view.switch_to_view(view_name)

    def _convert_cv_to_pil(self, cv_image):
        if cv_image is None: return None
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGRA2RGBA)
        return Image.fromarray(rgb_image)

    def open_image_dialog(self):
        file_path = filedialog.askopenfilename(
            title="Open PNG Image", filetypes=(("PNG files", "*.png"), ("All files", "*.*"))
        )
        if file_path:
            self.open_image(file_path)

    def open_image(self, file_path):
        try:
            self.image_path = file_path
            self._backup_original()
            self.original_image_cv = self.processor.load(file_path)
            self.config_path = f"{self.image_path}.yaml"
            # self.settings = self.config_manager.load(self.config_path)
            
            # Reset view state for new image
            self.display_mode = 'fit'
            self.zoom_level = 1.0
            
            self.switch_view("Line of Sight Tool")
            

        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Error", str(e))
            self._clear_image_context()
        except Exception as e:
            messagebox.showerror("Error Opening Image", f"An unexpected error occurred: {e}")
            self._clear_image_context()

    def update_gui(self):
        """
        Updates the GUI with the current image and settings.
        This is called after any change to the image or settings.
        """
        self._apply_all_tool_effects() # Process the image
        self.update_view()           # Display the result

    def _apply_all_tool_effects(self):
        """
        The new processing pipeline. It chains the tools together.
        """
        if self.original_image_cv is None:
            self.processed_image_cv = None
            return

        # Start with a fresh copy of the original image
        current_image = self.original_image_cv.copy()
        
        # Sequentially apply each tool's effect
        for tool_name, tool_instance in self.available_tools.items():
            if tool_name in self.settings:
                current_image = tool_instance.apply(current_image)
        
        self.processed_image_cv = current_image

    def update_view(self):
        """Updates the active view with the currently processed image data."""
        if self.view:
            # Find the active view (the one that is not hidden)
            active_view = self.view.views.get("Line of Sight Tool") # Assume LoS for now
            if active_view and active_view.winfo_ismapped():
                self.active_view = active_view
                if self.processed_image_cv is not None:
                    pil_image = self._convert_cv_to_pil(self.processed_image_cv)
                    active_view.update_display(pil_image)
                else:
                    active_view.update_display(None)

    def apply_changes(self, tool_name, tool_settings):
        if not self.is_image_loaded(): return
        self.settings[tool_name] = tool_settings
        self._apply_all_tool_effects()
        self.update_view()
    
    def save_image(self, save_path=None):
        if not self.is_image_loaded():
            messagebox.showwarning("Save Error", "No image to save.")
            return

        if save_path is None: save_path = self.image_path
        
        try:
            self.processor.save(save_path, self.processed_image_cv) # Save the final processed data
            self.config_manager.save(f"{save_path}.yaml", self.settings)
            if save_path != self.image_path: self.open_image(save_path)
            messagebox.showinfo("Success", f"Image and settings saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save: {e}")

    def load_tool_settings_dialog(self):
        iniFile = self.config_path or ((self.image_path + ".yaml") if self.image_path else "settings.yaml")
        iniDirectory = None
        if os.path.isabs(iniFile):
            iniDirectory = os.path.dirname(iniFile)
        file_path = filedialog.askopenfilename(
            title="Open YAML Settings File",
            initialfile=iniFile,
            initialdir=iniDirectory,
            defaultextension=".yaml",
            filetypes=(("YAML files", "*.yaml"), ("All files", "*.*"))
        )
        if file_path:
            # self.config_path = file_path
            self.settings = self.config_manager.load(file_path)
            self.update_gui()  # Update the view with the loaded settings

    def save_tool_settings(self, save_path=None):
        if not self.is_image_loaded():
            messagebox.showwarning("Save Settings Error", "No image loaded to save settings.")
            return
        
        try:
            if save_path is None: save_path = self.config_path
            self.config_manager.save(save_path, self.settings)
            messagebox.showinfo("Settings Saved", f"Settings saved to:\n{self.config_path}")
        except Exception as e:
            messagebox.showerror("Save Settings Error", f"Could not save settings: {e}")

    def save_tool_settings_as_dialog(self):
        if self.is_image_loaded():
            iniFile = self.config_path or ((self.image_path + ".yaml") if self.image_path else "settings.yaml")
            iniDirectory = None
            if os.path.isabs(iniFile):
                iniDirectory = os.path.dirname(iniFile)
            save_path = filedialog.asksaveasfilename(
                title="Save Tool Settings As",
                defaultextension=".yaml",
                initialfile=(self.get_current_image_filename()+".yaml"),
                initialdir=iniDirectory,
                filetypes=(("YAML files", "*.yaml"),)
            )
            if save_path: self.save_tool_settings(save_path)

    def save_image_as_dialog(self):
        if self.is_image_loaded():
            save_path = filedialog.asksaveasfilename(
                title="Save Image As", defaultextension=".png",
                initialfile=self.get_current_image_filename(),
                filetypes=(("PNG files", "*.png"),)
            )
            if save_path: self.save_image(save_path)

    def reset_image(self):
        if not self.backup_path or not os.path.exists(self.backup_path):
            messagebox.showwarning("Reset Error", "No backup available.")
            return
        
        assert isinstance(self.backup_path, str) and isinstance(self.image_path, str)

        try:
            shutil.copy2(self.backup_path, self.image_path)
            self.open_image(self.image_path)
            messagebox.showinfo("Image Reset", "Image has been reset.")
        except Exception as e:
            messagebox.showerror("Reset Error", f"Could not reset: {e}")

    # --- View Control Methods ---
    def set_display_mode(self, mode):
        """Sets the display mode ('fit' or 'actual') and updates the view."""
        if not self.is_image_loaded(): return
        self.display_mode = mode
        if mode == 'actual':
            self.zoom_level = 1.0
        self.update_view()
        
    def zoom_in(self):
        """Increases zoom level and updates the view."""
        if not self.is_image_loaded(): return
        self.display_mode = 'custom' # Switch from 'fit' mode if active
        self.zoom_level *= 1.25
        self.update_view()

    def zoom_out(self):
        """Decreases zoom level and updates the view."""
        if not self.is_image_loaded(): return
        self.display_mode = 'custom'
        self.zoom_level /= 1.25
        self.update_view()

    def is_image_loaded(self):
        return self.original_image_cv is not None

    def get_current_image_filename(self):
        return os.path.basename(self.image_path) if self.image_path else "untitled.png"
    
    def _backup_original(self):
        if self.image_path and os.path.exists(self.image_path):
            self.backup_path = f"{self.image_path}.bak"
            if not os.path.exists(self.backup_path):
                try: shutil.copy2(self.image_path, self.backup_path)
                except Exception as e: messagebox.showerror("Backup Error", f"Could not create backup: {e}")
    
    def _clear_image_context(self):
        self.image_path = self.backup_path = self.config_path = None
        self.original_image_cv = self.processed_image_cv = None
        self.settings = {}
        if self.active_view:
            self.active_view.update_display(None)
    
    # def load_tools(self, parent_frame):
    #     """
    #     Dynamically discovers and loads all tool plugins from the 'tools' directory.
    #     """
    #     self.available_tools = {}
    #     # Discover modules in the 'tools' package
    #     discovered_plugins = {
    #         name: importlib.import_module(name)
    #         for finder, name, ispkg
    #         in pkgutil.iter_modules(tools.__path__, tools.__name__ + ".")
    #     }

    #     for name, module in discovered_plugins.items():
    #         # Find classes within the module
    #         for i in inspect.getmembers(module, inspect.isclass):
    #             class_obj = i[1]
    #             # Check if it's a subclass of BaseTool and not BaseTool itself
    #             if issubclass(class_obj, BaseTool) and class_obj is not BaseTool:
    #                 # The key for the tool will be the module name minus "_tool"
    #                 tool_key = module.__name__.split('.')[-1].replace("_tool", "")
    #                 # Instantiate the tool
    #                 tool_instance = class_obj()
    #                 self.available_tools[tool_key] = tool_instance
    #                 print(f"Dynamically loaded tool: '{tool_key}'")
        
    #     # Now create the GUI for the discovered tools
    #     # A more advanced version might sort tools by a 'priority' attribute
    #     for tool_name, tool_instance in self.available_tools.items():
    #         tool_instance.create_gui(parent_frame, self)
        
    #     return self.available_tools