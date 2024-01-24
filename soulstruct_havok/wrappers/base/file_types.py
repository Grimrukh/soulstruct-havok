"""Base classes for various common Havok file types, with wrappers and variant indices for their basic contents.

Must be overridden by each Havok version to provide the correct `hk` types module.
"""
from __future__ import annotations

__all__ = [
    "BaseWrappedHKX",
    "AnimationHKX",
    "CollisionHKX",
    "SkeletonHKX",
    "RagdollHKX",
    "ClothHKX",
    "RemoAnimationHKX",
]

import abc
import logging
import typing as tp
from dataclasses import dataclass
from types import ModuleType

from soulstruct_havok.core import HKX
from soulstruct_havok.types import hk
from soulstruct_havok.utilities.maths import TRSTransform, Vector3, Vector4

from .animation import AnimationContainer
from .skeleton import Skeleton, SkeletonMapper, Bone
from .physics import PhysicsData, ClothPhysicsData
from .type_vars import *

_LOGGER = logging.getLogger("soulstruct_havok")


HK_T = tp.TypeVar("HK_T", bound=hk)


@dataclass(slots=True)
class BaseWrappedHKX(HKX, abc.ABC):

    TYPES_MODULE: tp.ClassVar[ModuleType]

    def get_variant(self, variant_index: int, *valid_types: tp.Type[HK_T]) -> HK_T:
        """Get variant at `variant_index` and check that it is one of the given `valid_types`."""
        variant = self.root.namedVariants[variant_index].variant
        valid_type_names = [t.__name__ for t in valid_types]
        if not any(type(variant) is t for t in valid_types):
            raise TypeError(
                f"HKX variant index {variant_index} has expected type `{variant.__class__.__name__}`, "
                f"which is not in `valid_type_names`: {valid_type_names}"
            )
        return variant


@dataclass(slots=True)
class AnimationHKX(BaseWrappedHKX, abc.ABC):
    """Animation HKX file inside a `.anibnd` Binder (with animation ID).

    NOTE: FromSoft animation files/containers never seem to contain more than one animation.
    """

    animation_container: AnimationContainer = None

    def __post_init__(self):
        super(BaseWrappedHKX, self).__post_init__()
        self.animation_container = AnimationContainer(
            self.TYPES_MODULE, self.get_variant(0, *ANIMATION_CONTAINER_T.__constraints__))


@dataclass(slots=True)
class CollisionHKX(BaseWrappedHKX, abc.ABC):
    """Loads HKX objects that just have collision physics, such as those in `.objbnd` Binders or map collisions."""

    physics_data: PhysicsData = None

    def __post_init__(self):
        super(BaseWrappedHKX, self).__post_init__()
        self.physics_data = PhysicsData(self.TYPES_MODULE, self.get_variant(0, *PHYSICS_DATA_T.__constraints__))


@dataclass(slots=True)
class SkeletonHKX(BaseWrappedHKX, abc.ABC):
    """Skeleton HKX file inside a `.chrbnd` Binder."""

    skeleton: Skeleton = None

    def __post_init__(self):
        super(BaseWrappedHKX, self).__post_init__()
        hka_animation_container = self.get_variant(0, *ANIMATION_CONTAINER_T.__constraints__)
        self.skeleton = Skeleton(self.TYPES_MODULE, hka_animation_container.skeletons[0])


@dataclass(slots=True)
class RagdollHKX(BaseWrappedHKX, abc.ABC):
    """Ragdoll HKX file inside a `.chrbnd` Binder (with model name)."""

    # Animation container does not need to be managed.
    standard_skeleton: Skeleton = None
    ragdoll_skeleton: Skeleton = None
    physics_data: PhysicsData = None
    # Ragdoll instance does not need to be managed.
    ragdoll_to_standard_skeleton_mapper: SkeletonMapper = None
    standard_to_ragdoll_skeleton_mapper: SkeletonMapper = None

    def __post_init__(self):
        super(BaseWrappedHKX, self).__post_init__()
        hka_animation_container = self.get_variant(0, *ANIMATION_CONTAINER_T.__constraints__)
        self.standard_skeleton = Skeleton(self.TYPES_MODULE, hka_animation_container.skeletons[0])
        self.ragdoll_skeleton = Skeleton(self.TYPES_MODULE, hka_animation_container.skeletons[1])
        self.physics_data = PhysicsData(self.TYPES_MODULE, self.get_variant(1, *PHYSICS_DATA_T.__constraints__))

        # NOTE: Ragdoll instance is not needed. It just references physics/skeletons that we already have.
        # ragdoll_instance = variant_property(2, "hkaRagdollInstance")

        # TODO: Confirm these are the right way around (90% sure).
        self.ragdoll_to_standard_skeleton_mapper = SkeletonMapper(
            self.TYPES_MODULE, self.get_variant(3, *SKELETON_MAPPER_T.__constraints__))
        self.standard_to_ragdoll_skeleton_mapper = SkeletonMapper(
            self.TYPES_MODULE, self.get_variant(4, *SKELETON_MAPPER_T.__constraints__))

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
        self.standard_skeleton.scale_all_translations(scale_factor)
        self.ragdoll_skeleton.scale_all_translations(scale_factor)
        self.physics_data.scale_all_translations(scale_factor)
        self.ragdoll_to_standard_skeleton_mapper.scale_all_translations(scale_factor)
        self.standard_to_ragdoll_skeleton_mapper.scale_all_translations(scale_factor)


@dataclass(slots=True)
class ClothHKX(BaseWrappedHKX, abc.ABC):
    """Loads HKX objects that are found in a "Cloth" HKX file (inside `chrbnd` binder, e.g. `c2410_c.hkx`).

    This file is not used for every character - only those with cloth physics (e.g. capes).
    """

    cloth_physics_data: ClothPhysicsData = None

    def __post_init__(self):
        super(BaseWrappedHKX, self).__post_init__()
        self.cloth_physics_data = ClothPhysicsData(
            self.TYPES_MODULE, self.get_variant(0, *PHYSICS_DATA_T.__constraints__)
        )


@dataclass(slots=True)
class RemoAnimationHKX(BaseWrappedHKX, abc.ABC):
    """HKX file that contains a skeleton AND animation data for a single continuous camera cut in a cutscene.

    Here, each root bone is the name of an `MSBPart` model manipulated in this camera cut of the REMO cutscene (each
    with child bones corresponding to the actual bones of that model, if applicable).
    """

    animation_container: AnimationContainer = None
    skeleton: Skeleton = None

    def __post_init__(self):
        super(BaseWrappedHKX, self).__post_init__()
        hka_animation_container = self.get_variant(0, *ANIMATION_CONTAINER_T.__constraints__)
        self.animation_container = AnimationContainer(self.TYPES_MODULE, hka_animation_container)
        self.skeleton = Skeleton(self.TYPES_MODULE, hka_animation_container.skeletons[0])

    # TODO: What does the top-level name of this skeleton mean? Seems to just be first bone, but that's also usually a
    #  collision, so it could be used...?

    def get_root_bones_by_name(self) -> dict[str, Bone]:
        """Returns a dictionary mapping each root bone part name to its root bone, for easy access from FLVER."""
        return {bone.name: bone for bone in self.skeleton.get_root_bones()}

    def get_part_bones(self, part_name: str, root_bone_name="master", bone_prefix="") -> dict[str, Bone]:
        """Returns a dictionary mapping standard bone names to the name-prefixed bones in this HKX (if one exists).

        `bone_prefix` will default to `part_name` if left empty (but that may have a 'AXXBXX_' prefix).
        """
        part_root_bones = self.get_root_bones_by_name()
        if part_name not in part_root_bones:
            raise ValueError(
                f"Part name '{part_name}' has no root bone in this `RemoAnimationHKX`. Bones: {part_root_bones}"
            )
        part_bones = {root_bone_name: part_root_bones[part_name]}
        if not bone_prefix:
            bone_prefix = part_name + "_"
        part_bones |= {
            bone.name.removeprefix(bone_prefix): bone
            for bone in part_root_bones[part_name].get_all_children()
        }
        return part_bones

    def get_all_part_arma_space_transforms_in_frame(
        self, frame_index: int, part_bones: dict[str, Bone] = None, part_name="", root_bone_name="master"
    ) -> dict[str, TRSTransform]:
        """Resolve all transforms to get armature space transforms of `part_name` at the given `frame_index`.

        Returns a dictionary mapping non-prefixed part bone names to their armature space transforms in this frame.

        Avoid recomputing transforms multiple times; each bone is only processed once, using parents' accumulating
        world transforms.

        NOTE: Unlike the 'local to world' transformations found elsewhere, which are really 'local to armature',
        these REMO animation coordinates are ACTUALLY world space transforms (due to the world space transform applied
        to the root bone).
        """
        if part_bones is None:
            if not part_name:
                raise ValueError("Must provide either `part_bones` or `part_name`.")
            part_bones = self.get_part_bones(part_name, root_bone_name)
        if not self.animation_container.is_interleaved:
            raise TypeError("Can only get bone animation tracks for interleaved animation.")
        self.animation_container.load_interleaved_data()
        if frame_index > len(self.animation_container.interleaved_data):
            raise ValueError(
                f"Frame must be between 0 and {len(self.animation_container.interleaved_data)}, not {frame_index}."
            )

        frame_local_transforms = self.animation_container.interleaved_data[frame_index]
        bone_world_transforms = {bone.name: TRSTransform.identity() for bone in part_bones.values()}
        track_bone_indices = self.animation_container.animation_binding.transformTrackToBoneIndices

        def bone_local_to_world(bone: Bone, world_transform: TRSTransform):
            track_index = track_bone_indices.index(bone.index)
            bone_world_transforms[bone.name] = world_transform @ frame_local_transforms[track_index]
            # Recur on children, using this bone's just-computed world transform.
            for child_bone in bone.children:
                bone_local_to_world(child_bone, bone_world_transforms[bone.name])

        bone_local_to_world(part_bones[root_bone_name], TRSTransform.identity())

        # Map standard FLVER bone names to their world transforms computed above.
        return {
            part_bone_name: bone_world_transforms[part_bones[part_bone_name].name]
            for part_bone_name in part_bones
        }
