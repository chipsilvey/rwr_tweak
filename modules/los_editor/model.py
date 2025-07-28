# RWR_TWEAK/modules/los_editor/model.py
# The data model for the Line of Sight Editor module.

from modules.module_model import BaseModuleModel

class LOSModel(BaseModuleModel):
    """
    Holds all the data and state for the Line of Sight Editor.
    """
    def __init__(self):
        self.image_path = None
        self.backup_path = None
        self.config_path = None
        
        self.original_image_cv = None
        self.processed_image_cv = None
        
        self.settings = {}
        
        self.zoom_level = 1.0
        self.display_mode = 'fit' # 'fit', 'actual', or 'custom'

    def is_image_loaded(self):
        return self.original_image_cv is not None

    def clear(self):
        """Resets the model to its initial state."""
        self.__init__()