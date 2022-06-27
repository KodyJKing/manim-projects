import math
from manim import *
from manim.utils.space_ops import ( 
    quaternion_mult as qmul,
    quaternion_from_angle_axis as aa2q,
    angle_axis_from_quaternion as q2aa,
    quaternion_conjugate as qconj
)
import numpy as np
from lib.ComplexArrow import ComplexArrow, ComplexProduct

from lib.ExternalLabeledDot import ExternalLabeledDot
from lib.LabeledArrow import LabeledArrow
from lib.TransformMatchingKeyTex import TransformMatchingKeyTex, set_transform_key
from lib.mathutils import clamp, rotate_cc, rotate_cw, smoothstep
from lib.utils import angle_label_pos, animate_arc_to, animate_replace_tex, colored_math_tex, compose_colored_tex

c1 = np.array([1, 0, 0])
ci = np.array([0, 1, 0])

blank_axis = { "include_ticks": False }

def get_shift( mobj, other ):
    return other.get_center() - mobj.get_center()
def eq_shift( eq: MathTex, other: MathTex ):
    return get_shift( eq.get_part_by_tex("="), other.get_part_by_tex("=") ) * RIGHT
def align_eqs(eq: MathTex, *others: MathTex):
    for other in others:
        other.shift( eq_shift(other, eq) )

class Intro(ThreeDScene):
    def construct(self):
        title = Tex("Imaginary Numbers").to_corner(UL)
        self.play(Write(title))

        # Introduce definition
        eqn0 = MathTex("\sqrt{-x}", "=", "\sqrt{", "-1", "\cdot", "x", "}")
        eqn0b = MathTex("\sqrt{-x}", "=", "\sqrt{", "-1", "}", "\sqrt{", "x", "}")
        eqn0c = MathTex("\sqrt{-x}", "=", "\sqrt{-1}", "\sqrt{x}")
        eqn0d = MathTex("\sqrt{-x}", "=", "i", "\sqrt{x}")
        eqn1 = MathTex( "i", "=", "\sqrt{-1}" )
        eqn2 = MathTex( "i^2", "=", "\sqrt{", "-1", "}^2" )
        eqn2b = MathTex( "i^2", "=", "-1" )

        eqn1.next_to(eqn0, DOWN)
        eqn2.next_to(eqn1, DOWN)
        eqn0b.move_to(eqn0)
        eqn0c.move_to(eqn0)
        eqn0d.move_to(eqn0)
        eqn2b.move_to(eqn2)

        eqns = VGroup(eqn0, eqn0b, eqn0c, eqn0d, eqn1, eqn2, eqn2b).move_to(ORIGIN)
        align_eqs(*eqns)

        self.play( Write(eqn0[0]) )
        self.wait()
        self.play( Write( VGroup( *eqn0[1:] ) ) )

        eqns.remove(eqn0)
        self.play( TransformMatchingTex( eqn0, eqn0b ) )
        self.wait()
        eqns.remove(eqn0b)
        self.play( TransformMatchingTex( eqn0b, eqn0c ), run_time=0.01 )

        self.play( Write(eqn1) )

        eqns.remove(eqn0c)
        self.play( TransformMatchingTex( eqn0c, eqn0d ) )
        
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
        title = Tex("Complex Numbers").to_corner(UL)
        self.play(Write(title))

        color_map = { 
            "a": RED, "b": GREEN,
            "arg": WHITE,
        }
        tex_config = { "tex_to_color_map": color_map }
        axes = Axes( x_axis_config=blank_axis, y_axis_config=blank_axis, x_length=20, y_length=10, tips=False ).set_z_index(-2)
        numplane = ComplexPlane()
        numplane.set_z_index(-1).get_coordinate_labels()
        coords = VGroup( numplane.get_coordinate_labels(), numplane.get_coordinate_labels(0) )
        self.play( Create(axes), Create(coords) )
        self.wait()

        self.play(Create(numplane))
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
        self.play(FadeOut(arrow_a, arrow_b), FadeOut(numplane), background.animate.set_opacity(0.125))
        
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

        self.play( 
            # FadeOut(angle_tex, brace, brace_tex),
            FadeOut(brace, brace_tex),
            FadeIn(arrow_a, arrow_b), axes.get_axis(1).animate.set_opacity(1),
            animate_replace_tex(angle_tex, "\\theta")
        )
        self.wait()

        # Define conjugate
        self.play( FadeOut(title) )
        title = Tex("Conjugate").to_corner(UL)
        self.play( Write(title) )
        self.wait()

        conjugate_parts = VGroup(
            arrow_b_conj := arrow_b.copy(), 
            arrow_v_conj := arrow_v.copy(), 
            angle_conj   := angle.copy()
        )
        self.add(conjugate_parts)
        
        self.play(Rotate(conjugate_parts, PI, RIGHT, ORIGIN))
        self.play(VGroup(arrow_v_conj, angle_conj).animate.set_color(BLUE))
        self.wait()
        
        dot_conjugate = ExternalLabeledDot(Dot(v*RIGHT -v*UP), MathTex("a - bi", **tex_config), direction=DR)
        dot_conjugate.set_z_index(-1)
        self.play( dot_conjugate.create_animation() )
        self.wait()

        eq_conjugate = MathTex("\\overline{a+bi}=a-bi").next_to(title, DOWN, aligned_edge=LEFT)
        self.play(Write(eq_conjugate))
        self.wait()

        # Arg of conjugate z is negative arg z
        angle_tex_conj = MathTex("-\\theta", color=BLUE).move_to(angle_tex.get_center() * np.array([1, -1, 1]))
        self.play(Write(angle_tex_conj))
        eq_conjugate_arg = MathTex("arg(\\overline{z}) = -arg(z)").next_to(eq_conjugate, DOWN, aligned_edge=LEFT)
        self.play(Write(eq_conjugate_arg))

        indices = index_labels(eq_conjugate)
        self.add(indices)

        self.wait()

class ComplexAdditionAndScaling(Scene):
    def construct(self):
        dot = Dot().set_z_index(10)

        u = RIGHT * 3 + UP
        v = LEFT * 2 + UP
        w = u + v

        arrow_u = LabeledArrow(
            Arrow(ORIGIN, u, buff=0, color=BLUE), MathTex("u", color=BLUE),
            distance=0, perp_distance=0.35, alpha=0.5
        )
        arrow_v = LabeledArrow(
            Arrow(ORIGIN, v, buff=0, color=YELLOW), MathTex("v", color=YELLOW),
            distance=0, perp_distance=-0.35, alpha=0.5
        )
        arrow_w = LabeledArrow(
            Arrow(ORIGIN, w, buff=0, color=GREEN), MathTex("u + v", tex_to_color_map={"u":BLUE,"v":YELLOW}),
            distance=0, perp_distance=0.35, alpha=0.75,
            aligned_edge=RIGHT
        )

        self.add(dot, arrow_u, arrow_v)
        self.wait()
        self.play(arrow_v.animate.shift(u))
        self.play(arrow_w.grow_animation())
        self.wait()

        self.play(FadeOut(arrow_u, arrow_v, arrow_w))

        x = RIGHT + UP
        s_tracker = ValueTracker(1)

        arrow_x = LabeledArrow(
            Arrow(ORIGIN, x, buff=0, color=BLUE), MathTex("u", color=BLUE),
            distance=0, perp_distance=0.35, alpha=0.5
        ).set_z_index(1)

        def get_scaled():
            s = s_tracker.get_value()
            opacity = smoothstep(1, 1.5, s)
            return LabeledArrow(
                Arrow(ORIGIN, s * x, buff=0, color=BLUE_A),
                VGroup(DecimalNumber(s).scale(0.75), MathTex("u", color=BLUE))
                    .arrange(buff=1/16).set_opacity(opacity),
                distance=0.35
            )

        arrow_sx = always_redraw(get_scaled)

        self.play(FadeIn(arrow_x))
        self.add(arrow_sx)
        self.wait()
        self.play(s_tracker.animate.set_value(2))
        self.wait()

class AlgebraicProps(Scene):
    def is_quaternion_scene(self):
        return False
        
    def construct(self):
        color_map = { "x": BLUE, "y": GREEN, "z": RED }

        def math_tex(*text, isolate=[], **kwargs):
            return colored_math_tex(*text, t2c=color_map, **kwargs)

        def sideline(mobj: Mobject):
            ul = mobj.get_corner(UL)
            dl = mobj.get_corner(DL)
            return Line(ul, dl), mobj

        is_quat = self.is_quaternion_scene()
        number_system = "Quaternion" if is_quat else "Complex Number"
        commutative_multiplication_condition = r"\text{ if } x \text{ or } y \text{ are real}" if is_quat else ""

        title = Tex(r"\underline{ " + number_system + r" Algebra}")
        title.to_corner(UL)
        self.add(title)

        field_blurb = MathTex(
            r"""&\text{Complex numbers follow the same addition}
            \\&\text{and multiplication rules as real numbers.}
            \\&\text{These rules are called the field axioms.}""",
            color=GRAY_A
        )
        field_blurb.scale(1/2).to_corner(UR)

        table_properties = VGroup(
            Tex("Associativity"), *sideline(math_tex(r"x + (y + z) &= (x + y) + z \\ x(y z) &= (x y)z")),
            Rectangle(BLACK, 1, 0.5),
            Tex("Commutativity"), *sideline(tex_commute := math_tex(r"x + y &= y + x \\ x y &= y x" + commutative_multiplication_condition)),

            Tex(r"Identity"), *sideline(math_tex(r"x + 0 &= x \\ x \cdot 1 &= x")),
            Rectangle(BLACK, 1, 0.5),
            Tex(r"Inverse"),  *sideline(math_tex(r"x + (-x) &= 0 \\ x \cdot \frac{1}{x} &= 1 \text{ if } x \neq 0")),

            Tex("Distributivity"), *sideline(math_tex(r"x (y + z) &= x y + x z \\ (x + y) z &= x z + y z")),
        ).arrange_in_grid(3, 7, col_alignments="rclcrcl", buff=(0.25, 0.5)).scale(2/3)

        self.add(table_properties)
        self.wait()

        if is_quat:
            # self.add(index_labels(tex_commute))
            self.play(Create(Underline(tex_commute[13:], color=RED)))
        else:
            self.play(Write(field_blurb))
        self.wait()

class RotationPreview(Scene):
    def construct(self):
        u_angle = PI/2 * 1.25
        # u_modulus = 1.3
        u_modulus = 0.8
        u = (math.cos(u_angle) + 1j * math.sin(u_angle)) * u_modulus
        v = 2 + 1j

        title = Tex("Complex Multiplication").to_corner(UL)
        self.add(title)
        
        cprod = ComplexProduct(u, v)
        cprod.move_to(ORIGIN + UP)
        self.play(FadeIn(cprod))
        self.wait()
        cprod.animate(self)

        color_map = {"u":BLUE, "v":YELLOW}
        label_rotation = Tex("Rotation rule: ")
        label_scaling = Tex("Scaling rule: ")
        label_commutativity = Tex("Commutativity: ")
        eq_rotation = MathTex(*"arg(uv) = arg(u)+arg(v)".split(" "), tex_to_color_map=color_map)
        eq_scaling = MathTex(*"|uv| = |u||v|".split(" "), tex_to_color_map=color_map)
        eq_commutativity = MathTex(*"uv = vu".split(" "), tex_to_color_map=color_map)

        table = VGroup(
            label_rotation, eq_rotation,
            label_scaling, eq_scaling,
            label_commutativity, eq_commutativity
        )
        table.arrange_in_grid(len(table) // 2, 2, (1, .25), LEFT)

        row_commutativity = VGroup(label_commutativity, eq_commutativity)
        row_commutativity.set_opacity(0)

        align_eqs(eq_rotation, eq_scaling, eq_commutativity)
        table.next_to(cprod.equation, DOWN, buff=1)
        self.play(Write(table))
        self.wait()

        cprod2 = ComplexProduct(v, u, u_color=YELLOW, v_color=BLUE)
        cprod2.move_to(ORIGIN + UP)
        self.play( 
            animate_arc_to( cprod.arrow_v, cprod2.arrow_u ),
            animate_arc_to( cprod.arrow_u, cprod2.arrow_v ),
            animate_arc_to( cprod.tex_times, cprod2.tex_times ),
        )
        self.play(FadeOut(cprod), FadeIn(cprod2), run_time=0.5)
        self.wait()
        cprod2.animate(self)

        # row_commutativity.set_opacity(1)
        # self.play(Write(row_commutativity))

        # operations = [ VGroup(*eq[5:]) for eq in [eq_rotation, eq_scaling] ]
        # rects = [ SurroundingRectangle(op) for op in operations ]
        # self.play(
        #     LaggedStart( *[Create(rect) for rect in rects], lag_ratio=0.1 ),
        #     run_time=1 )
        # self.wait()
        # self.play(
        #     LaggedStart(*[FadeOut(rect) for rect in rects], lag_ratio=0.1),
        #     run_tim=1 )

        self.wait()

class ActionOfI(Scene):
    def construct(self):
        color_map = {"a":RED, "b":GREEN, "u": BLUE}

        def math_tex(*text, **kwargs):
            return MathTex(*text, tex_to_color_map=color_map, **kwargs)

        def rotate_by_i(mobj, about_point=ORIGIN):
            return Rotate(mobj, PI/2, about_point=about_point)

        title = Tex("Action of i")
        title.to_corner(UL)

        numplane = ComplexPlane(x_range=[-10, 10], y_range=[-10, 10])
        numplane.set_opacity(0.25).set_z_index(-10)
        dot = Dot().set_z_index(10)

        equation1 = math_tex(*"i ( a + b i )".split(" "))
        equation1.next_to(equation1, DOWN, buff=1)
        equation_background = SurroundingRectangle(equation1, color=WHITE).set_fill(BLACK, 1).set_z_index(-1)
        
        u = 3 * c1 + 2 * ci
        iu = rotate_cc(u)
        arrow_ua = LabeledArrow(
            Arrow(ORIGIN, u * RIGHT, buff=0, color=RED),
            math_tex("a"),
            perp_distance=-0.35, distance=0, alpha=0.5
        )
        arrow_ub = LabeledArrow(
            Arrow(u * RIGHT, u, buff=0, color=GREEN),
            math_tex("bi"),
            perp_distance=-0.35, distance=0, alpha=0.5
        )

        arrow_u = Arrow(ORIGIN, u, buff=0, color=BLUE)
        arrow_iu = Arrow(ORIGIN, iu, buff=0, color=BLUE)
        angle_u_iu = Angle(arrow_u, arrow_iu, elbow=True, color=BLUE)

        dot_u = ExternalLabeledDot(
            Dot(u),
            math_tex("a + bi"),
            normalize(u)
        )
        dot_iu = ExternalLabeledDot(
            Dot(iu),
            math_tex("-b + ai"),
            normalize(iu)
        )

        self.add(dot, numplane)
        self.play(Write(title))

        self.wait()

        self.play(dot_u.create_animation())
        self.play(arrow_ua.grow_animation())
        self.play(arrow_ub.grow_animation())

        self.play( Write(equation1) )
        self.play( Create(equation_background) )
        self.wait()
        self.play( TransformMatchingTex( 
            equation1, 
            equation2 := math_tex(*"a i + b i i".split(" ")).move_to(equation1),
            shift=ORIGIN
        ) )
        self.add(equation3 := math_tex(*"a i + b ii".split(" ")).move_to(equation1))
        self.remove(equation2)
        self.play( TransformMatchingTex( 
            equation3, 
            equation4 := math_tex(*"a i - b".split(" ")).move_to(equation3),
            shift=ORIGIN, key_map={"ii":"-"}
        ) )

        arrow_uai = arrow_ua.copy()
        arrow_ubi = arrow_ub.copy()

        self.add(arrow_uai, arrow_ubi)
        self.remove(arrow_ua, arrow_ub)

        self.play( arrow_uai.animate_relabel( math_tex("a", "i") ) )
        self.play(rotate_by_i(arrow_uai.arrow))
        self.play( arrow_ubi.animate_relabel( math_tex("b", "i", "i") ) )
        arrow_ubi.relabel(math_tex("b", "ii"), scene=self)
        self.play( arrow_ubi.animate_relabel( math_tex("-", "b"), key_map={"ii":"-"} ) )
        self.play(rotate_by_i(arrow_ubi.arrow, about_point=arrow_ubi.arrow.get_start()))
        self.play( arrow_ubi.arrow.animate.shift(
            arrow_uai.arrow.get_end() - arrow_ubi.arrow.get_start()
        ) )
        self.play(dot_iu.create_animation())
        self.wait()

        self.play(FadeIn(arrow_ua, arrow_ub))

        rotation_group = VGroup(
            arrow_ua.arrow.copy(),
            arrow_ub.arrow.copy(),
        )

        self.play(rotate_by_i(rotation_group), rotate_by_i(numplane))

        self.play(FadeOut( rotation_group, arrow_ua, arrow_ub, arrow_uai, arrow_ubi, equation4, equation_background ))

        self.play(
            GrowArrow(arrow_u), GrowArrow(arrow_iu),
            dot_u.animate_relabel(math_tex("u")), dot_iu.animate_relabel(math_tex("iu")),
            Create(angle_u_iu)
        )

        self.wait()

class ArbitraryTimesArbitrary2(MovingCameraScene):
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
            perp_distance=-0.25, distance=0, alpha=0.75
        ).set_z_index(1)
        arrow_iu = LabeledArrow(
            Arrow( ORIGIN, iu, buff=0, color=BLUE_E ),
            MathTex("iu", color=BLUE_E),
            perp_distance=0.35, distance=0, alpha=0.75
        ).set_z_index(1)

        line_re = Line(ORIGIN, RIGHT)
        line_u = Line(ORIGIN, u * 10, color=BLUE )
        angle_u = always_redraw( lambda: Angle( line_re, arrow_u.arrow, color=BLUE ) )

        self.play( arrow_u.grow_animation() )

        angle_u.suspend_updating()
        self.play( Create( angle_u ) )
        angle_u.resume_updating()

        self.wait(1)
        self.play( arrow_iu.grow_animation() )
        # for arrow in [arrow_u, arrow_iu]:
        self.wait(0.5)

        # self.play( Create( numplane_u ) )
        self.play( FadeIn( numplane_u ) )
        self.wait()

        rotation_group = VGroup(arrow_u.arrow, arrow_iu.arrow, numplane_u)

        # Demonstrate rotation of plane by u
        for _delta_angle in [ PI / 4, -PI / 4 -u_angle, u_angle ]:
            self.play( Rotate( rotation_group, _delta_angle, about_point=ORIGIN ), run_time=1.5 )
        self.wait()
        # Demonstrate scaling of plane by u
        self.play( rotation_group.animate.scale(0.5, about_point=ORIGIN), run_time=1.5 )
        self.play( rotation_group.animate.scale(2, about_point=ORIGIN), run_time=1.5 )
        self.wait()

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
            # MathTex("au + biu", tex_to_color_map=color_map)
            compose_colored_tex(
                RED, "a", BLUE, "u", WHITE, "+",
                GREEN, "b", BLUE_E, "i", BLUE_E, "u"
            )
        )
        self.play( dot_uv.create_animation() )

        arrow_uv = Arrow( ORIGIN, dot_uv.dot.get_center(), color=YELLOW, buff=0 )
        angle_uv = Angle( arrow_u.arrow, arrow_uv, color=YELLOW )

        self.play( GrowArrow(arrow_uv), Create(angle_uv) )
        self.wait()

        self.play( dot_uv.animate_relabel( 
            MathTex(*"u ( a + b i )".split(" "), tex_to_color_map=color_map),
            path_arc=90*DEGREES
        ) )
        self.wait()

        rotation_group.add( dot_uv.dot, arrow_uv, angle_uv, arrow_au.arrow, arrow_biu.arrow )

        self.play( 
            Rotate( rotation_group, -u_angle, about_point=ORIGIN ),
            run_time=1.5
        )
        self.play(
            dot_uv.animate_relabel(
                MathTex(*"a + b i".split(" "), tex_to_color_map=color_map),
                shift=DOWN
            ),
            animate_replace_tex( arrow_au.label, "a", color_map ),
            animate_replace_tex( arrow_biu.label, "bi", color_map ),
        )
        self.wait()
        self.play(
            dot_uv.animate_relabel( 
                MathTex(*"u ( a + b i )".split(" "), tex_to_color_map=color_map),
                shift=DOWN
            ),
            animate_replace_tex( arrow_au.label, "au", color_map ),
            animate_replace_tex( arrow_biu.label, "biu", color_map ),
        )
        self.wait()
        self.play( Rotate( rotation_group, u_angle, about_point=ORIGIN ), run_time=1.5)
        self.wait(.5)

        angle_u.clear_updaters()
        rotation_group.add(angle_u)
        self.play( rotation_group.animate.scale(0.5, about_point=ORIGIN), run_time=1.5 )
        self.play( rotation_group.animate.scale(2, about_point=ORIGIN), run_time=1.5 )
        self.wait()

        self.play( animate_replace_tex( dot_uv.label, "uv", color_map ) )
        self.wait()

        self.play(  FadeOut( arrow_iu, numplane_u ) )

        eq_polar_product = MathTex(
            r"arg(uv) &= arg(u) + arg(v) \\ |uv| &= |u||v|",
            tex_to_color_map={"u":BLUE, "v":YELLOW})
        eq_polar_product.to_corner(UL)
        self.play( Write(eq_polar_product) )

class UnitComplexNumbers(Scene):
    def construct(self):
        numplane = ComplexPlane()
        numplane.add_coordinates()
        numplane.set_opacity(0.25)
        numplane.set_z_index(-10)
        self.add(numplane)

        title = Tex("Pure Rotations:")
        title.to_corner(UL)
        self.add(title[0])

        tex_mod_equals_one = MathTex("|u| = 1")
        tex_mod_equals_one.next_to(title, DOWN, 0.5, aligned_edge=LEFT)
        self.play(Write(tex_mod_equals_one))
        self.wait()

        circle = Circle(1, BLUE)
        circle.set_z_index(-1)
        self.play(Create(circle))

        line_re = Line(ORIGIN, RIGHT)
        line_re.set_z_index(-2)
        self.play(Create(line_re))

        theta_tracker = ValueTracker(45*DEGREES)
        def get_dot(label_text, sign=1):
            def func():
                theta = theta_tracker.get_value() * sign
                u = np.cos(theta) * RIGHT + np.sin(theta) * UP
                dot = Dot(u)
                line = Line(ORIGIN, u)
                line_re = Line(ORIGIN, RIGHT)
                angle = Angle(line_re, line, radius=0.25, other_angle=theta<0)
                theta_text = "\\theta" if sign > 0 else "-\\theta"
                label_theta = MathTex(theta_text).scale(.8).move_to(angle.get_midpoint() * 2)
                label = MathTex(label_text).next_to(dot, u, buff=0.1)
                result = VDict({
                    "dot": dot, "line": line, "angle": angle,
                    "label_theta": label_theta, "label": label
                })
                return result
            return func
        
        dot_u = always_redraw(get_dot("u"))

        self.play(Create(dot_u))
        self.play(theta_tracker.animate.set_value(135*DEGREES))

        tex_form = MathTex("u = cos(\\theta) + i sin(\\theta)", tex_to_color_map={"cos":RED, "sin":GREEN})
        tex_form.next_to(tex_mod_equals_one, DOWN, aligned_edge=LEFT)
        self.play(Write(tex_form))

        dot_uconj = always_redraw(get_dot("\\overline{u}", -1))
        self.play(Create(dot_uconj))
        self.wait()

        self.play(theta_tracker.animate.set_value(75*DEGREES))

        tex_inverse = MathTex("u^{-1}", "= \\overline{u}")
        tex_inverse.next_to(tex_form, DOWN, aligned_edge=LEFT)
        self.play(Write(tex_inverse))

        tex_inverse2 = MathTex("u \\overline{u} = 1")
        tex_inverse2.next_to(tex_inverse, DOWN, aligned_edge=LEFT)
        self.play(Write(tex_inverse2))
