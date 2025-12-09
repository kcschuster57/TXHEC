import tkinter as tk
from tkinter import ttk
import threading
import State as state

# === Custom Widget Classes ===
class LabeledEntryWithUnit:
    def __init__(self, master, label, default, units, row):
        self.value = tk.StringVar(value=default)
        self.unit = tk.StringVar(value=units[0])

        tk.Label(master, text=label, font=('georgia', 10, 'bold')).grid(row=row, column=0, sticky="w")
        tk.Entry(master, textvariable=self.value, font=('calibre', 10)).grid(row=row, column=1, padx=4)

        if units[0] != "none":
            tk.OptionMenu(master, self.unit, *units).grid(row=row, column=2, padx=4)

    def get_value(self):
        try:
            return float(self.value.get())
        except ValueError:
            return None

    def get_unit(self):
        return self.unit.get()

    def set_value(self, val):
        self.value.set(str(val))

    def get_string(self):
        return str(self.value.get())

class LabeledOutputWithUnit:
    def __init__(self, master, label, default, units, largecolumn, row):
        self.value = tk.StringVar(value=default)
        self.unit = tk.StringVar(value=units)

        base_col = largecolumn * 3
        tk.Label(master, text=label, font=('georgia', 10, 'bold')).grid(row=row, column=0 + base_col, sticky="w")
        tk.Label(master, textvariable=self.value, font=('calibre', 10)).grid(row=row, column=1 + base_col)
        if units.lower() != "none":
            tk.Label(master, textvariable=self.unit, font=('georgia', 10, 'bold')).grid(row=row, column=2 + base_col)

    def set_value(self, val):
        self.value.set(str(val))

class HideableButton(tk.Button):
    """
    Button that can be shown/hidden, and manages its own .grid() internally.
    Safely separates widget options (like width/height) from geometry options (like row/column).
    """
    def __init__(self, master, text, showoninit=True, command=None, **kwargs):
        # Separate widget options from grid options
        widget_opts = {}
        grid_opts = {}

        for key, value in kwargs.items():
            if key in ("row", "column", "rowspan", "columnspan", "sticky", "padx", "pady"):
                grid_opts[key] = value
            else:
                widget_opts[key] = value

        super().__init__(master, text=text, command=command, **widget_opts)

        self._grid_options = grid_opts
        self._is_visible = False

        if showoninit:
            self.grid(**self._grid_options)
            self._is_visible = True

    def show(self):
        if not self._is_visible:
            self.grid(**self._grid_options)
            self._is_visible = True

    def hide(self):
        if self._is_visible:
            self.grid_remove()
            self._is_visible = False

class ProgressDialog:
    """
    Reusable modal progress dialog with:
    - Determinate progress bar
    - Threaded worker execution
    - Cancel button using threading.Event
    - Thread-safe update callback
    """

    def __init__(self, parent, title="Working...", message="Please wait..."):
        self.parent = parent
        self.title = title
        self.message = message

        self.stop_event = threading.Event()
        self._build_dialog()

    # ----------------------------------------------------
    # UI construction
    # ----------------------------------------------------
    def _build_dialog(self):
        self.win = tk.Toplevel(self.parent)
        self.win.title(self.title)
        self.win.geometry("320x160")
        self.win.resizable(False, False)
        self.win.transient(self.parent)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None)  # disable close
        self.win.grab_set()
        self.win.iconbitmap(state.resource_path("tex.ico"))
        ttk.Label(self.win, text=self.message, font=('Segoe UI', 10)).pack(pady=10)
        self.progress = ttk.Progressbar(self.win, length=250, mode='determinate')
        self.progress.pack(pady=10)

        self.label = ttk.Label(self.win, text="0%")
        self.label.pack()

        # Cancel button
        self.cancel_btn = ttk.Button(self.win, text="Cancel", command=self.cancel)
        self.cancel_btn.pack(pady=5)

        self._center()

    def _center(self):
        self.win.update_idletasks()
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        w  = self.win.winfo_reqwidth()
        h  = self.win.winfo_reqheight()
        x = int((sw/2) - (w/2))
        y = int((sh/2) - (h/2))
        self.win.geometry(f"+{x}+{y}")

    # ----------------------------------------------------
    # Public API
    # ----------------------------------------------------
    def update_progress(self, fraction: float):
        """Thread-safe progress update from worker."""
        def _do_update():
            pct = fraction * 100
            self.progress['value'] = pct
            self.label.config(text=f"{pct:.1f}%")
        self.win.after(0, _do_update)

    def cancel(self):
        self.stop_event.set()
        self.label.config(text="Stopping...")

    def close(self):
        self.win.after(0, self.win.destroy)

    def run(self, target, *args):
        """
        Launch worker thread.
        Worker receives:
          - update_progress callback
          - stop_event
        """
        thread = threading.Thread(
            target=self._run_worker,
            args=(target, args),
            daemon=True
        )
        thread.start()

    # ----------------------------------------------------
    # Internal worker wrapper
    # ----------------------------------------------------
    def _run_worker(self, target, args):
        try:
            # inject callback + stop event into worker
            result = target(self.update_progress, self.stop_event, *args)
        except Exception as e:
            print(f"Worker exception: {e}")
            result = None

        self.close()
        return result
