import numpy as np
from calculemus import ODEsolver, cgs_geom_dictionary

#Class which builds a neutron star providing it a mass and a radius given by the solutions of TOV or Newton.
class NeutronStar:
    
    #Constructor, takes the type of neutron star and its equation of state.
    def __init__(self, NS_type, eq_state):
        
        self.kind = NS_type
        self.eos = eq_state
    
    #Returns the RHS increment.
    def Newton_eqs(self, r, y):
        #Unknowns.
        m,p=y
        #Couple with equation of state.
        eden = self.eos.Eden_from_Pres(p)
        dm = 4*np.pi*eden*r**2
        dp = - (eden*m)/(r**2)
        dy = [dm, dp]

        return dy        
    
    #Returns the RHS increment. 
    def TOV_eqs(self, r, y):
        #Unknowns.
        m,p=y
        if p<0:
            return [0,0]
        eden = self.eos.Eden_from_Pres(p)
        dm = 4*np.pi*eden*r**2
        dp = - (eden+p)*(m + 4*np.pi*r**3*p)/(r*(r-2*m))
        dy = [dm, dp]
        
        return dy

    #Makes use of calculemus ODE solver
    def star_solver(self, eq_type, central_value, value_type="pressure", unit_type="geom"):
        #in geometrical units smaller numerical errors
        central_value = central_value*cgs_geom_dictionary[unit_type][value_type]["geom"]
        
        #To perform the calculation we need pressure values.
        if value_type == "density":
            central_value = self.eos.Pres_from_Den(central_value)
        
        #Build solutions.
        solutions = ODEsolver(eq_type, central_value)
        r_out = np.array([])
        m_out = np.array([])
        p_out = np.array([])

        for i in range(solutions[0].size):
            r_out = np.append(r_out, solutions[0][i]*cgs_geom_dictionary["geom"]["lenght"]["km"])
            m_out = np.append(m_out, solutions[1][i]*cgs_geom_dictionary["geom"]["mass"]["m_sol"])
            p_out = np.append(p_out, solutions[2][i]*cgs_geom_dictionary["geom"]["pressure"]["cgs"])

        return r_out, m_out, p_out
        
