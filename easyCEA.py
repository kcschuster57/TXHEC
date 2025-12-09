import prop_maps
import CEA_Wrap as cw
import State as state

def parse_element_symbol(text: str):
    """Return element symbol from 'Carbon (C)' or other forms; empty string if invalid."""
    if not text:
        return ""
    text = text.strip()
    if "(" in text and ")" in text:
        return text.split("(")[1].split(")")[0].strip()
    tokens = text.split()
    return tokens[-1] if tokens else ""

def ready_known_prop(prop: str):
    prop_info = prop_maps.PROP_MAP[prop]
    formula=prop_info["formula"]
    hof_kjmol=prop_info["hof_kjmol"]
    return formula,hof_kjmol

def ready_prop_info(
    custom_toggle: bool,
    element_symbols: list = None,
    molar_amounts: list = None,
    hof_kjmol = 0.0,
    selected_known: str = None
):
    """
    Build and return a propellant card string.
    - If custom_toggle is False, selected_known must be provided (calls make_known_prop).
    - If custom_toggle is True, builds formula from element_symbols and molar_amounts.
    """
    if not custom_toggle:
        if not selected_known:
            raise ValueError("selected_known required when custom_toggle is False")
        return ready_known_prop(selected_known)

    element_symbols = element_symbols or []
    molar_amounts = molar_amounts or []

    parts = []
    for i, raw in enumerate(element_symbols):
        sym = parse_element_symbol(raw)
        if not sym:
            continue
        mol = ""
        if i < len(molar_amounts):
            mol = str(molar_amounts[i]).strip()
        if mol == "" or mol is None:
            mol = "1"
        parts.append(f"{sym} {mol}")

    formula = " ".join(parts).strip()
    if not formula:
        raise ValueError("No valid element/formula data provided for custom propellant")

    try:
        hof_val = float(hof_kjmol) if hof_kjmol is not None else 0.0
    except Exception:
        hof_val = 0.0

    return formula,hof_val

def make_reactants():
    fuel = cw.Fuel(name="customfuel",chemical_composition=state.locked_fuel_string,hf=state.locked_fuel_hof)
    oxid = cw.Oxidizer(name="customoxid",chemical_composition=state.locked_oxid_string,hf=state.locked_oxid_hof)
    materials = [fuel,oxid]
    state.locked_materials = materials
    return

def run_cea(pressure,o_f,sup):
    problem = cw.RocketProblem(pressure=pressure, o_f=o_f, sup=sup, materials=state.locked_materials)
    data = problem.run()
    return data

def get_velo_and_cstar(pressure,o_f,sup):
    data = run_cea(pressure,o_f,sup)
    outmach = data.mach
    outsonic = data.son
    outcstar = data.cstar
    outvelocity = outmach * outsonic
    return outvelocity,outcstar

def get_cstar_only(pressure,o_f):
    data = run_cea(pressure,o_f,99)
    outcstar = data.cstar
    return outcstar

def cleanup_files():
    state.delete_file("my_output.plt")
    state.delete_file("my_output.out")
    state.delete_file("my_output.inp")
