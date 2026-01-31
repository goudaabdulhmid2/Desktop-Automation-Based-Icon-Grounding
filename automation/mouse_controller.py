import pyautogui
import time
import config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MouseController:
    """Handles all mouse operations for automation."""
    
    def __init__(self):
        """Initialize mouse controller."""
        logger.info("Mouse controller initialized")
        
    def move_to(self, x: int, y: int, duration: float = 0.5) -> bool:
        """Move mouse to coordinates."""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"Failed to move mouse: {e}")
            return False

    def click(self, x: int, y: int) -> bool:
        """Click at coordinates."""
        try:
            self.move_to(x, y)
            pyautogui.click(x, y)
            return True
        except Exception as e:
            logger.error(f"Failed to click: {e}")
            return False

    def double_click(self, x: int, y: int) -> bool:
        """Double click at coordinates."""
        try:
            self.move_to(x, y)
            pyautogui.doubleClick(x, y)
            return True
        except Exception as e:
            logger.error(f"Failed to double click: {e}")
            return False
