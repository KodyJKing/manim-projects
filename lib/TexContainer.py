from typing import Callable
from manim import *
import numpy as np

# from utils import colored_math_tex

class TexContainer(VMobject):
    """ Provides some indirection over Tex/MathTex to avoid having to update references when replacing/transforming expressions."""
    def __init__(
        self, tex,
        to_tex: Callable[[Any], MathTex] = MathTex,
        **kwargs
    ):
        super().__init__(**kwargs)

        self._to_tex = to_tex
        self.tex = self.to_tex(tex)
        self.add(self.tex)

    def to_tex(self, tex):
        if isinstance(tex, MathTex):
            return tex
        return self._to_tex(tex)
    
    def transform(self, new_tex, instant=False, shift=ORIGIN, **kwargs):
        new_tex = self.to_tex(new_tex)
        old_tex = self.tex
        self.tex = new_tex

        new_tex.move_to(old_tex)

        def on_finish(scene: Scene):
            self.remove(old_tex)
            self.add(new_tex)
            if instant:
                scene.remove(old_tex)

        if instant:
            anims = []
            run_time = 0.001
        else:
            anims = [TransformMatchingTex(old_tex, new_tex, shift=shift, **kwargs)]
            run_time = None

        return AnimationGroup(*anims, run_time=run_time, _on_finish=on_finish)
    
    def replace(self, new_tex, **kwargs):
        return self.transform(new_tex, True, **kwargs)

# class Test(Scene):
#     def construct(self):
#         color_map = {"i":RED, "{i}":RED}
#         words = [r"\pi", "-1", "=", "0"]
#         to_tex = lambda x: colored_math_tex(x, words=words, t2c=color_map)

#         tc = TexContainer(r"e^{i \pi} = -1", to_tex)

#         self.play(Write(tc))

#         self.play(tc.transform(r"e^{i \pi} = cos(\pi) + {i} sin(\pi)"))
#         self.play(tc.replace(colored_math_tex(
#             r"e^{i \pi} = cos(\pi) + {i} sin(\pi)",
#             words=[r"cos(\pi)", r"sin(\pi)", *words],
#             t2c=color_map
#         )))
#         self.play(tc.transform(
#             r"e^{i \pi} = -1 + {i} 0",
#             key_map={"cos(\pi)":"-1"}
#         ))
#         self.play(tc.transform( r"e^{i \pi} = -1 + 0" ))
#         self.play(tc.transform( r"e^{i \pi} = -1" ))