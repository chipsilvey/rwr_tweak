# RWR Tweak - Application Context

## Overview

**RWR Tweak** is a Python-based image manipulation tool specifically designed for editing game assets from "Running with Rifles" (RWR), particularly Line of Sight (LoS) PNG images. The application provides a GUI for applying various image processing operations using OpenCV, with settings persistence through YAML configuration files.

### Primary Purpose
- Edit PNG images used in the RWR game, especially Line of Sight files
- Apply color, transparency, and other image transformations
- Save/load processing configurations
- Provide real-time preview of modifications

## Technology Stack

### Core Technologies
- **Python 3.x** - Primary language
- **Tkinter** - GUI framework (uses ttk themed widgets)
- **OpenCV (cv2)** - Image processing (BGRA format with alpha channel preservation)
- **Pillow (PIL)** - Image conversion and display
- **PyYAML** - Configuration file management
- **NumPy** - Array operations for image data
- **PyInstaller** - Application bundling (rwr_tweak.spec)

### Key Dependencies
- opencv-python - Image manipulation
- Pillow - Image display in Tkinter
- PyYAML - Settings persistence
- NumPy - Numerical operations

## Architecture

### Design Pattern: Model-View-Controller (MVC)

The application follows a modular MVC architecture with multiple layers:

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                               │
│                    (Entry Point)                             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                ┌─────────────┴──────────────┐
                │                            │
        ┌───────▼────────┐          ┌───────▼────────┐
        │  MainWindow    │          │ AppController  │
        │   (GUI Shell)  │◄─────────┤  (Coordinator) │
        └───────┬────────┘          └───────┬────────┘
                │                           │
        ┌───────▼────────┐          ┌───────▼────────┐
        │  AppView       │          │ ImageProcessor │
        │  (Base Class)  │          │ ConfigManager  │
        └───────┬────────┘          └────────────────┘
                │
        ┌───────▼────────┐
        │ LineOfSightTool│
        │     View       │
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │   BaseTool     │
        │ (ColorTool,    │
        │ Transparency)  │
        └────────────────┘
```

### Core Components

#### 1. Application Controller (`app_controller.py`)
**Role:** Central coordinator managing all application state and operations

**Responsibilities:**
- Image lifecycle management (load, process, save, backup)
- Settings persistence via ConfigManager
- View registration and switching
- Tool coordination and effect pipeline
- Display mode control (fit/actual/zoom)

**Key Methods:**
- `open_image(file_path)` - Loads image, creates backup, initializes processing
- `update_gui()` - Main update pipeline: apply effects → update view
- `_apply_all_tool_effects()` - Sequential tool processing pipeline
- `apply_changes(tool_name, tool_settings)` - Apply single tool modification
- `save_image(save_path)` - Save processed image + YAML settings
- `register_views(main_window)` - Initialize and register available views

**State Management:**
```python
self.image_path          # Current image file path
self.backup_path         # Backup file path (.png.bak)
self.config_path         # YAML settings file path (.png.yaml)
self.original_image_cv   # Original image (OpenCV format, BGRA)
self.processed_image_cv  # Processed result
self.settings            # Dict of tool settings
self.available_tools     # Dict of tool instances
self.display_mode        # 'fit' | 'actual' | 'custom'
self.zoom_level          # Current zoom factor
```

#### 2. Main Window (`gui/main_window.py`)
**Role:** Top-level GUI container and view manager

**Responsibilities:**
- Window layout and menu bar
- View registration and switching
- Startup message display

**Structure:**
```
MainWindow
├── Menu Bar
│   ├── File Menu (Exit)
│   └── Tools Menu (Populated by controller)
└── main_content_frame
    └── [Swappable Views]
```

**Key Features:**
- View dictionary (`self.views`) for managing multiple tool views
- Grid-based view switching (hide/show mechanism)
- Dynamic tool menu generation

#### 3. App View Base (`gui/views/app_view.py`)
**Role:** Abstract base class for all top-level views

**Contract:**
- Extends `ttk.Frame`
- Receives controller reference
- Provides consistent interface for view management

#### 4. Line of Sight Tool View (`gui/views/los_tool_view.py`)
**Role:** Primary view for image manipulation

**Layout:**
```
LineOfSightToolView
├── Left Column (weight=4)
│   ├── Image Display Area
│   │   ├── Canvas (scrollable, checkered background)
│   │   ├── Vertical Scrollbar
│   │   └── Horizontal Scrollbar
│   └── Status Bar
│       ├── Image Path Label
│       └── Config Path Label
└── Tools Panel (weight=1, right side)
    ├── Control Panel Header
    ├── Zoom Controls
    ├── Display Mode Controls
    └── [Dynamically Loaded Tools]
```

**Key Features:**
- Checkered background for transparency visualization
- Zoom and pan capabilities
- Tool panel with dynamically loaded widgets
- Status bar showing file paths
- Canvas resizing and auto-fit support

**RWR Integration:**
- `get_rwr_los_path()` - Locates RWR game installation via Steam registry
- Provides quick access to game's LoS files

#### 5. Image Processor (`image_processor.py`)
**Role:** OpenCV image I/O and manipulation

**Key Methods:**
- `load(path)` - Loads PNG with `cv2.IMREAD_UNCHANGED` (preserves alpha)
- `save(path, image_data)` - Saves PNG using cv2
- Ensures BGRA format (adds alpha channel if missing)

**Image Format:**
- Internal: OpenCV NumPy array, BGRA 4-channel
- Display: Converted to PIL/ImageTk for Tkinter

#### 6. Config Manager (`config_manager.py`)
**Role:** YAML settings persistence

**Methods:**
- `load(path)` - Reads YAML config, returns dict (empty dict on error/missing)
- `save(path, settings)` - Writes settings dict to YAML

**Settings Structure:**
```yaml
color:
  enabled: true
  hue_shift: 15
  saturation: 85.0
  brightness: 140.0
transparency:
  enabled: true
  alpha_scale: 0.7
```

#### 7. Tools System

##### Base Tool (`tools/base_tool.py`)
**Abstract Interface:**
```python
class BaseTool(ABC):
    @abstractmethod
    def create_gui(parent_frame, controller)
        # Creates Tkinter widgets for tool settings
    
    @abstractmethod
    def get_settings() -> Any
        # Returns current GUI state as serializable data
    
    @abstractmethod
    def set_settings(settings)
        # Applies loaded settings to GUI widgets
    
    @abstractmethod
    def apply(image_data: np.ndarray) -> np.ndarray
        # Processes image, returns modified version
```

##### Tool Implementation Pattern
Each tool:
1. Creates GUI in tool panel (sliders, checkboxes, etc.)
2. Binds widget changes to `_on_change()` callback
3. Callback triggers `controller.apply_changes(tool_name, settings)`
4. Controller rebuilds entire effect pipeline
5. Result displayed in canvas

##### Available Tools

**ColorTool** (`tools/color_tool.py`)
- Hue shift: -90° to +90°
- Saturation: 0% to 100%
- Brightness: 0 to 255
- Uses OpenCV HSV color space conversion
- Enable/disable checkbox

**TransparencyTool** (`tools/transparency_tool.py`)
- Alpha channel scaling
- Global opacity control
- Preserves per-pixel transparency patterns

### Processing Pipeline

```
Original Image (BGRA)
    │
    ├→ Tool 1 (if enabled)
    │    └→ apply(image) → modified_image
    │
    ├→ Tool 2 (if enabled)
    │    └→ apply(image) → modified_image
    │
    └→ Final Processed Image
         │
         ├→ Convert to PIL (RGBA)
         │
         ├→ Apply zoom/resize
         │
         └→ Convert to ImageTk → Display on Canvas
```

**Key Points:**
- Tools applied sequentially in order
- Each tool receives output of previous tool
- Entire pipeline re-runs on any setting change
- Always starts from original image (non-destructive)

## File Organization

```
rwr_tweak/
├── main.py                    # Entry point
├── app_controller.py          # Main application logic
├── image_processor.py         # OpenCV operations
├── config_manager.py          # YAML handling
├── path_finder.py             # Steam/RWR path detection
├── rwr_tweak.spec             # PyInstaller configuration
│
├── gui/
│   ├── __init__.py
│   ├── main_window.py         # Main window container
│   └── views/
│       ├── __init__.py
│       ├── app_view.py        # Base view class
│       └── los_tool_view.py   # Line of Sight tool view
│
├── tools/
│   ├── __init__.py
│   ├── base_tool.py           # Abstract base class
│   ├── color_tool.py          # HSV color adjustment
│   └── transparency_tool.py   # Alpha channel manipulation
│
└── modules/                   # Alternative module system (WIP)
    ├── __init__.py
    ├── module_controller.py
    ├── module_model.py
    ├── module_view.py
    ├── module_operation.py
    └── los_editor/            # LoS module implementation
        ├── __init__.py
        ├── conntroller.py
        ├── model.py
        ├── view.py
        └── operations/
            ├── __init__.py
            ├── color_op.py
            └── transparency_op.py
```

## Key Workflows

### Opening an Image

```
User → "Open Image..." → File Dialog
    ↓
AppController.open_image(file_path)
    ├─ Store image_path
    ├─ Create backup (.png.bak)
    ├─ Load via ImageProcessor → original_image_cv
    ├─ Set config_path (.png.yaml)
    ├─ Reset display_mode = 'fit', zoom = 1.0
    └─ Switch to LineOfSightToolView
        ↓
    update_gui()
        ├─ _apply_all_tool_effects()
        └─ update_view()
            └─ Convert CV → PIL → ImageTk
            └─ Display on canvas
```

### Modifying Settings

```
User adjusts slider → Tool._on_change()
    ↓
controller.apply_changes(tool_name, tool.get_settings())
    ├─ settings[tool_name] = tool_settings
    └─ update_gui()
        ├─ _apply_all_tool_effects()
        │   └─ For each tool in available_tools:
        │       └─ image = tool.apply(image)
        └─ update_view()
```

### Saving Work

```
User → "Save" / "Save As..."
    ↓
AppController.save_image(path)
    ├─ ImageProcessor.save(path, processed_image_cv)
    └─ ConfigManager.save(path + ".yaml", settings)
```

## State Management

### Controller State
- **Image Context**: `image_path`, `backup_path`, `original_image_cv`, `processed_image_cv`
- **Configuration**: `config_path`, `settings` dict
- **Tools**: `available_tools` dict (name → instance)
- **Display**: `zoom_level`, `display_mode`, `active_view`

### View State
- **Canvas**: Image position, scroll region, zoom transform
- **Tool Widgets**: Slider values, checkbox states (managed by tool instances)
- **Status Bar**: File path display

### Persistence
- **Images**: PNG format with alpha channel
- **Settings**: YAML files (`.png.yaml` convention)
- **Backups**: `.png.bak` files created on first open

## Image Format Details

### Internal Representation
- **Format**: NumPy ndarray, shape (H, W, 4)
- **Color Space**: BGRA (OpenCV default with alpha)
- **Data Type**: uint8
- **Alpha**: Fully opaque = 255, fully transparent = 0

### Conversions
```python
# Load: PNG → OpenCV BGRA
cv2.imread(path, cv2.IMREAD_UNCHANGED)

# Display: BGRA → RGBA → PIL → ImageTk
rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGRA2RGBA)
pil_image = Image.fromarray(rgb_image)
photo = ImageTk.PhotoImage(pil_image)
```

## Extension Points

### Adding a New Tool

1. **Create tool class** in `tools/my_tool.py`:
```python
from .base_tool import BaseTool
import numpy as np

class MyTool(BaseTool):
    def create_gui(self, parent_frame, controller):
        # Create Tkinter widgets
        pass
    
    def get_settings(self):
        # Return current settings
        return {"enabled": self.enabled_var.get()}
    
    def set_settings(self, settings):
        # Apply loaded settings
        self.enabled_var.set(settings.get("enabled", False))
    
    def apply(self, image_data: np.ndarray) -> np.ndarray:
        # Process and return image
        return image_data
```

2. **Load tool** in LineOfSightToolView:
```python
from tools.my_tool import MyTool
# In load_tools() or equivalent:
self.my_tool = MyTool()
self.my_tool.create_gui(self.tools_frame, self.controller)
```

3. **Register** with controller's `available_tools` dict

### Adding a New View

1. **Create view class** in `gui/views/my_view.py`:
```python
from .app_view import AppView

class MyView(AppView):
    def __init__(self, parent, main_window, controller):
        super().__init__(parent, controller)
        # Build GUI
```

2. **Register** in `AppController.register_views()`:
```python
my_view = MyView(main_window.main_content_frame, main_window, self)
main_window.register_view("My Tool", my_view)
```

3. **Add menu item** automatically added by registration loop

## Common Patterns

### Non-Destructive Editing
- Original image always preserved in `original_image_cv`
- All operations start from original, rebuild chain
- Undo = reset settings, reprocess

### Settings Binding
```python
# Tool creates Tkinter variable
self.value_var = tk.IntVar(value=50)

# Bind to change handler
slider = ttk.Scale(variable=self.value_var, command=self._on_change)

# On change, notify controller
def _on_change(self, _=None):
    self.controller.apply_changes("tool_name", self.get_settings())
```

### View Updates
```python
# Controller triggers view refresh
def update_view(self):
    if self.processed_image_cv is not None:
        pil_image = self._convert_cv_to_pil(self.processed_image_cv)
        active_view.update_display(pil_image)
```

## Error Handling

### File Operations
- Missing files → `messagebox.showerror()`
- Corrupt images → `ValueError` caught in `open_image()`
- Failed saves → Exception caught, error dialog shown

### Backup System
- Automatic `.bak` creation on first image open
- Reset functionality restores from backup
- Backup only created if not exists

## Steam/RWR Integration

### Path Detection (`path_finder.py`)
- Reads Windows registry: `HKEY_CURRENT_USER\Software\Valve\Steam`
- Parses `libraryfolders.vdf` for Steam libraries
- Locates RWR install (App ID: 270150)
- Finds game files directory structure

### LoS File Location
```
<Steam Library>/steamapps/common/RunningWithRifles/media/packages/vanilla/
```

## Development Considerations

### Architecture Notes
- **Dual Module System**: Both `tools/` and `modules/` exist
  - `tools/` - Current active system (base_tool.py pattern)
  - `modules/` - Alternative architecture (appears incomplete)
  - Consider consolidating to one pattern

- **View Management**: MainWindow grid-based view switching
  - Views created once, shown/hidden via grid()
  - More efficient than destroying/recreating

- **Processing Pipeline**: Sequential tool application
  - Order matters if tools have dependencies
  - Consider adding priority/ordering mechanism

### Performance
- Full pipeline runs on every setting change
- For large images with many tools, consider:
  - Debouncing slider updates
  - Background processing thread
  - Partial pipeline optimization

### Type Hints
- Partial type hint coverage
- `TYPE_CHECKING` guards prevent circular imports
- Consider full type annotation for better IDE support

## Debugging Tips

### Image Issues
- Check image channel count: `image.shape[2]` should be 4 (BGRA)
- Verify alpha channel: `image[:,:,3]` contains transparency data
- Color space: OpenCV uses BGR, display needs RGB

### GUI Updates Not Showing
- Ensure `update_gui()` called after state changes
- Check view is actually visible: `view.winfo_ismapped()`
- Verify tool is in `available_tools` dict

### Settings Not Persisting
- Check `config_path` is set correctly
- Verify YAML file write permissions
- Ensure tool's `get_settings()` returns serializable data

## Future Enhancements

### Potential Features
- Undo/Redo stack (currently only full reset)
- Layer system for complex edits
- Batch processing multiple files
- Custom tool plugin system with dynamic discovery
- Real-time preview toggle (skip processing for performance)
- More image operations (filters, effects, cropping)
- Game asset manager (not just LoS files)

### Code Improvements
- Consolidate tools/ and modules/ systems
- Complete type hint coverage
- Unit tests for image processing operations
- Configuration validation
- Logging system for debugging
- Async image processing for responsiveness

## Dependencies Graph

```
main.py
 ├─→ MainWindow
 │    └─→ AppView
 │         └─→ LineOfSightToolView
 │              └─→ BaseTool
 │                   ├─→ ColorTool
 │                   └─→ TransparencyTool
 └─→ AppController
      ├─→ ImageProcessor (cv2, numpy)
      ├─→ ConfigManager (yaml)
      └─→ path_finder (winreg)
```

## Quick Reference

### Key Files to Modify for Common Tasks

| Task | Files to Edit |
|------|---------------|
| Add new tool | `tools/new_tool.py`, `los_tool_view.py` |
| Change GUI layout | `gui/main_window.py`, `gui/views/los_tool_view.py` |
| Add menu items | `gui/main_window.py`, `app_controller.py` |
| Modify image processing | `image_processor.py`, `tools/*.py` |
| Change settings format | `config_manager.py`, affected tools |
| Add new view/mode | `gui/views/new_view.py`, `app_controller.register_views()` |

### Important Conventions

- **File naming**: Tools end with `_tool.py`, views end with `_view.py`
- **Config files**: `<imagename>.png.yaml` convention
- **Backups**: `<imagename>.png.bak` created automatically
- **Color format**: BGRA internally, RGBA for display
- **Tool settings**: Must be YAML-serializable (dict, list, primitives)

---

*This context document is designed for LLM consumption to understand the RWR Tweak codebase architecture, patterns, and implementation details.*
