import cmath
from manim import *

def comp2vec(c: complex):
    return np.array([c.real, c.imag, 0])

class ComplexArrow(VMobject):
    def __init__(self, value, color: str, **kwargs):
        super().__init__(**kwargs)

        self.arrow = Arrow(ORIGIN, value, buff=0, color=color)
        self.dot = Dot(z_index=1)
        self.line_re = Line(ORIGIN, RIGHT, color=color)
        self.angle = Angle(self.line_re, self.arrow, color=color, z_index=-1)
        self.add(self.arrow, self.dot, self.line_re, self.angle)

class ComplexProduct(VMobject):
    def __init__(
        self, 
        u: complex, v: complex,
        u_color = BLUE, v_color = YELLOW, uv_color = GREEN,
        **kwargs
    ):
        super().__init__(**kwargs)

        uv = u * v
        self.u = u
        self.v = v
        self.uv = uv

        self.arrow_u = ComplexArrow(comp2vec(u), u_color)
        self.arrow_v = ComplexArrow(comp2vec(v), v_color)
        self.arrow_uv = ComplexArrow(comp2vec(uv), uv_color)

        self.tex_times =  MathTex("\\times")
        self.tex_equals = MathTex("=")
        self.equation = VGroup(self.arrow_u, self.tex_times, self.arrow_v, self.tex_equals, self.arrow_uv)
        self.equation.arrange_in_grid(1, 5, buff=1, cell_alignment=DOWN)
        self.tex_equals.move_to(self.tex_times, coor_mask=UP) # Fix equal sign to line up with plus sign.

        self.add(self.arrow_u, self.arrow_v, self.arrow_uv, self.equation)
    
    def animate(self, scene: Scene):
        arrow_u_copy = self.arrow_u.copy()
        arrow_v_copy = self.arrow_v.copy()
        self.add(arrow_u_copy, arrow_v_copy)

        display_arrow = lambda arrow: always_redraw(lambda: Arrow(
            arrow.arrow.get_start(),
            arrow.arrow.get_end(),
            color=arrow.arrow.get_fill_color(),
            buff=0
        ))

        arrow_u_copy.arrow.set_opacity(0)
        arrow_v_copy.arrow.set_opacity(0)
        display_arrow_u = display_arrow(arrow_u_copy)
        display_arrow_v = display_arrow(arrow_v_copy)
        self.add(display_arrow_u, display_arrow_v)

        u_angle = cmath.phase(self.u)
        u_modulus = abs(self.u)

        scene.play( AnimationGroup(
            arrow_u_copy.animate
                .shift(self.arrow_uv.dot.get_center() - self.arrow_u.dot.get_center()),
            arrow_v_copy.animate
                .shift(self.arrow_uv.dot.get_center() - self.arrow_v.dot.get_center()),
            lag_ratio=0.5
        ) )
        about_point = arrow_v_copy.dot.get_center()
        scene.play(
            Rotate(arrow_v_copy, u_angle, OUT, about_point)
        )
        arrow_and_re_line = VGroup(arrow_v_copy.arrow, arrow_v_copy.line_re)
        scene.play(
            arrow_and_re_line.animate.scale(u_modulus, about_point=about_point)
        )
        scene.play(FadeOut(arrow_v_copy.line_re))