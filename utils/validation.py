from pathlib import Path
from typing import Optional, Tuple
import pygetwindow as gw
from utils.logger import setup_logger


logger = setup_logger(__name__)


def validate_coordinates(x: int, y: int, screen_width: int = 1920, screen_height: int = 1080) -> bool:
    """
    Validate that coordinates are within screen bounds.
    
    Args:
        x: X coordinate
        y: Y coordinate
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
    
    Returns:
        True if coordinates are valid
    """
    if not (0 <= x < screen_width):
        logger.warning(f"X coordinate {x} is out of bounds (0-{screen_width})")
        return False
    
    if not (0 <= y < screen_height):
        logger.warning(f"Y coordinate {y} is out of bounds (0-{screen_height})")
        return False
    
    return True


def validate_file_path(path: Path, must_exist: bool = False) -> bool:
    """
    Validate a file path.
    
    Args:
        path: Path to validate
        must_exist: If True, path must exist
    
    Returns:
        True if path is valid
    """
    try:
        path = Path(path)
        
        if must_exist and not path.exists():
            logger.error(f"Path does not exist: {path}")
            return False
        
        # Check if parent directory exists (or can be created)
        if not path.parent.exists():
            logger.warning(f"Parent directory does not exist: {path.parent}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Invalid path: {e}")
        return False


def find_window_by_title(
    title_pattern: str,
    exact_match: bool = False,
    timeout: float = 0
) -> Optional[gw.Win32Window]:
    """
    Find a window by title.
    
    Args:
        title_pattern: Window title or pattern to search for
        exact_match: If True, require exact title match
        timeout: How long to wait for window (0 = don't wait)
    
    Returns:
        Window object if found, None otherwise
    """
    import time
    start_time = time.time()
    
    while True:
        try:
            all_windows = gw.getAllWindows()
            
            for window in all_windows:
                if exact_match:
                    if window.title == title_pattern:
                        logger.debug(f"Found window: {window.title}")
                        return window
                else:
                    if title_pattern.lower() in window.title.lower():
                        logger.debug(f"Found window: {window.title}")
                        return window
            
            # Check timeout
            if timeout <= 0 or (time.time() - start_time) >= timeout:
                break
            
            time.sleep(0.2)
            
        except Exception as e:
            logger.warning(f"Error finding window: {e}")
            break
    
    logger.debug(f"Window not found: {title_pattern}")
    return None


def wait_for_window(
    title_pattern: str,
    timeout: float = 5.0,
    exact_match: bool = False
) -> Optional[gw.Win32Window]:
    """
    Wait for a window to appear.
    
    Args:
        title_pattern: Window title pattern to wait for
        timeout: Maximum time to wait in seconds
        exact_match: Require exact title match
    
    Returns:
        Window object if found within timeout, None otherwise
    """
    logger.info(f"Waiting for window: '{title_pattern}' (timeout: {timeout}s)")
    
    window = find_window_by_title(title_pattern, exact_match, timeout)
    
    if window:
        logger.info(f"✓ Window appeared: {window.title}")
    else:
        logger.warning(f"✗ Window did not appear within {timeout}s")
    
    return window


def verify_window_active(title_pattern: str) -> bool:
    """
    Verify that a window with the given title is currently active.
    
    Args:
        title_pattern: Window title pattern
    
    Returns:
        True if window is active
    """
    try:
        active_window = gw.getActiveWindow()
        if active_window and title_pattern.lower() in active_window.title.lower():
            logger.debug(f"Window is active: {active_window.title}")
            return True
        else:
            logger.debug(f"Window not active. Current: {active_window.title if active_window else 'None'}")
            return False
    except Exception as e:
        logger.warning(f"Error checking active window: {e}")
        return False


def get_screen_size() -> Tuple[int, int]:
    """
    Get current screen size.
    
    Returns:
        Tuple of (width, height)
    """
    import pyautogui
    size = pyautogui.size()
    return size.width, size.height


if __name__ == "__main__":
    # Test validators
    print("Testing validators...")
    
    # Test coordinates
    print(f"Valid coords (100, 100): {validate_coordinates(100, 100)}")
    print(f"Invalid coords (2000, 100): {validate_coordinates(2000, 100)}")
    
    # Test file paths
    test_path = Path("/tmp/test_file.txt")
    print(f"Valid path: {validate_file_path(test_path)}")
    print(f"Existing path: {validate_file_path(test_path, must_exist=True)}")
    
    # Test screen size
    width, height = get_screen_size()
    print(f"Screen size: {width}x{height}")
    
    # Test window finding (will likely not find anything in test environment)
    window = find_window_by_title("Notepad", timeout=1)
    print(f"Found Notepad: {window is not None}")
