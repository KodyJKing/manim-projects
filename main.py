from manim import *
import numpy as np

c1 = np.array([1, 0, 0])
ci = np.array([0, 1, 0])

class CreateTable(Scene):
    def construct(self):
        table = MathTable(
            [["", "1",  "i",  "j",  "k"],
            ["1", "1",  "i",  "j",  "k"],
            ["i", "i", "-1",  "k", "-j"],
            ["j", "j", "-k", "-1",  "i"],
            ["k", "k",  "j", "-i", "-1"]],
            include_outer_lines=True
        )

        self.play(table.create())
        self.wait()

class AnimateAngle(Scene):
    def construct(self):
        rotation_center = ORIGIN

        theta_tracker = ValueTracker(30)
        biv_slide_tracker = ValueTracker(0)

        vec_a = 3
        vec_b = 2

        arrow_v = easyAnimated(
            lambda: Arrow(ORIGIN, c1, buff=0, color=RED, z_index=1).rotate(
                theta_tracker.get_value() * DEGREES, about_point=rotation_center
            )
        )
        arrow_iv = easyAnimated(
            lambda: Arrow(ORIGIN, c1, buff=0, color=GREEN, z_index=1).rotate(
                (theta_tracker.get_value() + 90) * DEGREES, about_point=rotation_center
            )
        )

        text_v = attatchToArrow(arrow_v, MathTex("v", color=RED, z_index=1), -.5)
        text_iv =  attatchToArrow(arrow_iv, MathTex("iv", color=GREEN, z_index=1))

        numberplane = ComplexPlane().add_coordinates()

        self.add(numberplane, arrow_v, arrow_iv, text_v, text_iv)
        self.wait()

        self.play(theta_tracker.animate.set_value(50))
        self.play(theta_tracker.animate.set_value(10))
        self.play(theta_tracker.animate.set_value(20))

        arrow_av = easyAnimated(
            lambda: Arrow(ORIGIN, c1 * vec_a, buff=0).rotate(
                theta_tracker.get_value() * DEGREES, about_point=rotation_center
            )
        )
        arrow_biv = easyAnimated(
            lambda: Arrow(ORIGIN, c1 * vec_b, buff=0).rotate(
                (theta_tracker.get_value() + 90) * DEGREES, about_point=rotation_center
            ).shift(arrow_v.get_unit_vector() * vec_a * biv_slide_tracker.get_value())
        )

        text_av = attatchToArrow(arrow_av, MathTex("av", color=RED, z_index=1, substrings_to_isolate="a"), -.5)
        text_biv =  attatchToArrow(arrow_biv, MathTex("biv", color=GREEN, z_index=1, substrings_to_isolate="b"))
        text_av.set_color_by_tex("a", YELLOW)
        text_biv.set_color_by_tex("b", YELLOW)

        text_v.clear_updaters()
        text_iv.clear_updaters()
        set_updating(False, arrow_av, arrow_biv)
        self.play(FadeIn( arrow_av, arrow_biv, text_av, text_biv), FadeOut(text_v, text_iv))
        set_updating(True, arrow_av, arrow_biv)

        self.play(biv_slide_tracker.animate.set_value(1))

        arrow_uv = easyAnimated(
            lambda: Arrow(ORIGIN, arrow_biv.get_end(), buff=0, color=BLUE)
        )

        text_uv = MathTex("av + biv", z_index=1, substrings_to_isolate=["v", "iv", "a", "b"])
        attatchToArrow(arrow_uv, text_uv, .5, aligned_edge=[1, 0, 0], position="end")
        text_uv.set_color_by_tex("v", RED)
        text_uv.set_color_by_tex("iv", GREEN)
        text_uv.set_color_by_tex("a", YELLOW)
        text_uv.set_color_by_tex("b", YELLOW)

        set_updating( False, arrow_uv )
        self.play( FadeIn(arrow_uv) )
        self.play( Write(text_uv) )
        set_updating( True, arrow_uv )

        self.wait(2)

        self.play(theta_tracker.animate.set_value(0.001))

        text_a = attatchToArrow(arrow_av, MathTex("a", z_index=1, color=YELLOW), -.5)
        text_bi = attatchToArrow(arrow_biv, MathTex("bi", z_index=1, color=YELLOW, substrings_to_isolate="i"))
        text_bi.set_color_by_tex("i", WHITE)

        text_u = MathTex("a + bi", z_index=1, substrings_to_isolate=["a", "b"])
        attatchToArrow(arrow_uv, text_u, .5, aligned_edge=[1, 0, 0], position="end")
        text_u.set_color_by_tex("a", YELLOW)
        text_u.set_color_by_tex("b", YELLOW)

        text_av_copy = text_av.copy()
        text_biv_copy = text_biv.copy()
        text_uv_copy = text_uv.copy()

        self.play(
            Transform(text_av, text_a),
            Transform(text_biv, text_bi),
            Transform(text_uv, text_u)
        )

        self.wait(2)

        self.play(
            theta_tracker.animate.set_value(20),
            Transform(text_av, text_av_copy),
            Transform(text_biv, text_biv_copy),
            Transform(text_uv, text_uv_copy)
        )

        self.wait(2)

class BasisTimesI(Scene):
    def construct(self):
        numplane = ComplexPlane().add_coordinates()
        circle = Circle(1, color=WHITE)

        points = [
            [ 1,  0, 0],
            [ 0,  1, 0],
            [-1,  0, 0],
            [ 0, -1, 0]
        ]

        dots = VGroup(*map( lambda x: Dot(x), points ))

        arcs = []
        for i in range(len(points)):
            j = (i + 1) % len(points)
            pointI = points[i]
            pointJ = points[j]
            arc = CurvedArrow(pointI, pointJ, radius=2, tip_length=.2)
            arcs.append(arc)
        arcs = VGroup(*arcs)

        self.play( Create(numplane) )

        self.play( FadeIn(dots[0]) )
        for i in range(3):
            self.play( FadeIn(dots[i + 1]), FadeIn(arcs[i]))
        self.play( FadeIn(arcs[3]))

        arrow = Arrow(ORIGIN, c1, color=YELLOW, buff=0)
        self.play(FadeIn(arrow), FadeOut( arcs, dots ))
        for i in range(4):
            self.play( Rotate(arrow, PI / 2, about_point=ORIGIN) )
            self.wait(.5)

        self.wait()

class ArbitraryTimesI(Scene):
    pass

def set_updating(updating, *mobjects):
    for mobj in mobjects:
        if updating:
            mobj.resume_updating()
        else:
            mobj.suspend_updating()

def attatchToArrow(arrow, mobject, dist=.5, aligned_edge=[0, 0, 0], position="center"):
    def move(x):
        unit_vec = arrow.get_unit_vector()
        left_norm = ccnormal(unit_vec)
        pos = arrow.get_center() if position == "center" else arrow.get_end()
        return x.next_to(
            pos, left_norm * dist,
            aligned_edge=aligned_edge
        )
    mobject.add_updater(move)
    return move(mobject)

def easyAnimated(get_mobject):
    mobject = get_mobject()
    def update(x):
        fill = x.fill_color
        stroke = x.stroke_color
        x.become(get_mobject())
        x.set_stroke(stroke)
        x.set_fill(fill)
    mobject.add_updater(update)
    return mobject

def ccnormal(vec):
    return np.array([ -vec[1], vec[0], vec[2] ])