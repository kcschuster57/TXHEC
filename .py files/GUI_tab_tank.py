import tkinter as tk
from labeled_widgets import LabeledEntryWithUnit, LabeledOutputWithUnit

class tab_tank(tk.Frame):
    def __init__(self, master):
        super().__init__(master, borderwidth=0)
        self.create_widgets()

    def create_widgets(self):
        # === Frames ===
        self.frame_tank_physical = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        self.frame_tank_physical.grid(row=0, column=0)
        self.frame_tank_other = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        self.frame_tank_other.grid(row=1, column=0)
        self.frame_tank_results = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        self.frame_tank_results.grid(row=2, column=0)

        # === Labels ===
        self.label_frame_tank_physical = tk.Label(self.frame_tank_physical, text='Tank Physical Properties', font=('georgia',10,'bold'))
        self.label_frame_tank_physical.grid(row=0, column=0, columnspan=3)

        # === Tank physical entries ===
        self.tank_OD = LabeledEntryWithUnit(master=self.frame_tank_physical, label="Outer Diameter",
                                           default="0.168275", units=["m","mm","in"], row=1)
        self.tank_ID = LabeledEntryWithUnit(master=self.frame_tank_physical, label="Inner Diameter",
                                           default="0.1614678", units=["m","mm","in"], row=2)
        self.tank_Length = LabeledEntryWithUnit(master=self.frame_tank_physical, label="Tank Length",
                                               default="2.9718", units=["m","mm","in"], row=3)
        self.tank_Strength = LabeledEntryWithUnit(master=self.frame_tank_physical, label="Tensile Yield Strength",
                                                 default="276", units=["MPa","psi"], row=4)
        self.tank_Pressure = LabeledEntryWithUnit(master=self.frame_tank_physical, label="Tank MEOP",
                                                 default="5.51", units=["MPa","psi"], row=5)

        # === Other tank entries ===
        self.tank_Temp = LabeledEntryWithUnit(master=self.frame_tank_other, label="Tank Temperature",
                                             default="298", units=["K","F","C"], row=0)
        self.tullage = LabeledEntryWithUnit(master=self.frame_tank_other, label="Ullage %",
                                           default="10", units=["none"], row=1)

        # === Buttons ===
        self.button_tank_run = tk.Button(master=self, text="Run Tank Calculations", height=2, width=20, command=self.tank_run)
        self.button_tank_run.grid(row=6, column=0)

        self.button_send_tankdata = tk.Button(master=self, text="Send Tank Data to TC Sim", height=2, width=20, command=self.tank_send_data)
        self.button_send_tankdata.grid(row=12, column=0)

        # === Outputs ===
        self.output_TOX = LabeledOutputWithUnit(self.frame_tank_results, "Projected Oxidizer Mass:", "Run Simulation", "kg", 0, 0)
        self.output_TV = LabeledOutputWithUnit(self.frame_tank_results, "Tank Volume:", "Run Simulation", "m^3", 0, 1)
        self.output_SF = LabeledOutputWithUnit(self.frame_tank_results, "Factor of Safety:", "Run Simulation", "none", 0, 2)

    # === Placeholder methods ===
    def tank_run(self):
        print("Tank Run placeholder")

    def tank_send_data(self):
        print("Send Tank Data placeholder")

