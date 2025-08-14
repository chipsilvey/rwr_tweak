"""
config_manager.py

This module provides the ConfigManager class for handling the loading and saving of image editing tool settings
in YAML format. It abstracts reading and writing configuration files that store the state and parameters of
various image processing tools used in the application.

Usage:
- The AppController uses ConfigManager to persist and restore tool settings associated with each image.
- Settings are stored as dictionaries and serialized to YAML files, typically named after the image file with a .yaml extension.
- If a YAML file does not exist or is invalid, ConfigManager returns an empty dictionary to ensure robust operation.

Dependencies:
- PyYAML for YAML parsing and serialization.
- Standard Python modules: os.

Intended for use as a utility within the application's controller to manage user and tool configuration data.
"""

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