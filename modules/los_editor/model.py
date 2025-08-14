# RWR_TWEAK/modules/los_editor/model.py
# The data model for the Line of Sight Editor module.
import numpy as np
from modules.module_model import BaseModuleModel

class LOSModel(BaseModuleModel):
    """
    Holds all the data and state for the Line of Sight Editor.
    """
    def __init__(self):
        self.image_path = ""  # Path to the image being edited
        self.backup_path = ""  # Path to the backup image
        self.config_path = ""  # Path to the configuration file
        
        self.original_image_cv: np.ndarray | None = None # OpenCV image object for the original image
        self.processed_image_cv:  np.ndarray | None = None # OpenCV image object for the processed image
        
        self.settings = {}
        
        self.zoom_level = 1.0
        self.display_mode = 'fit' # 'fit', 'actual', or 'custom'

    def is_image_loaded(self):
        return self.original_image_cv is not None

    def clear(self):
        """Resets the model to its initial state."""
        self.__init__()