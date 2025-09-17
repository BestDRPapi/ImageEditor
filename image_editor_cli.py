#!/usr/bin/env python3
"""
Command-Line Image Editor
A comprehensive image editing application with drawing tools, text editing, 
and basic image manipulation capabilities.
"""

import os
import json
import sys
from datetime import datetime
from typing import List, Dict, Any, Tuple


class Canvas:
    """Represents a drawing canvas with ASCII art capabilities"""
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        self.objects = []
        self.colors = {
            'black': '█',
            'gray': '▓',
            'light': '▒',
            'dot': '░',
            'white': ' ',
            'x': 'X',
            'o': 'O',
            '*': '*',
            '+': '+',
            '#': '#'
        }
        
    def clear(self):
        """Clear the canvas"""
        self.grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.objects.clear()
        
    def set_pixel(self, x: int, y: int, char: str = '█'):
        """Set a pixel on the canvas"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = char
            
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, char: str = '█'):
        """Draw a line using Bresenham's algorithm"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        if dx > dy:
            err = dx / 2.0
            while x != x2:
                self.set_pixel(x, y, char)
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                self.set_pixel(x, y, char)
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        self.set_pixel(x, y, char)
        
    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int, char: str = '█', filled: bool = False):
        """Draw a rectangle"""
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        
        if filled:
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    self.set_pixel(x, y, char)
        else:
            # Draw borders
            for x in range(min_x, max_x + 1):
                self.set_pixel(x, min_y, char)
                self.set_pixel(x, max_y, char)
            for y in range(min_y, max_y + 1):
                self.set_pixel(min_x, y, char)
                self.set_pixel(max_x, y, char)
                
    def draw_circle(self, cx: int, cy: int, radius: int, char: str = '█', filled: bool = False):
        """Draw a circle using midpoint algorithm"""
        if filled:
            for y in range(max(0, cy - radius), min(self.height, cy + radius + 1)):
                for x in range(max(0, cx - radius), min(self.width, cx + radius + 1)):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                        self.set_pixel(x, y, char)
        else:
            x = 0
            y = radius
            d = 3 - 2 * radius
            
            while y >= x:
                # Draw the 8 octants
                points = [
                    (cx + x, cy + y), (cx - x, cy + y),
                    (cx + x, cy - y), (cx - x, cy - y),
                    (cx + y, cy + x), (cx - y, cy + x),
                    (cx + y, cy - x), (cx - y, cy - x)
                ]
                for px, py in points:
                    self.set_pixel(px, py, char)
                    
                if d < 0:
                    d = d + 4 * x + 6
                else:
                    d = d + 4 * (x - y) + 10
                    y -= 1
                x += 1
                
    def draw_text(self, x: int, y: int, text: str):
        """Draw text on the canvas"""
        for i, char in enumerate(text):
            if x + i < self.width and 0 <= y < self.height:
                self.set_pixel(x + i, y, char)
                
    def display(self):
        """Display the canvas"""
        print("+" + "-" * self.width + "+")
        for row in self.grid:
            print("|" + "".join(row) + "|")
        print("+" + "-" * self.width + "+")
        
    def save_to_file(self, filename: str):
        """Save canvas to text file"""
        with open(filename, 'w') as f:
            for row in self.grid:
                f.write("".join(row) + "\n")
                
    def export_data(self, filename: str):
        """Export canvas data as JSON"""
        data = {
            "width": self.width,
            "height": self.height,
            "objects": self.objects,
            "grid": self.grid
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)


class ImageEditor:
    """Main image editor class"""
    
    def __init__(self):
        self.canvas = Canvas()
        self.current_color = 'black'
        self.current_char = '█'
        self.clipboard = []
        self.undo_stack = []
        self.redo_stack = []
        self.running = True
        
    def save_state(self):
        """Save current state for undo"""
        state = {
            "grid": [row[:] for row in self.canvas.grid],
            "objects": self.canvas.objects[:]
        }
        self.undo_stack.append(state)
        if len(self.undo_stack) > 20:  # Limit undo stack
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        
    def undo(self):
        """Undo last action"""
        if len(self.undo_stack) > 1:
            current_state = {
                "grid": [row[:] for row in self.canvas.grid],
                "objects": self.canvas.objects[:]
            }
            self.redo_stack.append(current_state)
            
            self.undo_stack.pop()
            prev_state = self.undo_stack[-1]
            
            self.canvas.grid = [row[:] for row in prev_state["grid"]]
            self.canvas.objects = prev_state["objects"][:]
            print("Undone!")
            
    def redo(self):
        """Redo last undone action"""
        if self.redo_stack:
            current_state = {
                "grid": [row[:] for row in self.canvas.grid],
                "objects": self.canvas.objects[:]
            }
            self.undo_stack.append(current_state)
            
            redo_state = self.redo_stack.pop()
            self.canvas.grid = [row[:] for row in redo_state["grid"]]
            self.canvas.objects = redo_state["objects"][:]
            print("Redone!")
            
    def show_help(self):
        """Display help information"""
        help_text = """
╔═══════════════════════════════════════════════════════════════════╗
║                        IMAGE EDITOR COMMANDS                     ║
╠═══════════════════════════════════════════════════════════════════╣
║ Canvas Operations:                                                ║
║   new [width] [height]  - Create new canvas (default: 80x24)     ║
║   clear                 - Clear the canvas                        ║
║   display               - Show the current canvas                 ║
║   resize <width> <height> - Resize canvas                         ║
║                                                                   ║
║ Drawing Tools:                                                    ║
║   pixel <x> <y>         - Set a pixel                            ║
║   line <x1> <y1> <x2> <y2> - Draw a line                        ║
║   rect <x1> <y1> <x2> <y2> - Draw rectangle                     ║
║   fillrect <x1> <y1> <x2> <y2> - Draw filled rectangle          ║
║   circle <cx> <cy> <radius> - Draw circle                       ║
║   fillcircle <cx> <cy> <radius> - Draw filled circle            ║
║   text <x> <y> <text>   - Add text                               ║
║                                                                   ║
║ Text & Date:                                                      ║
║   datetime <x> <y>      - Insert current date/time               ║
║   bigtext <x> <y> <text> - Add large ASCII art text             ║
║                                                                   ║
║ Colors & Characters:                                              ║
║   color <name>          - Set drawing color/character            ║
║                          (black, gray, light, dot, white, x, o,  ║
║                           *, +, #, or any single character)      ║
║   colors                - Show available color options           ║
║                                                                   ║
║ Edit Operations:                                                  ║
║   undo                  - Undo last action                        ║
║   redo                  - Redo last undone action                 ║
║   copy <x1> <y1> <x2> <y2> - Copy region to clipboard           ║
║   paste <x> <y>         - Paste from clipboard                   ║
║                                                                   ║
║ File Operations:                                                  ║
║   save <filename>       - Save canvas to text file               ║
║   export <filename>     - Export canvas data as JSON             ║
║   load <filename>       - Load canvas from JSON file             ║
║                                                                   ║
║ Other:                                                            ║
║   help                  - Show this help                         ║
║   quit                  - Exit the editor                        ║
╚═══════════════════════════════════════════════════════════════════╝
        """
        print(help_text)
        
    def show_colors(self):
        """Show available colors"""
        print("\nAvailable colors/characters:")
        for name, char in self.canvas.colors.items():
            print(f"  {name:10} -> '{char}'")
        print("\nYou can also use any single character directly.")
        print(f"Current color: {self.current_color} ('{self.current_char}')")
        
    def draw_big_text(self, x: int, y: int, text: str):
        """Draw large ASCII art text"""
        # Simple 3x5 font patterns
        patterns = {
            'A': [
                " ██ ",
                "█  █",
                "████",
                "█  █",
                "█  █"
            ],
            'B': [
                "███ ",
                "█  █",
                "███ ",
                "█  █",
                "███ "
            ],
            'C': [
                " ███",
                "█   ",
                "█   ",
                "█   ",
                " ███"
            ],
            'H': [
                "█  █",
                "█  █",  
                "████",
                "█  █",
                "█  █"
            ],
            'E': [
                "████",
                "█   ",
                "███ ",
                "█   ",
                "████"
            ],
            'L': [
                "█   ",
                "█   ",
                "█   ",
                "█   ",
                "████"
            ],
            'O': [
                " ██ ",
                "█  █",
                "█  █",
                "█  █",
                " ██ "
            ],
            ' ': [
                "    ",
                "    ",
                "    ",
                "    ",
                "    "
            ]
        }
        
        char_width = 4
        char_height = 5
        
        for i, char in enumerate(text.upper()):
            if char in patterns:
                pattern = patterns[char]
                for row in range(char_height):
                    for col in range(len(pattern[row])):
                        if pattern[row][col] != ' ':
                            self.canvas.set_pixel(
                                x + i * char_width + col,
                                y + row,
                                self.current_char
                            )
                            
    def process_command(self, command: str):
        """Process a user command"""
        parts = command.strip().split()
        if not parts:
            return
            
        cmd = parts[0].lower()
        
        try:
            if cmd == "help":
                self.show_help()
                
            elif cmd == "quit" or cmd == "exit":
                self.running = False
                print("Goodbye!")
                
            elif cmd == "new":
                width = int(parts[1]) if len(parts) > 1 else 80
                height = int(parts[2]) if len(parts) > 2 else 24
                self.save_state()
                self.canvas = Canvas(width, height)
                print(f"Created new canvas: {width}x{height}")
                
            elif cmd == "clear":
                self.save_state()
                self.canvas.clear()
                print("Canvas cleared")
                
            elif cmd == "display":
                self.canvas.display()
                
            elif cmd == "resize":
                if len(parts) < 3:
                    print("Usage: resize <width> <height>")
                    return
                width, height = int(parts[1]), int(parts[2])
                self.save_state()
                new_canvas = Canvas(width, height)
                # Copy existing content
                for y in range(min(height, self.canvas.height)):
                    for x in range(min(width, self.canvas.width)):
                        new_canvas.set_pixel(x, y, self.canvas.grid[y][x])
                self.canvas = new_canvas
                print(f"Canvas resized to {width}x{height}")
                
            elif cmd == "pixel":
                if len(parts) < 3:
                    print("Usage: pixel <x> <y>")
                    return
                x, y = int(parts[1]), int(parts[2])
                self.save_state()
                self.canvas.set_pixel(x, y, self.current_char)
                print(f"Pixel set at ({x}, {y})")
                
            elif cmd == "line":
                if len(parts) < 5:
                    print("Usage: line <x1> <y1> <x2> <y2>")
                    return
                x1, y1, x2, y2 = map(int, parts[1:5])
                self.save_state()
                self.canvas.draw_line(x1, y1, x2, y2, self.current_char)
                print(f"Line drawn from ({x1}, {y1}) to ({x2}, {y2})")
                
            elif cmd == "rect":
                if len(parts) < 5:
                    print("Usage: rect <x1> <y1> <x2> <y2>")
                    return
                x1, y1, x2, y2 = map(int, parts[1:5])
                self.save_state()
                self.canvas.draw_rectangle(x1, y1, x2, y2, self.current_char, False)
                print(f"Rectangle drawn from ({x1}, {y1}) to ({x2}, {y2})")
                
            elif cmd == "fillrect":
                if len(parts) < 5:
                    print("Usage: fillrect <x1> <y1> <x2> <y2>")
                    return
                x1, y1, x2, y2 = map(int, parts[1:5])
                self.save_state()
                self.canvas.draw_rectangle(x1, y1, x2, y2, self.current_char, True)
                print(f"Filled rectangle drawn from ({x1}, {y1}) to ({x2}, {y2})")
                
            elif cmd == "circle":
                if len(parts) < 4:
                    print("Usage: circle <cx> <cy> <radius>")
                    return
                cx, cy, radius = int(parts[1]), int(parts[2]), int(parts[3])
                self.save_state()
                self.canvas.draw_circle(cx, cy, radius, self.current_char, False)
                print(f"Circle drawn at ({cx}, {cy}) with radius {radius}")
                
            elif cmd == "fillcircle":
                if len(parts) < 4:
                    print("Usage: fillcircle <cx> <cy> <radius>")
                    return
                cx, cy, radius = int(parts[1]), int(parts[2]), int(parts[3])
                self.save_state()
                self.canvas.draw_circle(cx, cy, radius, self.current_char, True)
                print(f"Filled circle drawn at ({cx}, {cy}) with radius {radius}")
                
            elif cmd == "text":
                if len(parts) < 4:
                    print("Usage: text <x> <y> <text>")
                    return
                x, y = int(parts[1]), int(parts[2])
                text = " ".join(parts[3:])
                self.save_state()
                self.canvas.draw_text(x, y, text)
                print(f"Text '{text}' added at ({x}, {y})")
                
            elif cmd == "bigtext":
                if len(parts) < 4:
                    print("Usage: bigtext <x> <y> <text>")
                    return
                x, y = int(parts[1]), int(parts[2])
                text = " ".join(parts[3:])
                self.save_state()
                self.draw_big_text(x, y, text)
                print(f"Big text '{text}' added at ({x}, {y})")
                
            elif cmd == "datetime":
                if len(parts) < 3:
                    print("Usage: datetime <x> <y>")
                    return
                x, y = int(parts[1]), int(parts[2])
                datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_state()
                self.canvas.draw_text(x, y, datetime_str)
                print(f"Date/time '{datetime_str}' added at ({x}, {y})")
                
            elif cmd == "color":
                if len(parts) < 2:
                    print("Usage: color <color_name_or_character>")
                    return
                color = parts[1]
                if color in self.canvas.colors:
                    self.current_color = color
                    self.current_char = self.canvas.colors[color]
                elif len(color) == 1:
                    self.current_color = color
                    self.current_char = color
                else:
                    print(f"Unknown color: {color}")
                    return
                print(f"Color set to: {self.current_color} ('{self.current_char}')")
                
            elif cmd == "colors":
                self.show_colors()
                
            elif cmd == "copy":
                if len(parts) < 5:
                    print("Usage: copy <x1> <y1> <x2> <y2>")
                    return
                x1, y1, x2, y2 = map(int, parts[1:5])
                min_x, max_x = min(x1, x2), max(x1, x2)
                min_y, max_y = min(y1, y2), max(y1, y2)
                
                self.clipboard = []
                for y in range(min_y, max_y + 1):
                    row = []
                    for x in range(min_x, max_x + 1):
                        if 0 <= x < self.canvas.width and 0 <= y < self.canvas.height:
                            row.append(self.canvas.grid[y][x])
                        else:
                            row.append(' ')
                    self.clipboard.append(row)
                print(f"Copied region ({x1}, {y1}) to ({x2}, {y2})")
                
            elif cmd == "paste":
                if len(parts) < 3:
                    print("Usage: paste <x> <y>")
                    return
                if not self.clipboard:
                    print("Nothing to paste")
                    return
                x, y = int(parts[1]), int(parts[2])
                self.save_state()
                for row_idx, row in enumerate(self.clipboard):
                    for col_idx, char in enumerate(row):
                        self.canvas.set_pixel(x + col_idx, y + row_idx, char)
                print(f"Pasted at ({x}, {y})")
                
            elif cmd == "undo":
                self.undo()
                
            elif cmd == "redo":
                self.redo()
                
            elif cmd == "save":
                if len(parts) < 2:
                    print("Usage: save <filename>")
                    return
                filename = parts[1]
                self.canvas.save_to_file(filename)
                print(f"Canvas saved to {filename}")
                
            elif cmd == "export":
                if len(parts) < 2:
                    print("Usage: export <filename>")
                    return
                filename = parts[1]
                self.canvas.export_data(filename)
                print(f"Canvas data exported to {filename}")
                
            elif cmd == "load":
                if len(parts) < 2:
                    print("Usage: load <filename>")
                    return
                filename = parts[1]
                try:
                    with open(filename, 'r') as f:
                        data = json.load(f)
                    self.save_state()
                    self.canvas = Canvas(data["width"], data["height"])
                    self.canvas.grid = data["grid"]
                    self.canvas.objects = data.get("objects", [])
                    print(f"Canvas loaded from {filename}")
                except Exception as e:
                    print(f"Error loading file: {e}")
                    
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands")
                
        except (ValueError, IndexError) as e:
            print(f"Error: Invalid command format. Type 'help' for usage.")
        except Exception as e:
            print(f"Error: {e}")
    
    def run(self):
        """Main editor loop"""
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                        ASCII ART IMAGE EDITOR                       ║")
        print("║                                                                      ║")
        print("║  A full-featured command-line image editor with drawing tools,      ║")
        print("║  text insertion, shape manipulation, copy/paste, and more!          ║")
        print("║                                                                      ║")
        print("║  Type 'help' for commands or 'display' to see the current canvas    ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print()
        
        # Save initial state
        self.save_state()
        
        while self.running:
            try:
                command = input("editor> ").strip()
                if command:
                    self.process_command(command)
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except EOFError:
                break
                
        return 0


def main():
    """Main entry point"""
    editor = ImageEditor()
    return editor.run()


if __name__ == "__main__":
    sys.exit(main())