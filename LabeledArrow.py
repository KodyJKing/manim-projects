from manim import *
import numpy as np

from mathutils import rotate_cc

class LabeledArrow(VMobject):

    def __init__(
        self, arrow: Arrow, label_or_str: Tex | str, alpha: float = 1,
        distance: float = .25, perp_distance: float = 0,
        aligned_edge=ORIGIN, **kwargs
    ):
        super().__init__(**kwargs)

        self.alpha = alpha
        self.distance = distance
        self.perp_distance = perp_distance
        self.aligned_edge = aligned_edge

        self.arrow = arrow
        if isinstance(label_or_str, str):
            self.label = MathTex(label_or_str)
        else:
            self.label = label_or_str
        
        self.add(self.arrow)
        self.add(self.label)
        
        self.refresh_updaters()

    def refresh_updaters(self):
        def update_label(label):
            arrow_dir = self.arrow.get_unit_vector()
            length = self.arrow.get_length()
            position = ( self.arrow.get_start() + arrow_dir * (self.alpha * length + self.distance)
                + rotate_cc(arrow_dir) * self.perp_distance )
            label.move_to(position, aligned_edge=self.aligned_edge)
        self.label.clear_updaters()
        self.label.add_updater(update_label)

    def copy(self):
        result = super().copy()
        result.refresh_updaters()
        return result
    
    def grow_animation(self):
        return GrowFromPoint( self, self.arrow.get_start() )
