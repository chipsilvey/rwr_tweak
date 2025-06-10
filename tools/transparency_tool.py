# tools/transparency_tool.py
import tkinter as tk
from tkinter import ttk
import numpy as np

from .base_tool import BaseTool

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app_controller import AppController

class TransparencyTool(BaseTool):
    def create_gui(self, parent_frame, controller:"AppController"):
        self.controller = controller
        
        # Use a LabelFrame to group the tool's widgets
        tool_frame = ttk.LabelFrame(parent_frame, text="Traransparency", padding=(10, 5))
        tool_frame.pack(pady=5, padx=10, fill=tk.X)

        self.enabled_var = tk.BooleanVar(value=False)
        self.opacity_var = tk.DoubleVar(value=0.0)
        self.falloff_var = tk.DoubleVar(value=1.0)
        self.alpha_offset_var = tk.DoubleVar(value=0.0)

        self.enabled_checkbox = ttk.Checkbutton(
            tool_frame,
            text="Enable",
            variable=self.enabled_var,
            onvalue=True,
            offvalue=False,
            command=self._on_change
        )
        self.enabled_checkbox.pack(anchor=tk.W, padx=5, pady=(5, 0))

        ttk.Label(tool_frame, text="Opacity").pack(pady=(5,0))
        self.opacity_slider = ttk.Scale(
            tool_frame, 
            from_=-100, 
            to=100, 
            orient=tk.HORIZONTAL,
            variable=self.opacity_var,
            command=self._on_change
        )
        self.opacity_slider.pack(fill=tk.X, expand=True)

        self.opacity_label = ttk.Label(tool_frame, text="0")
        self.opacity_label.pack()

        ttk.Label(tool_frame, text="Falloff").pack(pady=(5,0))
        self.falloff_slider = ttk.Scale(
            tool_frame, 
            from_=.01, 
            to=2.0, 
            orient=tk.HORIZONTAL,
            variable=self.falloff_var,
            command=lambda v: self._on_change()
        )
        self.falloff_slider.pack(fill=tk.X, expand=True)

        self.falloff_label = ttk.Label(tool_frame, text="0")
        self.falloff_label.pack()

        ttk.Label(tool_frame, text="Alpha Offset").pack(pady=(5,0))
        self.alpha_offset_var = tk.DoubleVar(value=0.0)
        self.alpha_offset_slider = ttk.Scale(
            tool_frame,
            from_=0.0,
            to=255.0,
            orient=tk.HORIZONTAL,
            variable=self.alpha_offset_var,
            command=lambda v: self._on_change()
        )
        self.alpha_offset_slider.pack(fill=tk.X, expand=True)
        self.alpha_offset_label = ttk.Label(tool_frame, text="0")
        self.alpha_offset_label.pack()

    def _on_change(self, _=None):
        
        self.opacity_label.config(text=f"{self.opacity_var.get():.1f}%")
        self.falloff_label.config(text=f"{self.falloff_var.get():.2f}")
        self.alpha_offset_label.config(text=f"{self.alpha_offset_var.get():.0f}")
        # Notify the controller of the change
        self.controller.apply_changes('transparency', self.get_settings())

    def get_settings(self):
        """Returns the current alpha value from the slider."""
        return {
            'enabled': self.enabled_var.get(),
            'alpha': self.opacity_var.get(),
            'falloff': self.falloff_var.get(),
            'alpha_offset': self.alpha_offset_var.get()
        }

    def set_settings(self, settings):
        """Sets the slider's value from a loaded settings dictionary."""
        self.enabled_var.set(settings.get('enabled', False))
        self.opacity_var.set(settings.get('alpha', 0.0))
        self.falloff_var.set(settings.get('falloff', 1.0))
        self.alpha_offset_var.set(settings.get('alpha_offset', 0.0))
        self._on_change()  # Update labels and notify controller

    def apply(self, image_data: np.ndarray) -> np.ndarray:
        """
        Applies the transparency effect to the given image.
        
        :param image: The OpenCV image to process.
        :return: The processed image with transparency applied.
        """
        if not self.enabled_var.get():
            return image_data

        if image_data is None or image_data.shape[2] < 4:
            print("Warning: Attempted to apply transparency to an image without an alpha channel.")
            return image_data
        
        settings = self.get_settings()

        alpha_adjust = settings.get('alpha', 0)  # Range: -100 to 100
        falloff = settings.get('falloff', 1.0)   # Higher = more contrast on fade-in
        alpha_offset = settings.get('alpha_offset', 0.0)  # Range: 0 to 255


        # Get alpha channel
        alpha = image_data[:, :, 3].astype(np.float32)

        # if alpha_adjust == 0:
        #     return  image_data# No change

        if alpha_adjust < 0:
            # Fade out all pixels (alpha *= scale from 1 to 0)
            scale = 1.0 + (alpha_adjust / 100.0)  # e.g., -50 → 0.5
            alpha *= scale
        else:
            # Fade in partially transparent pixels (non-zero alpha)
            scale = alpha_adjust / 100.0          # 0 to 1
            normalized = alpha / 255.0            # 0 to 1
            boosted = normalized + (1.0 - normalized) * (scale * (normalized ** falloff))
            alpha = boosted * 255.0

        # Apply alpha offset, but don't exceed 255
        if alpha_offset > 0:
            max_alpha = np.max(alpha)
            if max_alpha + alpha_offset > 255:
                # Scale offset so the max alpha becomes 255
                alpha_offset = 255 - max_alpha
            alpha = np.where( alpha > 0, alpha + alpha_offset, alpha)  # Only apply offset to non-zero alpha
            # alpha += alpha_offset

        # Clip and apply
        alpha = np.clip(alpha, 0, 255).astype(np.uint8)

        modified_image_data = image_data.copy()
        modified_image_data[:, :, 3] = alpha

        return modified_image_data