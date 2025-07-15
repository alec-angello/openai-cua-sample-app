#!/usr/bin/env python3
"""
Windows Desktop Automation Example

This script demonstrates how to use the WindowsDesktopComputer class
for automating Windows desktop applications in RDP environments.

Usage:
    python examples/windows_desktop_example.py

Requirements:
    - Windows environment (local or RDP)
    - All dependencies from requirements.txt installed
    - Notepad application available (standard on Windows)
"""

import time
import sys
import os
import base64
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from computers.default.windows_desktop import WindowsDesktopComputer


def save_screenshot(screenshot_b64: str, filename: str):
    """Save a base64 screenshot to a file."""
    try:
        screenshot_data = base64.b64decode(screenshot_b64)
        with open(filename, 'wb') as f:
            f.write(screenshot_data)
        print(f"Screenshot saved to: {filename}")
    except Exception as e:
        print(f"Failed to save screenshot: {e}")


def demonstrate_basic_operations(computer: WindowsDesktopComputer):
    """Demonstrate basic computer operations."""
    print("\n" + "="*50)
    print("BASIC OPERATIONS DEMONSTRATION")
    print("="*50)
    
    # Get screen information
    width, height = computer.get_dimensions()
    print(f"Screen dimensions: {width}x{height}")
    print(f"Environment: {computer.get_environment()}")
    
    # Take initial screenshot
    print("\n1. Taking initial screenshot...")
    screenshot = computer.screenshot()
    save_screenshot(screenshot, "initial_screenshot.jpg")
    
    # Test mouse movement
    print("\n2. Testing mouse movement...")
    center_x, center_y = width // 2, height // 2
    computer.move(center_x, center_y)
    computer.wait(500)
    
    # Test right-click (brings up context menu)
    print("\n3. Testing right-click at center...")
    computer.click(center_x, center_y, "right")
    computer.wait(1000)
    
    # Press Escape to close context menu
    print("   Closing context menu with Escape...")
    computer.keypress(["escape"])
    computer.wait(500)


def demonstrate_application_automation(computer: WindowsDesktopComputer):
    """Demonstrate application launching and automation."""
    print("\n" + "="*50)
    print("APPLICATION AUTOMATION DEMONSTRATION")
    print("="*50)
    
    # Launch Notepad
    print("\n1. Launching Notepad...")
    success = computer.start_application("notepad.exe")
    if not success:
        print("Failed to launch Notepad")
        return
    
    computer.wait(2000)  # Wait for Notepad to open
    
    # Check if Notepad is running
    print("\n2. Checking if Notepad is running...")
    is_running = computer.is_process_running("notepad")
    print(f"Notepad running: {is_running}")
    
    # Get list of windows
    print("\n3. Getting window list...")
    windows = computer.get_window_list()
    print(f"Found {len(windows)} windows:")
    for window in windows[:5]:  # Show first 5 windows
        print(f"  - {window}")
    
    # Find and activate Notepad window
    print("\n4. Activating Notepad window...")
    notepad_activated = False
    for window_title in windows:
        if "notepad" in window_title.lower() or "untitled" in window_title.lower():
            success = computer.activate_window(window_title)
            if success:
                print(f"Activated window: {window_title}")
                notepad_activated = True
                break
    
    if not notepad_activated:
        print("Could not find Notepad window to activate")
        return
    
    computer.wait(1000)
    
    # Type some text
    print("\n5. Typing text in Notepad...")
    sample_text = """Hello from OpenAI CUA Windows Desktop Automation!

This text was typed automatically using the WindowsDesktopComputer class.

Key features demonstrated:
- Application launching
- Window management  
- Text input
- Keyboard shortcuts
- Mouse operations

Current time: """ + time.strftime("%Y-%m-%d %H:%M:%S")
    
    computer.type(sample_text)
    computer.wait(1000)
    
    # Take screenshot of Notepad with content
    print("\n6. Taking screenshot of Notepad...")
    screenshot = computer.screenshot()
    save_screenshot(screenshot, "notepad_with_text.jpg")
    
    # Demonstrate keyboard shortcuts
    print("\n7. Testing keyboard shortcuts...")
    
    # Select all text (Ctrl+A)
    print("   Selecting all text (Ctrl+A)...")
    computer.keypress(["ctrl", "a"])
    computer.wait(500)
    
    # Copy text (Ctrl+C)
    print("   Copying text (Ctrl+C)...")
    computer.keypress(["ctrl", "c"])
    computer.wait(500)
    
    # Go to end of document (Ctrl+End)
    print("   Going to end of document (Ctrl+End)...")
    computer.keypress(["ctrl", "end"])
    computer.wait(500)
    
    # Add a new line and paste
    print("   Adding new line and pasting...")
    computer.keypress(["enter", "enter"])
    computer.type("--- COPIED TEXT ---")
    computer.keypress(["enter"])
    computer.keypress(["ctrl", "v"])
    computer.wait(1000)


def demonstrate_window_management(computer: WindowsDesktopComputer):
    """Demonstrate window management operations."""
    print("\n" + "="*50)
    print("WINDOW MANAGEMENT DEMONSTRATION")
    print("="*50)
    
    # Get current active window
    print("\n1. Getting active window...")
    active_window = computer.get_active_window()
    print(f"Active window: {active_window}")
    
    if "notepad" in active_window.lower() or "untitled" in active_window.lower():
        print("\n2. Managing Notepad window...")
        
        # Minimize window
        print("   Minimizing window...")
        computer.minimize_window(active_window)
        computer.wait(2000)
        
        # Take screenshot with minimized window
        screenshot = computer.screenshot()
        save_screenshot(screenshot, "notepad_minimized.jpg")
        
        # Restore/activate window
        print("   Restoring window...")
        computer.activate_window(active_window)
        computer.wait(1000)
        
        # Maximize window
        print("   Maximizing window...")
        computer.maximize_window(active_window)
        computer.wait(1000)
        
        # Take screenshot of maximized window
        screenshot = computer.screenshot()
        save_screenshot(screenshot, "notepad_maximized.jpg")


def demonstrate_cleanup(computer: WindowsDesktopComputer):
    """Demonstrate cleanup operations."""
    print("\n" + "="*50)
    print("CLEANUP DEMONSTRATION")
    print("="*50)
    
    # Get active window
    active_window = computer.get_active_window()
    
    if "notepad" in active_window.lower() or "untitled" in active_window.lower():
        print("\n1. Closing Notepad without saving...")
        
        # Try to close with Alt+F4
        computer.keypress(["alt", "f4"])
        computer.wait(1000)
        
        # If save dialog appears, click "Don't Save" 
        # (We'll just press 'n' for "No" which is usually the hotkey)
        print("   Handling potential save dialog...")
        computer.keypress(["n"])  # Usually "No" option
        computer.wait(500)
        
        # Alternative: Press Escape to cancel if dialog is still open
        computer.keypress(["escape"])
        computer.wait(500)
    
    # Verify Notepad is closed
    print("\n2. Verifying Notepad is closed...")
    is_running = computer.is_process_running("notepad")
    print(f"Notepad still running: {is_running}")
    
    # Take final screenshot
    print("\n3. Taking final screenshot...")
    screenshot = computer.screenshot()
    save_screenshot(screenshot, "final_screenshot.jpg")


def main():
    """Main demonstration function."""
    print("Windows Desktop Automation Example")
    print("=" * 50)
    print("This script will demonstrate Windows desktop automation")
    print("using the OpenAI CUA WindowsDesktopComputer class.")
    print("\nFeatures to be demonstrated:")
    print("- Basic mouse and keyboard operations")
    print("- Application launching (Notepad)")
    print("- Text input and manipulation")
    print("- Window management")
    print("- Screenshot capture")
    print("- Process monitoring")
    
    # Ask for user confirmation
    response = input("\nContinue with demonstration? (y/n): ").lower().strip()
    if response != 'y':
        print("Demonstration cancelled.")
        return
    
    # Initialize computer with RDP optimization
    print("\nInitializing WindowsDesktopComputer...")
    try:
        with WindowsDesktopComputer(
            action_delay=0.3,        # Moderate delay for RDP
            screenshot_quality=75,    # Good quality for demo
            max_retries=3,           # Retry failed actions
            rdp_mode=True            # Enable RDP optimizations
        ) as computer:
            
            print("Computer initialized successfully!")
            print(f"Screen size: {computer.get_dimensions()}")
            
            # Run demonstrations
            try:
                demonstrate_basic_operations(computer)
                demonstrate_application_automation(computer)
                demonstrate_window_management(computer)
                demonstrate_cleanup(computer)
                
                print("\n" + "="*50)
                print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
                print("="*50)
                print("\nScreenshots saved:")
                screenshots = [
                    "initial_screenshot.jpg",
                    "notepad_with_text.jpg", 
                    "notepad_minimized.jpg",
                    "notepad_maximized.jpg",
                    "final_screenshot.jpg"
                ]
                for screenshot in screenshots:
                    if os.path.exists(screenshot):
                        print(f"  ✓ {screenshot}")
                    else:
                        print(f"  ✗ {screenshot} (not found)")
                
            except KeyboardInterrupt:
                print("\n\nDemonstration interrupted by user.")
            except Exception as e:
                print(f"\nError during demonstration: {e}")
                import traceback
                traceback.print_exc()
            
    except Exception as e:
        print(f"Failed to initialize computer: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 