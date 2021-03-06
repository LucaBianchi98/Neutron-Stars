import numpy as np
import bisect

#dictionary for units provided by LIGO https://github.com/lscsoft/bilby/blob/master/bilby/gw/eos/eos.py

c_si = 299792458 #m/s
c_cgs = c_si*100 #cm/s
G_si = 6.6743*1e-11  #m^3/(kg*s^2)
G_cgs = G_si*1000 #cm^3/(g*s^2)
Msun_si = 2.0*1e30  #kg
Msun_cgs = Msun_si*1000 #g
hbar_si = 1.054571817*1e-34 #J*s
m_N = 1.67492749804*1e-27 #kg 
cgs_geom_dictionary = { "geom": { "lenght": {"cm": 100.,
                                             "m": 1,
                                             "km": 1e-3
                                             },
                                 
                                  "time": {"cgs": 1/c_si,
                                           "si": 1/c_si,
                                           "geom": 1.
                                           },
                                 
                                  "mass": { "g": 1e3*(c_si**2.)/G_si,
                                            "kg": (c_si**2.)/G_si,
                                            "m_sol": (c_si**2.)/G_si/Msun_si
                                           },
                                                                   
                                  "energy": {"cgs": 1e7*(c_si**4.)/G_si, 
                                             "si": (c_si**4.)/G_si,
                                             },
                                  
                                  "energy_density": {"cgs": 10*(c_si**4.)/G_si
                                                     },
                                  
                                  "density": {"cgs": 1e-3*(c_si**2.)/G_si
                                              },
                                  
                                  "pressure": {"cgs": 10*(c_si**4.)/G_si
                                               }
                                  },
                       
                        "cgs": { "lenght": { "cm": 1.,
                                            "m": 1e-2,
                                            "km": 1e-5
                                            },
                                
                                 "time": { "cgs": 1,
                                          "si": 1,
                                          "geom": c_si
                                          },
                                
                                 "mass": {"kg": 1e-3,
                                          "geom": 1e-3*G_si/(c_si**2.) ,
                                          "m_sol": 1/Msun_cgs
                                          },
                                 
                                  "energy": {"si": 1e-7, 
                                            "geom": 1e-7*G_si/(c_si**4.)
                                            },
                                                         
                                 "energy_density": {"si": 0.1,
                                                    "geom": 0.1*G_si/(c_si**4.) 
                                                    },
                                 
                                 "density": {"si": 1e3,
                                             "geom": 1e3*G_si/(c_si**2.)
                                             },
                                                         
                                 "pressure": {"si": 0.1,
                                              "geom": 0.1*G_si/(c_si**4.)
                                              }
                                 },
                        "si" : { "lenght": {"cm": 100.,
                                            "m": 1.,
                                            "km": 1e-3
                                            },
                                
                                 "time": {"cgs": 1.,
                                          "geom": c_si,
                                          },
                                 
                                 "mass": {"g": 1000.,
                                          "kg": 1.,
                                          "geom":  G_si/(c_si**2.),
                                          "m_sol": 1/Msun_si
                                          },
                                                                                                
                                 "energy": {"cgs": 1e7, 
                                            "geom":  G_si/(c_si**4.)
                                           },
                                
                                "energy_density": {"cgs": 10.,
                                                   "geom": G_si/(c_si**4.)
                                                   },
                                
                                 "density": {"cgs": 1e-3,
                                             "geom": (c_si**2.)/G_si,
                                             },
                                
                                "pressure": {"cgs": 10.,
                                             "geom": G_si/(c_si**4.)
                        
                                             },
                                }
                        }
                        
def RungeKutta(f, t, dt, u, v):
         
    k1 = f(t, [u, v])
    k2 = f(t + dt/2, [u + dt*k1[0]/2, v + dt*k1[1]/2])
    k3 = f(t + dt/2, [u + dt*k2[0]/2, v + dt*k2[1]/2])
    k4 = f(t + dt, [u + dt*k3[0], v + dt*k3[1]])
    
    du = (1/6)*(dt*k1[0] + 2*dt*k2[0] + 2*dt*k3[0] + dt*k4[0])
    dv = (1/6)*(dt*k1[1] + 2*dt*k2[1] + 2*dt*k3[1] + dt*k4[1])
    return [du, dv]

#RK applied to Newton/TOV equations. Returns solutions.
def ODEsolver(eq_type, central_pressure):
    csi = 1e-10  
    step = 10   
    #first condition, m=0 at r=0.
    mass = np.array([0])
    #condition on pressure (or energy) at r=0.
    pressure = np.array([central_pressure])
    #start the solving from a radius value a little bit bigger then zero.
    radius = np.array([csi])
    
    i=0
    #stop the calculation when the star is over.
    #Condition on the pressure (or energy), zero out of the star.
    while(pressure[i]>0):
        
        dy = RungeKutta(eq_type, radius[i], step, mass[i], pressure[i])
        mass = np.append(mass, mass[i] + dy[0])
        pressure = np.append(pressure, pressure[i] + dy[1])
        radius = np.append(radius, radius[i]+step)          
        i = i+1

    return radius,mass,pressure

#Returns a spline function. 

def CubicSpline(x, y):
    #Solve the system by using second derivatives, which are linear in x for a cubic spline.
    #Integrating 2 times and using continuity we remove the 2n integration constants.
    #Then, by derivating and matching first derivatives we find the n-1 M. 
    #The remaining equations come from the boundary conditions, that is second derivatives set to 0.
    #The system to solve is made by a triangular matrix and we introduce c_p and d_p to solve it.
    
    #Split data x into intervals.
    n = len(x)
    h = []
    for i in range(n-1):
        h.append(x[i+1] - x[i])
        
    #LHS coefficients of the system.
    A = []
    B = [] 
    C = [] 
    C.append(0)
    for i in range(n-2):
        A.append(h[i]/(h[i] + h[i+1])) 
        C.append(h[i+1]/(h[i] + h[i+1]))        
    for i in range(n):
       B.append(2)
    A.append(0)
    
    #RHS of the system.
    D = [0] 
    for i in range(1, n-1):
        D.append(6*((y[i+1] - y[i])/h[i] - (y[i] - y[i-1])/h[i-1])/(h[i] + h[i-1]))
    D.append(0)
    
    #Solutions of the system with Thomas method
    c_p = C + [0] 
    d_p = [0]*n
    M = [0]*n 
    c_p[0] = C[0]/B[0]
    d_p[0] = D[0]/B[0]
    for i in range(1, n):
        c_p[i] = (c_p[i]/(B[i] - c_p[i-1]*A[i-1]))
        d_p[i] = (D[i] - d_p[i-1]*A[i-1])/(B[i] - c_p[i-1]*A[i-1])

    #Find the solution, from the last equation to the first.
    M[-1] = d_p[-1]
    for i in range(n-2, -1, -1):
        M[i] = d_p[i] - c_p[i]*M[i + 1]
    
    #Formula for cubic spline coefficients.
    coefficients = []
    for i in range(n-1):
        coefficients.append([((M[i+1] - M[i])*h[i]**2)/6, (M[i]*h[i]**2)/2, (y[i+1] - y[i] - ((M[i+1] + 2*M[i])*h[i]**2)/6), y[i]])

    #bisect function returns the position in the sorted list, we insert the element in the right place. 
    def spline(val): 
        idx = min(bisect.bisect(x, val) - 1, n-1)
        z = (val - x[idx])/h[idx]
        Coef = coefficients[idx]
        S_z = Coef[0]*z**3 + Coef[1]*z**2 + Coef[2]*z + Coef[3]
        return S_z 
    return spline 
  
read_parameters = {
#neutrons, protons, electrons and muons#
'PAL6':[34.380,  2.227,  2.189,  2.159], #potential method. 
'SLy':[34.384,  3.005,  2.988,  2.851], 
'APR1':[33.943,  2.442,  3.256,  2.908], #variational method.
'APR2':[34.126,  2.643,  3.014,  2.945],
'APR3':[34.392,  3.166,  3.573,  3.281],
'APR4':[34.269,  2.830,  3.445,  3.348],
'FPS':[34.283,  2.985,  2.863,  2.600],
'WFF1':[34.031,  2.519,  3.791,  3.660],
'WFF2':[34.233,  2.888,  3.475,  3.517],
'WFF3':[34.283,  3.329,  2.952,  2.589],
'BBB2':[34.331,  3.418,  2.835,  2.832], #NR Brueckner-Hartree-Fock method.
'BPAL12':[34.358,  2.209,  2.201,  2.176], #R Brueckner-Hartree-Fock method.
'ENG':[34.437,  3.514,  3.130,  3.168], #R mean-field method.
'MPA1':[34.495,  3.446,  3.572,  2.887],
'MS1':[34.858,  3.224,  3.033,  1.325],
'MS2':[34.605,  2.447,  2.184,  1.855],
'MS1b':[34.855,  3.456,  3.011,  1.425],
#mesons#
'PS':[34.671,  2.216,  1.640,  2.365], #pion condensate. 
'GS1a':[34.504,  2.350,  1.267,  2.421], #R mean-field method.
'GS2a':[34.642,  2.519,  1.571,  2.314],
#hyperons#
'BGN1H1':[34.623,  3.258,  1.472,  2.464], #effective potential method. 
'GNH3':[34.648,  2.664,  2.194,  2.304], #R mean-field method (hyperons only).
'H1':[34.564,  2.595,  1.845,  1.897],
'H2':[34.617,  2.775,  1.855,  1.858],
'H3':[34.646,  2.787,  1.951,  1.901],
'H4':[34.669,  2.909,  2.246,  2.144],
'H5':[34.609,  2.793,  1.974,  1.915],
'H6a':[34.593,  2.637,  2.121,  2.064],
'H7':[34.559,  2.621,  2.048,  2.006],
'PCL2':[34.507,  2.554,  1.880,  1.977], #R mean-field method (hyperons and quarks).
#quarks#
'ALF1':[34.055,  2.013,  3.389,  2.033], #mixed APR nuclear matter and color-flavour-locked quark matter.
'ALF2':[34.616,  4.070,  2.411,  1.890],
'ALF3':[34.283,  2.883,  2.653,  1.952],
'ALF4':[34.314,  3.009,  3.438,  1.803]
}
