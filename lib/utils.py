from typing import Callable, Iterable, List, Tuple
from manim import *
import re

def style_exposition(mobj: VMobject):
    mobj.scale(2/3).set_stroke(BLACK, 5, 1, True)
    return mobj

def animate_replace_tex(tex: MathTex, text_or_tex: str | MathTex, tex_to_color_map=None, aligned_edge=LEFT):
    if isinstance(text_or_tex, str):
        text_or_tex = MathTex( text_or_tex, tex_to_color_map=tex_to_color_map )
    return tex.animate.become( text_or_tex.move_to(tex, aligned_edge) )

def animate_arc_to(mobj: Mobject, target: Mobject, aligned_edge=ORIGIN):
    offset = mobj.get_center() - mobj.get_edge_center(aligned_edge)
    return MoveAlongPath( mobj, ArcBetweenPoints( mobj.get_center(), target.get_edge_center(aligned_edge) + offset ) )

def swap_anim(mobj1: Mobject, mobj2: Mobject, aligned_edge=ORIGIN):
    return AnimationGroup(
        animate_arc_to(mobj1, mobj2, aligned_edge=aligned_edge),
        animate_arc_to(mobj2, mobj1, aligned_edge=aligned_edge)
    )

def tex_matches(tex: MathTex, *parts):
    matches = [ tex.get_part_by_tex(part) for part in parts ]
    not_none = [ match for match in matches if not match is None ]
    return VGroup(*not_none)

def angle_label_pos(line1, line2, radius, **kwargs):
    return Angle( line1, line2, radius=radius, **kwargs).point_from_proportion(0.5)

def colored_math_tex(*tex_strings, words:List[str]=[], t2c:dict[str, str]={}, **kwargs):
    """
        MathTex, but with better coloring behaviour.
        Does not match patterns in the middle of a word,
        allowing one to color "i" without coloring "sin" for example.
    """

    def get_tex_strings():
        keys = [*words, *t2c.keys()]
        if len(keys) == 0:
            return tex_strings
        word_patterns = [
            f"(?<!\w)({re.escape(pattern)})(?!\w)"
            for pattern in keys
        ]
        pattern = "|".join(word_patterns)
        result = []
        for s in tex_strings:
            result.extend(re.split(pattern, s))
        result = [piece for piece in result if piece and len(piece.strip(" ")) > 0]
        return result

    tex_strings = get_tex_strings()
    # print(tex_strings)

    result = MathTex(*tex_strings, **kwargs)
    result.set_color_by_tex_to_color_map(t2c, substring=False)

    # Remove lone invisible glyphs. These break Write animations.
    invisible_glyphs = ["}", r"\,"]
    for mob in result.submobjects:
        tex_string = mob.tex_string.strip(" ")
        if tex_string in invisible_glyphs:
            result.remove(mob)

    return result

def colored_tex(
    *tex_strings, 
    words:List[str]=[], 
    t2c:dict[str, str]={},
    arg_separator="", tex_environment="center",
    **kwargs
):
    return colored_math_tex(
        *tex_strings, 
        words=words, 
        t2c=t2c,
        arg_separator=arg_separator,
        tex_environment=tex_environment,
        **kwargs
    )

def compose_colored_tex(*color_tex: str, **kwargs):
    """Builds MathTex with colored tex. Argument has form color1, tex1, color2, tex2..."""
    colors = []
    texes = []
    length = len(color_tex)
    if length % 2 != 0:
        raise ValueError("Must provide as many colors as tex strings.")
    entry_count = length // 2
    for i in range(entry_count):
        colors.append(color_tex[i * 2 + 0])
        texes.append( color_tex[i * 2 + 1])
    
    tex = MathTex(*texes, **kwargs)

    for i in range(entry_count):
        tex[i].set_color(colors[i])
    
    return tex

def play_rewrite_sequence(
        scene: Scene, *steps: Tuple[MathTex, bool], key_map: dict[str, str] = {},
        first_wait=1, wait=1, run_time_per_step=1,
        aligned_edge: np.array = LEFT
    ):
        scene.play(Write(steps[0][0]))
        if first_wait > 0:
            scene.wait(first_wait)
        prev_step = steps[0][0]
        for tex, glide in steps[1:]:
            tex.move_to(prev_step, aligned_edge=aligned_edge)
            if glide:
                scene.play(TransformMatchingTex(prev_step, tex, path_arc=-90*DEGREES, key_map=key_map), run_time=run_time_per_step)
            else:
                scene.play(ReplacementTransform(prev_step, tex), run_time=run_time_per_step)
            if wait > 0:
                scene.wait(wait)
            prev_step = tex

def fallback_mobj(get_primary: Callable[[],Mobject], fallback: Mobject):
    try:
        return get_primary()
    except Exception as err:
        return fallback
