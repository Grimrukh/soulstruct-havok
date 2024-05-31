from __future__ import annotations

__all__ = [
    "BaseAnimationHKX",
]

import abc
import logging
import typing as tp
from dataclasses import dataclass

from soulstruct_havok.core import HavokFileFormat
from soulstruct_havok.types import hk2010, hk2014
from soulstruct_havok.utilities.maths import TRSTransform, Vector4

from ..core import BaseWrappedHKX
from ..type_vars import *
from .animation_container import AnimationContainer

if tp.TYPE_CHECKING:
    import numpy as np
    from soulstruct_havok.spline_compression import SplineCompressedAnimationData


_LOGGER = logging.getLogger("soulstruct_havok")


@dataclass(slots=True)
class BaseAnimationHKX(BaseWrappedHKX, abc.ABC):
    """Animation HKX file inside a `.anibnd` Binder (with animation ID).

    NOTE: FromSoft animation files/containers never seem to contain more than one animation.
    """

    animation_container: AnimationContainer = None

    def __post_init__(self):
        super(BaseWrappedHKX, self).__post_init__()
        self.animation_container = AnimationContainer(
            self.TYPES_MODULE, self.get_variant(0, *ANIMATION_CONTAINER_T.__constraints__))

    @classmethod
    def from_minimal_data_interleaved(
        cls,
        frame_transforms: list[list[TRSTransform]],  # outer list is frames, inner list is tracks
        track_names: list[str],
        duration: float,
        transform_track_bone_indices: list[int],
        root_motion_array: np.ndarray | None = None,  # four columns: X, Y, Z, Y rotation
        original_skeleton_name="master",
    ) -> "BaseAnimationHKX":
        """Create an interleaved, uncompressed `BaseAnimationHKX` instance from scratch by filling only the critical Havok
        fields.

        `frame_transforms`, as passed in, should be nested lists of frame transforms (i.e. indexed by frame FIRST and
        track SECOND). These transforms will be flattened into one list of `hkQsTransform` instances for Havok files.

        Note that `frame_count` (`numFrames`) is not needed for this class.
        """
        if cls.TYPES_MODULE == hk2010:
            raise ValueError("Cannot create HKX animation with Havok version 2010.")
        if cls.TYPES_MODULE == hk2014:
            raise ValueError("Cannot create HKX animation with Havok version 2014.")

        if len(track_names) != len(transform_track_bone_indices):
            raise ValueError(
                f"Number of track names ({len(track_names)}) does not match number of track bone indices "
                f"({len(transform_track_bone_indices)})."
            )

        qs_transforms = []
        for frame in frame_transforms:
            qs_transforms += [cls.TYPES_MODULE.hkQsTransform.from_trs_transform(transform) for transform in frame]

        if root_motion_array is not None:
            if root_motion_array.shape[1] != 4:
                raise ValueError("Root motion array must have four columns: X, Y, Z, Y rotation.")
            extracted_motion = cls.TYPES_MODULE.hkaDefaultAnimatedReferenceFrame(
                frameType=0,
                up=Vector4((0.0, 1.0, 0.0, 0.0)),
                forward=Vector4((0.0, 0.0, 1.0, 0.0)),
                duration=duration,
                referenceFrameSamples=root_motion_array,
            )
        else:
            extracted_motion = None

        animation = cls.TYPES_MODULE.hkaInterleavedUncompressedAnimation(
            # hkaAnimation:
            type=3,  # spline
            duration=duration,
            numberOfTransformTracks=len(track_names),
            numberOfFloatTracks=0,
            extractedMotion=extracted_motion,
            annotationTracks=[
                cls.TYPES_MODULE.hkaAnnotationTrack(
                    trackName=track_name,
                    annotations=[],
                ) for track_name in track_names
            ],
            # hkaInterleavedUncompressedAnimation:
            transforms=qs_transforms,
            floats=[],  # never used?
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

        return cls(
            root=root,
            hk_format=HavokFileFormat.Tagfile,
            hk_version=cls.get_version_string(),
        )

    @classmethod
    def from_minimal_data_spline(
        cls,
        spline_data: SplineCompressedAnimationData,
        track_names: list[str],
        duration: float,
        frame_count: int,
        transform_track_bone_indices: list[int],
        root_motion_array: np.ndarray | None = None,  # four columns: X, Y, Z, Y rotation
        original_skeleton_name="master",
    ) -> "BaseAnimationHKX":
        """Create a spline-compressed `BaseAnimationHKX` instance from scratch by filling only the critical Havok fields.

        Spline-compressed data must already be constructed and passed in.
        """
        if cls.TYPES_MODULE == hk2010:
            raise ValueError("Cannot create HKX animation with Havok version 2010.")
        if cls.TYPES_MODULE == hk2014:
            raise ValueError("Cannot create HKX animation with Havok version 2014.")

        data, block_count, track_count = spline_data.pack()

        if track_count != len(track_names):
            raise ValueError(
                f"Number of track names ({len(track_names)}) does not match number of tracks in spline data "
                f"({track_count})."
            )
        if track_count != transform_track_bone_indices:
            raise ValueError(
                f"Number of track bone indices ({len(transform_track_bone_indices)}) does not match number of tracks "
                f"in spline data ({track_count})."
            )

        if root_motion_array is not None:
            if root_motion_array.shape[1] != 4:
                raise ValueError("Root motion array must have four columns: X, Y, Z, Y rotation.")
            extracted_motion = cls.TYPES_MODULE.hkaDefaultAnimatedReferenceFrame(
                frameType=0,
                up=Vector4((0.0, 1.0, 0.0, 0.0)),
                forward=Vector4((0.0, 0.0, 1.0, 0.0)),
                duration=duration,
                referenceFrameSamples=root_motion_array,
            )
        else:
            extracted_motion = None

        animation = cls.TYPES_MODULE.hkaSplineCompressedAnimation(
            # hkaAnimation:
            type=3,  # spline
            duration=duration,
            numberOfTransformTracks=track_count,
            numberOfFloatTracks=0,
            extractedMotion=extracted_motion,
            annotationTracks=[
                cls.TYPES_MODULE.hkaAnnotationTrack(
                    trackName=track_name,
                    annotations=[],
                ) for track_name in track_names
            ],
            # hkaSplineCompressedAnimation:
            numFrames=frame_count,
            numBlocks=block_count,
            maxFramesPerBlock=256,
            maskAndQuantizationSize=336,
            blockDuration=8.5,
            blockInverseDuration=0.11764705926179886,
            frameDuration=0.03333333507180214,  # 30 fps
            blockOffsets=[0],
            floatBlockOffsets=[len(data) - 4],  # last four bytes in `data`
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
        return cls(
            root=root,
            hk_format=HavokFileFormat.Tagfile,
            hk_version=cls.get_version_string(),
        )

    def __repr__(self):
        if self.animation_container.is_spline:
            return f"{self.__class__.__name__}(<SplineCompressed>)"
        if self.animation_container.is_interleaved:
            return f"{self.__class__.__name__}(<Interleaved>)"
        return f"{self.__class__.__name__}(<Unknown Type>)"
