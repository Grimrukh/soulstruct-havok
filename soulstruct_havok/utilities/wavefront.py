from __future__ import annotations

__all__ = ["read_obj"]

import re
from pathlib import Path

from soulstruct_havok.utilities.maths import Vector4


def read_obj(obj_path: Path | str, invert_x=True) -> list[tuple[list[Vector4], list[tuple[int, int, int, int]]]]:
    """Reads OBJ file and returns a list of meshes, each of which is a list of `Vector4` vertices and a list of faces
    (vertex index triples).

    If `invert_x=True` (default), X coordinates will be negated, which is sufficient for having collisions appear
    properly in Blender (assuming they were also negated on conversion to OBJ or import into Blender).
    """
    meshes = []  # type: list[tuple[list[Vector4], list[tuple[int, int, int, int]]]]
    mesh = None  # type: None | tuple[list, list]

    o_re = re.compile(r"^o .*$")
    v_re = re.compile(r"^v ([-\d.]+) ([-\d.]+) ([-\d.]+)$")
    f_re = re.compile(r"^f (\d+)(?://\d+)? (\d+)(?://\d+)? (\d+)(?://\d+)?$")

    global_v_i = 0

    with Path(obj_path).open("r") as f:
        for line in f.readlines():
            if o_re.match(line):
                if mesh is not None:
                    global_v_i += len(mesh[0])  # increase global vertex count
                mesh = ([], [])  # vertices, faces
                meshes.append(mesh)
            elif v := v_re.match(line):
                if mesh is None:
                    raise ValueError("Found 'v' vertex line before an 'o' object definition.")
                if mesh[1]:
                    raise ValueError("Found 'v' vertex line after 'f' face lines.")
                x, y, z = float(v.group(1)), float(v.group(2)), float(v.group(3))
                vertex = Vector4((-x if invert_x else x), y, z, 0.0)
                mesh[0].append(vertex)
            elif f := f_re.match(line):
                if mesh is None:
                    raise ValueError("Found 'f' face line before an 'o' object definition.")
                if not mesh[0]:
                    raise ValueError("Found 'f' face line before a 'v' vertex lines.")
                # Switch to 0-indexing, localize vertex indices, and insert zero that appears between triplets in HKX.
                face = (
                    int(f.group(1)) - global_v_i - 1,
                    int(f.group(2)) - global_v_i - 1,
                    int(f.group(3)) - global_v_i - 1,
                    0,
                )
                mesh[1].append(face)
            else:
                pass  # ignore all other lines

    return meshes
