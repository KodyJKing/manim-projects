from typing import List
from webbrowser import get
from manim import *
from manim.mobject.opengl.opengl_three_dimensions import OpenGLSurface
from manim.utils.space_ops import ( quaternion_mult )
from sympy import rad
from complex import AlgebraicProps
from lib.TexContainer import TexContainer
from lib.angle3D import angle3D
from lib.mathutils import polar2xy, relative_quaternion, relative_quaternion2, smoothstep
import numpy as np

from lib.utils import animate_arc_to, animate_replace_tex, colored_math_tex, colored_tex, compose_colored_tex, play_rewrite_sequence, style_exposition, swap_anim, tex_matches
from lib.LabeledArrow import LabeledArrow

SurfaceClass = OpenGLSurface if config.renderer == "opengl" else Surface

vi = RIGHT
vj = UP
vk = OUT

ihat = "\hat{\imath}"
jhat = "\hat{\jmath}"
khat = "\hat{k}"
ihatn = "-" + ihat
jhatn = "-" + jhat
khatn = "-" + khat

MYPINK = "#ff6181"

color_map = { 
    "\\overline{q}": MYPINK,
    ihat: RED, jhat: GREEN, khat: BLUE,
    "{i'}": RED, "{j'}": GREEN, "{k'}": BLUE,
    "i'": RED, "j'": GREEN, "k'": BLUE,
    "$i$": RED, "$j$": GREEN, "$k$": BLUE,
    "i": RED, "j": GREEN, "k": BLUE,
    "b": WHITE,
    "q": MYPINK, r"\theta": MYPINK,
    "\\times": WHITE,
}

def math_tex(*args, **kwargs):
    return MathTex(*args, tex_to_color_map=color_map, **kwargs)

def replace_tex(tex, text, **kwargs):
    return animate_replace_tex(tex, text, tex_to_color_map=color_map, **kwargs)

def vec_cross_table(tex_to_color_map=None):
    ih, jh, kh = ihat, jhat, khat
    im, jm, km = ihatn, jhatn, khatn
    op = r"u \times v"
    crossproduct_table = [
        [op, ih, jh, kh],
        [ih,  0, kh, jm],
        [jh, km,  0, ih],
        [kh, jh, im,  0]
    ]
    return MathTable(
        crossproduct_table,
        include_outer_lines=True,
        element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map)
    )

def vec_dot_table(tex_to_color_map=None):
    ih, jh, kh = ihat, jhat, khat
    op = r"u \cdot v"
    dot_product_table = [
        [op, ih, jh, kh],
        [ih,  1,  0,  0],
        [jh,  0,  1,  0],
        [kh,  0,  0,  1]
    ]
    return MathTable(
        dot_product_table,
        include_outer_lines=True,
        element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map)
    )

def pure_quat_times_table(tex_to_color_map=None):
    op = "uv"
    quaternion_table_ijk = [
        [op,  "i",  "j",  "k"],
        ["i", "-1",  "k", "-j"],
        ["j", "-k", "-1",  "i"],
        ["k",  "j", "-i", "-1"]
    ]
    return MathTable(
        quaternion_table_ijk,
        include_outer_lines=True,
        element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map)
    )

def quat_times_table(tex_to_color_map=None):
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
        element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map),
    )

def coordinate_frame(suffix="", label_dist=0.5):
    arrow_i = Arrow3D(ORIGIN, vi, color=RED)
    arrow_j = Arrow3D(ORIGIN, vj, color=GREEN)
    arrow_k = Arrow3D(ORIGIN, vk, color=BLUE)
    tex_j = math_tex("j").set_stroke(BLACK, 5, 1, True)
    tex_i = math_tex("i").set_stroke(BLACK, 5, 1, True)
    tex_k = math_tex("k").set_stroke(BLACK, 5, 1, True)

    def add_updater(arrow: Arrow, tex: MathTex):
        # We need to use a helper line because 3D arrows do not transform their points after creation. (WTF?)
        line = Line(arrow.get_start(), arrow.get_end()).set_opacity(0)
        arrow.add(line)
        def updater(tex: MathTex):
            tex.unfix_orientation()
            u = line.get_unit_vector()
            tex.move_to(line.get_end() + u * label_dist)
            tex.fix_orientation()
        tex.add_updater(updater)
        updater(tex)
    
    add_updater(arrow_i, tex_i)
    add_updater(arrow_j, tex_j)
    add_updater(arrow_k, tex_k)

    return arrow_i, arrow_j, arrow_k, tex_i, tex_j, tex_k

def standard_axes():
    return ThreeDAxes(x_range=[-5, 5], y_range=[-5, 5], z_range=[-5, 5], x_length=10, y_length=10, z_length=10)
def jkplane():
    return NumberPlane(x_range=[-10, 10], y_range=[-10, 10]).rotate(PI/2, vj)

def play_commute_proof(scene: Scene, unit_string: str, unit_color: str, position:np.array=ORIGIN):
    color_map2 = {unit_string:unit_color, "a_2":GRAY, "b_2":GRAY, "v":GRAY}
    words2 = "a_1 b_1 a_2 b_2".split(" ")
    get_tex2 = lambda string: colored_math_tex(string, words=words2, t2c=color_map2)

    tc_commute = TexContainer(
        r"(a_1 + b_1 @)(a_2 + b_2 @)".replace("@", unit_string),
        get_tex2
    ).move_to(position)
    scene.play(Write(tc_commute))

    tc_commute_2 = TexContainer(
        r"a_1 a_2 + a_1 b_2 @ + b_1 @ a_2 + b_1 @ b_2 @".replace("@", unit_string), 
        get_tex2
    ).next_to(tc_commute, DOWN, 0.5)
    scene.play( TransformMatchingTex(tc_commute.tex.copy(), tc_commute_2.tex, path_arc=30*DEGREES) )
    scene.wait()

    tc_commute_3 = tc_commute_2.copy()
    scene.play(tc_commute_3.animate.next_to(tc_commute_2, DOWN, 0.5))

    scene.play( 
        tc_commute_3.transform(
            r"a_2 a_1 + b_2 @ a_1 + a_2 b_1 @ + b_2 @ b_1 @".replace("@", unit_string),
            path_arc=90*DEGREES
        )
    )
    scene.play(swap_anim( tc_commute_3.tex[3:6], tc_commute_3.tex[7:10] ))
    scene.wait()

    tc_commuted = TexContainer(
        r"(a_2 + b_2 @)(a_1 + b_1 @)".replace("@", unit_string),
        get_tex2
    ).next_to(tc_commute_3, DOWN, 0.5)
    scene.play( TransformMatchingTex(tc_commute_3.tex.copy(), tc_commuted.tex, path_arc=30*DEGREES) )
    scene.wait()

    equation = VGroup(tc_commute, Tex("="), tc_commuted)
    scene.play(
        FadeOut(tc_commute_2, tc_commute_3),
        equation.animate.arrange()
    )

    return equation

class QuatDefinition(Scene):
    def construct(self):
        _color_map = color_map | { "{i}": RED, "+":WHITE }
        tex_kw = { "t2c":_color_map }

        title = Tex(r"Chapter 3: Intro to Quaternions")
        self.play(FadeIn(title))
        self.wait()
        self.play(FadeOut(title))

        tex_form = colored_math_tex("a + b i", **tex_kw)
        self.play( Write( tex_form ) )
        self.wait()

        exposition1 = colored_tex(r"We can extend complex numbers by adding\\two more distinct imaginary elements, $j$ and $k$.", t2c=color_map)
        style_exposition(exposition1).to_edge(UP)
        self.play(Write(exposition1), run_time=3)
        self.wait()

        self.play( TransformMatchingTex(tex_form, tex_form := colored_math_tex("a + b i + c j + d k", **tex_kw).move_to(tex_form) ) )
        self.wait()

        self.play(FadeOut(exposition1))
        exposition2 = Tex(r"Because they have 4 components, you could\\think of quaternions as 4D vectors...")
        style_exposition(exposition2).to_edge(UP)
        self.play(Write(exposition2), run_time=2)

        group_4vec = VGroup(
            MathTex(r"\Leftrightarrow"),
            MathTex(r"\begin{bmatrix}a\\b\\c\\d\end{bmatrix}")
        ).arrange(RIGHT).next_to(tex_form, RIGHT)
        self.play(Write(group_4vec))
        self.wait()
        self.play(FadeOut(group_4vec, exposition2))

        exposition3 = Tex(
            r"However, for the purpose of understanding 3D rotations,\\",
            r"it will be more helpful to think of them as 3D vectors\\",
            r"with an extra component tacked on."
        )
        style_exposition(exposition3).to_edge(UP)
        self.play(Write(exposition3), run_time=3)

        def labeled_rect(contents: Mobject, label: str):
            rect = SurroundingRectangle(contents)
            texlabel = Tex(label, color=YELLOW).scale(0.5).next_to(rect, UP, buff=0.125)
            return VGroup(rect, texlabel)

        vector_part_rect = labeled_rect(tex_form[2:], "vector part")
        self.play(Write(vector_part_rect))
        self.wait()

        real_part_rect = labeled_rect(tex_form[0], "real part")
        real_part_rect[1].move_to(vector_part_rect[1], coor_mask=UP)
        self.play(Write(real_part_rect))
        self.wait()

        group_3vec = VGroup(
            MathTex(r"\Leftrightarrow"),
            tex_real_and_vec := MathTex(r"(a,\tiny\begin{bmatrix}b\\c\\d\end{bmatrix})")
        ).arrange(RIGHT).next_to(tex_form, RIGHT)
        self.play(Write(group_3vec))
        self.wait()
        self.play(Transform(tex_real_and_vec, MathTex(r"(a,\vec{v})").move_to(tex_real_and_vec, LEFT)))
        self.wait()
        self.play(FadeOut(group_3vec))

        self.play(FadeOut(exposition3))
        exposition4 = VGroup(
            line1 := colored_tex(
                r"The vector part of a quaternion tells us which axis we're rotating about,",
                t2c={"vector part":YELLOW}
            ),
            line2 := colored_tex(
                r"and real part tells us what angle we're rotating by.",
                t2c={"real part":YELLOW}
            )
        ).arrange(DOWN)
        style_exposition(exposition4).to_edge(UP)
        self.play(Write(line1))
        self.wait()

        self.play(Write(line2))
        self.wait()

        self.play(FadeOut(exposition4))
        exposition5 = VGroup(
            line1 := colored_tex(
                r"If a quaternion's real part is zero, it's called a vector quaternion.",
                t2c={"vector quaternion":YELLOW}
            ),
            line2 := colored_tex(
                "Vector quaternions are the things we will be rotating.",
                t2c={"Vector quaternions":YELLOW}
            ),
        ).arrange(DOWN)
        style_exposition(exposition5).to_edge(UP)
        self.play(Write(line1))

        tex_vec_quat = colored_math_tex("x i + y j + z k", **tex_kw)
        vec_quat_rect = labeled_rect(tex_vec_quat, "vector quaternion")
        vec_quat_group = VGroup(tex_vec_quat, vec_quat_rect).next_to(tex_form, DOWN, buff=0.5)
        self.play(Write(vec_quat_group))
        self.wait()

        self.play(Write(line2))
        self.wait()

        self.play(FadeOut(tex_form, vector_part_rect, real_part_rect, vec_quat_group, exposition5))

        exposition6 = Tex("But first we need to go over how to multiply quaternions...")
        style_exposition(exposition6)
        self.play(Write(exposition6))
        self.wait()

class QuatDefinition_AxisAngleVisual(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-1, 1], y_range=[-1, 1], z_range=[-1, 1],
            x_length=6, y_length=6, z_length=6,
            axis_config={"stroke_width":4},
            tips=False
        )
        direction = np.array([1, 1, 1])
        n = normalize(direction)
        arrow = Arrow(ORIGIN, direction * 3, buff=0, color=RED).rotate_about_origin(PI/2+PI/16, n)
        arrow_partial = Line(direction*(3/4+.1), direction*3, color=RED).rotate_about_origin(PI/2+PI/16, n)
        line = DashedLine(ORIGIN - direction * 5, direction * 5, color=RED)

        self.begin_ambient_camera_rotation()
        self.set_camera_orientation(phi=65*DEGREES, theta=0*DEGREES)

        self.add(axes)
        self.play(Create(arrow))
        self.play(FadeIn(line))

        self.wait(5)

        radius = 0.25
        arc = CurvedArrow(
            RIGHT*radius,
            DOWN*radius,
            arc_center=ORIGIN,
            angle=TAU*3/4,
            tip_length=0.2
        )
        quat = relative_quaternion(OUT, n)
        angle, axis = angle_axis_from_quaternion(quat)
        arc.move_to(ORIGIN).set_z_index(-1)
        arc.rotate_about_origin(angle, axis)
        arc.shift(direction*2)
        
        self.play(Create(arc))
        self.wait(3)

        self.stop_ambient_camera_rotation()

        obj = Dodecahedron(faces_config={"fill_opacity":0.75})
        self.play(FadeIn(obj), FadeIn(arrow_partial))
        self.play(Rotate(obj, TAU*3/4, n, ORIGIN), run_time=3)

        self.wait()

class QuatMultiplication(Scene):
    def construct(self):
        _color_map = color_map | { "{i}": RED, "+":WHITE }
        tex_kw = { "t2c":_color_map }

        exposition1 = Tex(
            r"We've been assuming that complex multiplication and addition", 
            " have the same algebraic properties as real multiplication and addition...",
        )
        style_exposition(exposition1)
        self.play(Write(exposition1))
        self.wait()

        self.play(FadeOut(exposition1))
        exposition2 = VGroup(
            line1 := Tex(
                r"Quaternions have all the same properties\\except their multiplication isn't commutative.",
                tex_to_color_map={"their multiplication isn't commutative":RED}
            ),
            line1b := VGroup(
                Tex(r"For example, "),
                colored_math_tex(r"i j = k \neq j i = -k", t2c=color_map)
            ).arrange(),
            line2 := Tex(
                r"But real numbers still commute with any quaternion."
            )
        ).arrange(DOWN, buff=0.35).shift(UP)
        exposition2.scale(2/3)
        self.play(Write(line1))
        self.wait()
        self.play(Write(line1b))
        self.wait()
        self.play(Write(line2))

        tc_commute = TexContainer(math_tex(*"3 (j+2k)".split(" ")))
        tc_commute.next_to(exposition2, DOWN, 0.5)
        self.play(Write(tc_commute))
        self.play(tc_commute.transform(math_tex(*"(j+2k) 3".split(" ")), path_arc=-120*DEGREES))
        self.wait()

        self.play(FadeOut(exposition2, tc_commute))
        exposition3 = Tex(
            r"You can show some other quaternions commute too,\\for instance complex quaternions still commute with each other...",
            tex_to_color_map={"complex quaternions":YELLOW}
        ).to_edge(UP)
        style_exposition(exposition3)
        self.play(Write(exposition3), run_time=3)
        self.wait()

        tmp_equation = play_commute_proof(self, "i", RED, UP*1.5)
        self.wait()
        self.play(FadeOut(tmp_equation, exposition3))

        tex_ident = colored_math_tex("i^2 = j^2 = k^2 = i j k = -1", **tex_kw)
        exposition4 = VGroup(
            line1 := Tex(r"This equation is used to define quaternion multiplication."),
            line2 := colored_tex("Like $i$, $j$ and $k$ also square to $-1$.", t2c=color_map),
            line3 := Tex(r"This last term defines the product of distinct imaginary units."),
        ).arrange(DOWN, buff=0.35)
        style_exposition(exposition4)#.to_edge(UP)
        exposition4.next_to(tex_ident, UP, 0.5)
        self.play(Write(line1))

        self.play( Write( tex_ident ) )
        self.wait()

        self.play(Write(line2))
        self.wait()

        self.play(Write(line3))
        self.play(Indicate(tex_ident[6:]))
        self.wait()
        self.play(FadeOut(exposition4))

        exposition5 = VGroup(
            line1 := Tex(r"If you play around with this equation, you can build this times table."),
            line2 := Tex(r"The algebra is a bit tedious, so we'll breeze through it,"),
            line3 := Tex(r"but you can pause and follow along if you're curious.")
        ).arrange(DOWN)
        style_exposition(exposition5).to_edge(UP)

        ijk_table = pure_quat_times_table(color_map).scale(2/3).move_to(RIGHT * 3)

        self.play(Write(line1))
        self.play( tex_ident.animate.move_to(LEFT * 3) )

        arrow = CurvedArrow(
            tex_ident.get_center() + UP * 0.5,
            ijk_table.get_corner(UL) + LEFT * 0.25 + DOWN * 0.5,
            angle=-60*DEGREES
        )

        self.play( Create(arrow), Create(ijk_table) )
        self.wait(3)

        self.play(Write(line2))
        self.play(Write(line3))
        self.wait()

class CrossDotProduct(Scene):
    def construct(self):
        scene_color_map = {
            "vector quaternions":YELLOW, "cross product":YELLOW, "dot product":YELLOW
        }

        ijk_table = pure_quat_times_table(color_map).scale(2/3)
        cross_table = vec_cross_table(color_map).scale(0.5)
        dot_table = vec_dot_table(color_map).scale(0.5)

        self.add(ijk_table)
    
        exposition1 = Tex(
            r"If you compare this times table to the\\times tables for the cross product and dot product...",
            tex_to_color_map=scene_color_map
        )
        style_exposition(exposition1)
        exposition1.next_to(ijk_table, UP, 1)
        self.play(Write(exposition1))

        alpha_tracker = ValueTracker(0)
        alpha_updater = lambda mobj: mobj.set_opacity(alpha_tracker.get_value())

        cross_table.add_updater(alpha_updater)
        dot_table.add_updater(alpha_updater)
        tables = VGroup(cross_table, dot_table, ijk_table)
        self.play(tables.animate.arrange(buff=0.35), alpha_tracker.animate.set_value(1))
        cross_table.clear_updaters()
        dot_table.clear_updaters()

        exposition2 = Tex(
            r"You can see that the product of two vector quaternions\\is their cross product minus their dot product.",
            tex_to_color_map=scene_color_map
        )
        style_exposition(exposition2)
        exposition2.next_to(tables, UP, 1)
        self.play(FadeOut(exposition1))
        self.play(Write(exposition2))
        self.wait()

        equation_quat_cross_dot = MathTex(r" uv = u \times v - u \cdot v ", tex_to_color_map=color_map)
        equation_quat_cross_dot.move_to(ijk_table)
        equation_quat_cross_dot.add_updater(alpha_updater)

        tmp_group = VGroup(exposition2, equation_quat_cross_dot)
        self.play(
            tmp_group.animate.arrange(buff=0.5).next_to(tables, UP, 1),
            alpha_tracker.set_value(0).animate.set_value(1)
        )
        
        # equation_quat_cross_dot.next_to(ijk_table, UP)
        # self.play( Write(equation_quat_cross_dot) )
        # self.wait()

        # self.play(FadeOut(ijk_table, vec_tables))
        # self.play(equation_quat_cross_dot.animate.move_to(ORIGIN))

class QuatProps(AlgebraicProps):
    def is_quaternion_scene(self):
        return True

class TableDerivation(Scene):
    def construct(self):
        _color_map = color_map | { 
            "{i}":RED, "{j}":GREEN, "{k}":BLUE,
            "ii":RED, "jj":GREEN, "kk":BLUE,
            "{(-1)}":WHITE, "(-1)":WHITE,
            "-1":WHITE, "1":WHITE,
            "+":WHITE, "-":WHITE, "=":WHITE
        }
        tex_kw = { "t2c":_color_map }

        tex_ident = colored_math_tex("i^2 = j^2 = k^2 = i j k = -1", **tex_kw)
        table = pure_quat_times_table(color_map).scale(0.5).to_corner(UR)
        # VGroup(tex_ident, table).arrange(buff=1)

        def get_table_entry(i, j):
            return table.get_entries((i + 2, j + 2))

        for i in range(3):
            for j in range(3):
                get_table_entry(i, j).set_opacity(0)

        # self.play(Write(tex_ident))
        # self.add(tex_ident)
        # self.play(FadeIn(table))
        self.add(tex_ident, table)
        self.wait()

        # Add squares of i,j,k to table.
        for i in range(3):
            self.remove(get_table_entry(i, i))
        self.play(LaggedStart(*[
            TransformMatchingTex( tex_ident.copy(), get_table_entry(i, i).set_opacity(1), shift=ORIGIN )
            for i in range(3)
        ]), run_time=1)

        def animate_permutation():
            def permute_animations(tc: TexContainer, left=True):
                key_map = {"ii":"(-1)", "jj":"(-1)", "kk":"(-1)"}

                transform = lambda next, **kwargs: tc.transform(next, key_map=key_map, **kwargs)
                replace = lambda next: tc.replace(next)

                yield Write(tc)

                if left:
                    yield transform( "{i} i j k {i} = {i}( - 1 ){i}", shift=DOWN )
                    yield transform( "{i} i j k {i} = -{i}{i}", shift=DOWN )
                    yield replace( "ii j k i = -{i}{i}" )
                    yield transform( "(-1) j k i = 1" )
                    yield replace( "( - 1 ) j k i = 1" )
                    yield transform( "j k i = - 1", shift=DOWN )
                else:
                    yield transform( "{k} i j k {k} = {k}( - 1 ){k}", shift=DOWN )
                    yield transform( "{k} i j k {k} = -{k}{k}", shift=DOWN )
                    yield replace( "k i j kk = -{k}{k}" )
                    yield transform( "k i j (-1) = 1" )
                    yield replace( "k i j ( - 1 ) = 1" )
                    yield transform( "k i j = - 1", shift=DOWN )
                
            get_tex = lambda string: colored_math_tex( string, **tex_kw )
            left_eq = TexContainer( colored_math_tex("i j k = - 1", **tex_kw), get_tex)
            right_eq = TexContainer( colored_math_tex("i j k = - 1", **tex_kw), get_tex)
            VGroup(left_eq, right_eq).arrange(DOWN).next_to(tex_ident, DOWN, buff=0.5)
            left_animations = permute_animations(left_eq, True)
            right_animations = permute_animations(right_eq, False)

            for l, r in zip(left_animations, right_animations):
                self.play(l, r)

            return left_eq, right_eq

        left_eq, right_eq = animate_permutation()
        self.wait()

        _tex_ident = colored_math_tex(r"& i^2 = j^2 = k^2 = -1 \\ & i j k = j k i = k i j = -1", **tex_kw).to_corner(UL)
        self.play(TransformMatchingTex(VGroup(tex_ident, left_eq.tex, right_eq.tex), _tex_ident))
        tex_ident = _tex_ident

        def animate_products():
            def relabel(expression: str, t: str, u: str, v: str):
                return expression.replace("t", t).replace("u", u).replace("v", v)

            def product_anims(tex: MathTex, t: str, u: str, v: str, table_i: int, table_j: int):
                get_tex = lambda string, **kwargs: colored_math_tex( relabel(string, t, u ,v), **tex_kw, **kwargs )
                squares_to_minus_one = {"ii":"(-1)", "jj":"(-1)", "kk":"(-1)"}
                squares_to_minus = {"ii":"{-}", "jj":"{-}", "kk":"{-}"}
                
                tc = TexContainer(tex, get_tex)
                yield Write(tc)

                replace = lambda next: tc.replace(next)
                transform = lambda next, key_map=squares_to_minus_one, words=[], **kwargs: tc.transform(
                    get_tex(next, words=words), key_map=key_map, **kwargs)

                yield transform( "{t} t u v = -{t}", shift=DOWN )
                yield replace( "tt u v = - t" )
                yield transform( "{-} u v = - t", words=["{-}"], key_map= squares_to_minus )
                yield transform( "u v = t" )

                entry = get_table_entry(table_i, table_j)
                entry.set_opacity(1)
                self.remove(entry)
                yield TransformMatchingTex(tc.tex.copy(), entry, shift=ORIGIN), {"lagged_start":True}

                yield Wait()

                next_tc = TexContainer( "t u v = - 1", get_tex ).set_opacity(0)
                center = tc.get_center()
                yield VGroup(tc, next_tc).animate().arrange(buff=1.5).move_to(center)
                old_tc = tc
                tc = next_tc
                yield FadeIn(tc.set_opacity(1))
                
                yield transform( "t u v {v}{u} = - {v}{u}", shift=DOWN )
                yield replace( "t u vv u = - v u" )
                yield transform( "t u (-1) u = - v u" )
                yield transform( "t u u (-1) = - v u", path_arc=90*DEGREES )
                yield replace( "t uu (-1) = - v u" )
                yield transform( "t {(-1)} (-1) = - v u" )
                yield transform( "t = - v u" )
                yield transform( "v u = - t", path_arc=90*DEGREES )

                entry = get_table_entry(table_j, table_i)
                entry.set_opacity(1)
                self.remove(entry)
                yield TransformMatchingTex(tc.tex.copy(), entry, shift=ORIGIN), {"lagged_start":True}

                yield Wait()

                yield FadeOut(old_tc, tc)
            
            eq1 = colored_math_tex("i j k = - 1", **tex_kw)
            eq2 = colored_math_tex("j k i = - 1", **tex_kw)
            eq3 = colored_math_tex("k i j = - 1", **tex_kw)

            VGroup(eq1, eq2, eq3).arrange(DOWN)

            anims1 = product_anims(eq1, "i", "j", "k", 1, 2)
            anims2 = product_anims(eq2, "j", "k", "i", 2, 0)
            anims3 = product_anims(eq3, "k", "i", "j", 0, 1)
            for a, b, c in zip(anims1, anims2, anims3):
                options = {}
                if isinstance(a, tuple):
                    a, options = a
                    b, _ = b
                    c, _ = c
                if options.get("lagged_start", False):
                    self.play(LaggedStart(a, b, c))
                else:
                    self.play(a, b, c)

        animate_products()

        self.play( FadeOut(tex_ident), table.animate.move_to(ORIGIN).scale(2/3 / 0.5) )

class ThreeD(ThreeDScene):
    def construct(self):
        def prep_exposition(exposition: Mobject):
            style_exposition(exposition)
            self.add_fixed_in_frame_mobjects(exposition)
            return exposition

        # template = TexTemplate()
        # template.add_to_preamble(r"\usepackage{times}")
        # texkw = {"tex_template":template}

        scene_color_map = color_map | {}
        texkw = {"t2c":scene_color_map}
        
        if config.renderer == "opengl":
            self.set_camera_orientation(phi=65*DEGREES, theta=110*DEGREES)
        else:
            self.set_camera_orientation(phi=65*DEGREES, theta=20*DEGREES)

        chapter = Tex("Chapter 4: Quaternion Rotation")
        self.add_fixed_in_frame_mobjects(chapter)
        self.play(FadeIn(chapter))
        self.wait()
        self.play(FadeOut(chapter))

        axes = standard_axes()
        numplane = jkplane().set_opacity(0)
        self.add(numplane)
        self.play(Create(axes))

        arrow_i, arrow_j, arrow_k, tex_i, tex_j, tex_k = coordinate_frame()
        self.add_fixed_orientation_mobjects( tex_i, tex_j, tex_k )

        self.play( 
            FadeIn( arrow_i, arrow_j, arrow_k),
            Write(tex_i), Write(tex_j), Write(tex_k) )
        
        exposition1 = VGroup(
            line1 := colored_tex("To start off our search for a rotation formula,", **texkw),
            line2 := colored_tex("let's look at the action of $i$ on numbers in", **texkw),
            line3 := colored_tex("the $j$$k$-plane.", **texkw),
        ).arrange(DOWN)
        prep_exposition(exposition1).to_edge(UP)
        self.play(Write(exposition1), run_time=4)

        def indicate_arrow(arrow, tex):
            return AnimationGroup( Indicate(arrow, scale_factor=1), Indicate(tex) )

        # self.play( indicate_arrow(arrow_i, tex_i) )
        # self.wait()
        self.play( 
            indicate_arrow(arrow_j, tex_j),
            indicate_arrow(arrow_k, tex_k),
            numplane.animate.set_opacity(0.25)
        )
        self.wait()

        self.play(FadeOut(exposition1))
        exposition2 = colored_tex(
            r"Remember, quaternion multiplication isn't commutative,\\"
            "so the side we multiply on matters."
        )
        prep_exposition(exposition2).to_edge(UP)
        self.play(Write(exposition2), run_time=2)

        table = pure_quat_times_table(color_map).scale(0.5).to_edge(LEFT)
        table_background = SurroundingRectangle( table, color=BLACK, fill_color=BLACK, fill_opacity=1, buff=0 )
        self.add_fixed_in_frame_mobjects(table_background)
        self.add_fixed_in_frame_mobjects(table)
        self.play( FadeIn(table_background), FadeIn(table) )

        def show_sided_i_multiplication(side="left"):
            sign = 1 if side == "left" else -1
            angle = PI/2 * sign

            def swap( coord ):
                if side == "left":
                    return coord
                elif type(coord) is tuple:
                    a, b = coord
                    return (b, a)
                elif type(coord) is np.ndarray:
                    a, b, c = coord
                    return np.array([b, a, c])

            i_rect = SurroundingRectangle( VGroup(
                table.get_cell( swap((2, 1)) ), table.get_cell( swap((2, 4)))  ), buff=SMALL_BUFF )
            self.add_fixed_in_frame_mobjects(i_rect)
            self.play( Create(i_rect) )

            # Indicate table entries and rotate one at a time.
            SIDE = swap(RIGHT)
            arcs = VGroup( *[ CurvedArrow(
                    table.get_entries( swap((1, index)) ).get_edge_center(SIDE) + SIDE * .1,
                    table.get_entries( swap((2, index)) ).get_edge_center(SIDE) + SIDE * .1,
                    radius=-.5, tip_length=.12, color=RED)
                for index in [ 3, 4 ] ] )
            arrows_jk = [ arrow_j, arrow_k ]

            radius = 1.05
            curve_ref = CurvedArrow(
                polar2xy( (90 - 10) * DEGREES, radius ),
                polar2xy( 10 * DEGREES,        radius ),
                radius=-radius,
                tip_length=0.2,
                stroke_width=6,
                color=RED
            )
            curves = VGroup(
                curve_ref.copy().rotate(-PI/2, vj, ORIGIN),
                curve_ref.copy().rotate(-PI/2, vj, ORIGIN).rotate( PI/2, vi, ORIGIN),
                curve_ref.copy().rotate(-PI/2, vj, ORIGIN).rotate( PI, vi, ORIGIN),
                curve_ref.copy().rotate(-PI/2, vj, ORIGIN).rotate( PI * 3/2, vi, ORIGIN),
            )
            if side == "right":
                curves.rotate(PI, vj, ORIGIN)
            
            def rotate_basis(i):
                arc = arcs[i]
                arrow = arrows_jk[i].copy()
                self.wait()
                self.add_fixed_in_frame_mobjects(arc)
                self.play( Create(arc) )
                self.wait()
                self.play( 
                    Rotate( arrow, angle, vi, ORIGIN ),
                    Create( curves[i*sign] )
                    # indicate_arrow(arrow_i, tex_i) 
                )
                self.play( FadeOut( arrow, run_time=.25 ) )
            
            if side == "left":
                self.play(FadeOut(exposition2))
                exposition3 = prep_exposition( VGroup(
                    line1 := colored_tex("Left multiplying by $i$ sends $j$ to $k$,", **texkw),
                    line2 := colored_tex("$k$ to $-$$j$,", **texkw),
                    line3 := colored_tex("and so on...", **texkw),
                ).arrange(DOWN) ).to_edge(UP).set_opacity(0)
                self.play(Write(line1.set_opacity(1)))

            rotate_basis(0)

            if side == "left":
                self.play(Write(line2.set_opacity(1)))

            rotate_basis(1)

            if side == "left":
                self.play(Write(line3.set_opacity(1)))

            for i in range(2, 4):
                self.play(Create(curves[i*sign]))

            if side == "left":
                self.play(FadeOut(exposition3))
                exposition4 = prep_exposition( 
                    colored_tex(
                        r"Just like with complex numbers, this implies\\",
                        r"multiplying by $i$ rotates any vector in this\\",
                        r"plane 90 degrees left.",
                        **texkw
                    )
                ).to_edge(UP)
                self.play(Write(exposition4))
            
            # Rotate all together
            arrows_jk_2 = [arrow_j.copy(), arrow_k.copy() ]
            self.add(*arrows_jk_2)
            self.play( 
                *[ Rotate( arrow, angle, vi, ORIGIN ) for arrow in arrows_jk_2 ],
                Rotate(numplane, angle, vi),
                # indicate_arrow(arrow_i, tex_i), 
                run_time=2
            )
            self.play( FadeOut(*arrows_jk_2) )

            if side == "left":
                self.play(FadeOut(exposition4))

            self.play( FadeOut( *arcs, i_rect, curves ) )
        
        tex_mult_side = VGroup(Tex("Left multiplication:"), math_tex("iv")).arrange()
        prep_exposition(tex_mult_side).next_to(table, UP)
        tex_mult_side[1].shift(UP * 0.05) # Align to baseline. Might be worth creating a generic utility function for this.
        self.play(Write(tex_mult_side))
        show_sided_i_multiplication("left")
        self.play(FadeOut(tex_mult_side))

        exposition5 = prep_exposition(
            colored_tex(
                r"Right multiplication by $i$ is similar,\\",
                r"but the direction of rotation is reversed.",
                **texkw
            )
        ).to_edge(UP)
        self.play(Write(exposition5))

        tex_mult_side = VGroup(Tex("Right multiplication:"), math_tex("vi")).arrange()
        prep_exposition(tex_mult_side).next_to(table, UP)
        tex_mult_side[1].shift(UP * 0.05) # Align to baseline
        self.play(Write(tex_mult_side))
        show_sided_i_multiplication("right")
        self.play(FadeOut(tex_mult_side))

        self.play(FadeOut(exposition5))
        self.wait()

class ThreeDPart2(ThreeDScene):
    def construct(self):
        def prep_exposition(exposition: Mobject):
            style_exposition(exposition)
            self.add_fixed_in_frame_mobjects(exposition)
            return exposition

        self.set_camera_orientation(phi=65*DEGREES, theta=110*DEGREES)

        numplane = jkplane().set_opacity(.25)
        self.add(numplane)
        axes = standard_axes()
        self.add(axes)

        arrow_i, arrow_j, arrow_k, tex_i, tex_j, tex_k = coordinate_frame()
        self.add(arrow_i, arrow_j, arrow_k)
        self.add_fixed_orientation_mobjects( tex_i, tex_j, tex_k )

        table = pure_quat_times_table(color_map).scale(0.5).to_edge(LEFT)
        table_background = SurroundingRectangle( table, color=BLACK, fill_color=BLACK, fill_opacity=1, buff=0 )
        self.add_fixed_in_frame_mobjects(table_background)
        self.add_fixed_in_frame_mobjects(table) 

        self.play(FadeOut(table_background, table))

        exposition1 = prep_exposition( VGroup(
            Tex(
                r"The argument we used to go from 90 degree rotations to\\",
                r"arbitrary rotations for complex numbers works here too."
            )
        ) )
        self.play(Write(exposition1))

        return

        tex_rotor = MathTex(*"q =cos(\\theta)+ i sin(\\theta)".split(" "))
        tex_rotor[0].set_color(MYPINK)
        tex_rotor[2].set_color(RED)
        tex_rotor.to_corner(UR)
        self.add_fixed_in_frame_mobjects(tex_rotor)
        self.play(Write(tex_rotor))
        self.wait()

        def animate_rotation(theta_label, angle):
            theta_tracker = ValueTracker(0)
            def get_angle():
                theta = theta_tracker.get_value()
                sign = np.sign(theta)
                if abs(theta) < 0.001:
                    return VGroup()
                angle = Angle(
                    Line(ORIGIN, UP),
                    Line(ORIGIN, UP).rotate(theta, about_point=ORIGIN),
                    other_angle=sign<0
                ).rotate(PI/2, vj, ORIGIN)
                midpoint = angle.get_midpoint()
                opacity = smoothstep(0, 20*DEGREES, abs(theta))
                label = MathTex(theta_label).next_to(midpoint + OUT * 0.1 * sign, normalize(midpoint), buff=0.1)
                label.set_opacity(opacity).scale(0.75)
                label.fix_orientation()
                return VGroup(angle, label)
            mobj_angle = always_redraw(get_angle)
            self.add(mobj_angle)

            arrow_j_copy = arrow_j.copy()
            arrow_k_copy = arrow_k.copy()
            rotation_group = Group(arrow_j_copy, arrow_k_copy)
            
            self.play(
                Rotate(rotation_group, angle, vi, ORIGIN),
                Rotate(numplane, angle, vi, ORIGIN),
                theta_tracker.animate.increment_value(angle)
            )
            self.wait()
            self.play( FadeOut(mobj_angle, arrow_j_copy, arrow_k_copy) )
            self.play( numplane.animate.set_opacity(0), run_time=0.5 )
            numplane.rotate(-angle, vi, ORIGIN)
            self.play( numplane.animate.set_opacity(0.25),  run_time=0.5 )

        # Show sided multiplication by q
        tex_left_label = Tex("Counter-clockwise: ")
        tex_left_multiply = math_tex("qv").next_to(tex_left_label, RIGHT).shift(DOWN * 0.1)
        left_group = VGroup(tex_left_label, tex_left_multiply)
        left_group.to_corner(UL)
        self.add_fixed_in_frame_mobjects(left_group)
        self.play(Write(left_group))
        
        animate_rotation("\\theta", 60*DEGREES)
        self.wait()

        tex_right_label = Tex("Clockwise: ")
        tex_right_multiply = math_tex("vq").next_to(tex_right_label, RIGHT).shift(DOWN * 0.1)
        right_group = VGroup(tex_right_label, tex_right_multiply)
        right_group.next_to(left_group, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(right_group)
        self.play(Write(right_group))

        animate_rotation("-\\theta", -60*DEGREES)
        self.wait()

        self.play(FadeOut(left_group, right_group, tex_rotor))

        # Show issue with rotation outside of jk-plane
        arrow_v = Arrow3D(ORIGIN, vj + vk)
        self.play(FadeIn(arrow_v))
        self.play(Indicate(numplane, 1.1))

        self.move_camera(phi=75*DEGREES, theta=145*DEGREES)

        arrow_v_i = Arrow3D(ORIGIN, vi, color=RED).shift(vj + vk)
        self.play(
            # FadeIn(arrow_v_i),
            GrowFromPoint(arrow_v_i, vj + vk),
            arrow_v.animate.become(Arrow3D(ORIGIN, vj + vk + vi))
        )
        self.wait()

        self.play(
            LaggedStart(
                AnimationGroup(Indicate(arrow_i, 1), Indicate(tex_i)),
                Rotate(
                    Group(arrow_v, arrow_v_i),
                    TAU, vi, ORIGIN
                )
            ),
            run_time=2
        )
        self.wait()
        
        # Write out i(xi + yj + zk) and simplify.
        self.play(FadeIn(table_background, table))
        steps = [
            (math_tex(*"i ( x i + y j + z k )".split(" ")), False),
            (math_tex(*" x i i + y i j + z i k".split(" ")), True),
            (math_tex(*" x ( - 1 ) + y k + z ( - j )".split(" ")), False),
            (math_tex(*"- x + y k - z j".split(" ")), True),
        ]
        steps[0][0].to_corner(UL)
        for step in steps:
            step[0].fix_in_frame()
        play_rewrite_sequence(self, *steps)

        # Highlight real part of product.
        rect = SurroundingRectangle(steps[-1][0][:2], color=RED)
        self.add_fixed_in_frame_mobjects(rect)
        self.play(Create(rect))
        self.wait()

class DualPlanes(Scene):
    def construct(self):

        def make_plane(x_color, y_color, x_label, y_label ):
            plane_group = VDict()

            plane_range = [-3, +3]
            axes = Axes(x_range=plane_range, y_range=plane_range,
                x_length=None, y_length=None, tips=False)
            x_axis, y_axis = axes.get_axes()
            x_axis.set_fill(x_color).set_stroke(x_color)
            y_axis.set_fill(y_color).set_stroke(y_color)
            plane_group["axes"] = axes

            labels = VGroup()
            plane_group["labels"] = labels
            for label, color, axis in [ ( x_label, x_color, RIGHT ), ( y_label, y_color, UP ) ]:
                offset = np.cross(axis, OUT)
                labels.add( MathTex( label, color=color )
                    .scale(1/2)
                    .next_to( axes.c2p(*axis), offset ) )

            circle = Circle(
                plane_range[1]+.1, color=WHITE,
                fill_color=BLACK, fill_opacity=1,
                z_index=-1
            )
            plane_group["circle"] = circle

            return plane_group

        plane_1i = make_plane(WHITE, RED, "1", "i")
        plane_jk = make_plane(BLUE, GREEN, "j", "k")
        plane_1i["title"] = Tex("$1i$-Plane \n (Complex Plane)").next_to(plane_1i, DOWN, aligned_edge=LEFT)
        plane_jk["title"] = Tex("$jk$-Plane").next_to(plane_jk, DOWN, aligned_edge=RIGHT)

        plane_scale = 2/3
        plane_group = VGroup(plane_1i, plane_jk)
        plane_group.scale(plane_scale).arrange(buff=1).shift(UP)

        for plane in plane_group:
            self.play( Create(plane) )

        self.wait()

        tex_v = math_tex(*"v = a + bi + cj + dk".split(" ")).next_to(plane_group, DOWN)
        tex_q = colored_math_tex(r"q = cos(\theta) + i sin(\theta)", t2c=color_map).next_to(tex_v, DOWN)
        self.play( Write( tex_v ) )

        self.wait()
        
        # Complex and jk components of v.
        c45 = np.cos(45 * DEGREES)
        arrow_ab, arrow_cd = [
            LabeledArrow(
                Arrow( plane["axes"].c2p(0,0), plane["axes"].c2p(*coord), buff=0),
                math_tex("v").scale(plane_scale),
            ) for plane, coord in [ 
                # (plane_1i, (3/5,-4/5)), (plane_jk, (3/5, 4/5))
                # (plane_1i, (c45, c45)), (plane_jk, (c45, c45))
                (plane_1i, (0, 1)), (plane_jk, (c45, c45))
            ]
        ]

        self.play(
            VGroup(
                plane_1i["axes"], plane_1i["labels"],
                plane_jk["axes"], plane_jk["labels"],
            ).animate.set_opacity(0.25)
        )

        self.play( LaggedStart( 
            arrow_ab.grow_animation(),
            Circumscribe( tex_matches(tex_v, "a", "i" ) ),
            lag_ratio=.25 ), run_time=1.5 )
        self.play( LaggedStart(  
            arrow_cd.grow_animation(),
            Circumscribe( tex_matches(tex_v, "c", "k" ) ),
            lag_ratio=.25 ), run_time=1.5 )

        self.play( Write(tex_q) )

        theta = PI/4
        origin_ab = arrow_ab.arrow.get_start()
        origin_cd = arrow_cd.arrow.get_start()
        arrow_iab = arrow_ab.copy()
        arrow_abi = arrow_ab.copy()
        arrow_icd = arrow_cd.copy()
        arrow_cdi = arrow_cd.copy()
        self.add(arrow_iab, arrow_abi, arrow_icd, arrow_cdi)

        def add_angle(from_arrow, to_arrow, other_angle: bool):
            def get_angle():
                try:
                    return Angle(from_arrow.arrow, to_arrow.arrow, 
                        color=MYPINK, radius=0.25, other_angle=other_angle)
                except:
                    return VGroup()
            angle = always_redraw(get_angle)
            to_arrow.add(angle)

        add_angle(arrow_ab, arrow_iab, False)
        add_angle(arrow_ab, arrow_abi, False)
        add_angle(arrow_cd, arrow_icd, False)
        add_angle(arrow_cd, arrow_cdi, True)

        # Multiply complex-componet on either side.
        self.play( Rotate(arrow_iab.arrow, theta, about_point=origin_ab),
            replace_tex(arrow_iab.label, math_tex("qv").scale(plane_scale) ) )
        self.play( Rotate(arrow_abi.arrow, theta, about_point=origin_ab),
            replace_tex(arrow_abi.label, math_tex("vq").scale(plane_scale) ),
            FadeOut( arrow_iab ) )
        self.play(replace_tex(arrow_abi.label, math_tex("qv, vq").scale(plane_scale) ))
        self.wait()

        # Multiply jk-component on either side.
        self.play( Rotate(arrow_icd.arrow, theta, about_point=origin_cd),
            replace_tex(arrow_icd.label, math_tex("qv").scale(plane_scale) ) )
        self.play( Rotate(arrow_cdi.arrow, -theta, about_point=origin_cd),
            replace_tex(arrow_cdi.label, math_tex("vq").scale(plane_scale) ) )
        self.wait()

        # Vary theta.
        for d_theta in [PI/6, -PI/6]:
            self.play(
                *[
                    Rotate(arrow.arrow, d_theta, about_point=arrow.arrow.get_start())
                    for arrow in [arrow_abi, arrow_icd]
                ],
                Rotate(arrow_cdi.arrow, -d_theta, about_point=arrow_cdi.arrow.get_start())
            )
            self.wait(0.25)
        self.wait()

        self.play( FadeOut( arrow_icd, arrow_abi, arrow_cdi ) )

        self.wait()

        tex_sandwich_1 = math_tex("qvq").to_edge(UP)
        tex_sandwich_2 = math_tex("qv\\overline{q}").next_to(tex_sandwich_1, DOWN)
        self.play( Write( tex_sandwich_1 ) )
        self.wait()

        def animate_sandwich(
            labeled_arrow: LabeledArrow, plane: Axes,
            label2: str, angle: float, reverse_step_2: bool,
            net_angle_steps: List[str]
        ):
            arrow = labeled_arrow.arrow
            origin = arrow.get_start()
            step2sign = -1 if reverse_step_2 else 1
            angle2 = angle * step2sign
            radius = 0.25
            radius2 = 0.375 if reverse_step_2 else radius

            arrow_rot1 = arrow.copy().rotate(angle, about_point=origin)
            arrow_rot2 = arrow_rot1.copy().rotate(angle2, about_point=origin)
            mobj_angle1 = Angle(arrow, arrow_rot1, radius=radius, color=MYPINK)
            mobj_angle2 = Angle(arrow_rot1, arrow_rot2, radius=radius2, color=MYPINK, other_angle=reverse_step_2)

            arrow_qv = LabeledArrow( arrow.copy(), math_tex("v").scale(plane_scale) )
            self.play(
                Rotate(arrow_qv.arrow, angle, about_point=origin),
                replace_tex(arrow_qv.label, math_tex("qv").scale(plane_scale) ),
                Create(mobj_angle1)
            )

            get_tex = lambda string: colored_math_tex(string, t2c=color_map).scale(plane_scale)
            tc_net_angle = TexContainer(net_angle_steps[0], get_tex)
            tc_net_angle.move_to(plane["axes"].c2p(1, -1))
            self.play(Write(tc_net_angle))

            self.wait(0.5)

            arrow_qvq = LabeledArrow( arrow_qv.arrow.copy(), math_tex("qv").scale(plane_scale) )
            conditional_steps = [ FadeOut(labeled_arrow.label) ] if reverse_step_2 else []
            self.play(
                Rotate(arrow_qvq.arrow, angle2, about_point=origin),
                replace_tex(arrow_qvq.label, math_tex(label2).scale(plane_scale) ),
                Create(mobj_angle2),
                *conditional_steps
            )

            self.play(tc_net_angle.transform(net_angle_steps[1]))
            self.wait(0.5)
            self.play(tc_net_angle.transform(net_angle_steps[2], match=False))
            underline = Underline(tc_net_angle, color=WHITE)
            self.play(Create(underline))

            return VGroup( arrow_qv, arrow_qvq, mobj_angle1, mobj_angle2, tc_net_angle, underline )
        
        label = "qvq"
        angle = PI / 4
        sandwich1 = animate_sandwich(arrow_ab, plane_1i, label, angle, False, [
            r"\theta",
            r"\theta + \theta",
            r"2 \theta",
        ])
        self.wait()
        sandwich2 = animate_sandwich(arrow_cd, plane_jk, label, angle, True, [
            r"\theta",
            r"\theta - \theta",
            r"0",
        ])
        self.wait()

        self.play(
            tex_sandwich_1.animate.set_opacity(0.25),
            FadeOut(sandwich1, sandwich2),
            FadeIn(arrow_cd.label),
            Write(tex_sandwich_2),
        )
        self.wait()

        label = "qv\\overline{q}"
        sandwich1 = animate_sandwich(arrow_ab, plane_1i, label, angle, True, [
            r"\theta",
            r"\theta + (-\theta)",
            r"0",
        ])
        self.wait()
        sandwich2 = animate_sandwich(arrow_cd, plane_jk, label, angle, False, [
            r"\theta",
            r"\theta - (-\theta)",
            r"2 \theta",
        ])
        self.wait()

class RotationFormula(Scene):
    def construct(self):
        tex_title = Tex(r"Rotation Formula").to_corner(UL)
        self.add(tex_title)

        lines = VGroup(
            VGroup(
                Tex("The map"),
                colored_math_tex(r"v \rightarrow q v \overline{q}", t2c=color_map),
                Tex(r"rotates $v$ about ", "$i$", " by ").set_color_by_tex("i", RED),
                tex_angle := colored_math_tex(r"2 \theta", t2c=color_map)
            ).arrange(),
            Tex("where"),
            tex_q_def := colored_math_tex(r"q = cos(\theta) + i sin(\theta)", t2c=color_map),
        ).arrange(DOWN)

        
        self.play(Write(lines))
        self.wait()

        self.play(Indicate(tex_angle[1]), Indicate(tex_q_def[2]), Indicate(tex_q_def[6]))

        q_def_2_string = r"q = cos(\tfrac{1}{2}\theta) + i sin(\tfrac{1}{2}\theta)"
        _color_map = color_map | {r"\tfrac{1}{2}":WHITE}
        self.play( 
            LaggedStart(
                TransformMatchingTex( tex_q_def, colored_math_tex(q_def_2_string, t2c=_color_map).move_to(tex_q_def) ),
                TransformMatchingTex( tex_angle, colored_math_tex(r"\theta", t2c=color_map).move_to(tex_angle, LEFT), shift=ORIGIN ),
                lag_ratio=0.75
            ),
            run_time=1.5
        )

class PrimeCoordinates(ThreeDScene):
    def construct(self):
        if config.renderer == "opengl":
            self.set_camera_orientation(phi=65*DEGREES, theta=110*DEGREES)
        else:
            self.set_camera_orientation(phi=65*DEGREES, theta=20*DEGREES)

        def get_tex(string):
            return colored_math_tex(string, t2c=color_map)

        axes = standard_axes()
        numplane = jkplane()
        # self.add(numplane)
        self.add(axes)

        frame = Group(*coordinate_frame(label_dist=0.75))
        arrow_i, arrow_j, arrow_k, tex_i, tex_j, tex_k = frame
        self.add(arrow_i, arrow_j, arrow_k)
        self.add_fixed_orientation_mobjects( tex_i, tex_j, tex_k )

        self.wait()

        def transform_tex_anim(tex_from, tex_to):
            tex_to.move_to(tex_from).fix_orientation()
            tex_to.add_updater(tex_from.get_updaters()[0])
            return Transform(tex_from, tex_to)
        
        self.play( 
            *[
                Rotate( mobj, PI/3, normalize(vi - vj - vk), about_point=ORIGIN )
                # for mobj in [ numplane, arrow_i, arrow_j, arrow_k ]
                for mobj in [ arrow_i, arrow_j, arrow_k ]
            ],
            transform_tex_anim(tex_i, get_tex("i'")),
            transform_tex_anim(tex_j, get_tex("j'")),
            transform_tex_anim(tex_k, get_tex("k'"))
        )

        self.move_camera(phi=30*DEGREES, theta=70*DEGREES)
        self.wait()

class Isomorphism(Scene):
    def construct(self):
        words = ["-", "="]
        local_color_map = color_map | { "a":BLUE, "b":GREEN }
        def get_tex(string, t2c={}):
            return colored_math_tex(string, words=words, t2c=local_color_map | t2c)

        def ident_and_rotation_formula(i, j, k):
            replace = lambda string: string.replace("@i", i).replace("@j", j).replace("@k", k)

            def rotation_formula():
                text_rot = replace(r"q v \overline{q} \text{ rotates } v \text{ about } @i}")
                text_rot2 = replace(r"\text{counter-clockwise by } \theta")
                text_q = replace(r"q = cos( \frac{1}{2} \theta) + @i sin( \frac{1}{2} \theta)")
                tex_rot = get_tex(text_rot)
                tex_rot2 = get_tex(text_rot2)
                tex_q = get_tex(text_q)
                lines = VGroup(tex_rot, tex_rot2, tex_q).arrange(DOWN)
                rect = SurroundingRectangle(lines, fill_color=BLACK, fill_opacity=1)
                return VGroup(
                    MathTex(r"\Rightarrow"),
                    VGroup(rect, lines)
                ).arrange(RIGHT).scale(0.75)

            text_ident = replace(r"@i^2 = @j^2 = @k^2 = @i @j @k = -1")
            tex_ident = get_tex(text_ident).set_stroke(BLACK, 5, 1, True)

            return VGroup(tex_ident, rotation_formula()).arrange(RIGHT, buff=0.5)

        equations = ident_and_rotation_formula("i", "j", "k")
        equations_prime = ident_and_rotation_formula("{i'}", "{j'}", "{k'}")

        table = VGroup(
            *equations, 
            *equations_prime
        ).arrange_in_grid(2, 2, col_alignments="rl", buff=(0.25, 0.5))

        self.play(FadeIn(equations[0]))
        self.wait()
        self.play(FadeIn(equations[1]))
        self.wait()

        self.play(Write(equations_prime[0]))
        self.wait(2)
        self.play(FadeIn(equations_prime[1]))
        self.wait(2)

        ident, rotation_formula = equations_prime
        self.play( FadeOut( equations, equations_prime[1] ), ident.animate.to_corner(UL) )
        self.wait()

        # tex_cross_length = get_tex(r"|a \times b| = |a||b|sin(\theta)", t2c={r"\theta":WHITE})
        # tex_dot = get_tex(r"a \cdot b = |a||b|cos(\theta)", t2c={r"\theta":WHITE}).to_corner(UR)
        # tex_cross_length.to_corner(UR)
        # tex_dot.next_to(tex_cross_length, DOWN)
        tex_quat_product = get_tex(r"u v = u \times v - u \cdot v").to_corner(UR)

        tc = TexContainer("{i'}^2", get_tex)
        self.play(Write(tc))
        self.wait()

        self.play(Write(tex_quat_product))
        self.wait()

        self.play(tc.transform(r"{i'}^2 = {i'} \times {i'} - {i'} \cdot {i'}"))
        self.wait()

        # self.play(FadeIn(tex_cross_length))
        # self.wait()
        
        for part in tc.tex[3:6]:
            part.tex_string += "_" # Don't match these strings.
        self.play(tc.transform(r"{i'}^2 = - {i'} \cdot {i'}"))
        self.wait()

        # self.play(FadeIn(tex_dot))
        # self.wait()

        self.play(tc.transform(r"{i'}^2 = - |{i'}|^2"))
        self.wait()
        self.play(tc.transform(r"{i'}^2 = - 1"))
        self.wait()

        self.play(tc.transform(r"{i'}^2 = {j'}^2 = {k'}^2 = - 1"))
        self.wait()

        self.play(FadeOut(tc))
        self.wait()

        tc = TexContainer("i' j' k'", get_tex)
        self.play(FadeIn(tc))
        self.wait()

        self.play(Indicate(tc.tex[:2]))
        self.wait()

        tc_ij = TexContainer(r"i' j' = i' \times j' - i' \cdot j'", get_tex).next_to(tc, DOWN, buff=0.5)
        self.play(Write(tc_ij))
        self.wait()
        for part in tc_ij.tex[6:]:
            part.tex_string += "_" # Don't match these strings.
        self.play(tc_ij.transform(r"i' j' = i' \times j'"))
        self.wait()
        tex_ij2 = get_tex(r"i' j' = i' \times j' = k'").move_to(tc_ij, LEFT)
        self.play(Write(tex_ij2[6:]))
        self.wait()

        self.play(FadeOut(tc_ij, tex_ij2))
        self.play(Indicate(tc.tex[:2]))
        self.play(tc.transform("i' j' k' = {k'}{k'}"))
        self.wait()
        self.play(tc.transform("i' j' k' = {k'}^2"))
        self.wait()
        self.play(tc.transform("i' j' k' = -1"))
        self.wait()

        rotation_formula.set_opacity(0)
        # self.play(FadeOut(tc, tex_cross_length, tex_dot), equations_prime.animate.arrange().set_opacity(1))
        self.play(FadeOut(tc, tex_quat_product), equations_prime.animate.arrange().set_opacity(1))
        self.wait()

        # self.add(index_labels(tc.tex))
        # self.wait()
        # return