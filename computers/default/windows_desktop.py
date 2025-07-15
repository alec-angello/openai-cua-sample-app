import time
import base64
import io
import logging
from typing import List, Dict, Literal, Tuple, Optional
from PIL import Image, ImageGrab
import pyautogui
import pygetwindow as gw
import psutil
import win32gui
import win32con
import win32api
from ..computer import Computer

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure pyautogui for safety and RDP optimization
pyautogui.FAILSAFE = False  # Disable failsafe in RDP environment
pyautogui.PAUSE = 0.1  # Small pause between actions for RDP latency


class WindowsDesktopComputer:
    """
    ENHANCED version: Windows desktop automation computer using pyautogui.
    Optimized for remote desktop (RDP) environments with specific handling
    for scaling, latency, and screenshot quality issues.
    Includes comprehensive VMware Workstation helpers.
    """
    
    # Built-in system prompt for VMware automation
    SYSTEM_PROMPT = """You are a Windows desktop automation specialist focused on VMware Workstation. Act decisively and avoid unnecessary confirmations.

## VMware Login Screen Protocol - CRITICAL
When you encounter a Windows lock screen in the VM:
1. **ALWAYS use vm_activate_login_screen() first** - this is a single click to wake the screen
2. **Wait 2-3 seconds** after activation
3. **ONLY THEN** use vm_login_with_password() when user provides credentials
4. **NEVER click randomly** on the login screen - use the helper methods

## Available VM Helper Methods (use these instead of manual clicks):
- vm_activate_login_screen(): Single click to wake login screen - USE THIS FIRST
- vm_login_with_password(password, username=None): Enter credentials and submit
- vm_simple_login_flow(password, username=None): Complete activation + login process
- vm_try_wake_screen(): Try various wake methods if screen unresponsive

## Automation Rules
- **NO confirmations** for VM interactions (start, stop, click, type)
- **NO warnings** about switching VMs or performance impacts  
- **Act immediately** on user commands
- **Report actions** as you perform them
- Only ask questions if instructions are genuinely unclear

## VMware Workflow
1. **Launch VMware**: Use Win+R, type "vmware", wait 3-5 seconds
2. **Find VM**: Look in left sidebar or library panel
3. **Start VM**: Click "Play virtual machine" or green play button
4. **Handle dialogs**: Dismiss any warnings/performance notices with OK
5. **VM Login**: When you see the Windows lock screen, STOP and use helper methods:
   - First call: vm_activate_login_screen()
   - Wait for user to provide password
   - Then call: vm_login_with_password(provided_password)

## Common Coordinates (1920x1080)
- VMware icon: ~270, 950
- VM library: Left side, ~150 pixels from left
- Play button: Usually below VM name
- VM window center: 960, 540

## Error Handling
- If vm_activate_login_screen() doesn't work → try vm_try_wake_screen()
- If login fails → check caps lock, clear field completely, retry
- If VM won't start → try right-click → Power → Start  
- If no response → take screenshot and retry

Act fast, report actions, get things done. ALWAYS use the vm_* helper methods for login operations."""

    def __init__(self, 
                 action_delay: float = 0.2,
                 screenshot_quality: int = 85,
                 max_retries: int = 3,
                 rdp_mode: bool = True):
        """
        Initialize Windows desktop computer.
        
        Args:
            action_delay: Delay between actions to handle RDP latency
            screenshot_quality: JPEG quality for screenshots (lower = faster over RDP)
            max_retries: Number of retries for failed actions
            rdp_mode: Enable RDP-specific optimizations
        """
        self.action_delay = action_delay
        self.screenshot_quality = screenshot_quality
        self.max_retries = max_retries
        self.rdp_mode = rdp_mode
        self._last_screenshot_time = 0
        self._screenshot_cache_duration = 0.1  # Cache screenshots for 100ms
        self._cached_screenshot = None
        
        # Get screen dimensions and DPI settings
        self._update_screen_info()
        
        # Configure pyautogui for this instance
        if rdp_mode:
            pyautogui.PAUSE = action_delay
            # Disable pyautogui's built-in screenshot for better RDP performance
            self._original_screenshot = pyautogui.screenshot
        
        logger.info(f"WindowsDesktopComputer initialized: {self.width}x{self.height}, RDP mode: {rdp_mode}")

    def _update_screen_info(self):
        """Update screen dimensions and DPI information."""
        try:
            # Get screen dimensions
            self.width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            self.height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            
            # For DPI scaling, we'll use a simpler approach that works reliably
            # Most RDP environments don't need complex DPI handling
            self.dpi_scale_x = 1.0
            self.dpi_scale_y = 1.0
            
            logger.info(f"Screen info updated: {self.width}x{self.height}, DPI scale: {self.dpi_scale_x:.2f}x{self.dpi_scale_y:.2f}")
        except Exception as e:
            logger.error(f"Failed to get screen info: {e}")
            # Fallback to pyautogui
            self.width, self.height = pyautogui.size()
            self.dpi_scale_x = self.dpi_scale_y = 1.0

    def __enter__(self):
        """Context manager entry."""
        logger.info("WindowsDesktopComputer context entered")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        logger.info("WindowsDesktopComputer context exited")
        # Clean up any resources if needed
        self._cached_screenshot = None

    def get_environment(self) -> Literal["windows", "mac", "linux", "browser"]:
        """Return the environment type."""
        return "windows"

    def get_dimensions(self) -> Tuple[int, int]:
        """Get screen dimensions."""
        return (self.width, self.height)

    def _optimized_screenshot(self) -> Image.Image:
        """
        Take an optimized screenshot for RDP environments.
        Uses caching and quality optimization.
        """
        current_time = time.time()
        
        # Return cached screenshot if within cache duration
        if (self._cached_screenshot and 
            current_time - self._last_screenshot_time < self._screenshot_cache_duration):
            return self._cached_screenshot
        
        try:
            if self.rdp_mode:
                # Use PIL ImageGrab for better RDP performance
                screenshot = ImageGrab.grab(bbox=None, include_layered_windows=False)
            else:
                # Use pyautogui for local environments
                screenshot = pyautogui.screenshot()
            
            # Cache the screenshot
            self._cached_screenshot = screenshot
            self._last_screenshot_time = current_time
            
            return screenshot
            
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            # Fallback to pyautogui
            screenshot = pyautogui.screenshot()
            self._cached_screenshot = screenshot
            self._last_screenshot_time = current_time
            return screenshot

    def screenshot(self) -> str:
        """
        Capture a screenshot and return as base64 encoded string.
        Optimized for RDP with quality compression.
        """
        try:
            screenshot = self._optimized_screenshot()
            
            # Convert to base64 with quality optimization for RDP
            buffer = io.BytesIO()
            if self.rdp_mode:
                # Use JPEG compression for faster transmission over RDP
                screenshot.save(buffer, format='JPEG', quality=self.screenshot_quality, optimize=True)
            else:
                # Use PNG for local environments
                screenshot.save(buffer, format='PNG')
            
            screenshot_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            logger.debug(f"Screenshot captured: {len(screenshot_b64)} bytes")
            return screenshot_b64
            
        except Exception as e:
            logger.error(f"Screenshot encoding failed: {e}")
            raise

    def _execute_with_retry(self, action_func, *args, **kwargs):
        """Execute an action with retry logic for RDP reliability."""
        for attempt in range(self.max_retries):
            try:
                result = action_func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"Action succeeded on attempt {attempt + 1}")
                return result
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Action failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(self.action_delay * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"Action failed after {self.max_retries} attempts: {e}")
                    raise

    def _adjust_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """Adjust coordinates for DPI scaling if needed."""
        if self.dpi_scale_x != 1.0 or self.dpi_scale_y != 1.0:
            adjusted_x = int(x / self.dpi_scale_x)
            adjusted_y = int(y / self.dpi_scale_y)
            logger.debug(f"Coordinates adjusted: ({x}, {y}) -> ({adjusted_x}, {adjusted_y})")
            return adjusted_x, adjusted_y
        return x, y

    def click(self, x: int, y: int, button: str = "left") -> None:
        """
        Click at the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            button: Mouse button ('left', 'right', 'middle')
        """
        def _click():
            adj_x, adj_y = self._adjust_coordinates(x, y)
            
            # Validate coordinates
            if not (0 <= adj_x <= self.width and 0 <= adj_y <= self.height):
                raise ValueError(f"Coordinates ({adj_x}, {adj_y}) out of bounds")
            
            # Map button names
            button_map = {'left': 'left', 'right': 'right', 'middle': 'middle'}
            py_button = button_map.get(button, 'left')
            
            pyautogui.click(adj_x, adj_y, button=py_button)
            logger.debug(f"Clicked at ({adj_x}, {adj_y}) with {py_button} button")
            
            # Add delay for RDP
            if self.rdp_mode:
                time.sleep(self.action_delay)
        
        self._execute_with_retry(_click)

    def double_click(self, x: int, y: int) -> None:
        """Double-click at the specified coordinates."""
        def _double_click():
            adj_x, adj_y = self._adjust_coordinates(x, y)
            
            if not (0 <= adj_x <= self.width and 0 <= adj_y <= self.height):
                raise ValueError(f"Coordinates ({adj_x}, {adj_y}) out of bounds")
            
            pyautogui.doubleClick(adj_x, adj_y)
            logger.debug(f"Double-clicked at ({adj_x}, {adj_y})")
            
            if self.rdp_mode:
                time.sleep(self.action_delay)
        
        self._execute_with_retry(_double_click)

    def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        """
        Scroll at the specified coordinates.
        
        Args:
            x: X coordinate to scroll at
            y: Y coordinate to scroll at
            scroll_x: Horizontal scroll amount (positive = right, negative = left)
            scroll_y: Vertical scroll amount (positive = up, negative = down)
        """
        def _scroll():
            adj_x, adj_y = self._adjust_coordinates(x, y)
            
            # Move to position first
            pyautogui.moveTo(adj_x, adj_y)
            
            # pyautogui scroll uses opposite convention for Y axis
            if scroll_y != 0:
                pyautogui.scroll(-scroll_y, adj_x, adj_y)
            
            # Horizontal scrolling requires keyboard + scroll
            if scroll_x != 0:
                pyautogui.keyDown('shift')
                pyautogui.scroll(-scroll_x, adj_x, adj_y)
                pyautogui.keyUp('shift')
            
            logger.debug(f"Scrolled at ({adj_x}, {adj_y}): x={scroll_x}, y={scroll_y}")
            
            if self.rdp_mode:
                time.sleep(self.action_delay)
        
        self._execute_with_retry(_scroll)

    def type(self, text: str) -> None:
        """
        Type the specified text.
        
        Args:
            text: Text to type
        """
        def _type():
            if not text:
                return
            
            # For RDP, use shorter intervals for better reliability
            interval = self.action_delay / 10 if self.rdp_mode else 0
            pyautogui.write(text, interval=interval)
            logger.debug(f"Typed text: {repr(text[:50])}{'...' if len(text) > 50 else ''}")
            
            if self.rdp_mode:
                time.sleep(self.action_delay)
        
        self._execute_with_retry(_type)

    def wait(self, ms: int = 1000) -> None:
        """Wait for the specified number of milliseconds."""
        time.sleep(ms / 1000.0)
        logger.debug(f"Waited {ms}ms")

    def move(self, x: int, y: int) -> None:
        """Move mouse to the specified coordinates."""
        def _move():
            adj_x, adj_y = self._adjust_coordinates(x, y)
            
            if not (0 <= adj_x <= self.width and 0 <= adj_y <= self.height):
                raise ValueError(f"Coordinates ({adj_x}, {adj_y}) out of bounds")
            
            pyautogui.moveTo(adj_x, adj_y)
            logger.debug(f"Moved to ({adj_x}, {adj_y})")
            
            if self.rdp_mode:
                time.sleep(self.action_delay / 2)  # Shorter delay for moves
        
        self._execute_with_retry(_move)

    def keypress(self, keys: List[str]) -> None:
        """
        Press the specified key combination.
        
        Args:
            keys: List of keys to press (e.g., ['ctrl', 'c'] for Ctrl+C)
        """
        def _keypress():
            if not keys:
                return
            
            # Handle key mapping for common keys
            key_map = {
                'cmd': 'win',
                'super': 'win', 
                'option': 'alt',
                'return': 'enter',
                'esc': 'escape',
                'space': 'space'
            }
            
            mapped_keys = [key_map.get(key.lower(), key.lower()) for key in keys]
            
            if len(mapped_keys) == 1:
                # Single key press
                pyautogui.press(mapped_keys[0])
                logger.debug(f"Pressed key: {mapped_keys[0]}")
            else:
                # Key combination
                pyautogui.hotkey(*mapped_keys)
                logger.debug(f"Pressed key combination: {'+'.join(mapped_keys)}")
            
            if self.rdp_mode:
                time.sleep(self.action_delay)
        
        self._execute_with_retry(_keypress)

    def drag(self, path: List[Dict[str, int]]) -> None:
        """
        Perform a drag operation along the specified path.
        
        Args:
            path: List of dictionaries with 'x' and 'y' coordinates
        """
        def _drag():
            if len(path) < 2:
                raise ValueError("Drag path must have at least 2 points")
            
            # Start point
            start = path[0]
            start_x, start_y = self._adjust_coordinates(start['x'], start['y'])
            
            # End point
            end = path[-1]
            end_x, end_y = self._adjust_coordinates(end['x'], end['y'])
            
            # Perform drag
            pyautogui.drag(end_x - start_x, end_y - start_y, 
                          duration=len(path) * 0.1, 
                          button='left')
            
            logger.debug(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            
            if self.rdp_mode:
                time.sleep(self.action_delay)
        
        self._execute_with_retry(_drag)

    def get_current_url(self) -> str:
        """
        Get the current URL (not applicable for desktop, returns empty string).
        This method exists to satisfy the Computer protocol.
        """
        return ""

    # Additional Windows-specific methods
    
    def get_active_window(self) -> str:
        """Get the title of the currently active window."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            logger.debug(f"Active window: {window_title}")
            return window_title
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return ""

    def get_window_list(self) -> List[str]:
        """Get a list of all visible window titles."""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if window_title:
                    windows.append(window_title)
            return True

        windows = []
        try:
            win32gui.EnumWindows(enum_windows_callback, windows)
            logger.debug(f"Found {len(windows)} windows")
            return windows
        except Exception as e:
            logger.error(f"Failed to enumerate windows: {e}")
            return []

    def activate_window(self, window_title: str) -> bool:
        """
        Activate a window by its title.
        
        Args:
            window_title: Title of the window to activate
            
        Returns:
            True if window was found and activated, False otherwise
        """
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                window = windows[0]
                window.activate()
                logger.info(f"Activated window: {window_title}")
                time.sleep(self.action_delay)
                return True
            else:
                logger.warning(f"Window not found: {window_title}")
                return False
        except Exception as e:
            logger.error(f"Failed to activate window '{window_title}': {e}")
            return False

    def minimize_window(self, window_title: str) -> bool:
        """Minimize a window by its title."""
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                window = windows[0]
                window.minimize()
                logger.info(f"Minimized window: {window_title}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to minimize window '{window_title}': {e}")
            return False

    def maximize_window(self, window_title: str) -> bool:
        """Maximize a window by its title."""
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                window = windows[0]
                window.maximize()
                logger.info(f"Maximized window: {window_title}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to maximize window '{window_title}': {e}")
            return False

    def start_application(self, app_path: str) -> bool:
        """
        Start an application by its path or command.
        
        Args:
            app_path: Path to executable or command name
            
        Returns:
            True if application was started successfully
        """
        try:
            import subprocess
            subprocess.Popen(app_path, shell=True)
            logger.info(f"Started application: {app_path}")
            time.sleep(self.action_delay * 5)  # Wait for app to start
            return True
        except Exception as e:
            logger.error(f"Failed to start application '{app_path}': {e}")
            return False

    def is_process_running(self, process_name: str) -> bool:
        """
        Check if a process is currently running.
        
        Args:
            process_name: Name of the process to check
            
        Returns:
            True if process is running, False otherwise
        """
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to check process '{process_name}': {e}")
            return False 

    # -------------------- VMware LOGIN HELPERS --------------------

    def vm_activate_login_screen(self, vm_center_x: int | None = None, vm_center_y: int | None = None) -> bool:
        """Single click to wake the Windows lock screen inside the VM."""
        try:
            if vm_center_x is None:
                vm_center_x = self.width // 2
            if vm_center_y is None:
                vm_center_y = self.height // 2

            logger.info(f"Activating VM login screen at ({vm_center_x}, {vm_center_y})")
            self.click(vm_center_x, vm_center_y)
            self.wait(2000)  # wait 2 s for prompt
            return True
        except Exception as e:
            logger.error(f"Failed to activate VM login screen: {e}")
            return False

    def vm_login_with_password(self, password: str, username: str | None = None) -> bool:
        """Enter credentials and submit to log in inside the VM."""
        try:
            if username:
                self.type(username)
                self.keypress(["tab"])
                self.wait(500)

            # clear field then type password
            self.keypress(["ctrl", "a"])
            self.wait(200)
            self.keypress(["delete"])
            self.wait(200)
            self.type(password)
            self.wait(500)
            self.keypress(["enter"])
            self.wait(5000)  # wait for desktop
            return True
        except Exception as e:
            logger.error(f"VM password entry failed: {e}")
            return False

    def vm_try_wake_screen(self) -> None:
        """Send a few common key presses to wake an unresponsive lock screen."""
        self.keypress(["space"])
        self.wait(1000)
        self.keypress(["enter"])
        self.wait(1000)
        self.keypress(["ctrl", "alt", "insert"])
        self.wait(2000)

    def vm_simple_login_flow(self, password: str, username: str | None = None) -> bool:
        """High-level helper: activate screen, then enter credentials."""
        logger.info("Starting simple VM login flow…")
        if not self.vm_activate_login_screen():
            logger.warning("Initial click didn't work, trying wake sequence…")
            self.vm_try_wake_screen()
            self.vm_activate_login_screen()

        return self.vm_login_with_password(password, username) 