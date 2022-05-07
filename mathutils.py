import numpy as np

def rotate_cc(vec):
    return np.array([ -vec[1], vec[0], vec[2] ])
    
def rotate_cw(vec):
    return np.array([ vec[1], -vec[0], vec[2] ])