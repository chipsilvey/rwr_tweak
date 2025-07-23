# The abstract base class defines views for the GUI.

from abc import ABC, abstractmethod

class AppView(ABC):
    pass

    @abstractmethod
    def update_view(self):
        """
        Update the view with the latest data or changes.
        This method should be implemented by subclasses.
        """
        pass