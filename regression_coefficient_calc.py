import State as state
import math as math
import CEA_Wrap as cw

def BCC_run(port_length,fuel_density):
    print("run bcc")
    average_perimeter = sum(state.grain_perimeter)/len(state.grain_perimeter)
    average_diameter = average_perimeter/math.pi
    print("average diameter",average_diameter)
    port_length = port_length
    print("port length",port_length)
    area_ratio = 99 #not necessary, but we just need a number
    fuel_density = fuel_density

    #Hard Constants
    C1 = 2 # Constant
    Universal_Gas_Constant = 8.314462618
    Koxe = 1
    hard_sphere_diameter = 5 # angstroms
    temperature_ratio_exponent = 0.29 # l
    Prandtl = 1
    temperature_ambient = 298 # K

    if(-2==-2):
        def calculate_molecular_weight(formula: str) -> float:
            # Atomic weights in g/mol
            atomic_weights = {
                'C': 12.01,
                'H': 1.008,
                'O': 16.00,
                'N': 14.01,
                'S': 32.07,
                'P': 30.97,
                'Cl': 35.45,
                'F': 18.998
            }

            tokens = formula.split()
            if len(tokens) % 2 != 0:
                raise ValueError("Invalid input format. Use 'Element Count' pairs, e.g., 'C 7.337 H 10.982'")

            total_weight = 0.0
            i = 0
            while i < len(tokens):
                element = tokens[i]
                try:
                    count = float(tokens[i + 1])
                except ValueError:
                    raise ValueError(f"Invalid number for element {element}: {tokens[i + 1]}")

                if element not in atomic_weights:
                    raise ValueError(f"Unknown element: {element}")

                total_weight += atomic_weights[element] * count
                i += 2

            return total_weight

        def parse_elemental_string(formula: str) -> dict:
            """Parses a string like 'C 7.337 H 10.982 O 2.0' into a dictionary {'C': 7.337, 'H': 10.982, 'O': 2.0}"""
            tokens = formula.split()
            if len(tokens) % 2 != 0:
                raise ValueError("Invalid input format. Use 'Element Count' pairs.")

            comp = {}
            i = 0
            while i < len(tokens):
                element = tokens[i]
                try:
                    count = float(tokens[i + 1])
                except ValueError:
                    raise ValueError(f"Invalid number for element {element}: {tokens[i + 1]}")
                comp[element] = count
                i += 2
            return comp

        def stoichiometric_ratio_elemental(fuel_str: str, oxidizer_str: str) -> float:
            """Calculate stoichiometric O/F mass ratio using elemental format like 'C 2 H 6 O 1'."""
            fuel = parse_elemental_string(fuel_str)
            oxidizer = parse_elemental_string(oxidizer_str)

            # Extract fuel atom counts
            nC = fuel.get('C', 0.0)
            nH = fuel.get('H', 0.0)
            nO_fuel = fuel.get('O', 0.0)

            # Total oxygen needed for complete combustion:
            # Each C -> CO2 needs 2 O
            # Each 2 H -> H2O needs 1 O
            O_required = 2 * nC + (nH / 2) - nO_fuel

            # Oxygen atoms provided per oxidizer molecule
            O_per_oxidizer = oxidizer.get('O', 0.0)
            if O_per_oxidizer <= 0:
                raise ValueError("Oxidizer must provide at least one oxygen atom.")

            # Moles of oxidizer needed to supply required O atoms
            moles_oxidizer_needed = O_required / O_per_oxidizer

            # Use your existing function to compute molecular weights
            mass_fuel = calculate_molecular_weight(fuel_str)
            mass_oxidizer = moles_oxidizer_needed * calculate_molecular_weight(oxidizer_str)

            return mass_oxidizer / mass_fuel

        def REALRunChemcicalCalculations():
            #Chemical Calculations
            k = -.005*(Ea/((Universal_Gas_Constant/1000)*temperature_surface)) - .08
            temperature_Mean = (temperature_chamber+temperature_surface)/2
            average_Molecular_Weight = (fuel_molecular_weight + oxidizer_molecular_weight*O_F)/O_F
            dh = cp_chamber*(temperature_chamber-temperature_ambient) - cp_surface*(temperature_surface-temperature_ambient)
            dh_hg = dh/hg
            phic = ((1.22*O_F*dh_hg)/(Koxe+(O_F+Koxe)*dh_hg))
            Ts_Tm = temperature_surface/temperature_Mean
            um = 26.69*math.sqrt((average_Molecular_Weight*temperature_surface)/((hard_sphere_diameter)**2)) * 10**(-7)
            A = ((0.022)*(Prandtl**-0.6)*(dh_hg**0.23)*(phic**0.77))/((um**k)*(Ts_Tm**temperature_ratio_exponent))
            return A, k, um

        def REALCalculateRegression(Gox,port_Diameter,port_Length,A,k,um):
            #Big Regression Rate Equation Broken Up
            port_Diameter = port_Diameter*100
            port_Length = port_Length*100
            Term1 = 1+2.5*C1*((Gox*port_Diameter/um)**(-0.22))*(port_Diameter/port_Length)

            Term2 =4*A*(k+1)*((Gox*port_Diameter)**k)*(port_Length/port_Diameter)

            Remaining = (A/fuel_density)*(Gox**(k+1))*(port_Diameter**k)

            raw_Regression_Rate = Remaining * (Term1 + Term2)

            print(Term1)
            print(Term2)
            print(Remaining)

            return raw_Regression_Rate

        def RunCEA(OF,fuelstring,oxstring,fHOF,oHOF):
            theof = OF
            area_ratio = 4 

            fuel = cw.Fuel(name= "fuel", chemical_composition = fuelstring, hf = fuel_heat_of_formation)

            oxidizer = cw.Oxidizer(name= "oxidizer", chemical_composition = oxstring, hf = oHOF)

            themats = [fuel, oxidizer]
            problem = cw.RocketProblem(pressure=400,o_f = theof, sup = area_ratio, materials = themats)
            data = problem.run()
            print("isp",data.isp)
            return data.c_t, data.c_cp
            return data.c_t, data.c_cp

    Ea = 200 #kJ/mol, this is an average number that probably should be looked into
    hg = 2314 #J/g, this is an average value calculated from multiple different polymers

    fuel_compound = state.locked_fuel_string
    fuel_heat_of_formation = state.locked_fuel_hof
    fuel_molecular_weight = calculate_molecular_weight(fuel_compound) # g/mol
    print(f"Fuel \"{fuel_compound}\"Molecular Weight: {fuel_molecular_weight:.3f} g/mol")

    oxidizer_compound = state.locked_oxid_string
    ox_heat_of_formation = state.locked_oxid_hof
    oxidizer_molecular_weight = calculate_molecular_weight(oxidizer_compound) # g/mol
    print(f"Oxidizer \"{oxidizer_compound}\" Molecular weight: {oxidizer_molecular_weight:.3f} g/mol")

    O_F = stoichiometric_ratio_elemental(fuel_compound,oxidizer_compound)
    print("O/F Ratio",O_F)

    temperature_chamber,cp_chamber = RunCEA(O_F,fuel_compound,oxidizer_compound,fuel_heat_of_formation,ox_heat_of_formation)

    temperature_surface = -1.0
    fuel_of = .00001
    while (temperature_surface == -1.0):
        try:
            temperature_surface,cp_surface = RunCEA(fuel_of,fuel_compound,oxidizer_compound,fuel_heat_of_formation,ox_heat_of_formation)
        except RuntimeError:
            fuel_of = fuel_of*10

    print("Fuel Surface O/F Ratio",fuel_of)
    print("Temperature of Chamber",temperature_chamber)
    print("Temperature of Surface",temperature_surface)
    print("cp of Chamber",cp_chamber)
    print("cp of Surface",cp_surface)


    globA, globk, globum = REALRunChemcicalCalculations()

    correction_Factor = 20000

    ballistic_a = REALCalculateRegression(1,average_diameter,port_length,globA,globk,globum)*correction_Factor
    ballistic_n = (1+globk*2)

    #a and n values for when ox flux is in kg/m^2s
    print("a",ballistic_a)
    print("n",ballistic_n)
    
    state.ballistic_a = ballistic_a
    state.ballistic_n = ballistic_n