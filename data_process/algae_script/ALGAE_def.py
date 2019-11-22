# -*- coding: utf-8 -*-

import math as ma
import numpy as na
import matplotlib
import matplotlib.pyplot as plt
import os
import glob
import pandas as pd

# Show the first derivative of the
# import sympy as sim
# from sympy import *
# omega, tau_a, AcAt, tau_k, K_rate_coefficient, t1,t = symbols('omega, tau_a, AcAt, tau_k, K_rate_coefficient, t1,t')
# diff( omega * tau_a * AcAt * (1-exp(-tau_k * K_rate_coefficient * ( t - t1)**4)),t)


# Read a list of file csv and concatenate value
path = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\data_process\algae_script'  # BG path

# There is only 1 file in the folder
allFiles = glob.glob(path + "/*.csv")
frame = pd.DataFrame()
list_ = []
for file_ in allFiles:
    df = pd.read_csv(file_, index_col=None, header=None)
    list_.append(df)
    frame = pd.concat(list_)
pass

# Set initial value (instead of reading a list of values as requested)
material_code = frame.loc[0, 1]
Porosity = 0.25
Roughness = 2.95
total_pore_area = 2.22

# Set parameters r,s,u,v _A (uguali per tutti i materiali)
A1 = 3.8447E-4
A2 = -4.0800E-6
A3 = -2.1164E-4
B1 = -2.7874E-2
B2 = 2.95905E-4
B3 = 1.1856E-2
C1 = 5.5270E-1
C2 = -5.8670E-3
C3 = -1.4727E-1
D1 = -2.1146
D2 = 2.2450E-2
D3 = 4.7041E-1

# Set parameters r,s,u,v _K (the same for all materials)
E1 = 8.3270E-5
E2 = 6.7E-7
E3 = -1.8459E-4
F1 = -6.0378E-3
F2 = -4.88E-5
F3 = 9.877E-3
G1 = 1.1971E-1
G2 = 9.69E-4
G3 = -1.0759E-1
H1 = -4.5803E-1
H2 = -3.71E-3
H3 = 3.1809E-1

# Set alfa, beta, gamma, deltaA, etaA, lambdaA, muA, deltaK, etaK, lambdaK, muK
if material_code == "brick":
    alfa = 1
    beta = 1
    gamma = 1
    deltaA = 1
    etaA = 1
    lambdaA = 1
    muA = 1
    deltaK = 1
    etaK = 1
    lambdaK = 1
    muK = 1

# deltaA, etaA, lambdaA, muA, deltaK, etaK, lambdaK, muK for i sandstone 
elif material_code == "sandstone":
    alfa = 2
    beta = 1.724
    gamma = 0.2
    deltaA = 1
    etaA = 1
    lambdaA = 1
    muA = 1
    deltaK = 1
    etaK = 1
    lambdaK = 1
    muK = 1

# deltaA, etaA, lambdaA, muA, deltaK, etaK, lambdaK, muK for i limestone 
elif material_code == "limestone":
    alfa = 100
    beta = 6.897
    gamma = 1.6
    deltaA = 1
    etaA = 1
    lambdaA = 1
    muA = 1
    deltaK = 1
    etaK = 1
    lambdaK = 1
    muK = 1
else:
    alfa = 1
    beta = 1
    gamma = 1
    deltaA = 1
    etaA = 1
    lambdaA = 1
    muA = 1
    deltaK = 1
    etaK = 1
    lambdaK = 1
    muK = 1
pass

ra = deltaA * (A1 * Porosity + A2 * Roughness + A3)
sa = etaA * (B1 * Porosity + B2 * Roughness + B3)
ua = lambdaA * (C1 * Porosity + C2 * Roughness + C3)
va = muA * (D1 * Porosity + D2 * Roughness + D3)

rk = deltaK * (E1 * Porosity + E2 * Roughness + E3)
sk = etaK * (F1 * Porosity + F2 * Roughness + F3)
uk = lambdaK * (G1 * Porosity + G2 * Roughness + G3)
vk = muK * (H1 * Porosity + H2 * Roughness + H3)

if Roughness == 5.02:
    t1 = 30
else:
    t1 = gamma * (5 / ((Roughness - 5.02) ** 2))
    pass

AcAt = (1 - na.exp(-alfa * (2.48 * Porosity + 0.126 * Roughness) ** 4))
K_rate_coefficient = (1 - na.exp(-beta * ((4.49E-3 * (Porosity * total_pore_area) - 5.79E-3) / 2.09) ** 2))
if AcAt < 0:
    AcAt = 0
else:
    pass
if AcAt > 1:
    AcAt = 1
else:
    pass
if K_rate_coefficient < 0:
    K_rate_coefficient = 0
else:
    pass

pass

covered_area = na.zeros([365, 1])
tempo = na.zeros([365, 1])
T_plot = na.zeros([365, 1])
rh_plot = na.zeros([365, 1])

for t in range(1, 365):

    # rh = 0.99
    # Temperature = 27.5
    Temperature = round(float(frame.iloc[t, 0]), 2)
    rh = round(float(frame.iloc[t, 1]), 2)

    if t == 1:
        covered_area[t] = 0
        delta_t = 0
    else:

        if t <= t1:
            covered_area[t] = covered_area[t - 1]
        else:

            tau_a = ra * Temperature ** 3 + sa * Temperature ** 2 + ua * Temperature + va
            tau_k = rk * Temperature ** 3 + sk * Temperature ** 2 + uk * Temperature + vk

            if tau_a < 0:
                tau_a = 0
            else:
                pass
            if tau_a > 1:
                tau_a = 1
            else:
                pass
            if tau_k < 0:
                tau_k = 0
            else:
                pass
            if tau_k > 1:
                tau_k = 1
            else:
                pass

            if rh >= 0.98:
                if Temperature < 5:
                    covered_area[t] = covered_area[t - 1]
                elif Temperature > 40:
                    covered_area[t] = covered_area[t - 1]
                else:
                    if covered_area[t - 1] < tau_a * AcAt:
                        delta_t = (-(1 / (tau_k * K_rate_coefficient)) * na.log(
                            1 - (covered_area[t - 1] / (tau_a * AcAt)))) ** (1 / 4) - (t - 1 - t1)
                        covered_area[t] = tau_a * AcAt * (
                                    1 - na.exp(-tau_k * K_rate_coefficient * (t + delta_t - t1) ** 4))
                    else:
                        covered_area[t] = covered_area[t - 1]
                    pass

                pass
            else:
                covered_area[t] = covered_area[t - 1]
            pass

        pass

        tempo[t] = t - 1
        # print(t)
    pass
    T_plot[t] = Temperature
    rh_plot[t] = rh

pass

# Data for plotting

t = tempo
Coverage = covered_area
data1 = Coverage
data2 = T_plot
data3 = rh_plot * 100

#na.savetxt(r"C:\Users\ocni\PycharmProjects\delphin_6_automation\pytest\test_files\damage_models\algae\covered_result.txt", covered_area[:, 0])
#na.savetxt(r"C:\Users\ocni\PycharmProjects\delphin_6_automation\pytest\test_files\damage_models\algae\rh.txt", rh_plot[:, 0])
#na.savetxt(r"C:\Users\ocni\PycharmProjects\delphin_6_automation\pytest\test_files\damage_models\algae\temparature.txt", T_plot[:, 0])

fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('time (days)')
ax1.set_ylabel('Coverage', color=color)
ax1.set_xlim([0, 365])
ax1.set_ylim([0, 1])
ax1.plot(t, data1, color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('Temperature & RH%', color=color)  # we already handled the x-label with ax1
ax2.set_ylim([0, 100])
ax2.plot(t, data2, color='orange')
ax2.plot(t, data3, color='blue')
ax1.grid()
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
# fig.savefig("test.png")
plt.show()
