from manim import *
from typing import Callable, Union

def animate_replace_tex(tex: MathTex, text_or_tex: str | MathTex, tex_to_color_map=None, aligned_edge=LEFT):
    if isinstance(text_or_tex, str):
        text_or_tex = MathTex( text_or_tex, tex_to_color_map=tex_to_color_map )
    return tex.animate.become( text_or_tex.move_to(tex, aligned_edge) )

def tex_matches(tex: MathTex, *parts):
    matches = [ tex.get_part_by_tex(part) for part in parts ]
    not_none = [ match for match in matches if not match is None ]
    return VGroup(*not_none)

# Functional Mobjects

MobjectFunction = Union[Callable[["Mobject"], "Mobject"], Callable[[], "Mobject"]]
default_retain = [ "fill_color", "fill_opacity", "stroke_color", "stroke_opacity" ]

def functional_mobject(get_mobject: MobjectFunction, retain_fields: list[str] | None=default_retain):
    mobject = get_mobject()

    def updater(x: Mobject):
        if not retain_fields is None:
            retained = {}
            for field in retain_fields:
                retained[field] = getattr(x, field)

        x.become(get_mobject())

        if not retain_fields is None:
            for field in retain_fields:
                setattr(x, field, retained[field])

    mobject.add_updater(updater)

    return mobject

class _TestScene_functional_mobject(Scene):
    def construct(self):

        angle = ValueTracker(30)

        arrow = functional_mobject(
            lambda: Arrow(ORIGIN, RIGHT, buff=0).rotate_about_origin(angle.get_value() * DEGREES)
        )

        self.add(arrow)

        self.play( angle.animate.set_value(90) )

        self.wait()