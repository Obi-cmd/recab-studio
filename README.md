# 🚀 Recab Studio 3.1

Recab Studio is a powerful, modern, open-source multi-language development environment for beginners and advanced developers alike.  
It combines a stunning UI with intelligent features like Gemini AI, a real terminal, code runner, and a full visual Blockly editor.

![Recab Banner](recab-logo.png)

---

## ✨ Features

✅ Multi-language support (Python, HTML, CSS, JavaScript, Java, C++, PHP, Go, SQL, Blockly)  
✅ Modern tabbed code editor with syntax highlighting  
✅ Google Gemini 1.5 AI assistant (with 2.5 fallback)  
✅ Live terminal — run system and pip commands  
✅ Code execution for multiple languages  
✅ Extensions system — drop .py scripts into the extensions folder  
✅ Drag-and-drop Blockly programming interface  
✅ Icon-based sidebar to switch languages  
✅ Rounded buttons, animations, modern PyQt6 UI  
✅ Project save/load support  
✅ Full installer and uninstaller  
✅ Completely open source under the MIT License

---

## 🖥️ Screenshot

> ![Preview](recab-logo.png)  
> Full UI, terminal, and Gemini integration in action.

---

## 📦 Installation

1. Clone this repository or download the ZIP  
2. Run the installer:

```bash
python recab_installer_gui.py
```

3. Or run directly:

```bash
python recab3.py
```

Requirements are in requirements.txt (see below).

---

## 🧠 AI Assistant (Gemini)

Recab Studio integrates Google Gemini 1.5 and 2.5.  
To activate it:

1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set it as an environment variable:

```bash
set GEMINI_API_KEY=your-key-here       # Windows
export GEMINI_API_KEY=your-key-here    # macOS/Linux
```

Gemini responses appear in the right panel. Use “Insert” to paste into code or “Keep” to save to disk.

---

## 🧱 Blockly Visual Coding

Accessible via the Blockly tab, Recab offers a drag-and-drop coding interface with themed blocks:

- Control, Logic, Loops
- Sensors, Video, Custom
- Full execution support and code export

---

## 📁 Folder Structure

```
Recab-Studio-3.1/
├── recab3.py                # Main app
├── recab_installer_gui.py  # Installer GUI
├── recab_uninstaller.py    # Uninstaller
├── LICENSE.txt
├── README.md
├── requirements.txt
├── assets/                 # Language icons and logos
├── blockly/                # HTML-based Blockly interface
├── extensions/             # Drop .py files here
└── temp/                   # Used to run files
```

---

## 🧩 Extensions System

Drop any .py plugin into the /extensions folder and it will auto-load into the Extensions tab.  
Use it to create:

- Custom language support
- New tool integrations
- Gemini prompt pre-processors
- Visualization or drawing tools

---

## 🧪 Requirements

Install with:

```bash
pip install -r requirements.txt
```

Dependencies:

- PyQt6
- PyQt6-WebEngine
- requests
- Pillow (optional for image generation)

---

## ⚖️ License

This project is licensed under the MIT License.  
See [LICENSE.txt](LICENSE.txt) for full terms and icon attribution.

---

## 👤 Credits

Created by [Obiakor Studios](https://github.com/obi-cmd)  
Language icons from Icons8 and Flaticon (see LICENSE)  
Recab logo is original and open source

---

## ⭐ Support & Contributions

Star ⭐ this repo, fork 🍴, and submit PRs to help make Recab better!  
All contributions are welcome — UI, icons, features, translations, anything!

---

Made with ❤️ using Python & Qt.
