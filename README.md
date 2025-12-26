# Modelling the Effect of Business Cycles on Ocean Acidification

### Contribution
This project was completed collaboratively with Sumedhaa Ruhil as part of a second-year Engineering Science course at the University of Toronto. 
I was primarily responsible for data acquisition and normalization, numerical analysis, result interpretation, and technical report writing, and contributed to the system modelling and numerical implementation.

## 1. Project Overview

The aim of this project is to formulate a Lotka-Volterra (LV) system with non-constant coefficients as a more accurate way to describe the interdependence between $CO_2$ levels and ocean acidification, by incorporating the impact of business cycles on carbon emissions.

Ocean acidity is characterised by concentration of aragonite in the ocean ($\Omega_{ar}$).

The original LV system by Mendoza-Mendoza et al. :

$$\frac{dCO_2}{dt} = aCO_2 + b(CO_2)^2$$
$$\frac{d\Omega_{ar}}{dt} = -d\Omega_{ar} + e(\Omega_{ar})^2 - f\Omega_{ar}(CO_2) + g\sin (\omega _A t + \Phi)$$

Our modified model is:

$$\frac{dCO_2}{dt} = aCO_2 + b(CO_2)^2$$
$$\frac{d\Omega_{ar}}{dt} = -d\Omega_{ar} + e(\Omega_{ar})^2 - f(t)\Omega_{ar}(CO_2) + g\sin (\omega _A t + \Phi)$$

where $f(t) = A_f \sin(w_f + \phi_f)$.

The definitions of the variables used in the above systems are available in the Project Report. The impact of business cycles on carbon emissions is accounted for using f(t). Above is defined in `src\ODE\model.py`.

## 2. Methodology

This project's code objectives are divided into three distinct phases: data processing, model simulation and data visulization.

### 2.1 Data Processing

The real data for ocean properties (from ALOHA) and carbon emissions (from EDGAR and OSCAR) have been stored in two csv files.

For $\Omega_{ar}$, PyCO2SYS is used to calculate $\Omega_{ar}$ from the ocean properties. Next, a Fast Fourier Transform is conducted on the calculated $\Omega_{ar}$ values to denoise the data. The files from both steps are saved. The denoised data for $\Omega_{ar}$ is used for the rest of the code.

A plot comparing the original data (original signal) and the denoised data (denoised signal) is generated and saved in the `plot_images` folder.

For $CO_2$ emissions, the carbon emissions from fossil fuels and land use change are added and then normalised to the range 24 - 40. The normalised $CO_2$ values are used for the rest of the code.

### 2.2 Model Simulation

The original LV model `og_LV` is simulated using the fit parameters given in the reference paper via the RK4 (Runge Kutta 4) numerical method:

| Parameters | MCMC Method (Original) | GA Method (Original) |
| :--- | :---: | :---: |
| **<kbd>a</kbd>** | $14.28837 \times 10^{-4}$ | $1.3652 \times 10^{-2}$ |
| **<kbd>b</kbd>** | $4.89799 \times 10^{-4}$ | $1.4411 \times 10^{-4}$ |
| **<kbd>d</kbd>** | $2.35865 \times 10^{-2}$ | $3.49188 \times 10^{-3}$ |
| **<kbd>e</kbd>** | $6.41611 \times 10^{-3}$ | $2.46133 \times 10^{-3}$ |
| **<kbd>f</kbd>** | $5.78787 \times 10^{-5}$ | $2.3697 \times 10^{-4}$ |
| **<kbd>g</kbd>** | $0.48753$ | $-0.1535$ |
| **<kbd>$\phi$</kbd>** | $-1986.9857$ | $-1988.33277$ |
| **<kbd>$CO_{2}(0)$</kbd>** | $27.07203$ | $26.56956$ |
| **<kbd>$\Omega_{ar}(0)$</kbd>** | $3.77466$ | $3.79583$ |

For the modified LV model `mod_LV`, the $f$ constant parameter is replaced with a non-constant function, $A_f \sin(w_f + \phi_f)$. The fit parameters for this new coefficient are calculated using the Least Squares method available in the scipy library.
Once the best $A_f$, $w_f$, $\phi_f$ values have been determined, Root Mean Squared Error percent value is calculated for the fitting and the modified model is simulated via RK4. 

### 2.3 Data visualization

Once the models are simulated and the values generated using the RK4 method on the defined system of equations, three plots are graphed for each original parameter set (GA and MCMC defined in [2.2 Model Simulation](#22-model-simulation)):

1. Real Data against the Original Model's simulation with percentage error plots.
3. Comparison plot with Original Model for $\Omega_{ar}$ and Modified data for $\Omega_{ar}$ along with their percentage error plots.

The above graphs are saved in the `plot_images\` folder.

Additionally, reduced $\chi^2$ values are calculated to compare the model fitting with the real data for the original and modified models. 

## 3. Installation and Setup

To setup your system for the code, please execute the following in the terminal:

For Windows (Command Prompt / PowerShell)
```bash
git clone https://github.com/SRuhil/MAT292-Project_Code.git
cd MAT292-Project_Code

python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```
> If you get an error activating the virtual environment on Windows, please execute the following and then retry:
```bash
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

For Mac and Linux (macOS/Ubuntu/Debian):
```bash
git clone https://github.com/SRuhil/MAT292-Project_Code.git
cd MAT292-Project_Code

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. How to Run

To run the python program, simply execute the following in the terminal:
```bash
python main.py
```

This executes all the three phases described in [2. Methodology](#2-methodology).

## 5. Repository Structure

This repository follows the following structure:

```
├── data/
│   ├── raw/                  CSVs with Ocean data and Carbon Emissions
│   └── processed/            CSV outputs from CO2SYS, FFT denoising and Carbon Normalisation
├── src/
│   ├── data_processing/      Scripts for for PyCO2SYS, FFT and Carbon Normalisation
│   ├── data_visualization/   Matplotlib scripts for result plotting
│   └── ODE/                  LV Models, RK4, Least Squares and SimulatedData class
├── plot_images/              All generated analysis plots and error graphs saved here
├── main.py                   Central execution script (Pipeline Controller)
├── pyproject.toml            Project metadata and build configuration
├── requirements.txt          List of Python dependencies
└── README.md                 Project documentation
```

## 6. Interpreting the Results

The comparison plot with Real, Original and Modified data along with their percentage error plots shows that the change from constant f to $A_f \sin(w_f + \phi_f)$ improves the modelling as compared with the real data.

The $A_f$, $w_f$, $phi_f$ and reduced $\chi^2$ values are available in the terminal after the program is executed. Discussion on these values is available in the Project Report (Section 7.1).
