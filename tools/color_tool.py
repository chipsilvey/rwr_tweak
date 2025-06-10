# tools/color_tool.py

from email.mime import image
import re
import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from .base_tool import BaseTool
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app_controller import AppController

class ColorTool(BaseTool):
    """
    A tool for adjusting Hue, Saturation, and Value (Brightness).
    """
    def create_gui(self, parent_frame, controller: "AppController"):
        self.controller = controller
        
        tool_frame = ttk.LabelFrame(parent_frame, text="Color (HSV)", padding=(10, 5))
        tool_frame.pack(pady=5, padx=10, fill=tk.X)

        self.enabled_var = tk.BooleanVar(value=False)

        # --- Create variables to hold slider values ---
        self.hue_var = tk.IntVar(value=0)
        self.sat_var = tk.DoubleVar(value=100.0)
        self.val_var = tk.DoubleVar(value=100.0)
        
        self.enabled_checkbox = ttk.Checkbutton(
            tool_frame,
            text="Enable",
            variable=self.enabled_var,
            onvalue=True,
            offvalue=False,
            command=self._on_change
        )
        self.enabled_checkbox.pack(anchor=tk.W, padx=5, pady=(5, 0))

        # --- Hue Slider ---
        ttk.Label(tool_frame, text="Hue Shift").pack()
        self.hue_slider = ttk.Scale(
            tool_frame,
            from_=-90,
            to=90,
            orient=tk.HORIZONTAL,
            variable=self.hue_var,
            command=self._on_change
        )
        self.hue_slider.pack(fill=tk.X, expand=True)
        self.hue_label = ttk.Label(tool_frame, text="0")
        self.hue_label.pack()

        # --- Saturation Slider ---
        ttk.Label(tool_frame, text="Saturation").pack(pady=(5,0))
        self.sat_slider = ttk.Scale(
            tool_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.sat_var,
            command=self._on_change
        )
        self.sat_slider.pack(fill=tk.X, expand=True)
        self.sat_label = ttk.Label(tool_frame, text="100.0%")
        self.sat_label.pack()

        # --- Value (Brightness) Slider ---
        ttk.Label(tool_frame, text="Brightness").pack(pady=(5,0))
        self.val_slider = ttk.Scale(
            tool_frame,
            from_=0,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.val_var,
            command=self._on_change
        )
        self.val_slider.pack(fill=tk.X, expand=True)
        self.val_label = ttk.Label(tool_frame, text="100.0%")
        self.val_label.pack()

    def _on_change(self, _=None):
        # Update labels
        self.hue_label.config(text=f"{self.hue_var.get()}")
        self.sat_label.config(text=f"{self.sat_var.get():.1f}%")
        self.val_label.config(text=f"{self.val_var.get():.1f}%")
        # Notify controller of the change
        self.controller.apply_changes('color', self.get_settings())

    def get_settings(self):
        """Returns the current color values from the sliders."""
        return {
            'enabled': self.enabled_var.get(),
            'hue': self.hue_var.get(),
            'saturation': self.sat_var.get(),
            'value': self.val_var.get()
        }

    def set_settings(self, settings):
        """Sets the sliders' values from a loaded settings dictionary."""
        self.enabled_var.set(settings.get('enabled', False))
        self.hue_var.set(settings.get('hue', 0))
        self.sat_var.set(settings.get('saturation', 100.0))
        self.val_var.set(settings.get('value', 100.0))
        self._on_change()

    def apply(self, image_data: np.ndarray) -> np.ndarray:
        """
        Applies the transparency effect to the given image.
        
        :param image: The OpenCV image to process.
        :return: The processed image with transparency applied.
        """
        if not self.enabled_var.get():
            return image_data
        
        if image_data is None or image_data.shape[2] < 4:
            return image_data
        
        settings = self.get_settings()

        hue = settings.get('hue', 0)            # [-90, 90]
        saturation = settings.get('saturation', 100)  # [0, 200]
        value_scale = settings.get('value', 100) / 100.0  # [0.0, 2.0]

        # Clamp and normalize
        hue = np.clip(hue, -180, 180)
        sat = np.clip(saturation, 0, 200) / 100.0
        sat_fill_value = int(np.clip(sat * 255, 0, 255))

        # Separate alpha channel
        gray_bgr = image_data[:, :, :3]
        alpha = image_data[:, :, 3]

        # Convert BGR to grayscale (this ensures you're working from the luminance)
        gray = cv2.cvtColor(gray_bgr, cv2.COLOR_BGR2GRAY)

        # Construct synthetic HSV image
        h_channel = np.full_like(gray, (hue % 180), dtype=np.uint8)          # H in [0,179]
        s_channel = np.full_like(gray, sat_fill_value, dtype=np.uint8)       # S in [0,255]
        v_channel = np.clip(gray * value_scale, 0, 255).astype(np.uint8)     # V from gray

        hsv = cv2.merge([h_channel, s_channel, v_channel])

        # Convert to BGR
        color_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Merge with original alpha
        b, g, r = cv2.split(color_bgr)
        image_data = cv2.merge([b, g, r, alpha])

        return image_data