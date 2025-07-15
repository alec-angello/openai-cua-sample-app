# VMware Automation Testing Guide

## Overview

This guide provides a comprehensive testing strategy for the VMware Workstation automation workflow in remote desktop environments.

## Testing Prerequisites

1. **Environment Setup**
   - Windows remote desktop access
   - VMware Workstation installed
   - Target VM ("HDP 25 partner") available
   - Python environment with all dependencies
   - Sufficient permissions for automation

2. **Test Data**
   - VM name: "HDP 25 partner"
   - Valid login credentials
   - Known VM state (powered off)

## Testing Phases

### Phase 1: Component Testing

#### 1.1 Test WindowsDesktopComputer Basic Functions
```bash
# Test basic Windows automation
python -c "
from computers.default.windows_desktop import WindowsDesktopComputer
with WindowsDesktopComputer() as c:
    print(f'Screen: {c.get_dimensions()}')
    c.screenshot()
    c.move(100, 100)
    print('Basic functions working')
"
```

#### 1.2 Test VMware Enhancement Methods
```bash
# Test VMware-specific methods
python -c "
from computers.default.windows_desktop import WindowsDesktopComputer
from computers.default.vmware_enhanced import VMwareEnhancements

class TestComputer(WindowsDesktopComputer, VMwareEnhancements):
    pass

with TestComputer() as c:
    windows = c.get_window_list()
    vmware = c.find_vmware_window()
    print(f'VMware running: {vmware is not None}')
"
```

### Phase 2: Integration Testing

#### 2.1 Test VMware Launch
```bash
# Test launching VMware
python examples/vmware_automation_example.py \
    --vm "HDP 25 partner" \
    --password "test" \
    --test-phase launch
```

#### 2.2 Test VM Discovery
```bash
# Test finding VM in library
python examples/vmware_automation_example.py \
    --vm "HDP 25 partner" \
    --password "test" \
    --test-phase discover
```

#### 2.3 Test VM Start
```bash
# Test starting VM
python examples/vmware_automation_example.py \
    --vm "HDP 25 partner" \
    --password "test" \
    --test-phase start
```

### Phase 3: End-to-End Testing

#### 3.1 Full Workflow Test
```bash
# Run complete workflow
python examples/vmware_automation_example.py \
    --vm "HDP 25 partner" \
    --password "actual_password" \
    --action-delay 0.5
```

#### 3.2 Error Recovery Test
```bash
# Test with non-existent VM
python examples/vmware_automation_example.py \
    --vm "NonExistent VM" \
    --password "test"
```

## Testing with CUA CLI

### Basic VMware Automation
```bash
# Using the standard CUA CLI with VMware prompts
python cli.py --computer windows-desktop --input "Launch VMware Workstation and start the 'HDP 25 partner' virtual machine"
```

### With Enhanced System Prompt
```bash
# Create a test script that uses the enhanced prompt
cat > test_vmware_cua.py << 'EOF'
import sys
sys.path.append('.')

from agent.agent import Agent
from computers.default.windows_desktop import WindowsDesktopComputer

# Read the VMware system prompt
with open('examples/vmware_system_prompt.md', 'r') as f:
    vmware_prompt = f.read()

# Initialize computer and agent
with WindowsDesktopComputer(rdp_mode=True, action_delay=0.3) as computer:
    agent = Agent(computer=computer)
    
    # Add VMware knowledge to the conversation
    items = [
        {"role": "system", "content": vmware_prompt},
        {"role": "user", "content": "Launch VMware Workstation and start the 'HDP 25 partner' VM"}
    ]
    
    # Run the agent
    result = agent.run(starting_messages=items)
    print(f"Result: {result}")
EOF

python test_vmware_cua.py
```

## Test Scenarios

### Scenario 1: Happy Path
1. VMware launches successfully
2. VM is found in library
3. VM starts without issues
4. Boot completes normally
5. Login succeeds
6. Operations complete

**Expected Result**: All phases complete successfully

### Scenario 2: VMware Already Running
1. VMware is already open
2. Continue with VM operations

**Expected Result**: Detects running VMware and proceeds

### Scenario 3: VM Not in Library
1. VMware launches
2. VM not found initially
3. Refresh library (F5)
4. VM appears and continues

**Expected Result**: Recovers and finds VM after refresh

### Scenario 4: Boot Timeout
1. VM starts but hangs during boot
2. Timeout after 2 minutes
3. VM is reset
4. Boot retried

**Expected Result**: Handles timeout and attempts recovery

### Scenario 5: Login Failure
1. VM boots successfully
2. First login attempt fails
3. Caps lock checked/toggled
4. Login retried

**Expected Result**: Recovers from login failure

## Performance Testing

### Measure Operation Times
```python
import time
from computers.default.windows_desktop import WindowsDesktopComputer

times = {}

with WindowsDesktopComputer(rdp_mode=True) as c:
    # Screenshot performance
    start = time.time()
    c.screenshot()
    times['screenshot'] = time.time() - start
    
    # Click performance
    start = time.time()
    c.click(100, 100)
    times['click'] = time.time() - start
    
    # Type performance
    start = time.time()
    c.type("test text")
    times['type'] = time.time() - start

print("Performance Metrics:")
for op, duration in times.items():
    print(f"  {op}: {duration:.3f}s")
```

## Debugging Failed Tests

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your tests - you'll see detailed output
```

### Capture Screenshots
```python
# Modify workflow to save screenshots
import base64

def save_screenshot(computer, filename):
    screenshot = computer.screenshot()
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(screenshot))
```

### Check VM State Manually
1. Take screenshot at each phase
2. Verify visual elements match expectations
3. Check for unexpected dialogs or errors
4. Monitor system resources

## Continuous Testing

### Automated Test Suite
```bash
# Create a test suite script
cat > run_vmware_tests.sh << 'EOF'
#!/bin/bash

echo "Running VMware Automation Tests"
echo "=============================="

# Test 1: Basic functionality
echo "Test 1: Basic Windows automation"
python -m pytest tests/test_windows_desktop.py -v

# Test 2: VMware launch
echo "Test 2: VMware launch test"
python examples/vmware_automation_example.py --vm "test" --password "test" --dry-run

# Test 3: Error handling
echo "Test 3: Error handling test"
python examples/vmware_automation_example.py --vm "nonexistent" --password "test" 2>&1 | grep -q "VM not found" && echo "PASS" || echo "FAIL"

echo "Tests complete"
EOF

chmod +x run_vmware_tests.sh
./run_vmware_tests.sh
```

### Integration with CI/CD
```yaml
# Example GitHub Actions workflow
name: VMware Automation Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python -m pytest tests/test_windows_desktop.py
```

## Best Practices for Testing

1. **Always Test in Isolation**
   - Close other applications
   - Start with known VM state
   - Clear any previous errors

2. **Use Consistent Timing**
   - Same action delays
   - Same screenshot intervals
   - Account for RDP latency

3. **Document Failures**
   - Save screenshots
   - Capture error messages
   - Note exact failure point

4. **Test Edge Cases**
   - Very long VM names
   - Special characters in passwords
   - Multiple VMs with similar names
   - Different screen resolutions

5. **Monitor Resources**
   - CPU usage during automation
   - Network latency impact
   - Memory consumption

## Troubleshooting Common Issues

### Issue: Screenshots are black
**Solution**: Check RDP color depth settings, try different screenshot methods

### Issue: Clicks don't register
**Solution**: Increase action delays, verify coordinates, check DPI scaling

### Issue: VM library not visible
**Solution**: Press F9 to toggle, check View menu settings

### Issue: Login keeps failing
**Solution**: Check caps lock, verify password encoding, try manual entry

### Issue: Automation too slow
**Solution**: Reduce screenshot quality, optimize action delays, check network

## Validation Checklist

- [ ] VMware launches within 30 seconds
- [ ] VM library is visible and populated
- [ ] Target VM can be selected
- [ ] Start button/menu works
- [ ] VM boots within 2 minutes
- [ ] Login screen appears correctly
- [ ] Password entry works
- [ ] Desktop loads completely
- [ ] Basic operations succeed
- [ ] Error recovery works
- [ ] Performance is acceptable
- [ ] Screenshots are clear
- [ ] Logs are informative

## Summary

A robust testing strategy ensures reliable VMware automation:

1. **Component Testing**: Verify individual functions work
2. **Integration Testing**: Test phase transitions
3. **End-to-End Testing**: Validate complete workflows
4. **Error Testing**: Ensure graceful failure handling
5. **Performance Testing**: Monitor execution times
6. **Continuous Testing**: Automate test execution

Regular testing helps identify issues early and ensures the automation remains reliable across different environments and VM configurations. 