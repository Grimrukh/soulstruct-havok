from __future__ import annotations

__all__ = ["read_obj"]

import re
from pathlib import Path

import numpy as np


def read_obj(obj_path: Path | str, invert_x=True) -> list[tuple[np.ndarray, np.ndarray]]:
    """Reads OBJ file and returns a list of meshes, each of which is a list of `Vector4` vertices and a list of faces
    (vertex index triples).

    If `invert_x=True` (default), X coordinates will be negated, which is sufficient for having collisions appear
    properly in Blender (assuming they were also negated on conversion to OBJ or import into Blender).

    TODO: Not sure if `invert_x` is still correct with my improved Blender conversion.
    """
    o_re = re.compile(r"^o .*$")
    v_re = re.compile(r"^v ([-\d.]+) ([-\d.]+) ([-\d.]+)$")
    f_re = re.compile(r"^f (\d+)(?://\d+)? (\d+)(?://\d+)? (\d+)(?://\d+)?$")

    global_v_i = 0

    meshes = []  # type: list[tuple[np.ndarray, np.ndarray]]
    vertex_list = None  # type: None | list[tuple[float, float, float]]
    face_list = None  # type: None | list[tuple[int, int, int]]

    with Path(obj_path).open("r") as f:
        lines = f.readlines()

    for line in lines:
        if o_re.match(line):
            # New object definition.
            if vertex_list is not None:
                global_v_i += len(vertex_list)  # increase global vertex count
            # Finish previous mesh.
            meshes.append((np.array(vertex_list), np.array(face_list)))

            # Start new mesh.
            vertex_list = []
            face_list = []
        elif v := v_re.match(line):
            # Vertex definition.
            if vertex_list is None:
                raise ValueError("Found 'v' vertex line before an 'o' object definition.")
            if face_list:
                raise ValueError("Found 'v' vertex line after 'f' face lines.")
            x, y, z = float(v.group(1)), float(v.group(2)), float(v.group(3))
            if invert_x:
                x = -x
            vertex_list.append((x, y, z))
        elif f := f_re.match(line):
            if vertex_list is None:
                raise ValueError("Found 'f' face line before an 'o' object definition.")
            if not vertex_list:
                raise ValueError("Found 'f' face line before any 'v' vertex lines.")
            # Switch to 0-indexing, localize vertex indices, and insert zero that appears between triplets in HKX.
            face = (
                int(f.group(1)) - global_v_i - 1,
                int(f.group(2)) - global_v_i - 1,
                int(f.group(3)) - global_v_i - 1,
            )
            face_list.append(face)
        else:
            pass  # ignore all other lines

    # Finish final mesh.
    meshes.append((np.array(vertex_list), np.array(face_list)))

    return meshes
