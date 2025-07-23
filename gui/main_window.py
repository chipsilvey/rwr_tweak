# gui/main_window.py
# Defines the main GUI layout and widgets for the Image Editor.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk # For displaying images
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app_controller import AppController


class MainWindow:
    """
    Defines the main GUI layout and widgets, now with zoom and scroll functionality.
    """
    def __init__(self, root, controller: "AppController"):
        self.root = root
        self.controller = controller
        self.root.title("RWR Tweak")
        self.root.geometry("1024x768") # Increased default size
        # self.root.geometry("800x600") # Set a more manageable default size

        # --- Main Content Frame ---
        # This frame will hold the currently active view
        self.main_content_frame = ttk.Frame(self.root)
        self.main_content_frame.pack(fill=tk.BOTH, expand=True)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # --- View Management ---
        # A dictionary to hold instances of all available views
        self.views = {} 

        self.menubar = None
        self.create_menu()
        
        # The controller will create and register the views
        self.controller.register_views(self)

        # Show a default message or view on startup
        self.show_startup_message()

    def show_startup_message(self):
        """Displays a welcome message before any tool is selected."""
        self.startup_label = ttk.Label(
            self.main_content_frame, 
            text="Welcome! Please select a tool from the 'Tools' menu to begin.",
            font=("Arial", 18),
            justify=tk.CENTER,
            anchor=tk.CENTER
        )
        self.startup_label.pack(fill=tk.BOTH, expand=True)

    def register_view(self, view_name, view_instance):
        """Adds a view instance to the dictionary and places it in the content frame."""
        self.views[view_name] = view_instance
        # Place the view in the grid but hide it initially
        view_instance.grid(row=0, column=0, sticky="nsew", in_=self.main_content_frame)
        view_instance.grid_remove() # Hide it

    def switch_to_view(self, view_name):
        """Hides all other views and shows the requested one."""
        # Hide the startup message if it's visible
        if hasattr(self, 'startup_label') and self.startup_label.winfo_exists():
            self.startup_label.pack_forget()

        for key, view in self.views.items():
            if key == view_name:
                view.grid() # Show the selected view
                # If the view has a 'was_activated' method, call it.
                if hasattr(view, 'was_activated'):
                    view.was_activated()
            else:
                view.grid_remove() # Hide all other views
        
        # Update the window title to reflect the current tool
        self.root.title(f"Python Image Tools - {view_name}")

    def create_menu(self):
        """Creates the main menu bar for the application."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File Menu (now simpler)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools Menu (New)
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        # The controller will populate this menu

        # --- OLD CODE from __init__---

        # # --- Main Paned Window for resizable sections ---
        # main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        # main_pane.pack(fill=tk.BOTH, expand=True)

        # # --- Left Column (Image Area + Status Bar) --- new
        # left_column_frame = ttk.Frame(main_pane)
        # main_pane.add(left_column_frame, weight=4) # Give more weight to this column # new end

        # # --- Image Display Area with Scrollbars ---
        # # self.image_display_frame = ttk.Frame(main_pane, relief=tk.SUNKEN, style='TFrame')
        # # main_pane.add(self.image_display_frame, weight=4) # Give more weight to image frame

        # # self.v_scrollbar = ttk.Scrollbar(self.image_display_frame, orient=tk.VERTICAL)
        # self.image_display_frame = ttk.Frame(left_column_frame, relief=tk.SUNKEN, style='TFrame') # new
        # self.image_display_frame.pack(fill=tk.BOTH, expand=True) # Pack into left_column_frame

        # self.v_scrollbar = ttk.Scrollbar(self.image_display_frame, orient=tk.VERTICAL) # type: ignore # new end

        # self.h_scrollbar = ttk.Scrollbar(self.image_display_frame, orient=tk.HORIZONTAL)
        # self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        # self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # self.image_canvas = tk.Canvas(
        #     self.image_display_frame, 
        #     bg="gray70", 
        #     highlightthickness=0,
        #     xscrollcommand=self.h_scrollbar.set,
        #     yscrollcommand=self.v_scrollbar.set
        # )
        # self.image_canvas.grid(row=0, column=0, sticky='nsew')
        
        # self.v_scrollbar.config(command=self.image_canvas.yview)
        # self.h_scrollbar.config(command=self.image_canvas.xview)
        
        # self.image_display_frame.grid_rowconfigure(0, weight=1)
        # self.image_display_frame.grid_columnconfigure(0, weight=1)
        
        # self.canvas_image_id = None

        # self.rwr_los_path = self.get_rwr_los_path()

        # # --- Checkered Background ---
        # self.checkered_bg = None
        # self._draw_checkered_background()

        # # self.initial_text_id = self.image_canvas.create_text(
        # #     400, 300, text="Load a PNG image to begin", 
        # #     font=("Arial", 16), fill="dim gray", anchor="center"
        # # )
        # self.initial_text_id = self.image_canvas.create_text(
        #     self.image_canvas.winfo_width()/2, self.image_canvas.winfo_height()/2, 
        #     text="Load a PNG image to begin", 
        #     font=("Arial", 16), fill="dim gray", anchor="center", tags="initial_text"
        # )
        # self.image_canvas.bind("<Configure>", self._on_canvas_resize)

        # # --- Status Bar Area --- # new
        # self.status_bar_frame = ttk.Frame(left_column_frame, relief=tk.GROOVE)
        # self.status_bar_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(2,0), ipady=2)

        # self.image_path_var = tk.StringVar(value="Image: N/A")
        # image_path_label = ttk.Label(self.status_bar_frame, textvariable=self.image_path_var, anchor='w')
        # # image_path_label.pack(side=tk.LEFT, padx=(5,10), fill=tk.X, expand=True)
        # image_path_label.pack(side=tk.TOP, padx=(5,5), fill=tk.X, anchor='w')

        # self.config_path_var = tk.StringVar(value="Config: N/A")
        # config_path_label = ttk.Label(self.status_bar_frame, textvariable=self.config_path_var, anchor='w')
        # # config_path_label.pack(side=tk.LEFT, padx=(10,5), fill=tk.X, expand=True)
        # config_path_label.pack(side=tk.TOP, padx=(5,5), fill=tk.X, anchor='w', pady=(0,2)) # new end

        # # --- Tools Panel ---
        # self.tools_frame = ttk.Frame(main_pane, width=280, relief=tk.RAISED)
        # main_pane.add(self.tools_frame, weight=1)
        # tk.Label(self.tools_frame, text="Tools Panel", bg="lightgray", font=("Arial", 12, "bold"), relief=tk.GROOVE).pack(pady=10, fill=tk.X, padx=5)

        # self.create_menu()
        # self.tools = self.controller.load_tools(self.tools_frame)

    

    # def _draw_checkered_background(self, event=None):
        
    #     self.image_canvas.delete("checker") # Remove old background
        
    #     width = self.image_canvas.winfo_width()
    #     height = self.image_canvas.winfo_height()
        
    #     # Create a small tile
    #     tile_size = 20
    #     # c1, c2 = "gray80", "gray85"
    #     c1, c2 = (204, 204, 204), (217, 217, 217)  # Use RGB tuples instead of color names
    #     tile_pil = Image.new("RGB", (tile_size * 2, tile_size * 2))
        
    #     # Simple drawing of a 2x2 checker pattern
    #     for i in range(2):
    #         for j in range(2):
    #             color = c1 if (i + j) % 2 == 0 else c2
    #             # Create a rectangle of the color
    #             img_rect = Image.new("RGB", (tile_size, tile_size), color)
    #             tile_pil.paste(img_rect, (i * tile_size, j * tile_size))

    #     self.checkered_bg = ImageTk.PhotoImage(tile_pil)

    #     # Tile the background
    #     for y in range(0, height, self.checkered_bg.height()):
    #         for x in range(0, width, self.checkered_bg.width()):
    #             self.image_canvas.create_image(x, y, image=self.checkered_bg, anchor="nw", tags="checker")
        
    #     # Ensure background is at the bottom
    #     self.image_canvas.tag_lower("checker")

    # def _on_canvas_resize(self, event):
    #     """On canvas resize, redraw background and handle image/text positioning."""
    #     self._draw_checkered_background(event)

    #     if self.controller.display_mode == 'fit' and self.controller.is_image_loaded():
    #         self.update_display()
    #     else:
    #         # Keep text centered
    #         if self.canvas_image_id is None and self.initial_text_id:
    #             self.image_canvas.coords(self.initial_text_id, event.width / 2, event.height / 2)

    # def create_menu_old(self):
    #     """Creates the main menu bar for the application."""
    #     self.menubar = tk.Menu(self.root)
    #     self.root.config(menu=self.menubar)

    #     # File Menu
    #     self.file_menu = tk.Menu(self.menubar, tearoff=0)
    #     self.menubar.add_cascade(label="File", menu=self.file_menu)
    #     self.file_menu.add_command(label="Open Image...", command=lambda: self.controller.open_image_dialog())
    #     self.file_menu.add_command(label="Open RWR los.png", command=lambda: self.open_rwr_los(), state=tk.NORMAL if self.rwr_los_path else tk.DISABLED)
    #     self.file_menu.add_command(label="Save", command=lambda: self.controller.save_image(), state=tk.DISABLED)
    #     self.file_menu.add_command(label="Save As...", command=lambda: self.controller.save_image_as_dialog(), state=tk.DISABLED)
    #     self.file_menu.add_separator()
    #     self.file_menu.add_command(label="Reset to Original", command=lambda: self.controller.reset_image(), state=tk.DISABLED)
    #     self.file_menu.add_separator()
    #     self.file_menu.add_command(label="Load Tool Settings...", command=lambda: self.controller.load_tool_settings_dialog(), state=tk.DISABLED)
    #     self.file_menu.add_command(label="Save Tool Settings...", command=lambda: self.controller.save_tool_settings(), state=tk.DISABLED)
    #     self.file_menu.add_command(label="Save Tool Settings As...", command=lambda: self.controller.save_tool_settings_as_dialog(), state=tk.DISABLED)
    #     self.file_menu.add_separator()
    #     self.file_menu.add_command(label="Exit", command=self.root.quit)
        
    #     # View Menu (New)
    #     self.view_menu = tk.Menu(self.menubar, tearoff=0)
    #     self.menubar.add_cascade(label="View", menu=self.view_menu)
    #     self.view_menu.add_command(label="Zoom In (+)", command=lambda: self.controller.zoom_in(), state=tk.DISABLED)
    #     self.view_menu.add_command(label="Zoom Out (-)", command=lambda: self.controller.zoom_out(), state=tk.DISABLED)
    #     self.view_menu.add_separator()
    #     self.view_menu.add_command(label="Fit to Window", command=lambda: self.controller.set_display_mode('fit'), state=tk.DISABLED)
    #     self.view_menu.add_command(label="Actual Size (100%)", command=lambda: self.controller.set_display_mode('actual'), state=tk.DISABLED)

    # def update_display(self, pil_image_to_display:Image.Image | None=None):
    #     """
    #     Main function to update the canvas. It handles scaling, centering, and scroll region.
    #     """
    #     if self.initial_text_id:
    #         self.image_canvas.delete(self.initial_text_id)
    #         self.initial_text_id = None
        
    #     if pil_image_to_display is None:
    #         self.image_canvas.delete("all")
    #         self.update_menu_states(image_loaded=False)
    #         return

    #     canvas_width = self.image_canvas.winfo_width()
    #     canvas_height = self.image_canvas.winfo_height()
        
    #     # --- Image Scaling Logic ---
    #     img_w, img_h = pil_image_to_display.size
        
    #     if self.controller.display_mode == 'fit':
    #         # Calculate scale factor to fit image in canvas
    #         scale_w = canvas_width / img_w
    #         scale_h = canvas_height / img_h
    #         scale = min(scale_w, scale_h)
    #         # if scale >= 1.0: # Don't scale up past 100% in fit mode
    #         #     scale = 1.0
    #         self.controller.zoom_level = scale # Update controller's zoom level
    #     else: # 'actual' or other zoom modes
    #         scale = self.controller.zoom_level

    #     # New dimensions for display
    #     new_w, new_h = int(img_w * scale), int(img_h * scale)

    #     # Use Pillow to resize the image for display. This does NOT affect the saved data.
    #     # Image.Resampling.LANCZOS is high quality, use NEAREST for pixel art if needed.
    #     display_img = pil_image_to_display.resize((new_w, new_h), Image.Resampling.LANCZOS)

    #     # --- Composite with checkered background ---
    #     # Create a checkered background PIL image of the same size
    #     tile_size = 20
    #     c1, c2 = (204, 204, 204), (217, 217, 217)
    #     bg = Image.new("RGBA", (new_w, new_h))
    #     for y in range(0, new_h, tile_size):
    #         for x in range(0, new_w, tile_size):
    #             color = c1 if ((x // tile_size + y // tile_size) % 2 == 0) else c2
    #             Image.Image.paste(bg, Image.new("RGBA", (tile_size, tile_size), color + (255,)), (x, y))
    #     # Ensure display_img is RGBA
    #     if display_img.mode != "RGBA":
    #         display_img = display_img.convert("RGBA")
    #     # Composite image over checkered background
    #     composited_img = Image.alpha_composite(bg, display_img)
        
    #     # Convert to Tkinter-compatible format
    #     self.tk_image = ImageTk.PhotoImage(composited_img)
        
    #     # --- Canvas Update Logic ---
    #     self.image_canvas.delete("all") # Clear previous image
        
    #     # Position the image on the canvas
    #     self.canvas_image_id = self.image_canvas.create_image(0, 0, anchor='nw', image=self.tk_image)
        
    #     # Configure the scroll region to match the scaled image size
    #     self.image_canvas.config(scrollregion=(0, 0, new_w, new_h))
        
    #     self.update_menu_states(image_loaded=True)

    # def update_menu_states(self, image_loaded):
    #     """Enable or disable menu items based on whether an image is loaded."""
    #     state = tk.NORMAL if image_loaded else tk.DISABLED
    #     # File Menu
    #     # self.file_menu.entryconfig("Open RWR los.png", state=tk.NORMAL if self.rwr_los_path else tk.DISABLED)
    #     self.file_menu.entryconfig("Save", state=state)
    #     self.file_menu.entryconfig("Save As...", state=state)
    #     self.file_menu.entryconfig("Reset to Original", state=state)
    #     self.file_menu.entryconfig("Load Tool Settings...", state=state)
    #     self.file_menu.entryconfig("Save Tool Settings...", state=state)
    #     self.file_menu.entryconfig("Save Tool Settings As...", state=state)
    #     # View Menu
    #     self.view_menu.entryconfig("Zoom In (+)", state=state)
    #     self.view_menu.entryconfig("Zoom Out (-)", state=state)
    #     self.view_menu.entryconfig("Fit to Window", state=state)
    #     self.view_menu.entryconfig("Actual Size (100%)", state=state)
    
    # def load_tool_settings(self, settings):
    #     """Applies loaded settings to the relevant tool GUIs."""
    #     for tool_name, tool_instance in self.tools.items():
    #         tool_instance.set_settings(settings.get(tool_name, {}))
        
    # def update_status_bar(self, image_path: str | None, config_path: str | None): # new
    #     """Updates the labels in the status bar."""
    #     img_text = f"Image: {image_path}" if image_path else "Image: N/A"
    #     cfg_text = f"Config: {config_path}" if config_path else "Config: N/A"
    #     self.image_path_var.set(img_text)
    #     self.config_path_var.set(cfg_text)

    # def get_rwr_los_path(self):
    #     """
    #     Opens a file dialog to select the RWR LOS file.
    #     """
    #     rwr_path = path_finder.find_game_install_path()
    #     if not rwr_path:
    #         messagebox.showerror("Error", "RWR installation path not found.")
    #         return None
        
    #     rwr_los_suffix = "media/packages/vanilla/textures/los.png"
    #     rwr_los_path = os.path.join(rwr_path, rwr_los_suffix)
    #     if not os.path.exists(rwr_los_path):
    #         messagebox.showerror("Error", f"RWR LOS file not found at {rwr_los_path}.")
    #         return None
        
    #     return rwr_los_path
    
    # def open_rwr_los(self):
    #     """
    #     Opens the RWR LOS file in the image display area.
    #     """
    #     if not self.rwr_los_path:
    #         messagebox.showerror("Error", "RWR LOS path is not set.")
    #         return
        
    #     try:
    #         self.controller.open_image(self.rwr_los_path)
    #     except Exception as e:
    #         messagebox.showerror("Error", f"Failed to open RWR LOS file: {e}")