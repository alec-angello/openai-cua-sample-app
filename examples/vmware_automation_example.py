#!/usr/bin/env python3
"""
VMware Workstation Complete Automation Example

This script demonstrates a complete VMware automation workflow including:
- Launching VMware Workstation
- Finding and starting a VM
- Handling VM boot process
- Performing login
- Basic VM operations
- Comprehensive error handling

Usage:
    python examples/vmware_automation_example.py --vm "HDP 25 partner" --password "your_password"
"""

import sys
import time
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from computers.default.windows_desktop import WindowsDesktopComputer
from computers.default.vmware_enhanced import VMwareEnhancements

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VMwareWindowsComputer(WindowsDesktopComputer, VMwareEnhancements):
    """Combined class with Windows desktop and VMware functionality."""
    pass


class VMwareAutomationWorkflow:
    """Manages the complete VMware automation workflow."""
    
    def __init__(self, computer: VMwareWindowsComputer, vm_name: str, password: str, username: Optional[str] = None):
        self.computer = computer
        self.vm_name = vm_name
        self.password = password
        self.username = username
        self.workflow_state: Dict[str, Any] = {
            'vmware_launched': False,
            'vm_found': False,
            'vm_started': False,
            'vm_booted': False,
            'logged_in': False,
            'operations_complete': False,
            'errors': []
        }
    
    def run_complete_workflow(self) -> bool:
        """
        Execute the complete VMware automation workflow.
        
        Returns:
            True if workflow completed successfully
        """
        try:
            # Phase 1: Launch VMware
            if not self._phase1_launch_vmware():
                return False
            
            # Phase 2: Find and start VM
            if not self._phase2_start_vm():
                return False
            
            # Phase 3: Wait for boot and login
            if not self._phase3_vm_login():
                return False
            
            # Phase 4: Perform operations
            if not self._phase4_vm_operations():
                return False
            
            logger.info("Workflow completed successfully!")
            self.workflow_state['operations_complete'] = True
            return True
            
        except Exception as e:
            logger.error(f"Workflow failed with error: {e}")
            self.workflow_state['errors'].append(str(e))
            return False
    
    def _phase1_launch_vmware(self) -> bool:
        """Phase 1: Launch VMware Workstation."""
        logger.info("=== Phase 1: Launching VMware Workstation ===")
        
        try:
            # Take initial screenshot
            logger.info("Taking initial desktop screenshot...")
            self.computer.screenshot()
            
            # Launch VMware
            if not self.computer.launch_vmware(timeout=30):
                logger.error("Failed to launch VMware Workstation")
                self.workflow_state['errors'].append("VMware launch failed")
                return False
            
            # Ensure library is visible
            logger.info("Ensuring VM library is visible...")
            self.computer.ensure_vm_library_visible()
            
            # Verify VMware is ready
            logger.info("Verifying VMware interface...")
            self.computer.screenshot()
            self.computer.wait(2000)
            
            self.workflow_state['vmware_launched'] = True
            logger.info("✓ VMware Workstation launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Phase 1 error: {e}")
            self.workflow_state['errors'].append(f"Phase 1: {e}")
            return False
    
    def _phase2_start_vm(self) -> bool:
        """Phase 2: Find and start the target VM."""
        logger.info(f"=== Phase 2: Starting VM '{self.vm_name}' ===")
        
        try:
            # Find VM in library
            logger.info(f"Searching for VM '{self.vm_name}'...")
            vm_coords = self.computer.find_vm_in_library(self.vm_name)
            
            if not vm_coords:
                logger.error(f"VM '{self.vm_name}' not found in library")
                self.workflow_state['errors'].append("VM not found")
                
                # Try refresh
                logger.info("Refreshing VM library...")
                self.computer.keypress(["f5"])
                self.computer.wait(2000)
                vm_coords = self.computer.find_vm_in_library(self.vm_name)
                
                if not vm_coords:
                    return False
            
            self.workflow_state['vm_found'] = True
            logger.info(f"✓ Found VM at coordinates: {vm_coords}")
            
            # Select the VM
            logger.info("Selecting VM...")
            self.computer.click(vm_coords[0], vm_coords[1])
            self.computer.wait(1000)
            self.computer.screenshot()
            
            # Try to start VM
            logger.info("Starting VM...")
            start_success = False
            
            # Method 1: Toolbar button
            if self.computer.start_vm_from_toolbar():
                logger.info("Clicked toolbar start button")
                self.computer.wait(2000)
                start_success = True
            
            # Method 2: Context menu if toolbar didn't work
            if not start_success:
                logger.info("Trying context menu approach...")
                if self.computer.start_vm_from_context_menu(vm_coords[0], vm_coords[1]):
                    self.computer.wait(2000)
                    start_success = True
            
            if not start_success:
                logger.error("Failed to start VM")
                self.workflow_state['errors'].append("VM start failed")
                return False
            
            self.workflow_state['vm_started'] = True
            logger.info("✓ VM start command issued")
            return True
            
        except Exception as e:
            logger.error(f"Phase 2 error: {e}")
            self.workflow_state['errors'].append(f"Phase 2: {e}")
            return False
    
    def _phase3_vm_login(self) -> bool:
        """Phase 3: Wait for VM boot and perform login."""
        logger.info("=== Phase 3: VM Boot and Login ===")
        
        try:
            # Wait for VM to start booting
            logger.info("Waiting for VM to begin boot sequence...")
            self.computer.wait(5000)
            self.computer.screenshot()
            
            # Monitor boot process
            logger.info("Monitoring boot process (this may take 30-90 seconds)...")
            boot_start_time = time.time()
            screenshot_interval = 15  # seconds
            last_screenshot = boot_start_time
            
            while True:
                current_time = time.time()
                elapsed = current_time - boot_start_time
                
                # Take periodic screenshots
                if current_time - last_screenshot >= screenshot_interval:
                    logger.info(f"Boot progress: {elapsed:.0f} seconds elapsed...")
                    self.computer.screenshot()
                    last_screenshot = current_time
                
                # Check for timeout
                if elapsed > 120:  # 2 minute timeout
                    logger.error("VM boot timeout")
                    self.workflow_state['errors'].append("Boot timeout")
                    
                    # Try to reset VM
                    logger.info("Attempting VM reset...")
                    self.computer.reset_vm()
                    return False
                
                # Check if login screen is ready
                # In practice, you'd use image recognition here
                if elapsed > 30:  # Assume login screen after 30 seconds
                    logger.info("Boot sequence appears complete")
                    break
                
                self.computer.wait(5000)
            
            self.workflow_state['vm_booted'] = True
            logger.info("✓ VM has booted to login screen")
            
            # Perform login
            logger.info("Preparing to login...")
            self.computer.wait(3000)
            
            # Click in console to ensure focus
            console_x = self.computer.width // 2
            console_y = self.computer.height // 2
            self.computer.click(console_x, console_y)
            self.computer.wait(1000)
            
            # Perform login
            if not self.computer.vm_login(self.password, self.username):
                logger.error("Login failed")
                self.workflow_state['errors'].append("Login failed")
                
                # Try again with caps lock check
                logger.info("Checking caps lock and retrying...")
                self.computer.keypress(["caps_lock"])  # Toggle caps lock
                self.computer.wait(500)
                
                if not self.computer.vm_login(self.password, self.username):
                    return False
            
            self.workflow_state['logged_in'] = True
            logger.info("✓ Successfully logged into VM")
            
            # Wait for desktop to fully load
            logger.info("Waiting for desktop to load...")
            self.computer.wait(10000)  # 10 seconds for desktop
            self.computer.screenshot()
            
            return True
            
        except Exception as e:
            logger.error(f"Phase 3 error: {e}")
            self.workflow_state['errors'].append(f"Phase 3: {e}")
            return False
    
    def _phase4_vm_operations(self) -> bool:
        """Phase 4: Perform basic VM operations."""
        logger.info("=== Phase 4: VM Operations ===")
        
        try:
            # Example: Open a terminal or application
            logger.info("Opening application menu...")
            
            # Try common methods to open application menu
            # Method 1: Click Start button (bottom-left)
            self.computer.click(50, self.computer.height - 50)
            self.computer.wait(2000)
            self.computer.screenshot()
            
            # Type to search for application
            logger.info("Searching for terminal application...")
            self.computer.type("terminal")
            self.computer.wait(2000)
            self.computer.screenshot()
            
            # Press Enter to launch
            self.computer.keypress(["enter"])
            self.computer.wait(3000)
            
            # Take final screenshot
            logger.info("Taking final screenshot of VM state...")
            self.computer.screenshot()
            
            logger.info("✓ Basic VM operations completed")
            return True
            
        except Exception as e:
            logger.error(f"Phase 4 error: {e}")
            self.workflow_state['errors'].append(f"Phase 4: {e}")
            return False
    
    def generate_report(self) -> str:
        """Generate a summary report of the workflow execution."""
        report = [
            "=== VMware Automation Workflow Report ===",
            f"Target VM: {self.vm_name}",
            f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Workflow Status:",
            f"  VMware Launched: {'✓' if self.workflow_state['vmware_launched'] else '✗'}",
            f"  VM Found: {'✓' if self.workflow_state['vm_found'] else '✗'}",
            f"  VM Started: {'✓' if self.workflow_state['vm_started'] else '✗'}",
            f"  VM Booted: {'✓' if self.workflow_state['vm_booted'] else '✗'}",
            f"  Logged In: {'✓' if self.workflow_state['logged_in'] else '✗'}",
            f"  Operations Complete: {'✓' if self.workflow_state['operations_complete'] else '✗'}",
            ""
        ]
        
        if self.workflow_state['errors']:
            report.extend([
                "Errors Encountered:",
                *[f"  - {error}" for error in self.workflow_state['errors']],
                ""
            ])
        
        report.append("=" * 40)
        return "\n".join(report)


def main():
    """Main function to run the VMware automation workflow."""
    parser = argparse.ArgumentParser(description="VMware Workstation Automation")
    parser.add_argument("--vm", default="HDP 25 partner", help="Name of the VM to automate")
    parser.add_argument("--password", required=True, help="VM login password")
    parser.add_argument("--username", help="VM login username (if needed)")
    parser.add_argument("--rdp-mode", action="store_true", default=True, help="Enable RDP optimizations")
    parser.add_argument("--action-delay", type=float, default=0.3, help="Delay between actions")
    
    args = parser.parse_args()
    
    print("VMware Workstation Automation")
    print("=" * 40)
    print(f"Target VM: {args.vm}")
    print(f"RDP Mode: {args.rdp_mode}")
    print(f"Action Delay: {args.action_delay}s")
    print()
    
    # Initialize computer with RDP optimizations
    try:
        with VMwareWindowsComputer(
            action_delay=args.action_delay,
            screenshot_quality=70,
            max_retries=3,
            rdp_mode=args.rdp_mode
        ) as computer:
            
            # Create and run workflow
            workflow = VMwareAutomationWorkflow(
                computer=computer,
                vm_name=args.vm,
                password=args.password,
                username=args.username
            )
            
            # Execute workflow
            success = workflow.run_complete_workflow()
            
            # Print report
            print()
            print(workflow.generate_report())
            
            # Exit with appropriate code
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main() 