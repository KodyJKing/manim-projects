from manim import *

ihat = "\hat{\imath}"
jhat = "\hat{\jmath}"
khat = "\hat{k}"
ihatn = "-" + ihat
jhatn = "-" + jhat
khatn = "-" + khat

def add_table_highlights(width: int, table: Table):
    for i in range(width):
        table.add_highlighted_cell((i + 2, 1), DARK_GRAY)
        table.add_highlighted_cell((1, i + 2), DARK_GRAY)
    table.add_highlighted_cell((1, 1), GRAY)
    return table

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
    return add_table_highlights(3, MathTable(
        crossproduct_table,
        include_outer_lines=True,
        element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map)
    ) )

def vec_dot_table(tex_to_color_map=None):
    ih, jh, kh = ihat, jhat, khat
    op = r"u \cdot v"
    dot_product_table = [
        [op, ih, jh, kh],
        [ih,  1,  0,  0],
        [jh,  0,  1,  0],
        [kh,  0,  0,  1]
    ]
    return add_table_highlights(3, MathTable(
        dot_product_table,
        include_outer_lines=True,
        element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map)
    ) )

def pure_quat_times_table(tex_to_color_map=None):
    op = "uv"
    quaternion_table_ijk = [
        [op,  "i",  "j",  "k"],
        ["i", "-1",  "k", "-j"],
        ["j", "-k", "-1",  "i"],
        ["k",  "j", "-i", "-1"]
    ]
    return add_table_highlights(3, MathTable(
        quaternion_table_ijk,
        include_outer_lines=True,
        element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map)
    ) )

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
        element_to_mobject=lambda s: MathTex(s, tex_to_color_map=tex_to_color_map),
    )