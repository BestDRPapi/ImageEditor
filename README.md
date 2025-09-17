# Full-Featured Image Editor

A comprehensive image editing application with multiple implementations providing drawing tools, text editing, image manipulation, copy/paste functionality, date/time insertion, and much more.

## 🌟 Features

### Core Drawing Tools
- **Brush/Freehand Drawing**: Smooth drawing with adjustable brush sizes
- **Line Tool**: Draw straight lines with customizable thickness
- **Rectangle Tool**: Draw outlined and filled rectangles
- **Circle/Oval Tool**: Create circles and ovals (outlined and filled)
- **Text Tool**: Add text with different fonts, sizes, and styles
- **Selection Tool**: Select, move, copy, and paste graphics and text

### Text and Content Features
- **Date and Time Insertion**: Automatically insert current date/time
- **Multiple Font Support**: Choose from system fonts with size control
- **Text Formatting**: Bold, italic, and different font families
- **Big ASCII Art Text**: Large decorative text rendering

### Image Manipulation
- **Canvas Resizing**: Dynamically resize the working area
- **Image Rotation**: Rotate images 90° clockwise/counterclockwise
- **Flip Operations**: Horizontal and vertical image flipping
- **Color Management**: Full color picker with quick color palette
- **Shape Properties**: Adjustable line thickness and fill options

### Advanced Features
- **Copy and Paste**: Copy selections and paste graphics/text anywhere
- **Undo/Redo System**: Multi-level undo/redo (up to 50 operations)
- **File Operations**: Save, load, export in multiple formats
- **Layer Management**: Object-based editing with selection controls
- **Canvas Export**: Export as PostScript, JSON data, or text files

## 📋 Available Versions

This project includes three different implementations to suit various needs:

### 1. Full GUI Version (`image_editor.py`)
- **Requirements**: Pillow, numpy
- **Features**: Complete GUI with PIL image processing
- **Best for**: Professional image editing with full feature set

### 2. Simplified GUI Version (`image_editor_simple.py`)
- **Requirements**: tkinter (built-in)
- **Features**: Vector-based drawing with tkinter canvas
- **Best for**: Lightweight GUI editing without external dependencies

### 3. Command-Line Version (`image_editor_cli.py`)
- **Requirements**: None (pure Python)
- **Features**: ASCII art editing with full command interface
- **Best for**: Terminal-based editing, servers, or systems without GUI

## 🚀 Quick Start

### Running the GUI Version (Recommended)
```bash
# Install dependencies (for full version)
pip install Pillow numpy

# Run the full GUI version
python3 image_editor.py

# Or run the simplified GUI version (no dependencies)
python3 image_editor_simple.py
```

### Running the Command-Line Version
```bash
# No installation required - pure Python
python3 image_editor_cli.py

# Example commands:
editor> help                           # Show all commands
editor> display                        # Show current canvas
editor> rect 10 5 30 15                # Draw rectangle
editor> text 15 8 Hello World          # Add text
editor> datetime 10 18                 # Insert date/time
editor> save my_artwork.txt             # Save canvas
```

### Running the Demo
```bash
python3 demo.py
```

## 🎯 Command Reference (CLI Version)

### Canvas Operations
- `new [width] [height]` - Create new canvas
- `clear` - Clear the canvas
- `display` - Show current canvas
- `resize <width> <height>` - Resize canvas

### Drawing Tools
- `pixel <x> <y>` - Set a single pixel
- `line <x1> <y1> <x2> <y2>` - Draw line
- `rect <x1> <y1> <x2> <y2>` - Draw rectangle
- `fillrect <x1> <y1> <x2> <y2>` - Draw filled rectangle
- `circle <cx> <cy> <radius>` - Draw circle
- `fillcircle <cx> <cy> <radius>` - Draw filled circle

### Text and Content
- `text <x> <y> <text>` - Add text
- `bigtext <x> <y> <text>` - Add large ASCII art text
- `datetime <x> <y>` - Insert current date/time

### Colors and Style
- `color <name>` - Set drawing color/character
- `colors` - Show available colors
- Available colors: `black`, `gray`, `light`, `dot`, `white`, `x`, `o`, `*`, `+`, `#`

### Edit Operations
- `undo` - Undo last action
- `redo` - Redo last undone action
- `copy <x1> <y1> <x2> <y2>` - Copy region to clipboard
- `paste <x> <y>` - Paste from clipboard

### File Operations
- `save <filename>` - Save canvas to text file
- `export <filename>` - Export canvas data as JSON
- `load <filename>` - Load canvas from JSON file

## 🎨 GUI Controls

### Toolbar Tools
- 🖌️ **Brush**: Freehand drawing
- 📏 **Line**: Straight lines
- ⬜ **Rectangle**: Rectangular shapes
- ⬛ **Filled Rectangle**: Solid rectangles
- ⭕ **Circle**: Circular shapes
- ⚫ **Filled Circle**: Solid circles
- 📝 **Text**: Text insertion
- 👆 **Select**: Selection and manipulation

### Keyboard Shortcuts
- `Ctrl+N`: New canvas/image
- `Ctrl+O`: Open image (full version)
- `Ctrl+S`: Save
- `Ctrl+Z`: Undo
- `Ctrl+Y`: Redo
- `Ctrl+C`: Copy selection
- `Ctrl+V`: Paste
- `Del`: Delete selected objects

### Properties Panel
- **Color Picker**: Choose custom colors
- **Quick Colors**: Instant access to common colors
- **Brush Size**: Adjustable from 1-50 pixels
- **Font Properties**: Family, size, bold, italic
- **Canvas Info**: Dimensions and selection details

## 📁 File Formats

### Supported Export Formats
- **PostScript (.ps)**: Vector graphics format
- **JSON (.json)**: Canvas data with full object information
- **Text (.txt)**: ASCII art representation

### Example Output
```
+----------------------------------------+
|                    ███████████         |
|     ███████████    █         █         |
|     █         █    █HELLO    █         |
|     █HELLO    █    █         █         |
|     █         █    █         █         |
|     █         █    ███████████         |
|     ███████████      ▓▓▓▓▓▓▓           |
|                       ▓▓▓▓▓            |
|  ────────────────────────────────────  |
|     2025-09-17 12:09                   |
+----------------------------------------+
```

## 🛠️ Technical Features

### Architecture
- **Object-oriented design** with clean separation of concerns
- **State management** with undo/redo system
- **Event-driven interface** for responsive user interaction
- **Multiple rendering backends** (PIL, tkinter, ASCII)

### Performance
- **Efficient drawing algorithms** (Bresenham's line, midpoint circle)
- **Memory-optimized** state storage
- **Scalable canvas** with scrolling support
- **Fast object manipulation** with selection caching

### Extensibility
- **Modular tool system** - easy to add new drawing tools
- **Pluggable file formats** - simple to add export options
- **Customizable UI** - themes and layout modifications
- **Command system** - extensible command interface

## 📊 Demo Results

The included demo showcases:
- ✅ Drawing rectangles, circles, and lines
- ✅ Text insertion with timestamps
- ✅ Color/character variations
- ✅ Copy and paste operations
- ✅ File save/export functionality
- ✅ Big ASCII art text rendering

## 🤝 Contributing

This image editor demonstrates professional software development practices:
- Clean, documented code with type hints
- Comprehensive error handling
- Multiple implementation approaches
- Extensive feature coverage
- User-friendly interfaces

## 📄 License

Open source - free to use, modify, and distribute.
