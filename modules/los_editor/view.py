# RWR_TWEAK/modules/los_editor/view.py
# The GUI Frame for the Line of Sight Editor module.

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2

from module_view import BaseModuleView
from module_controller import BaseModuleController
from modules.los_editor.controller import LOSController


class LOSView(BaseModuleView):

    def __init__(self, parent, controller: BaseModuleController):
        super().__init__(parent, controller)

        if isinstance(controller, LOSController):
            self.controller = controller
        else:
            raise TypeError("Controller must be an instance of LOSController")
        
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        self.image_display_frame = ttk.Frame(main_pane, relief=tk.SUNKEN)
        main_pane.add(self.image_display_frame, weight=4)

        self.v_scrollbar = ttk.Scrollbar(self.image_display_frame, orient=tk.VERTICAL)
        self.h_scrollbar = ttk.Scrollbar(self.image_display_frame, orient=tk.HORIZONTAL)
        self.image_canvas = tk.Canvas(
            self.image_display_frame, bg="gray70", highlightthickness=0,
            xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set
        )
        self.v_scrollbar.config(command=self.image_canvas.yview)
        self.h_scrollbar.config(command=self.image_canvas.xview)
        
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        self.image_canvas.grid(row=0, column=0, sticky='nsew')
        self.image_display_frame.grid_rowconfigure(0, weight=1)
        self.image_display_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas_image_id = None
        self.checkered_bg = None
        self.image_canvas.bind("<Configure>", self._on_canvas_resize)

        self.tools_frame = ttk.Frame(main_pane, width=280, relief=tk.RAISED)
        main_pane.add(self.tools_frame, weight=1)
        
        self._create_tool_panel_header()

    def _create_tool_panel_header(self):
        header_frame = ttk.Frame(self.tools_frame)
        header_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Button(header_frame, text="Open Image...", command=self.controller.open_image).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,2))
        ttk.Button(header_frame, text="Save", command=self.controller.save_image).pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        ttk.Separator(self.tools_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5, padx=5)

    def _on_canvas_resize(self, event):
        self._draw_checkered_background()
        if self.controller.get_display_mode() == 'fit':
            self.controller.update_view()

    def _draw_checkered_background(self):
        self.image_canvas.delete("checker")
        width, height = self.image_canvas.winfo_width(), self.image_canvas.winfo_height()
        if width == 1 or height == 1: return # Not ready yet
        tile_size = 20
        c1, c2 = "gray80", "gray85"
        tile_pil = Image.new("RGB", (tile_size * 2, tile_size * 2))
        for i in range(2):
            for j in range(2):
                color = c1 if (i + j) % 2 == 0 else c2
                img_rect = Image.new("RGB", (tile_size, tile_size), color)
                tile_pil.paste(img_rect, (i * tile_size, j * tile_size))
        self.checkered_bg = ImageTk.PhotoImage(tile_pil)
        for y in range(0, height, self.checkered_bg.height()):
            for x in range(0, width, self.checkered_bg.width()):
                self.image_canvas.create_image(x, y, image=self.checkered_bg, anchor="nw", tags="checker")
        self.image_canvas.tag_lower("checker")

    def update_display(self, cv_image_to_display=None):
        self.image_canvas.delete("image")
        if cv_image_to_display is None: return

        # Convert CV2 image to PIL for display
        rgb_image = cv2.cvtColor(cv_image_to_display, cv2.COLOR_BGRA2RGBA)
        pil_image = Image.fromarray(rgb_image)

        canvas_width, canvas_height = self.image_canvas.winfo_width(), self.image_canvas.winfo_height()
        img_w, img_h = pil_image.size
        
        if self.controller.get_display_mode() == 'fit':
            if img_w == 0 or img_h == 0: return
            scale = min(canvas_width / img_w, canvas_height / img_h)
            if scale >= 1.0: scale = 1.0
            self.controller.set_zoom_level(scale)
        else:
            scale = self.controller.get_zoom_level()

        new_w, new_h = int(img_w * scale), int(img_h * scale)
        if new_w <= 0 or new_h <= 0: return

        display_img = pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(display_img)
        self.canvas_image_id = self.image_canvas.create_image(0, 0, anchor='nw', image=self.tk_image, tags="image")
        self.image_canvas.config(scrollregion=(0, 0, new_w, new_h))

    def load_tool_settings(self, settings):
        for op_name, op_instance in self.controller.operations.items():
            op_instance.set_settings(settings.get(op_name, {}))