"""Manages inputs and outputs for my `HavokSkeletonMapper` C++ executable.

Not working on this at the moment because, while it does work in principle, the resulting mapping was clearly wrong
in-game, and I never figured out why.

Currently uses `hk2015` types, but theoretically could use any supported Havok version (2010-2018).
"""
from __future__ import annotations

__all__ = ["write_skeleton_mapper_input", "exe_output_to_skeleton_mapper"]

from pathlib import Path

from soulstruct_havok.types.hk2015 import *
from soulstruct_havok.utilities.maths import Vector4, Quaternion


def write_skeleton_mapper_input(skeleton: hkaSkeleton, txt_path: Path):
    """Print skeletons for C++."""
    input_lines = [str(len(skeleton.bones))]
    bone_zip = zip(skeleton.parentIndices, skeleton.bones, skeleton.referencePose)
    for i, (parent_index, bone, ref_pose) in enumerate(bone_zip):
        if parent_index != -1 and parent_index >= i:
            raise ValueError(f"Bad `hkaSkeleton`: Parent index {parent_index} is not less than this bone index {i}.")
        input_lines += [
            bone.name,
            str(bone.lockTranslation),
            str(parent_index),
            f"{ref_pose.translation.x} {ref_pose.translation.y} {ref_pose.translation.z} {ref_pose.translation.w}",
            f"{ref_pose.rotation.x} {ref_pose.rotation.y} {ref_pose.rotation.z} {ref_pose.rotation.w}",
            f"{ref_pose.scale.x} {ref_pose.scale.y} {ref_pose.scale.z} {ref_pose.scale.w}",
        ]
    txt_path.write_text("\n".join(input_lines))


def exe_output_to_skeleton_mapper(
    skeleton_a: hkaSkeleton, skeleton_b: hkaSkeleton, txt_path: Path
) -> hkaSkeletonMapper:
    """Use given skeletons and text file output of `HavokSkeletonMapper` to create `hkaSkeletonMapper`."""

    lines = txt_path.read_text().strip().split("\n")
    simple_mappings = []
    chain_mappings = []
    unmapped_indices = []
    mode = ""
    i = 0

    def read_four_floats():
        floats = [float(f) for f in lines[i].strip().split()]
        return floats

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            continue  # ignore blank lines
        if line == "Simple Mappings:":
            mode = "simple"
            i += 1
            continue
        elif line == "Chain Mappings:":
            mode = "chain"
            i += 1
            continue
        elif line == "Unmapped Bone Indices:":
            mode = "unmapped"
            i += 1
            continue

        if mode == "simple":
            bone_a, bone_b = line.split(" -> ")
            i += 1
            translation = read_four_floats()
            i += 1
            rotation = read_four_floats()
            i += 1
            scale = read_four_floats()
            i += 1
            simple_mappings.append((int(bone_a), int(bone_b), translation, rotation, scale))
        elif mode == "chain":
            bones_a, bones_b = line.split(" -> ")
            start_bone_a, end_bone_a = bones_a.split(" >> ")
            start_bone_b, end_bone_b = bones_b.split(" >> ")
            i += 1
            start_translation = read_four_floats()
            i += 1
            start_rotation = read_four_floats()
            i += 1
            start_scale = read_four_floats()
            i += 1
            end_translation = read_four_floats()
            i += 1
            end_rotation = read_four_floats()
            i += 1
            end_scale = read_four_floats()
            i += 1
            chain_mappings.append(
                (
                    int(start_bone_a), int(end_bone_a), int(start_bone_b), int(end_bone_b),
                    start_translation, start_rotation, start_scale,
                    end_translation, end_rotation, end_scale,
                )
            )
        elif mode == "unmapped":
            unmapped_indices.append(int(line))
            i += 1
        else:
            raise ValueError(f"Unknown mode: {mode}")

    mapping = hkaSkeletonMapperData(
        skeletonA=skeleton_a,
        skeletonB=skeleton_b,
        partitionMap=[],
        simpleMappingPartitionRanges=[],
        chainMappingPartitionRanges=[],
        simpleMappings=[
            hkaSkeletonMapperDataSimpleMapping(
                boneA=bone_a,
                boneB=bone_b,
                aFromBTransform=hkQsTransform(
                    translation=Vector4(translation),
                    rotation=Quaternion(rotation),
                    scale=Vector4(scale),
                ),
            )
            for bone_a, bone_b, translation, rotation, scale in simple_mappings
        ],
        chainMappings=[
            hkaSkeletonMapperDataChainMapping(
                startBoneA=start_bone_a,
                endBoneA=end_bone_a,
                startBoneB=start_bone_b,
                endBoneB=end_bone_b,
                startAFromBTransform=hkQsTransform(
                    translation=Vector4(start_translation),
                    rotation=Quaternion(start_rotation),
                    scale=Vector4(start_scale),
                ),
                endAFromBTransform=hkQsTransform(
                    translation=Vector4(end_translation),
                    rotation=Quaternion(end_rotation),
                    scale=Vector4(end_scale),
                ),
            )
            for (
                start_bone_a, end_bone_a, start_bone_b, end_bone_b,
                start_translation, start_rotation, start_scale,
                end_translation, end_rotation, end_scale
            ) in chain_mappings
        ],
        unmappedBones=unmapped_indices,
        extractedMotionMapping=hkQsTransform.identity(),
        keepUnmappedLocal=True,
        mappingType=0,  # ragdoll
    )

    return hkaSkeletonMapper(mapping=mapping)
