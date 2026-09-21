"""Base classes for various common Havok file types, with wrappers and variant indices for their basic contents.

Must be overridden by each Havok version to provide the correct `hk` types module.
"""
from __future__ import annotations

__all__ = ["BaseRemoAnimationHKX", "RemoPartTracks"]

import abc
import logging
import typing as tp
from dataclasses import dataclass, field

from soulstruct.havok.fromsoft.base import BaseAnimationHKX, BaseSkeletonHKX
from soulstruct.havok.utilities.maths import TRSTransform

from ..animation import AnimationContainer
from ..skeleton import Skeleton, Bone
from ..type_vars import *

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class RemoPartTracks:
    """Everything needed to build one MSB Part's bones and tracks of a cutscene cut animation from scratch.

    The cutscene skeleton gives each part a root bone named after the part (`name`, e.g. 'c5350_0001', 'm2510B1',
    'd0000_0010' or 'A10B02_m2350B2A10' for a part of another map) whose track holds the part's world-space transform
    per frame (`root_frames`). Beneath it sit the part's own bones (`bone_names`, un-prefixed; they are written with
    `bone_prefix` prepended, e.g. 'c5350_0001_Pelvis'), in depth-first order with `bone_parent_indices` into
    `bone_names` (-1 = immediate child of the part root). In vanilla files these are the part's ANIBND skeleton bones
    minus its top-level 'Master'/model-name bone, whose children become the part's cutscene root bones.

    `bone_frames[frame][bone]` are the bones' LOCAL (parent-relative) transforms in the cutscene skeleton, where the
    cutscene root bones (parent -1) are relative to identity (NOT to the part root, which the game applies separately
    as root motion). This is exactly what `RemoCut._add_cut_arma_frames()` reads back. Parts without bones (Map Pieces,
    Collisions, Dummies) leave `bone_names` empty.
    """
    name: str
    root_frames: list[TRSTransform]
    bone_prefix: str = ""
    bone_names: list[str] = field(default_factory=list)
    bone_parent_indices: list[int] = field(default_factory=list)
    bone_frames: list[list[TRSTransform]] = field(default_factory=list)

    def __post_init__(self):
        if len(self.bone_parent_indices) != len(self.bone_names):
            raise ValueError(
                f"RemoPartTracks '{self.name}' has {len(self.bone_names)} bone names but "
                f"{len(self.bone_parent_indices)} parent indices."
            )
        for i, parent_index in enumerate(self.bone_parent_indices):
            if not -1 <= parent_index < i:
                raise ValueError(
                    f"RemoPartTracks '{self.name}' bone {i} ('{self.bone_names[i]}') has invalid parent index "
                    f"{parent_index}: parents must precede children (depth-first order) and -1 marks part root bones."
                )
        if self.bone_names:
            if len(self.bone_frames) != len(self.root_frames):
                raise ValueError(
                    f"RemoPartTracks '{self.name}' has {len(self.root_frames)} root frames but "
                    f"{len(self.bone_frames)} bone frames."
                )
            for frame_index, frame in enumerate(self.bone_frames):
                if len(frame) != len(self.bone_names):
                    raise ValueError(
                        f"RemoPartTracks '{self.name}' bone frame {frame_index} has {len(frame)} transforms, not "
                        f"{len(self.bone_names)}."
                    )

    @property
    def frame_count(self) -> int:
        return len(self.root_frames)

    @property
    def prefixed_bone_names(self) -> list[str]:
        return [self.bone_prefix + bone_name for bone_name in self.bone_names]


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

    @classmethod
    def from_remo_part_tracks(
        cls,
        parts: tp.Sequence[RemoPartTracks],
        frame_rate: float = 30.0,
        skeleton_name: str = "",
    ) -> tp.Self:
        """Build an interleaved cutscene cut animation (skeleton + animation + binding) from scratch.

        Bones are laid out part by part: each part's root bone followed by its bones (see `RemoPartTracks`), so the
        skeleton is in depth-first order like vanilla files. Every bone gets a track (also as in vanilla), annotated
        with its name. The reference pose is the first frame of every track (the most common vanilla convention; the
        game animates every bone, so the reference pose is not used for posing). `skeleton_name` defaults to the first
        part's root bone name, which is what vanilla files use (and is also written as the binding's
        `originalSkeletonName`).

        The result is uncompressed; convert it with the spline-compression splice used by cutscene export (build a
        plain `AnimationHKX` from the same local frames, `to_spline_hkx()` it, then replace this file's animation and
        binding), as `to_spline_hkx()` is not defined for cutscene animations.
        """
        if not parts:
            raise ValueError("At least one `RemoPartTracks` is required to build a cutscene animation.")
        frame_count = parts[0].frame_count
        if frame_count < 2:
            raise ValueError("Cutscene animations must have at least two frames.")
        for part in parts:
            if part.frame_count != frame_count:
                raise ValueError(
                    f"All parts must have the same frame count: part '{part.name}' has {part.frame_count} frames, "
                    f"but part '{parts[0].name}' has {frame_count}."
                )

        bone_names = []  # type: list[str]
        parent_indices = []  # type: list[int]
        frame_transforms = [[] for _ in range(frame_count)]  # type: list[list[TRSTransform]]
        for part in parts:
            if part.name in bone_names:
                raise ValueError(f"Duplicate cutscene part root bone name: '{part.name}'.")
            root_index = len(bone_names)
            bone_names.append(part.name)
            parent_indices.append(-1)
            for frame_index in range(frame_count):
                frame_transforms[frame_index].append(part.root_frames[frame_index].copy())
            for bone_index, bone_name in enumerate(part.prefixed_bone_names):
                if bone_name in bone_names:
                    raise ValueError(f"Duplicate cutscene bone name: '{bone_name}' (part '{part.name}').")
                bone_names.append(bone_name)
                parent_index = part.bone_parent_indices[bone_index]
                parent_indices.append(root_index if parent_index == -1 else root_index + 1 + parent_index)
                for frame_index in range(frame_count):
                    frame_transforms[frame_index].append(part.bone_frames[frame_index][bone_index].copy())

        skeleton_name = skeleton_name or parts[0].name
        bone_type = cls.HAVOK_MODULE.get_type("hkaBone")
        qs_transform_type = cls.HAVOK_MODULE.get_type("hkQsTransform")
        skeleton_type = cls.HAVOK_MODULE.get_type("hkaSkeleton")
        # noinspection PyArgumentList
        skeleton = skeleton_type(
            name=skeleton_name,
            parentIndices=parent_indices,
            bones=[bone_type(name=bone_name, lockTranslation=False) for bone_name in bone_names],
            referencePose=[qs_transform_type.from_trs_transform(transform) for transform in frame_transforms[0]],
            referenceFloats=[],
            floatSlots=[],
            localFrames=[],
            partitions=[],
        )

        root = cls.build_interleaved_root(
            frame_transforms,
            transform_track_bone_indices=list(range(len(bone_names))),
            root_motion_array=None,
            original_skeleton_name=skeleton_name,
            frame_rate=frame_rate,
            skeleton_for_armature_to_local=None,  # already local
            track_names=bone_names,
            skeletons=[skeleton],
        )
        return cls(root=root, **cls.get_default_hkx_kwargs())

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
