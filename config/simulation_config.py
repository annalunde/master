import numpy as np

# estimated service time of a node
S_P = 2  # standard seats
S_W = 5  # wheelchair

# ARRIVAL RATES FOR DISRUPTION TYPES
arrival_rate_request = np.array([20.89189189189189, 13.378378378378379, 10.873873873873874, 8.977477477477477,
                                 7.36936936936937, 5.387387387387387, 3.7972972972972974, 0.6621621621621622,
                                 0.02252252252252252], dtype=float)

# med delay = 0.5 minutes
arrival_rate_delay = np.array([7.194444444444445, 6.333333333333333, 6.337962962962963, 6.949074074074074,
                               7.337962962962963, 7.597222222222222, 4.791666666666667, 2.449074074074074,
                               0.0787037037037037], dtype=float)

arrival_rate_cancel = np.array([3.0462962962962963, 2.1805555555555554, 1.9490740740740742, 1.75,
                                1.3981481481481481, 0.7824074074074074, 0.33796296296296297, 0.06944444444444445,
                                0.0001], dtype=float)

arrival_rate_no_show = np.array([0.719047619047619, 0.8714285714285714, 0.8380952380952381, 0.8809523809523809,
                                 1.061904761904762, 0.9761904761904762, 0.5428571428571428, 0.34285714285714286,
                                 0.01904761904761905], dtype=float)

# start and end time of Poisson - 0 is 10.00 and 9 is 18.00
start_poisson = 0
end_poisson = 9

# percentage of requests with requested pickup time
percentage_dropoff = 1.7523953605648008/100

# PARAMETERS FOR GAMMA DISTRIBUTION FOR REQUESTED PICKUP TIME
pickup_fit_shape = 1.0099021053517845
pickup_fit_loc = 0.18326168773040002
pickup_fit_scale = 107.89424220559195

# PARAMETERS FOR GAMMA DISTRIBUTION FOR REQUESTED DROPOFF TIME
dropoff_fit_shape = 4.448374147659267
dropoff_fit_loc = -47.161377830375486
dropoff_fit_scale = 47.59166885428937

# PARAMETERS FOR BETA DISTRIBUTION FOR DELAYS
delay_fit_a = 0.8920223245173695
delay_fit_b = 22.23772193022893
delay_fit_loc = 4.999999999999999
delay_fit_scale = 168.82933635388434
