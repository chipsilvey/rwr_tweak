# modules/base_module.py
# The interface (Abstract Base Class) for all Application Modules.

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from tkinter import ttk

# Use TYPE_CHECKING to avoid circular import errors with the AppController
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app_controller import AppController

class BaseModuleController(ABC):
    """
    Defines the contract for a self-contained feature module.
    Each module will be discovered and loaded by the AppController at runtime.
    """
    def __init__(self, app_controller: AppController):
        """
        Initializes the module.

        Args:
            app_controller: A reference to the main application controller,
                            used to access shared services (file dialogs, etc.).
        """
        self.app_controller = app_controller

    @property
    @abstractmethod
    def module_name(self) -> str:
        """
        Returns the user-facing name of this module for display in menus.
        """
        pass

    @abstractmethod
    def get_view(self, parent_frame: ttk.Frame) -> ttk.Frame:
        """
        Creates and returns the main GUI Frame for this module.
        This Frame will be displayed in the MainWindow when the module is active.

        Args:
            parent_frame: The parent widget (a Frame in MainWindow) to build the GUI upon.
        
        Returns:
            The fully constructed main view (as a ttk.Frame subclass) for this module.
        """
        pass

    @abstractmethod
    def apply(self):
        """
        Applies the module's effect to the given data.

        This method is designed to be generic.
        """
        pass

    @abstractmethod
    def activate(self):
        """
        Optional: Called by the AppController when this module's view is shown.
        Use this to load data, refresh state, or perform actions needed
        when the user switches to this tool.
        """
        pass

    @abstractmethod
    def deactivate(self):
        """
        Optional: Called by the AppController when this module's view is hidden.
        Use this to save state, release resources, or perform cleanup.
        """
        pass