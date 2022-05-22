import math
from manim import *
from manim.utils.space_ops import ( 
    quaternion_mult as qmul,
    quaternion_from_angle_axis as aa2q,
    angle_axis_from_quaternion as q2aa,
    quaternion_conjugate as qconj
)
import numpy as np

from ExternalLabeledDot import ExternalLabeledDot
from LabeledArrow import LabeledArrow
from mathutils import clamp, rotate_cc, rotate_cw
from utils import angle_label_pos, animate_replace_tex

c1 = np.array([1, 0, 0])
ci = np.array([0, 1, 0])

blank_axes = { "include_ticks": False }

def get_shift( mobj, other ):
    return other.get_center() - mobj.get_center()
def eq_shift( eq: MathTex, other: MathTex ):
    return get_shift( eq.get_part_by_tex("="), other.get_part_by_tex("=") ) * RIGHT
def align_eq(eq: MathTex, other: MathTex):
    eq.next_to(other, DOWN)
    eq.shift( eq_shift(eq, other) )

class Intro(ThreeDScene):
    def construct(self):
        # Introduce definition
        eqn1 = MathTex( "i", "=", "\sqrt{-1}" )
        eqn2 = MathTex( "i^2", "=", "\sqrt{", "-1", "}^2" )
        eqn2b = MathTex( "i^2", "=", "-1" )
        align_eq(eqn2, eqn1)
        align_eq(eqn2b, eqn1)
        eqns = VGroup(eqn1, eqn2, eqn2b).move_to(ORIGIN)
        self.play( Write(eqn1[0]) )
        self.wait()
        self.play( Write( VGroup( *eqn1[1:] ) ) )
        self.play( FadeIn( eqn2, shift=DOWN ) )
        eqns.remove(eqn2)
        self.play( TransformMatchingTex( eqn2, eqn2b ) )
        self.wait()
        self.add_fixed_in_frame_mobjects(eqns)

        # Demonstrate absence of i on real number line
        axes = Axes( tips=False, x_range=[-3, 3], y_range=[-3, 9], x_length=4, y_length=4 )
        axes.set_opacity(0)
        self.play( VGroup( eqns, axes ).animate.arrange(buff=2) )
        axes.set_opacity(1)
        square_graph = axes.plot( lambda x: x * x, color=BLUE )
        eq_xsq = MathTex( "y = x^2" ).next_to( axes.c2p(-2,9), UP )
        self.play( Create(axes), Create(square_graph), Write(eq_xsq) )

        # Add evaluation indicators to graph
        x_tracker = ValueTracker(2.5)
        def get_dots(plot_axes, func, unit=None, label_dirs=(DOWN, RIGHT+UP*.5)):
            x = x_tracker.get_value()
            fx = func(x)
            def get_dot(coor_mask: np.ndarray=np.array([1, 1, 1])):
                coord = np.array([x, fx, 1]) * coor_mask
                return Dot( plot_axes.c2p(*coord) )
            dot_xy = get_dot()
            dot_x = get_dot( np.array([1, 0, 1]) )
            dot_y = get_dot( np.array([0, 1, 1]) )
            line_x = Line( dot_x.get_center(), dot_xy.get_center() )
            line_y = Line( dot_xy.get_center(), dot_y.get_center() )
            opacity = 1 - (1 / (9*x**2 + 1) )
            x_dir, y_dir = label_dirs
            decimal_x = DecimalNumber(x,  font_size=36, unit=unit).next_to(dot_x, x_dir).set_opacity(opacity)
            decimal_y = DecimalNumber(fx, font_size=36).next_to(dot_y, y_dir).set_opacity(opacity)
            return VGroup( dot_x, line_x, dot_xy, line_y, dot_y, decimal_x, decimal_y )
        dots = always_redraw( lambda: get_dots( axes, lambda x: x * x ) )
        self.play(Create(dots))

        # Sweep x
        self.play( x_tracker.animate.set_value(-2.5), run_time=4 )
        self.wait()
        dots.suspend_updating()
        self.play( Indicate( axes.get_axis(0) ) )
        dots.resume_updating()
        self.play( x_tracker.animate.set_value(0), run_time=2 )
        self.wait()

        # New axis
        self.play( FadeOut( eq_xsq ) )
        axes_im = Axes( tips=False, x_range=[-3, 3], y_range=[-9, 3], x_length=4, y_length=4 )
        axes_im.set_z_index(-1)
        axes_im.shift( axes.c2p(0, 0) - axes_im.c2p(0, 0) ).rotate(PI/2,UP)
        axes_im.get_axis(1).rotate(-PI/2,UP)
        axes_im.set_opacity(0)
        graph_parts = VGroup( axes, axes_im, square_graph, dots )
        self.play(graph_parts.animate.shift(UP))

        quat = qmul(
            aa2q( 15*DEGREES, RIGHT ),
            aa2q( -75*DEGREES, UP ) )
        angle, axis = q2aa(quat)
        about_point = axes.c2p(0, 3)
        self.play( Rotate( graph_parts, angle, axis, about_point=about_point ) )

        axes_im.set_opacity(1)
        self.play( Create(axes_im) )
        self.play(Indicate(axes_im.get_axis(0)))
        square_graph_im = axes_im.plot( lambda x: -x * x, color=BLUE_E )
        square_graph_im.set_z_index(-1)
        self.play( Create( square_graph_im ) )
        graph_parts.add(axes_im, square_graph_im)
        self.wait()

        self.play( axes.get_axis(0).animate.set_opacity(.25) )

        self.remove(dots)
        dots = always_redraw( lambda: get_dots( 
            axes_im, lambda x: -x * x, "i",
            ( UP, LEFT )
        ) )
        self.add(dots)
        self.play( x_tracker.animate.set_value(2), run_time=2 )
        self.wait()
        self.play( x_tracker.animate.set_value(1), run_time=1 )
        
        # quat_inv = qconj(quat)
        # angle, axis = q2aa(quat_inv)
        # self.play( Rotate( graph_parts, angle, axis, about_point=about_point ) )

        self.wait()

class ComplexNumbers(Scene):
    def construct(self):
        color_map = { 
            "a": RED, "b": GREEN,
            "arg": WHITE,
        }
        tex_config = { "tex_to_color_map": color_map }
        axes = Axes( x_axis_config=blank_axes, y_axis_config=blank_axes, x_length=20, y_length=10, tips=False ).set_z_index(-2)
        numplane = ComplexPlane().set_z_index(-1)
        numplane.get_coordinate_labels()
        coords = VGroup( numplane.get_coordinate_labels(), numplane.get_coordinate_labels(0) )
        self.play( Create(axes), Create(coords) )
        self.wait()

        # Introduce a + bi
        v = 3*c1 + 2*ci
        arrow_a = Arrow(ORIGIN, v*RIGHT, color=RED, buff=0).set_z_index(1)
        arrow_a.add(label_a := MathTex("a", **tex_config).next_to(arrow_a, DOWN))
        arrow_b = Arrow(ORIGIN, v*UP, color=GREEN, buff=0).shift(v*RIGHT)
        arrow_b.add(label_b := MathTex("bi", **tex_config).next_to(arrow_b, RIGHT))
        dot_v = ExternalLabeledDot( Dot( v ), MathTex("a + bi", **tex_config) )
        arrow_v = Arrow( ORIGIN, v, buff=0 ).set_z_index(2)
        self.play( GrowArrow( arrow_a ) )
        self.play( GrowArrow( arrow_b ) )
        self.play( dot_v.create_animation() )
        arrow_a.remove(label_a)
        arrow_b.remove(label_b)
        self.play(FadeOut(label_a, label_b))
        self.wait()
        self.play( GrowArrow(arrow_v) )

        background = VGroup(coords, axes.get_axis(1))
        self.play(FadeOut(arrow_a, arrow_b), background.animate.set_opacity(0.125))
        
        # Define arg and modulus
        brace = Brace(arrow_v, direction=arrow_v.copy().rotate(PI/2).get_unit_vector() )
        brace_tex = MathTex("r")
        brace.put_at_tip(brace_tex, False)
        self.play(Create(brace), Write(brace_tex))
        self.wait()

        angle = Angle(arrow_a, arrow_v, 1 ).set_z_index(-1)
        angle_tex = MathTex("\\theta" ).move_to(angle_label_pos(arrow_a, arrow_v, 1 + 3 * SMALL_BUFF))
        self.play( Create(angle), Write(angle_tex) )
        self.wait()

        self.play(animate_replace_tex(brace_tex, "|a+bi|", color_map, RIGHT))
        self.wait()
        arg_tex = MathTex("arg", "(a+bi)", **tex_config)
        arg_tex[0].set_color(WHITE)
        self.play(animate_replace_tex(angle_tex, arg_tex))
        self.wait()

        self.play( FadeOut(angle_tex, brace, brace_tex),
            FadeIn(arrow_a, arrow_b), background.animate.set_opacity(1) )

        # Define conjugate
        conjugate_parts = VGroup(arrow_b.copy(), arrow_v.copy(), angle_conj := angle.copy())
        self.add(conjugate_parts)
        self.play(Rotate(conjugate_parts, PI, RIGHT, ORIGIN))
        self.wait()
        dot_conjugate = ExternalLabeledDot(Dot(v*RIGHT -v*UP), MathTex("a - bi", **tex_config), direction=DR)
        self.play( dot_conjugate.create_animation() )
        self.wait()

        eq_conjugate = MathTex("\\overline{a+bi}=a-bi").to_corner(UL)
        self.play(Write(eq_conjugate))
        self.wait()

        # Arg of conjugate z is negative arg z
        self.play(Indicate(angle_conj), run_time=2)
        eq_conjugate_arg = MathTex("arg(\\overline{z}) = -arg(z)").next_to(eq_conjugate, DOWN, aligned_edge=LEFT)
        self.play(Write(eq_conjugate_arg))

class ComponentTimesI(Scene):
    def construct(self):
        numplane = ComplexPlane().add_coordinates()

        points = [c1, ci, -c1, -ci]

        def get_dots_and_arcs(scale, get_label):
            def labeled_dot(point, index):
                return ExternalLabeledDot(
                    Dot(point * scale),
                    get_label(point * scale, index),
                    direction=normalize(point),
                    distance=1
                )
            dots = VGroup(*map( labeled_dot, points, range(4) ))
            arcs = []
            for i in range(len(points)):
                j = (i + 1) % len(points)
                pointI = points[i] * scale
                pointJ = points[j] * scale
                normal = rotate_cw(pointJ - pointI)
                color = BLUE
                arc = CurvedArrow(pointI, pointJ, radius=scale, tip_length=.2, color=color)
                label = MathTex("i", color=color).next_to(arc.get_center(), normal)
                arc = VGroup(arc, label)
                arcs.append(arc)
            arcs = VGroup(*arcs)
            return dots, arcs

        dots, arcs = get_dots_and_arcs(1, lambda p, i: ["1", "i", "-1", "-i"][i])

        self.play( Create(numplane) )

        self.play(
            numplane.coordinate_labels.animate.set_opacity(.25),
            numplane.animate.set_opacity(.25),
            FadeIn(dots[0])
        )
        arrow = Arrow(ORIGIN, c1, color=RED, buff=0, z_index=1)
        for i in range(3):
            self.play( FadeIn(dots[i + 1]), Rotate(arrow, PI / 2, about_point=ORIGIN), FadeIn(arcs[i]))
            self.wait(.5)
        self.play(FadeIn(arcs[3]), Rotate(arrow, PI / 2, about_point=ORIGIN))

        self.play(FadeOut(arrow))

        scale_tracker = ValueTracker(1)
        def get_loop():
            def get_label(p, i):
                return DecimalNumber(p[0] + p[1], unit=[None, "i"][i % 2])
            scale = scale_tracker.get_value()
            dots, arcs = get_dots_and_arcs(scale, get_label)
            return VGroup(dots, arcs)
        loop = always_redraw( get_loop )
        self.play( ReplacementTransform(VGroup(dots, arcs), loop) )
        self.play(scale_tracker.animate.set_value(3), run_time=3)
        self.wait()

class ArbitraryTimesI(Scene):
    def construct(self):
        color_map = { "a": RED, "b": GREEN }

        v = np.array([3, 2, 0])
        iv = rotate_cc(v)
        arrow_re_ref = Arrow(ORIGIN, v[0] * c1, buff=0, color=RED)
        arrow_im_ref = Arrow(ORIGIN, v[1] * ci, buff=0, color=GREEN)
        arrow_im_ref.shift(arrow_re_ref.get_end())

        dot_v = ExternalLabeledDot( 
            Dot(v),  MathTex("a + bi", tex_to_color_map=color_map),
            distance=1, z_index=1 )
        
        dot_iv = ExternalLabeledDot( 
            Dot(iv),  MathTex("i(a + bi)", tex_to_color_map=color_map),
            direction=normalize(LEFT + UP),
            distance=1, z_index=1 )

        numplane = ComplexPlane().add_coordinates()

        arrow_re = arrow_re_ref.copy()
        arrow_im = arrow_im_ref.copy()

        self.add(numplane)
        self.play( dot_v.create_animation() )
        self.play( GrowArrow(arrow_re) )
        self.play( GrowArrow(arrow_im) )

        self.wait()

        self.play(
            Rotate( arrow_re, PI / 2, about_point=arrow_re.get_start() ),
            Rotate( arrow_im, PI / 2, about_point=arrow_im.get_start() )
        )
        self.play( arrow_im.animate.shift( arrow_re.get_end() - arrow_im.get_start() ) )
        self.play( FadeIn( arrow_re_ref, arrow_im_ref ) )
        self.play( dot_iv.create_animation() )
        self.wait()
        steps = "ai + bi^2; -b + ai".split(";")
        for step in steps:
            self.play( animate_replace_tex( dot_iv.label, step, color_map, ORIGIN ) )
            self.wait()

        self.play(
            Transform( arrow_re, arrow_re_ref ),
            Transform( arrow_im, arrow_im_ref )
        )

        arrow_comp_ref = Arrow(ORIGIN, v, buff=0)
        arrow_comp = arrow_comp_ref.copy()

        self.play( FadeIn(arrow_comp) )
        self.add(arrow_comp_ref)
        arrows = VGroup(arrow_re, arrow_im, arrow_comp)

        self.play( Rotate(arrows, PI / 2, about_point=ORIGIN) )

        right_angle = RightAngle(arrow_comp_ref, arrow_comp, .5)

        self.play( Create(right_angle) )
        
        step_tex = MathTex("(a, b) \cdot (-b, a)", tex_to_color_map=color_map).move_to(ORIGIN + DOWN * 2)
        step_rect = SurroundingRectangle(step_tex, color=WHITE).set_fill(BLACK, opacity=1)
        step = VGroup(step_rect, step_tex)
        self.play( Write(step) )
        self.wait()
        self.play( animate_replace_tex(step_tex, "-ab + ba", color_map, ORIGIN) )
        self.wait()
        self.play( animate_replace_tex(step_tex, "0", color_map, ORIGIN) )

        self.wait()

class VActingOnI(Scene):
    def construct(self):
        numplane = ComplexPlane().set_opacity(.25).set_z_index(-100)
        dot_origin = Dot(ORIGIN)

        self.add(numplane, dot_origin)

        v_angle = PI / 4
        v = np.array([ math.cos(v_angle), math.sin(v_angle), 0 ])
        
        arrow_i = LabeledArrow( Arrow(ORIGIN, ci, buff=0, stroke_width=3), "i" )
        arrow_v = LabeledArrow( Arrow(ORIGIN, v, buff=0, stroke_width=3), "v" )

        line_re = Line(ORIGIN, c1)
        angle_i = Angle(line_re, arrow_i.arrow, radius=.5, elbow=True)
        angle_v = Angle(line_re, arrow_v.arrow, radius=.5)

        comparison_i = get_angle_comparison(arrow_i.arrow, v_angle, BLUE)
        comparison_v = get_angle_comparison(arrow_v.arrow, PI / 2, BLUE)

        self.play( FadeIn(arrow_v, angle_v) )
        self.add( comparison_v["arrow"] )
        self.play( 
            FadeOut(arrow_v.label),
            Rotate( arrow_v.arrow, PI / 2, about_point=ORIGIN ),
            Create(comparison_v["angle"])
        )
        dot_iv = ExternalLabeledDot(Dot(arrow_v.arrow.get_end()), "iv", aligned_edge=RIGHT).set_z_index(10)
        self.play( dot_iv.create_animation() )
        self.play( FadeOut(arrow_v.arrow, angle_v, comparison_v) )

        self.play( FadeIn(arrow_i, angle_i))
        self.add( comparison_i["arrow"] )
        self.play(
            FadeOut(arrow_i.label),
            Rotate( arrow_i.arrow, v_angle, about_point=ORIGIN ),
            Create(comparison_i["angle"])
        )
        self.play( FadeOut(arrow_i.arrow, angle_i, comparison_i) )

class ArbitraryTimesArbitrary2(Scene):
    def construct(self):
        color_map = { 
            "a": RED, "b": GREEN,
            "u": BLUE, "v": YELLOW, "iu": BLUE_E,
            "\\theta_{u}": BLUE, "\\theta_{v}": YELLOW,
            "r_{u}": BLUE, "r_{v}": YELLOW,
        }

        v = np.array([3, 2, 0])
        u_angle = PI / 12
        u = np.array([math.cos(u_angle), math.sin(u_angle), 0])
        iu = rotate_cc(u)

        numplane = Axes(x_range=[-8, 8], y_range=[-8, 8], x_length=None, y_length=None).set_opacity(0.5).set_z_index(-3)
        numplane_u = NumberPlane(x_range=[-16, 16], y_range=[-16, 16]).set_opacity(0.5).set_z_index(-2).rotate(u_angle)

        self.add(numplane)
        self.add( Dot(ORIGIN).set_z_index(2) )
        self.wait(0.5)

        arrow_u = LabeledArrow( 
            Arrow( ORIGIN, u, buff=0, color=BLUE ),
            MathTex("u", color=BLUE),
            perp_distance=-0.25, distance=0, alpha=0.5
        ).set_z_index(1)
        arrow_iu = LabeledArrow(
            Arrow( ORIGIN, iu, buff=0, color=BLUE_E ),
            MathTex("iu", color=BLUE_E),
            perp_distance=0.25, distance=0, alpha=0.5
        ).set_z_index(1)

        line_re = Line(ORIGIN, RIGHT)
        line_u = Line(ORIGIN, u * 10, color=BLUE )
        angle_u = always_redraw( lambda: Angle( line_re, arrow_u.arrow, radius=1, color=BLUE ) )

        self.play( arrow_u.grow_animation() )

        angle_u.suspend_updating()
        self.play( Create( angle_u ) )
        angle_u.resume_updating()

        self.wait(2)
        self.play( arrow_iu.grow_animation() )
        # for arrow in [arrow_u, arrow_iu]:
        self.wait(0.5)

        self.play( Create( numplane_u ) )

        rotation_group = VGroup(arrow_u.arrow, arrow_iu.arrow, numplane_u)

        for _delta_angle in [ PI / 4, -PI / 4 -u_angle, u_angle ]:
            self.play( Rotate( rotation_group, _delta_angle, about_point=ORIGIN ), run_time=1.5 )

        self.wait(1)

        arrow_au = LabeledArrow(
            Arrow( ORIGIN, u * v[0], buff=0, color=RED ),
            MathTex("au", tex_to_color_map=color_map),
            perp_distance=-0.25, distance=0, alpha=0.75
        )
        arrow_biu = LabeledArrow(
            Arrow( ORIGIN, iu * v[1], buff=0, color=GREEN ),
            MathTex("biu", tex_to_color_map=color_map),
            perp_distance=-0.2, distance=0, alpha=0.5,
            aligned_edge=LEFT
        ).shift( arrow_au.arrow.get_end() )

        for arrow in [arrow_au, arrow_biu]:
            self.play( arrow.grow_animation() )
        
        dot_uv = ExternalLabeledDot(
            Dot( arrow_biu.arrow.get_end(), z_index=2),
            MathTex("au + biu", tex_to_color_map=color_map)
        )
        self.play( dot_uv.create_animation() )

        arrow_uv = Arrow( ORIGIN, dot_uv.dot.get_center(), color=YELLOW, buff=0 )
        angle_uv = Angle( arrow_u.arrow, arrow_uv, radius=1, color=YELLOW )

        self.play( GrowArrow(arrow_uv), Create(angle_uv) )
        self.wait()

        self.play( animate_replace_tex( dot_uv.label, "u(a + bi)", color_map ) )
        self.wait()

        rotation_group.add( dot_uv.dot, arrow_uv, angle_uv, arrow_au.arrow, arrow_biu.arrow )

        # for _delta_angle in [ PI / 8, -PI / 8 ]:
        #     self.play( Rotate( rotation_group, _delta_angle, about_point=ORIGIN ), run_time=1.5 )
        # self.wait(0.5)

        self.play( 
            Rotate( rotation_group, -u_angle, about_point=ORIGIN ),
            animate_replace_tex( dot_uv.label, "a + bi", color_map ),
            animate_replace_tex( arrow_au.label, "a", color_map ),
            animate_replace_tex( arrow_biu.label, "bi", color_map ),
            run_time=1.5
        )
        self.wait(1)
        self.play(
            Rotate( rotation_group, u_angle, about_point=ORIGIN ),
            animate_replace_tex( dot_uv.label, "u(a + bi)", color_map ),
            animate_replace_tex( arrow_au.label, "au", color_map ),
            animate_replace_tex( arrow_biu.label, "biu", color_map ),
            run_time=1.5
        )
        self.wait(.5)

        angle_u.clear_updaters()
        rotation_group.add(angle_u)
        self.play( rotation_group.animate.scale(0.5, about_point=ORIGIN) )
        self.play( rotation_group.animate.scale(2, about_point=ORIGIN) )

        self.play( animate_replace_tex( dot_uv.label, "uv", color_map ) )
        self.wait()

        self.play(  FadeOut( arrow_iu, numplane_u ) )

        eq_polar_product = MathTex(
            r"(r_{u}, \theta_{u})(r_{v}, \theta_{v}) = (r_{u}r_{v}, \theta_{u} + \theta_{v})",
            tex_to_color_map=color_map)
        eq_polar_product.to_corner(UL)
        self.play( Write(eq_polar_product) )

def get_angle_comparison(arrow_ref, angle, color=WHITE):
    arrow_base = arrow_ref.copy()
    arrow_base.set_opacity(0.5)
    arrow_rot = arrow_ref.copy().rotate(angle, about_point=arrow_ref.get_start())
    elbow = math.fabs(math.fabs(angle) - PI / 2) < 0.00001
    angle = Angle(arrow_base, arrow_rot, radius=0.5, elbow=elbow, color=color)
    return VDict([ ("arrow", arrow_base), ("angle", angle) ])#.set_z_index(-1)