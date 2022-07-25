import numpy as np
from manim import *
from manim.utils.space_ops import (
    quaternion_mult,
    quaternion_from_angle_axis,
    angle_axis_from_quaternion,
    quaternion_conjugate,
)

def clamp(x, min_val=0, max_val=1):
    return max( min_val, max( max_val, x ) )

def smoothstep(edge0: float, edge1: float, x: float):
    if x < edge0:
        return 0
    if x >= edge1:
        return 1
    x = (x - edge0) / (edge1 - edge0)
    return x * x * (3 - 2 * x)

def rotate_cc(vec):
    return np.array([ -vec[1], vec[0], vec[2] ])
    
def rotate_cw(vec):
    return np.array([ vec[1], -vec[0], vec[2] ])

def relative_quaternion( v1, v2, fallback_axis=None ):
    mid = v1 + v2
    mid = mid / np.linalg.norm(mid)
    dot = np.dot(v1, mid)
    cross = np.cross(v1, mid)
    epsilon = 0.00001
    if (not fallback_axis is None) and np.abs( dot + 1 ) < epsilon:
        return np.array([0, *fallback_axis])
    return np.array([dot, *cross])

def relative_quaternion2( forward1, up1, forward2, up2 ):
    """ Finds the relative rotation between two orientations given their forward and up directions. """
    forward_quat = relative_quaternion(forward1, forward2)
    up1_by_forward_quat = rotate_vec_by_quat(up1, forward_quat)
    up_quat = relative_quaternion( up1_by_forward_quat, up2, fallback_axis=forward2 )
    result = quaternion_mult( up_quat, forward_quat )
    # print( "\nRotated forward, up:" )
    # print( np.around( rotate_vec_by_quat( forward1, result ), 3 ) )
    # print( np.around( rotate_vec_by_quat( up1, result ), 3) )
    # print("")
    return result

def rotate_vec_by_quat(vec, quat):
    quat_inv = quaternion_conjugate(quat)
    return quaternion_mult(
        quaternion_mult( quat, np.array([ 0, *vec ]) ),
        quat_inv
    )[1:]

def polar2xy(theta, radius=1):
    return RIGHT * np.cos(theta) * radius + UP * np.sin(theta) * radius

# print("\n=Tests===")
# print(relative_quaternion(
#     np.array([1, 0, 0]),
#     np.array([0, 1, 0]),
# ))
# print(
#     relative_quaternion2(
#         np.array([1, 0, 0]),
#         np.array([0, 1, 0]),

#         np.array([0, 1, 0]),
#         np.array([1, 0, 0]),
#     )
# )
# print("=========\n")