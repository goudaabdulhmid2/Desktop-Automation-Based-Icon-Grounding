import pyautogui
import pyperclip
import time
from typing import List
import config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class KeyboardController:
    """Handles all keyboard operations for automation."""
    
    def __init__(self, type_interval: float = None):
        """
        Initialize keyboard controller.
        
        Args:
            type_interval: Delay between keystrokes (uses config default if None)
        """
        self.type_interval = type_interval or config.TYPE_DELAY
        logger.info(f"Keyboard controller initialized (interval: {self.type_interval}s)")
    
    def type_text(self, text: str, interval: float = None, use_clipboard: bool = True) -> bool:
        """
        Type text.
        
        Args:
            text: Text to type
            interval: Delay between characters (None uses default)
            use_clipboard: If True, use paste instead of typing (faster)
        
        Returns:
            True if typing was successful
        """
        if use_clipboard:
            return self.paste_text(text)
        
        interval = interval or self.type_interval
        
        try:
            logger.debug(f"Typing text: '{text[:50]}...' (length: {len(text)})")
            pyautogui.write(text, interval=interval)
            return True
        except Exception as e:
            logger.error(f"Typing failed: {e}")
            return False
    
    def paste_text(self, text: str) -> bool:
        """
        Paste text using clipboard (faster than typing).
        
        Args:
            text: Text to paste
        
        Returns:
            True if paste was successful
        """
        try:
            logger.debug(f"Pasting text (length: {len(text)})")
            pyperclip.copy(text)
            time.sleep(0.1)  # Small delay for clipboard
            pyautogui.hotkey('ctrl', 'v')
            return True
        except Exception as e:
            logger.error(f"Paste failed: {e}")
            return False
    
    def press_key(self, key: str, presses: int = 1, interval: float = 0.1) -> bool:
        """
        Press a key.
        
        Args:
            key: Key name (e.g., 'enter', 'esc', 'tab')
            presses: Number of times to press
            interval: Delay between presses
        
        Returns:
            True if key press was successful
        """
        try:
            logger.debug(f"Pressing key: {key} (x{presses})")
            pyautogui.press(key, presses=presses, interval=interval)
            return True
        except Exception as e:
            logger.error(f"Key press failed: {e}")
            return False
    
    def hotkey(self, *keys: str) -> bool:
        """
        Press a hotkey combination.
        
        Args:
            *keys: Keys to press together (e.g., 'ctrl', 's')
        
        Returns:
            True if hotkey was successful
        """
        try:
            logger.debug(f"Pressing hotkey: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            logger.error(f"Hotkey failed: {e}")
            return False
    
    def save_file(self) -> bool:
        """Press Ctrl+S to save."""
        logger.info("Saving file (Ctrl+S)")
        return self.hotkey('ctrl', 's')
    
    def select_all(self) -> bool:
        """Press Ctrl+A to select all."""
        logger.debug("Selecting all (Ctrl+A)")
        return self.hotkey('ctrl', 'a')
    
    def copy(self) -> bool:
        """Press Ctrl+C to copy."""
        logger.debug("Copying (Ctrl+C)")
        return self.hotkey('ctrl', 'c')
    
    def cut(self) -> bool:
        """Press Ctrl+X to cut."""
        logger.debug("Cutting (Ctrl+X)")
        return self.hotkey('ctrl', 'x')
    
    def paste(self) -> bool:
        """Press Ctrl+V to paste."""
        logger.debug("Pasting (Ctrl+V)")
        return self.hotkey('ctrl', 'v')
    
    def undo(self) -> bool:
        """Press Ctrl+Z to undo."""
        logger.debug("Undoing (Ctrl+Z)")
        return self.hotkey('ctrl', 'z')
    
    def close_window(self) -> bool:
        """Press Alt+F4 to close window."""
        logger.debug("Closing window (Alt+F4)")
        return self.hotkey('alt', 'F4')


if __name__ == "__main__":
    # Test keyboard controller
    keyboard = KeyboardController()
    print("Keyboard controller ready")
    print("Note: Actual testing would type/press keys")
