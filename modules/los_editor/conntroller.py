
import os
import importlib, pkgutil, inspect
from tkinter import messagebox
from tkinter import ttk
from modules.module_controller import BaseModuleController
from .model import LOSModel
from .view import LOSView
from modules.module_operation import BaseModuleOperation

# These are now services provided by the shell
from image_processor import ImageProcessor
from config_manager import ConfigManager


class LOSController(BaseModuleController):
    @property
    def module_name(self) -> str:
        return "Line of Sight Editor"

    def __init__(self, app_controller):
        super().__init__(app_controller)
        self.model = LOSModel()
        self.view = None
        self.operations = {}
        
        # Use the generic services
        self.image_processor = ImageProcessor()
        self.config_manager = ConfigManager()

    
    
    def get_view(self, parent_frame: ttk.Frame) -> ttk.Frame:
        """        Creates and returns the main GUI Frame for this module.
        This Frame will be displayed in the MainWindow when the module is active.
        Args:
            parent_frame: The parent widget (a Frame in MainWindow) to build the GUI upon.
        Returns:
            The fully constructed main view (as a ttk.Frame subclass) for this module.
        """
        if self.view is None:
            self.view = LOSView(parent_frame, self)
            self._load_operations()
        return self.view
    
    def _load_operations(self):
        """Dynamically loads all image operations for this module."""
        import modules.los_editor.operations as ops
        
        for _, name, _ in pkgutil.iter_modules(ops.__path__, ops.__name__ + "."):
            module = importlib.import_module(name)
            for _, class_obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(class_obj, BaseModuleOperation) and class_obj is not BaseModuleOperation:
                    op_key = name.split('.')[-1].replace("_op", "")
                    self.operations[op_key] = class_obj()
        
        for op_instance in self.operations.values():
            op_instance.create_gui(self.view.tools_frame, self)
    
    def open_image(self):
        """Uses the app_controller's service to open a file."""
        file_path = self.app_controller.request_file_open(
            title="Open PNG Image", filetypes=(("PNG files", "*.png"),)
        )
        if not file_path:
            return

        try:
            # Reset model for new image
            self.model.clear()
            
            # Use services for file operations
            self.model.image_path = file_path
            self.model.backup_path = self.app_controller.backup_file(file_path)
            
            # Use local processors for data handling
            self.model.original_image_cv = self.image_processor.load(file_path)
            self.model.config_path = f"{file_path}.yaml"
            self.model.settings = self.config_manager.load(self.model.config_path)
            
            self._apply_all_operations()
            self.update_view()
            self.view.load_tool_settings(self.model.settings)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open and process image: {e}")
            self.model.clear()
            self.update_view()

    def _apply_all_operations(self):
        if not self.model.is_image_loaded():
            self.model.processed_image_cv = None
            return
        
        current_image = self.model.original_image_cv.copy()
        for op_name, op_instance in self.operations.items():
            if op_name in self.model.settings:
                current_image = op_instance.apply(current_image)
        
        self.model.processed_image_cv = current_image

    def update_view(self):
        """Pushes the current processed image data to the view for display."""
        if self.view:
            self.view.update_display(self.model.processed_image_cv)

    def operation_update(self, op_name, op_settings):
        """Called by an operation when its GUI changes."""
        if not self.model.is_image_loaded(): return
        self.model.settings[op_name] = op_settings
        self._apply_all_operations()
        self.update_view()

    def save_image(self, save_path=None):
        if not self.model.is_image_loaded(): return
        if save_path is None: save_path = self.model.image_path
        
        self.image_processor.save(save_path, self.model.processed_image_cv)
        self.config_manager.save(f"{save_path}.yaml", self.model.settings)
        
        if save_path != self.model.image_path:
            self.open_image() # Re-trigger the open process for the new file
        else:
            messagebox.showinfo("Success", "Image and settings saved.")

    # --- Passthrough methods for view interaction ---
    def get_display_mode(self): return self.model.display_mode
    def get_zoom_level(self): return self.model.zoom_level
    def set_zoom_level(self, level): self.model.zoom_level = level
    def set_display_mode(self, mode):
        self.model.display_mode = mode
        if mode == 'actual': self.model.zoom_level = 1.0
        self.update_view()

    def apply(self):
        """
        Applies the module's effect to the given data.

        This method is designed to be generic.
        """
        pass

    def activate(self):
        pass

    def deactivate(self):
        pass