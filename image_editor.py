#!/usr/bin/env python3
"""
Full-Featured Image Editor
A comprehensive image editing application with drawing tools, text editing, 
image manipulation, and more.
"""

import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox, font, simpledialog
from PIL import Image, ImageDraw, ImageFont, ImageTk
import numpy as np
from datetime import datetime
import os
import io
import json


class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.root.geometry("1200x800")
        
        # Canvas and image variables
        self.canvas_width = 800
        self.canvas_height = 600
        self.current_image = None
        self.display_image = None
        self.canvas_image_id = None
        
        # Drawing state variables
        self.current_tool = "brush"
        self.current_color = "#000000"
        self.brush_size = 5
        self.last_x = None
        self.last_y = None
        self.shapes = []
        self.texts = []
        self.undo_stack = []
        self.redo_stack = []
        
        # Clipboard
        self.clipboard_data = None
        self.clipboard_type = None
        
        # Selection variables
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        
        self.setup_ui()
        self.new_image()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Create main menu
        self.create_menu()
        
        # Create toolbar
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
        file_menu.add_command(label="New", command=self.new_image, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_image, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        
        # Insert menu
        insert_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Insert", menu=insert_menu)
        insert_menu.add_command(label="Date and Time", command=self.insert_datetime)
        insert_menu.add_command(label="Text", command=self.insert_text)
        
        # Image menu
        image_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Image", menu=image_menu)
        image_menu.add_command(label="Resize", command=self.resize_image)
        image_menu.add_command(label="Rotate 90° CW", command=lambda: self.rotate_image(90))
        image_menu.add_command(label="Rotate 90° CCW", command=lambda: self.rotate_image(-90))
        image_menu.add_command(label="Flip Horizontal", command=self.flip_horizontal)
        image_menu.add_command(label="Flip Vertical", command=self.flip_vertical)
        
        # Keyboard bindings
        self.root.bind('<Control-n>', lambda e: self.new_image())
        self.root.bind('<Control-o>', lambda e: self.open_image())
        self.root.bind('<Control-s>', lambda e: self.save_image())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # Tool buttons
        tools = [
            ("Brush", "brush", "🖌️"),
            ("Line", "line", "📏"),
            ("Rectangle", "rectangle", "⬜"),
            ("Circle", "circle", "⭕"),
            ("Text", "text", "📝"),
            ("Select", "select", "👆")
        ]
        
        for name, tool, icon in tools:
            btn = ttk.Button(toolbar, text=f"{icon} {name}", 
                           command=lambda t=tool: self.set_tool(t))
            btn.pack(side=tk.LEFT, padx=2)
            
    def create_tool_panel(self, parent):
        """Create the left tool panel"""
        tool_frame = ttk.LabelFrame(parent, text="Tools", width=200)
        tool_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        tool_frame.pack_propagate(False)
        
        # Color selection
        color_frame = ttk.Frame(tool_frame)
        color_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(color_frame, text="Color:").pack()
        self.color_button = tk.Button(color_frame, bg=self.current_color, 
                                    width=10, height=2, command=self.choose_color)
        self.color_button.pack(pady=2)
        
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
        self.font_var = tk.StringVar(value="Arial")
        font_combo = ttk.Combobox(text_frame, textvariable=self.font_var,
                                values=list(font.families()))
        font_combo.pack(fill=tk.X, padx=2, pady=2)
        
        # Font size
        ttk.Label(text_frame, text="Size:").pack()
        self.font_size_var = tk.IntVar(value=12)
        size_spin = ttk.Spinbox(text_frame, from_=8, to=72, textvariable=self.font_size_var)
        size_spin.pack(fill=tk.X, padx=2, pady=2)
        
        # Image info
        info_frame = ttk.LabelFrame(props_frame, text="Image Info")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.info_label = ttk.Label(info_frame, text="No image loaded")
        self.info_label.pack(padx=5, pady=5)
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def new_image(self):
        """Create a new blank image"""
        self.current_image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.display_image = self.current_image.copy()
        self.update_canvas()
        self.update_info()
        self.save_state()
        self.status_bar.config(text="New image created")
        
    def open_image(self):
        """Open an existing image file"""
        file_path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_image = Image.open(file_path)
                if self.current_image.mode != "RGB":
                    self.current_image = self.current_image.convert("RGB")
                
                # Resize canvas if needed
                img_width, img_height = self.current_image.size
                self.canvas_width = max(img_width, self.canvas_width)
                self.canvas_height = max(img_height, self.canvas_height)
                
                self.display_image = self.current_image.copy()
                self.update_canvas()
                self.update_info()
                self.save_state()
                self.status_bar.config(text=f"Opened: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {str(e)}")
                
    def save_image(self):
        """Save the current image"""
        if not hasattr(self, 'current_file_path'):
            self.save_as_image()
        else:
            try:
                self.current_image.save(self.current_file_path)
                self.status_bar.config(text=f"Saved: {os.path.basename(self.current_file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {str(e)}")
                
    def save_as_image(self):
        """Save the current image with a new name"""
        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_image.save(file_path)
                self.current_file_path = file_path
                self.status_bar.config(text=f"Saved: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {str(e)}")
                
    def update_canvas(self):
        """Update the canvas display"""
        if self.current_image:
            # Convert PIL image to PhotoImage for display
            self.photo_image = ImageTk.PhotoImage(self.display_image)
            
            # Update canvas size
            self.canvas.config(scrollregion=(0, 0, self.display_image.width, self.display_image.height))
            
            # Clear and redraw
            self.canvas.delete("all")
            self.canvas_image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
            
    def update_info(self):
        """Update image information display"""
        if self.current_image:
            width, height = self.current_image.size
            mode = self.current_image.mode
            info_text = f"Size: {width}×{height}\nMode: {mode}"
            self.info_label.config(text=info_text)
        else:
            self.info_label.config(text="No image loaded")
            
    def set_tool(self, tool):
        """Set the current drawing tool"""
        self.current_tool = tool
        self.status_bar.config(text=f"Tool: {tool.title()}")
        
    def choose_color(self):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(color=self.current_color)[1]
        if color:
            self.current_color = color
            self.color_button.config(bg=color)
            
    def update_brush_size(self, value):
        """Update brush size from scale"""
        self.brush_size = int(float(value))
        self.size_label.config(text=f"Size: {self.brush_size}")
        
    def canvas_click(self, event):
        """Handle canvas click events"""
        if not self.current_image:
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.current_tool == "brush":
            self.last_x = x
            self.last_y = y
        elif self.current_tool in ["line", "rectangle", "circle"]:
            self.shape_start = (x, y)
        elif self.current_tool == "text":
            self.add_text(x, y)
        elif self.current_tool == "select":
            self.selection_start = (x, y)
            
    def canvas_drag(self, event):
        """Handle canvas drag events"""
        if not self.current_image:
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.current_tool == "brush" and self.last_x and self.last_y:
            # Draw on the image
            draw = ImageDraw.Draw(self.current_image)
            draw.line([(self.last_x, self.last_y), (x, y)], 
                     fill=self.current_color, width=self.brush_size)
            self.last_x = x
            self.last_y = y
            
            # Update display
            self.display_image = self.current_image.copy()
            self.update_canvas()
            
        elif self.current_tool == "select" and self.selection_start:
            # Update selection rectangle
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
            self.selection_rect = self.canvas.create_rectangle(
                self.selection_start[0], self.selection_start[1], x, y,
                outline="blue", dash=(5, 5))
                
    def canvas_release(self, event):
        """Handle canvas release events"""
        if not self.current_image:
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.current_tool == "brush":
            self.save_state()
        elif self.current_tool in ["line", "rectangle", "circle"] and hasattr(self, 'shape_start'):
            self.draw_shape(self.shape_start, (x, y))
        elif self.current_tool == "select":
            self.selection_end = (x, y)
            
        self.last_x = None
        self.last_y = None
        
    def draw_shape(self, start, end):
        """Draw a shape on the image"""
        draw = ImageDraw.Draw(self.current_image)
        
        if self.current_tool == "line":
            draw.line([start, end], fill=self.current_color, width=self.brush_size)
        elif self.current_tool == "rectangle":
            draw.rectangle([start, end], outline=self.current_color, width=self.brush_size)
        elif self.current_tool == "circle":
            draw.ellipse([start, end], outline=self.current_color, width=self.brush_size)
            
        self.display_image = self.current_image.copy()
        self.update_canvas()
        self.save_state()
        
    def add_text(self, x, y):
        """Add text to the image"""
        text = tk.simpledialog.askstring("Add Text", "Enter text:")
        if text:
            try:
                font_size = self.font_size_var.get()
                font_family = self.font_var.get()
                
                # Try to use the selected font
                try:
                    pil_font = ImageFont.truetype(font_family, font_size)
                except:
                    pil_font = ImageFont.load_default()
                
                draw = ImageDraw.Draw(self.current_image)
                draw.text((x, y), text, fill=self.current_color, font=pil_font)
                
                self.display_image = self.current_image.copy()
                self.update_canvas()
                self.save_state()
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not add text: {str(e)}")
                
    def insert_datetime(self):
        """Insert current date and time"""
        if not self.current_image:
            return
            
        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Position at center of image
        x = self.current_image.width // 2
        y = self.current_image.height // 2
        
        try:
            font_size = self.font_size_var.get()
            font_family = self.font_var.get()
            
            try:
                pil_font = ImageFont.truetype(font_family, font_size)
            except:
                pil_font = ImageFont.load_default()
            
            draw = ImageDraw.Draw(self.current_image)
            draw.text((x, y), datetime_str, fill=self.current_color, font=pil_font)
            
            self.display_image = self.current_image.copy()
            self.update_canvas()
            self.save_state()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not insert date/time: {str(e)}")
            
    def insert_text(self):
        """Insert text at center of image"""
        if not self.current_image:
            return
            
        x = self.current_image.width // 2
        y = self.current_image.height // 2
        self.add_text(x, y)
        
    def copy(self):
        """Copy selected area to clipboard"""
        if self.selection_start and self.selection_end:
            # Get selection bounds
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            
            # Ensure correct order
            left = min(x1, x2)
            right = max(x1, x2)
            top = min(y1, y2)
            bottom = max(y1, y2)
            
            # Crop the selection
            selection = self.current_image.crop((left, top, right, bottom))
            self.clipboard_data = selection
            self.clipboard_type = "image"
            
            self.status_bar.config(text="Selection copied to clipboard")
        else:
            self.status_bar.config(text="No selection to copy")
            
    def paste(self):
        """Paste from clipboard"""
        if self.clipboard_data and self.clipboard_type == "image":
            # Paste at top-left corner for now
            self.current_image.paste(self.clipboard_data, (10, 10))
            self.display_image = self.current_image.copy()
            self.update_canvas()
            self.save_state()
            self.status_bar.config(text="Pasted from clipboard")
        else:
            self.status_bar.config(text="Nothing to paste")
            
    def resize_image(self):
        """Resize the current image"""
        if not self.current_image:
            return
            
        dialog = ResizeDialog(self.root, self.current_image.size)
        if dialog.result:
            new_width, new_height = dialog.result
            self.current_image = self.current_image.resize((new_width, new_height))
            self.display_image = self.current_image.copy()
            self.update_canvas()
            self.update_info()
            self.save_state()
            
    def rotate_image(self, angle):
        """Rotate the image by specified angle"""
        if not self.current_image:
            return
            
        self.current_image = self.current_image.rotate(angle, expand=True)
        self.display_image = self.current_image.copy()
        self.update_canvas()
        self.update_info()
        self.save_state()
        
    def flip_horizontal(self):
        """Flip image horizontally"""
        if not self.current_image:
            return
            
        self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
        self.display_image = self.current_image.copy()
        self.update_canvas()
        self.save_state()
        
    def flip_vertical(self):
        """Flip image vertically"""
        if not self.current_image:
            return
            
        self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
        self.display_image = self.current_image.copy()
        self.update_canvas()
        self.save_state()
        
    def save_state(self):
        """Save current state for undo functionality"""
        if self.current_image:
            # Convert image to bytes for storage
            img_bytes = io.BytesIO()
            self.current_image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            self.undo_stack.append(img_bytes.getvalue())
            
            # Limit undo stack size
            if len(self.undo_stack) > 50:
                self.undo_stack.pop(0)
                
            # Clear redo stack on new action
            self.redo_stack.clear()
            
    def undo(self):
        """Undo last action"""
        if len(self.undo_stack) > 1:  # Keep at least one state
            # Move current state to redo stack
            current_bytes = io.BytesIO()
            self.current_image.save(current_bytes, format='PNG')
            self.redo_stack.append(current_bytes.getvalue())
            
            # Pop last state
            self.undo_stack.pop()
            
            # Restore previous state
            prev_state = self.undo_stack[-1]
            self.current_image = Image.open(io.BytesIO(prev_state))
            self.display_image = self.current_image.copy()
            self.update_canvas()
            self.update_info()
            
            self.status_bar.config(text="Undone")
            
    def redo(self):
        """Redo last undone action"""
        if self.redo_stack:
            # Move current state to undo stack
            current_bytes = io.BytesIO()
            self.current_image.save(current_bytes, format='PNG')
            self.undo_stack.append(current_bytes.getvalue())
            
            # Restore redo state
            redo_state = self.redo_stack.pop()
            self.current_image = Image.open(io.BytesIO(redo_state))
            self.display_image = self.current_image.copy()
            self.update_canvas()
            self.update_info()
            
            self.status_bar.config(text="Redone")


class ResizeDialog:
    def __init__(self, parent, current_size):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title("Resize Image")
        dialog.geometry("300x150")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Current size display
        current_frame = ttk.Frame(dialog)
        current_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(current_frame, text=f"Current size: {current_size[0]} × {current_size[1]}").pack()
        
        # New size inputs
        size_frame = ttk.Frame(dialog)
        size_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(size_frame, text="Width:").grid(row=0, column=0, padx=5)
        self.width_var = tk.IntVar(value=current_size[0])
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(size_frame, text="Height:").grid(row=1, column=0, padx=5)
        self.height_var = tk.IntVar(value=current_size[1])
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=1, column=1, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        
        self.dialog = dialog
        
    def ok_clicked(self):
        try:
            width = self.width_var.get()
            height = self.height_var.get()
            if width > 0 and height > 0:
                self.result = (width, height)
            self.dialog.destroy()
        except:
            pass


def main():
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()