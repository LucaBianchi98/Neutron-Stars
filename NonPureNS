from eqs_state import Piecewise
from NSclass import NeutronStar as ns
from calculemus import cgs_geom_dictionary
import matplotlib.pyplot as plt
import numpy as np

#Creating the equation of state.
cv = 3.5e15
#Choose the model for the interior from the table.
chosen_state = Piecewise("PAL6")
chosen_state.BuildK()
chosen_state.BuildPiecewise()

#Creating the star.
star = ns("ReadNS", chosen_state)

#Mass and pressure vs radius

#Solving the system.
r_newton, m_newton, p_newton = star.star_solver(star.Newton_eqs, cv, "density", "cgs")
r_TOV,m_TOV,p_TOV = star.star_solver(star.TOV_eqs, cv, "density", "cgs")

print("central value of ", cv, "g/cm**3")

print("Newton: mass = ", m_newton[-1],"solar masses; total radius =", r_newton[-1], "km")
R_newton = r_newton[-1]
M_newton= m_newton[-1]

print("TOV: mass = ", m_TOV[-1],"solar masses; total radius =", r_TOV[-1], "km")
R_TOV = r_TOV[-1]
M_TOV= m_TOV[-1]

#Plotting.

fig,ax = plt.subplots()
ax.plot(r_newton, p_newton, color="red", label = 'Newton p(r)')
ax.plot(r_TOV, p_TOV, color="blue", label = 'TOV p(r)')
ax.set_xlabel('r [km]',fontsize=10)
ax.set_ylabel('P [$dyne/cm^2$]', fontsize=10)
ax.minorticks_on()

ax2 = ax.twinx()
ax2.minorticks_on()
ax2.plot(r_newton, m_newton,color="red", linestyle=":", label = 'Newton m(r)')
ax2.plot(r_TOV, m_TOV, color="blue", linestyle=":", label = 'TOV m(r)')
ax2.plot(R_newton, M_newton, marker = 'o', linestyle="", color='red', label='Newtonian mass')
ax2.plot(R_TOV, M_TOV, marker = 'o', color='blue', linestyle="", label='TOV mass')
ax2.set_ylabel("m/$M_{\odot}$",fontsize=10)

fig.legend(loc='lower right', bbox_to_anchor=(1.47,0.55), bbox_transform=ax.transAxes)
