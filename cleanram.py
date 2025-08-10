import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import pystray
import subprocess

# ---------------------- Configuration ----------------------
THEME = {
    'bg': '#23272e',
    'fg': '#f8f8f2',
    'accent': '#61afef',
    'button': '#282c34',
    'button_fg': '#f8f8f2',
    'status_ready': '#98c379',
    'status_cleaning': '#e5c07b',
    'status_done': '#56b6c2',
    'status_error': '#e06c75',
}
MIN_WIDTH, MIN_HEIGHT = 420, 340
GRAPH_SECONDS = 60

# ---------------------- RAM Cleaner Class ----------------------
class RAMCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('RAM Cleaner')
        self.root.configure(bg=THEME['bg'])
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)
        self.is_cleaning = False
        self.ram_history = [0] * GRAPH_SECONDS
        self.status_var = tk.StringVar(value='Ready')
        self.status_color = THEME['status_ready']
        self._setup_ui()
        self._setup_tray()
        self._update_ram_usage()
        self._update_graph()

    def _setup_ui(self):
        # Title
        title = tk.Label(self.root, text='RAM Cleaner', font=('Segoe UI', 20, 'bold'), bg=THEME['bg'], fg=THEME['accent'])
        title.pack(pady=(18, 6))
        # RAM Usage
        self.usage_var = tk.StringVar()
        usage_label = tk.Label(self.root, textvariable=self.usage_var, font=('Segoe UI', 13), bg=THEME['bg'], fg=THEME['fg'])
        usage_label.pack(pady=(0, 8))
        # Graph
        self.fig, self.ax = plt.subplots(figsize=(4.2, 1.5), dpi=100)
        self.fig.patch.set_facecolor(THEME['bg'])
        self.ax.set_facecolor(THEME['bg'])
        self.ax.tick_params(colors=THEME['fg'])
        self.ax.spines['bottom'].set_color(THEME['fg'])
        self.ax.spines['top'].set_color(THEME['fg'])
        self.ax.spines['right'].set_color(THEME['fg'])
        self.ax.spines['left'].set_color(THEME['fg'])
        self.line, = self.ax.plot([], [], color=THEME['accent'], linewidth=2)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, GRAPH_SECONDS)
        self.ax.set_ylabel('% Used', color=THEME['fg'])
        self.ax.set_xlabel('Seconds Ago', color=THEME['fg'])
        self.ax.set_xticks([0, 30, 60])
        self.ax.set_xticklabels(['60', '30', '0'])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(pady=(0, 8), fill='x', expand=False)
        # Clean Button
        self.clean_btn = tk.Button(self.root, text='Clean RAM', font=('Segoe UI', 12, 'bold'), bg=THEME['button'], fg=THEME['button_fg'], activebackground=THEME['accent'], activeforeground=THEME['fg'], command=self.clean_ram)
        self.clean_btn.pack(pady=(0, 10), ipadx=10, ipady=4)
        # Status
        self.status_label = tk.Label(self.root, textvariable=self.status_var, font=('Segoe UI', 11), bg=THEME['bg'], fg=self.status_color)
        self.status_label.pack(pady=(0, 8))
        # Make window resizable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _setup_tray(self):
        # Load tray icon
        icon_path = os.path.join(os.path.dirname(sys.argv[0]), 'ram_icon.ico')
        if not os.path.exists(icon_path):
            # Generate a simple icon if not present
            img = Image.new('RGBA', (64, 64), THEME['accent'])
            icon_path = os.path.join(os.path.dirname(sys.argv[0]), 'ram_icon_temp.ico')
            img.save(icon_path)
        image = Image.open(icon_path)
        menu = (
            pystray.MenuItem('Quick Clean', self.tray_quick_clean),
            pystray.MenuItem('Show Window', self.show_window),
            pystray.MenuItem('Exit', self.exit_app)
        )
        self.tray_icon = pystray.Icon('RAMCleaner', image, 'RAM Cleaner', menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _update_ram_usage(self):
        mem = psutil.virtual_memory()
        used_mb = (mem.total - mem.available) // (1024 * 1024)
        total_mb = mem.total // (1024 * 1024)
        percent = mem.percent
        self.usage_var.set(f'RAM Usage: {used_mb:,} MB / {total_mb:,} MB  ({percent:.1f}%)')
        self.ram_history.append(percent)
        if len(self.ram_history) > GRAPH_SECONDS:
            self.ram_history.pop(0)
        self.root.after(1000, self._update_ram_usage)

    def _update_graph(self):
        y = self.ram_history[-GRAPH_SECONDS:]
        x = list(range(len(y)))
        self.line.set_data(x, y)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, GRAPH_SECONDS)
        self.canvas.draw_idle()
        self.root.after(1000, self._update_graph)

    def set_status(self, text, color):
        self.status_var.set(text)
        self.status_label.config(fg=color)

    def clean_ram(self):
        if self.is_cleaning:
            return
        self.is_cleaning = True
        self.set_status('Cleaning…', THEME['status_cleaning'])
        self.clean_btn.config(state='disabled')
        threading.Thread(target=self._clean_ram_thread, daemon=True).start()

    def _clean_ram_thread(self):
        try:
            self._try_clean_ram()
            self.set_status('RAM cleaned successfully.', THEME['status_done'])
        except Exception as e:
            self.set_status(f'Error: {e}', THEME['status_error'])
        finally:
            self.clean_btn.config(state='normal')
            self.is_cleaning = False
            self.root.after(3000, lambda: self.set_status('Ready', THEME['status_ready']))

    def _try_clean_ram(self):
        # 1. Try EmptyStandbyList.exe if present
        exe_path = os.path.join(os.path.dirname(sys.argv[0]), 'EmptyStandbyList.exe')
        if os.path.exists(exe_path):
            try:
                subprocess.run([exe_path], check=True, timeout=10)
            except Exception as e:
                raise RuntimeError(f'Failed to run EmptyStandbyList.exe: {e}')
        # 2. Try to reduce memory of non-essential processes
        errors = []
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                if self._is_nonessential(proc):
                    p = psutil.Process(proc.info['pid'])
                    p.suspend()
                    p.resume()
                    if hasattr(p, 'memory_full_info'):
                        p.memory_full_info()
                    if hasattr(p, 'memory_info'):
                        p.memory_info()
            except Exception as ex:
                errors.append(str(ex))
        if errors:
            raise RuntimeError('Some processes could not be optimized.')

    def _is_nonessential(self, proc):
        # Don't touch system, service, or current process
        try:
            if proc.info['pid'] == os.getpid():
                return False
            if proc.info['username'] is None:
                return False
            if 'system' in (proc.info['username'] or '').lower():
                return False
            if proc.info['name'] and proc.info['name'].lower() in ['explorer.exe', 'winlogon.exe', 'csrss.exe', 'services.exe', 'lsass.exe', 'svchost.exe']:
                return False
            return True
        except Exception:
            return False

    # ---------------------- System Tray ----------------------
    def tray_quick_clean(self, icon, item):
        self.clean_ram()

    def show_window(self, *args):
        self.root.after(0, self._show_window)

    def _show_window(self):
        self.root.deiconify()
        self.root.after(0, self.root.lift)
        self.root.after(0, self.root.focus_force)

    def hide_window(self):
        self.root.withdraw()

    def exit_app(self, *args):
        self.tray_icon.stop()
        self.root.destroy()
        sys.exit(0)

# ---------------------- Main Entry ----------------------
def main():
    # Check for required modules
    try:
        import psutil, pystray, matplotlib, PIL
    except ImportError as e:
        messagebox.showerror('Missing Dependency', f'Missing required module: {e}.\nPlease install all dependencies.')
        sys.exit(1)
    root = tk.Tk()
    app = RAMCleanerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
