import typing as tp

from soulstruct.utilities.maths import QuatTransform, Vector4
from soulstruct_havok.types import hk2010, hk2014, hk2015, hk2018
from soulstruct_havok.spline_compression import SplineCompressedAnimationData

from .core import BaseWrapperHKX


ANIMATION_TYPING = tp.Union[
    hk2010.hkaAnimation, hk2014.hkaAnimation, hk2015.hkaAnimation, hk2018.hkaAnimation,
]
ANIMATION_BINDING_TYPING = tp.Union[
    hk2010.hkaAnimationBinding, hk2014.hkaAnimationBinding, hk2015.hkaAnimationBinding, hk2018.hkaAnimationBinding,
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


class AnimationHKX(BaseWrapperHKX):
    """Loads HKX objects that are found in an "Animation" HKX file (inside `anibnd` binder, e.g. `a00_3000.hkx`)."""

    animation: ANIMATION_TYPING
    animation_binding: ANIMATION_BINDING_TYPING

    def create_attributes(self):
        animation_container = self.get_variant_index(0, "hkaAnimationContainer")
        self.animation = animation_container.animations[0]
        self.animation_binding = animation_container.bindings[0]

    def get_root_motion(self):
        if isinstance(self.animation, SPLINE_ANIMATION_TYPES) and self.animation.extractedMotion:
            reference_frame = self.animation.extractedMotion
            if isinstance(reference_frame, DEFAULT_ANIMATED_REFERENCE_FRAME_TYPES):
                return reference_frame.referenceFrameSamples
        raise TypeError("No root motion for this animation class/reference frame class.")

    def set_root_motion(self, samples: list[Vector4]):
        if isinstance(self.animation, SPLINE_ANIMATION_TYPES) and self.animation.extractedMotion:
            reference_frame = self.animation.extractedMotion
            if isinstance(reference_frame, DEFAULT_ANIMATED_REFERENCE_FRAME_TYPES):
                reference_frame.referenceFrameSamples = samples
                return
        raise TypeError("No root motion for this animation class/reference frame class.")

    def get_spline_compressed_animation_data(self) -> SplineCompressedAnimationData:
        if isinstance(self.animation, SPLINE_ANIMATION_TYPES):
            return SplineCompressedAnimationData(
                data=self.animation.data,
                transform_track_count=self.animation.numberOfTransformTracks,
                block_count=self.animation.numBlocks,
            )
        raise TypeError("Animation is not spline-compressed. Cannot get data.")

    def set_spline_compressed_animation_data(
        self,
        spline_compressed_data: SplineCompressedAnimationData,
        duration: float = None,
        frame_count: int = None,
        max_frames_per_block: int = None,
        mask_and_quantization_size: int = None,
        float_track_count: int = None,
    ):
        if isinstance(self.animation, SPLINE_ANIMATION_TYPES):
            data, block_count, track_count = spline_compressed_data.pack()
            self.animation.data = data
            self.animation.numBlocks = block_count
            self.animation.floatBlockOffsets = [len(data) - 4]
            self.animation.numberOfTransformTracks = track_count

            # Optional additional attributes to set.
            if duration is not None:
                self.set_animation_duration(duration)
            if frame_count is not None:
                self.animation.numFrames = frame_count
            if max_frames_per_block is not None:
                self.animation.maxFramesPerBlock = max_frames_per_block
            if mask_and_quantization_size is not None:
                self.animation.maskAndQuantizationSize = mask_and_quantization_size
            if float_track_count is not None:
                self.animation.numberOfFloatTracks = float_track_count
        else:
            raise TypeError("Animation is not spline-compressed. Cannot set data.")

    def set_animation_duration(self, duration: float):
        self.animation.duration = duration
        extracted_motion = self.animation.extractedMotion
        if isinstance(extracted_motion, DEFAULT_ANIMATED_REFERENCE_FRAME_TYPES):
            extracted_motion.duration = duration

    def decompress_spline_animation_data(self) -> list[list[QuatTransform]]:
        """Convert spline-compressed animation data to a list of lists (per track) of `QuatTransform` instances."""
        if isinstance(self.animation, SPLINE_ANIMATION_TYPES):
            return self.get_spline_compressed_animation_data().to_transform_track_lists(
                frame_count=self.animation.numFrames,
                max_frames_per_block=self.animation.maxFramesPerBlock
            )
        raise TypeError("Animation is not spline-compressed. Cannot decompress data.")

    def scale(self, factor: float):
        """Modifies all spline/static animation tracks, and also root motion (reference frame samples)."""
        if not isinstance(self.animation, SPLINE_ANIMATION_TYPES):
            raise TypeError("Animation is not spline-compressed. Cannot scale data.")
        animation_data = self.get_spline_compressed_animation_data()
        animation_data.scale(factor)
        self.animation.data = animation_data.pack()[0]  # no chance that block/transform counts have changed

        # Root motion (if present), sans W.
        try:
            reference_frame_samples = self.get_root_motion()
        except TypeError:
            pass
        else:
            for sample in reference_frame_samples:
                # Scale X, Y, and Z only, not W.
                sample.x *= factor
                sample.y *= factor
                sample.z *= factor
            self.set_root_motion(reference_frame_samples)

    def reverse(self):
        """Reverses all control points in all spline tracks, and also root motion (reference frame samples)."""
        if not isinstance(self.animation, SPLINE_ANIMATION_TYPES):
            raise TypeError("Animation is not spline-compressed. Cannot reverse data.")
        reversed_data = self.get_spline_compressed_animation_data().reverse()
        self.animation.data = reversed_data

        # Root motion (if present).
        try:
            reference_frame_samples = self.get_root_motion()
        except TypeError:
            pass
        else:
            self.set_root_motion(list(reversed(reference_frame_samples)))
