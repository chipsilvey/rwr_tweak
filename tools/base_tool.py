# The abstract base class defines the contract for all tools.

from abc import ABC, abstractmethod
import numpy as np
from typing import Any

class BaseTool(ABC):
    @abstractmethod
    def create_gui(self, parent_frame, controller):
        """Creates the Tkinter widgets for this tool."""
        pass

    @abstractmethod
    def get_settings(self) -> Any:
        """Returns the current settings from the GUI widgets."""
        pass
    
    @abstractmethod
    def set_settings(self, settings):
        """Applies loaded settings to the GUI widgets."""
        pass

    @abstractmethod
    def apply(self, image_data: np.ndarray) -> np.ndarray:
        """
        Applies the tool's effect to the given image.
        
        :param image: The OpenCV image to process.
        :return: The processed image.
        """
        pass