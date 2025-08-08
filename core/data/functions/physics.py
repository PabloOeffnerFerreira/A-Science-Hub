from math import sqrt
def kinetic_energy(m, v): return 0.5 * m * v * v
def speed(distance, time): return distance / time
def terminal_velocity(m, rho, A, Cd, g=9.80665): return sqrt((2*m*g)/(rho*A*Cd))
