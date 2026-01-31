import os 
from pathlib import Path


# Paths
HOME_DIR = Path.home()
DESKTOP_PATH = HOME_DIR / "Desktop"
PROJECT_DIR_NAME = "tjm-project"
OUTPUT_DIR = DESKTOP_PATH / PROJECT_DIR_NAME

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()
RESOURCES_DIR = PROJECT_ROOT / "resources"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
TEMPLATE_PATH = RESOURCES_DIR / "notepad_icon.png"

# API Configuration
API_URL = "https://jsonplaceholder.typicode.com/posts"
API_TIMEOUT = 5
POSTS_COUNT = 10

# Grounding Configuration
TEMPLATE_MATCH_THRESHOLD = 0.7  
OCR_CONFIDENCE_THRESHOLD = 0.6
MAX_GROUNDING_ATTEMPTS = 3
GROUNDING_RETRY_DELAY = 1  

# Window Configuration
NOTEPAD_WINDOW_TITLES = ["Untitled - Notepad", "Notepad"]
WINDOW_WAIT_TIMEOUT = 5  
WINDOW_ACTIVATION_DELAY = 0.5

# Automation Timings
STARTUP_DELAY = 5  
DOUBLE_CLICK_INTERVAL = 0.3
TYPE_DELAY = 0.1
SAVE_DIALOG_WAIT = 2
POST_SAVE_DELAY = 1.5
POST_CLOSE_DELAY = 1

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# Debug Configuration
SAVE_DEBUG_SCREENSHOTS = True
DEBUG_MARKER_COLOR = "red"
DEBUG_MARKER_RADIUS = 15

def ensure_directories():
    """Create necessary directories if they don't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

def validate_config():
    """Validate configuration and check for required files."""
    errors = []
    
    if not DESKTOP_PATH.exists():
        errors.append(f"Desktop path does not exist: {DESKTOP_PATH}")
    

    if not TEMPLATE_PATH.exists():
        errors.append(f"Warning: Template file not found at {TEMPLATE_PATH}")
    
    return errors

if __name__ == "__main__":
    # For testing configuration
    print(f"Desktop Path: {DESKTOP_PATH}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Template Path: {TEMPLATE_PATH}")
    print(f"Project Root: {PROJECT_ROOT}")
    
    errors = validate_config()
    if errors:
        print("\nConfiguration Issues:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\nConfiguration validated successfully!")