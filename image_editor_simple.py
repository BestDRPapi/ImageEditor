#!/usr/bin/env python3
"""
Full-Featured Image Editor (Simplified Version)
A comprehensive image editing application with drawing tools, text editing, 
and basic image manipulation using only built-in Python libraries.
"""

import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox, font, simpledialog
from datetime import datetime
import os
import json


class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.root.geometry("1200x800")
        
        # Canvas and drawing variables
        self.canvas_width = 800
        self.canvas_height = 600
        
        # Drawing state variables
        self.current_tool = "brush"
        self.current_color = "#000000"
        self.brush_size = 5
        self.last_x = None
        self.last_y = None
        self.drawing_objects = []
        self.undo_stack = []
        self.redo_stack = []
        
        # Clipboard
        self.clipboard_data = None
        self.clipboard_type = None
        
        # Selection variables
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        self.selected_objects = []
        
        # Text properties
        self.current_font_family = "Arial"
        self.current_font_size = 12
        
        self.setup_ui()
        self.new_canvas()
        
    def setup_ui(self):
        """Set up the user interface"""
        self.create_menu()
        self.create_toolbar()
        
        # Create main layout
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for tools
        self.create_tool_panel(main_frame)
        
        # Center canvas area
        self.create_canvas_area(main_frame)
        
        # Right panel for properties
        self.create_properties_panel(main_frame)
        
        # Status bar
        self.create_status_bar()
        
    def create_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_canvas, accelerator="Ctrl+N")
        file_menu.add_command(label="Save As PostScript", command=self.save_canvas, accelerator="Ctrl+S")
        file_menu.add_command(label="Export Canvas", command=self.export_canvas)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy", command=self.copy_selection, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_selection, accelerator="Ctrl+V")
        edit_menu.add_command(label="Delete", command=self.delete_selected, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear All", command=self.clear_canvas)
        
        # Insert menu
        insert_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Insert", menu=insert_menu)
        insert_menu.add_command(label="Date and Time", command=self.insert_datetime)
        insert_menu.add_command(label="Text", command=self.insert_text)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Brush", command=lambda: self.set_tool("brush"))
        tools_menu.add_command(label="Line", command=lambda: self.set_tool("line"))
        tools_menu.add_command(label="Rectangle", command=lambda: self.set_tool("rectangle"))
        tools_menu.add_command(label="Filled Rectangle", command=lambda: self.set_tool("filled_rectangle"))
        tools_menu.add_command(label="Circle", command=lambda: self.set_tool("circle"))
        tools_menu.add_command(label="Filled Circle", command=lambda: self.set_tool("filled_circle"))
        tools_menu.add_command(label="Text", command=lambda: self.set_tool("text"))
        tools_menu.add_command(label="Select", command=lambda: self.set_tool("select"))
        
        # Keyboard bindings
        self.root.bind('<Control-n>', lambda e: self.new_canvas())
        self.root.bind('<Control-s>', lambda e: self.save_canvas())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-c>', lambda e: self.copy_selection())
        self.root.bind('<Control-v>', lambda e: self.paste_selection())
        self.root.bind('<Delete>', lambda e: self.delete_selected())
        
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # Tool buttons with icons
        tools = [
            ("🖌️ Brush", "brush"),
            ("📏 Line", "line"),
            ("⬜ Rectangle", "rectangle"),
            ("⬛ Filled Rect", "filled_rectangle"),
            ("⭕ Circle", "circle"),
            ("⚫ Filled Circle", "filled_circle"),
            ("📝 Text", "text"),
            ("👆 Select", "select")
        ]
        
        for name, tool in tools:
            btn = ttk.Button(toolbar, text=name, 
                           command=lambda t=tool: self.set_tool(t))
            btn.pack(side=tk.LEFT, padx=2)
            
    def create_tool_panel(self, parent):
        """Create the left tool panel"""
        tool_frame = ttk.LabelFrame(parent, text="Tools & Properties", width=220)
        tool_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        tool_frame.pack_propagate(False)
        
        # Color selection
        color_frame = ttk.Frame(tool_frame)
        color_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(color_frame, text="Color:").pack()
        self.color_button = tk.Button(color_frame, bg=self.current_color, 
                                    width=15, height=2, command=self.choose_color)
        self.color_button.pack(pady=2)
        
        # Quick colors
        quick_colors_frame = ttk.Frame(color_frame)
        quick_colors_frame.pack(fill=tk.X, pady=2)
        
        quick_colors = ["#000000", "#FF0000", "#00FF00", "#0000FF", 
                       "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF"]
        
        for i, color in enumerate(quick_colors):
            row = i // 4
            col = i % 4
            btn = tk.Button(quick_colors_frame, bg=color, width=2, height=1,
                          command=lambda c=color: self.set_color(c))
            btn.grid(row=row, column=col, padx=1, pady=1, sticky="ew")
            
        # Configure grid weights
        for i in range(4):
            quick_colors_frame.columnconfigure(i, weight=1)
        
        # Brush size
        size_frame = ttk.Frame(tool_frame)
        size_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(size_frame, text="Brush/Line Size:").pack()
        self.size_var = tk.IntVar(value=self.brush_size)
        size_scale = ttk.Scale(size_frame, from_=1, to=50, variable=self.size_var,
                             orient=tk.HORIZONTAL, command=self.update_brush_size)
        size_scale.pack(fill=tk.X)
        
        self.size_label = ttk.Label(size_frame, text=f"Size: {self.brush_size}")
        self.size_label.pack()
        
        # Shape fill option
        fill_frame = ttk.Frame(tool_frame)
        fill_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.fill_var = tk.BooleanVar(value=False)
        fill_check = ttk.Checkbutton(fill_frame, text="Fill shapes", variable=self.fill_var)
        fill_check.pack()
        
    def create_canvas_area(self, parent):
        """Create the main canvas area"""
        canvas_frame = ttk.LabelFrame(parent, text="Canvas")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Create scrollable canvas
        canvas_container = ttk.Frame(canvas_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL)
        
        # Canvas
        self.canvas = tk.Canvas(canvas_container, bg="white",
                              scrollregion=(0, 0, self.canvas_width, self.canvas_height),
                              yscrollcommand=v_scrollbar.set,
                              xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind canvas events
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release)
        self.canvas.bind("<Button-3>", self.canvas_right_click)  # Right click
        
    def create_properties_panel(self, parent):
        """Create the right properties panel"""
        props_frame = ttk.LabelFrame(parent, text="Properties", width=200)
        props_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        props_frame.pack_propagate(False)
        
        # Text properties
        text_frame = ttk.LabelFrame(props_frame, text="Text Properties")
        text_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Font family
        ttk.Label(text_frame, text="Font:").pack()
        self.font_var = tk.StringVar(value=self.current_font_family)
        font_combo = ttk.Combobox(text_frame, textvariable=self.font_var,
                                values=list(font.families())[:20])  # Limit to first 20 fonts
        font_combo.pack(fill=tk.X, padx=2, pady=2)
        font_combo.bind("<<ComboboxSelected>>", self.update_font)
        
        # Font size
        ttk.Label(text_frame, text="Size:").pack()
        self.font_size_var = tk.IntVar(value=self.current_font_size)
        size_spin = ttk.Spinbox(text_frame, from_=8, to=72, textvariable=self.font_size_var,
                              command=self.update_font_size)
        size_spin.pack(fill=tk.X, padx=2, pady=2)
        
        # Font style
        style_frame = ttk.Frame(text_frame)
        style_frame.pack(fill=tk.X, padx=2, pady=2)
        
        self.bold_var = tk.BooleanVar(value=False)
        self.italic_var = tk.BooleanVar(value=False)
        
        bold_check = ttk.Checkbutton(style_frame, text="Bold", variable=self.bold_var,
                                   command=self.update_font)
        bold_check.pack(side=tk.LEFT)
        
        italic_check = ttk.Checkbutton(style_frame, text="Italic", variable=self.italic_var,
                                     command=self.update_font)
        italic_check.pack(side=tk.LEFT)
        
        # Canvas info
        info_frame = ttk.LabelFrame(props_frame, text="Canvas Info")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.info_label = ttk.Label(info_frame, text=f"Size: {self.canvas_width}×{self.canvas_height}")
        self.info_label.pack(padx=5, pady=5)
        
        # Selected object info
        selected_frame = ttk.LabelFrame(props_frame, text="Selection")
        selected_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.selected_info = ttk.Label(selected_frame, text="No selection")
        self.selected_info.pack(padx=5, pady=5)
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def new_canvas(self):
        """Create a new blank canvas"""
        self.canvas.delete("all")
        self.drawing_objects.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.selected_objects.clear()
        self.save_state()
        self.status_bar.config(text="New canvas created")
        self.update_selection_info()
        
    def save_canvas(self):
        """Save canvas as PostScript file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Canvas As",
            defaultextension=".ps",
            filetypes=[
                ("PostScript files", "*.ps"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.canvas.postscript(file=file_path)
                self.status_bar.config(text=f"Saved: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save canvas: {str(e)}")
                
    def export_canvas(self):
        """Export canvas data as JSON"""
        file_path = filedialog.asksaveasfilename(
            title="Export Canvas Data",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                canvas_data = {
                    "width": self.canvas_width,
                    "height": self.canvas_height,
                    "objects": self.drawing_objects
                }
                with open(file_path, 'w') as f:
                    json.dump(canvas_data, f, indent=2)
                self.status_bar.config(text=f"Exported: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export canvas: {str(e)}")
                
    def set_tool(self, tool):
        """Set the current drawing tool"""
        self.current_tool = tool
        self.status_bar.config(text=f"Tool: {tool.title().replace('_', ' ')}")
        
        # Clear selection when changing tools
        if tool != "select":
            self.clear_selection()
            
    def choose_color(self):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(color=self.current_color)[1]
        if color:
            self.set_color(color)
            
    def set_color(self, color):
        """Set the current color"""
        self.current_color = color
        self.color_button.config(bg=color)
        
        # Update selected objects' color
        if self.selected_objects:
            for obj_id in self.selected_objects:
                try:
                    if self.canvas.type(obj_id) == "text":
                        self.canvas.itemconfig(obj_id, fill=color)
                    else:
                        self.canvas.itemconfig(obj_id, outline=color)
                except tk.TclError:
                    pass  # Object might have been deleted
                    
    def update_brush_size(self, value):
        """Update brush size from scale"""
        self.brush_size = int(float(value))
        self.size_label.config(text=f"Size: {self.brush_size}")
        
        # Update selected objects' width
        if self.selected_objects:
            for obj_id in self.selected_objects:
                try:
                    if self.canvas.type(obj_id) != "text":
                        self.canvas.itemconfig(obj_id, width=self.brush_size)
                except tk.TclError:
                    pass
                    
    def update_font(self, event=None):
        """Update font properties"""
        self.current_font_family = self.font_var.get()
        
        # Update selected text objects
        if self.selected_objects:
            font_style = []
            if self.bold_var.get():
                font_style.append("bold")
            if self.italic_var.get():
                font_style.append("italic")
                
            font_tuple = (self.current_font_family, self.current_font_size, " ".join(font_style))
            
            for obj_id in self.selected_objects:
                try:
                    if self.canvas.type(obj_id) == "text":
                        self.canvas.itemconfig(obj_id, font=font_tuple)
                except tk.TclError:
                    pass
                    
    def update_font_size(self):
        """Update font size"""
        try:
            self.current_font_size = self.font_size_var.get()
            self.update_font()
        except:
            pass
            
    def canvas_click(self, event):
        """Handle canvas click events"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.current_tool == "brush":
            self.last_x = x
            self.last_y = y
        elif self.current_tool in ["line", "rectangle", "filled_rectangle", "circle", "filled_circle"]:
            self.shape_start = (x, y)
            self.temp_shape = None
        elif self.current_tool == "text":
            self.add_text(x, y)
        elif self.current_tool == "select":
            self.handle_selection(x, y, event)
            
    def canvas_drag(self, event):
        """Handle canvas drag events"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.current_tool == "brush" and self.last_x is not None and self.last_y is not None:
            # Draw brush stroke
            obj_id = self.canvas.create_line(self.last_x, self.last_y, x, y,
                                           fill=self.current_color, width=self.brush_size,
                                           capstyle=tk.ROUND, smooth=True)
            self.drawing_objects.append({
                "type": "line",
                "id": obj_id,
                "coords": [self.last_x, self.last_y, x, y],
                "color": self.current_color,
                "width": self.brush_size
            })
            self.last_x = x
            self.last_y = y
            
        elif self.current_tool in ["line", "rectangle", "filled_rectangle", "circle", "filled_circle"] and hasattr(self, 'shape_start'):
            # Preview shape
            if self.temp_shape:
                self.canvas.delete(self.temp_shape)
                
            if self.current_tool == "line":
                self.temp_shape = self.canvas.create_line(
                    self.shape_start[0], self.shape_start[1], x, y,
                    fill=self.current_color, width=self.brush_size)
            elif self.current_tool == "rectangle":
                self.temp_shape = self.canvas.create_rectangle(
                    self.shape_start[0], self.shape_start[1], x, y,
                    outline=self.current_color, width=self.brush_size)
            elif self.current_tool == "filled_rectangle":
                self.temp_shape = self.canvas.create_rectangle(
                    self.shape_start[0], self.shape_start[1], x, y,
                    fill=self.current_color, outline=self.current_color, width=self.brush_size)
            elif self.current_tool == "circle":
                self.temp_shape = self.canvas.create_oval(
                    self.shape_start[0], self.shape_start[1], x, y,
                    outline=self.current_color, width=self.brush_size)
            elif self.current_tool == "filled_circle":
                self.temp_shape = self.canvas.create_oval(
                    self.shape_start[0], self.shape_start[1], x, y,
                    fill=self.current_color, outline=self.current_color, width=self.brush_size)
                    
    def canvas_release(self, event):
        """Handle canvas release events"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.current_tool == "brush":
            if self.drawing_objects:  # If we drew something
                self.save_state()
        elif self.current_tool in ["line", "rectangle", "filled_rectangle", "circle", "filled_circle"] and hasattr(self, 'shape_start'):
            if self.temp_shape:
                # Finalize the shape
                obj_data = {
                    "type": self.current_tool,
                    "id": self.temp_shape,
                    "coords": [self.shape_start[0], self.shape_start[1], x, y],
                    "color": self.current_color,
                    "width": self.brush_size
                }
                self.drawing_objects.append(obj_data)
                self.temp_shape = None
                self.save_state()
                
        self.last_x = None
        self.last_y = None
        
    def canvas_right_click(self, event):
        """Handle right-click context menu"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Insert Text Here", 
                               command=lambda: self.add_text(x, y))
        context_menu.add_command(label="Insert Date/Time Here", 
                               command=lambda: self.add_datetime_at(x, y))
        context_menu.add_separator()
        context_menu.add_command(label="Paste Here", 
                               command=lambda: self.paste_at(x, y))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def add_text(self, x, y):
        """Add text to the canvas"""
        text = simpledialog.askstring("Add Text", "Enter text:", 
                                    initialvalue="Text")
        if text:
            font_style = []
            if self.bold_var.get():
                font_style.append("bold")
            if self.italic_var.get():
                font_style.append("italic")
                
            font_tuple = (self.current_font_family, self.current_font_size, " ".join(font_style))
            
            obj_id = self.canvas.create_text(x, y, text=text, fill=self.current_color,
                                           font=font_tuple, anchor=tk.NW)
            
            obj_data = {
                "type": "text",
                "id": obj_id,
                "coords": [x, y],
                "text": text,
                "color": self.current_color,
                "font": font_tuple
            }
            self.drawing_objects.append(obj_data)
            self.save_state()
            
    def insert_datetime(self):
        """Insert current date and time at center"""
        x = self.canvas_width // 2
        y = self.canvas_height // 2
        self.add_datetime_at(x, y)
        
    def add_datetime_at(self, x, y):
        """Add date/time at specific position"""
        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        font_style = []
        if self.bold_var.get():
            font_style.append("bold")
        if self.italic_var.get():
            font_style.append("italic")
            
        font_tuple = (self.current_font_family, self.current_font_size, " ".join(font_style))
        
        obj_id = self.canvas.create_text(x, y, text=datetime_str, fill=self.current_color,
                                       font=font_tuple, anchor=tk.NW)
        
        obj_data = {
            "type": "text",
            "id": obj_id,
            "coords": [x, y],
            "text": datetime_str,
            "color": self.current_color,
            "font": font_tuple
        }
        self.drawing_objects.append(obj_data)
        self.save_state()
        
    def insert_text(self):
        """Insert text at center of canvas"""
        x = self.canvas_width // 2
        y = self.canvas_height // 2
        self.add_text(x, y)
        
    def handle_selection(self, x, y, event):
        """Handle selection tool"""
        # Find objects at this position
        obj_ids = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
        
        if obj_ids:
            # Select the topmost object
            top_obj = obj_ids[-1]
            
            if event.state & 0x4:  # Ctrl key held
                # Add to selection
                if top_obj not in self.selected_objects:
                    self.selected_objects.append(top_obj)
                else:
                    self.selected_objects.remove(top_obj)
            else:
                # New selection
                self.clear_selection()
                self.selected_objects.append(top_obj)
                
            self.highlight_selection()
            self.update_selection_info()
        else:
            # Click on empty space - clear selection
            self.clear_selection()
            
    def clear_selection(self):
        """Clear current selection"""
        # Remove selection highlights
        for obj_id in list(self.canvas.find_withtag("selection_highlight")):
            self.canvas.delete(obj_id)
            
        self.selected_objects.clear()
        self.update_selection_info()
        
    def highlight_selection(self):
        """Highlight selected objects"""
        # Remove old highlights
        for obj_id in list(self.canvas.find_withtag("selection_highlight")):
            self.canvas.delete(obj_id)
            
        # Add new highlights
        for obj_id in self.selected_objects:
            try:
                bbox = self.canvas.bbox(obj_id)
                if bbox:
                    highlight = self.canvas.create_rectangle(
                        bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2,
                        outline="blue", width=2, dash=(3, 3),
                        tags="selection_highlight")
            except tk.TclError:
                pass
                
    def update_selection_info(self):
        """Update selection information display"""
        if self.selected_objects:
            count = len(self.selected_objects)
            self.selected_info.config(text=f"{count} object(s) selected")
        else:
            self.selected_info.config(text="No selection")
            
    def copy_selection(self):
        """Copy selected objects to clipboard"""
        if not self.selected_objects:
            self.status_bar.config(text="No objects selected to copy")
            return
            
        # Store selected objects data
        copied_data = []
        for obj_id in self.selected_objects:
            for obj_data in self.drawing_objects:
                if obj_data["id"] == obj_id:
                    copied_data.append(obj_data.copy())
                    break
                    
        self.clipboard_data = copied_data
        self.clipboard_type = "objects"
        self.status_bar.config(text=f"Copied {len(copied_data)} object(s)")
        
    def paste_selection(self):
        """Paste objects from clipboard"""
        if not self.clipboard_data or self.clipboard_type != "objects":
            self.status_bar.config(text="Nothing to paste")
            return
            
        self.paste_at(50, 50)  # Default offset
        
    def paste_at(self, offset_x, offset_y):
        """Paste objects at specific position"""
        if not self.clipboard_data or self.clipboard_type != "objects":
            return
            
        # Calculate original position (first object's position)
        if self.clipboard_data:
            original_x = self.clipboard_data[0]["coords"][0]
            original_y = self.clipboard_data[0]["coords"][1]
            
            # Calculate offset
            dx = offset_x - original_x
            dy = offset_y - original_y
        else:
            dx = dy = 0
            
        # Paste objects with offset
        new_objects = []
        for obj_data in self.clipboard_data:
            new_coords = []
            for i in range(0, len(obj_data["coords"]), 2):
                new_coords.append(obj_data["coords"][i] + dx)
                new_coords.append(obj_data["coords"][i+1] + dy)
                
            # Create new object
            if obj_data["type"] == "line":
                new_id = self.canvas.create_line(
                    *new_coords, fill=obj_data["color"], width=obj_data["width"],
                    capstyle=tk.ROUND, smooth=True)
            elif obj_data["type"] == "rectangle":
                new_id = self.canvas.create_rectangle(
                    *new_coords, outline=obj_data["color"], width=obj_data["width"])
            elif obj_data["type"] == "filled_rectangle":
                new_id = self.canvas.create_rectangle(
                    *new_coords, fill=obj_data["color"], outline=obj_data["color"], 
                    width=obj_data["width"])
            elif obj_data["type"] == "circle":
                new_id = self.canvas.create_oval(
                    *new_coords, outline=obj_data["color"], width=obj_data["width"])
            elif obj_data["type"] == "filled_circle":
                new_id = self.canvas.create_oval(
                    *new_coords, fill=obj_data["color"], outline=obj_data["color"], 
                    width=obj_data["width"])
            elif obj_data["type"] == "text":
                new_id = self.canvas.create_text(
                    new_coords[0], new_coords[1], text=obj_data["text"], 
                    fill=obj_data["color"], font=obj_data["font"], anchor=tk.NW)
                    
            new_obj_data = obj_data.copy()
            new_obj_data["id"] = new_id
            new_obj_data["coords"] = new_coords
            new_objects.append(new_obj_data)
            self.drawing_objects.append(new_obj_data)
            
        self.save_state()
        self.status_bar.config(text=f"Pasted {len(new_objects)} object(s)")
        
    def delete_selected(self):
        """Delete selected objects"""
        if not self.selected_objects:
            self.status_bar.config(text="No objects selected to delete")
            return
            
        # Delete from canvas
        for obj_id in self.selected_objects:
            self.canvas.delete(obj_id)
            
        # Remove from drawing objects list
        self.drawing_objects = [obj for obj in self.drawing_objects 
                              if obj["id"] not in self.selected_objects]
        
        count = len(self.selected_objects)
        self.clear_selection()
        self.save_state()
        self.status_bar.config(text=f"Deleted {count} object(s)")
        
    def clear_canvas(self):
        """Clear the entire canvas"""
        result = messagebox.askyesno("Clear Canvas", 
                                   "Are you sure you want to clear the entire canvas?")
        if result:
            self.canvas.delete("all")
            self.drawing_objects.clear()
            self.selected_objects.clear()
            self.save_state()
            self.status_bar.config(text="Canvas cleared")
            self.update_selection_info()
            
    def save_state(self):
        """Save current state for undo functionality"""
        # Save current state
        state = {
            "objects": [obj.copy() for obj in self.drawing_objects]
        }
        self.undo_stack.append(state)
        
        # Limit undo stack size
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
            
        # Clear redo stack on new action
        self.redo_stack.clear()
        
    def undo(self):
        """Undo last action"""
        if len(self.undo_stack) > 1:  # Keep at least one state
            # Move current state to redo stack
            current_state = {
                "objects": [obj.copy() for obj in self.drawing_objects]
            }
            self.redo_stack.append(current_state)
            
            # Pop last state
            self.undo_stack.pop()
            
            # Restore previous state
            prev_state = self.undo_stack[-1]
            self.restore_state(prev_state)
            
            self.status_bar.config(text="Undone")
            
    def redo(self):
        """Redo last undone action"""
        if self.redo_stack:
            # Move current state to undo stack
            current_state = {
                "objects": [obj.copy() for obj in self.drawing_objects]
            }
            self.undo_stack.append(current_state)
            
            # Restore redo state
            redo_state = self.redo_stack.pop()
            self.restore_state(redo_state)
            
            self.status_bar.config(text="Redone")
            
    def restore_state(self, state):
        """Restore canvas to a previous state"""
        # Clear canvas
        self.canvas.delete("all")
        self.drawing_objects.clear()
        self.clear_selection()
        
        # Recreate objects
        for obj_data in state["objects"]:
            if obj_data["type"] == "line":
                new_id = self.canvas.create_line(
                    *obj_data["coords"], fill=obj_data["color"], 
                    width=obj_data["width"], capstyle=tk.ROUND, smooth=True)
            elif obj_data["type"] == "rectangle":
                new_id = self.canvas.create_rectangle(
                    *obj_data["coords"], outline=obj_data["color"], 
                    width=obj_data["width"])
            elif obj_data["type"] == "filled_rectangle":
                new_id = self.canvas.create_rectangle(
                    *obj_data["coords"], fill=obj_data["color"], 
                    outline=obj_data["color"], width=obj_data["width"])
            elif obj_data["type"] == "circle":
                new_id = self.canvas.create_oval(
                    *obj_data["coords"], outline=obj_data["color"], 
                    width=obj_data["width"])
            elif obj_data["type"] == "filled_circle":
                new_id = self.canvas.create_oval(
                    *obj_data["coords"], fill=obj_data["color"], 
                    outline=obj_data["color"], width=obj_data["width"])
            elif obj_data["type"] == "text":
                new_id = self.canvas.create_text(
                    obj_data["coords"][0], obj_data["coords"][1], 
                    text=obj_data["text"], fill=obj_data["color"], 
                    font=obj_data["font"], anchor=tk.NW)
                    
            # Update object data with new ID
            new_obj_data = obj_data.copy()
            new_obj_data["id"] = new_id
            self.drawing_objects.append(new_obj_data)


def main():
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()