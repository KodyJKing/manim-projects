from re import T
from manim import *
from manim.mobject.opengl.opengl_three_dimensions import OpenGLSurface
from manim.utils.space_ops import ( quaternion_mult )
from mathutils import relative_quaternion2, smoothstep
import numpy as np

from utils import animate_replace_tex, colored_math_tex, compose_colored_tex, play_rewrite_sequence, tex_matches
from LabeledArrow import LabeledArrow

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
    "i": RED, "j": GREEN, "k": BLUE, "b": WHITE,
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
        if config.renderer == "opengl":
            self.set_camera_orientation(phi=65*DEGREES, theta=110*DEGREES)
        else:
            self.set_camera_orientation(phi=65*DEGREES, theta=20*DEGREES)

        axes = ThreeDAxes(x_range=[-5, 5], y_range=[-5, 5], z_range=[-5, 5], x_length=10, y_length=10, z_length=10)
        numplane = NumberPlane(x_range=[-10, 10], y_range=[-10, 10])
        numplane.set_opacity(0).rotate(PI/2, vj)
        self.add(numplane)
        self.add(axes)

        arrow_i = Arrow3D(ORIGIN, vi, color=RED)
        arrow_j = Arrow3D(ORIGIN, vj, color=GREEN)
        arrow_k = Arrow3D(ORIGIN, vk, color=BLUE)

        label_dist = 1.25
        tex_i = math_tex("i").move_to(vi * label_dist).set_stroke(BLACK, 5, 1, True)
        tex_j = math_tex("j").move_to(vj * label_dist).set_stroke(BLACK, 5, 1, True)
        tex_k = math_tex("k").move_to(vk * label_dist).set_stroke(BLACK, 5, 1, True)
        self.add_fixed_orientation_mobjects( tex_i, tex_j, tex_k )

        self.play( 
            FadeIn( arrow_i, arrow_j, arrow_k),
            Create(tex_i), Create(tex_j), Create(tex_k) )

        def indicate_arrow(arrow, tex):
            return AnimationGroup( Indicate(arrow, scale_factor=1), Indicate(tex) )

        self.wait()
        self.play( 
            indicate_arrow(arrow_j, tex_j),
            indicate_arrow(arrow_k, tex_k),
            numplane.animate.set_opacity(0.25)
        )
        self.play( indicate_arrow(arrow_i, tex_i) )
        self.wait()

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
        
        tex_mult_side = VGroup(Tex("Left multiplication:"), math_tex("iv")).arrange().to_corner(UL)
        tex_mult_side[1].shift(UP * 0.05) # Align to baseline. Might be worth creating a generic utility function for this.
        self.add_fixed_in_frame_mobjects(tex_mult_side)
        self.play(Write(tex_mult_side))
        show_sided_i_multiplication("left")
        self.play(FadeOut(tex_mult_side))
        tex_mult_side = VGroup(Tex("Right multiplication:"), math_tex("vi")).arrange().to_corner(UL)
        tex_mult_side[1].shift(UP * 0.05) # Align to baseline
        self.add_fixed_in_frame_mobjects(tex_mult_side)
        self.play(Write(tex_mult_side))
        show_sided_i_multiplication("right")
        self.play(FadeOut(tex_mult_side))

        self.wait()

class ThreeDPart2(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=65*DEGREES, theta=110*DEGREES)

        numplane = NumberPlane(x_range=[-10, 10], y_range=[-10, 10])
        numplane.rotate(PI/2, vj).set_opacity(.25)
        self.add(numplane)
        axes = ThreeDAxes(x_range=[-5, 5], y_range=[-5, 5], z_range=[-5, 5], x_length=10, y_length=10, z_length=10)
        self.add(axes)

        arrow_i = Arrow3D(ORIGIN, vi, color=RED)
        arrow_j = Arrow3D(ORIGIN, vj, color=GREEN)
        arrow_k = Arrow3D(ORIGIN, vk, color=BLUE)
        self.add(arrow_i, arrow_j, arrow_k)

        label_dist = 1.25
        tex_i = math_tex("i").move_to(vi * label_dist)
        tex_j = math_tex("j").move_to(vj * label_dist)
        tex_k = math_tex("k").move_to(vk * label_dist)
        self.add_fixed_orientation_mobjects( tex_i, tex_j, tex_k )

        table = pure_quat_times_table(color_map).scale(0.5).to_edge(LEFT)
        table_background = SurroundingRectangle( table, color=BLACK, fill_color=BLACK, fill_opacity=1, buff=0 )
        self.add_fixed_in_frame_mobjects(table_background)
        self.add_fixed_in_frame_mobjects(table) 

        self.play(FadeOut(table_background, table))

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

        def animate_sandwich(labeled_arrow: LabeledArrow, plane: Axes, label2: str, angle: float, reverse_step_2: bool):
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

            self.wait(0.5)

            arrow_qvq = LabeledArrow( arrow_qv.arrow.copy(), math_tex("qv").scale(plane_scale) )
            conditional_steps = [ FadeOut(labeled_arrow.label) ] if reverse_step_2 else []
            self.play(
                Rotate(arrow_qvq.arrow, angle2, about_point=origin),
                replace_tex(arrow_qvq.label, math_tex(label2).scale(plane_scale) ),
                Create(mobj_angle2),
                *conditional_steps
            )

            net_angle = "\\theta - \\theta" if reverse_step_2 else "\\theta + \\theta"
            net_angle2 = "0" if reverse_step_2 else "2\\theta"
            tex_net_angle = math_tex(net_angle).move_to(plane["axes"].c2p(1, -1))
            self.play(Write(tex_net_angle))
            self.wait(.5)
            self.play(replace_tex(tex_net_angle, net_angle2, aligned_edge=ORIGIN))
            circle = Circle(0.3, color=YELLOW).move_to(tex_net_angle)
            # circle.point_from_proportion()
            self.play(Create(circle))

            return VGroup( arrow_qv, arrow_qvq, mobj_angle1, mobj_angle2, tex_net_angle, circle )
        
        label = "qvq"
        angle = PI / 4
        sandwich1 = animate_sandwich(arrow_ab, plane_1i, label, angle, False)
        self.wait()
        sandwich2 = animate_sandwich(arrow_cd, plane_jk, label, angle, True)
        self.wait()

        self.play(
            tex_sandwich_1.animate.set_opacity(0.25),
            FadeOut(sandwich1, sandwich2),
            FadeIn(arrow_cd.label),
            Write(tex_sandwich_2),
        )
        self.wait()

        label = "qv\\overline{q}"
        sandwich1 = animate_sandwich(arrow_ab, plane_1i, label, angle, True)
        self.wait()
        sandwich2 = animate_sandwich(arrow_cd, plane_jk, label, angle, False)
        self.wait()

class RotationFormula(Scene):
    def construct(self):
        tex_title = Tex(r"\underline{Rotation Formula}").to_corner(UL)
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

class Generalizing(Scene):
    def construct(self):
        _color_map = color_map | {"ii":RED, "{i}":RED, "-1": WHITE, "=": WHITE}
        tex_kw = { "t2c": _color_map }

        def get_permute(r):
            epsilon = 0.05/r
            circle = Circle(r)
            pfp = lambda p: circle.point_from_proportion(p)
            get_arrow = lambda p: CurvedArrow(pfp(p+epsilon), pfp(p+1/3-epsilon), radius=r+r/15, tip_length=r/5)
            return VGroup(
                math_tex("i").move_to(pfp(0/3)),
                get_arrow(0/3),
                math_tex("j").move_to(pfp(1/3)),
                get_arrow(1/3),
                math_tex("k").move_to(pfp(2/3)),
                get_arrow(2/3),
            )

        equations = VGroup(
            tex_full_ident := math_tex("i^2 = j^2 = k^2 = ijk = -1"),
            tex_ident := colored_math_tex("i j k = -1", **tex_kw),
        ).arrange(DOWN, 1)

        self.play(Write(tex_full_ident))

        permute = get_permute(.5)
        permute.to_edge(UP)
        self.play(Write(permute))

        self.play(Write(tex_ident))

        def transform(new_tex, match=True, **kwargs):
            new_tex.move_to(tex_ident)
            if match:
                self.play(TransformMatchingTex(tex_ident, new_tex, **kwargs))
            else:
                self.play(ReplacementTransform(tex_ident, new_tex, **kwargs))
            return new_tex
        
        def replace(new_tex):
            new_tex.move_to(tex_ident)
            self.remove(tex_ident)
            return new_tex

        tex_ident = transform(colored_math_tex("{i}(i j k){i} = {i}(-1){i}", **tex_kw), shift=DOWN)
        self.wait()
        tex_ident = replace(colored_math_tex("i(i j k)i = i(-1)i", **tex_kw))
        tex_ident = transform(colored_math_tex("(i i)j k i = (i i)(-1)", **tex_kw), path_arc=90*DEGREES)
        self.wait()
        tex_ident = replace(colored_math_tex("(ii)j k i = (ii)(-1)", **tex_kw))
        tex_ident = transform(colored_math_tex("j k i = -1", **tex_kw), shift=DOWN)
        self.wait()

        tex_ident_squares = colored_math_tex("j^2 = k^2 = i^2 = ", **tex_kw)
        VGroup(tex_ident_squares, tex_ident_copy := tex_ident.copy()).arrange(aligned_edge=DOWN, buff=0.16).move_to(tex_ident)
        self.play(Write(tex_ident_squares), tex_ident.animate.move_to(tex_ident_copy))
        tex_ident_full_j = VGroup(tex_ident_squares, tex_ident)

        self.play( VGroup( tex_full_ident, tex_ident_full_j ).animate.to_edge(LEFT, buff=1) )

        def add_blurb(identity, axis_string="i", color=RED, theta_color=MYPINK):

            _color_map = color_map | { r"\overline{q}": theta_color, "q": theta_color, r"\theta": theta_color }

            blurb = VGroup(
                VGroup(
                    Tex("If"),
                    colored_math_tex(r"q = cos(\tfrac{1}{2}\theta) + " + axis_string + r" sin(\tfrac{1}{2}\theta)", t2c=_color_map),
                ).arrange(),
                VGroup(
                    colored_math_tex(r"q v \overline{q}", t2c=_color_map),
                    Tex(r"rotates $v$ about ", f"${axis_string}$", " by ").set_color_by_tex(axis_string, color),
                    colored_math_tex(r"\theta", t2c=_color_map)
                ).arrange(),
            ).arrange(DOWN)
            blurb.scale(2/3)
            blurb = VGroup( SurroundingRectangle(blurb).set_z_index(-1), blurb )
            blurb = VGroup( MathTex(r"\Rightarrow"), blurb ).arrange(buff=1)
            blurb.next_to(identity, buff=1)

            self.play(Write(blurb))
        
        add_blurb(tex_full_ident)
        add_blurb(tex_ident_full_j, "j", GREEN, GREEN_B)