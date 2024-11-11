from __future__ import annotations

__all__ = [
    "BaseAnimationHKX",
]

import abc
import logging
import typing as tp
from dataclasses import dataclass

from soulstruct_havok.types import hk, hk550
from soulstruct_havok.utilities.maths import TRSTransform, Vector4, float32

from ..core import BaseWrappedHKX
from ..type_vars import *
from .animation_container import AnimationContainer

if tp.TYPE_CHECKING:
    import numpy as np
    from soulstruct_havok.spline_compression import SplineCompressedAnimationData
    from ..skeleton import BaseSkeletonHKX


_LOGGER = logging.getLogger("soulstruct_havok")


@dataclass(slots=True)
class BaseAnimationHKX(BaseWrappedHKX, abc.ABC):
    """Animation HKX file inside a `.anibnd` Binder (with animation ID).

    NOTE: FromSoft animation files/containers never seem to contain more than one animation.
    """

    animation_container: AnimationContainer = None

    def __post_init__(self):
        self.animation_container = AnimationContainer(
            self.TYPES_MODULE, self.get_variant(0, *ANIMATION_CONTAINER_T.__constraints__))

    @classmethod
    def get_default_hkx_kwargs(cls) -> dict[str, tp.Any]:
        """Overridden by packfile-using Havok versions to create their headers automatically."""
        return dict(
            hk_format=cls.get_default_hk_format(),
            hk_version=cls.get_version_string(),
        )

    @classmethod
    def get_default_animated_reference_frame(cls, root_motion_array: np.ndarray, frame_rate: float = 30.0) -> hk:
        """Create a new `hkaDefaultAnimatedReferenceFrame` instance from a root motion array."""
        if root_motion_array.shape[1] != 4:
            raise ValueError("Root motion array must have four columns: X, Y, Z, and Y rotation.")

        duration = (root_motion_array.shape[0] - 1) / frame_rate

        ref_frame_class = cls.TYPES_MODULE.hkaDefaultAnimatedReferenceFrame  # type: type[hk]
        ref_frame_kwargs = dict(
            up=Vector4((0.0, 1.0, 0.0, 0.0)),
            forward=Vector4((0.0, 0.0, 1.0, 0.0)),
            duration=float32(duration),
            referenceFrameSamples=root_motion_array,
        )
        if ref_frame_class.has_member("frameType"):  # added between 2010 and 2014
            ref_frame_kwargs["frameType"] = 0

        # noinspection PyArgumentList
        return ref_frame_class(**ref_frame_kwargs)

    @classmethod
    def from_minimal_data_interleaved(
        cls,
        frame_transforms: list[list[TRSTransform]],  # outer list is frames, inner list is tracks (must be regular)
        transform_track_bone_indices: list[int],
        root_motion_array: np.ndarray | None = None,  # four columns: X, Y, Z, Y rotation
        original_skeleton_name="master",
        frame_rate: float = 30.0,
        skeleton_for_armature_to_local: BaseSkeletonHKX = None,
        track_names: list[str] = (),
    ) -> tp.Self:
        """Create an interleaved, uncompressed `BaseAnimationHKX` instance from scratch by filling only the critical
        Havok fields.

        `frame_transforms`, as passed in, should be nested lists of frame transforms (i.e. indexed by frame FIRST and
        track SECOND). These transforms will be flattened into one list of `hkQsTransform` instances for the interleaved
        Havok animation data. The number of frames (minus 1) will be divided by `frame_rate` to calculate the duration.

        Note that `frame_count` (`numFrames`) is not needed for this class, unlike spline-compressed animations, as it
        is immediately inferrable from the data size (divided by track count).

        If `skeleton_for_armature_to_local` is given, it is assumed that `frame_transforms` are currently in armature
        space and require conversion to local space, which can only be done by providing the skeleton (so the 'track
        hierarchy' can be determined). It should NOT be given if `frame_transforms` are already in local space.

        Track names are optional and will be written to track annotations if given. Length of names must match track
        count in this case.
        """
        if track_names and len(track_names) != len(transform_track_bone_indices):
            raise ValueError(
                f"Number of track names ({len(track_names)}) does not match number of track bone indices "
                f"({len(transform_track_bone_indices)})."
            )

        if len(frame_transforms) < 2:
            raise ValueError("Animation must have at least two frames.")

        # Check that all frames have the same number of tracks.
        track_count = len(track_names)
        for i, frame in enumerate(frame_transforms):
            if len(frame) != track_count:
                raise ValueError(f"Frame {i} has {len(frame)} tracks, but all frames must have {track_count} tracks.")
        duration = (len(frame_transforms) - 1) / frame_rate  # seconds between first and last frame

        qs_transforms = []
        if skeleton_for_armature_to_local:
            # First, compute 'track hierarchy' (track parent indices).
            track_parent_indices = []  # type: list[int]
            for track_index in range(len(transform_track_bone_indices)):
                bone_index = transform_track_bone_indices[track_index]
                bone = skeleton_for_armature_to_local.skeleton.bones[bone_index]
                track_parent_index = transform_track_bone_indices.index(bone.parent.index) if bone.parent else -1
                track_parent_indices.append(track_parent_index)

            # Now, convert frame transforms to local space using AnimationContainer method.
            local_frame_transforms = AnimationContainer.armature_transforms_to_local_transforms(
                frame_transforms, track_parent_indices
            )
            for frame in local_frame_transforms:
                qs_transforms += [cls.TYPES_MODULE.hkQsTransform.from_trs_transform(transform) for transform in frame]
        else:
            # We can just use the frame transforms as they are. Otherwise, they will be handled later.
            for frame in frame_transforms:
                qs_transforms += [cls.TYPES_MODULE.hkQsTransform.from_trs_transform(transform) for transform in frame]

        if root_motion_array is not None:
            extracted_motion = cls.get_default_animated_reference_frame(root_motion_array, frame_rate)
        else:
            extracted_motion = None

        if track_names:
            annotation_tracks = [
                cls.TYPES_MODULE.hkaAnnotationTrack(
                    trackName=track_name,
                    annotations=[],
                ) for track_name in track_names
            ]
        else:
            annotation_tracks = []

        animation = cls.TYPES_MODULE.hkaInterleavedUncompressedAnimation(
            # hkaAnimation:
            type=1,  # correct for all Havok versions
            duration=float32(duration),
            numberOfTransformTracks=len(track_names),
            numberOfFloatTracks=0,
            extractedMotion=extracted_motion,
            annotationTracks=annotation_tracks,
            # hkaInterleavedUncompressedAnimation:
            transforms=qs_transforms,
            floats=[],  # never used
        )

        if not cls.get_version_string().startswith(("Havok_", "hk_2010")):
            extra_binding_kwargs = {"partitionIndices": []}
        else:
            extra_binding_kwargs = {}
        binding = cls.TYPES_MODULE.hkaAnimationBinding(
            originalSkeletonName=original_skeleton_name,
            animation=animation,
            transformTrackToBoneIndices=transform_track_bone_indices,
            floatTrackToFloatSlotIndices=[],
            blendHint=0,
            **extra_binding_kwargs,
        )

        root = cls.TYPES_MODULE.hkRootLevelContainer(
            namedVariants=[
                cls.TYPES_MODULE.hkRootLevelContainerNamedVariant(
                    name="Merged Animation Container",
                    className="hkaAnimationContainer",
                    variant=cls.TYPES_MODULE.hkaAnimationContainer(
                        skeletons=[],
                        animations=[animation],
                        bindings=[binding],
                        attachments=[],
                        skins=[],
                    ),
                ),
            ],
        )

        return cls(root=root, **cls.get_default_hkx_kwargs())

    @classmethod
    def from_minimal_data_spline(
        cls,
        spline_data: SplineCompressedAnimationData,
        frame_count: int,
        transform_track_bone_indices: list[int],
        root_motion_array: np.ndarray | None = None,  # four columns: X, Y, Z, Y rotation
        original_skeleton_name="master",
        frame_rate: float = 30.0,
        track_names: list[str] = (),
    ) -> tp.Self:
        """Create a spline-compressed `BaseAnimationHKX` instance from scratch by filling only critical Havok fields.

        Spline-compressed data must already be constructed and passed in.

        Track names are optional and will be written to track annotations if given. Length of names must match track
        count in this case.
        """
        if cls.TYPES_MODULE == hk550:
            raise ValueError("Spline-compressed animations not supported by Havok version 5.5.0 (Demon's Souls).")
        if not hasattr(cls.TYPES_MODULE, "hkaSplineCompressedAnimation"):
            raise ValueError(
                f"Spline-compressed animation class not known for this Havok version ({cls.get_version_string()})."
            )

        data, block_count, track_count = spline_data.pack()

        # NOTE: Float blocks are never actually used, but sometimes there are 1-3 zeroes at the end of the data.
        # I've considered checking for zeroes, but can't guarantee they're not real spline data, so for now, the float
        # block offsets are set to the final offset.
        float_block_offset = len(data)

        if track_names and track_count != len(track_names):
            raise ValueError(
                f"Number of track names ({len(track_names)}) does not match number of tracks in spline data "
                f"({track_count})."
            )
        if track_count != len(transform_track_bone_indices):
            raise ValueError(
                f"Number of track bone indices ({len(transform_track_bone_indices)}) does not match number of tracks "
                f"in spline data ({track_count})."
            )

        duration = (frame_count - 1) / frame_rate  # seconds between first and last frame

        if root_motion_array is not None:
            extracted_motion = cls.get_default_animated_reference_frame(root_motion_array, frame_rate)
        else:
            extracted_motion = None

        # Animation type enumeration changed between 2010 and 2014.
        animation_type = 5 if cls.get_version_string().startswith("hk_2010") else 3  # spline

        if track_names:
            annotation_tracks = [
                cls.TYPES_MODULE.hkaAnnotationTrack(
                    trackName=track_name,
                    annotations=[],
                ) for track_name in track_names
            ]
        else:
            annotation_tracks = []

        animation = cls.TYPES_MODULE.hkaSplineCompressedAnimation(
            # hkaAnimation:
            type=animation_type,
            duration=float32(duration),
            numberOfTransformTracks=track_count,
            numberOfFloatTracks=0,
            extractedMotion=extracted_motion,
            annotationTracks=annotation_tracks,
            # hkaSplineCompressedAnimation:
            numFrames=frame_count,
            numBlocks=block_count,
            maxFramesPerBlock=256,
            maskAndQuantizationSize=336,
            blockDuration=8.5,
            blockInverseDuration=0.11764705926179886,
            frameDuration=float32(1 / frame_rate),
            blockOffsets=[0],
            floatBlockOffsets=[float_block_offset],
            transformOffsets=[],
            floatOffsets=[],
            data=data,
            endian=0,  # little-endian
        )

        binding = cls.TYPES_MODULE.hkaAnimationBinding(
            originalSkeletonName=original_skeleton_name,
            animation=animation,
            transformTrackToBoneIndices=transform_track_bone_indices,
            floatTrackToFloatSlotIndices=[],
            partitionIndices=[],
            blendHint=0,
        )

        root = cls.TYPES_MODULE.hkRootLevelContainer(
            namedVariants=[
                cls.TYPES_MODULE.hkRootLevelContainerNamedVariant(
                    name="Merged Animation Container",
                    className="hkaAnimationContainer",
                    variant=cls.TYPES_MODULE.hkaAnimationContainer(
                        skeletons=[],
                        animations=[animation],
                        bindings=[binding],
                        attachments=[],
                        skins=[],
                    ),
                ),
            ],
        )
        return cls(root=root, **cls.get_default_hkx_kwargs())

    def get_spline_hkx(self) -> tp.Self:
        """Get a spline-compressed version of this interleaved animation.

        Implemented per subclass and generally involves a round trip to hk2010.
        """
        raise TypeError(f"{self.__class__.__name__} cannot be spline-compressed by Soulstruct.")

    def __repr__(self):
        if self.animation_container.is_spline:
            return f"{self.__class__.__name__}(<SplineCompressed>)"
        if self.animation_container.is_interleaved:
            return f"{self.__class__.__name__}(<Interleaved>)"
        return f"{self.__class__.__name__}(<Unknown Type>)"