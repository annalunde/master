from decouple import config
from datetime import datetime, timedelta


# Allowed excess ride time
F = 1

# Number of vehicles
V = 16

# Allowed deviaiton from Requested service time (either pickup or dropoff)
U_D = timedelta(minutes=15)
L_D = timedelta(minutes=-15)
P_S = timedelta(minutes=7.5)  # penalized soft time windows

# Rush hour factor
R_F = 1.5

# Estimated time to serve a node
S_P = 2  # standard seats
S_W = 5  # wheelchairs

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

chosen_columns = [
    "Request Creation Time",
    "Wheelchair",
    "Request ID",
    "Request Status",
    "Rider ID",
    "Ride ID",
    "Number of Passengers",
    "Requested Pickup Time",
    "Actual Pickup Time",
    "Requested Dropoff Time",
    "Actual Dropoff Time",
    "Cancellation Time",
    "No Show Time",
    "Origin Zone",
    "Origin Lat",
    "Origin Lng",
    "Destination Zone",
    "Destination Lat",
    "Destination Lng",
    "Reason For Travel",
    "Original Planned Pickup Time",
]
