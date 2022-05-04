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
        if aligned_edge == None:
            self.aligned_edge = -self.direction

        self.update_label_position()
    
    def update_label_position(self):
        self.label.next_to(self.dot, direction=self.direction * self.distance, aligned_edge=self.aligned_edge)

    def create_animation(self):
        return AnimationGroup(
            GrowFromCenter(self.dot),
            Write(self.label)
        )

class _TestScene(Scene):
    def construct(self):
        dot = ExternalLabeledDot( Dot(ORIGIN), "e^{i\pi}", distance=1 )
        self.play( FadeIn(dot) )
        self.play( Transform( dot.label, MathTex("-1").next_to(dot.label, RIGHT) ) )
        self.play( dot.animate.update_label_position() )
        self.wait()