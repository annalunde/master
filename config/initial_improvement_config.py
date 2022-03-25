from datetime import datetime, timedelta


# Allowed excess ride time
F = 1

# Number of vehicles
V = 16

# Allowed deviaiton from Requested service time (either pickup or dropoff)
U_D_N = timedelta(minutes=5)
L_D_N = timedelta(minutes=-5)
U_D_D = timedelta(minutes=30)
L_D_D = timedelta(minutes=-30)

# Estimated time to serve a node
S_P = 2  # standard seats
S_W = 5  # wheelchair

# Vehicle standard seats capacity
P = 15

# Vehicle wheelchair seats capacity
W = 1

# Weight of ride time in objective function
alpha = 1

# Weight of deviation in objective function
beta = 5

# Weight of infeasible set in objective function
gamma = 10000
