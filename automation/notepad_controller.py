import time
from pathlib import Path
from typing import Tuple
import config
from utils.logger import setup_logger
from utils.retry import retry_on_exception
from automation.mouse_controller import MouseController
from automation.keyboard_controller import KeyboardController
from automation.window_manager import WindowManager

logger = setup_logger(__name__)


class NotepadController:
    """High-level controller for Notepad automation."""
    
    def __init__(self):
        """Initialize Notepad controller with sub-controllers."""
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.window_manager = WindowManager()
        
        logger.info("Notepad controller initialized")
    
    @retry_on_exception(max_attempts=3, delay=1)
    def launch_notepad(self, coords: Tuple[int, int]) -> bool:
        """
        Launch Notepad by double-clicking icon.
        
        Args:
            coords: (x, y) coordinates of Notepad icon
        
        Returns:
            True if Notepad launched successfully
        
        Raises:
            RuntimeError: If Notepad fails to launch after retries
        """
        logger.info(f"Launching Notepad from coordinates {coords}")
        
        # Double-click the icon
        if not self.mouse.double_click(coords[0], coords[1]):
            raise RuntimeError("Failed to double-click Notepad icon")
        
        # Wait for Notepad window to appear
        logger.debug("Waiting for Notepad window...")
        window = self.window_manager.wait_for_window(
            "Notepad",
            timeout=config.WINDOW_WAIT_TIMEOUT
        )
        
        if not window:
            raise RuntimeError("Notepad window did not appear")
        
        # Activate the window
        time.sleep(0.5)
        self.window_manager.activate_window(window)
        
        logger.info("✓ Notepad launched successfully")
        return True
    
    def write_content(self, content: str) -> bool:
        """
        Write content to Notepad.
        
        Args:
            content: Text to write
        
        Returns:
            True if successful
        """
        logger.info(f"Writing content to Notepad (length: {len(content)})")
        
        # Use paste for faster and more reliable text entry
        success = self.keyboard.paste_text(content)
        
        if success:
            time.sleep(config.TYPE_DELAY * 5)  # Give time for large text
            logger.info("✓ Content written successfully")
        else:
            logger.error("✗ Failed to write content")
        
        return success
    
    def save_file(self, filepath: Path) -> bool:
        """
        Save Notepad content to file.
        
        Args:
            filepath: Full path where to save file
        
        Returns:
            True if successful
        """
        logger.info(f"Saving file: {filepath}")
        
        # Open Save dialog
        if not self.keyboard.save_file():
            logger.error("Failed to open Save dialog")
            return False
        
        time.sleep(config.SAVE_DIALOG_WAIT)
        
        # Type the full filepath
        if not self.keyboard.paste_text(str(filepath)):
            logger.error("Failed to enter filepath")
            return False
        
        time.sleep(0.5)
        
        # Press Enter to save
        if not self.keyboard.press_key('enter'):
            logger.error("Failed to press Enter")
            return False
        
        time.sleep(config.POST_SAVE_DELAY)
        logger.info("✓ File saved")
        return True
    
    def close_notepad(self, filename: str = None) -> bool:
        """
        Close Notepad window.
        
        Args:
            filename: Optional specific filename to close
        
        Returns:
            True if successful
        """
        if filename:
            # Close specific file
            title_pattern = f"{filename} - Notepad"
            logger.info(f"Closing Notepad window: {title_pattern}")
            count = self.window_manager.close_windows_by_title(title_pattern)
        else:
            # Close any Notepad window
            logger.info("Closing Notepad windows")
            count = self.window_manager.close_windows_by_title("Notepad")
        
        time.sleep(config.POST_CLOSE_DELAY)
        
        if count > 0:
            logger.info(f"✓ Closed {count} Notepad window(s)")
            return True
        else:
            logger.warning("No Notepad windows were closed")
            return False
    
    def write_post_to_file(
        self,
        content: str,
        filepath: Path,
        coords: Tuple[int, int]
    ) -> bool:
        """
        Complete workflow: Launch Notepad, write content, save, close.
        
        Args:
            content: Text content to write
            filepath: Where to save the file
            coords: Coordinates of Notepad icon
        
        Returns:
            True if entire workflow succeeded
        """
        filename = filepath.name
        logger.info(f"=== Writing post to {filename} ===")
        
        try:
            # 1. Launch Notepad
            if not self.launch_notepad(coords):
                raise RuntimeError("Failed to launch Notepad")
            
            # 2. Write content
            if not self.write_content(content):
                raise RuntimeError("Failed to write content")
            
            # 3. Save file
            if not self.save_file(filepath):
                raise RuntimeError("Failed to save file")
            
            # 4. Close Notepad
            if not self.close_notepad(filename):
                logger.warning("Failed to close Notepad (might need manual cleanup)")
            
            logger.info(f"✓ Successfully created {filename}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Workflow failed: {e}")
            
            # Attempt cleanup
            logger.info("Attempting cleanup...")
            self.window_manager.close_windows_by_title("Notepad")
            
            return False
    
    def verify_notepad_open(self) -> bool:
        """
        Verify that Notepad is currently open.
        
        Returns:
            True if Notepad window exists
        """
        is_open = self.window_manager.is_window_open("Notepad")
        
        if is_open:
            logger.debug("Notepad is currently open")
        else:
            logger.debug("Notepad is not open")
        
        return is_open
    
    def cleanup_all_notepad_windows(self) -> int:
        """
        Close all Notepad windows (useful for cleanup).
        
        Returns:
            Number of windows closed
        """
        logger.info("Cleaning up all Notepad windows...")
        count = self.window_manager.close_windows_by_title("Notepad", close_all=True)
        logger.info(f"Cleaned up {count} Notepad window(s)")
        return count


if __name__ == "__main__":
    # Test Notepad controller
    controller = NotepadController()
    print("Notepad controller ready")
    print("Note: Actual operations require Notepad to be on desktop")