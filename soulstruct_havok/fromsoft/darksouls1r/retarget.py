from __future__ import annotations

__all__ = [
    "retarget_animation",
]

import numpy as np
from scipy.optimize import linear_sum_assignment

from soulstruct_havok.fromsoft.darksouls1r.core import AnimationHKX, SkeletonHKX
from soulstruct_havok.fromsoft.darksouls1r.anibnd import ANIBND


def retarget_animation(
    animation_hkx: AnimationHKX,
    skeleton_a_hkx: SkeletonHKX,
    skeleton_b_hkx: SkeletonHKX,
) -> AnimationHKX:
    """Retarget `animation` of `skeleton_a` to a new animation for `skeleton_b`.

    TODO: Loose spec:
        - As spatially-based as possible. Not looking to match bone names. Just want SOME horrible animated mass of
        skeleton B to repeat roughly the same movement, scaled as needed, as the given animation for skeleton A.
    """

    # 1. PREPROCESSING.

    container = animation_hkx.animation_container
    if container.is_spline:
        container = container.to_interleaved_container()

    # Get names and local (hierarchical) reference poses of skeleton bones.
    skeleton_a_ref_pose = skeleton_a_hkx.skeleton.get_reference_poses()
    skeleton_b_ref_pose = skeleton_b_hkx.skeleton.get_reference_poses()
    # Calculate bone lengths of skeletons, which is just the magnitude of their local reference pose translations.
    skeleton_a_bone_lengths = {
        name: transform.translation.get_magnitude()
        for name, transform in skeleton_a_ref_pose.items()
    }
    skeleton_b_bone_lengths = {
        name: transform.translation.get_magnitude()
        for name, transform in skeleton_b_ref_pose.items()
    }
    # Drop 'master' root bones.
    skeleton_a_bone_lengths.pop("master", None)
    skeleton_b_bone_lengths.pop("master", None)
    # Calculate average bone length for each skeleton.
    avg_a_bone_length = np.mean(list(skeleton_a_bone_lengths.values()))
    avg_b_bone_length = np.mean(list(skeleton_b_bone_lengths.values()))

    # Get global skeleton poses for actual retargeting.
    skeleton_a_arma_ref_pose = skeleton_a_hkx.skeleton.get_arma_space_reference_poses()
    skeleton_b_arma_ref_pose = skeleton_b_hkx.skeleton.get_arma_space_reference_poses()

    # Get armature-space frames. Outer list is frames, inner list is bones.
    arma_space_frames = container.get_interleaved_data_in_armature_space(skeleton_a_hkx.skeleton)

    # Convert to NumPy (frames x bones x 10).
    anim_data = np.array([
        [
            [*t.translation, *t.rotation, *t.scale]
            for t in frame
        ]
        for frame in arma_space_frames])

    # 2. RETARGETING.

    # Global scale factor to apply to animation data, e.g. if skeleton B is twice as large, scale_factor = 2.
    scale_factor = avg_b_bone_length / avg_a_bone_length

    # Apply average bone scale factor from above to animation.
    anim_data[:, :, :3] *= scale_factor
    # Also apply it to skeleton A (arma) reference pose for our main spatial retarget.
    for name, transform in skeleton_a_arma_ref_pose.items():
        transform.translation *= scale_factor

    # Prepare reference pose data for mapping. Bone order is preserved from dictionaries.
    bone_positions_a = np.array([
        skeleton_a_arma_ref_pose[name].translation
        for name in skeleton_a_arma_ref_pose
    ])
    bone_positions_b = np.array([
        skeleton_b_arma_ref_pose[name].translation
        for name in skeleton_b_arma_ref_pose
    ])

    # Compute Euclidean distance between each bone's arma reference pose in skeleton A and skeleton B.
    # This will be used to find the best matching bone for each bone in skeleton A.
    distances = np.linalg.norm(bone_positions_a[:, np.newaxis, :] - bone_positions_b[np.newaxis, :, :], axis=2)

    # Employ the Hungarian Algorithm to find the optimal one-to-one bone mapping.
    bone_names_a = list(skeleton_a_arma_ref_pose.keys())
    bone_names_b = list(skeleton_b_arma_ref_pose.keys())
    row_ind, col_ind = linear_sum_assignment(distances)
    bone_map = {bone_names_a[i]: bone_names_b[j] for i, j in zip(row_ind, col_ind)}  # {bone_a: bone_b}
    # TODO: Hungarian algorithm ignores excess bones in the larger skeleton. Those unmapped (either src or dest) bones
    #  need to be handled.
    #   - If the dest skeleton is smaller than the source skeleton, that's good, because every dest bone will be
    #   guaranteed to find a source bone.

    """
    TODO: Thoughts.
        - This approach won't work, I think. 1:1 bone mapping isn't going to cut it.
        - I want a very GENERAL sort of "spatial dragging" of Skeleton B along with Animation A.
        - My algorithm:
            - Use the arma ref poses to "weight" Skeleton B bones to Skeleton A bones, just like weighting a mesh.
            - Then each animation arma transform for a Skeleton B bone is a weighted sum of its arma transforms for its
            weighted Skeleton A bones.
            - Indirectly, it feels like we're still animating the "ghost" of Skeleton A, and Skeleton B is being pulled
            along with it according to our bone mapping. Of course, we bake out that ghost and get the final transforms
            of Skeleton B on every frame.
        - There are probably a few assumptions I can exploit:
            - Every DS1 skeleton probably starts at a 'Pelvis' bone, and I can line these up.
    
    OK, tyhink
    """

    bone_indices_a = {name: i for i, name in enumerate(bone_names_a)}
    bone_indices_b = {name: i for i, name in enumerate(bone_names_b)}

    # Create new animation data array.
    anim_data_b = np.zeros_like(anim_data)

    # Invert bone map.
    bone_map_inv = {v: k for k, v in bone_map.items()}

    for bone_b_name, idx_b in bone_indices_b.items():
        if bone_b_name in bone_map_inv:
            # This dest bone has a source bone mapped to it.
            bone_a_name = bone_map_inv[bone_b_name]
            idx_a = bone_indices_a[bone_a_name]
            # Copy animation data from src to dest bone. (Src data already globally scaled.)
            anim_data_b[:, idx_b, :] = anim_data[:, idx_a, :]
        else:
            # Use rest pose for unmapped bones
            transform = skeleton_b_ref_pose[bone_b_name]
            t = transform.translation
            r = transform.rotation
            s = transform.scale
            anim_data_b[:, idx_b, :3] = t
            anim_data_b[:, idx_b, 3:7] = r
            anim_data_b[:, idx_b, 7:] = s

    # TODO: Finish...


if __name__ == '__main__':
    from soulstruct import DSR_PATH
    _anibnd_src = ANIBND.from_path(DSR_PATH + "/chr/c2240.anibnd.dcx")  # Capra Demon
    _anibnd_src.load_from_entries(0)
    _anibnd_dest = ANIBND.from_path(DSR_PATH + "/chr/c2410.anibnd.dcx")  # Silver Knight
    _anibnd_dest.load_from_entries(0)  # for skeleton

    _skeleton_a = _anibnd_src.skeleton_hkx
    _skeleton_b = _anibnd_dest.skeleton_hkx
    _animation_a = _anibnd_src.animations_hkx[0]  # idle

    _animation_b = retarget_animation(_animation_a, _skeleton_a, _skeleton_b)
