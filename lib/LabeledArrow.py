from manim import *
import numpy as np

from lib.mathutils import rotate_cc

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

    def position_label(self, label):
        arrow_dir = self.arrow.get_unit_vector()
        length = self.arrow.get_length()
        position = ( self.arrow.get_start() + arrow_dir * (self.alpha * length + self.distance)
            + rotate_cc(arrow_dir) * self.perp_distance )
        label.move_to(position, aligned_edge=self.aligned_edge)

    def refresh_updaters(self):
        self.label.clear_updaters()
        self.label.add_updater(lambda label: self.position_label(label))
        self.position_label(self.label)

    def copy(self):
        result = super().copy()
        result.refresh_updaters()
        return result
    
    def grow_animation(self):
        return GrowFromPoint( self, self.arrow.get_start() )

    def relabel(self, next_label: MathTex, add_next=True, scene: Scene=None):
        old_label = self.label
        self.label = next_label
        next_label.add_updater(lambda label: self.position_label(label))
        self.position_label(next_label)
        self.remove(old_label)
        if add_next:
            self.add(next_label)
        if scene:
            scene.remove(old_label)

    def animate_relabel(self, next_label: MathTex, match_tex=True, extra_sources: Group | None = None, **kwargs):
        old_label = self.label
        self.relabel(next_label, False)

        if match_tex:
            sources = extra_sources if extra_sources else Group()
            sources.add(old_label)
            animation = TransformMatchingTex(sources, next_label, **kwargs)
        else:
            animation = ReplacementTransform(old_label, next_label, **kwargs)

        def on_finish(scene: Scene):
            self.add(next_label)

        return AnimationGroup(animation, _on_finish=on_finish )
