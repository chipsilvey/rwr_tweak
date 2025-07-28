# Defines the abstract base class for all top-level views.

from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk

from modules.module_controller import BaseModuleController

class BaseModuleView(ttk.Frame,ABC):
    
    """
    Abstract base class for all main views that can be swapped
    in the MainWindow.
    """
    def __init__(self, parent, controller: BaseModuleController):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller