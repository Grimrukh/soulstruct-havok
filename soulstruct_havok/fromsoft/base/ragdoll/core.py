"""Base classes for various common Havok file types, with wrappers and variant indices for their basic contents.

Must be overridden by each Havok version to provide the correct `hk` types module.
"""
from __future__ import annotations

__all__ = ["BaseRagdollHKX"]

import abc
from dataclasses import dataclass

from soulstruct_havok.utilities.maths import Vector3, Vector4

from ..core import BaseWrappedHKX
from ..skeleton import Skeleton
from ..physics import PhysicsData
from ..type_vars import *
from .skeleton_mapper import SkeletonMapper


class BaseRagdollHKX(BaseWrappedHKX, abc.ABC):
    """Ragdoll HKX file inside a `.chrbnd` Binder (with model name)."""

    # Animation container does not need to be managed.
    animation_skeleton: Skeleton = None
    ragdoll_skeleton: Skeleton = None
    physics_data: PhysicsData = None
    # Ragdoll instance does not need to be managed.
    animation_to_ragdoll_skeleton_mapper: SkeletonMapper = None
    ragdoll_to_animation_skeleton_mapper: SkeletonMapper = None

    def __post_init__(self):
        hka_animation_container = self.get_variant(0, *ANIMATION_CONTAINER_T.__constraints__)
        self.animation_skeleton = Skeleton(self.HAVOK_MODULE, hka_animation_container.skeletons[0])
        self.ragdoll_skeleton = Skeleton(self.HAVOK_MODULE, hka_animation_container.skeletons[1])
        self.physics_data = PhysicsData(self.HAVOK_MODULE, self.get_variant(1, *PHYSICS_DATA_T.__constraints__))

        # NOTE: Ragdoll instance is not needed. It just references physics/skeletons that we already have.
        # ragdoll_instance = variant_property(2, "hkaRagdollInstance")

        self.animation_to_ragdoll_skeleton_mapper = SkeletonMapper(
            self.HAVOK_MODULE, self.get_variant(3, *SKELETON_MAPPER_T.__constraints__))
        self.ragdoll_to_animation_skeleton_mapper = SkeletonMapper(
            self.HAVOK_MODULE, self.get_variant(4, *SKELETON_MAPPER_T.__constraints__))

    def scale_all_translations(self, scale_factor: float | Vector3 | Vector4):
        """Scale all translation information, including:
            - bones in both the standard and ragdoll skeletons
            - rigid body collidables
            - motion state transforms and swept transforms
            - skeleton mapper transforms in both directions

        This is currently working well, though since actual "ragdoll mode" only occurs when certain enemies die, any
        mismatched (and probably harmless) physics will be more of an aesthetic issue.
        """
        if isinstance(scale_factor, Vector3):
            scale_factor = Vector4.from_vector3(scale_factor)
        self.animation_skeleton.scale_all_translations(scale_factor)
        self.ragdoll_skeleton.scale_all_translations(scale_factor)
        self.physics_data.scale_all_translations(scale_factor)
        self.animation_to_ragdoll_skeleton_mapper.scale_all_translations(scale_factor)
        self.ragdoll_to_animation_skeleton_mapper.scale_all_translations(scale_factor)
