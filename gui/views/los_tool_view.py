# The view for our original Line of Sight (Image Manipulation) tool.

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import path_finder
from .app_view import AppView

import importlib
import pkgutil
import inspect
import tools
from tools.base_tool import BaseTool

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app_controller import AppController
    from gui.main_window import MainWindow

class LineOfSightToolView(AppView):
    """
    The main view for the image manipulation tool.
    This class now contains the canvas, tool panel, and specific menus.
    """
    def __init__(self, parent, main_window: "MainWindow", controller: "AppController"):
        super().__init__(parent, controller)

        self.main_window = main_window

        # --- Main Layout ---
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # --- Left Column (Image Area + Status Bar) --- new
        left_column_frame = ttk.Frame(main_pane)
        main_pane.add(left_column_frame, weight=4) # Give more weight to this column # new end

        # --- Image Display Area ---
        # self.image_display_frame = ttk.Frame(main_pane, relief=tk.SUNKEN, style='TFrame')
        # main_pane.add(self.image_display_frame, weight=4)

        # self.v_scrollbar = ttk.Scrollbar(self.image_display_frame, orient=tk.VERTICAL)
        self.image_display_frame = ttk.Frame(left_column_frame, relief=tk.SUNKEN, style='TFrame') # new
        self.image_display_frame.pack(fill=tk.BOTH, expand=True) # Pack into left_column_frame

        self.v_scrollbar = ttk.Scrollbar(self.image_display_frame, orient=tk.VERTICAL) # type: ignore # new end
        self.h_scrollbar = ttk.Scrollbar(self.image_display_frame, orient=tk.HORIZONTAL)

        self.image_canvas = tk.Canvas(
            self.image_display_frame, 
            bg="gray70", 
            highlightthickness=0,
            xscrollcommand=self.h_scrollbar.set,
            yscrollcommand=self.v_scrollbar.set
        )

        self.v_scrollbar.config(command=self.image_canvas.yview)
        self.h_scrollbar.config(command=self.image_canvas.xview)
        
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')

        self.image_canvas.grid(row=0, column=0, sticky='nsew')

        self.image_display_frame.grid_rowconfigure(0, weight=1)
        self.image_display_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas_image_id = None
        self.rwr_los_path = self.get_rwr_los_path()

        # --- Checkered Background ---
        self.checkered_bg = None
        self._draw_checkered_background()

        self.initial_text_id = self.image_canvas.create_text(
            self.image_canvas.winfo_width()/2, self.image_canvas.winfo_height()/2, 
            text="Load a PNG image to begin", 
            font=("Arial", 16), fill="dim gray", anchor="center", tags="initial_text"
        )

        self.image_canvas.bind("<Configure>", self._on_canvas_resize)

        # --- Status Bar Area --- # new
        self.status_bar_frame = ttk.Frame(left_column_frame, relief=tk.GROOVE)
        self.status_bar_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(2,0), ipady=2)

        self.image_path_var = tk.StringVar(value="Image: N/A")
        image_path_label = ttk.Label(self.status_bar_frame, textvariable=self.image_path_var, anchor='w')
        # image_path_label.pack(side=tk.LEFT, padx=(5,10), fill=tk.X, expand=True)
        image_path_label.pack(side=tk.TOP, padx=(5,5), fill=tk.X, anchor='w')

        self.config_path_var = tk.StringVar(value="Config: N/A")
        config_path_label = ttk.Label(self.status_bar_frame, textvariable=self.config_path_var, anchor='w')
        # config_path_label.pack(side=tk.LEFT, padx=(10,5), fill=tk.X, expand=True)
        config_path_label.pack(side=tk.TOP, padx=(5,5), fill=tk.X, anchor='w', pady=(0,2)) # new end

        # --- Tools Panel ---
        self.tools_frame = ttk.Frame(main_pane, width=280, relief=tk.RAISED)
        main_pane.add(self.tools_frame, weight=1)
        tk.Label(self.tools_frame, text="Image Tools", bg="lightgray", font=("Arial", 12, "bold"), relief=tk.GROOVE).pack(pady=10, fill=tk.X, padx=5)

        # create menu only after activated
        # self.create_menu()

        # --- Load Image Processing Tools ---
        self.tools = self.load_tools(self.tools_frame)

    def activated(self, value: bool):
        """Called by MainWindow when this view is shown."""
        if value:
            self._draw_checkered_background()
            self.create_menu()
            # If an image is already loaded in the controller, display it.
            # This handles switching back to this view after opening an image.
            self.controller.update_view()
        else:
            self.remove_menu()


    def _draw_checkered_background(self, event=None):
        """Draws a checkered background on the canvas."""
        self.image_canvas.delete("checker")
        width, height = self.image_canvas.winfo_width(), self.image_canvas.winfo_height()
        # Create a small tile
        tile_size = 20
        # c1, c2 = "gray80", "gray85"
        c1, c2 = (204, 204, 204), (217, 217, 217)  # Use RGB tuples instead of color names
        tile_pil = Image.new("RGB", (tile_size * 2, tile_size * 2))

        for i in range(2):
            for j in range(2):
                color = c1 if (i + j) % 2 == 0 else c2
                img_rect = Image.new("RGB", (tile_size, tile_size), color)
                tile_pil.paste(img_rect, (i * tile_size, j * tile_size))

        self.checkered_bg = ImageTk.PhotoImage(tile_pil)

        # Tile the background
        for y in range(0, height, self.checkered_bg.height()):
            for x in range(0, width, self.checkered_bg.width()):
                self.image_canvas.create_image(x, y, image=self.checkered_bg, anchor="nw", tags="checker")

        # Ensure background is at the bottom
        self.image_canvas.tag_lower("checker")

    def _on_canvas_resize(self, event):
        """On canvas resize, redraw background and handle image/text positioning."""
        self._draw_checkered_background(event)

        if self.controller.display_mode == 'fit' and self.controller.is_image_loaded():
            self.controller.update_view()
        else:
            # Keep text centered
            if self.canvas_image_id is None and self.initial_text_id:
                self.image_canvas.coords(self.initial_text_id, event.width / 2, event.height / 2)

    def create_menu(self):
        """creates a menu for the Line of Sight tool."""
        if self.parent and hasattr(self.main_window, "menubar") and self.main_window.menubar is not None:
                self.los_menu = tk.Menu(self.main_window.menubar, tearoff=0)
                self.main_window.menubar.add_cascade(label="Line of Sight", menu=self.los_menu)

                self.los_menu.add_command(label="Open Image...", command=lambda: self.controller.open_image_dialog())
                self.los_menu.add_command(label="Open RWR los.png", command=lambda: self.open_rwr_los(), state=tk.NORMAL if self.rwr_los_path else tk.DISABLED)
                self.los_menu.add_command(label="Save", command=lambda: self.controller.save_image(), state=tk.DISABLED)
                self.los_menu.add_command(label="Save As...", command=lambda: self.controller.save_image_as_dialog(), state=tk.DISABLED)
                self.los_menu.add_separator()
                self.los_menu.add_command(label="Reset to Original", command=lambda: self.controller.reset_image(), state=tk.DISABLED)
                self.los_menu.add_separator()
                self.los_menu.add_command(label="Load Tool Settings...", command=lambda: self.controller.load_tool_settings_dialog(), state=tk.DISABLED)
                self.los_menu.add_command(label="Save Tool Settings...", command=lambda: self.controller.save_tool_settings(), state=tk.DISABLED)
                self.los_menu.add_command(label="Save Tool Settings As...", command=lambda: self.controller.save_tool_settings_as_dialog(), state=tk.DISABLED)
      
                self.view_menu = tk.Menu(self.main_window.menubar, tearoff=0)
                self.main_window.menubar.add_cascade(label="View", menu=self.view_menu)

                self.view_menu.add_command(label="Zoom In (+)", command=lambda: self.controller.zoom_in(), state=tk.DISABLED)
                self.view_menu.add_command(label="Zoom Out (-)", command=lambda: self.controller.zoom_out(), state=tk.DISABLED)
                self.view_menu.add_separator()
                self.view_menu.add_command(label="Fit to Window", command=lambda: self.controller.set_display_mode('fit'), state=tk.DISABLED)
                self.view_menu.add_command(label="Actual Size (100%)", command=lambda: self.controller.set_display_mode('actual'), state=tk.DISABLED)

    def update_menu_states(self, image_loaded):
        """Enable or disable menu items based on whether an image is loaded."""
        state = tk.NORMAL if image_loaded else tk.DISABLED
        # LOS Menu
        self.los_menu.entryconfig("Save", state=state)
        self.los_menu.entryconfig("Save As...", state=state)
        self.los_menu.entryconfig("Reset to Original", state=state)
        self.los_menu.entryconfig("Load Tool Settings...", state=state)
        self.los_menu.entryconfig("Save Tool Settings...", state=state)
        self.los_menu.entryconfig("Save Tool Settings As...", state=state)
        # View Menu
        self.view_menu.entryconfig("Zoom In (+)", state=state)
        self.view_menu.entryconfig("Zoom Out (-)", state=state)
        self.view_menu.entryconfig("Fit to Window", state=state)
        self.view_menu.entryconfig("Actual Size (100%)", state=state)

    def remove_menu(self):
        """Removes the LOS and View menus from the menubar."""
        menubar = self.main_window.menubar
        if menubar is not None:
            for label in ["Line of Sight", "View"]:
                try:
                    index = menubar.index(label)
                    if index is not None:
                        menubar.delete(index)
                except Exception:
                    pass  # Menu might not exist

    def update_display(self, pil_image_to_display:Image.Image | None=None):
        """
        Main function to update the canvas. It handles scaling, centering, and scroll region.
        """
        if self.initial_text_id:
            self.image_canvas.delete(self.initial_text_id)
            self.initial_text_id = None
        
        if pil_image_to_display is None:
            self.image_canvas.delete("all")
            self.update_menu_states(image_loaded=False)
            self.update_status_bar(None, None)
            self.load_tool_settings({})
            return
        
        self.image_canvas.delete("image")
        if pil_image_to_display is None: return

        canvas_width, canvas_height = self.image_canvas.winfo_width(), self.image_canvas.winfo_height()

        # --- Image Scaling Logic ---
        img_w, img_h = pil_image_to_display.size
        
        if self.controller.display_mode == 'fit':
            # Calculate scale factor to fit image in canvas
            scale_w = canvas_width / img_w
            scale_h = canvas_height / img_h
            scale = min(scale_w, scale_h)
            # if scale >= 1.0: # Don't scale up past 100% in fit mode
            #     scale = 1.0
            self.controller.zoom_level = scale # Update controller's zoom level
        else: # 'actual' or other zoom modes
            scale = self.controller.zoom_level

        # New dimensions for display
        new_w, new_h = int(img_w * scale), int(img_h * scale)

        if new_w <= 0 or new_h <= 0: return

        # Use Pillow to resize the image for display. This does NOT affect the saved data.
        # Image.Resampling.LANCZOS is high quality, use NEAREST for pixel art if needed.
        display_img = pil_image_to_display.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # --- Composite with checkered background ---
        # Create a checkered background PIL image of the same size
        tile_size = 20
        c1, c2 = (204, 204, 204), (217, 217, 217)
        bg = Image.new("RGBA", (new_w, new_h))
        for y in range(0, new_h, tile_size):
            for x in range(0, new_w, tile_size):
                color = c1 if ((x // tile_size + y // tile_size) % 2 == 0) else c2
                Image.Image.paste(bg, Image.new("RGBA", (tile_size, tile_size), color + (255,)), (x, y))
        # Ensure display_img is RGBA
        if display_img.mode != "RGBA":
            display_img = display_img.convert("RGBA")
        # Composite image over checkered background
        composited_img = Image.alpha_composite(bg, display_img)

        # Convert to Tkinter-compatible format
        self.tk_image = ImageTk.PhotoImage(display_img)

        # --- Canvas Update Logic ---
        self.image_canvas.delete("all") # Clear previous image

        # Position the image on the canvas
        self.canvas_image_id = self.image_canvas.create_image(0, 0, anchor='nw', image=self.tk_image, tags="image")

        # Configure the scroll region to match the scaled image size
        self.image_canvas.config(scrollregion=(0, 0, new_w, new_h))

        self.update_menu_states(image_loaded=True)
        self.update_status_bar(self.controller.image_path, self.controller.config_path)
        self.load_tool_settings(self.controller.settings)

    def load_tool_settings(self, settings):
        for tool_name, tool_instance in self.tools.items():
            tool_instance.set_settings(settings.get(tool_name, {}))

    def update_status_bar(self, image_path: str | None, config_path: str | None): # new
        """Updates the labels in the status bar."""
        img_text = f"Image: {image_path}" if image_path else "Image: N/A"
        cfg_text = f"Config: {config_path}" if config_path else "Config: N/A"
        self.image_path_var.set(img_text)
        self.config_path_var.set(cfg_text)

    def get_rwr_los_path(self):
        """
        Opens a file dialog to select the RWR LOS file.
        """
        rwr_path = self.controller.app_controller.rwr_root
        # rwr_path = path_finder.find_game_install_path()
        # if not rwr_path:
        #     messagebox.showerror("Error", "RWR installation path not found.")
        #     return None
        
        rwr_los_suffix = "media/packages/vanilla/textures/los.png"
        rwr_los_path = os.path.join(rwr_path, rwr_los_suffix)
        if not os.path.exists(rwr_los_path):
            messagebox.showerror("Error", f"RWR LOS file not found at {rwr_los_path}.")
            return None
        
        return rwr_los_path
    
    def open_rwr_los(self):
        """
        Opens the RWR LOS file in the image display area.
        """
        if not self.rwr_los_path:
            messagebox.showerror("Error", "RWR LOS path is not set.")
            return
        
        try:
            self.controller.open_image(self.rwr_los_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open RWR LOS file: {e}")

    def load_tools(self, parent_frame):
        """
        Dynamically discovers and loads all tool plugins from the 'tools' directory.
        """
        self.available_tools = {}
        # Discover modules in the 'tools' package
        discovered_plugins = {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in pkgutil.iter_modules(tools.__path__, tools.__name__ + ".")
        }

        for name, module in discovered_plugins.items():
            # Find classes within the module
            for i in inspect.getmembers(module, inspect.isclass):
                class_obj = i[1]
                # Check if it's a subclass of BaseTool and not BaseTool itself
                if issubclass(class_obj, BaseTool) and class_obj is not BaseTool:
                    # The key for the tool will be the module name minus "_tool"
                    tool_key = module.__name__.split('.')[-1].replace("_tool", "")
                    # Instantiate the tool
                    tool_instance = class_obj()
                    self.available_tools[tool_key] = tool_instance
                    print(f"Dynamically loaded tool: '{tool_key}'")
        
        # Now create the GUI for the discovered tools
        # A more advanced version might sort tools by a 'priority' attribute
        for tool_name, tool_instance in self.available_tools.items():
            tool_instance.create_gui(parent_frame, self)
        
        return self.available_tools