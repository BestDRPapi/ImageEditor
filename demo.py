#!/usr/bin/env python3
"""
Demo script for the Image Editor functionality
"""

from image_editor_cli import ImageEditor, Canvas
from datetime import datetime

def demo_drawing():
    """Demonstrate drawing capabilities"""
    print("=== IMAGE EDITOR DEMO ===\n")
    
    # Create editor and canvas
    editor = ImageEditor()
    
    print("1. Creating a new canvas (40x20)...")
    editor.canvas = Canvas(40, 20)
    editor.canvas.display()
    
    print("\n2. Drawing shapes...")
    
    # Draw a rectangle
    editor.canvas.draw_rectangle(5, 3, 15, 8, '█', False)
    print("   - Rectangle drawn")
    
    # Draw a filled circle
    editor.canvas.draw_circle(25, 6, 4, '▓', True)
    print("   - Filled circle drawn")
    
    # Draw some lines
    editor.canvas.draw_line(2, 12, 37, 12, '─')
    editor.canvas.draw_line(2, 14, 37, 16, '*')
    print("   - Lines drawn")
    
    editor.canvas.display()
    
    print("\n3. Adding text and date/time...")
    
    # Add regular text
    editor.canvas.draw_text(6, 5, "HELLO")
    
    # Add date/time
    datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    editor.canvas.draw_text(5, 18, datetime_str)
    
    editor.canvas.display()
    
    print("\n4. Demonstrating different characters/colors...")
    
    # Create a new smaller canvas for color demo
    color_canvas = Canvas(30, 10)
    
    chars = ['█', '▓', '▒', '░', 'X', 'O', '*', '+', '#']
    for i, char in enumerate(chars):
        color_canvas.draw_rectangle(i*3, 1, i*3+2, 3, char, True)
        color_canvas.draw_text(i*3, 5, char)
        
    print("Color/Character palette:")
    color_canvas.display()
    
    print("\n5. Copy and paste demonstration...")
    
    # Copy a region (the rectangle we drew)
    copied_region = []
    for y in range(3, 9):  # Rectangle area
        row = []
        for x in range(5, 16):
            row.append(editor.canvas.grid[y][x])
        copied_region.append(row)
    
    # Paste it elsewhere
    for row_idx, row in enumerate(copied_region):
        for col_idx, char in enumerate(row):
            editor.canvas.set_pixel(20 + col_idx, 2 + row_idx, char)
    
    print("   - Copied and pasted rectangle")
    editor.canvas.display()
    
    print("\n6. Saving canvas to file...")
    editor.canvas.save_to_file("demo_output.txt")
    print("   - Canvas saved to 'demo_output.txt'")
    
    print("\n7. Exporting canvas data...")
    editor.canvas.export_data("demo_output.json")
    print("   - Canvas data exported to 'demo_output.json'")
    
    return editor

def demo_big_text():
    """Demonstrate big text functionality"""
    print("\n=== BIG TEXT DEMO ===\n")
    
    editor = ImageEditor()
    editor.canvas = Canvas(60, 15)
    
    # Draw big text
    editor.draw_big_text(5, 2, "HELLO")
    editor.draw_big_text(5, 8, "BIG TEXT")
    
    print("Big ASCII art text:")
    editor.canvas.display()
    
    return editor

def main():
    """Run the demo"""
    try:
        # Basic drawing demo
        editor1 = demo_drawing()
        
        # Big text demo  
        editor2 = demo_big_text()
        
        print("\n=== FEATURE SUMMARY ===")
        print("✓ Drawing tools: lines, rectangles, circles (filled and outlined)")
        print("✓ Text insertion with various fonts/characters")
        print("✓ Date and time insertion")
        print("✓ Multiple colors/characters support")
        print("✓ Copy and paste functionality")
        print("✓ Undo/redo system (20 levels)")
        print("✓ File save/load (text and JSON formats)")
        print("✓ Canvas resizing and manipulation")
        print("✓ Big ASCII art text rendering")
        print("✓ Interactive command-line interface")
        
        print("\n=== FILES CREATED ===")
        print("- image_editor.py: Full GUI version (requires Pillow)")
        print("- image_editor_simple.py: Simplified GUI version (tkinter only)")
        print("- image_editor_cli.py: Command-line version (no dependencies)")
        print("- demo_output.txt: Sample canvas output")
        print("- demo_output.json: Sample canvas data export")
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"Demo error: {e}")

if __name__ == "__main__":
    main()