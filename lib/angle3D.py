import numpy as np
from manim import *
from lib.mathutils import relative_quaternion2
from manim.utils.space_ops import (
    quaternion_mult,
    quaternion_from_angle_axis,
    angle_axis_from_quaternion,
    quaternion_conjugate,
)

def angle3D(line_a: Line, line_b: Line, **kwargs):
    """ Works around inability to use Angle on lines in 3D """

    CENTER_OF_ROT = line_a.get_start()

    forward1 = RIGHT
    up1 = OUT

    forward2 = line_a.get_unit_vector()
    up2 = normalize(np.cross(forward2, line_b.get_unit_vector()))

    rel_quat = relative_quaternion2(forward1, up1, forward2, up2)
    rel_quat_inv = quaternion_conjugate(rel_quat)

    angle, axis = angle_axis_from_quaternion(rel_quat_inv)

    pre_line_a = line_a.copy().rotate(angle, axis, CENTER_OF_ROT)
    pre_line_b = line_b.copy().rotate(angle, axis, CENTER_OF_ROT)

    mask = np.array([1, 1, 0])
    masked_line = lambda line: Line(line.get_start() * mask, line.get_end() * mask)

    angle_mobj = Angle(masked_line(pre_line_a), masked_line(pre_line_b), **kwargs)

    angle, axis = angle_axis_from_quaternion(rel_quat)
    angle_mobj.rotate(angle, axis, CENTER_OF_ROT)

    return angle_mobj