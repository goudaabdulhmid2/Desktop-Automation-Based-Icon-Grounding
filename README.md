# Desktop Automation - Intelligent Icon Grounding

A robust, lightweight desktop automation system that dynamically locates and interacts with desktop icons using smart template matching and OCR. This system is designed to handle moving icons and varying desktop states with high reliability.

## 🎯 Project Overview

This project implements a complete pipeline that:
1.  **Fetches Data**: Retrieves blog post data from JSONPlaceholder API (with local fallback).
2.  **Locates Target**: Uses Adaptive Template Matching to find the "Notepad" icon on your desktop.
3.  **Automates Workflow**: Opens Notepad, types the content, saves the file to a specific folder, and closes the application.
4.  **Verifies**: checks window states and file creation to ensure success.

### Key Features

*   **🔍 Adaptive Template Matching**: Uses BotCity's advanced image matching with dynamic thresholding to find icons even if they are slightly different.
*   **� Optical Character Recognition (OCR)**: Falls back to reading text on the screen if the image match fails (using EasyOCR).
*   **☁️ Cloud-Aware**: Automatically detects Desktop path, including **OneDrive** configurations.
*   **⚡ Lightweight**: No heavy AI models (Torch/Transformers) required. Installs and runs instantly.
*   **🔄 Reliability**: Built-in retry logic, comprehensive logging, and error recovery.

## 📁 Project Structure

```
tjm-project/
│
├── main.py                          # Entry point - orchestrates the workflow
├── config.py                        # Configuration (paths, timeouts, thresholds)
│
├── grounding/                       # Intelligence Layer
│   ├── template_grounding.py       # Primary Strategy: Image matching
│   ├── ocr_grounding.py            # Secondary Strategy: Text reading
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
*   **Notepad** shortcut detected on your Desktop (saved as `resources/notepad_icon.png`).

### 1. Install uv
If you don't have it yet:
```powershell
pip install uv
```

### 2. Sync Dependencies
This will create a virtual environment and install all necessary packages.
```powershell
uv sync
```

## ▶️ Usage

### Run the Automation
To start the standard workflow (processing 10 posts):

```powershell
uv run main.py
```

### How it Works
1.  The system initializes.
2.  It looks for the "Notepad" icon using the image in `resources/notepad_icon.png`.
3.  For each post fetched from the API:
    *   It opens Notepad.
    *   Writes the post title and body.
    *   Saves it as `post_{id}.txt` in standard `Desktop/tjm-project` folder.
    *   Closes Notepad.

### Configuration
You can customize behavior in `config.py`:
*   **`POSTS_COUNT`**: Number of posts to process.
*   **`WINDOW_WAIT_TIMEOUT`**: How long to wait for Notepad to open.
*   **`SHOW_DEBUG_SCREENSHOTS`**: Save images showing where the system found the icon.

## 🐛 Troubleshooting

*   **Desktop not found?**
    The system now automatically checks for `OneDrive\Desktop`. If your desktop is elsewhere, edit `config.py`.
*   **Notepad not opening?**
    Ensure the shortcut is on the main desktop screen and not covered by other windows.
*   **Icon not found?**
    Make sure `resources/notepad_icon.png` matches how your Notepad icon looks on your current wallpaper. You might need to take a fresh screenshot/crop of your icon and replace that file.
