from manim import *

UP_RIGHT = normalize(UP + RIGHT)

class ExternalLabeledDot(VMobject):

    def __init__(self, dot, label_or_str, direction=UP_RIGHT, aligned_edge=None, distance=0.75, **kwargs):
        super().__init__(**kwargs)
        
        self.dot = dot
        if isinstance(label_or_str, str):
            self.label = MathTex(label_or_str)
        else:
            self.label = label_or_str

        super().add(self.dot)
        super().add(self.label)

        self.direction = direction
        self.distance = distance
        if aligned_edge is None:
            self.aligned_edge = -self.direction
        else:
            self.aligned_edge = aligned_edge
        
        self.position_label(self.label)
        self.label.add_updater(lambda label: self.position_label(label))

    def position_label(self, label):
        return label.next_to(self.dot, direction=self.direction * self.distance, aligned_edge=self.aligned_edge)
    
    def create_animation(self):
        return AnimationGroup(
            GrowFromCenter(self.dot),
            Write(self.label)
        )
    
    def animate_relabel(self, next_label: MathTex, **kwargs):
        old_label = self.label
        self.label = next_label

        next_label.add_updater(lambda label: self.position_label(label))
        self.position_label(next_label)

        return TransformMatchingTex(old_label, next_label, **kwargs)

# class _TestScene(Scene):
#     def construct(self):
#         dot = ExternalLabeledDot( Dot(ORIGIN), "e^{i\pi}", distance=1 )
#         self.play( FadeIn(dot) )
#         self.play( Transform( dot.label, MathTex("-1").next_to(dot.label, RIGHT) ) )
#         self.play( dot.animate.update_label_position() )
#         self.wait()