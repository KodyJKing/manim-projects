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
from lib.TexContainer import TexContainer
from lib.ExternalLabeledDot import ExternalLabeledDot
from lib.LabeledArrow import LabeledArrow
from lib.TransformMatchingKeyTex import TransformMatchingKeyTex, set_transform_key
from lib.mathutils import clamp, rotate_cc, rotate_cw, smoothstep
from lib.utils import angle_label_pos, animate_arc_to, animate_replace_tex, colored_math_tex, colored_tex, compose_colored_tex, fallback_mobj

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

def polar2xy(theta, radius=1):
    return RIGHT * np.cos(theta) * radius + UP * np.sin(theta) * radius

class Intro(ThreeDScene):
    def construct(self):
        scene_color_map = { "a": RED, "b": GREEN }

        def get_tex(*strings, **kwargs):
            return colored_math_tex(*strings, t2c=scene_color_map, **kwargs)

        exposition1 = VGroup(
            Tex(
                r"A complex number is the sum of a real number and an imaginary number.",
                tex_to_color_map={"real number": RED, "imaginary number": GREEN}
            ),
            VGroup(
                Tex( "They can be written in the form" ),
                get_tex("a + b i \\text{,}"),
                Tex("where $a$ and $b$ are real numbers", tex_to_color_map={"$a$": RED, "$b$": GREEN})
            ).arrange(),
            Tex(
                "and $i$ is $\sqrt{-1}$, the \"imaginary unit\"."
            )

        ).arrange(DOWN, aligned_edge=LEFT).scale(2/3).to_corner(UL)

        self.play(Write(exposition1), run_time=4)

        equations = VGroup(
            tex_form := get_tex(r"a + b i"),
            tex_ident := get_tex(r"i = \sqrt{-1}", words=["i", "=", "-1"]),
            tex_ident2 := get_tex(r"i^2 = -1", words=["i", "=", "-1"]),
        ).arrange(DOWN)

        self.play(Write(tex_form))
        self.next_section()


        self.play(Write(tex_ident))
        self.wait()
        self.play(TransformMatchingTex(tex_ident.copy(), tex_ident2, shift=ORIGIN))

        self.wait(2)

        self.play(FadeOut(exposition1))
        exposition3 = VGroup(
            line1 := Tex("You can see that $i$ is not a real number by looking at a plot of $y=x^2$."),
            line2 := Tex("No value on the real number line squares to a negative.")
        ).arrange(DOWN, aligned_edge=LEFT).scale(2/3).to_corner(UL)
        self.play(Write(line1))

        # Demonstrate absence of i on real number line
        axes = Axes( tips=False, x_range=[-3, 3], y_range=[-3, 9], x_length=4, y_length=4 )
        axes.set_opacity(0)
        self.play( VGroup( equations, axes ).animate.arrange(buff=2) )
        axes.set_opacity(1)
        square_graph = axes.plot( lambda x: x * x, color=BLUE )
        self.play( Create(axes), Create(square_graph) )
        self.play(Write(line2))
        self.play( Indicate( axes.get_axis(0) ) )
        self.next_section()

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
        self.play( x_tracker.animate.set_value(0), run_time=2 )
        self.wait()
        self.next_section()

        self.play(FadeOut(exposition3))
        exposition4 = VGroup(
            line1 := Tex("You can think of imaginary numbers as lying on a separate number line"),
            line2 := Tex("the imaginary number line.")
        ).arrange(DOWN, aligned_edge=LEFT).scale(2/3).to_corner(UL)

        self.play(Write(line1))

        # New axis
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
        self.play(Write(line2))
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

        self.wait()

        exposition5 = VGroup(
            line1 := Tex("Since a complex number has two components,"),
            line2 := Tex("a real one", " and an imaginary one,",
                tex_to_color_map={"real": RED, "imaginary": GREEN}),
            line3 := Tex("they can be thought of as 2D vectors."),
        ).arrange(DOWN, aligned_edge=LEFT).scale(2/3)

        VGroup(
            exposition5,
            tex_form_target := tex_form.copy()
        ).arrange(buff=2).to_edge(LEFT)
        
        self.play(
            FadeOut( exposition4, axes, axes_im, square_graph, square_graph_im, dots, tex_ident, tex_ident2 ),
            tex_form.animate.move_to(tex_form_target)
        )

        part_a = tex_form[0]
        part_b = tex_form[2:]

        part_real = line2[0:3]
        part_imag = line2[3:]

        self.play(Write(line1))
        self.play(Write(part_real))
        self.play(Indicate(part_a))
        self.play(Write(part_imag))
        self.play( Indicate(part_b))
        self.play(Write(line3))

        tex_arrow = MathTex(r"\Leftrightarrow")
        tex_vector = MathTex(r"\begin{bmatrix}a\\b\end{bmatrix}")
        group_veclike = VGroup(tex_arrow, tex_vector).arrange().next_to(tex_form, RIGHT)
        self.play(Write(group_veclike))

        self.wait()

class ComplexNumbers(Scene):
    def construct(self):
        color_map = { 
            "a": RED, "b": GREEN,
            "arg": WHITE,
        }
        tex_config = { "tex_to_color_map": color_map }
        axes = Axes( x_axis_config=blank_axis, y_axis_config=blank_axis, x_length=20, y_length=10, tips=False ).set_z_index(-2)
        numplane = ComplexPlane().set_opacity(0.5)
        numplane.set_z_index(-1).get_coordinate_labels()
        coords = VGroup( numplane.get_coordinate_labels(), numplane.get_coordinate_labels(0) )

        # self.play( Create(axes), Create(coords) )
        # self.wait()
        # self.play(Create(numplane))
        # self.wait()

        exposition1 = VGroup(
            Tex("Because complex numbers are 2D in a sense,"),
            Tex("it helps to visualize them in the complex plane.", tex_to_color_map={"complex plane": YELLOW}),
        ).arrange(DOWN).scale(2/3)
        self.play(Write(exposition1), run_time=2)

        self.wait(2)
        
        self.play(
            FadeOut(exposition1),
            FadeIn(axes, coords, numplane)
        )

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

        exposition2 = VGroup(
            Tex("We can express complex numbers in polar form...")
        ).scale(2/3).to_corner(UL)
        self.play(Write(exposition2))
        
        # Define arg and modulus
        exposition3 = Tex("They have length,").scale(2/3).next_to(exposition2, DOWN, 1, LEFT).shift(RIGHT)
        self.play(Write(exposition3))
        
        brace = Brace(arrow_v, direction=arrow_v.copy().rotate(PI/2).get_unit_vector() )
        brace_tex = MathTex("r")
        brace.put_at_tip(brace_tex, False)
        self.play(Create(brace), Write(brace_tex))
        self.wait()

        exposition4 = Tex("and direction.").scale(2/3).next_to(exposition3, DOWN)
        self.play(Write(exposition4))

        angle = Angle(arrow_a, arrow_v, 1 ).set_z_index(-1)
        angle_tex = MathTex("\\theta" ).move_to(angle_label_pos(arrow_a, arrow_v, 1 + 3 * SMALL_BUFF))
        self.play( Create(angle), Write(angle_tex) )
        self.wait()

        self.play(FadeOut(exposition3, exposition4))

        exposition5 = Tex(
            "This length is called the number's modulus,",
            tex_to_color_map={"modulus":YELLOW}
        ).scale(2/3).move_to(brace_tex).to_edge(LEFT).shift(UP*0.5)
        self.play(Write(exposition5))

        self.play(animate_replace_tex(brace_tex, "|a+bi|", color_map, RIGHT))
        self.wait()

        exposition6 = Tex(
            "and this angle is its argument.",
            tex_to_color_map={"argument":YELLOW}
        ).scale(2/3).next_to(angle_tex, DOWN, 0.75)
        self.play(Write(exposition6))

        arg_tex = MathTex("arg", "(a+bi)", **tex_config)
        arg_tex[0].set_color(WHITE)
        self.play(animate_replace_tex(angle_tex, arg_tex))
        self.wait()

class ComplexAdditionAndScaling(Scene):
    def construct(self):

        scene_color_map = {
            "a": RED, "b": GREEN,
            "c": RED_E, "d": GREEN_E,
        }

        def get_tex(*strings, **kwargs):
            return colored_math_tex(*strings, t2c=scene_color_map, **kwargs)

        exposition1 = VGroup(
            line1 := Tex("Like vectors, you can add complex numbers component by component,"),
            line2 := Tex("or you can visually add them tip-to-tail.")
        ).arrange(DOWN).scale(2/3).to_edge(UP)

        self.play(Write(line1))

        VGroup(
            tex_u := MathTex("3", "+", "1i", tex_to_color_map={"3": RED, "1": GREEN}),
            tex_v := MathTex("2", "+", "1i", tex_to_color_map={"2": RED, "1": GREEN}),
            tex_w := MathTex("5", "+", "2i", tex_to_color_map={"5": RED, "2": GREEN}),
        ).arrange(DOWN)

        add_op = VGroup(
            MathTex("+").next_to(tex_v, LEFT, 0.25),
            Underline(tex_v)
        )

        self.play(Write(VGroup(tex_u, tex_v, add_op)))

        self.play(
            Create(
                rect := SurroundingRectangle( VGroup(tex_u[0], tex_w[0]) )
            )
        )

        self.play(Write(tex_w[0]))

        self.play(
            rect.animate.become(
                SurroundingRectangle( VGroup(tex_u[2:], tex_w[2:]) )
            )
        )

        self.play(Write(tex_w[1:]))
        self.play(FadeOut(rect))

        self.play(
            ReplacementTransform( tex_u,  tex_u := get_tex("a + b i").move_to(tex_u, aligned_edge=LEFT) ),
            ReplacementTransform( tex_v,  tex_v := get_tex("c + d i").move_to(tex_v, aligned_edge=LEFT) ),
            ReplacementTransform( tex_w,  tex_w := get_tex("(a + c) + (b + d) i").scale(2/3).move_to(tex_w) ),
        )

        self.play(Write(line2))
        self.play(FadeOut(add_op, tex_u, tex_v, tex_w))

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

        self.play(FadeIn(dot, arrow_u, arrow_v))
        self.wait()
        self.play(arrow_v.animate.shift(u))
        self.play(arrow_w.grow_animation())
        self.wait()

        self.play(FadeOut(arrow_u, arrow_v, arrow_w, dot, exposition1))

        exposition2 = VGroup(
            line1 := Tex("Unlike vectors, you can also multiply complex numbers."),
            line2 := Tex("First distrubute the terms and replace $i^2$ with $-1$."),
            line3 := Tex("Then group the real and imaginary terms."),
        ).arrange(DOWN).scale(2/3).to_edge(UP)
        self.play(Write(line1))

        VGroup(
            step1 := get_tex("(a + b i) (c + d i)"),
            step2 := get_tex("a c + a d i + b c i + b d i^2"),
            step3 := get_tex("(a c - b d) + (a d + b c)i"),
        ).arrange(DOWN)
        step2b = get_tex("a c + a d i + b c i + b d (-1)").move_to(step2)

        self.play(Write(step1))

        self.play(Write(line2))
        self.play( TransformMatchingTex( step1.copy(), step2 ) )
        self.play( TransformMatchingTex( step2, step2b ) )

        self.play(Write(line3))

        self.play( TransformMatchingTex( step2b.copy(), step3 ) )
        self.wait()

        mult_eqn = VGroup( step1, equal_sign := MathTex(" = ").set_opacity(0), step3 )

        self.play( FadeOut(step2b), mult_eqn.animate.arrange() )
        self.play(Write(equal_sign.set_opacity(1)))
        self.wait()

        self.play(FadeOut(exposition2))

        exposition3 = Tex("This is great for computation, but a more visual intuition would be nice...").scale(2/3).to_edge(UP)
        self.play(Write(exposition3))
        self.wait()

        self.play(FadeOut(exposition3, mult_eqn))
        
        # sum_eqn = get_tex("(a + b i) + (c + d i) = (a + c) + (b + d) i").next_to(mult_eqn, UP)

        # exposition3 = Tex("These addition and multiplication rules allow us to do algebra with complex numbers like we do with real numbers.")
        # exposition3.scale(2/3).to_edge(UP)
        # self.play(FadeIn(sum_eqn))
        # self.play(Write(exposition3))

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

        title = Tex(number_system + r" Algebra")
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
        color_map = {"u":BLUE, "v":YELLOW}

        u_angle = PI/2 * 1.25
        # u_modulus = 1.3
        u_modulus = 0.8
        u = (math.cos(u_angle) + 1j * math.sin(u_angle)) * u_modulus
        v = 2 + 1j

        # title = Tex("Complex Multiplication").to_corner(UL)
        # self.add(title)

        exposition1 = Tex(
            r"Remarkably, when we multiply complex numbers, one term gets \\ rotated and scaled by the other like this...",
            tex_to_color_map = {"rotated and scaled": YELLOW}
        )
        exposition1.scale(2/3).to_edge(UP)
        self.play(Write(exposition1))
        
        cprod = ComplexProduct(u, v)
        cprod.move_to(ORIGIN + UP)
        self.play(FadeIn(cprod))
        self.wait()
        cprod.animate(self)

        self.play(FadeOut(exposition1))
        exposition2 = colored_tex(r"That is, v gets rotated by the argument of u\\and scaled by the modulus of u.", t2c=color_map)
        exposition2.scale(2/3).to_edge(UP)
        self.play(Write(exposition2))
        self.wait(1)

        tmp = ComplexProduct(u, v)
        tmp.move_to(ORIGIN + UP)
        self.play(FadeOut(cprod), FadeIn(tmp))
        cprod = tmp
        cprod.animate(self)

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
        self.wait(2)

        self.play(FadeOut(exposition2))
        exposition3 = VGroup(
             colored_tex("The order does not matter because complex multiplication is commutative.", t2c={"commutative":YELLOW}),
             colored_tex("So you can think of it as v rotating and scaling u instead.", t2c=color_map)
        ).arrange(DOWN).scale(2/3).to_edge(UP)
        self.play(Write(exposition3))
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

        self.play(FadeOut(exposition3))
        exposition4 = Tex("Let's take a minute to justify the rotation and scaling rules...").scale(2/3).to_edge(UP)
        self.play(Write(exposition4))

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

class ComponentTimesI(Scene):
    def construct(self):
        exposition1 = Tex(
            r"We can start to get a feel for why complex multiplication\\"\
            r" produces rotation by looking at successive powers of $i$."
        ).scale(2/3)
        self.play(Write(exposition1))
        self.wait()

        # numplane = ComplexPlane().add_coordinates().set_opacity(0.25)
        numplane = ComplexPlane().set_opacity(0.25)

        points = [c1, ci, -c1, -ci]

        steps = [
            x.split(";") for x in [
                "1",
                "1 i;i",
                "i i; i ^2; - 1",
                "- 1 i; - i",
                "- i i; - i ^2; - ( - 1 ); 1",
            ]
        ]
        
        def get_step_player(step_group):
            previous_line = None
            self.add(step_group)

            for step in steps:
                newline = True
                for substep in step:
                    tex = MathTex(*substep.split(" "))
                    if previous_line == None:
                        tex.to_corner(UL).shift(RIGHT)
                        self.play(Write(tex))
                    else:
                        extra_anims = []
                        if newline:
                            tex.next_to(previous_line, DOWN, aligned_edge=LEFT)
                            hbuff = LEFT * 0.5
                            vbuff = DOWN * 0.1
                            arc = CurvedArrow(
                                previous_line.get_edge_center(LEFT)+hbuff+vbuff, 
                                tex.get_edge_center(LEFT)+hbuff-vbuff,
                                tip_length=0.12, color=BLUE
                            )
                            label = MathTex("i", color=BLUE).next_to(arc.get_center(), LEFT)
                            extra_anims.append(Create(arc))
                            extra_anims.append(Write(label))
                            step_group.add(arc, label)
                        else:
                            tex.move_to(previous_line, aligned_edge=LEFT)
                        self.play(
                            TransformMatchingTex(previous_line, tex, shift=DOWN),
                            *extra_anims
                        )
                    self.wait(.25)
                    previous_line = tex
                    newline = False
                step_group.add(previous_line.copy())
                self.remove(previous_line)
                yield

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
        
        self.play(FadeOut(exposition1))
        self.play(FadeIn(numplane))

        # Animate first cycle
        step_group = VGroup()
        step_player = get_step_player(step_group)
        arrow = Arrow(ORIGIN, c1, color=RED, buff=0, z_index=1)
        self.play(
            numplane.animate.set_opacity(.25),
            FadeIn(dots[0], arrow)
        )
        step_player.__next__()
        self.wait()
        for i in range(3):
            step_player.__next__()
            self.play( FadeIn(dots[i + 1]), Rotate(arrow, PI / 2, about_point=ORIGIN), FadeIn(arcs[i]))
            self.wait()
        step_player.__next__()
        self.play(FadeIn(arcs[3]), Rotate(arrow, PI / 2, about_point=ORIGIN))
        self.wait()

        self.play(FadeOut(arrow, step_group))

        exposition2 = Tex("Multiplying by $i$ rotates these 4 values, 90 degrees left.")
        exposition2.scale(2/3).to_edge(UP)
        exposition2.set_stroke(BLACK, 5, 1, True)
        self.play(Write(exposition2))
        self.play(Indicate(dots))
        self.wait()

        self.play(FadeOut(exposition2))
        exposition3 = VGroup(
            exposition3_line1 := Tex("If you scale these values,"),
            line_real := Tex("you see that any real", tex_to_color_map={"real":RED}),
            line_imag := Tex("or imaginary number gets", tex_to_color_map={"imaginary":GREEN}),
            Tex("rotated 90 degrees left"),
            Tex("when multiplied by $i$.")
        ).arrange(DOWN, aligned_edge=LEFT)
        exposition3.scale(2/3).to_corner(UL)
        exposition3.set_stroke(BLACK, 5, 1, True)
        self.play(Write(exposition3_line1))

        # Scaling cycle
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

        self.play(Write(exposition3[1:]), run_time=2)
        
        axes = numplane.get_axes()
        axis_real, axis_imag = axes
        tex_real = line_real.get_part_by_tex("real")
        tex_imag = line_imag.get_part_by_tex("imaginary")
        self.play(axes.animate.set_opacity(1))
        self.play(LaggedStart(Indicate(tex_real), axis_real.animate.set_color(RED)), run_time=1.5)
        self.play(LaggedStart(Indicate(tex_imag), axis_imag.animate.set_color(GREEN)), run_time=1.5)
        self.wait()

        self.play(scale_tracker.animate.set_value(2), run_time=1.5)

        self.play(FadeOut(exposition3, loop))
        self.wait()

        exposition4 = Tex("But what about other complex numbers?")
        exposition4.scale(2/3).to_corner(UL)
        exposition4.set_stroke(BLACK, 5, 1, True)
        self.play(Write(exposition4))
        self.play(numplane.animate.set_color(YELLOW).set_opacity(0.5))
        self.play(numplane.animate.set_color(BLUE).set_opacity(0.25))
        self.wait()

class ActionOfI(Scene):
    def construct(self):
        color_map = {"a":RED, "b":GREEN, "iu":BLUE_E, "u": BLUE}
        words = ["(", ")", "+", "i"]

        def math_tex(*text, **kwargs):
            return colored_math_tex(*text, t2c=color_map, words=words, **kwargs)

        def rotate_by_i(mobj, about_point=ORIGIN):
            return Rotate(mobj, PI/2, about_point=about_point)

        numplane = ComplexPlane(x_range=[-10, 10], y_range=[-10, 10])
        numplane.set_opacity(0.25).set_z_index(-10)
        dot = Dot().set_z_index(10)
        
        # equation1 = math_tex(*"i ( a + b i )".split(" "))
        equation1 = math_tex("i ( a + b i )")
        equation1.next_to(equation1, DOWN, buff=1)
        get_eqn_background = lambda eqn: SurroundingRectangle(eqn, color=WHITE).set_fill(BLACK, 1).set_z_index(-1)
        equation_background = get_eqn_background(equation1)
        
        u = 3 * c1 + 2 * ci
        iu = rotate_cc(u)
        arrow_ua = LabeledArrow(
            Arrow(ORIGIN, u * RIGHT, buff=0, color=RED),
            math_tex("a"),
            perp_distance=-0.35, distance=0, alpha=0.5
        )
        arrow_ub = LabeledArrow(
            Arrow(u * RIGHT, u, buff=0, color=GREEN),
            math_tex("b i"),
            perp_distance=-0.35, distance=0, alpha=0.5
        )

        arrow_u = Arrow(ORIGIN, u, buff=0, color=BLUE)
        arrow_iu = Arrow(ORIGIN, iu, buff=0, color=BLUE_E)
        angle_u_iu = Angle(arrow_u, arrow_iu, elbow=True)

        dot_u = ExternalLabeledDot(
            Dot(u),
            math_tex("a + b i"),
            normalize(u)
        )
        dot_iu = ExternalLabeledDot(
            Dot(iu),
            math_tex("-b + a i"),
            normalize(iu)
        )

        self.add(dot, numplane)

        exposition1 = Tex("Let's pick out an arbitrary point and see what happens when we multiply by $i$.")
        exposition1.scale(2/3).to_edge(UP)
        exposition1.set_stroke(BLACK, 5, 1, True)
        self.play(Write(exposition1))
        self.wait()

        self.play(dot_u.create_animation())
        self.play(arrow_ua.grow_animation())
        self.play(arrow_ub.grow_animation())

        self.play( Write(equation1) )
        self.play( Create(equation_background) )
        self.wait()


        self.play(FadeOut(exposition1))
        exposition2 = Tex("First, distribute the $i$.")
        exposition2.scale(2/3).next_to(equation_background, LEFT, 0.5)
        exposition2.set_stroke(BLACK, 5, 1, True)
        self.play(Write(exposition2))

        self.play( 
            TransformMatchingTex( 
                equation1, 
                equation2 := math_tex("a i + b i i").move_to(equation1),
                shift=ORIGIN
            ),
            equation_background.animate.become(get_eqn_background(equation2))
        )

        self.play(FadeOut(exposition2))
        exposition3 = Tex(
            r"We've shown that real and imaginary\\numbers get rotated 90 degrees left\\when we multiply by $i$.",
            tex_to_color_map={"real":RED, "imaginary":GREEN}
        )
        exposition3.scale(2/3).to_edge(LEFT)
        exposition3.set_stroke(BLACK, 5, 1, True)
        self.play(Write(exposition3))

        arrow_uai = arrow_ua.copy()
        arrow_ubi = arrow_ub.copy()

        self.add(arrow_uai, arrow_ubi)
        self.remove(arrow_ua, arrow_ub)

        self.play(FadeOut(equation2, equation_background))

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

        self.play(FadeOut(exposition3))
        exposition4 = Tex(
            r"But rotating component by component\\"
            r"gives the same result as rotating\\",
            r"everything in one rigid motion."
        )
        exposition4.scale(2/3).to_edge(LEFT)
        exposition4.set_stroke(BLACK, 5, 1, True)
        self.play(Write(exposition4))

        self.play(FadeIn(arrow_ua, arrow_ub))

        rotation_group = VGroup(
            arrow_ua.arrow.copy(),
            arrow_ub.arrow.copy(),
        )

        self.play(rotate_by_i(rotation_group), rotate_by_i(numplane), run_time=2)

        self.play(FadeOut(exposition4))
        exposition5 = VGroup(
            Tex(r"So multiplying by $i$ rotates any", tex_to_color_map={"any":YELLOW}),
            Tex(r"complex number 90 degrees left."),
        ).arrange(DOWN)
        exposition5.scale(2/3).set_stroke(BLACK, 5, 1, True).to_edge(LEFT, 0.75)
        self.play(Write(exposition5))

        self.play(FadeOut( rotation_group, arrow_ua, arrow_ub, arrow_uai, arrow_ubi ))

        self.play(
            Create(angle_u_iu),
            GrowArrow(arrow_u), GrowArrow(arrow_iu),
            dot_u.animate_relabel(math_tex("u")), dot_iu.animate_relabel(math_tex("iu")),
        )

        self.wait()

        self.play(FadeOut(exposition5))
        exposition6 = Tex(r"Now we're ready to prove the general scaling and rotation rules...")
        exposition6.scale(2/3).set_stroke(BLACK, 5, 1, True).shift(DOWN)
        self.play(Write(exposition6))

class ArbitraryTimesArbitrary2(MovingCameraScene):
    def construct(self):
        color_map = { 
            "$a$": RED, "$b$": GREEN,
            "a": RED, "b": GREEN,
            "$u$": BLUE, "$iu$": BLUE_E,
            "u": BLUE, "v": YELLOW, "iu": BLUE_E,
            "\\theta_{u}": BLUE, "\\theta_{v}": YELLOW,
            "r_{u}": BLUE, "r_{v}": YELLOW,
        }

        v = np.array([3, 2, 0])
        u_angle = PI / 12
        u = np.array([math.cos(u_angle), math.sin(u_angle), 0])
        iu = rotate_cc(u)

        numplane = Axes(x_range=[-8, 8], y_range=[-8, 8], x_length=None, y_length=None).set_opacity(0.5).set_z_index(-3)
        numplane_u = NumberPlane(x_range=[-16, 16], y_range=[-16, 16]).set_opacity(0.25).set_z_index(-2).rotate(u_angle)

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

        exposition1 = VGroup(
            line1 := colored_tex("Take some arbitrary complex number, $u$,", t2c=color_map),
            line2 := colored_tex("and the perpendicular value, $iu$.", t2c=color_map),
            line3 := colored_tex("These form the basis of a plane."),
        ).arrange(DOWN, aligned_edge=LEFT)
        exposition1.scale(2/3).to_corner(UL).shift(DOWN)
        exposition1.set_stroke(BLACK, 5, 1, True)

        self.play(Write(line1))

        self.play( arrow_u.grow_animation() )

        angle_u.suspend_updating()
        self.play( Create( angle_u ) )
        angle_u.resume_updating()

        self.play(Write(line2))
        self.wait(0.5)
        self.play( arrow_iu.grow_animation() )
        # for arrow in [arrow_u, arrow_iu]:
        self.wait(0.5)

        self.play(Write(line3))

        # self.play( Create( numplane_u ) )
        self.play( FadeIn( numplane_u ) )
        self.wait(2)

        self.play(FadeOut(exposition1))

        exposition2 = VGroup(
            line1 := colored_tex("Rotating $u$ rotates the plane along with it,", t2c=color_map),
            line2 := colored_tex("and scaling $u$ scales the plane.", t2c=color_map)
        ).arrange(DOWN)
        exposition2.scale(2/3).to_corner(UL).shift(DOWN)
        exposition2.set_stroke(BLACK, 5, 1, True)

        self.play(Write(line1))

        rotation_group = VGroup(arrow_u.arrow, arrow_iu.arrow, numplane_u)

        # Demonstrate rotation of plane by u
        for _delta_angle in [ PI / 4, -PI / 4 -u_angle, u_angle ]:
            self.play( Rotate( rotation_group, _delta_angle, about_point=ORIGIN ), run_time=1.5 )
        self.wait()

        self.play(Write(line2))

        # Demonstrate scaling of plane by u
        self.play( rotation_group.animate.scale(0.5, about_point=ORIGIN), run_time=1.5 )
        self.play( rotation_group.animate.scale(2, about_point=ORIGIN), run_time=1.5 )
        self.wait()

        self.play(FadeOut(exposition2))
        exposition3 = VGroup(
            line1 := colored_tex("We can pick out an arbitrary point in this transformed plane"),
            line2 := colored_tex("by walking $a$ units along the $u$ axis", t2c=color_map),
            line3 := colored_tex("and $b$ units along the $iu$ axis.", t2c=color_map),
        ).arrange(DOWN)
        exposition3.scale(2/3).to_corner(UL)
        exposition3.set_stroke(BLACK, 5, 1, True)
        self.play(Write(line1))

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

        for arrow, line in [(arrow_au, line2), (arrow_biu, line3)]:
            self.play( Write(line) )
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

        self.play(FadeOut(exposition3))
        exposition4 = colored_tex(
            "Let's factor out the $u$ in the transformed point.",
            t2c=color_map
        )
        exposition4.scale(2/3).next_to(dot_uv.label, LEFT, 0.5).to_edge(UP)
        exposition4.set_stroke(BLACK, 5, 1, True)
        self.play(Write(exposition4))

        self.play( dot_uv.animate_relabel( 
            MathTex(*"u ( a + b i )".split(" "), tex_to_color_map=color_map),
            path_arc=90*DEGREES
        ) )
        self.wait()

        self.play(FadeOut(exposition4))
        exposition5 = VGroup(
            line1 := colored_tex("What this is saying is that if"),
            line2 := VGroup(
                colored_tex("we take some arbitrary point,"),
                colored_math_tex(r"a + b i \text{,}", t2c=color_map),
            ).arrange(RIGHT),
            line3 := colored_tex("and multiply it by $u$,", t2c=color_map),
            line4 := colored_tex("it gets rotated by the argument of $u$,", t2c=color_map|{"argument":YELLOW}),
            line5 := colored_tex("and scaled by the modulus of $u$.", t2c=color_map|{"modulus":YELLOW}),
        ).arrange(DOWN)
        exposition5.scale(2/3).to_corner(UL).shift(DOWN)
        exposition5.set_stroke(BLACK, 5, 1, True)
        self.play(Write(line1))
        self.play(Write(line2))

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

        self.play(Write(line3))

        self.play(
            dot_uv.animate_relabel( 
                MathTex(*"u ( a + b i )".split(" "), tex_to_color_map=color_map),
                shift=DOWN
            ),
            animate_replace_tex( arrow_au.label, "au", color_map ),
            animate_replace_tex( arrow_biu.label, "biu", color_map ),
        )
        self.wait()

        self.play(Write(line4))
        self.play( Rotate( rotation_group, u_angle, about_point=ORIGIN ), run_time=1.5)
        self.wait(.5)

        self.play(Write(line5))
        angle_u.clear_updaters()
        rotation_group.add(angle_u)
        self.play( rotation_group.animate.scale(0.5, about_point=ORIGIN), run_time=1.5 )
        self.play( rotation_group.animate.scale(2, about_point=ORIGIN), run_time=1.5 )
        self.wait(2)

        self.play(FadeOut(exposition5))
        exposition6 = Tex(r"So we've proven the rotation and scaling\\rules for complex multiplication.")
        exposition6.scale(2/3).move_to(exposition5)
        exposition6.set_stroke(BLACK, 5, 1, True)
        self.play(Write(exposition6))

        self.play( animate_replace_tex( dot_uv.label, "uv", color_map ) )
        self.wait()

        self.play(  FadeOut( arrow_iu, numplane_u, exposition6 ) )

        eq_polar_product = MathTex(
            r"arg(uv) &= arg(u) + arg(v) \\ |uv| &= |u||v|",
            tex_to_color_map={"u":BLUE, "v":YELLOW})
        eq_polar_product.to_corner(UL)
        self.play( Write(eq_polar_product) )

class UnitComplexNumbers(Scene):
    def construct(self):
        theta_tracker = ValueTracker(0.001*DEGREES)

        U_COLOR = BLUE
        CONJ_COLOR = YELLOW
        scene_color_map = { 
            "$u$": U_COLOR, r"$\overline{u}$":CONJ_COLOR,
            "u": U_COLOR, r"\overline{u}":CONJ_COLOR,
            # r"\theta": U_COLOR,
            "cos":RED, "sin":GREEN,
            "i": WHITE, "-": WHITE
        }

        def get_tex(*strings):
            return colored_math_tex(*strings, t2c=scene_color_map)

        def get_numplane():
            xrange = [-10, 10]
            result = NumberPlane(x_range=xrange, y_range=xrange).rotate(theta_tracker.get_value())
            return result.set_opacity(0.25).set_z_index(-10)
        numplane = always_redraw( get_numplane )

        dot = Dot().set_z_index(10)
        self.play(FadeIn(numplane, dot))

        exposition1 = VGroup(
            line1 := colored_tex(
                "Numbers of modulus $1$ represent pure rotations.",
                t2c={"modulus":YELLOW, "pure rotations":YELLOW}
            ),
            line2 := colored_tex("These numbers lie on the unit circle.")
        ).arrange(DOWN)
        exposition1.scale(2/3).to_edge(UP)
        exposition1.set_stroke(BLACK, 5, 1, True)
        self.play(Write(line1))

        equations = VGroup(
            tex_mod_equals_one := get_tex("| u | = 1"),
            tex_form := get_tex("u = cos(\\theta) + i sin(\\theta)"),
            tex_form_conj := get_tex("\\overline{u} = cos(\\theta) - i sin(\\theta)")
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(LEFT).shift(UP*0.5)

        self.play(Write(tex_mod_equals_one))

        circle = Circle(1, WHITE)
        circle.set_z_index(-1)
        self.play(FadeIn(circle))

        self.play(Write(line2))

        self.wait()
        self.play(Indicate(circle), Indicate(tex_mod_equals_one))

        self.play(Write(tex_form))

        line_re = Line(ORIGIN, RIGHT)
        line_re.set_z_index(-2)
        self.play(Create(line_re))

        def get_dot(label_text, sign=1, color=WHITE):
            def func():
                theta = theta_tracker.get_value() * sign
                u = polar2xy(theta)
                alpha = smoothstep( 15*DEGREES, 25*DEGREES, theta*sign )

                dot = Dot(u, color=color)
                
                line = Line(ORIGIN, u, color=color)
                line_re = Line(ORIGIN, RIGHT)
                
                angle = Angle(line_re, line, color=color, radius=0.25, other_angle=theta<0)
                
                theta_text = "\\theta" if sign > 0 else "-\\theta"
                label_theta = MathTex(theta_text).scale(.8).move_to(angle.get_midpoint() * 2)
                label_theta.set_opacity(alpha)

                label = MathTex(label_text, color=color).next_to(dot, u, buff=0.1)

                arrow_radius = 2
                theta_buff = PI/32
                arrow = CurvedArrow(
                    polar2xy(0     + theta_buff*sign, arrow_radius),
                    polar2xy(theta - theta_buff*sign, arrow_radius),
                    radius=arrow_radius*sign,
                    tip_length=0.2,
                    color=color
                )
                arrow.get_tip().set_opacity(alpha)
                
                result = VDict({
                    "dot": dot, "line": line, "angle": angle,
                    "label_theta": label_theta, "label": label,
                    "arrow": arrow
                })
                return result
            return func
        
        dot_u = always_redraw(get_dot("u", color=U_COLOR))

        self.play(Create(dot_u))
        self.play(theta_tracker.animate.set_value(135*DEGREES), run_time=1.5)
        self.play(FadeOut(numplane))
        self.wait()

        self.play(FadeOut(exposition1))
        exposition2 = VGroup(
            line1 := colored_tex("We can obtain the opposite rotation by reflecting $u$ vertically.", t2c=scene_color_map),
            line2 := colored_tex(
                r"This opperation is called conjugation and the reflected value\\is called u-conjugate.",
                t2c={"u-conjugate":CONJ_COLOR}|scene_color_map
            )
        ).arrange(DOWN)
        exposition2.scale(2/3).set_stroke(BLACK, 5, 1, True).to_edge(UP)
        self.play(Write(line1))

        dot_uconj = always_redraw(get_dot("\\overline{u}", -1, CONJ_COLOR))
        # self.play(Create(dot_uconj))
        self.play(ReplacementTransform(dot_u.copy(), dot_uconj))
        self.wait()

        self.play(Write(line2))

        self.play(Write(tex_form_conj))

        self.play(FadeOut(exposition2))
        exposition3 = colored_tex(
            r"The conjugate of a complex number is calculated\\by negating its imaginary component.",
            t2c={"imaginary":GREEN}
        )
        exposition3.scale(2/3).set_stroke(BLACK, 5, 1, True).to_edge(UP)
        self.play(Write(exposition3))

        self.next_section()
        self.play( Indicate(tex_form_conj[4:]) )