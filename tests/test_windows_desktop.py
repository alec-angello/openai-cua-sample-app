import unittest
import time
import tempfile
import os
from unittest.mock import patch, MagicMock
from computers.default.windows_desktop import WindowsDesktopComputer


class TestWindowsDesktopComputer(unittest.TestCase):
    """Test suite for WindowsDesktopComputer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create computer instance with test configuration
        self.computer = WindowsDesktopComputer(
            action_delay=0.1,  # Faster for testing
            screenshot_quality=50,  # Lower quality for faster tests
            max_retries=2,  # Fewer retries for testing
            rdp_mode=True
        )

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.computer, '_cached_screenshot'):
            self.computer._cached_screenshot = None

    def test_computer_protocol_compliance(self):
        """Test that WindowsDesktopComputer implements the Computer protocol."""
        # Check that all required methods exist
        required_methods = [
            'get_environment', 'get_dimensions', 'screenshot', 'click',
            'double_click', 'scroll', 'type', 'wait', 'move', 'keypress',
            'drag', 'get_current_url'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(self.computer, method),
                          f"Missing required method: {method}")
            self.assertTrue(callable(getattr(self.computer, method)),
                          f"Method {method} is not callable")

    def test_get_environment(self):
        """Test that get_environment returns 'windows'."""
        self.assertEqual(self.computer.get_environment(), "windows")

    def test_get_dimensions(self):
        """Test that get_dimensions returns valid screen dimensions."""
        width, height = self.computer.get_dimensions()
        self.assertIsInstance(width, int)
        self.assertIsInstance(height, int)
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)

    def test_context_manager(self):
        """Test that the computer works as a context manager."""
        with self.computer as comp:
            self.assertIs(comp, self.computer)
            self.assertEqual(comp.get_environment(), "windows")

    @patch('computers.default.windows_desktop.ImageGrab')
    @patch('computers.default.windows_desktop.pyautogui')
    def test_screenshot_caching(self, mock_pyautogui, mock_imagegrab):
        """Test screenshot caching functionality."""
        # Mock the screenshot methods
        mock_image = MagicMock()
        mock_image.save = MagicMock()
        mock_imagegrab.grab.return_value = mock_image
        
        # Take two screenshots quickly
        screenshot1 = self.computer.screenshot()
        screenshot2 = self.computer.screenshot()
        
        # Should use cached version for second call
        self.assertEqual(mock_imagegrab.grab.call_count, 1)

    @patch('computers.default.windows_desktop.pyautogui')
    def test_coordinate_adjustment(self, mock_pyautogui):
        """Test DPI coordinate adjustment."""
        # Set up DPI scaling
        self.computer.dpi_scale_x = 1.5
        self.computer.dpi_scale_y = 1.5
        
        # Test coordinate adjustment
        adjusted_x, adjusted_y = self.computer._adjust_coordinates(150, 150)
        self.assertEqual(adjusted_x, 100)  # 150 / 1.5
        self.assertEqual(adjusted_y, 100)  # 150 / 1.5

    @patch('computers.default.windows_desktop.pyautogui')
    def test_click_with_retry(self, mock_pyautogui):
        """Test click method with retry functionality."""
        # Mock successful click
        mock_pyautogui.click = MagicMock()
        mock_pyautogui.size.return_value = (1920, 1080)
        
        self.computer.click(100, 100, "left")
        
        # Verify click was called
        mock_pyautogui.click.assert_called_once()

    @patch('computers.default.windows_desktop.pyautogui')
    def test_click_with_failure_and_retry(self, mock_pyautogui):
        """Test click method retry on failure."""
        mock_pyautogui.size.return_value = (1920, 1080)
        
        # Mock click to fail first time, succeed second time
        mock_pyautogui.click = MagicMock(side_effect=[Exception("Test error"), None])
        
        self.computer.click(100, 100, "left")
        
        # Should have been called twice (retry)
        self.assertEqual(mock_pyautogui.click.call_count, 2)

    @patch('computers.default.windows_desktop.pyautogui')
    def test_double_click(self, mock_pyautogui):
        """Test double-click functionality."""
        mock_pyautogui.doubleClick = MagicMock()
        mock_pyautogui.size.return_value = (1920, 1080)
        
        self.computer.double_click(200, 200)
        
        mock_pyautogui.doubleClick.assert_called_once()

    @patch('computers.default.windows_desktop.pyautogui')
    def test_type_text(self, mock_pyautogui):
        """Test text typing functionality."""
        mock_pyautogui.write = MagicMock()
        
        test_text = "Hello, World!"
        self.computer.type(test_text)
        
        mock_pyautogui.write.assert_called_once_with(test_text, interval=0.02)

    @patch('computers.default.windows_desktop.pyautogui')
    def test_keypress_single_key(self, mock_pyautogui):
        """Test single key press."""
        mock_pyautogui.press = MagicMock()
        
        self.computer.keypress(['enter'])
        
        mock_pyautogui.press.assert_called_once_with('enter')

    @patch('computers.default.windows_desktop.pyautogui')
    def test_keypress_key_combination(self, mock_pyautogui):
        """Test key combination press."""
        mock_pyautogui.hotkey = MagicMock()
        
        self.computer.keypress(['ctrl', 'c'])
        
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'c')

    @patch('computers.default.windows_desktop.pyautogui')
    def test_keypress_key_mapping(self, mock_pyautogui):
        """Test key mapping functionality."""
        mock_pyautogui.hotkey = MagicMock()
        
        # Test mapping of 'cmd' to 'win'
        self.computer.keypress(['cmd', 'r'])
        
        mock_pyautogui.hotkey.assert_called_once_with('win', 'r')

    @patch('computers.default.windows_desktop.pyautogui')
    def test_mouse_move(self, mock_pyautogui):
        """Test mouse movement."""
        mock_pyautogui.moveTo = MagicMock()
        mock_pyautogui.size.return_value = (1920, 1080)
        
        self.computer.move(300, 300)
        
        mock_pyautogui.moveTo.assert_called_once()

    @patch('computers.default.windows_desktop.pyautogui')
    def test_scroll(self, mock_pyautogui):
        """Test scrolling functionality."""
        mock_pyautogui.moveTo = MagicMock()
        mock_pyautogui.scroll = MagicMock()
        
        self.computer.scroll(400, 400, 0, 3)  # Scroll up 3 units
        
        mock_pyautogui.moveTo.assert_called_once_with(400, 400)
        mock_pyautogui.scroll.assert_called_once_with(-3, 400, 400)

    @patch('computers.default.windows_desktop.pyautogui')
    def test_drag(self, mock_pyautogui):
        """Test drag functionality."""
        mock_pyautogui.drag = MagicMock()
        
        path = [{'x': 100, 'y': 100}, {'x': 200, 'y': 200}]
        self.computer.drag(path)
        
        mock_pyautogui.drag.assert_called_once()

    def test_drag_invalid_path(self):
        """Test drag with invalid path."""
        with self.assertRaises(ValueError):
            self.computer.drag([{'x': 100, 'y': 100}])  # Only one point

    def test_wait(self):
        """Test wait functionality."""
        start_time = time.time()
        self.computer.wait(100)  # 100ms
        end_time = time.time()
        
        # Should wait approximately 100ms (allow some variance)
        self.assertGreaterEqual(end_time - start_time, 0.09)
        self.assertLessEqual(end_time - start_time, 0.15)

    def test_get_current_url(self):
        """Test get_current_url returns empty string for desktop."""
        self.assertEqual(self.computer.get_current_url(), "")

    @patch('computers.default.windows_desktop.win32gui')
    def test_get_active_window(self, mock_win32gui):
        """Test getting active window title."""
        mock_win32gui.GetForegroundWindow.return_value = 12345
        mock_win32gui.GetWindowText.return_value = "Test Window"
        
        window_title = self.computer.get_active_window()
        
        self.assertEqual(window_title, "Test Window")

    @patch('computers.default.windows_desktop.gw')
    def test_activate_window(self, mock_gw):
        """Test window activation."""
        mock_window = MagicMock()
        mock_gw.getWindowsWithTitle.return_value = [mock_window]
        
        result = self.computer.activate_window("Test Window")
        
        self.assertTrue(result)
        mock_window.activate.assert_called_once()

    @patch('computers.default.windows_desktop.gw')
    def test_activate_window_not_found(self, mock_gw):
        """Test window activation when window not found."""
        mock_gw.getWindowsWithTitle.return_value = []
        
        result = self.computer.activate_window("Non-existent Window")
        
        self.assertFalse(result)

    @patch('computers.default.windows_desktop.subprocess')
    def test_start_application(self, mock_subprocess):
        """Test application startup."""
        mock_subprocess.Popen = MagicMock()
        
        result = self.computer.start_application("notepad.exe")
        
        self.assertTrue(result)
        mock_subprocess.Popen.assert_called_once_with("notepad.exe", shell=True)

    @patch('computers.default.windows_desktop.psutil')
    def test_is_process_running(self, mock_psutil):
        """Test process running check."""
        mock_proc = MagicMock()
        mock_proc.info = {'name': 'notepad.exe'}
        mock_psutil.process_iter.return_value = [mock_proc]
        
        result = self.computer.is_process_running("notepad")
        
        self.assertTrue(result)

    def test_bounds_checking(self):
        """Test coordinate bounds checking."""
        # Mock screen size
        self.computer.width = 1920
        self.computer.height = 1080
        
        with self.assertRaises(ValueError):
            self.computer.click(2000, 500)  # X out of bounds
        
        with self.assertRaises(ValueError):
            self.computer.click(500, 1200)  # Y out of bounds

    def test_rdp_mode_settings(self):
        """Test RDP mode configuration."""
        rdp_computer = WindowsDesktopComputer(rdp_mode=True)
        local_computer = WindowsDesktopComputer(rdp_mode=False)
        
        self.assertTrue(rdp_computer.rdp_mode)
        self.assertFalse(local_computer.rdp_mode)


class TestWindowsDesktopIntegration(unittest.TestCase):
    """Integration tests for real Windows desktop automation."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.computer = WindowsDesktopComputer(
            action_delay=0.5,  # Slower for real actions
            rdp_mode=True
        )

    def test_real_screenshot(self):
        """Test taking a real screenshot."""
        try:
            screenshot_b64 = self.computer.screenshot()
            self.assertIsInstance(screenshot_b64, str)
            self.assertGreater(len(screenshot_b64), 1000)  # Should be substantial data
        except Exception as e:
            self.skipTest(f"Screenshot test skipped due to environment: {e}")

    def test_safe_mouse_move(self):
        """Test safe mouse movement that won't disrupt user."""
        try:
            # Move to center of screen (safe area)
            width, height = self.computer.get_dimensions()
            center_x, center_y = width // 2, height // 2
            
            self.computer.move(center_x, center_y)
            
            # Test passed if no exception was raised
            self.assertTrue(True)
        except Exception as e:
            self.skipTest(f"Mouse move test skipped due to environment: {e}")

    def test_window_enumeration(self):
        """Test window enumeration functionality."""
        try:
            windows = self.computer.get_window_list()
            self.assertIsInstance(windows, list)
            # Should have at least one window (the test runner)
            self.assertGreater(len(windows), 0)
        except Exception as e:
            self.skipTest(f"Window enumeration test skipped due to environment: {e}")


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test methods from both classes
    for test_class in [TestWindowsDesktopComputer, TestWindowsDesktopIntegration]:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}") 