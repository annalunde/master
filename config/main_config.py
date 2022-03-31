from datetime import datetime, timedelta


reaction_factor = 0.7

weights = [15, 10, 5, 0]

iterations = 100

destruction_degree = 0.4

# Number of requests
R = 106

# Number of vehicles
V = 16

# Number of tries for + 15 minutes for a rejected request:
N_R = 0

# Simulated annealing temperatures -- NOTE: these must be tuned
start_temperature = 50
end_temperature = 10
cooling_rate = 0.999
