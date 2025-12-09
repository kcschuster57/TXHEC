import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import State as state
import easyCEA as eCEA
import regression_coefficient_calc as rcc
from labeled_widgets import LabeledEntryWithUnit, LabeledOutputWithUnit, HideableButton, ProgressDialog

class tab_cea(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # --- Main CEA frame ---
        self.frame_cea_related = tk.Frame(self, borderwidth=5, relief=tk.RIDGE)
        self.frame_cea_related.grid(row=0, column=0)

        # --- Fuel composition frame ---
        border_frame_fuel = tk.Frame(self, bg="red", borderwidth=5, relief=tk.RIDGE)
        border_frame_fuel.grid(row=0, column=1)
        self.frame_fuel_composition = tk.Frame(border_frame_fuel)
        self.frame_fuel_composition.grid(row=0, column=0)

        # --- Oxidizer composition frame ---
        border_frame_ox = tk.Frame(self, bg="blue", borderwidth=5, relief=tk.RIDGE)
        border_frame_ox.grid(row=0, column=2)
        self.frame_ox_composition = tk.Frame(border_frame_ox)
        self.frame_ox_composition.grid(row=0, column=0)

        # --- Ballistic coefficients frame ---
        border_frame_voodoo = tk.Frame(self, bg="purple", borderwidth=5, relief=tk.RIDGE)
        border_frame_voodoo.grid(row=1, column=0)
        self.frame_voodoo = tk.Frame(border_frame_voodoo)
        self.frame_voodoo.grid(row=0, column=0)

        tk.Label(self.frame_cea_related, text='NASA CEA', font=('georgia', 10, 'bold')).grid(row=0, column=0,columnspan = 3)

        self.btn_cea_run = tk.Button(self.frame_cea_related, text="Lock CEA", height=2, width=10, command=self.cea_run)
        self.btn_cea_run.grid(row=1, column=0,columnspan = 3)

        self.output_fuel_comp = LabeledOutputWithUnit(self.frame_cea_related, "Fuel Composition:", "Fuel Not Declared", "none", 0, 2)
        self.output_fuel_hof = LabeledOutputWithUnit(self.frame_cea_related, "Fuel Heat of Formation:", "Fuel Not Declared", "kJ/mol", 0, 3)

        self.output_oxid_comp = LabeledOutputWithUnit(self.frame_cea_related, "Oxidizer Composition:", "Oxidizer Not Declared", "none", 0, 4)
        self.output_oxid_hof = LabeledOutputWithUnit(self.frame_cea_related, "Oxidizer Heat of Formation:", "Oxidizer Not Declared", "kJ/mol", 0, 5)





        # ==========================
        # Fuel Composition
        # ==========================
        tk.Label(self.frame_fuel_composition, text='Fuel Composition', font=('georgia', 10, 'bold')).grid(row=0, column=0, columnspan=3)
        self.custom_fuel_toggle = tk.IntVar()
        tk.Checkbutton(self.frame_fuel_composition, text='Custom Fuel?', variable=self.custom_fuel_toggle, command=self.show_custom_fuel).grid(row=1, column=0)
        self.unit_fuel_selection = tk.StringVar()
        options_fuel_selection = ["ABS","HTPB","PMMA","Paraffin","Sorbitol","PBAN","H2","PLA","Wood (Spanish Oak)"]
        self.drop_fuel_selection = tk.OptionMenu(self.frame_fuel_composition, self.unit_fuel_selection, *options_fuel_selection)
        self.drop_fuel_selection.grid(row=1, column=1)


        self.f_button_add_element = tk.Button(self.frame_fuel_composition, text="Add Element", height=2, width=10, command=self.f_cea_add_element)
        self.f_var_HOF = tk.StringVar()
        self.f_entry_HOF = tk.Entry(self.frame_fuel_composition, textvariable=self.f_var_HOF, font=('calibre', 10, 'normal'))
        self.f_label_HOF = tk.Label(self.frame_fuel_composition, text='kJ/mol', font=('georgia', 10, 'bold'))

        # ==========================
        # Oxidizer Composition
        # ==========================
        tk.Label(self.frame_ox_composition, text='Oxidizer Composition', font=('georgia', 10, 'bold')).grid(row=0, column=0, columnspan=3)
        self.custom_ox_toggle = tk.IntVar()
        tk.Checkbutton(self.frame_ox_composition, text='Custom Oxidizer?', variable=self.custom_ox_toggle, command=self.show_custom_ox).grid(row=1, column=0)
        self.unit_ox_selection = tk.StringVar()
        options_ox_selection = ["N2O","O2","O3"]
        self.drop_ox_selection = tk.OptionMenu(self.frame_ox_composition, self.unit_ox_selection, *options_ox_selection)
        self.drop_ox_selection.grid(row=1, column=1)


        self.o_button_add_element = tk.Button(self.frame_ox_composition, text="Add Element", height=2, width=10, command=self.o_cea_add_element)
        self.o_var_HOF = tk.StringVar()
        self.o_entry_HOF = tk.Entry(self.frame_ox_composition, textvariable=self.o_var_HOF, font=('calibre', 10, 'normal'))
        self.o_label_HOF = tk.Label(self.frame_ox_composition, text='kJ/mol', font=('georgia', 10, 'bold'))

        # ==========================
        # Ballistic Coefficients
        # ==========================
        tk.Label(self.frame_voodoo, text="Ballistic Coefficients Calculator", font=('georgia', 10, 'bold')).grid(row=0, column=0, columnspan=2)

        tk.Label(self.frame_voodoo, text='Port Length', font=('georgia', 10, 'bold')).grid(row=1, column=0)
        self.var_port_length_BC = tk.StringVar(value="1.1")
        tk.Entry(self.frame_voodoo, textvariable=self.var_port_length_BC).grid(row=1, column=1)

        tk.Label(self.frame_voodoo, text='Fuel Density', font=('georgia', 10, 'bold')).grid(row=2, column=0)
        self.var_density_BC = tk.StringVar(value="975")
        tk.Entry(self.frame_voodoo, textvariable=self.var_density_BC).grid(row=2, column=1)

        tk.Label(self.frame_voodoo, text='a', font=('georgia', 10, 'bold')).grid(row=4, column=0)
        self.lguia = tk.Label(self.frame_voodoo, text="Run BCC Sim", font=('calibre', 10, 'normal'))
        self.lguia.grid(row=4, column=1)
        tk.Label(self.frame_voodoo, text='n', font=('georgia', 10, 'bold')).grid(row=5, column=0)
        self.lguin = tk.Label(self.frame_voodoo, text="Run BCC Sim", font=('calibre', 10, 'normal'))
        self.lguin.grid(row=5, column=1)

        tk.Button(self.frame_voodoo, text="Run Ballistic Coefficients Calculator", height=2, width=30, command=self.BCC_run).grid(row=7, column=0, columnspan=2)

        


        # --- Initialize element lists ---
        self.f_element_number = 0
        self.f_element_list = []
        self.o_element_number = 0
        self.o_element_list = []



    def ready_props(self):
        self.f_cea_build_custom_gui_wrapper()
        self.o_cea_build_custom_gui_wrapper()
        eCEA.make_reactants()
        return

    def BCC_run(self):
        if(state.grain_config == 0):
            messagebox.showinfo("Sim Failed","Need to run Grain Simulation first")
            return()
        if(state.cea_config == 0):
            messagebox.showinfo("Sim Failed","Need to lock CEA propellants")
            return()
        rcc.BCC_run(float(self.var_port_length_BC.get()),float(self.var_density_BC.get()))
        self.lguia.config(text = state.ballistic_a)
        self.lguin.config(text = state.ballistic_n)

    def cea_run(self):
        self.ready_props()

        self.output_fuel_comp.set_value(state.locked_fuel_string)
        self.output_fuel_hof.set_value(state.locked_fuel_hof)
        self.output_oxid_comp.set_value(state.locked_oxid_string)
        self.output_oxid_hof.set_value(state.locked_oxid_hof)

        state.tab_tc_ref.clear_cea_hold()
        state.cea_config = 1

    # ==========================
    # Fuel/Ox functions
    # ==========================
    def show_custom_fuel(self):
        if self.custom_fuel_toggle.get() == 1:
            self.drop_fuel_selection.grid_remove()
            self.f_button_add_element.grid(row=2, column=0)
            self.f_entry_HOF.grid(row=2, column=1)
            self.f_label_HOF.grid(row=2, column=2)
        else:
            self.drop_fuel_selection.grid(row=1, column=1)
            self.f_button_add_element.grid_remove()
            self.f_entry_HOF.grid_remove()
            self.f_label_HOF.grid_remove()
            try:
                for entry in getattr(self, "f_entries", []):
                    entry.grid_remove()
                for btn in getattr(self, "f_btn_dict", {}).values():
                    btn.grid_remove()
            except AttributeError:
                pass

        self.f_element_number = 0
        self.f_element_list = []


    def show_custom_ox(self):
        if self.custom_ox_toggle.get() == 1:
            self.drop_ox_selection.grid_remove()
            self.o_button_add_element.grid(row=2, column=0)
            self.o_entry_HOF.grid(row=2, column=1)
            self.o_label_HOF.grid(row=2, column=2)
        else:
            self.drop_ox_selection.grid(row=1, column=1)
            self.o_button_add_element.grid_remove()
            self.o_entry_HOF.grid_remove()
            self.o_label_HOF.grid_remove()
            try:
                for entry in getattr(self, "o_entries", []):
                    entry.grid_remove()
                for btn in getattr(self, "o_btn_dict", {}).values():
                    btn.grid_remove()
            except AttributeError:
                pass

        self.o_element_number = 0
        self.o_element_list = []


        # --- Fuel functions ---
    def f_cea_add_element(self):
        try:
            for entry in getattr(self, "f_entries", []):
                entry.grid_remove()
            for btn in getattr(self, "f_btn_dict", {}).values():
                btn.grid_remove()
        except AttributeError:
            pass

        self.f_element_number += 1
        self.f_entries = [tk.Entry(self.frame_fuel_composition) for _ in range(self.f_element_number)]
        self.f_btn_dict = {}
        self.f_element_list = []

        options = [
            "Hydrogen (H)","Helium (He)","Lithium (Li)","Beryllium (Be)","Boron (B)","Carbon (C)",
            "Nitrogen (N)","Oxygen (O)","Fluorine (F)","Neon (Ne)","Sodium (Na)","Magnesium (Mg)",
            "Aluminium (Al)","Silicon (Si)","Phosphorus (P)","Sulfur (S)","Chlorine (Cl)","Argon (Ar)",
            "Potassium (K)","Calcium (Ca)","Scandium (Sc)","Titanium (Ti)","Vanadium (V)","Chromium (Cr)",
            "Manganese (Mn)","Iron (Fe)","Cobalt (Co)","Nickel (Ni)","Copper (Cu)","Zinc (Zn)","Gallium (Ga)",
            "Germanium (Ge)","Bromine (Br)","Krypton (Kr)","Rubidium (Rb)","Strontium (Sr)","Zirconium (Zr)",
            "Niobium (Nb)","Molybdenum (Mo)","Silver (Ag)","Cadmium (Cd)","Indium (In)","Tin (Sn)","Iodine (I)",
            "Xenon (Xe)","Cesium (Cs)","Barium (Ba)","Tantalum (Ta)","Tungsten (W)","Lead (Pb)","Radon (Rn)",
            "Thorium (Th)","Uranium (U)"
        ]

        dropdown_refs = {}
        for i in range(self.f_element_number):
            self.f_entries[i].grid(row=i+3, column=1)
            dropdown_refs[i] = tk.StringVar(self.frame_fuel_composition)
            self.f_element_list.append(dropdown_refs[i])
            self.f_btn_dict[i] = tk.OptionMenu(self.frame_fuel_composition, dropdown_refs[i], *options)
            self.f_btn_dict[i].grid(row=i+3, column=0)

    def o_cea_add_element(self):
        try:
            for entry in getattr(self, "o_entries", []):
                entry.grid_remove()
            for btn in getattr(self, "o_btn_dict", {}).values():
                btn.grid_remove()
        except AttributeError:
            pass

        self.o_element_number += 1
        self.o_entries = [tk.Entry(self.frame_ox_composition) for _ in range(self.o_element_number)]
        self.o_btn_dict = {}
        self.o_element_list = []

        options = [
            "Hydrogen (H)","Helium (He)","Lithium (Li)","Beryllium (Be)","Boron (B)","Carbon (C)",
            "Nitrogen (N)","Oxygen (O)","Fluorine (F)","Neon (Ne)","Sodium (Na)","Magnesium (Mg)",
            "Aluminium (Al)","Silicon (Si)","Phosphorus (P)","Sulfur (S)","Chlorine (Cl)","Argon (Ar)",
            "Potassium (K)","Calcium (Ca)","Scandium (Sc)","Titanium (Ti)","Vanadium (V)","Chromium (Cr)",
            "Manganese (Mn)","Iron (Fe)","Cobalt (Co)","Nickel (Ni)","Copper (Cu)","Zinc (Zn)","Gallium (Ga)",
            "Germanium (Ge)","Bromine (Br)","Krypton (Kr)","Rubidium (Rb)","Strontium (Sr)","Zirconium (Zr)",
            "Niobium (Nb)","Molybdenum (Mo)","Silver (Ag)","Cadmium (Cd)","Indium (In)","Tin (Sn)","Iodine (I)",
            "Xenon (Xe)","Cesium (Cs)","Barium (Ba)","Tantalum (Ta)","Tungsten (W)","Lead (Pb)","Radon (Rn)",
            "Thorium (Th)","Uranium (U)"
        ]

        dropdown_refs = {}
        for i in range(self.o_element_number):
            self.o_entries[i].grid(row=i+3, column=1)
            dropdown_refs[i] = tk.StringVar(self.frame_ox_composition)
            self.o_element_list.append(dropdown_refs[i])
            self.o_btn_dict[i] = tk.OptionMenu(self.frame_ox_composition, dropdown_refs[i], *options)
            self.o_btn_dict[i].grid(row=i+3, column=0)



    #buildings
    def f_cea_build_custom_gui_wrapper(self):
        """
        Example method you can place inside your tab_cea class.
        - collects widget values, calls build_propellant_card_from_data, returns card.
        """
        molar_array = [entry.get() for entry in getattr(self, "f_entries", [])]
        element_array = [el.get() for el in getattr(self, "f_element_list", [])]
        hof_val = getattr(self, "f_var_HOF", None)
        hof_val = hof_val.get() if hof_val is not None else 0.0
        selected_fuel = self.unit_fuel_selection.get() if hasattr(self, "unit_fuel_selection") else None

        state.locked_fuel_string, state.locked_fuel_hof = eCEA.ready_prop_info(
            (self.custom_fuel_toggle.get() == 1),
            element_symbols=element_array,
            molar_amounts=molar_array,
            hof_kjmol=hof_val,
            selected_known=selected_fuel,
        )

        print(state.locked_fuel_string, state.locked_fuel_hof)
        return

    def o_cea_build_custom_gui_wrapper(self):
        molar_array = [entry.get() for entry in getattr(self, "o_entries", [])]
        element_array = [el.get() for el in getattr(self, "o_element_list", [])]
        hof_val = getattr(self, "o_var_HOF", None)
        hof_val = hof_val.get() if hof_val is not None else 0.0
        selected_ox = self.unit_ox_selection.get() if hasattr(self, "unit_ox_selection") else None

        state.locked_oxid_string, state.locked_oxid_hof = eCEA.ready_prop_info(
            (self.custom_ox_toggle.get() == 1),
            element_symbols=element_array,
            molar_amounts=molar_array,
            hof_kjmol=hof_val,
            selected_known=selected_ox,
        )

        print(state.locked_oxid_string, state.locked_oxid_hof)
        return
