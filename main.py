import math
from manim import *
import numpy as np

from ExternalLabeledDot import ExternalLabeledDot
from LabeledArrow import LabeledArrow
from mathutils import rotate_cc, rotate_cw
from utils import animate_replace_tex

c1 = np.array([1, 0, 0])
ci = np.array([0, 1, 0])

# ihat = "\hat{\imath}"
# jhat = "\hat{\jmath}"
# khat = "\hat{k}"
# ihatn = "-" + ihat
# jhatn = "-" + jhat
# khatn = "-" + khat

# def vec_ijk_cross_table(tex_to_color_map=None):
#     ih, jh, kh = ihat, jhat, khat
#     im, jm, km = ihatn, jhatn, khatn
#     crossproduct_table = [
#         ["", ih, jh, kh],
#         [ih, -1, kh, jm],
#         [jh, km, -1, ih],
#         [kh, jh, im, -1]
#     ]
#     return MathTable(
#         crossproduct_table,
#         include_outer_lines=True,
#         # element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map)
#     )

# def quat_ijk_times_table(tex_to_color_map=None):
#     quaternion_table_ijk = [
#         ["",  "i",  "j",  "k"],
#         ["i", "-1",  "k", "-j"],
#         ["j", "-k", "-1",  "i"],
#         ["k",  "j", "-i", "-1"]
#     ]
#     return MathTable(
#         quaternion_table_ijk,
#         include_outer_lines=True,
#         element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map)
#     )

# def quat_fill_times_table(tex_to_color_map=None):
#     quaternion_table = [
#         ["", "1",  "i",  "j",  "k"],
#         ["1", "1",  "i",  "j",  "k"],
#         ["i", "i", "-1",  "k", "-j"],
#         ["j", "j", "-k", "-1",  "i"],
#         ["k", "k",  "j", "-i", "-1"]
#     ]
#     return MathTable(
#         quaternion_table,
#         include_outer_lines=True,
#         element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map)
#     )

class ComponentTimesI(Scene):
    def construct(self):
        numplane = ComplexPlane().add_coordinates()

        labels = ["1", "i", "-1", "-i"]
        points = [c1, ci, -c1, -ci]

        def labeled_dot(point, label):
            return ExternalLabeledDot(
                Dot(point),
                label,
                direction=normalize(point),
                distance=1
            )

        dots = VGroup(*map( labeled_dot, points, labels ))

        arcs = []
        for i in range(len(points)):
            j = (i + 1) % len(points)
            pointI = points[i]
            pointJ = points[j]
            normal = rotate_cw(pointJ - pointI)
            color = BLUE
            arc = CurvedArrow(pointI, pointJ, radius=1, tip_length=.2, color=color)
            label = MathTex("i", color=color).next_to(arc.get_center(), normal)
            arc = VGroup(arc, label)
            arcs.append(arc)
        arcs = VGroup(*arcs)

        self.play( Create(numplane) )

        self.play(
            numplane.coordinate_labels.animate.set_opacity(.25),
            numplane.animate.set_opacity(.25),
            FadeIn(dots[0])
        )
        for i in range(3):
            self.play( FadeIn(dots[i + 1]), FadeIn(arcs[i]))
        self.play( FadeIn(arcs[3]))

        arrow = Arrow(ORIGIN, c1, color=RED, buff=0)
        self.play(FadeIn(arrow), FadeOut( dots, arcs ))
        for i in range(4):
            self.play( Rotate(arrow, PI / 2, about_point=ORIGIN), FadeIn(arcs[i]) )
            self.wait(.5)

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
        steps = "ai + bi^2; ai + b(-1); -b + ai".split(";")
        for step in steps:
            self.play( animate_replace_tex( dot_iv.label, step, color_map, ORIGIN ) )

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

class ArbitraryTimesArbitrary(Scene):
    def construct(self):
        color_map = { "a": RED, "b": GREEN, "u": BLUE, "v": YELLOW }

        numplane = ComplexPlane().add_coordinates().set_z_index(-100)
        circle = Circle(1, color=WHITE)
        circle.stroke_width = 2

        self.add(numplane, circle)
        self.wait()

        v = np.array([3, -2, 0])
        u_angle = PI / 4
        u = np.array([math.cos(u_angle), math.sin(u_angle), 0])

        arrow_u = Arrow(ORIGIN, u, buff=0, color=BLUE, z_index=1)
        arrow_v = Arrow(ORIGIN, v, buff=0, color=YELLOW, z_index=1)

        self.play( GrowArrow(arrow_v) )

        dot_v = ExternalLabeledDot(
            Dot(arrow_v.get_end()),
            MathTex("a + bi", tex_to_color_map=color_map),
            direction=normalize(DOWN + RIGHT)
        )
        self.play( dot_v.create_animation() )

        self.play( GrowArrow(arrow_u) )

        angle = Angle(Line(ORIGIN, RIGHT), arrow_u, radius=0.25)

        self.play( Create(angle) )

        arrow_v_re_ref = Arrow(ORIGIN, [v[0], 0, 0], buff=0, color=RED)
        arrow_v_im_ref = Arrow(ORIGIN, [0, v[1], 0], buff=0, color=GREEN).shift(arrow_v_re_ref.get_end())
        arrow_v_re = arrow_v_re_ref.copy()
        arrow_v_im = arrow_v_im_ref.copy()

        self.play( FadeIn(arrow_v_re, arrow_v_im) )

        comparison_re = get_angle_comparison( arrow_v_re, u_angle )
        comparison_im = get_angle_comparison( arrow_v_im, u_angle )

        self.add( comparison_re["arrow"], comparison_im["arrow"] )

        self.play(
            Rotate(arrow_v_re, u_angle, about_point=ORIGIN),
            Rotate(arrow_v_im, u_angle, about_point=arrow_v_im.get_start()),
            Create(comparison_re["angle"]),
            Create(comparison_im["angle"])
        )

        self.wait()

        self.play(
            Uncreate(comparison_re["angle"]),
            Uncreate(comparison_im["angle"]),
            arrow_v_im.animate.shift(
                arrow_v_re.get_end() - arrow_v_im.get_start()
            )
        )

        #  Show uv
        dot_uv = ExternalLabeledDot(
            Dot(arrow_v_im.get_end()),
            MathTex("ua + ubi", tex_to_color_map=color_map)
        )
        self.play( dot_uv.create_animation() )
        self.wait()
        self.play( animate_replace_tex(dot_uv.label, "u(a + bi)", color_map) )
        self.wait()
        self.play( animate_replace_tex(dot_uv.label, "uv", color_map) )

        self.wait()

        self.play( FadeOut(
            arrow_v_re, arrow_v_im,
            comparison_re["arrow"], comparison_im["arrow"]
        ) )

        comparison_v = get_angle_comparison(arrow_v, u_angle )
        self.add(comparison_v["arrow"])
        self.play( 
            Rotate(arrow_v, u_angle, about_point=ORIGIN),
            Create(comparison_v["angle"])
        )

        self.wait()

class ArbitraryTimesArbitrary2(MovingCameraScene):
    def construct(self):
        color_map = { "a": RED, "b": GREEN, "u": BLUE, "v": YELLOW, "iu": BLUE_E }

        numplane = ComplexPlane().set_opacity(0.25)
        self.add(numplane)
        self.wait(0.5)

        self.add( Dot(ORIGIN).set_z_index(2) )

        v = np.array([3, 2, 0])
        u_angle = PI / 12
        u = np.array([math.cos(u_angle), math.sin(u_angle), 0])
        iu = rotate_cc(u)

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

        for arrow in [arrow_u, arrow_iu]:
            self.play( arrow.grow_animation() )
        self.wait(0.5)

        rotation_group = VGroup(arrow_u.arrow, arrow_iu.arrow)

        for _delta_angle in [ PI / 4, -PI / 4 -u_angle, u_angle ]:
            self.play( Rotate( rotation_group, _delta_angle, about_point=ORIGIN ), run_time=1.5 )

        self.wait(1)

        arrow_au = LabeledArrow(
            Arrow( ORIGIN, u * v[0], buff=0, color=RED ),
            MathTex("au", tex_to_color_map=color_map),
            perp_distance=-0.25, distance=0, alpha=0.5
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
            Dot( arrow_biu.arrow.get_end() ),
            MathTex("au + biu", tex_to_color_map=color_map)
        )
        self.play( dot_uv.create_animation() )

        self.wait(.5)
        
        rotation_group.add(arrow_au.arrow, arrow_biu.arrow, dot_uv.dot)

        for _delta_angle in [ PI / 8, -PI / 8 ]:
            self.play( Rotate( rotation_group, _delta_angle, about_point=ORIGIN ), run_time=1.5 )
        self.wait(0.5)

        self.play( 
            Rotate( rotation_group, -u_angle, about_point=ORIGIN ),
            animate_replace_tex( dot_uv.label, "a + bi", color_map ),
            animate_replace_tex( arrow_au.label, "a", color_map ),
            animate_replace_tex( arrow_biu.label, "bi", color_map ),
            animate_replace_tex( arrow_u.label, "1", color_map ),
            animate_replace_tex( arrow_iu.label, "i", color_map ),
            run_time=1.5
        )
        self.wait(1)
        self.play(
            Rotate( rotation_group, u_angle, about_point=ORIGIN ),
            animate_replace_tex( dot_uv.label, "au + biu", color_map ),
            animate_replace_tex( arrow_au.label, "au", color_map ),
            animate_replace_tex( arrow_biu.label, "biu", color_map ),
            animate_replace_tex( arrow_u.label, "u", color_map ),
            animate_replace_tex( arrow_iu.label, "iu", color_map ),
            run_time=1.5
        )
        self.wait(.5)

        self.play( animate_replace_tex( dot_uv.label, "u(a + bi)", color_map ) )
        self.wait()

def get_angle_comparison(arrow_ref, angle, color=WHITE):
    arrow_base = arrow_ref.copy()
    arrow_base.set_opacity(0.5)
    arrow_rot = arrow_ref.copy().rotate(angle, about_point=arrow_ref.get_start())
    elbow = math.fabs(math.fabs(angle) - PI / 2) < 0.00001
    angle = Angle(arrow_base, arrow_rot, radius=0.5, elbow=elbow, color=color)
    return VDict([ ("arrow", arrow_base), ("angle", angle) ])#.set_z_index(-1)