from __future__ import annotations

__all__ = ["SkeletonMapper"]

import abc
import logging
import typing as tp
from dataclasses import dataclass
from types import ModuleType

import numpy as np

from soulstruct_havok.utilities.maths import Vector3, Vector4

from ..type_vars import SKELETON_MAPPER_T

_LOGGER = logging.getLogger("soulstruct_havok")


@dataclass(slots=True, repr=False)
class SkeletonMapper(tp.Generic[SKELETON_MAPPER_T], abc.ABC):
    """Wrapper for `hkaSkeletonMapper` Havok type, which maps the bones in a standard HKX skeleton (e.g. the one used
    for animations) to a usually simpler ragdoll skeleton, and vice versa.

    This allows animations to also animate the ragdoll skeleton and its collision contents.
    """

    types_module: ModuleType
    skeleton_mapper: SKELETON_MAPPER_T

    def get_mapper_dict(self) -> dict[str, dict[str, dict]]:
        """Construct a streamlined dictionary of the skeleton mapper for inspection."""
        mapping = self.skeleton_mapper.mapping
        bones_a = mapping.skeletonA.bones
        bones_b = mapping.skeletonB.bones

        default_rotation = np.array((0.0, 0.0, 0.0, 1.0), dtype=np.float32)
        default_scale = np.array((1.0, 1.0, 1.0, 0.0), dtype=np.float32)

        simple_mappings = {}
        for simple in mapping.simpleMappings:
            bone_mapping = simple_mappings[bones_b[simple.boneB].name] = {
                "to_bone": bones_a[simple.boneA].name,
                "translation": simple.aFromBTransform.translation,
            }
            if not np.isclose(simple.aFromBTransform.rotation.data, default_rotation, atol=0.001).all():
                bone_mapping["rotation"] = simple.aFromBTransform.rotation
            if not np.isclose(simple.aFromBTransform.scale.data, default_scale, atol=0.001).all():
                bone_mapping["scale"] = simple.aFromBTransform.scale

        chain_mappings = {}
        for chain in mapping.chainMappings:
            bone_a_names = [bones_a[bone_a].name for bone_a in (chain.startBoneA, chain.endBoneA)]
            bone_b_names = [bones_b[bone_b].name for bone_b in (chain.startBoneB, chain.endBoneB)]
            bone_mapping = chain_mappings[tuple(bone_b_names)] = {
                "to_bones": tuple(bone_a_names),
                "start_translation": chain.startAFromBTransform.translation,
                "end_translation": chain.endAFromBTransform.translation,
            }
            if not (
                np.isclose(chain.startAFromBTransform.rotation.data, default_rotation, atol=0.001).all()
                and np.isclose(chain.endAFromBTransform.rotation.data, default_rotation, atol=0.001).all()
            ):
                bone_mapping["start_rotation"] = chain.startAFromBTransform.rotation
                bone_mapping["end_rotation"] = chain.endAFromBTransform.rotation
            if not (
                np.isclose(chain.startAFromBTransform.scale.data, default_scale, atol=0.001).all()
                and np.isclose(chain.endAFromBTransform.scale.data, default_scale, atol=0.001).all()
            ):
                bone_mapping["start_scale"] = chain.startAFromBTransform.scale
                bone_mapping["end_scale"] = chain.endAFromBTransform.scale

        return {
            "simple": simple_mappings,
            "chain": chain_mappings,
        }

    def scale_all_translations(self, scale_factor: float | Vector3 | Vector4):
        if isinstance(scale_factor, Vector3):
            scale_factor = Vector4.from_vector3(scale_factor)
        for simple in self.skeleton_mapper.mapping.simpleMappings:
            simple.aFromBTransform.translation *= scale_factor
        for chain in self.skeleton_mapper.mapping.chainMappings:
            chain.startAFromBTransform.translation *= scale_factor

    # TODO: repr
