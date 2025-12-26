import src.data_processing.CO2SYS as CO2SYS
import src.data_processing.fast_fourier_transform as FFT
import src.data_processing.carbon_emissions as CE
import src.data_visualization.plot as plot
import src.ODE.least_squares as LS
from src.ODE.simulated_data import SimulatedData

import numpy as np

if __name__ == "__main__":
    # Data Preprocessing

    # Compute Aragonite Saturation (Omega_Ar) and save to new CSV
    CO2SYS.compute_aragonite_saturation(
        input_file_path="data/raw/ocean_data.csv",
        output_file_path="data/processed/ocean_data_with_aragonite.csv")
    
    # Apply Fast Fourier Transform to denoise Omega_Ar data
    FFT.fft(
        input_file_path="data/processed/ocean_data_with_aragonite.csv",
        output_file_path="data/processed/denoised_omega_arag.csv")

    # Normalize CO2 Emissions data and save to new CSV
    CE.normalize_co2_emissions(
        input_file_path="data/raw/Carbon_Emissions_EDGAR_OSCAR.csv",
        output_file_path="data/processed/CO2_combined_normalized.csv")

    # Define the parameters for the Original LV Model
    params_og_MCMC = {"a": (14.28837 * (10 **(-4))), "b": (4.89799 * (10 **(-4))), 
              "d": (2.35865 * (10 **(-2))), "e": (6.41611 * (10 **(-3))), "f": (5.78787 * (10 **(-5))), 
              "g": 0.48753, "w_A":  2 * np.pi, "phi": -1986.9857}
    
    params_og_GA = {"a": (1.3652 * (10 **(-2))), "b": (1.4411 * (10 **(-4))), 
            "d": (3.49188 * (10 **(-3))), "e": (2.46133 * (10 **(-3))), "f": (2.3697 * (10 **(-4))), 
            "g": -0.1535, "w_A":  2 * np.pi, "phi": -1988.33277}
    
    params = {"og_MCMC_parameters": params_og_MCMC, "og_GA_parameters": params_og_GA}

    # Load datasets from processed CSV files
    CO2_dataset = np.genfromtxt('data/processed/CO2_combined_normalized.csv', delimiter=',', skip_header=1)
    Ar_dataset = np.genfromtxt('data/processed/denoised_omega_arag.csv', delimiter=',', skip_header=1)

    # extract data from CO2_dataset
    CO2_time = CO2_dataset[:, 0]
    CO2_data = CO2_dataset[:, 4]  # Normalized CO2 emissions

    # extract data from Ar_dataset
    Omega_Ar_time = Ar_dataset[:, 0]
    Omega_Ar_data = Ar_dataset[:, 2]    # Denoised 
    
    # Initial Conditions and Simulation Parameters
    x0 = np.array([CO2_data[0], Omega_Ar_data[0]])
    t0 = CO2_time[0] # time unit is year, initial time
    tf = CO2_time[-1] # final time
    step_divider = 4
    dt = (CO2_time[1] - CO2_time[0]) / step_divider # time step size

    print("Step size (dt):", dt)

    for param_set_name, param_set in params.items():

        print(f"\n\n ~~~~ Simulations for parameter set ~~~~: {param_set_name}")

        # Model Simulation of the Original LV Model by Mendoza-Mendoza et al.
        og_model_sim = SimulatedData(model="og_LV")
        og_model_sim.simulate_model(param_set, x0, t0, tf, dt)
        plot.plot_LV_Model(param_set_name, og_model_sim, CO2_data, CO2_time, Omega_Ar_data, Omega_Ar_time)

        print("Percentage error in Original Model:", "for CO2:", max(og_model_sim.CO2_percent_error), "for Omega_Ar:", max(og_model_sim.Omega_Ar_percent_error))

        # Parameter Fitting and Model Simulation for the Modified LV Model
        params_modified = LS.fit_parameters(param_set, x0, t0, tf, dt, CO2_data, CO2_time, Omega_Ar_data, Omega_Ar_time)
        mod_model_sim = SimulatedData(model="mod_LV")
        mod_model_sim.simulate_model(params_modified, x0, t0, tf, dt)
        
        print("~~ Fitting f(t) ~~")

        # Comparison Plot between Original and Modified LV Models
        plot.comparison_plot(og_model_sim, mod_model_sim, Omega_Ar_data, Omega_Ar_time, param_set_name)

        print("Percentage error in Modified Model for Omega_Ar:", max(mod_model_sim.Omega_Ar_percent_error))

        print("\n~~ Chi-Squared Calculations ~~")
        # Calculating Chi-Squared for both models
        og_model_sim.compute_chi_squared("CO2 Emissions", CO2_data, CO2_time, num_params=8)
        og_model_sim.compute_chi_squared("Omega_Ar", Omega_Ar_data, Omega_Ar_time, num_params=8)
        print(f"Original LV Model - CO2 Emissions Reduced Chi-Squared: {og_model_sim.CO2_chi_squared_reduced}")
        print(f"Original LV Model - Omega_Ar Reduced Chi-Squared: {og_model_sim.Omega_Ar_chi_squared_reduced}")

        #mod_model_sim.compute_chi_squared("CO2 Emissions", CO2_data, CO2_time)
        mod_model_sim.compute_chi_squared("Omega_Ar", Omega_Ar_data, Omega_Ar_time) # +2 for w_A, phi
        #print(f"Modified LV Model - CO2 Emissions Reduced Chi-Squared: {mod_model_sim.CO2_chi_squared_reduced}")
        print(f"Modified LV Model - Omega_Ar Reduced Chi-Squared: {mod_model_sim.Omega_Ar_chi_squared_reduced}")
    
    print("\n\nAll simulations and plots completed.")