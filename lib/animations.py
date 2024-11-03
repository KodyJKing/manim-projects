from math import inf
from typing import Callable, Tuple
import numpy as np
from manim import *

DIAGONALS = [ UL, UR, DR, DL ]

def extent(mobj: Mobject, direction: np.array):
    maxDot = -inf
    for dir in DIAGONALS:
        v = mobj.get_corner(dir)
        maxDot = max( maxDot, np.dot(v, direction) )
    return maxDot

class WaveInDirection(Homotopy):
    """Send a wave through the Mobject distorting it temporarily.

    Parameters
    ----------
    mobject
        The mobject to be distorted.
    direction
        The direction in which the wave nudges points of the shape
    amplitude
        The distance points of the shape get shifted
    wave_func
        The function defining the shape of one wave flank.
    time_width
        The length of the wave relative to the width of the mobject.
    ripples
        The number of ripples of the wave
    run_time
        The duration of the animation.
    """

    def __init__(
        self,
        mobject: "Mobject",
        direction: np.ndarray = RIGHT,
        nudge_direction: np.ndarray = UP,
        amplitude: float = 0.2,
        wave_func: Callable[[float], float] = smooth,
        time_width: float = 1,
        ripples: int = 1,
        run_time: float = 2,
        **kwargs
    ) -> None:
        minExtent = -extent(mobject, -direction)
        maxExtent = extent(mobject, direction)
        vect = amplitude * normalize(nudge_direction)

        def wave(t):
            # Mirrored looks better in the way the wave is used.
            t = 1 - t

            # Clamp input
            if t >= 1 or t <= 0:
                return 0

            phases = ripples * 2
            phase = int(t * phases)
            if phase == 0:
                # First rising ripple
                return wave_func(t * phases)
            elif phase == phases - 1:
                # last ripple. Rising or falling depending on the number of ripples
                # The (ripples % 2)-term is used to make this destinction.
                t -= phase / phases  # Time relative to the phase
                return (1 - wave_func(t * phases)) * (2 * (ripples % 2) - 1)
            else:
                # Longer phases:
                phase = int((phase - 1) / 2)
                t -= (2 * phase + 1) / phases

                # Similar to last ripple:
                return (1 - 2 * wave_func(t * ripples)) * (1 - 2 * ((phase) % 2))

        def homotopy(
            x: float,
            y: float,
            z: float,
            t: float,
        ) -> Tuple[float, float, float]:
            upper = interpolate(0, 1 + time_width, t)
            lower = upper - time_width
            extent = direction[0] * x + direction[1] * y
            rel = inverse_interpolate(minExtent, maxExtent, extent)
            wave_phase = inverse_interpolate(lower, upper, rel)
            nudge = wave(wave_phase) * vect
            return np.array([x, y, z]) + nudge

        super().__init__(homotopy, mobject, run_time=run_time, **kwargs)