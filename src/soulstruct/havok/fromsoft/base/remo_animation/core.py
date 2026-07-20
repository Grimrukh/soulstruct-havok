"""Base classes for various common Havok file types, with wrappers and variant indices for their basic contents.

Must be overridden by each Havok version to provide the correct `hk` types module.
"""
from __future__ import annotations

__all__ = ["BaseRemoAnimationHKX",]

import abc
import logging
from dataclasses import dataclass

from soulstruct.havok.fromsoft.base import BaseAnimationHKX, BaseSkeletonHKX
from soulstruct.havok.utilities.maths import TRSTransform

from ..animation import AnimationContainer
from ..skeleton import Skeleton, Bone
from ..type_vars import *

_LOGGER = logging.getLogger(__name__)


class BaseRemoAnimationHKX(BaseAnimationHKX, abc.ABC):
    """HKX animation file that animates multiple MSB Parts in a single continuous camera cut in a cutscene.

    Always contains a multi-Part HKX skeleton. Here, each root bone is the name of an `MSBPart` model manipulated in
    this camera cut of the REMO cutscene (each with child bones corresponding to the actual bones of that model, if
    applicable).

    NOTE: If any bone in an MSBPart is NOT animated by the cutscene (e.g. the top-level "Master" bone of a character),
    the rest pose of that bone will be ignored. This is important when computing pose basis matrices in Blender. (This
    is actually true for HKX animations in general; animation transforms are local to the parent's animation transform
    and do not care about the rest pose. The rest pose is only relevant for how bound meshes are deformed. It is only
    extra relevant here because top-level bones are generally never skipped in standard HKX animations.)
    """

    skeleton: Skeleton = None

    def __post_init__(self):
        super().__post_init__()  # set `self.animation_container`
        hka_animation_container = self.get_variant(0, *ANIMATION_CONTAINER_T.__constraints__)
        self.skeleton = Skeleton(self.HAVOK_MODULE, hka_animation_container.skeletons[0])

    def get_root_bones_by_name(self) -> dict[str, Bone]:
        """Returns a dictionary mapping each root bone part name to its root bone, for easy access from FLVER."""
        return {bone.name: bone for bone in self.skeleton.get_root_bones()}

    def get_root_and_part_bones(
        self, remo_part_name: str, bone_prefix=""
    ) -> tuple[Bone, dict[str, Bone]]:
        """Returns the root cutscene bone and a dictionary mapping standard
        bone names to the name-prefixed bones in this HKX (if one exists).

        `bone_prefix` will default to `part_name` if left empty (but that may have a 'AXXBXX_' prefix).
        """
        bone_prefix = bone_prefix or remo_part_name + "_"
        all_root_bones = self.get_root_bones_by_name()
        try:
            part_root_bone = all_root_bones[remo_part_name]
        except KeyError:
            raise ValueError(
                f"`RemoPart` name '{remo_part_name}' has no root bone in this `RemoAnimationHKX`. "
                f"Root bones: {all_root_bones}"
            )

        # Strips the Part's name prefix from each key in this dictionary.
        return part_root_bone, {
            bone.name.removeprefix(bone_prefix): bone
            for bone in part_root_bone.get_all_children()
        }

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
        bone_track_indices = {
            v: i for i, v in enumerate(self.animation_container.hkx_binding.transformTrackToBoneIndices)
        }

        def bone_local_to_world(bone: Bone, world_transform: TRSTransform):
            try:
                track_index = bone_track_indices[bone.index]
            except ValueError:
                # Bone has no track (not animated). We don't recur on child bones below.
                return
            else:
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
