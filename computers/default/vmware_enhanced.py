"""
VMware-specific enhancements for WindowsDesktopComputer

This module provides VMware-specific functionality that can be mixed into
the WindowsDesktopComputer class for enhanced VMware automation.
"""

import time
import logging
from typing import Optional, Tuple, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from computers.default.windows_desktop import WindowsDesktopComputer

logger = logging.getLogger(__name__)


class VMwareEnhancements:
    """
    Mixin class providing VMware-specific automation methods.
    
    This class should be mixed with WindowsDesktopComputer to provide
    VMware Workstation automation capabilities.
    
    Example:
        class VMwareComputer(WindowsDesktopComputer, VMwareEnhancements):
            pass
    """
    
    # Type hints for methods that will be available from WindowsDesktopComputer
    if TYPE_CHECKING:
        width: int
        height: int
        
        def screenshot(self) -> bytes: ...
        def click(self, x: int, y: int, button: str = "left") -> None: ...
        def keypress(self, keys: List[str]) -> None: ...
        def type(self, text: str) -> None: ...
        def wait(self, milliseconds: int) -> None: ...
        def get_window_list(self) -> List[str]: ...
        def get_active_window(self) -> str: ...
        def activate_window(self, window_title: str) -> bool: ...
    
    def find_vmware_window(self) -> Optional[str]:
        """
        Find the VMware Workstation window among open windows.
        
        Returns:
            Window title if found, None otherwise
        """
        windows = self.get_window_list()
        for window in windows:
            if "vmware workstation" in window.lower():
                logger.info(f"Found VMware window: {window}")
                return window
        return None

    # ------------------------------------------------------------------
    # Window-focus helpers (implements WINDOW FOCUS PROTOCOL)
    # ------------------------------------------------------------------
    def ensure_vmware_focus(self, wait_seconds: float = 2.0) -> bool:
        """Ensure a VMware Workstation window is the active foreground window.

        1. Take an initial screenshot so the calling workflow can log what is
           currently on screen.
        2. Check the active window title; if it already contains "vmware",
           nothing else is needed.
        3. Otherwise, iterate through *all* open windows (`get_window_list()`)
           and activate the first one whose title includes the word
           "vmware".  Wait a short period to allow the OS to bring that
           window to the front.
        4. Take a second screenshot to confirm the window is now visible.

        Args:
            wait_seconds: Seconds to wait after activating the window.

        Returns:
            True when a VMware window is active, False otherwise.
        """

        # Step 1 – record current visual context
        self.screenshot()

        active_title = self.get_active_window()
        if active_title and "vmware" in active_title.lower():
            logger.debug("VMware is already the active window")
            return True

        # Step 3 – search and activate
        vm_window = self.find_vmware_window()
        if vm_window:
            logger.info(f"Activating VMware window: {vm_window}")
            if self.activate_window(vm_window):
                self.wait(int(wait_seconds * 1000))
                # Step 4 – confirm visually
                self.screenshot()
                active_after = self.get_active_window()
                return bool(active_after and "vmware" in active_after.lower())

        logger.warning("Unable to find or activate a VMware window – focus may be incorrect")
        return False
    
    def launch_vmware(self, timeout: int = 30) -> bool:
        """
        Launch VMware Workstation and wait for it to be ready.
        
        Args:
            timeout: Maximum time to wait for VMware to launch
            
        Returns:
            True if launched successfully, False otherwise
        """
        # Check if already running
        if self.find_vmware_window():
            logger.info("VMware Workstation already running")
            return True
        
        # Launch VMware
        logger.info("Launching VMware Workstation...")
        self.keypress(["win", "r"])
        self.wait(500)
        self.type("vmware")
        self.keypress(["enter"])
        
        # Wait for window to appear
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.wait(1000)
            if self.find_vmware_window():
                self.wait(3000)  # Extra time for UI to stabilize
                return True
        
        logger.error("VMware Workstation failed to launch within timeout")
        return False
    
    def find_vm_in_library(self, vm_name: str, screenshot: bool = True) -> Optional[Tuple[int, int]]:
        """
        Find a VM in the VMware library panel.
        
        Args:
            vm_name: Name of the VM to find
            screenshot: Whether to take a screenshot for analysis
            
        Returns:
            Tuple of (x, y) coordinates if found, None otherwise
        """
        if screenshot:
            screen_data = self.screenshot()
            logger.info(f"Searching for VM '{vm_name}' in library...")
        
        # This is a placeholder - in real implementation, you'd use
        # image recognition or OCR to find the VM
        # For now, return approximate library coordinates
        
        # Typical VMware library is on the left side
        library_x = 150  # Center of library panel
        library_y_start = 150  # Below toolbar
        library_y_increment = 80  # Space between VMs
        
        # Try common positions (up to 10 VMs)
        for i in range(10):
            y_pos = library_y_start + (i * library_y_increment)
            if y_pos < self.height - 100:  # Stay within screen
                return (library_x, y_pos)
        
        return None
    
    def ensure_vm_library_visible(self) -> bool:
        """
        Ensure the VM library panel is visible in VMware.
        
        Returns:
            True if library is visible or made visible
        """
        logger.info("Ensuring VM library is visible...")
        
        # Press F9 to toggle library if needed
        self.keypress(["f9"])
        self.wait(1000)
        
        # Take screenshot to verify
        self.screenshot()
        
        # In practice, you'd verify the library is actually visible
        # For now, assume success
        return True
    
    def start_vm_from_toolbar(self) -> bool:
        """
        Click the Start button in VMware toolbar.
        
        Returns:
            True if clicked successfully
        """
        # WINDOW FOCUS PROTOCOL – confirm VMware window is active
        self.ensure_vmware_focus()
        # Typical toolbar button positions
        toolbar_y = 70  # Below menu bar
        start_button_x = 100  # Approximate position
        
        logger.info("Clicking Start button in toolbar...")
        self.click(start_button_x, toolbar_y)
        self.wait(1000)
        
        return True
    
    def start_vm_from_context_menu(self, vm_x: int, vm_y: int) -> bool:
        """
        Start a VM using right-click context menu.
        
        Args:
            vm_x: X coordinate of VM in library
            vm_y: Y coordinate of VM in library
            
        Returns:
            True if started successfully
        """
        # WINDOW FOCUS PROTOCOL – confirm VMware window is active
        self.ensure_vmware_focus()
        logger.info("Starting VM from context menu...")
        
        # Right-click on VM
        self.click(vm_x, vm_y, button="right")
        self.wait(500)
        
        # Click "Power" in context menu (usually ~100 pixels down)
        self.click(vm_x + 50, vm_y + 100)
        self.wait(300)
        
        # Click "Start" in submenu (usually ~30 pixels right and down)
        self.click(vm_x + 150, vm_y + 130)
        self.wait(1000)
        
        return True
    
    def wait_for_vm_state(self, target_state: str, timeout: int = 120) -> bool:
        """
        Wait for VM to reach a specific state.
        
        Args:
            target_state: State to wait for ("running", "login", "desktop")
            timeout: Maximum time to wait
            
        Returns:
            True if state reached, False if timeout
        """
        logger.info(f"Waiting for VM to reach '{target_state}' state...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            self.screenshot()
            
            # In practice, you'd analyze the screenshot to detect state
            # This is a simplified time-based approach
            
            if target_state == "running":
                # VM typically starts within 5-10 seconds
                if time.time() - start_time > 5:
                    return True
                    
            elif target_state == "login":
                # Login screen typically appears after 30-90 seconds
                if time.time() - start_time > 30:
                    return True
                    
            elif target_state == "desktop":
                # Desktop typically loads 10-30 seconds after login
                if time.time() - start_time > 10:
                    return True
            
            self.wait(5000)  # Check every 5 seconds
        
        logger.warning(f"Timeout waiting for '{target_state}' state")
        return False
    
    def vm_login(self, password: str, username: Optional[str] = None) -> bool:
        """
        Perform VM login with credentials.
        
        Args:
            password: Password to enter
            username: Username (if needed)
            
        Returns:
            True if login appears successful
        """
        # WINDOW FOCUS PROTOCOL – confirm VMware window is active
        self.ensure_vmware_focus()
        logger.info("Performing VM login...")
        
        # Click in center of console to ensure focus
        console_center_x = self.width // 2
        console_center_y = self.height // 2
        self.click(console_center_x, console_center_y)
        self.wait(500)
        
        # If username provided, enter it first
        if username:
            self.type(username)
            self.keypress(["tab"])
            self.wait(300)
        
        # Clear any existing text and enter password
        self.keypress(["ctrl", "a"])
        self.keypress(["delete"])
        self.wait(300)
        self.type(password)
        self.wait(500)
        
        # Submit login
        self.keypress(["enter"])
        self.wait(2000)
        
        # Wait for desktop
        return self.wait_for_vm_state("desktop", timeout=30)
    
    def send_ctrl_alt_del_to_vm(self) -> None:
        """Send Ctrl+Alt+Delete to the VM (Ctrl+Alt+Insert in VMware)."""
        logger.info("Sending Ctrl+Alt+Delete to VM...")
        self.keypress(["ctrl", "alt", "insert"])
        self.wait(1000)
    
    def reset_vm(self) -> bool:
        """
        Reset the VM using VMware menu.
        
        Returns:
            True if reset initiated
        """
        logger.info("Resetting VM...")
        
        # Use Alt menu navigation
        self.keypress(["alt"])
        self.wait(300)
        self.type("v")  # VM menu
        self.wait(300)
        self.type("r")  # Reset
        self.wait(500)
        
        # Confirm if dialog appears
        self.keypress(["enter"])
        self.wait(1000)
        
        return True
    
    def take_vm_snapshot(self, snapshot_name: str) -> bool:
        """
        Take a snapshot of the current VM state.
        
        Args:
            snapshot_name: Name for the snapshot
            
        Returns:
            True if snapshot initiated
        """
        logger.info(f"Taking VM snapshot: {snapshot_name}")
        
        # Use Ctrl+Shift+S shortcut
        self.keypress(["ctrl", "shift", "s"])
        self.wait(1000)
        
        # Enter snapshot name
        self.type(snapshot_name)
        self.wait(500)
        
        # Confirm
        self.keypress(["enter"])
        self.wait(2000)
        
        return True
    
    def detect_vm_error_dialog(self) -> bool:
        """
        Check for common VMware error dialogs.
        
        Returns:
            True if error dialog detected
        """
        # Take screenshot for analysis
        self.screenshot()
        
        # In practice, you'd use image recognition or OCR
        # to detect error dialogs
        
        # Try to dismiss any dialog with Escape
        self.keypress(["escape"])
        self.wait(500)
        
        return False


# Example usage - this would be implemented in your actual code:
# 
# from computers.default.windows_desktop import WindowsDesktopComputer
# from computers.default.vmware_enhanced import VMwareEnhancements
# 
# class VMwareWindowsComputer(WindowsDesktopComputer, VMwareEnhancements):
#     """Enhanced Windows computer with VMware-specific functionality."""
#     pass
# 
# # Usage:
# with VMwareWindowsComputer() as computer:
#     computer.launch_vmware()
#     vm_coords = computer.find_vm_in_library("HDP 25 partner")
#     if vm_coords:
#         computer.start_vm_from_context_menu(*vm_coords)
#         computer.wait_for_vm_state("login")
#         computer.vm_login("password123") 