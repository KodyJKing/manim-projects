from manim import *

transform_key = "__transform_key__"

def set_transform_key(mobject: Mobject, key: str):
    setattr(mobject, transform_key, key)
    return mobject

class TransformMatchingKeyTex(TransformMatchingTex):
    @staticmethod
    def get_mobject_key(mobject: Mobject) -> str:
        if hasattr(mobject, transform_key):
            key = getattr(mobject, transform_key)
        else:
            key = ""
        return mobject.tex_string + "~" + key
