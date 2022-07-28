import numpy as np
from manim import *
from sympy import Curve
from lib.mathutils import polar2xy, relative_quaternion, vec_compare

def arrow_angle(
    angle: float, 
    radius: float = 1,
    normal: np.array = OUT, 
    angle_offset = 0, 
    stroke_width: float | None = None,
    tip_length: float | None = None, 
    **kwargs
):
    if stroke_width == None and config.renderer == "opengl":
        stroke_width = 8 * radius
    if tip_length == None:
        tip_length = radius / 4
    
    start = polar2xy(angle_offset, radius)
    end = polar2xy(angle_offset+angle, radius)

    if vec_compare(normal, OUT):
        rot_angle, rot_axis = 0, OUT
    else:
        rot_angle, rot_axis = angle_axis_from_quaternion(relative_quaternion(OUT, normal))

    curve = CurvedArrow(
        start, end, angle=angle,
        stroke_width=stroke_width,
        tip_length=tip_length,
        **kwargs
    )
    curve.rotate_about_origin(rot_angle, rot_axis)

    return curve