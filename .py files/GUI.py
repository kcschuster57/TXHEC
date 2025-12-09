# chills CEAwrap the hell out
import subprocess
import sys
if sys.platform == "win32":
    CREATE_NO_WINDOW = 0x08000000
    orig_popen = subprocess.Popen

    def silent_popen(*args, **kwargs):
        kwargs.setdefault("creationflags", 0)
        kwargs["creationflags"] |= CREATE_NO_WINDOW
        return orig_popen(*args, **kwargs)

    subprocess.Popen = silent_popen

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from GUI_tab_tc import tab_tc
from GUI_tab_cea import tab_cea
from GUI_tab_tank import tab_tank
from GUI_tab_grain import tab_grain

import State as state



def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def create_splash(root):
    splash = tk.Toplevel()
    splash.overrideredirect(True)

    window_width = 900
    window_height = 900
    splash.geometry(f"{window_width}x{window_height}")
    splash.resizable(False, False)

    center_window(splash, window_width, window_height)

    original_image = Image.open(state.resource_path("TXHEC.png"))
    resized_image = original_image.resize((window_width, window_height))

    photo_image = ImageTk.PhotoImage(resized_image)
    splash.image = photo_image  # prevent garbage collection

    tk.Label(splash, image=photo_image).pack(fill="both", expand=True)

    return splash

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Texas Hybrid Engine Creator")
        self.geometry("1200x800")
        self.withdraw()
        self.iconbitmap(state.resource_path("tex.ico"))

        self.protocol("WM_DELETE_WINDOW", self.cleanup_and_exit)

        self.tabControl = ttk.Notebook(self)

        self.tab_cea = tab_cea(self.tabControl)
        self.tab_tc = tab_tc(self.tabControl, self.tab_cea)
        state.tab_tc_ref = self.tab_tc
        self.tab_grain = tab_grain(self.tabControl)

        self.tabControl.add(self.tab_tc, text="Thrust Curve Calculator")
        self.tabControl.add(self.tab_cea, text="NASA CEA")
        self.tabControl.add(self.tab_grain, text="Grain Geometry")

        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)

        self.tabControl.grid(column=0, row=0, sticky=tk.NSEW)

    def show_app(self):
        self.deiconify()

    def cleanup_and_exit(self):
        state.delete_file("my_output.plt")
        state.delete_file("my_output.out")
        state.delete_file("my_output.inp")
        state.delete_file("trans.lib")
        state.delete_file("thermo.lib")
        state.delete_file("grain_image.png")
        self.destroy()



if __name__ == "__main__":
    app = MainApp()

    splash = create_splash(app)

    def start_app():
        splash.destroy()
        app.show_app()

    app.after(2000, start_app)

    app.mainloop()
