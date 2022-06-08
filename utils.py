from manim import *

def animate_replace_tex(tex: MathTex, text_or_tex: str | MathTex, tex_to_color_map=None, aligned_edge=LEFT):
    if isinstance(text_or_tex, str):
        text_or_tex = MathTex( text_or_tex, tex_to_color_map=tex_to_color_map )
    return tex.animate.become( text_or_tex.move_to(tex, aligned_edge) )

def animate_arc_to(mobj, target):
    return MoveAlongPath( mobj, ArcBetweenPoints( mobj.get_center(), target.get_center() ) )

def tex_matches(tex: MathTex, *parts):
    matches = [ tex.get_part_by_tex(part) for part in parts ]
    not_none = [ match for match in matches if not match is None ]
    return VGroup(*not_none)

def angle_label_pos(line1, line2, radius, **kwargs):
    return Angle( line1, line2, radius=radius, **kwargs).point_from_proportion(0.5)
