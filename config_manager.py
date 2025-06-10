# config_manager.py
# Handles reading and writing of YAML configuration files.

import yaml
import os

class ConfigManager:
    """
    Manages loading and saving of image modification settings to a YAML file.
    """
    def load(self, path):
        """
        Loads settings from a YAML file.
        If the file doesn't exist, returns an empty dictionary.
        """
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    settings = yaml.safe_load(f)
                    # If file is empty or corrupt, safe_load might return None
                    return settings if settings is not None else {}
            except yaml.YAMLError as e:
                print(f"Error loading YAML file '{path}': {e}")
                return {} # Return empty dict on error
        return {} # Return empty dict if file doesn't exist

    def save(self, path, settings):
        """
        Saves the given settings dictionary to a YAML file.
        """
        try:
            with open(path, 'w') as f:
                yaml.dump(settings, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"Error saving YAML file '{path}': {e}")