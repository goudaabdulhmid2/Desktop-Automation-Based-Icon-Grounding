# Desktop Automation - Vision-Based Icon Grounding

Vision-based desktop automation system that uses computer vision to dynamically locate and interact with desktop icons on Windows, enabling robust automation even when icon positions change.

## 🎯 Project Overview

This project implements a complete desktop automation solution that:
- **Dynamically locates** Notepad desktop icon regardless of position
- **Fetches data** from JSONPlaceholder API (with fallback)
- **Automates Notepad** to create and save text files
- **Uses multi-strategy grounding** (template matching + OCR)
- **Handles errors gracefully** with retry logic

## 📁 Project Structure

```
tjm-project/
│
├── main.py                          # Entry point - orchestrates entire workflow
├── config.py                        # Centralized configuration
│
├── grounding/                       # Icon detection and grounding
│   ├── __init__.py
│   ├── base_grounding.py           # Abstract base class for strategies
│   ├── template_grounding.py       # Template matching (BotCity)
│   ├── ocr_grounding.py            # OCR-based detection (EasyOCR)
│   └── screenshot.py               # Screen capture utilities
│
├── automation/                      # Desktop automation controllers
│   ├── __init__.py
│   ├── mouse_controller.py         # Mouse operations
│   ├── keyboard_controller.py      # Keyboard operations
│   ├── window_manager.py           # Window management
│   └── notepad_controller.py       # Notepad-specific logic
│
├── data/                            # API and data handling
│   ├── __init__.py
│   ├── api_client.py               # JSONPlaceholder API client
│   └── fallback_data.json          # Backup data
│
├── utils/                           # Utilities
│   ├── __init__.py
│   ├── logger.py                   # Logging configuration
│   ├── retry.py                    # Retry decorators
│   └── validators.py               # Validation utilities
│
├── resources/                       # Template images
│   └── notepad_icon.png            # Notepad icon template
│
├── screenshots/                     # Debug screenshots
├── logs/                            # Log files
│
├── requirements.txt                 # Python dependencies
├── pyproject.toml                  # UV/pip configuration
└── README.md                        # This file
```

## 🚀 Installation

### Prerequisites

- **OS**: Windows 10/11
- **Resolution**: 1920x1080 (configurable)
- **Python**: 3.8 or higher
- **Notepad shortcut**: Must be on desktop

### Option 1: Using uv (Recommended)

```bash
# Install uv if you haven't
pip install uv

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Option 2: Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 3: Install with GPU support (for faster OCR)

```bash
pip install -e ".[gpu]"
```

## 📋 Setup

### 1. Create Notepad Desktop Shortcut

1. Right-click on Desktop → New → Shortcut
2. Enter location: `C:\Windows\System32\notepad.exe`
3. Name it "Notepad"
4. Place anywhere on your desktop

### 2. Prepare Template Image (Optional)

If you want to use template matching:

1. Take a screenshot of your Notepad icon
2. Crop just the icon (approximately 64x64 pixels)
3. Save as `resources/notepad_icon.png`

**Note**: The OCR fallback strategy works without a template!

### 3. Configure Settings

Edit `config.py` to adjust:
- Output directory path
- API timeout
- Grounding thresholds
- Window wait times
- etc.

## ▶️ Usage

### Basic Usage

```bash
python main.py
```

The script will:
1. Wait 5 seconds for you to prepare
2. Fetch 10 posts from JSONPlaceholder API
3. For each post:
   - Capture desktop screenshot
   - Locate Notepad icon
   - Launch Notepad
   - Write post content
   - Save to `Desktop/tjm-project/post_{id}.txt`
   - Close Notepad
4. Display completion statistics

### Custom Number of Posts

```python
# In main.py
if __name__ == "__main__":
    workflow = DesktopAutomationWorkflow()
    workflow.run(posts_count=5)  # Process only 5 posts
```

### Testing Grounding Only

```python
from grounding import MultiStrategyGrounding, AdaptiveTemplateGrounding, ScreenCapture

# Capture screen
screen = ScreenCapture.capture_screen()

# Try to locate Notepad
grounding = AdaptiveTemplateGrounding()
coords = grounding.locate(screen, "Notepad")
print(f"Notepad found at: {coords}")
```

## 🎨 Features

### ✅ Implemented

- ✅ **Multi-strategy grounding** (template + OCR fallback)
- ✅ **Retry logic** (3 attempts with 1s delay)
- ✅ **Window validation** (verifies Notepad opened)
- ✅ **Re-grounding per post** (fresh screenshot each time)
- ✅ **Error handling** (graceful degradation)
- ✅ **Flexible paths** (no hardcoded user directories)
- ✅ **Debug screenshots** (annotated with detection markers)
- ✅ **Comprehensive logging** (console + file)
- ✅ **API fallback** (local data when API unavailable)
- ✅ **Clean architecture** (modular, testable, extensible)

### 🔄 Architecture Improvements

**Original Code Issues Fixed:**

1. **Hardcoded paths** → Now uses `Path.home()` and config
2. **No retry logic** → Implemented decorator-based retries
3. **Single grounding attempt** → Multi-strategy with fallbacks
4. **Fixed sleep times** → Configurable timeouts
5. **No window validation** → Validates Notepad actually opened
6. **Tight coupling** → Separated concerns (mouse, keyboard, window, notepad)
7. **Poor error recovery** → Comprehensive exception handling

## 🧪 Testing

The project includes extensive logging for debugging. Check:

- **Console output**: Real-time progress
- **Log files**: `logs/automation_YYYYMMDD_HHMMSS.log`
- **Debug screenshots**: `screenshots/notepad_grounding_*.png`

### Manual Testing Steps

1. **Test with icon in top-left**:
   - Move Notepad icon to top-left of desktop
   - Run `python main.py`
   - Check `screenshots/` for annotated detection

2. **Test with icon in bottom-right**:
   - Move Notepad icon to bottom-right
   - Run again

3. **Test with icon in center**:
   - Move to center, run again

**Required**: Create 3 annotated screenshots showing successful detection in each position.

## ⚙️ Configuration

### Key Settings in `config.py`:

```python
# Paths
OUTPUT_DIR = DESKTOP_PATH / "tjm-project"
TEMPLATE_PATH = RESOURCES_DIR / "notepad_icon.png"

# Grounding
TEMPLATE_MATCH_THRESHOLD = 0.7
OCR_CONFIDENCE_THRESHOLD = 0.6
MAX_GROUNDING_ATTEMPTS = 3

# Timings
STARTUP_DELAY = 5
WINDOW_WAIT_TIMEOUT = 5
SAVE_DIALOG_WAIT = 2
```

## 🐛 Troubleshooting

### Issue: "Template not found"
**Solution**: Either create `resources/notepad_icon.png` or rely on OCR strategy (will fallback automatically)

### Issue: "Notepad window did not appear"
**Solutions**:
- Increase `WINDOW_WAIT_TIMEOUT` in config
- Ensure Notepad shortcut exists on desktop
- Check if another window is blocking Notepad

### Issue: "Could not locate Notepad icon"
**Solutions**:
- Check `screenshots/` for what was detected
- Lower `TEMPLATE_MATCH_THRESHOLD` to 0.5
- Lower `OCR_CONFIDENCE_THRESHOLD` to 0.4
- Ensure icon is not obscured by windows

### Issue: Import errors
**Solution**: Install missing dependencies:
```bash
pip install --break-system-packages <package-name>
```

## 📊 Code Quality Improvements

### Before (Original Code)

```python
# ❌ Hardcoded path
DESKTOP_PATH = os.path.join("C:\\Users\\gouda\\OneDrive", "Desktop")

# ❌ No retry
coords, screen_img = self.grounding.locate_target(program_name)

# ❌ No validation
pyautogui.doubleClick(coords[0], coords[1])
time.sleep(3)  # Hope it works!
```

### After (Refactored Code)

```python
# ✅ Dynamic path
DESKTOP_PATH = Path.home() / "Desktop"

# ✅ With retry
@retry_on_exception(max_attempts=3, delay=1)
def locate_notepad_icon(self):
    coords = self.grounding_system.locate(screenshot, "Notepad")
    if not coords:
        raise RuntimeError("Could not locate")
    return coords

# ✅ With validation
def launch_notepad(self, coords):
    self.mouse.double_click(coords)
    window = self.window_manager.wait_for_window("Notepad", timeout=5)
    if not window:
        raise RuntimeError("Notepad did not open")
```

## 📈 Performance

- **Icon detection**: ~1-3 seconds (depends on strategy)
- **Per post processing**: ~8-12 seconds
- **Total for 10 posts**: ~90-120 seconds

## 🔮 Future Enhancements

### Recommended (from project requirements):

1. **Vision model grounding** (OmniParser-style)
   - Can detect arbitrary UI elements without templates
   - Handles unexpected pop-ups
   - More flexible for general automation

2. **Multi-resolution support**
   - Currently optimized for 1920x1080
   - Could add dynamic scaling

3. **Theme support**
   - Handle light/dark themes
   - Different icon sizes

4. **Error recovery**
   - Screenshot on failure for debugging
   - Automatic recovery strategies

## 📄 License

This is a take-home project for demonstration purposes.

## 👤 Author

Your Name - Interview Candidate

## 🙏 Acknowledgments

- Project based on take-home assignment requirements
- OmniParser paper for grounding inspiration
- BotCity and EasyOCR for computer vision capabilities