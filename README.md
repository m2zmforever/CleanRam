# Advanced RAM Cleaner

A professional, production-ready RAM cleaner for Windows with a modern GUI and system tray integration.

## Features

- **Modern Tkinter GUI**: Clean, resizable window with dark theme.
- **Live RAM Usage**: Real-time display of used/total RAM and percentage.
- **Live Usage Graph**: 60-second RAM usage graph with smooth updates.
- **One-Click Cleaning**: Frees up unused memory without killing essential system processes.
- **System Tray Integration**: Minimize to tray, quick clean, show window, and exit from tray menu.
- **Standby Memory Cleaning**: Uses `EmptyStandbyList.exe` if present for deep cleaning.
- **Robust Error Handling**: Friendly messages and safe operations.

## Requirements

- Windows 10/11
- Python 3.8+
- The following Python packages:
  - `psutil`
  - `pystray`
  - `matplotlib`
  - `Pillow`

Install dependencies with:

```
pip install psutil pystray matplotlib pillow
```

## Usage

1. **Download** or clone this repository.
2. **(Optional)**: Place `EmptyStandbyList.exe` in the same directory for advanced standby memory cleaning.
3. Run the program:

```
python advanced_ram_cleaner.py
```

4. The app will appear in the system tray when minimized or closed. Use the tray icon for quick actions.

## System Tray Menu
- **Quick Clean**: Instantly free up RAM.
- **Show Window**: Restore the main window.
- **Exit**: Quit the application.

## Notes
- The app never kills essential system processes.
- All cleaning actions are safe and reversible.
- For best results, run as administrator.

## Screenshots

![Main Window](screenshots/main_window.png)
![System Tray](screenshots/tray_menu.png)

## License

MIT License. See [LICENSE](LICENSE) for details.

---

**Advanced RAM Cleaner** — Professional, safe, and modern memory optimization for Windows.
