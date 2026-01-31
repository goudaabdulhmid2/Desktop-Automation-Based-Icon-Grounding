import pygetwindow as gw
import time
from typing import List, Optional
import config
from utils.logger import setup_logger
from utils.validators import wait_for_window, find_window_by_title

logger = setup_logger(__name__)


class WindowManager:
    """Manages window operations - finding, activating, closing."""
    
    def __init__(self, activation_delay: float = None):
        """
        Initialize window manager.
        
        Args:
            activation_delay: Delay after activating windows
        """
        self.activation_delay = activation_delay or config.WINDOW_ACTIVATION_DELAY
        logger.info("Window manager initialized")
    
    def find_window(
        self,
        title_pattern: str,
        exact_match: bool = False
    ) -> Optional[gw.Win32Window]:
        """
        Find a window by title.
        
        Args:
            title_pattern: Window title or pattern
            exact_match: Require exact match
        
        Returns:
            Window object if found
        """
        return find_window_by_title(title_pattern, exact_match, timeout=0)
    
    def wait_for_window(
        self,
        title_pattern: str,
        timeout: float = None,
        exact_match: bool = False
    ) -> Optional[gw.Win32Window]:
        """
        Wait for a window to appear.
        
        Args:
            title_pattern: Window title pattern
            timeout: Max time to wait
            exact_match: Require exact match
        
        Returns:
            Window object if found within timeout
        """
        timeout = timeout or config.WINDOW_WAIT_TIMEOUT
        return wait_for_window(title_pattern, timeout, exact_match)
    
    def activate_window(self, window: gw.Win32Window) -> bool:
        """
        Activate (bring to front) a window.
        
        Args:
            window: Window to activate
        
        Returns:
            True if successful
        """
        if not window:
            logger.error("Cannot activate None window")
            return False
        
        try:
            logger.info(f"Activating window: {window.title}")
            window.activate()
            time.sleep(self.activation_delay)
            return True
        except Exception as e:
            logger.error(f"Failed to activate window: {e}")
            return False
    
    def close_window(self, window: gw.Win32Window, force: bool = False) -> bool:
        """
        Close a window.
        
        Args:
            window: Window to close
            force: If True, force close (kills process)
        
        Returns:
            True if successful
        """
        if not window:
            logger.error("Cannot close None window")
            return False
        
        try:
            logger.info(f"Closing window: {window.title}")
            
            if force:
                # Force close by killing process (more aggressive)
                import subprocess
                subprocess.run(['taskkill', '/F', '/PID', str(window._hWnd)], 
                             capture_output=True)
            else:
                # Normal close
                window.close()
            
            return True
        except Exception as e:
            logger.error(f"Failed to close window: {e}")
            return False
    
    def close_windows_by_title(
        self,
        title_pattern: str,
        close_all: bool = True
    ) -> int:
        """
        Close all windows matching title pattern.
        
        Args:
            title_pattern: Window title pattern
            close_all: If True, close all matches; otherwise just first
        
        Returns:
            Number of windows closed
        """
        windows = gw.getWindowsWithTitle(title_pattern)
        closed_count = 0
        
        for window in windows:
            try:
                window.activate()
                time.sleep(0.2)
                window.close()
                closed_count += 1
                logger.debug(f"Closed: {window.title}")
                
                if not close_all:
                    break
            except Exception as e:
                logger.warning(f"Failed to close {window.title}: {e}")
        
        if closed_count > 0:
            logger.info(f"Closed {closed_count} window(s) matching '{title_pattern}'")
        
        return closed_count
    
    def get_all_windows(self) -> List[gw.Win32Window]:
        """Get list of all visible windows."""
        return gw.getAllWindows()
    
    def get_active_window(self) -> Optional[gw.Win32Window]:
        """Get currently active window."""
        try:
            return gw.getActiveWindow()
        except Exception as e:
            logger.warning(f"Failed to get active window: {e}")
            return None
    
    def is_window_open(self, title_pattern: str) -> bool:
        """
        Check if window with title is open.
        
        Args:
            title_pattern: Window title pattern
        
        Returns:
            True if window exists
        """
        window = self.find_window(title_pattern)
        return window is not None
    
    def maximize_window(self, window: gw.Win32Window) -> bool:
        """
        Maximize a window.
        
        Args:
            window: Window to maximize
        
        Returns:
            True if successful
        """
        if not window:
            return False
        
        try:
            logger.debug(f"Maximizing window: {window.title}")
            window.maximize()
            return True
        except Exception as e:
            logger.error(f"Failed to maximize window: {e}")
            return False
    
    def minimize_window(self, window: gw.Win32Window) -> bool:
        """
        Minimize a window.
        
        Args:
            window: Window to minimize
        
        Returns:
            True if successful
        """
        if not window:
            return False
        
        try:
            logger.debug(f"Minimizing window: {window.title}")
            window.minimize()
            return True
        except Exception as e:
            logger.error(f"Failed to minimize window: {e}")
            return False


if __name__ == "__main__":
    # Test window manager
    wm = WindowManager()
    
    print("Current windows:")
    for window in wm.get_all_windows():
        print(f"  - {window.title}")
    
    active = wm.get_active_window()
    if active:
        print(f"\nActive window: {active.title}")