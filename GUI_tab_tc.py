import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import traceback
import threading
from pathlib import Path
import State as state
import thrustmodel as thrust
from collections.abc import Iterable
import csv
import os

from labeled_widgets import LabeledEntryWithUnit, LabeledOutputWithUnit, HideableButton, ProgressDialog

class tab_tc(tk.Frame):
    def __init__(self, master,tab_cea_ref):
        super().__init__(master, borderwidth=0)
        self.tab_cea = tab_cea_ref
        self.create_widgets()

    def create_widgets(self):
        frame_tank_inputs = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        frame_tank_inputs.grid(row=0, column=0)

        frame_injector_inputs = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        frame_injector_inputs.grid(row=1, column=0)

        frame_fuel_inputs = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        frame_fuel_inputs.grid(row=2, column=0)

        frame_other_inputs = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        frame_other_inputs.grid(row=3, column=0)

        frame_outputs = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        frame_outputs.grid(row=5, column=0)

        frame_graph_settings = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        frame_graph_settings.grid(row=6, column=0)

        frame_loaded_check = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        frame_loaded_check.grid(row=7,column = 0)
        
        #Checks
        self.ceacanvas = tk.Canvas(frame_loaded_check, width=20, height=20, bg="red")
        self.ceacanvas.grid(row=0,column = 1,padx = 5)
        
        self.cea_loaded = tk.Label(frame_loaded_check, text='CEA Configured?', font=('georgia',10,'bold'))
        self.cea_loaded.grid(row=0, column=0)
        
        self.gcanvas = tk.Canvas(frame_loaded_check, width=20, height=20, bg="red")
        self.gcanvas.grid(row=1,column = 1,padx = 5)
        
        self.grain_loaded = tk.Label(frame_loaded_check, text='Grain Configured?', font=('georgia',10,'bold'))
        self.grain_loaded.grid(row=1, column=0)




        # === DROPDOWNS ===
        self.unit_xaxis = tk.StringVar(value="Time")
        options_unit_unit_xaxis = [
            "Time", "Thrust", "Temperature", "Tank Pressure", "CC Pressure", "Pressure Drop",
            "Ox Flow Rate", "Ox Mass", "Gas Mass", "Ox Mass Flux", "Regression Rate",
            "Fuel Mass Flow Rate", "O/F Ratio", "Fuel Mass"
        ]
        label_xaxis = tk.Label(frame_graph_settings, text="X-Axis:", font=('georgia', 10, 'bold'))
        drop_xaxis = tk.OptionMenu(frame_graph_settings, self.unit_xaxis, *options_unit_unit_xaxis)
        label_xaxis.grid(row=0, column=0)
        drop_xaxis.grid(row=0, column=1)

        self.unit_yaxis = tk.StringVar(value="Thrust")
        options_unit_unit_yaxis = options_unit_unit_xaxis.copy()
        label_yaxis = tk.Label(frame_graph_settings, text="Y-Axis:", font=('georgia', 10, 'bold'))
        drop_yaxis = tk.OptionMenu(frame_graph_settings, self.unit_yaxis, *options_unit_unit_yaxis)
        label_yaxis.grid(row=1, column=0)
        drop_yaxis.grid(row=1, column=1)

        self.unit_ox_flux = tk.StringVar(value="kg/m^2")
        options_unit_ox_flux = ["g/cm^2", "kg/m^2"]
        label_ox_flux = tk.Label(frame_fuel_inputs, text='Ox Flux Units', font=('georgia', 10, 'bold'))
        drop_ox_flux = tk.OptionMenu(frame_fuel_inputs, self.unit_ox_flux, *options_unit_ox_flux)
        label_ox_flux.grid(row=2, column=0)
        drop_ox_flux.grid(row=2, column=1)

        # === INPUTS ===
        self.tc_init_Tank_Temp = LabeledEntryWithUnit(frame_tank_inputs, "Tank Temperature", "298", ["K", "F", "C"], 1)
        self.tc_Volume = LabeledEntryWithUnit(frame_tank_inputs, "Tank Volume", "0.06174661", ["m^3", "cm^3", "in^3"], 2)
        self.tc_Ullage = LabeledEntryWithUnit(frame_tank_inputs, "Ullage %", "10", ["none"], 3)
        self.tc_discharge_Coefficient = LabeledEntryWithUnit(frame_injector_inputs, "Discharge Coefficient", "0.82", ["none"], 0)
        self.tc_total_Injector_Area = LabeledEntryWithUnit(frame_injector_inputs, "Total Injector Area", "0.00006925", ["m^2", "mm^2", "in^2"], 1)
        self.tc_port_Length = LabeledEntryWithUnit(frame_fuel_inputs, "Port Length", "1.1", ["m", "mm", "in"], 0)
        self.tc_fuel_Density = LabeledEntryWithUnit(frame_fuel_inputs, "Fuel Density", "975", ["kg/m^3"], 1)
        self.tc_a = LabeledEntryWithUnit(frame_fuel_inputs, "a", "0.038", ["none"], 3)
        self.tc_n = LabeledEntryWithUnit(frame_fuel_inputs, "n", "0.7", ["none"], 4)
        self.tc_throat_diameter = LabeledEntryWithUnit(frame_other_inputs, "Nozzle Throat Diameter", "0.057686", ["m", "mm", "in"], 2)
        self.tc_exit_diameter = LabeledEntryWithUnit(frame_other_inputs, "Nozzle Exit Diameter", "0.115372", ["m", "mm", "in"], 3)
        self.tc_engine_efficiency = LabeledEntryWithUnit(frame_other_inputs, "Engine Efficiency %", "100", ["none"], 1)

        # === OUTPUTS ===
        self.output_oxidizer_Mass = LabeledOutputWithUnit(frame_outputs, "Oxidizer Mass:", "Run Simulation", "kg", 0, 1)
        self.output_prop_Mass = LabeledOutputWithUnit(frame_outputs, "Propellant Mass:", "Run Simulation", "kg", 0, 0)
        self.output_prop_after_Burn = LabeledOutputWithUnit(frame_outputs, "Fuel Remaining After Burn:", "Run Simulation", "kg", 0, 2)
        self.output_total_Impulse = LabeledOutputWithUnit(frame_outputs, "Total Impulse:", "Run Simulation", "Ns", 1, 0)
        self.output_engine_Class = LabeledOutputWithUnit(frame_outputs, "Engine Class:", "Run Simulation", "none", 1, 2)
        self.output_specific_Impulse = LabeledOutputWithUnit(frame_outputs, "Specific Impulse:", "Run Simulation", "s", 1, 1)

        # === BUTTONS ===
        use_bcc_button = HideableButton(frame_fuel_inputs, text="Use BCC Values", showoninit=1, command=self.get_bcc_data, height=2, width=15, row=5, column=0,columnspan=3)
        sim_button = HideableButton(self, text="Run Sim", showoninit=1, command=self.run_simulation, height=2, width=10, row=8, column=0)
        plot_button = HideableButton(self, text="Plot", showoninit=1, command=self.plot, height=2, width=10, row=9, column=0)
        clear_plot_button = HideableButton(self, text="Clear Plot", showoninit=1, command=self.clear_plot, height=2, width=10, row=9, column=1)
        save_button = HideableButton(self, text="Save as .eng", showoninit=1, command=self.save, height=2, width=10, row=10, column=0)
        export_simulation_button = HideableButton(self, text="Export Data", showoninit=1, command=self.export_simulation_to_csv, height=2, width=12, row=10, column=1,columnspan =2)

        # === PLOT ===
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.18, right=.9, top=.9, bottom=0.15)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=3, rowspan=9, columnspan=9)



    def clear_cea_hold(self):
        self.ceacanvas.create_rectangle(0, 0, 22, 22, fill="green")

    def clear_grain_hold(self):
        self.gcanvas.create_rectangle(0, 0, 22, 22, fill="green")


    def plot(self):
        simtc = state.simulation_result  # stored by simtc() earlier
        xaxisunit = self.unit_xaxis.get()
        yaxisunit = self.unit_yaxis.get()

        # Map dropdowns to data lists
        x = getattr(simtc, self.map_axis_to_attr(xaxisunit), simtc.time)
        y = getattr(simtc, self.map_axis_to_attr(yaxisunit), simtc.thrust)

        units_labels = {
            "Time": "Time (s)",
            "Thrust": "Thrust (N)",
            "Temperature": "Temperature (K)",
            "Tank Pressure": "Tank Pressure (Pa)",
            "CC Pressure": "Chamber Pressure (Pa)",
            "Pressure Drop": "Pressure Drop (Pa)",
            "Ox Flow Rate": "Ox Flow Rate (kg/s)",
            "Ox Mass": "Ox Mass (kg)",
            "Gas Mass": "Gas Mass (kg)",
            "Ox Mass Flux": "Ox Mass Flux (kg/m^2-s)",
            "Regression Rate": "Regression Rate (m/s)",
            "Fuel Mass Flow Rate": "Fuel Mass Flow Rate (kg/s)",
            "O/F Ratio": "O/F Ratio (dimensionless)",
            "Fuel Mass": "Fuel Mass (kg)",
        }

        self.ax.clear()
        self.ax.scatter(x, y)
        self.ax.set_ylim(bottom=0, top=max(y) * 1.05 if len(y) else 1)
        self.ax.set_xlabel(units_labels.get(xaxisunit, xaxisunit))
        self.ax.set_ylabel(units_labels.get(yaxisunit, yaxisunit))
        self.canvas.draw()

    def clear_plot(self):
        self.ax.cla()
        self.canvas.draw()

    def map_axis_to_attr(self, axis_name):
        # Convert axis label to matching attribute name in simulation object
        mapping = {
            "Time": "time",
            "Thrust": "thrust",
            "Temperature": "temperature",
            "Tank Pressure": "tank_pressure",
            "CC Pressure": "cc_pressure",
            "Pressure Drop": "pressure_drop",
            "Ox Flow Rate": "ox_flow_rate",
            "Ox Mass": "ox_mass",
            "Gas Mass": "gas_mass",
            "Ox Mass Flux": "ox_mass_flux",
            "Regression Rate": "regression_rate",
            "Fuel Mass Flow Rate": "fuel_mass_flow_rate",
            "O/F Ratio": "of_ratio",
            "Fuel Mass": "fuel_mass",
        }
        return mapping.get(axis_name, "time")

    def run_simulation(self):

        if(state.grain_config == 0):
            messagebox.showinfo("Sim Failed","Need to run Grain Simulation first")
            return()
        if(state.cea_config == 0):
            messagebox.showinfo("Sim Failed","Need to lock CEA propellants")
            return()
        if(state.locked_oxid_string != "N 2 O 1"):
            messagebox.showinfo("WARNING","Model only designed to work with Nitrous Oxide; Sim results will be inaccurate")

        progbar = ProgressDialog(self, "Running Simulation...", "Simulating... Please wait.")

        def worker(update, stop_event):
            try:
                result = thrust.dosim(
                    state.convert_by_unit(self.tc_init_Tank_Temp.get_value(), self.tc_init_Tank_Temp.get_unit()),
                    state.convert_by_unit(self.tc_Volume.get_value(), self.tc_Volume.get_unit()),
                    float(self.tc_Ullage.get_value()),
                    float(self.tc_discharge_Coefficient.get_value()),
                    state.convert_by_unit(self.tc_total_Injector_Area.get_value(), self.tc_total_Injector_Area.get_unit()),
                    state.convert_by_unit(self.tc_port_Length.get_value(), self.tc_port_Length.get_unit()),
                    state.convert_by_unit(self.tc_fuel_Density.get_value(), self.tc_fuel_Density.get_unit()),
                    self.unit_ox_flux.get(),
                    float(self.tc_a.get_value()),
                    float(self.tc_n.get_value()),
                    state.convert_by_unit(self.tc_throat_diameter.get_value(), self.tc_throat_diameter.get_unit()),
                    state.convert_by_unit(self.tc_exit_diameter.get_value(), self.tc_exit_diameter.get_unit()),
                    float(self.tc_engine_efficiency.get_value()),
                    update,       # progress callback
                    stop_event    # stop handling
                )

                # After computation finishes
                state.simulation_result = result
                self.output_oxidizer_Mass.set_value(state.simulation_result.output_oxidizer_Mass)
                self.output_prop_Mass.set_value(state.simulation_result.output_prop_Mass)
                self.output_prop_after_Burn.set_value(state.simulation_result.output_prop_after_Burn)
                self.output_total_Impulse.set_value(state.simulation_result.output_total_Impulse)
                self.output_engine_Class.set_value(state.simulation_result.output_engine_Class)
                self.output_specific_Impulse.set_value(state.simulation_result.output_specific_Impulse)
                if(state.simulation_result.output_prop_after_Burn <= 0):
                    messagebox.showinfo("WARNING","All fuel was consumed during burn, resulting in engine burnout")
            except Exception as e:
                print("ERROR in worker:")
                traceback.print_exc()
                raise   # re-raise so the main process still sees it


        progbar.run(worker)

    def get_bcc_data(self):
        if(state.ballistic_a == -1):
            messagebox.showinfo("Data Not Available","Need to run Ballistic Coefficients Calculator")
            return()
        self.tc_a.set_value(state.ballistic_a)
        self.tc_n.set_value(state.ballistic_n)
        messagebox.showinfo("WARNING","Make sure that the Ox Flux units are set to kg/m^2; Also, Port length and density are not carried over from BCC")

    def save(self):
        save_window = tk.Toplevel()
        save_window.geometry("350x150")
        save_window.iconbitmap(state.resource_path("tex.ico"))
        motor_name = LabeledEntryWithUnit(
        master=save_window,
        label="Motor Name:",
        default="",
        units=["none"],
        row=0
        )
        motor_diameter = LabeledEntryWithUnit(
        master=save_window,
        label="Motor Diameter:",
        default="",
        units=["mm"],
        row=1
        )
        motor_length = LabeledEntryWithUnit(
        master=save_window,
        label="Motor Length:",
        default="",
        units=["mm"],
        row=2
        )
        motor_manu = LabeledEntryWithUnit(
        master=save_window,
        label="Manufacturer:",
        default="",
        units=["none"],
        row=3
        )
        downloads_path = str(Path.home() / "Downloads")
    
        def write():
            write_var_name = str(motor_name.get_string())
            write_var_diameter = str(motor_diameter.get_value())
            write_var_length = str(motor_length.get_value())
            write_var_manu = str(motor_manu.get_string())
            write_burn_prop = str(float(state.simulation_result.output_prop_Mass)-float(state.simulation_result.output_prop_after_Burn))
            write_total_prop = str(state.simulation_result.output_prop_Mass)
            types = [('RASP File Format', '*.eng')] 
            file_path = filedialog.asksaveasfilename(title="Save Motor File",defaultextension=".eng", filetypes=types, initialdir=downloads_path)
            if file_path != None:
                file_writer = open(file_path, mode = "w")
                file_writer.write(write_var_name)
                file_writer.write(" ")
                file_writer.write(write_var_diameter)
                file_writer.write(" ")
                file_writer.write(write_var_length)
                file_writer.write(" ")
                file_writer.write("P")
                file_writer.write(" ")
                file_writer.write(write_burn_prop)
                file_writer.write(" ")
                file_writer.write(write_total_prop)
                file_writer.write(" ")
                file_writer.write(write_var_manu)
                file_writer.write("\n")
                z=0
                i = len(state.simulation_result.thrust)
                while z != i:
                    string_time_array = str(state.simulation_result.time[z])
                    string_thrust_array = str(state.simulation_result.thrust[z])
                    file_writer.write(string_time_array)
                    file_writer.write(" ")
                    file_writer.write(string_thrust_array)
                    file_writer.write("\n")
                    z = z+1
        
                file_writer.close()
                save_window.destroy()
    
        write_button = HideableButton(master=save_window, text="Save as RASP", showoninit=1, command=write, height=2, width=10, row=4, column=0)
        save_window.grab_set()         # grab all input to this window
        save_window.focus_set()        # put keyboard focus on it
        save_window.wait_window()      # block here until this window is closed

    def export_simulation_to_csv(self):
        simtc = state.simulation_result

        # Prompt user for save location
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        types = [('CSV', '*.csv')]
        file_path = filedialog.asksaveasfilename(
            title="Save Simulation Data",
            defaultextension=".csv",
            filetypes=types,
            initialdir=downloads_path
        )

        if not file_path:
            print("Save cancelled.")
            return

        import collections.abc

        # Get all field names
        fieldnames = list(simtc.__dict__.keys())

        # Determine lengths and list vs scalar
        lengths = {}
        for name in fieldnames:
            value = getattr(simtc, name)
            if isinstance(value, collections.abc.Iterable) and not isinstance(value, (str, bytes)):
                lengths[name] = len(value)
            else:
                lengths[name] = 1

        # Determine row count from list fields only
        list_lengths = {l for l in lengths.values() if l > 1}

        if len(list_lengths) > 1:
            raise ValueError(f"Inconsistent list lengths in simulation_result: {list_lengths}")

        row_count = list_lengths.pop() if list_lengths else 1

        # Write the CSV
        with open(file_path, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for i in range(row_count):
                row = {}
                for name in fieldnames:
                    value = getattr(simtc, name)

                    if lengths[name] == 1:
                        # Scalar -> only include in first row, blank for others
                        row[name] = value if i == 0 else ""
                    else:
                        # List entry
                        row[name] = value[i]
                    row[name] = str(row[name]).strip("'")


                writer.writerow(row)

        print(f"Simulation data exported to: {file_path}")






# End of tab_tc.py
