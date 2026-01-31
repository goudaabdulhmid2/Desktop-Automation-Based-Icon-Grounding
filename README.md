# Desktop Automation - Vision-Based Icon Grounding

A robust, vision-based desktop automation system that utilizes the state-of-the-art **Florence-2 Vision-Language Model** to dynamically locate and interact with desktop icons. This system is designed to handle moving icons, unexpected pop-ups, and varying screen states without relying on brittle fixed coordinates.

## 🎯 Project Overview

This project implements a complete pipeline that:
1.  **Fetches Data**: Retrieves blog post data from JSONPlaceholder API (with local fallback).
2.  **Locates Target**: Uses Computer Vision (Florence-2) to find the "Notepad" icon on your desktop, regardless of where it is placed.
3.  **Automates Workflow**: Opens Notepad, types the content, saves the file to a specific folder, and closes the application.
4.  **Verifies**: checks window states and file creation to ensure success.

### Key Features

*   **🧠 Advanced Vision Grounding**: Uses Microsoft's **Florence-2** model to find UI elements by natural language description (e.g., "Notepad icon", "Save button"). No template images required!
*   **🛡️ Multi-Strategy Fallback**:
    1.  **Primary**: Vision Model (Florence-2) - flexible and robust.
    2.  **Secondary**: Template Matching (BotCity) - fast if standard icons are used.
    3.  **Tertiary**: OCR (Optical Character Recognition) - finds elements by reading text.
*   **☁️ Cloud-Aware**: Automatically detects Desktop path, including **OneDrive** configurations.
*   **⚡ Modern Stack**: Built with `uv` for fast, reliable dependency management.
*   **🔄 Reliability**: Built-in retry logic, comprehensive logging, and error recovery.

## 📁 Project Structure

```
tjm-project/
│
├── main.py                          # Entry point - orchestrates the workflow
├── config.py                        # Configuration (paths, timeouts, thresholds)
│
├── grounding/                       # Intelligence Layer
│   ├── vision_grounding.py         # Florence-2 Vision Model implementation
│   ├── template_grounding.py       # Template matching strategy
│   ├── ocr_grounding.py            # OCR strategy
│   └── screenshot.py               # Screen capture utilities
│
├── automation/                      # Action Layer
│   ├── notepad_controller.py       # Specific logic for Notepad
│   ├── mouse_controller.py         # Low-level mouse inputs
│   ├── keyboard_controller.py      # Low-level keyboard inputs
│   └── window_manager.py           # Window focus and management
│
├── data/                            # Data Layer
│   ├── api_client.py               # Fetches posts from API
│   └── fallback_data.json          # Offline backup data
│
├── utils/                           # Shared Utilities
│   ├── validators.py               # Path and coordinate validation
│   ├── retry.py                    # Retry decorators
│   └── logger.py                   # Logging setup
│
├── pyproject.toml                   # Project dependencies (uv)
├── uv.lock                         # Exact dependency version lockfile
└── requirements.txt                 # Legacy pip requirements
```

## 🚀 Installation

We use **uv** for ultra-fast package management.

### Prerequisites
*   Windows 10/11
*   Python 3.9 or higher
*   **Notepad** shortcut detected on your Desktop (Naming it "Notepad" is recommended).

### 1. Install uv
If you don't have it yet:
```powershell
pip install uv
```

### 2. Sync Dependencies
This will create a virtual environment and install all necessary packages (including PyTorch for the AI model).
```powershell
uv sync
```

> **Note**: The first run will download the Florence-2 model (~500MB). This is normal and happens only once.

## ▶️ Usage

### Run the Automation
To start the standard workflow (processing 10 posts):

```powershell
uv run main.py
```

### How it Works
1.  The script initializes and loads the AI models.
2.  It looks for a "Notepad" icon on your visible Desktop.
3.  For each post fetched from the API:
    *   It opens Notepad.
    *   Writes the post title and body.
    *   Saves it as `post_{id}.txt` in standard `Desktop/tjm-project` folder.
    *   Closes Notepad.

### Configuration
You can customize behavior in `config.py`:
*   **`POSTS_COUNT`**: Number of posts to process.
*   **`WINDOW_WAIT_TIMEOUT`**: How long to wait for Notepad to open.
*   **`SHOW_DEBUG_SCREENSHOTS`**: Save images showing where the AI found the icon.

## 🐛 Troubleshooting

*   **Desktop not found?**
    The system now automatically checks for `OneDrive\Desktop`. If your desktop is elsewhere, edit `config.py`.
*   **Notepad not opening?**
    Ensure the shortcut is on the main desktop screen and not covered by other windows.
*   **Dependency errors?**
    Run `uv sync` again to ensure your environment is clean.
