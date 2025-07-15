# VMware Workflow Automation Prompts

## Phase 1: Launch VMware Workstation

### Prompt 1.1: Initial Launch
```
Please launch VMware Workstation. First, take a screenshot to see the current desktop state. Then use the Windows Run dialog (Win+R) and type "vmware" to launch the application. Wait for the VMware Workstation window to fully load, including the VM library panel on the left side. Take another screenshot once VMware is open and confirm you can see the main interface.
```

### Prompt 1.2: Verify VMware Ready State
```
Please verify that VMware Workstation has fully loaded. Check that:
1. The main VMware window is visible
2. The VM library panel is shown on the left (if not, press F9 to toggle it)
3. The title bar shows "VMware Workstation"
4. No splash screens or loading dialogs are present
Take a screenshot and describe what you see in the VMware interface.
```

## Phase 2: VM Selection and Startup

### Prompt 2.1: Locate Target VM
```
Now locate the "HDP 25 partner" virtual machine in the VM library on the left side of the VMware window. The VM library shows all available virtual machines as tiles or list items. Look for one labeled "HDP 25 partner". Once you find it, click on it once to select it (it should become highlighted). Take a screenshot showing the selected VM and describe its current state (Powered Off, Suspended, etc.).
```

### Prompt 2.2: Start the VM
```
With "HDP 25 partner" selected, start the virtual machine. Look for a green "Start" or "Power On" button - this is usually in the toolbar at the top or visible when the VM is selected. If you can't find the button, try right-clicking on the VM and selecting "Power" > "Start" from the context menu. After clicking start, you should see the VM state change to "Starting" and the console view should activate. Take a screenshot showing the VM is starting.
```

### Prompt 2.3: Monitor Boot Process
```
Monitor the VM boot process in the console view. You should see:
1. Initial black screen or BIOS/UEFI messages
2. Operating system boot logo (likely Linux for HDP)
3. Boot progress messages

This process typically takes 30-90 seconds. Take screenshots every 15 seconds to track progress. Wait until you see a login screen appear. The login screen should show a password field and possibly a username field. Once the login screen is stable and ready for input, take a final screenshot and confirm the VM has finished booting.
```

## Phase 3: VM Login

### Prompt 3.1: Prepare for Login
```
The VM has reached the login screen. Before entering credentials:
1. Click anywhere in the VM console view to ensure it has keyboard focus
2. Look for any visual indicators that the VM is ready for input (cursor blinking, field highlighted)
3. If there's a username field, check if it's pre-filled
4. Click in the password field to position the cursor there
Take a screenshot showing the cursor is in the password field.
```

### Prompt 3.2: Enter Login Credentials
```
Now enter the login credentials for the HDP VM:
1. Make sure the cursor is in the password field
2. Clear any existing content with Ctrl+A and Delete
3. Carefully type the password: [PASSWORD_HERE]
4. Press Enter to submit the login
5. Wait for the desktop environment to load

Watch for any error messages or login failures. If the login fails (shaking field, error message), we'll need to retry. Take a screenshot after pressing Enter and monitor the login progress.
```

### Prompt 3.3: Verify Successful Login
```
Wait for the desktop environment to fully load after login. This typically takes 10-30 seconds. Look for:
1. Desktop background appearing
2. Taskbar/panel fully loaded
3. Any startup applications or services
4. System tray icons populated

For HDP VMs, there may be additional services starting up. Wait until the system appears stable and responsive. Take a screenshot of the fully loaded desktop and confirm the VM is ready for use.
```

## Phase 4: Basic VM Operations

### Prompt 4.1: Navigate to Application
```
Now that the VM desktop is loaded, let's navigate to the workflow export functionality:
1. Look for application menus or desktop shortcuts related to HDP/Hadoop tools
2. Click on the application menu (usually bottom-left or top-left)
3. Search for or navigate to the workflow/data management tool
4. Take screenshots as you navigate to help identify the correct application

Describe what applications and options you see available in the VM.
```

### Prompt 4.2: Perform Export Operation
```
[This prompt would be customized based on the specific workflow export tool in the HDP environment]

Once you've opened the workflow management tool:
1. Look for an "Export" option in the menu or toolbar
2. Navigate to File > Export or find an export button
3. Select the workflow to export
4. Choose export format and destination
5. Confirm the export operation

Take screenshots of each step and confirm when the export completes successfully.
```

## Error Handling Prompts

### E1: VMware Won't Launch
```
VMware Workstation failed to launch. Let's try alternative methods:
1. Click the Start button and search for "VMware Workstation"
2. If found in search results, click to launch
3. If not found, look for a desktop shortcut
4. As a last resort, navigate to "C:\Program Files (x86)\VMware\VMware Workstation" and run vmware.exe

Take a screenshot of what happens with each attempt.
```

### E2: VM Not Found
```
Cannot find "HDP 25 partner" in the VM library. Let's troubleshoot:
1. Press F5 to refresh the VM library
2. Check if the library view is set correctly (View menu > Customize)
3. Try File > Open and browse for the VM files
4. Look for any VMs with similar names that might be the target
5. Check the bottom of the window for any error messages

Take a screenshot of the current VM library and any error messages.
```

### E3: VM Start Failed
```
The VM failed to start. Let's diagnose:
1. Check the bottom status bar for error messages
2. Look for any dialog boxes with error details
3. Try right-clicking the VM and selecting "Power" > "Power On"
4. If it mentions locked files, close any other VMware windows
5. Check if Windows is showing any security prompts

Take a screenshot of any error messages and describe what you see.
```

### E4: Boot Timeout
```
The VM boot process seems stuck. It's been over 90 seconds. Let's intervene:
1. Take a screenshot of the current console state
2. Try pressing Ctrl+Alt+Insert to send Ctrl+Alt+Delete to the VM
3. If no response, right-click the VM tab and select "Power" > "Reset"
4. If still stuck, select "Power" > "Power Off" then start again
5. Note where in the boot process it gets stuck

Document what you observe during the boot sequence.
```

### E5: Login Failed
```
The login attempt failed. Let's retry:
1. Check if Caps Lock is on (look for indicator)
2. Click the password field again to ensure focus
3. Clear the field completely with Ctrl+A then Delete
4. If there's a "Show Password" option, click it to verify input
5. Re-type the password slowly and carefully: [PASSWORD_HERE]
6. Try using the mouse to click the submit button instead of Enter

If it fails again, take a screenshot of any error messages.
```

## Verification Prompts

### V1: Confirm Each Stage
```
Before proceeding to the next step, please confirm:
1. Current state of the operation (what just completed)
2. Visual confirmation (what you see on screen)
3. Any unexpected elements or dialogs
4. Screenshot of the current state
5. Readiness for the next step

Example: "VMware has launched successfully. I can see the main window with the VM library on the left showing 3 VMs including 'HDP 25 partner' which shows as Powered Off."
```

### V2: Final Verification
```
Please provide a final summary of the completed workflow:
1. VMware Workstation: Successfully launched
2. VM Located: "HDP 25 partner" found and selected
3. VM Started: Boot sequence completed in X seconds
4. Login: Successfully authenticated
5. Desktop: Fully loaded and responsive
6. Export: Workflow export completed (if applicable)

Take a final screenshot showing the successful end state and note any issues encountered during the process.
``` 