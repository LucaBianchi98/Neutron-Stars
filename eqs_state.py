import numpy as np
from calculemus import *
    
class Polytropic:
    #Set to zero constant in the simple NR case, crucial value in the piecewise polytropic for the continuity of eden.
    a = 0.0
    #Constructor, polytropic parameters.
    def __init__(self, k, gamma):
        self.kind = "PressureEnergyDensityPolytropic"
        #polytropic factor.
        self.k = k 
        #polytropic index.
        self.gamma = gamma
        #polytropic N.
        self.n = 1/(self.gamma-1)
        
    def Den_from_Pres(self, pressure):
        density = (pressure/self.k)**(1/self.gamma)
        return density
        
    def Pres_from_Den(self, density):
        pressure = self.k*density**self.gamma
        return pressure
    #for NR polytropic Den=Eden
    def Eden_from_Pres(self, pressure):
        density = self.Den_from_Pres(pressure)
        eden = self.Eden_from_Den(density)
        return eden

    def Eden_from_Den(self,density):
        eden = (1+self.a)*density + self.n*self.k*(density**self.gamma)
        return eden

class Piecewise:
    
    def __init__(self, key): 
        #Go from the external layer of the crust to the inner layer of the core.
        parameters = read_parameters[key]
        self.kind = "PressureEnergyDensityPiecewise"
        #gammaSly0,sly1,sly2,sly3,gamma1,2,3
        self.gammas = [1.58425, 1.28733, 0.62223, 1.35692, parameters[1], parameters[2], parameters[3]]
        #ksly0,sly1,sly2,sly3
        self.kappas = [6.80110e-9, 1.06186e-6, 5.32697e1, 3.99874e-8] 
        #rhosly1,2,3,trans,2,3,central
        self.densities = [1e3,  2.44034e7, 3.78358e11, 2.62780e12, 2.7e14, 10**(14.7), 1e15]  
        self.densities = [x*cgs_geom_dictionary["cgs"]["density"]["geom"] for x in self.densities]
        #k1*trans**gamma1
        self.trans_pressure = (10**parameters[0])*cgs_geom_dictionary["cgs"]["pressure"]["geom"]
        #Prepare the tropes for the piecewise.
        self.layers = []
        self.edens = []
        self.pressures = []
        
    def BuildK(self):
        #Continuity of the pressure.
        for i in range(len(self.kappas)):
            self.kappas[i] = (c_cgs**2)*(self.kappas[i]*cgs_geom_dictionary["cgs"]["lenght"]["m"]**(3*self.gammas[i] -1)
                                               *cgs_geom_dictionary["cgs"]["time"]["geom"]**(-2)
                                               *cgs_geom_dictionary["cgs"]["mass"]["geom"]**(1-self.gammas[i]))     
        #Interior kappas.
        k1 = self.trans_pressure/(self.densities[4]**self.gammas[4])
        k2 = k1*self.densities[5]**(self.gammas[4]-self.gammas[5])
        k3 = k2*self.densities[6]**(self.gammas[5]-self.gammas[6])
        self.kappas.append(k1)
        self.kappas.append(k2)
        self.kappas.append(k3)
    
    def BuildPressures(self):
        for density in self.densities:
            self.pressures = self.PressureFromDensity(density)
        
    def BuildPiecewise(self):
        for k, gamma in zip(self.kappas, self.gammas):  
            #Polytropic in each layer.
            self.layers.append(Polytropic(k, gamma))
        #Glue the crust and the core.
        self.densities[4] = (self.kappas[4]/self.kappas[3])**(1/(self.gammas[3]-self.gammas[4]))
        
        prev_layer=None
        for (layer, density) in zip(self.layers, self.densities):

                if not( prev_layer == None ):
                    #Continuity of the energy density.
                    layer.a = self.set_trans_const( prev_layer, layer, density )
                else:
                    #Outer layer of the crust, max radius energy gives a=0.
                    density = 0.0

                eden = layer.Eden_from_Den(density)
                pressure = layer.Pres_from_Den(density)

                #Eden and pressure corresponding to the densities transition values.
                self.pressures.append(pressure)
                self.edens.append(eden)
                
                prev_layer = layer

    def set_trans_const(self, prev_layer, layer, transition):
        return prev_layer.a + (prev_layer.k/(prev_layer.gamma - 1))*transition**(prev_layer.gamma-1) - (layer.k/(layer.gamma - 1))*transition**(layer.gamma-1)
    
    #Piecewise of density, energy density and pressure convertion.    
    def Pres_from_Den(self, density):        
        layer = self.FindLayer(density, "density")
        return layer.Pres_from_Den(density) 

    def Den_from_Pres(self, pressure,index="False"):                
        layer = self.FindLayer(pressure, "pressure")
        return layer.Den_from_Pres(pressure)     

    def Eden_from_Pres(self, pressure):                
        layer = self.FindLayer(pressure, "pressure")
        return layer.Eden_from_Pres(pressure)    
    
    #Going from the outside to the inner region. 
    #Match the value of density/pressure untill it meet a transition value which is bigger.
    #Then it returns the layer. 
    def FindLayer(self, value, value_type):
        if value_type == "pressure":
            if value >= self.pressures[-1]:
                return self.layers[-1]
            for x in range( len(self.pressures) - 1):
                if self.pressures[x] <= value < self.pressures[x+1]:
                    return self.layers[x]                
        elif value_type == "density":
            if value >= self.densities[-1]:
                return self.layers[-1]
            for x in range( len(self.densities) - 1):
                if self.densities[x] <= value < self.densities[x+1]:
                    return self.layers[x] 
                
                
                
class Implicit:
    
    def __init__(self):
        self.kind = "PressureEnergyDensityImplicit"        
        self.e0 = ((m_N**4)*(c_si**5)/((np.pi**2)*(hbar_si**3)))*cgs_geom_dictionary['si']['energy_density']['geom']
        self.Eden_from_Pres, self.Pres_from_Den = self.InterpolateSolution()
        
    def ImplicitDensity(self, x):       
        return (self.e0/8)*((2*x**3 + x)*np.sqrt(1.0 + x**2) - np.arcsinh(x))

    def ImplicitPressure(self, x):
        return (self.e0/24)*((2*x**3 - 3*x)*np.sqrt(1.0 + x**2) + 3*np.arcsinh(x))
    
    
    def InterpolateSolution(self):
        #Giving enough Fermi momenta to build a good spline.
        x_range = np.linspace(0,1e3,int(100000))
        p_column, e_column = self.ImplicitPressure(x_range), self.ImplicitDensity(x_range)

        return CubicSpline(p_column, e_column), CubicSpline(e_column, p_column)
