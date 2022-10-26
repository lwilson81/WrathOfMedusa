import numpy as np


def fifth_poly(q_i, q_f, t):
    # time/0.005
    traj_t = np.arange(0, t, 0.004)
    dq_i = 0
    dq_f = 0
    ddq_i = 0
    ddq_f = 0
    a0 = q_i
    a1 = dq_i
    a2 = 0.5 * ddq_i
    a3 = 1 / (2 * t ** 3) * (20 * (q_f - q_i) - (8 * dq_f +
                                                 12 * dq_i) * t - (3 * ddq_f - ddq_i) * t ** 2)
    a4 = 1 / (2 * t ** 4) * (30 * (q_i - q_f) + (14 * dq_f +
                                                 16 * dq_i) * t + (3 * ddq_f - 2 * ddq_i) * t ** 2)
    a5 = 1 / (2 * t ** 5) * (12 * (q_f - q_i) -
                             (6 * dq_f + 6 * dq_i) * t - (ddq_f - ddq_i) * t ** 2)
    traj_pos = a0 + a1 * traj_t + a2 * traj_t ** 2 + a3 * \
        traj_t ** 3 + a4 * traj_t ** 4 + a5 * traj_t ** 5
    return traj_pos
