import State as state
from CoolProp.CoolProp import PropsSI
import math as math
import numpy as np
import easyCEA as eCEA

def dosim(init_Tank_Temp,
          tank_Volume,
          ullage,
          discharge_Coefficient,
          total_Injector_Area,
          port_Length,
          fuel_density,
          ox_Flux_units,
          a,
          n,
          throat_diameter,
          exit_diameter,
          engine_efficiency,
          update_callback,
          stop_event):

    print(f"init_Tank_Temp:           {init_Tank_Temp}")
    print(f"tank_Volume:              {tank_Volume}")
    print(f"ullage:                   {ullage}")
    print(f"discharge_Coefficient:    {discharge_Coefficient}")
    print(f"total_Injector_Area:      {total_Injector_Area}")
    print(f"port_Length:              {port_Length}")
    print(f"fuel_density:             {fuel_density}")
    print(f"ox_Flux_units:            {ox_Flux_units}")
    print(f"a (regression coeff):     {a}")
    print(f"n (regression exponent):  {n}")
    print(f"throat diameter:         {throat_diameter}")
    print(f"exit diameter:         {exit_diameter}")
    print(f"engine_efficiency:        {engine_efficiency}")
    
    simtc = state.SimulationResult()

    #Grabbing Globals from State
    grain_area_array = np.array(state.grain_area)
    grain_total_regression_array = np.array(state.grain_regression)
    grain_perimeter_array = np.array(state.grain_perimeter)
    grain_OD = state.grain_OD_m


    #preparing values
    
    #.001 converts regression units from mm/s to m/s
    a = a*.001
    ullage = ullage*.01

    engine_efficiency = engine_efficiency*.01
    
    #MPa to Pa
    init_CC_Pressure = 101300 #This doesn't acutally mean anything. It gets set to whatever nozzle throat is

    #Diameter to Area
    throat_area = math.pi*(throat_diameter/2)**2
    exit_area = math.pi*(exit_diameter/2)**2


    #Constants
    first = 0
    debug_mode = 0
    iteration = 0
    time_Increment = .05
    time = 0
    total_regression = 0
    thrust_array = []
    time_array = []
    change_in_Temp_array = []
    vapor_correction_factor = 1
    g = 9.80665      # m/s^2
    eps = exit_area/throat_area #change to variable maybe eventually


    #calculations
    liquid_Density = PropsSI('D','T',init_Tank_Temp,'Q',0,'N2O')
    vapor_Density  = PropsSI('D','T',init_Tank_Temp,'Q',1,'N2O')
    init_Tank_Pressure = PropsSI('P','T',init_Tank_Temp,'Q',1,'N2O')
    init_Ox_Mass = (tank_Volume*liquid_Density*(1-ullage))+(tank_Volume*vapor_Density*(ullage))
    init_fuel_Mass = ((math.pi*(grain_OD/2)**2)-grain_area_array[0])*port_Length*fuel_density
    init_prop_Mass = init_Ox_Mass+init_fuel_Mass

    tank_Pressure = 999999
    m_Liquid_New = 99
    previous_cc_Pressure = 0.0
    fuel_mass = init_fuel_Mass

    # Cache CEA results for slowly changing pressure & O/F ratio
    cea_cache = {}
    def get_cea_cached(pressure_psi, o_F, sup):
        key = (round(pressure_psi, 0), round(o_F, 2))  #Ex. 319.23 psi & 4.29347 o/f -> 319psi & 4.29 o/f
        if key not in cea_cache:
            cea_cache[key] = eCEA.get_velo_and_cstar(pressure=pressure_psi, o_f=o_F, sup=sup)
        return cea_cache[key]


    #Chills the CC_Pressure the Hell Out
    #Motor Startup not added yet, but this fixes weird issues from CC_Pressure not matching with what
    #a particular nozzle throat diameter would give
    for i in range(10):
        tank_Pressure = init_Tank_Pressure
        cc_Pressure = init_CC_Pressure
        pressure_Drop = tank_Pressure - cc_Pressure
        if(pressure_Drop > 0):
            ox_Flow_Rate = discharge_Coefficient*total_Injector_Area*math.sqrt(2*pressure_Drop*liquid_Density)
        else:
            ox_Flow_Rate = ox_Flow_Rate
        z = 0
        port_perimeter = grain_perimeter_array[z]
        port_area = grain_area_array[z]
        port_surface_area = port_perimeter*port_Length
        if(ox_Flux_units == "g/cm^2"):
            ox_Mass_Flux = ox_Flow_Rate/port_area/10
        elif(ox_Flux_units == "kg/m^2"):
            ox_Mass_Flux = ox_Flow_Rate/port_area
        regression_rate = a*(ox_Mass_Flux**n)
        fuel_mass_flow_rate = regression_rate*port_surface_area*fuel_density
        mass_flow_rate = ox_Flow_Rate+fuel_mass_flow_rate
        o_F = ox_Flow_Rate/fuel_mass_flow_rate
        cstar = eCEA.get_cstar_only(pressure = cc_Pressure*0.000145037737734, o_f=o_F)
        cc_Pressure = (cstar*mass_flow_rate)/throat_area
        init_CC_Pressure = cc_Pressure

    while(tank_Pressure > 400000 and fuel_mass > 0):
        iteration = iteration+1
        time = time_Increment*iteration
    
        if(m_Liquid_New>=0):
            if(first==0):
                temperature = init_Tank_Temp
                tank_Pressure = init_Tank_Pressure
                cc_Pressure = init_CC_Pressure
                pressure_Drop = tank_Pressure - cc_Pressure
                if(pressure_Drop > 0):
                    ox_Flow_Rate = discharge_Coefficient*total_Injector_Area*math.sqrt(2*pressure_Drop*liquid_Density)
                ox_Mass = init_Ox_Mass
                m_Liquid_Old = init_Ox_Mass
                m_Liquid_New = (((tank_Volume*(1-ullage))-(ox_Mass/vapor_Density))/((1/liquid_Density)-(1/vapor_Density)))
                gas_Vaporized = 0
                gas_Mass = m_Liquid_Old - m_Liquid_New

                specific_Enthalpy_of_Vaporization = (PropsSI('H','P',tank_Pressure,'Q',1,'N2O') - PropsSI('H','P',tank_Pressure,'Q',0,'N2O'))/1000
                liquid_Specific_Heat_Capacity = PropsSI('C','P',tank_Pressure,'Q',0,'N2O')/1000

                if (m_Liquid_Old>m_Liquid_New):
                    dQ_Heat_Removed = specific_Enthalpy_of_Vaporization*gas_Vaporized
                else:
                    dQ_Heat_Removed = 0
                change_In_Temperature = dQ_Heat_Removed/(liquid_Specific_Heat_Capacity*m_Liquid_New)

                #this is needed
                fuel_mass = init_fuel_Mass

            else:
                if(previous_temperature>250):
                    temperature = previous_temperature - previous_change_In_Temperature
                    if(previous_temperature<255):
                        change_in_Temp_array.append(previous_change_In_Temperature)
                else:
                    if(len(change_in_Temp_array)==0):
                        change_in_Temp_array.append(previous_change_In_Temperature)
                    temperature = previous_temperature - (sum(change_in_Temp_array)/len(change_in_Temp_array))
                if(temperature<0):
                    temperature = 1
                tank_Pressure = previous_tank_Pressure*(temperature/previous_temperature)
                pressure_Drop = tank_Pressure - cc_Pressure
                if(pressure_Drop<0):
                    pressure_Drop=1000
                ox_Flow_Rate = discharge_Coefficient*total_Injector_Area*math.sqrt(2*pressure_Drop*liquid_Density)
                m_Liquid_Old = (previous_m_Liquid_New - (ox_Flow_Rate*time_Increment))
                ox_Mass = m_Liquid_Old + previous_gas_Mass
                m_Liquid_New = ((tank_Volume-(ox_Mass/vapor_Density))/((1/liquid_Density)-(1/vapor_Density)))
                gas_Vaporized = m_Liquid_Old - m_Liquid_New
                gas_Mass = previous_gas_Mass + gas_Vaporized

                specific_Enthalpy_of_Vaporization = (PropsSI('H','P',tank_Pressure,'Q',1,'N2O') - PropsSI('H','P',tank_Pressure,'Q',0,'N2O'))/1000
                liquid_Specific_Heat_Capacity = PropsSI('C','P',tank_Pressure,'Q',0,'N2O')/1000

                if (m_Liquid_Old>m_Liquid_New):
                    dQ_Heat_Removed = specific_Enthalpy_of_Vaporization*gas_Vaporized
                else:
                    dQ_Heat_Removed = 0
                
                change_In_Temperature = dQ_Heat_Removed/(liquid_Specific_Heat_Capacity*m_Liquid_New)
        else:
            molesperkgnitrous = 22.72
            moles = molesperkgnitrous*gas_Mass
            molefactor = tank_Pressure/moles
            gamma = 1.31 #for N2O
            Pcr = (2/(gamma+1))**(gamma/(gamma-1))
            densityofnitrous = previous_gas_Mass/tank_Volume
            ox_Flow_Rate = vapor_correction_factor * discharge_Coefficient*total_Injector_Area*math.sqrt(densityofnitrous*previous_tank_Pressure* ( ((2*gamma)/(gamma-1)) * (Pcr**(2/gamma)) * (1-(Pcr**((gamma-1)/gamma)))  ) )    
            gas_Mass = previous_gas_Mass - (ox_Flow_Rate*time_Increment)
            ox_Mass = gas_Mass
            moles = molesperkgnitrous*gas_Mass
            tank_Pressure = moles*molefactor
    
        #fuel section
        z = np.argmin(np.abs(grain_total_regression_array - total_regression))
        port_perimeter = grain_perimeter_array[z]
        port_area = grain_area_array[z]

        port_surface_area = port_perimeter*port_Length
        if(ox_Flux_units == "g/cm^2"):
            ox_Mass_Flux = ox_Flow_Rate/port_area/10
        elif(ox_Flux_units == "kg/m^2"):
            ox_Mass_Flux = ox_Flow_Rate/port_area
        regression_rate = a*(ox_Mass_Flux**n)
        fuel_mass_flow_rate = regression_rate*port_surface_area*fuel_density
        fuel_mass = fuel_mass-fuel_mass_flow_rate*time_Increment
        total_regression = total_regression+regression_rate*time_Increment
        if(fuel_mass<0):
            fuel_mass = 0
        #thrust related
        o_F = ox_Flow_Rate/fuel_mass_flow_rate
        mass_flow_rate = ox_Flow_Rate+fuel_mass_flow_rate

        if (o_F>=0):            
            
            pressure_psi = cc_Pressure * 0.000145037737734  # Pa to psi
            exhaust_velocity, cstar = get_cea_cached(pressure_psi, o_F, eps)
            
            cc_Pressure = (cstar*mass_flow_rate)/throat_area
            if(previous_cc_Pressure<cc_Pressure and m_Liquid_New<=0):
                cc_Pressure = previous_cc_Pressure
            thrust = exhaust_velocity*mass_flow_rate*engine_efficiency

            
        time = round(time, 3)
        #maybe make change with the timeinterval
        thrust = round(thrust, 1)
        
        simtc.time.append(time)
        simtc.thrust.append(round(thrust, 1))
        simtc.temperature.append(temperature)
        simtc.tank_pressure.append(tank_Pressure)
        simtc.cc_pressure.append(cc_Pressure)
        simtc.pressure_drop.append(pressure_Drop)
        simtc.ox_flow_rate.append(ox_Flow_Rate)
        simtc.ox_mass.append(ox_Mass)
        simtc.m_liquid_old.append(m_Liquid_Old)
        simtc.m_liquid_new.append(m_Liquid_New)
        simtc.gas_mass.append(gas_Mass)
        simtc.ox_mass_flux.append(ox_Mass_Flux)
        simtc.change_in_temp.append(change_In_Temperature)
        simtc.regression_rate.append(regression_rate)
        simtc.total_regression.append(total_regression)
        simtc.fuel_mass_flow_rate.append(fuel_mass_flow_rate)
        simtc.mass_flow_rate.append(mass_flow_rate)
        simtc.of_ratio.append(o_F)
        simtc.fuel_mass.append(fuel_mass)
        if (debug_mode == 1):
            #Print to Command Line
            print()
            print("Iteration:",iteration)
            print("Time:",time)
            print("Temperature:",temperature)
            print("Tank Pressure:",tank_Pressure)
            print("CC Pressure:",cc_Pressure)
            print("Pressure Drop",pressure_Drop)
            print("Ox Flow Rate",ox_Flow_Rate)
            print("ox_Mass",ox_Mass)
            print("m_Liquid_Old",m_Liquid_Old)
            print("m_Liquid_New",m_Liquid_New)
            print("gas_Vaporized",gas_Vaporized)
            print("gas_Mass",gas_Mass)
            print("specific_Enthalpy_of_Vaporization",specific_Enthalpy_of_Vaporization)
            print("liquid_Specific_Heat_Capacity",liquid_Specific_Heat_Capacity)
            print("dQ_Heat_Removed",dQ_Heat_Removed)
            print("change_In_Temperature",change_In_Temperature)
            print("port_area",port_area)
            print("ox_Mass_Flux",ox_Mass_Flux)
            print("regression_rate",regression_rate)
            print("fuel_mass_flow_rate",fuel_mass_flow_rate)
            print("o_F",o_F)
            print("mass_flow_rate",mass_flow_rate)
            print("thrust",thrust)
            print("fuelmass",fuel_mass)
        first = 1
    
        previous_iteration = iteration
        previous_time = time
        previous_temperature = temperature
        previous_tank_Pressure = tank_Pressure
        previous_cc_Pressure = cc_Pressure
        previous_pressure_Drop = pressure_Drop
        previous_ox_Flow_Rate = ox_Flow_Rate
        previous_ox_Mass = ox_Mass
        previous_m_Liquid_Old = m_Liquid_Old
        previous_m_Liquid_New = m_Liquid_New
        previous_gas_Vaporized = gas_Vaporized
        previous_gas_Mass = gas_Mass
        previous_dQ_Heat_Removed = dQ_Heat_Removed
        previous_change_In_Temperature = change_In_Temperature
        previous_port_area = port_area
        previous_ox_Mass_Flux = ox_Mass_Flux
        previous_regression_rate = regression_rate
        previous_fuel_mass_flow_rate = fuel_mass_flow_rate
        previous_o_F = o_F
        previous_mass_flow_rate = mass_flow_rate
        previous_thrust = thrust
        previous_fuel_mass = fuel_mass


        if update_callback and iteration % 2 == 0:
            fraction = (init_Ox_Mass - ox_Mass) / init_Ox_Mass
            fraction = (0.3 + 0.7 * fraction)**5
            update_callback(fraction)
            if stop_event.is_set():  # <- check if user pressed Cancel
                break

    if update_callback:
        update_callback(1.0)

    #Display Thrust Curve
    z=0
    i = len(simtc.thrust)
    if(debug_mode==1):
        while z != i:
            print(simtc.time[z],simtc.thrust[z])
            z = z+1
    total_impulse = 0
    for i in range(len(simtc.time) - 1):
        h = simtc.time[i + 1] - simtc.time[i]  # Width of the interval
        area = 0.5 * h * (simtc.thrust[i] + simtc.thrust[i + 1])  # Area of the trapezoid
        total_impulse += area
    print(total_impulse)
    
    if(total_impulse<160):
        print("Less than H Class")
        show_engine_Class = "< H Class"
    elif(total_impulse<320):
        print("H Class")
        show_engine_Class = "H Class"
    elif(total_impulse<640):
        print("I Class")
        show_engine_Class = "I Class"
    elif(total_impulse<1280):
        print("J Class")
        show_engine_Class = "J Class"
    elif(total_impulse<2560):
        print("K Class")
        show_engine_Class = "K Class"
    elif(total_impulse<5120):
        print("L Class")
        show_engine_Class = "L Class"
    elif(total_impulse<10240):
        print("M Class")
        show_engine_Class = "M Class"
    elif(total_impulse<20480):
        print("N Class")
        show_engine_Class = "N Class"
    elif(total_impulse<40960):
        print("O Class")
        show_engine_Class = "O Class"
    elif(total_impulse<81920):
        print("P Class")
        show_engine_Class = "P Class"
    elif(total_impulse<163840):
        print("Q Class")
        show_engine_Class = "Q Class"
    elif(total_impulse<327680):
        print("R Class")
        show_engine_Class = "R Class"
    elif(total_impulse<655360):
        print("S Class")
        show_engine_Class = "S Class"
    elif(total_impulse<1311000):
        print("T Class, the FAA might be mad")
        show_engine_Class = "T Class, Reaching Limit"
    elif(total_impulse>=1311000):
        print("Above T Class, The FAA is upset")
        show_engine_Class = "> T Class, FAA Mad"
    prop_burned = (init_prop_Mass - fuel_mass)
    isp = total_impulse/prop_burned/9.807
    print(isp)

    show_oxidizer = init_Ox_Mass
    show_oxidizer = round(show_oxidizer,2)
    simtc.output_oxidizer_Mass = show_oxidizer

    show_prop_Mass = init_prop_Mass
    show_prop_Mass = round(show_prop_Mass,2)
    simtc.output_prop_Mass = show_prop_Mass

    show_prop_after_Burn = fuel_mass
    show_prop_after_Burn = round(show_prop_after_Burn,2)
    simtc.output_prop_after_Burn = show_prop_after_Burn

    show_total_Impulse = total_impulse
    show_total_Impulse = round(show_total_Impulse,1)
    simtc.output_total_Impulse = show_total_Impulse

    show_specific_Impulse = isp
    show_specific_Impulse = round(show_specific_Impulse,1)
    simtc.output_specific_Impulse = show_specific_Impulse

    simtc.output_engine_Class = show_engine_Class

    eCEA.cleanup_files()

    return simtc

