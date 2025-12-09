import numpy as np
import os
import sys

#basically stores global variables

grain_OD_m = -1

grain_regression = []
grain_perimeter = []
grain_area = []

tab_tc_ref = -1
cea_config = 0

grain_config = 0

simulation_result = -1

locked_fuel_string = ""
locked_fuel_hof = -1
locked_oxid_string = ""
locked_oxid_hof = -1

locked_materials = []

ballistic_a = -1
ballistic_n = -1


def linear_interpolate(data, scale_factor):
    result = []
    n = len(data)
    for i in range(n - 1):
        start = data[i]
        end = data[i + 1]
        steps = scale_factor  # The number of intervals between points
        # Interpolate linearly between start and end
        result.extend([start + (end - start) * j / steps for j in range(steps)])
    result.append(data[-1])  # Add the last value
    return result

def convert_by_unit(value, unit):
    if unit in ("K", "F", "C"):
        if unit == "K":
            value = value
        elif unit == "F":
            value = (value - 32) * (5/9) + 273.15
        elif unit == "C":
            value = value + 273.15

    if unit in ("m", "mm", "in"):
        if(unit == "m"):
            value = value
        elif(unit == "mm"):
            value = value*0.001
        elif(unit == "in"):
            value = value*0.0254
    if unit in ("m^2", "mm^2", "in^2"):
        if(unit == "m^2"):
            value = value
        elif(unit == "mm^2"):
            value = value*.000001
        elif(unit == "in^2"):
            value = value*0.00064516
    if unit in ("m^3", "cm^3", "in^3"):
        if(unit == "m^3"):
            value = value
        elif(unit == "cm^3"):
            value = value*.000001
        elif(unit == "in^3"):
            value = value*.000016387064
    if unit in ("MPa", "psi"):
        if(unit == "MPa"):
            value = value
        elif(unit == "psi"):
            value = value*0.00689476
    return value

class SimulationResult:
    def __init__(self):
        self.time = []
        self.thrust = []
        self.temperature = []
        self.tank_pressure = []
        self.cc_pressure = []
        self.pressure_drop = []
        self.ox_flow_rate = []
        self.ox_mass = []
        self.m_liquid_old = []
        self.m_liquid_new = []
        self.gas_mass = []
        self.ox_mass_flux = []
        self.change_in_temp = []
        self.regression_rate = []
        self.total_regression = []
        self.fuel_mass_flow_rate = []
        self.mass_flow_rate = []
        self.of_ratio = []
        self.fuel_mass = []

        self.output_oxidizer_Mass = -1
        self.output_prop_Mass = -1
        self.output_prop_after_Burn = -1
        self.output_total_Impulse = -1
        self.output_specific_Impulse = -1
        self.output_engine_Class = -1

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File: {file_path} deleted.")
    else:
        print(f"File: {file_path} not found.")
