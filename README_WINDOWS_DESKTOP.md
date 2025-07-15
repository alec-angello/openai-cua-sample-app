# Windows Desktop Computer Integration

This document describes the Windows Desktop Computer integration for OpenAI's Computer Using Agent (CUA) sample application. This integration allows you to automate Windows desktop applications using the CUA framework, optimized for remote desktop (RDP) environments.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [RDP Optimization](#rdp-optimization)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Security Considerations](#security-considerations)
- [API Reference](#api-reference)

## Overview

The `WindowsDesktopComputer` class provides desktop automation capabilities for Windows environments, implementing the Computer protocol used by the OpenAI CUA framework. It's specifically optimized for remote desktop scenarios where network latency, screen compression, and DPI scaling present unique challenges.

### Key Components

- **WindowsDesktopComputer**: Main automation class implementing the Computer protocol
- **RDP Optimizations**: Specialized handling for remote desktop environments  
- **Screenshot Caching**: Optimized screenshot capture with compression
- **Retry Logic**: Robust error handling with exponential backoff
- **DPI Scaling**: Automatic coordinate adjustment for high-DPI displays

## Features

### Core Automation Features
- ✅ **Mouse Operations**: Click, double-click, right-click, drag, scroll
- ✅ **Keyboard Input**: Text typing, key combinations, special keys
- ✅ **Screenshot Capture**: High-performance screen capture with compression
- ✅ **Window Management**: Activate, minimize, maximize, enumerate windows
- ✅ **Application Control**: Launch applications, monitor processes
- ✅ **Coordinate System**: Automatic DPI scaling and bounds checking

### RDP-Specific Optimizations
- ✅ **Latency Handling**: Configurable delays between actions
- ✅ **Compression Optimization**: JPEG compression for faster transmission
- ✅ **Screenshot Caching**: Reduced network traffic with intelligent caching
- ✅ **Retry Logic**: Automatic retry with exponential backoff
- ✅ **Network Resilience**: Robust error handling for unstable connections

## Installation

### Prerequisites

- Windows 10/11 or Windows Server 2016+
- Python 3.8+
- Administrator privileges (for some automation features)

### 1. Install Dependencies

```bash
# Install the Windows-specific dependencies
pip install pyautogui==0.9.54
pip install pygetwindow==0.0.9  
pip install psutil==6.1.0
pip install pywin32==308
pip install pillow==11.1.0

# Or install all dependencies at once
pip install -r requirements.txt
```

### 2. Configure PyAutoGUI

For security, disable the failsafe in RDP environments:

```python
import pyautogui
pyautogui.FAILSAFE = False  # Disable mouse failsafe for RDP
```

### 3. Verify Installation

```bash
# Run the test suite
python -m pytest tests/test_windows_desktop.py -v

# Or run the example
python examples/windows_desktop_example.py
```

## Configuration

### Basic Configuration

```python
from computers.default.windows_desktop import WindowsDesktopComputer

# Standard configuration for RDP environment
computer = WindowsDesktopComputer(
    action_delay=0.2,        # Delay between actions (seconds)
    screenshot_quality=85,   # JPEG quality (1-100)
    max_retries=3,           # Number of retries for failed actions
    rdp_mode=True           # Enable RDP optimizations
)
```

### Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `action_delay` | 0.2 | Delay between actions in seconds |
| `screenshot_quality` | 85 | JPEG compression quality (1-100) |
| `max_retries` | 3 | Number of retry attempts for failed actions |
| `rdp_mode` | True | Enable RDP-specific optimizations |

### Environment-Specific Settings

#### Local Desktop
```python
computer = WindowsDesktopComputer(
    action_delay=0.05,      # Faster for local
    screenshot_quality=95,   # Higher quality
    rdp_mode=False          # Disable RDP optimizations
)
```

#### High-Latency RDP
```python
computer = WindowsDesktopComputer(
    action_delay=0.5,       # Slower for high latency
    screenshot_quality=60,   # Lower quality for speed
    max_retries=5,          # More retries
    rdp_mode=True
)
```

#### Low-Bandwidth RDP
```python
computer = WindowsDesktopComputer(
    action_delay=0.3,
    screenshot_quality=40,   # Very low quality
    max_retries=3,
    rdp_mode=True
)
```

## Usage

### Using with CUA CLI

```bash
# Use Windows desktop computer with the CUA CLI
python cli.py --computer windows-desktop --input "Open Notepad and type 'Hello World'"
```

### Programmatic Usage

```python
from computers.default.windows_desktop import WindowsDesktopComputer

# Context manager usage (recommended)
with WindowsDesktopComputer() as computer:
    # Take a screenshot
    screenshot = computer.screenshot()
    
    # Get screen dimensions
    width, height = computer.get_dimensions()
    
    # Click at center of screen
    computer.click(width // 2, height // 2)
    
    # Type text
    computer.type("Hello, World!")
    
    # Press keyboard shortcut
    computer.keypress(["ctrl", "s"])  # Save
    
    # Launch application
    computer.start_application("notepad.exe")
    
    # Window management
    computer.activate_window("Notepad")
    computer.maximize_window("Notepad")
```

### Advanced Examples

#### Form Automation
```python
with WindowsDesktopComputer() as computer:
    # Fill out a form
    computer.click(100, 200)  # Click first field
    computer.type("John Doe")
    
    computer.click(100, 250)  # Click second field  
    computer.type("john.doe@example.com")
    
    computer.click(200, 300)  # Click submit button
```

#### File Operations
```python
with WindowsDesktopComputer() as computer:
    # Open File Explorer
    computer.keypress(["win", "e"])
    computer.wait(1000)
    
    # Navigate to folder
    computer.keypress(["ctrl", "l"])  # Focus address bar
    computer.type("C:\\Users\\Documents")
    computer.keypress(["enter"])
    
    # Create new folder
    computer.keypress(["ctrl", "shift", "n"])
    computer.type("New Folder")
    computer.keypress(["enter"])
```

## RDP Optimization

### Network Latency Handling

The WindowsDesktopComputer automatically adjusts for RDP latency:

```python
# Automatic delay insertion
computer.click(x, y)           # Click
# Automatic delay (action_delay) here
computer.type("text")          # Type
# Automatic delay here
computer.keypress(["enter"])   # Keypress
```

### Screenshot Optimization

Screenshots are optimized for RDP transmission:

```python
# RDP mode uses JPEG compression
screenshot = computer.screenshot()  # Returns compressed JPEG as base64

# Local mode uses PNG for quality
computer_local = WindowsDesktopComputer(rdp_mode=False)
screenshot = computer_local.screenshot()  # Returns PNG as base64
```

### Caching Strategy

Screenshots are cached to reduce network traffic:

```python
# First screenshot - captured from screen
screenshot1 = computer.screenshot()

# Second screenshot within 100ms - returns cached version
screenshot2 = computer.screenshot()  # Uses cached data
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/test_windows_desktop.py -v

# Run specific test categories
python -m pytest tests/test_windows_desktop.py::TestWindowsDesktopComputer -v
python -m pytest tests/test_windows_desktop.py::TestWindowsDesktopIntegration -v

# Run with coverage
python -m pytest tests/test_windows_desktop.py --cov=computers.default.windows_desktop
```

### Manual Testing

```bash
# Run the interactive example
python examples/windows_desktop_example.py

# Test basic functionality
python -c "
from computers.default.windows_desktop import WindowsDesktopComputer
with WindowsDesktopComputer() as c:
    print(f'Screen: {c.get_dimensions()}')
    print(f'Environment: {c.get_environment()}')
    print('Screenshot size:', len(c.screenshot()))
"
```

### Test Coverage

The test suite covers:
- ✅ Computer protocol compliance
- ✅ All mouse and keyboard operations
- ✅ Screenshot capture and caching
- ✅ DPI scaling and coordinate adjustment
- ✅ Window management functions
- ✅ Application control
- ✅ Error handling and retry logic
- ✅ RDP optimization features

## Troubleshooting

### Common Issues

#### 1. Import Errors

```python
# Error: ModuleNotFoundError: No module named 'pyautogui'
# Solution: Install dependencies
pip install -r requirements.txt
```

#### 2. Screenshot Failures

```python
# Error: Screenshot failed: access is denied
# Solution: Run with administrator privileges or disable UAC prompts
```

#### 3. Mouse/Keyboard Not Working

```python
# Error: Actions not registering
# Solutions:
# 1. Disable pyautogui failsafe
pyautogui.FAILSAFE = False

# 2. Increase action delays
computer = WindowsDesktopComputer(action_delay=0.5)

# 3. Check for interference from security software
```

#### 4. RDP Performance Issues

```python
# Issue: Slow performance over RDP
# Solutions:
# 1. Reduce screenshot quality
computer = WindowsDesktopComputer(screenshot_quality=50)

# 2. Increase action delays
computer = WindowsDesktopComputer(action_delay=0.5)

# 3. Enable compression optimizations
computer = WindowsDesktopComputer(rdp_mode=True)
```

#### 5. DPI Scaling Issues

```python
# Issue: Clicks miss targets on high-DPI displays
# Solution: DPI adjustment is automatic, but can be verified:
computer = WindowsDesktopComputer()
print(f"DPI Scale: {computer.dpi_scale_x}x{computer.dpi_scale_y}")
```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from computers.default.windows_desktop import WindowsDesktopComputer
with WindowsDesktopComputer() as computer:
    computer.click(100, 100)  # Will show debug output
```

### Performance Monitoring

```python
import time
from computers.default.windows_desktop import WindowsDesktopComputer

with WindowsDesktopComputer() as computer:
    # Measure screenshot performance
    start = time.time()
    screenshot = computer.screenshot()
    duration = time.time() - start
    print(f"Screenshot took {duration:.2f}s, size: {len(screenshot)} bytes")
    
    # Measure action performance
    start = time.time()
    computer.click(100, 100)
    duration = time.time() - start
    print(f"Click took {duration:.2f}s")
```

## Best Practices

### 1. Use Context Managers

```python
# ✅ Good - Automatic cleanup
with WindowsDesktopComputer() as computer:
    computer.click(100, 100)

# ❌ Bad - Manual cleanup required
computer = WindowsDesktopComputer()
computer.click(100, 100)
# Need to manually clean up
```

### 2. Handle Exceptions Gracefully

```python
try:
    with WindowsDesktopComputer() as computer:
        computer.click(x, y)
except ValueError as e:
    print(f"Invalid coordinates: {e}")
except Exception as e:
    print(f"Automation failed: {e}")
```

### 3. Validate Coordinates

```python
width, height = computer.get_dimensions()
if 0 <= x <= width and 0 <= y <= height:
    computer.click(x, y)
else:
    print(f"Coordinates ({x}, {y}) out of bounds")
```

### 4. Use Appropriate Delays

```python
# ✅ Good - Account for application response time
computer.start_application("notepad.exe")
computer.wait(2000)  # Wait for app to start
computer.type("Hello")

# ❌ Bad - No wait time
computer.start_application("notepad.exe")
computer.type("Hello")  # May fail if app not ready
```

### 5. Optimize for Your Environment

```python
# For RDP environments
computer = WindowsDesktopComputer(
    action_delay=0.3,        # Account for network latency
    screenshot_quality=70,   # Balance quality and performance
    rdp_mode=True           # Enable RDP optimizations
)

# For local environments  
computer = WindowsDesktopComputer(
    action_delay=0.05,      # Faster local response
    screenshot_quality=95,   # Higher quality
    rdp_mode=False          # Disable RDP overhead
)
```

## Security Considerations

### 1. Disable Failsafe

```python
# Required for RDP environments but reduces safety
pyautogui.FAILSAFE = False
```

**Risk**: Cannot stop automation by moving mouse to corner
**Mitigation**: Use keyboard interrupts (Ctrl+C) and proper exception handling

### 2. Administrative Privileges

Some operations require elevated privileges:

```python
# May require admin rights:
# - Taking screenshots of secure applications
# - Automating UAC prompts
# - Accessing certain system windows
```

**Risk**: Running with elevated privileges increases attack surface
**Mitigation**: Run with minimum required privileges, use dedicated automation accounts

### 3. Unattended Automation

```python
# Risk: Automation continuing in unintended ways
# Mitigation: Add safety checks
if not computer.is_process_running("target_application"):
    print("Target application not running, stopping automation")
    return
```

### 4. Screen Content Privacy

```python
# Screenshots may capture sensitive information
screenshot = computer.screenshot()
# Ensure secure handling and disposal of screenshot data
```

**Risk**: Screenshots contain sensitive information
**Mitigation**: Implement secure storage, automatic cleanup, and access controls

### 5. Input Validation

```python
# Validate all external input
def safe_type(computer, text):
    if not isinstance(text, str):
        raise ValueError("Text must be string")
    if len(text) > 10000:
        raise ValueError("Text too long")
    computer.type(text)
```

## API Reference

### WindowsDesktopComputer

#### Constructor

```python
WindowsDesktopComputer(
    action_delay: float = 0.2,
    screenshot_quality: int = 85,
    max_retries: int = 3,
    rdp_mode: bool = True
)
```

#### Core Computer Protocol Methods

##### `get_environment() -> Literal["windows"]`
Returns the environment type.

##### `get_dimensions() -> Tuple[int, int]`
Returns screen dimensions as (width, height).

##### `screenshot() -> str`
Captures screenshot and returns as base64-encoded string.

##### `click(x: int, y: int, button: str = "left") -> None`
Clicks at specified coordinates.
- `button`: "left", "right", or "middle"

##### `double_click(x: int, y: int) -> None`
Double-clicks at specified coordinates.

##### `scroll(x: int, y: int, scroll_x: int, scroll_y: int) -> None`
Scrolls at specified position.
- `scroll_y`: Positive = up, negative = down
- `scroll_x`: Positive = right, negative = left

##### `type(text: str) -> None`
Types the specified text.

##### `wait(ms: int = 1000) -> None`
Waits for specified milliseconds.

##### `move(x: int, y: int) -> None`
Moves mouse to specified coordinates.

##### `keypress(keys: List[str]) -> None`
Presses key combination.
- Example: `["ctrl", "c"]` for Ctrl+C

##### `drag(path: List[Dict[str, int]]) -> None`
Performs drag operation along path.
- Example: `[{"x": 100, "y": 100}, {"x": 200, "y": 200}]`

##### `get_current_url() -> str`
Returns empty string (not applicable for desktop).

#### Windows-Specific Methods

##### `get_active_window() -> str`
Returns title of currently active window.

##### `get_window_list() -> List[str]`
Returns list of all visible window titles.

##### `activate_window(window_title: str) -> bool`
Activates window by title. Returns success status.

##### `minimize_window(window_title: str) -> bool`
Minimizes window by title. Returns success status.

##### `maximize_window(window_title: str) -> bool`
Maximizes window by title. Returns success status.

##### `start_application(app_path: str) -> bool`
Starts application by path or command. Returns success status.

##### `is_process_running(process_name: str) -> bool`
Checks if process is running. Returns True if found.

### Key Mappings

The following keys are automatically mapped:

| Input Key | Windows Key |
|-----------|-------------|
| `cmd` | `win` |
| `super` | `win` |
| `option` | `alt` |
| `return` | `enter` |
| `esc` | `escape` |

---

## Support

For issues specific to the Windows Desktop Computer integration:

1. Check the [Troubleshooting](#troubleshooting) section
2. Run the test suite to identify issues
3. Enable debug logging for detailed error information
4. Review the example scripts for usage patterns

For general CUA framework issues, refer to the main project documentation. 