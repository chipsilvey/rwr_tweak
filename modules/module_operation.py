# modules/los_editor/operations/base_operation.py
# The interface (Abstract Base Class) for all image operations.

from __future__ import annotations
from abc import ABC, abstractmethod
from tkinter import ttk
from typing import Any, Dict

from modules.module_controller import BaseModuleController

class BaseModuleOperation(ABC):
    """
    Defines the contract for an operation that can be performed on images.
    Each operation will be discovered and loaded by the AppController at runtime.
    """
    
    def __init__(self, controller: BaseModuleController):
        """
        Initializes the operation.

        Args:
            controller: A reference to the module controller,
                        used to access shared services (file dialogs, etc.).
        """
        self.controller = controller

    @property
    @abstractmethod
    def operation_name(self) -> str:
        """
        Returns the user-facing name of this operation for display in menus.
        """
        pass

    @abstractmethod
    def get_view(self, parent_frame: ttk.Frame) -> ttk.Frame:
        """
        Creates and returns the main GUI Frame for this operation.
        
        Args:
            parent_frame: The parent widget (a Frame in MainWindow) to build the GUI upon.
        
        Returns:
            The fully constructed main view (as a ttk.Frame subclass) for this operation.
        """
        pass

    @abstractmethod
    def get_settings(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def set_settings(self, settings: Dict[str, Any]):
        pass

    @abstractmethod
    def apply(self, data: Any, **kwargs) -> Any:
        """
        Applies the operation's effect to the given data.

        This method is designed to be generic. The module's controller is
        responsible for passing the correct data type (e.g., a NumPy array
        for image data, an ElementTree object for XML, etc.).

        Args:
            data: The input data to be processed.
            **kwargs: Optional additional arguments if needed by the operation.

        Returns:
            The processed data.
        """
        pass