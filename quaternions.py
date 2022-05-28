import imp
from re import M
from unicodedata import numeric
from manim import *
from manim.mobject.opengl.opengl_three_dimensions import OpenGLSurface
from manim.utils.space_ops import ( quaternion_mult )
from mathutils import relative_quaternion2
import numpy as np

from utils import animate_replace_tex, tex_matches
from LabeledArrow import LabeledArrow

SurfaceClass = OpenGLSurface if config.renderer == "opengl" else Surface

ihat = "\hat{\imath}"
jhat = "\hat{\jmath}"
khat = "\hat{k}"
ihatn = "-" + ihat
jhatn = "-" + jhat
khatn = "-" + khat

color_map = { 
    ihat: RED, jhat: GREEN, khat: BLUE,
    "i": RED, "j": GREEN, "k": BLUE, "b": WHITE,
    "\\times": WHITE,
}

def math_tex(*args, **kwargs):
    return MathTex(*args, tex_to_color_map=color_map, **kwargs)

def replace_tex(tex, text):
    return animate_replace_tex(tex, text, tex_to_color_map=color_map)

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
        # self.play( 
        #     Circumscribe( VGroup(
        #         tex_quat_form.get_part_by_tex("b"),
        #         tex_quat_form.get_part_by_tex("k"),
        #     ), run_time=3 ),
        #     run_time=3
        # )
        self.play( Write( tex_ijk_definition ) )

        ijk_table = pure_quat_times_table(color_map).scale(0.75).move_to(RIGHT * 3)
        cross_table = vec_cross_table(color_map) #.scale(0.5).move_to(LEFT * 3)
        dot_table = vec_dot_table(color_map) #.scale(0.5).move_to(LEFT * 3)
        dot_table.next_to(cross_table, DOWN)
        vec_tables = VGroup(cross_table, dot_table).scale(.6).move_to(LEFT * 3)

        rect = SurroundingRectangle(tex_ijk_definition)
        tex_ijk_definition.add(rect)
        self.play(Create(rect))

        self.play( equations.animate.move_to(LEFT * 3) )
        self.play( Create(ijk_table) )
        self.wait(3)
        self.play( FadeOut(equations) )
        self.play( FadeIn(vec_tables) )
        self.wait()

        equation_quat_cross_dot = MathTex(r" uv = u \times v - u \cdot v ", tex_to_color_map=color_map)
        equation_quat_cross_dot.next_to(ijk_table, UP)
        self.play( Write(equation_quat_cross_dot) )

        self.wait()

class ThreeD(ThreeDScene):
    def construct(self):
        vi = RIGHT
        vj = UP
        vk = OUT

        self.set_camera_orientation(phi=65*DEGREES, theta=110*DEGREES)

        numplane = NumberPlane(x_range=[-10, 10], y_range=[-10, 10])
        numplane.set_opacity(0).rotate(PI/2, vj)
        self.add(numplane)
        axes = ThreeDAxes()
        self.add(axes)

        arrow_i = Arrow3D(ORIGIN, vi, color=RED)
        arrow_j = Arrow3D(ORIGIN, vj, color=GREEN)
        arrow_k = Arrow3D(ORIGIN, vk, color=BLUE)

        label_dist = 1.25
        tex_i = math_tex("i").move_to(vi * label_dist)
        tex_j = math_tex("j").move_to(vj * label_dist)
        tex_k = math_tex("k").move_to(vk * label_dist)
        self.add_fixed_orientation_mobjects( tex_i, tex_j, tex_k )

        self.play( 
            # FadeIn( arrow_i, arrow_j, arrow_k, plane ),
            FadeIn( arrow_i, arrow_j, arrow_k),
            Create(tex_i), Create(tex_j), Create(tex_k) )

        def indicate_arrow(arrow, tex):
            return AnimationGroup( Indicate(arrow, scale_factor=1), Indicate(tex) )


        self.play( indicate_arrow(arrow_i, tex_i) )
        self.wait()
        numplane.set_opacity(.25)
        self.play( 
            indicate_arrow(arrow_j, tex_j),
            indicate_arrow(arrow_k, tex_k),
            # GrowFromPoint(plane, ORIGIN) )
            FadeIn(numplane)
        )

        table = pure_quat_times_table(color_map).scale(0.5).to_edge(LEFT)
        table_background = SurroundingRectangle( table, color=BLACK, fill_color=BLACK, fill_opacity=1, buff=0 )
        self.add_fixed_in_frame_mobjects(table_background)
        self.add_fixed_in_frame_mobjects(table)
        self.play( FadeIn(table_background), Write(table) )

        def show_sided_i_multiplication(side="left"):
            angle = PI/2 if side == "left" else -PI/2
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
            for i in range(2):
                arc = arcs[i]
                arrow = arrows_jk[i].copy()
                self.add_fixed_in_frame_mobjects(arc)
                self.play( Create(arc) )
                self.play( Rotate( arrow, angle, vi, ORIGIN ), indicate_arrow(arrow_i, tex_i) )
                self.play( FadeOut( arrow, run_time=.25 ) )
            
            # Rotate all together
            arrows_jk_2 = [arrow_j.copy(), arrow_k.copy() ]
            self.add(*arrows_jk_2)
            self.play( 
                *[ Rotate( arrow, angle, vi, ORIGIN ) for arrow in arrows_jk_2 ],
                Rotate(numplane, angle, vi),
                indicate_arrow(arrow_i, tex_i), run_time=2 )
            self.play( FadeOut(*arrows_jk_2) )

            self.play( FadeOut( *arcs, i_rect ) )
        
        show_sided_i_multiplication("left")
        show_sided_i_multiplication("right")

        self.wait()

class DualPlanes(Scene):
    def construct(self):

        def make_plane(x_color, y_color, x_label, y_label ):
            plane_range = [-3, +3]
            axes = Axes(x_range=plane_range, y_range=plane_range,
                x_length=None, y_length=None, tips=False)
            x_axis, y_axis = axes.get_axes()
            x_axis.set_fill(x_color).set_stroke(x_color)
            y_axis.set_fill(y_color).set_stroke(y_color)

            for label, color, axis in [ ( x_label, x_color, RIGHT ), ( y_label, y_color, UP ) ]:
                # x, y, z = axis
                # offset = np.array([ -y, -x, z ])
                offset = np.cross(axis, OUT)
                axes.add( MathTex( label, color=color )
                    .scale(1/2)
                    .next_to( axes.c2p(*axis), offset ) )

            # axes.add( SurroundingRectangle(
            #     axes, buff=0.1, color=WHITE,
            #     fill_color=BLACK, fill_opacity=1,
            #     z_index=-1 ) )
            axes.add( Circle(plane_range[1]+.1, color=WHITE,
                fill_color=BLACK, fill_opacity=1,
                z_index=-1) )

            return axes

        plane_1i = make_plane(WHITE, RED, "1", "i")
        plane_jk = make_plane(BLUE, GREEN, "j", "k")

        plane_scale = 2/3
        for plane, corner in [ (plane_1i, UL), (plane_jk, UR) ]:
            self.play( Create(plane) )
            self.play( plane.animate.scale(plane_scale).to_corner(corner) )

        self.wait()

        tex_quat_form = math_tex(*"v = a + bi + cj + dk".split(" "))
        self.play( Write( tex_quat_form ) )

        self.wait()
        
        # Complex and jk components of v.
        arrow_ab, arrow_cd = [
            LabeledArrow(
                Arrow( plane.c2p(0,0), plane.c2p(*coord), buff=0),
                math_tex("v").scale(plane_scale),
                # distance=.1, aligned_edge=edge
            ) for plane, coord, edge in [ 
                (plane_1i, (3/5,-4/5), LEFT),
                (plane_jk, (3/5, 4/5), RIGHT)
            ]
        ]

        self.play( LaggedStart( 
            arrow_ab.grow_animation(),
            Circumscribe( tex_matches(tex_quat_form, "a", "i" ) ),
            lag_ratio=.25 ), run_time=1.5 )
        self.play( LaggedStart(  
            arrow_cd.grow_animation(),
            Circumscribe( tex_matches(tex_quat_form, "c", "k" ) ),
            lag_ratio=.25 ), run_time=1.5 )

        self.play(
            plane_1i.animate.set_opacity(0.25),
            plane_jk.animate.set_opacity(0.25),
        )

        arrows_iv = VGroup(arrow_ab.copy(), arrow_cd.copy())
        self.add(arrows_iv)
        self.play( *[
            AnimationGroup( Rotate( arrow.arrow, PI/2, about_point=arrow.arrow.get_start() ),
                replace_tex(arrow.label, math_tex("iv").scale(plane_scale) ) )
            for arrow in arrows_iv
        ])

        self.wait()

        arrow_abi = arrow_ab.copy()
        arrow_cdi = arrow_cd.copy()
        self.add(arrow_abi, arrow_cdi)
        self.play( 
            Rotate(arrow_abi.arrow, PI/2, about_point=arrow_abi.arrow.get_start() ),
            replace_tex(arrow_abi.label, math_tex("vi").scale(plane_scale) ),
            FadeOut( arrows_iv[0].label ),

            Rotate(arrow_cdi.arrow, -PI/2, about_point=arrow_cdi.arrow.get_start() ),
            replace_tex(arrow_cdi.label, math_tex("vi").scale(plane_scale) ),
        )

        self.wait()