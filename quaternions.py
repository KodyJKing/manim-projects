from manim import *
import numpy as np

ihat = "\hat{\imath}"
jhat = "\hat{\jmath}"
khat = "\hat{k}"
ihatn = "-" + ihat
jhatn = "-" + jhat
khatn = "-" + khat

color_map = { 
    ihat: RED, jhat: GREEN, khat: BLUE,
    "i": RED, "j": GREEN, "k": BLUE, "b": WHITE
}

def vec_ijk_cross_table(tex_to_color_map=None):
    ih, jh, kh = ihat, jhat, khat
    im, jm, km = ihatn, jhatn, khatn
    crossproduct_table = [
        ["", ih, jh, kh],
        [ih,  0, kh, jm],
        [jh, km,  0, ih],
        [kh, jh, im,  0]
    ]
    return MathTable(
        crossproduct_table,
        include_outer_lines=True,
        element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map)
    )

def quat_ijk_times_table(tex_to_color_map=None):
    quaternion_table_ijk = [
        ["",  "i",  "j",  "k"],
        ["i", "-1",  "k", "-j"],
        ["j", "-k", "-1",  "i"],
        ["k",  "j", "-i", "-1"]
    ]
    return MathTable(
        quaternion_table_ijk,
        include_outer_lines=True,
        element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map)
    )

def quat_fill_times_table(tex_to_color_map=None):
    quaternion_table = [
        ["", "1",  "i",  "j",  "k"],
        ["1", "1",  "i",  "j",  "k"],
        ["i", "i", "-1",  "k", "-j"],
        ["j", "j", "-k", "-1",  "i"],
        ["k", "k",  "j", "-i", "-1"]
    ]
    return MathTable(
        quaternion_table,
        include_outer_lines=True,
        element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map)
    )

class QuatDefinition(Scene):
    def construct(self):
        tex_quat_form = MathTex("a + bi + cj + dk", tex_to_color_map=color_map)
        tex_ijk_definition = MathTex("i^2 = j^2 = k^2 = ijk = -1", tex_to_color_map=color_map)

        equations = VGroup()
        equations += tex_quat_form
        equations += tex_ijk_definition

        prev_line = None
        for line in equations:
            if prev_line:
                line.next_to(prev_line, DOWN)
            prev_line = line
        equations.move_to(ORIGIN)

        self.play( Write( tex_quat_form ) )
        self.play( 
            Circumscribe( VGroup(
                tex_quat_form.get_part_by_tex("b"),
                tex_quat_form.get_part_by_tex("k"),
            ), run_time=3 ),
            run_time=3
        )
        self.play( Write( tex_ijk_definition ) )

        ijk_table = quat_ijk_times_table(color_map).scale(0.75).move_to(RIGHT * 3)
        vec_ijk_table = vec_ijk_cross_table(color_map).scale(0.72).move_to(LEFT * 3)

        rect = SurroundingRectangle(tex_ijk_definition)
        tex_ijk_definition.add(rect)
        self.play(Create(rect))

        self.play( equations.animate.move_to(LEFT * 3) )
        self.play( Create(ijk_table) )
        self.wait(3)
        self.play( FadeOut(equations) )
        self.play( FadeIn(vec_ijk_table) )
        self.wait()