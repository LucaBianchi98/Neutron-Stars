# Neutron-Stars
A project for solving the structure equations of a neutron star.
You can solve Newton equations or TOV equations for three main types of equation of states: non relativistic, relativistic and Read. 
The last one consists on fitting in a piecewise polytropical equation of state a bunch of candidate equations of state, with parameters depending on the particle content of the star taken in exam, the method for modelizing the potential and constraints putted by observational datas and GR.
As an output, you get the mass and the pressure of the considered star as a function of the distance. 

# Instructions
To test the program, you have to select one of the three possible mains (i.e. one from "NonPureNS", "RPureNS", "NRPureNS"), give a cv = central value and execute the program. 
For the Non Pure equation of state case, you can select from the file "calculemus" one of the candidate models by uncommenting it (only one candidate at a time).
A PDF file is loaded to get informations on the theory behind neutron stars and numerical algorithms used in the code.
# Acknowledgements
A very grateful thanks to Matteo Tagliazucchi for suggesting me very useful papers, especially "Constraints on a phenomenologically parametrized neutron-star equation of state" by Read et al. A special thanks also to Federico Rocco for giving me advice on the formal structure of the code, without him it would have been a messy, chaotic and unreadable one file code. 
# Bibliography
"Neutron stars for undergraduates", R. R. Silbar, S. Reddy, 2004.\\
"Compact Stars for Undergraduates", I. Sagert et al, 2004.
"Constraints on a phenomenologically parametrized neutron-star equation of state", J. Read et al, 2009.
"On Massive Neutron Cores", J. Oppenheimer, 1939.
"Computational Physics, Lecture Notes Fall 2015", M. Jensen, 2015.
"Programming for Computations - A Gentle Introduction to Numerical Simulations with Python", S. Linge, H.Langtangen, 2016.
https://en.wikiversity.org/wiki/Cubic_Spline_Interpolation
