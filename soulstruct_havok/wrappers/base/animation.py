from __future__ import annotations

import abc
import logging
import typing as tp

from soulstruct_havok.utilities.maths import TRSTransform, Vector4
from soulstruct_havok.types import hk2010, hk2014, hk2015, hk2018
from soulstruct_havok.spline_compression import SplineCompressedAnimationData

from .core import BaseWrapperHKX

_LOGGER = logging.getLogger(__name__)


ANIMATION_TYPING = tp.Union[
    hk2010.hkaAnimation, hk2014.hkaAnimation, hk2015.hkaAnimation, hk2018.hkaAnimation,
]
ANIMATION_BINDING_TYPING = tp.Union[
    hk2010.hkaAnimationBinding, hk2014.hkaAnimationBinding, hk2015.hkaAnimationBinding, hk2018.hkaAnimationBinding,
]
INTERLEAVED_ANIMATION_TYPES = (
    hk2010.hkaInterleavedUncompressedAnimation, hk2015.hkaInterleavedUncompressedAnimation,
)
INTERLEAVED_ANIMATION_TYPING = tp.Union[
    hk2010.hkaInterleavedUncompressedAnimation, hk2015.hkaInterleavedUncompressedAnimation,
]
SPLINE_ANIMATION_TYPES = (
    hk2010.hkaSplineCompressedAnimation, hk2015.hkaSplineCompressedAnimation, hk2018.hkaSplineCompressedAnimation,
)
SPLINE_ANIMATION_TYPING = tp.Union[
    hk2015.hkaSplineCompressedAnimation, hk2018.hkaSplineCompressedAnimation,
]
DEFAULT_ANIMATED_REFERENCE_FRAME_TYPES = (
    hk2015.hkaDefaultAnimatedReferenceFrame, hk2018.hkaDefaultAnimatedReferenceFrame
)
DEFAULT_ANIMATED_REFERENCE_FRAME_TYPING = tp.Union[
    hk2015.hkaDefaultAnimatedReferenceFrame, hk2018.hkaDefaultAnimatedReferenceFrame
]


class BaseAnimationHKX(BaseWrapperHKX, abc.ABC):
    """Loads HKX objects that are found in an "Animation" HKX file (inside `anibnd` binder, e.g. `a00_3000.hkx`)."""

    animation: ANIMATION_TYPING
    animation_binding: ANIMATION_BINDING_TYPING

    # Loaded upon first use or explicit `load_spline_data()` call. Will be resaved on `pack()` if present, or with
    # explicit `save_spline_data()` call.
    spline_data: tp.Optional[SplineCompressedAnimationData] = None

    # Loaded upon first use or explicit `load_interleaved_data()` call. Will be resaved on `pack()` if present, or with
    # explicit `save_spline_data()` call. All this data does is split the frame transforms into separate 'track' lists.
    interleaved_data: list[list[TRSTransform]] = None

    def create_attributes(self):
        animation_container = self.get_variant_index(0, "hkaAnimationContainer")
        self.animation = animation_container.animations[0]
        self.animation_binding = animation_container.bindings[0]

        if self.is_interleaved:  # basic enough to do outomatically
            self.load_interleaved_data()

    def load_spline_data(self, reload=False):
        if self.is_spline:
            self.animation: SPLINE_ANIMATION_TYPING
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
        """NOTE: If any animation properties such as `duration` or `numFrames` changes, you must set those yourself.

        This method will only modify these members using the spline data:
            data
            numBlocks
            floatBlockOffsets
            numberOfTransformTracks
        """
        if self.is_spline:
            self.animation: SPLINE_ANIMATION_TYPING
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
            self.animation: INTERLEAVED_ANIMATION_TYPING
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
            self.animation: INTERLEAVED_ANIMATION_TYPING
            if not self.interleaved_data:
                raise ValueError("Interleaved data has not been loaded yet. Nothing to save.")
            qs_transform_cls = self.TYPES_MODULE.hkQsTransform
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
            if isinstance(extracted_motion, DEFAULT_ANIMATED_REFERENCE_FRAME_TYPES):
                return [Vector4(v) for v in extracted_motion.referenceFrameSamples]
        raise TypeError("No root motion for this animation reference frame class.")

    def set_reference_frame_samples(self, samples: list[Vector4]):
        if self.animation.extractedMotion:
            extracted_motion = self.animation.extractedMotion
            if isinstance(extracted_motion, DEFAULT_ANIMATED_REFERENCE_FRAME_TYPES):
                extracted_motion.referenceFrameSamples = samples
                return
        raise TypeError("No root motion for this animation reference frame class.")

    def set_animation_duration(self, duration: float):
        """Set duration in both the animation and (if applicable) the reference frame."""
        self.animation.duration = duration
        extracted_motion = self.animation.extractedMotion
        if isinstance(extracted_motion, DEFAULT_ANIMATED_REFERENCE_FRAME_TYPES):
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
        """
        if self.is_spline:
            self.animation: SPLINE_ANIMATION_TYPING
            self.load_spline_data()
            self.spline_data.apply_transform_to_all_track_translations(transform)
        elif self.is_interleaved:
            self.animation: INTERLEAVED_ANIMATION_TYPING
            self.load_interleaved_data()
            for frame in self.interleaved_data:
                for track_index in range(len(frame)):
                    frame[track_index].translation = transform.transform_vector(frame[track_index].translation)
        else:
            raise TypeError(
                f"Animation is not interleaved or spline-compressed: {type(self.animation)}. Cannot transform data."
            )

        self.try_transform_root_motion(transform)

    def scale(self, factor: float):
        """Apply a simple scaling transformation.

        Note that this scales the `translate` data of each bone transform, NOT its `scale` data. This modifies the
        bones in their parent's frame of reference, rather than scaling the bone's frame of reference itself (though
        you could achieve the same result that way).
        """
        self.transform(TRSTransform(scale=factor))

    def reverse(self):
        """Reverses all control points/static transforms, and also root motion (reference frame samples)."""
        if self.is_spline:
            self.animation: SPLINE_ANIMATION_TYPING
            if not self.spline_data:
                self.load_spline_data()
            self.spline_data.reverse()
        elif self.is_interleaved:
            self.animation: INTERLEAVED_ANIMATION_TYPING
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
        """Modify animation data/class in place, from `hkaSplineCompressedAnimation` to
        `hkaInterleavedUncompressedAnimation`.

        Note that this is much more complicated to reverse: the entire Havok file must be downgraded to 2010,
        converted with an executable compiled by Horkrux, and upgraded back to the desired version.
        """
        if not self.is_spline:
            raise TypeError("Animation is not spline-compressed. Cannot convert to interleaved.")
        self.animation: SPLINE_ANIMATION_TYPING
        if not self.spline_data:
            self.load_spline_data()

        try:
            interleaved_cls = self.TYPES_MODULE.hkaInterleavedUncompressedAnimation
        except AttributeError:
            raise TypeError("No `hkaInterleavedUncompressedAnimation` class exists for this Havok version.")
        interleaved_cls: tp.Type[INTERLEAVED_ANIMATION_TYPING]

        self.interleaved_data = self.spline_data.to_interleaved_transforms(
            self.animation.numFrames,
            self.animation.maxFramesPerBlock,
        )

        # Save interleaved data to concatenated list (for writing directly to new Havok instance).
        qs_transform_cls = self.TYPES_MODULE.hkQsTransform
        transforms = []
        for frame in self.interleaved_data:
            transforms += [qs_transform_cls.from_trs_transform(t) for t in frame]

        # TODO: Some arguments will differ for older versions. Move to abstract method.
        self.animation = interleaved_cls(
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
        animation_container = self.get_variant_index(0, "hkaAnimationContainer")
        animation_container.animations = [self.animation]

        self.spline_data = None

    def pack(self, hk_format="") -> bytes:
        if self.is_spline and self.spline_data:
            self.save_spline_data()
        elif self.is_interleaved and self.interleaved_data:
            self.save_interleaved_data()
        return super().pack(hk_format)

    @property
    def is_spline(self):
        try:
            spline_cls = self.TYPES_MODULE.hkaSplineCompressedAnimation
        except AttributeError:
            return False
        return isinstance(self.animation, spline_cls)

    @property
    def is_interleaved(self):
        try:
            interleaved_cls = self.TYPES_MODULE.hkaInterleavedUncompressedAnimation
        except AttributeError:
            return False
        return isinstance(self.animation, interleaved_cls)

    @property
    def track_count(self):
        return self.animation.numberOfTransformTracks

    @property
    def frame_count(self):
        if self.is_spline:
            self.animation: SPLINE_ANIMATION_TYPING
            return self.animation.numFrames
        elif self.is_interleaved:
            self.animation: INTERLEAVED_ANIMATION_TYPING
            return len(self.animation.transforms) // self.animation.numberOfTransformTracks
        raise TypeError("Cannot infer animation frame count from non-spline, non-interleaved animation type.")
