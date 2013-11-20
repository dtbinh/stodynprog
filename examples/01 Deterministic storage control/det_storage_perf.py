#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Assess the performance of the deterministic storage control:
Pierre Haessig — November 2013
"""

from __future__ import division, print_function, unicode_literals
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool

from det_storage_control import p, generate_input, N_E, dpsolv, T_horiz

J_fin = np.zeros(N_E)

N_samples = 50

E_rated_list = [0.2, 0.5, 1, 2, 3, 4, 5, 6, 7, 10.]

def compute_rms_deviation(E_rated):
    print('E_rated = {:.1f}'.format(E_rated))
    p['E_rated'] = E_rated
    dpsolv.discretize_state(0, p['E_rated'], N_E)[0]

    # Generate a new random input:
    generate_input()

    # Solve the problem:
    J, pol = dpsolv.bellman_recursion(T_horiz, J_fin)

    # RMS cost:
    J_l2_mid = np.sqrt(J[0,N_E//2]/T_horiz)
    print('RMS deviation if SoE(0)=0.5: {:.4f}'.format(J_l2_mid))
    return J_l2_mid

def compute_rms_deviation_list(n):
    print('\n**** Sample {:2d} ****'.format(n))
    rms = []
    np.random.seed(n)
    for E_rated in E_rated_list:
        rms.append(compute_rms_deviation(E_rated))
    return rms


if __name__ == '__main__':
    pool = Pool(8)
    rms_list = pool.map(compute_rms_deviation_list, range(N_samples), chunksize=1)
    print(rms_list)
    
    rms_list = np.array(rms_list).T
    
    ### Save computation:
    np.savez('whitenoise_perf.npz', E_rated_list = E_rated_list,
                                 rms_list = rms_list)
    assert rms_list.shape == (len(E_rated_list), N_samples)
    d = np.load('whitenoise_perf.npz')
    
    rms_mean = np.sqrt(np.mean(rms_list**2, axis=1))
    rms_std = np.std(rms_list, axis=1)
    
    fig = plt.figure('RMS = f(E_rated)')
    ax = fig.add_subplot(111,  title='Cost evolution with the storage capacity',
                         xlabel='$E_{rated}$ (MWh)', ylabel='RMS deviation (MW)')
    plt.plot(E_rated_list, rms_mean, 'r', label='anticipative opt. ctrl')
    plt.plot(E_rated_list, rms_list, 'rx', alpha=0.3)
    plt.fill_between(E_rated_list, rms_mean-rms_std, rms_mean+rms_std,
                     alpha=0.3, color='r', lw=0)

    plt.legend(loc='upper right')
    plt.ylim(0,1)

    plt.show()