from __future__ import annotations

__all__ = ["AnimationContainer"]

import logging
import typing as tp
from types import ModuleType

from soulstruct_havok.spline_compression import SplineCompressedAnimationData
from soulstruct_havok.utilities.maths import TRSTransform, Vector3, Vector4

from .type_vars import (
    ANIMATION_CONTAINER_T,
    ANIMATION_T,
    ANIMATION_BINDING_T,
    INTERLEAVED_ANIMATION_T,
    SPLINE_ANIMATION_T,
    DEFAULT_ANIMATED_REFERENCE_FRAME_T,
)

_LOGGER = logging.getLogger(__name__)


class AnimationContainer(tp.Generic[
    ANIMATION_CONTAINER_T, ANIMATION_T, ANIMATION_BINDING_T,
    INTERLEAVED_ANIMATION_T, SPLINE_ANIMATION_T, DEFAULT_ANIMATED_REFERENCE_FRAME_T
]):
    """Manages/manipulates a Havok animation container containing a single animation and a single binding.

    NOTE: Does not manage `hkaSkeleton` inside container. See `wrappers.base.skeleton.Skeleton` for that.
    """

    types_module: ModuleType | None
    animation_container: ANIMATION_CONTAINER_T

    # Loaded upon first use or explicit `load_spline_data()` call. Will be resaved on `pack()` if present, or with
    # explicit `save_spline_data()` call.
    spline_data: SplineCompressedAnimationData | None = None

    # Loaded upon first use or explicit `load_interleaved_data()` call. Will be resaved on `pack()` if present, or with
    # explicit `save_spline_data()` call. All this data does is split the frame transforms into separate 'track' lists,
    # since by default, all the tracks and frames are in a single merged list.
    # Note that the outer list is frames and the inner list is bones! In other words, iterate over it like this:
    #     for frame in self.interleaved_data:
    #         for bone_transforms in frame:
    #             ...
    interleaved_data: list[list[TRSTransform]] | None = None

    def __init__(self, types_module: ModuleType, animation_container: ANIMATION_CONTAINER_T):
        self.types_module = types_module
        self.animation_container = animation_container
        self.spline_data = None
        self.interleaved_data = None

        if self.is_interleaved:  # basic enough to do outomatically
            self.load_interleaved_data()

    @property
    def animation(self) -> ANIMATION_T:
        return self.animation_container.animations[0]

    @property
    def animation_binding(self) -> ANIMATION_BINDING_T:
        return self.animation_container.bindings[0]

    def load_spline_data(self, reload=False):
        if self.is_spline:
            if self.spline_data is not None and not reload:
                # Already exists. Do nothing.
                return
            # Otherwise, regenerate spline data.
            self.spline_data = SplineCompressedAnimationData(
                data=self.animation.data,
                transform_track_count=self.animation.numberOfTransformTracks,
                block_count=self.animation.numBlocks,
            )
        else:
            raise TypeError(f"Animation type `{type(self.animation).__name__}` is not spline-compressed.")

    def save_spline_data(self):
        """NOTE: If any animation properties such as `duration` or `numFrames` change, they must be set separately.

        This method will only modify these members using the spline data:
            `data`
            `numBlocks`
            `floatBlockOffsets`
            `numberOfTransformTracks`
        """
        if self.is_spline:
            if not self.spline_data:
                raise ValueError("Spline data has not been loaded yet. Nothing to save.")
            data, block_count, track_count = self.spline_data.pack()
            self.animation.data = data
            self.animation.numBlocks = block_count
            self.animation.floatBlockOffsets = [len(data) - 4]
            self.animation.numberOfTransformTracks = track_count
            _LOGGER.info("Saved spline data to animation.")
        else:
            raise TypeError(f"Animation type `{type(self.animation).__name__}` is not spline-compressed.")

    def load_interleaved_data(self, reload=False):
        if self.is_interleaved:
            if self.interleaved_data is not None and not reload:
                # Already exists. Do nothing.
                return
            # Otherwise, reorganize lists and convert transforms to `TRSTransform`.
            track_count = self.animation.numberOfTransformTracks
            transforms = self.animation.transforms
            if len(transforms) % track_count > 0:
                raise ValueError(
                    f"Number of transforms in interleaved animation data ({len(transforms)}) is not a multiple of the "
                    f"number of transform tracks: {track_count}")
            frame_count = len(transforms) // track_count
            self.interleaved_data = []
            for i in range(frame_count):
                frame = [t.to_trs_transform() for t in transforms[i * track_count:(i + 1) * track_count]]
                self.interleaved_data.append(frame)
        else:
            raise TypeError(f"Animation type `{type(self.animation).__name__}` is not interleaved.")

    def save_interleaved_data(self):
        if self.is_interleaved:
            if not self.interleaved_data:
                raise ValueError("Interleaved data has not been loaded yet. Nothing to save.")
            qs_transform_cls = self.types_module.hkQsTransform
            transforms = []
            for frame in self.interleaved_data:
                transforms += [qs_transform_cls.from_trs_transform(t) for t in frame]
            self.animation.transforms = transforms
            _LOGGER.info("Saved interleaved data to animation.")
        else:
            raise TypeError(f"Animation type `{type(self.animation).__name__}` is not interleaved.")

    def get_reference_frame_samples(self) -> list[Vector4]:
        if self.animation.extractedMotion:
            extracted_motion = self.animation.extractedMotion
            if hasattr(extracted_motion, "referenceFrameSamples"):
                return [Vector4(v) for v in extracted_motion.referenceFrameSamples]
        raise TypeError("No root motion for this animation reference frame class.")

    def set_reference_frame_samples(self, samples: list[Vector4]):
        if self.animation.extractedMotion:
            extracted_motion = self.animation.extractedMotion
            if hasattr(extracted_motion, "referenceFrameSamples"):
                extracted_motion.referenceFrameSamples = samples
                return
        raise TypeError("No root motion for this animation reference frame class.")

    def set_animation_duration(self, duration: float):
        """Set duration in both the animation and (if applicable) the reference frame."""
        self.animation.duration = duration
        extracted_motion = self.animation.extractedMotion
        if hasattr(extracted_motion, "duration"):
            extracted_motion.duration = duration

    def get_track_index_of_bone(self, bone_index: int):
        try:
            return self.animation_binding.transformTrackToBoneIndices.index(bone_index)
        except IndexError:
            raise IndexError(f"Bone index {bone_index} has no corresponding track index.")

    def get_bone_index_of_track(self, track_index: int):
        try:
            return self.animation_binding.transformTrackToBoneIndices[track_index]
        except IndexError:
            raise IndexError(f"There is no animation track with index {track_index}.")

    def transform(self, transform: TRSTransform):
        """Apply `transform` to all animation tracks (control points or static/interleaved values).

        This transforms the `translate` vectors -- that is, bone POSITIONS can be translated, rotated, and/or scaled
        relative to their parent. It does not affect the rotation or scale of the bone transforms (frames).

        Acts upon spline control points for spline-type animation data, which still has the desired result.
        """
        if self.is_spline:
            self.load_spline_data()
            self.spline_data.apply_transform_to_all_track_translations(transform)
        elif self.is_interleaved:
            self.load_interleaved_data()
            for frame in self.interleaved_data:
                for track_index in range(len(frame)):
                    frame[track_index].translation = transform.transform_vector(frame[track_index].translation)
        else:
            raise TypeError(
                f"Animation is not interleaved or spline-compressed: {type(self.animation)}. Cannot transform data."
            )

        self.try_transform_root_motion(transform)

    def scale_all_translations(self, scale_factor: float | Vector3 | Vector4):
        """Apply a simple scaling transformation.

        Note that this scales the `translate` data of each bone transform, NOT its `scale` data. This modifies the
        bones in their parent's frame of reference, rather than scaling the bone's frame of reference itself (though
        you could achieve the same result that way).

        Saves the transformed interleaved/spline data automatically.
        """
        if isinstance(scale_factor, float):
            scale_factor = Vector3((scale_factor, scale_factor, scale_factor))
        elif isinstance(scale_factor, Vector4):
            scale_factor = Vector3((scale_factor.x, scale_factor.y, scale_factor.z))
        self.transform(TRSTransform(scale=scale_factor))

    def reverse(self):
        """Reverses all control points/static transforms and root motion (reference frame samples) in-place."""
        if self.is_spline:
            if not self.spline_data:
                self.load_spline_data()
            self.spline_data.reverse()
        elif self.is_interleaved:
            self.animation.transforms = list(reversed(self.animation.transforms))
        else:
            raise TypeError("Animation is not interleaved or spline-compressed. Cannot reverse data.")

        self.try_reverse_root_motion()

    def try_transform_root_motion(self, transform: TRSTransform) -> bool:
        """Transform root motion vectors if present, or do nothing otherwise."""
        try:
            reference_frame_samples = self.get_reference_frame_samples()
        except TypeError:
            return False
        for i in range(len(reference_frame_samples)):
            reference_frame_samples[i] = transform.transform_vector(reference_frame_samples[i])
        return True

    def try_reverse_root_motion(self) -> bool:
        """Reverse root motion vectors if present, or do nothing otherwise."""
        try:
            reference_frame_samples = self.get_reference_frame_samples()
        except TypeError:
            return False
        self.set_reference_frame_samples(list(reversed(reference_frame_samples)))
        return True

    def spline_to_interleaved(self):
        """Change animation data type in-place from `hkaSplineCompressedAnimation` to
        `hkaInterleavedUncompressedAnimation`.

        Note that this is much more complicated to reverse: the entire Havok file must be downgraded to 2010,
        converted with an executable compiled by Horkrux, and upgraded back to the desired version (which only Havok
        2015 currently supports).
        """
        if not self.is_spline:
            raise TypeError("Animation is not spline-compressed. Cannot convert to interleaved.")
        if not self.spline_data:
            self.load_spline_data()

        try:
            interleaved_cls = self.types_module.hkaInterleavedUncompressedAnimation
        except AttributeError:
            raise TypeError("No `hkaInterleavedUncompressedAnimation` class exists for this Havok version.")

        self.interleaved_data = self.spline_data.to_interleaved_transforms(
            self.animation.numFrames,
            self.animation.maxFramesPerBlock,
        )

        # Save interleaved data to concatenated list (for writing directly to new Havok instance).
        qs_transform_cls = self.types_module.hkQsTransform
        transforms = []
        for frame in self.interleaved_data:
            transforms += [qs_transform_cls.from_trs_transform(t) for t in frame]

        # TODO: Some arguments will differ for older versions. Move to abstract method.
        animation = interleaved_cls(
            memSizeAndFlags=0,
            refCount=0,
            type=1,  # correct for all Havok versions
            duration=self.animation.duration,
            numberOfTransformTracks=self.animation.numberOfTransformTracks,
            numberOfFloatTracks=self.animation.numberOfFloatTracks,
            extractedMotion=self.animation.extractedMotion,
            annotationTracks=self.animation.annotationTracks,
            transforms=transforms,
            floats=[],  # TODO: Not sure if this is ever used.
        )

        # Set Havok instance.
        self.animation_container.animations = [animation]

        self.spline_data = None

    def save_data(self):
        """Save managed spline or interleaved data. Should be called before writing HKX file."""
        if self.is_spline and self.spline_data:
            self.save_spline_data()
        elif self.is_interleaved and self.interleaved_data:
            self.save_interleaved_data()

    @property
    def is_spline(self) -> bool:
        return type(self.animation).__name__ == "hkaSplineCompressedAnimation"

    @property
    def is_interleaved(self) -> bool:
        return type(self.animation).__name__ == "hkaInterleavedUncompressedAnimation"

    @property
    def track_count(self):
        return self.animation.numberOfTransformTracks

    @property
    def frame_count(self):
        if self.is_spline:
            return self.animation.numFrames
        elif self.is_interleaved:
            return len(self.animation.transforms) // self.animation.numberOfTransformTracks
        raise TypeError("Cannot infer animation frame count from non-spline, non-interleaved animation type.")
