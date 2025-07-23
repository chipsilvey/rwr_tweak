# Defines the abstract base class for all top-level views.

from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk

class AppView(ttk.Frame,ABC):
    
    """
    Abstract base class for all main views that can be swapped
    in the MainWindow.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

    # @abstractmethod
    # def update_display(self):
    #     """
    #     Update the view with the latest data or changes.
    #     This method should be implemented by subclasses.
    #     """
    #     pass