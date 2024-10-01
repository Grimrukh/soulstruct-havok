from __future__ import annotations

__all__ = ["AnimationContainer"]

import logging
import typing as tp
from types import ModuleType

import numpy as np

from soulstruct_havok.spline_compression import SplineCompressedAnimationData
from soulstruct_havok.utilities.maths import TRSTransform, Vector3, Vector4

from soulstruct_havok.fromsoft.base.type_vars import (
    ANIMATION_CONTAINER_T,
    ANIMATION_T,
    ANIMATION_BINDING_T,
    INTERLEAVED_ANIMATION_T,
    SPLINE_ANIMATION_T,
    DEFAULT_ANIMATED_REFERENCE_FRAME_T,
)

if tp.TYPE_CHECKING:
    from ..skeleton import Skeleton

_LOGGER = logging.getLogger("soulstruct_havok")


class AnimationContainer(tp.Generic[
    ANIMATION_CONTAINER_T, ANIMATION_T, ANIMATION_BINDING_T,
    INTERLEAVED_ANIMATION_T, SPLINE_ANIMATION_T, DEFAULT_ANIMATED_REFERENCE_FRAME_T
]):
    """Manages/manipulates a Havok animation container containing a single animation and a single binding.

    NOTE: Does not manage `hkaSkeleton` inside container. See `wrappers.base.skeleton.Skeleton` for that.
    """

    types_module: ModuleType | None
    # TODO: confusing to have the same name as this class. Change to `hkx_animation_container`?
    animation_container: ANIMATION_CONTAINER_T

    # Loaded upon first use or explicit `load_spline_data()` call. Will be resaved on `pack()` if present, or with
    # explicit `save_spline_data()` call.
    spline_data: SplineCompressedAnimationData | None = None

    # Loaded upon first use or explicit `load_interleaved_data()` call. Will be resaved on `pack()` if present, or with
    # explicit `save_spline_data()` call. All this data does is split the frame transforms into separate 'track' lists,
    # since by default, all the tracks and frames are in a single merged list.
    # Note that the outer list is frames and the inner list is tracks (bones)! In other words, iterate like this:
    # ```
    # for frame in self.interleaved_data:
    #     for bone_transforms in frame:
    #         ...
    # ```
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
        if not self.is_interleaved:
            raise TypeError(f"Animation type `{type(self.animation).__name__}` is not interleaved.")

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

    def save_interleaved_data(self):
        """Convert exposed interleaved `TRSTransform` nested lists back to Havok types."""
        if not self.is_interleaved:
            raise TypeError(f"Animation type `{type(self.animation).__name__}` is not interleaved.")

        if not self.interleaved_data:
            raise ValueError("Interleaved data has not been loaded yet. Nothing to save.")
        qs_transform_cls = self.types_module.hkQsTransform
        transforms = []
        track_count = None
        for frame in self.interleaved_data:
            if track_count is None:
                track_count = len(frame)
            elif len(frame) != track_count:
                raise ValueError(
                    f"Interleaved animation data has inconsistent track counts between frames: "
                    f"{track_count} vs {len(frame)}."
                )
            transforms += [qs_transform_cls.from_trs_transform(t) for t in frame]
        self.animation.transforms = transforms
        self.animation.numberOfTransformTracks = track_count  # guaranteed to be set above
        _LOGGER.info("Saved interleaved data to animation.")

    def get_reference_frame_samples(self) -> np.ndarray:
        """Get reference frame sample array ("root motion") from animation if available.

        The fourth column of the array is Y-axis rotation in radians.
        """
        if not self.animation.extractedMotion:
            raise ValueError("No `extractedMotion` reference frame exists for this animation.")

        extracted_motion = self.animation.extractedMotion
        if hasattr(extracted_motion, "referenceFrameSamples"):
            return extracted_motion.referenceFrameSamples

        cls_name = extracted_motion.__class__.__name__
        raise TypeError(f"No reference frame samples (root motion) for animation extracted motion class `{cls_name}`.")

    def set_reference_frame_samples(self, samples: np.ndarray, frame_rate: float = 30.0):
        """Set reference frame sample array ("root motion") in animation if available.

        Duration is calculated from sample count (minus 1) over frame rate.
        """

        if samples.shape[1] == 3:
            # Assume no rotation: add an extra column of zeroes to convert to `hkArray[hkVector4]` format.
            samples = np.c_[samples, np.zeros((samples.shape[0], 1))]
        if samples.shape[1] != 4:
            raise ValueError(
                f"Reference frame samples must have 3 or 4 columns (XYZ + Y rotation), not {samples.shape[1]}."
            )
        if samples.dtype != np.float32:
            samples = samples.astype(np.float32)

        duration = (len(samples) - 1) / frame_rate

        if not self.animation.extractedMotion:

            default_animated_ref_frame_type = getattr(self.types_module, "hkaDefaultAnimatedReferenceFrame", None)
            if default_animated_ref_frame_type is None:
                raise ValueError(
                    "No `extractedMotion` animated reference frame ('root motion') exists for this animation and could "
                    "not create it."
                )

            self.animation.extracted_motion = default_animated_ref_frame_type(
                up=Vector4((0.0, 1.0, 0.0, 0.0)),
                forward=Vector4((0.0, 0.0, 1.0, 0.0)),
                duration=duration,
                referenceFrameSamples=samples,
            )

            _LOGGER.info("Created new `hkaDefaultAnimatedReferenceFrame` instance for animation root motion samples.")
            return

        extracted_motion = self.animation.extractedMotion
        if not hasattr(extracted_motion, "referenceFrameSamples"):
            cls_name = extracted_motion.__class__.__name__
            raise TypeError(
                f"Animation HKX uses a different `hkaAnimatedReferenceFrame` subclass for its extracted (root) motion: "
                f"{cls_name}. Cannot set reference frame samples. (You can set `extractedMotion = None` and call this "
                f"again to create a new `hkaDefaultAnimatedReferenceFrame` instance.)"
            )

        extracted_motion.duration = duration
        extracted_motion.referenceFrameSamples = samples

    def set_animation_duration(self, duration: float):
        """Set `duration` in both the animation and (if applicable) the reference frame."""
        self.animation.duration = duration
        extracted_motion = self.animation.extractedMotion
        if hasattr(extracted_motion, "duration"):
            extracted_motion.duration = duration

    def get_track_names(self) -> list[str]:
        return [
            annotation_track.trackName
            for annotation_track in self.animation.annotationTracks
        ]

    def get_track_bone_indices(self) -> list[int]:
        return self.animation_binding.transformTrackToBoneIndices

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
            if self.spline_data is None:
                raise ValueError("Spline data has not been loaded yet. Nothing to transform.")
            self.spline_data.apply_transform_to_all_track_translations(transform)
        elif self.is_interleaved:
            if self.interleaved_data is None:
                raise ValueError("Interleaved data has not been loaded yet. Nothing to transform.")
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
                raise ValueError("Spline data has not been loaded yet. Nothing to reverse.")
            self.spline_data.reverse()
        elif self.is_interleaved:
            self.animation.transforms = list(reversed(self.animation.transforms))
            if self.interleaved_data:
                # Reload interleaved data if it's already loaded.
                self.load_interleaved_data(reload=True)
        else:
            raise TypeError("Animation is not interleaved or spline-compressed. Cannot reverse data.")

        self.try_reverse_root_motion()

    def try_transform_root_motion(self, transform: TRSTransform) -> bool:
        """Transform root motion vectors if present, or do nothing otherwise."""
        try:
            reference_frame_samples = self.get_reference_frame_samples()
        except TypeError:
            return False
        reference_frame_samples = transform.transform_vector_array(reference_frame_samples)
        self.set_reference_frame_samples(reference_frame_samples)
        return True

    def try_reverse_root_motion(self) -> bool:
        """Reverse root motion vectors if present, or do nothing otherwise."""
        try:
            reference_frame_samples = self.get_reference_frame_samples()
        except TypeError:
            return False
        reference_frame_samples = np.flip(reference_frame_samples, axis=0)
        self.set_reference_frame_samples(reference_frame_samples)
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
            interleaved_cls = self.types_module.hkaInterleavedUncompressedAnimation  # type: INTERLEAVED_ANIMATION_T
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

        # All `hkaInterleavedUncompressedAnimation` instances have this conversion class method.
        interleaved_animation = interleaved_cls.from_spline_animation(self.animation, transforms)

        # Set Havok instance and binding.
        self.animation_container.animations = [interleaved_animation]
        self.animation_binding.animation = interleaved_animation

        self.spline_data = None

    def get_track_parent_indices(self, skeleton: Skeleton) -> list[int]:
        """Get a list of parent indices (-1 for root tracks) based on the parent bones of corresponding bones in
        `skeleton`."""
        track_bone_indices = self.animation_binding.transformTrackToBoneIndices
        track_parent_indices = []  # type: list[int]
        for track_index in range(len(track_bone_indices)):
            bone_index = track_bone_indices[track_index]
            bone = skeleton.bones[bone_index]
            track_parent_indices.append(track_bone_indices.index(bone.parent.index) if bone.parent else -1)
        return track_parent_indices

    def get_track_child_indices(self, skeleton: Skeleton) -> list[list[int]]:
        """Get a list of lists of child indices for each track in the animation, based on children of corresponding
        bones in `skeleton`."""
        track_bone_indices = self.animation_binding.transformTrackToBoneIndices
        track_child_indices = []  # type: list[list[int]]
        for track_index in range(len(track_bone_indices)):
            bone_index = track_bone_indices[track_index]  # will almost always be the same, but being safe
            bone = skeleton.bones[bone_index]
            child_indices = [track_bone_indices.index(child_bone.index) for child_bone in bone.children]
            track_child_indices.append(child_indices)
        return track_child_indices

    def get_root_track_indices(self, skeleton: Skeleton) -> list[int]:
        """Get a list of track indices that correspond to root bones in `skeleton`."""
        track_bone_indices = self.animation_binding.transformTrackToBoneIndices
        root_track_indices = []  # type: list[int]
        for track_index in range(len(track_bone_indices)):
            bone_index = track_bone_indices[track_index]  # will almost always be the same, but being safe
            bone = skeleton.bones[bone_index]
            if not bone.parent:
                root_track_indices.append(track_index)
        return root_track_indices

    def get_interleaved_data_in_armature_space(self, skeleton: Skeleton) -> list[list[TRSTransform]]:
        """Transform all interleaved frames (in local HKX bone space) to armature-space transforms.

        Preserves ordering of tracks, which should almost always match bone ordering, but does not necessarily need to.
        Does NOT modify this instance.
        """
        if not self.is_interleaved:
            raise TypeError(f"Animation type `{type(self.animation).__name__}` is not interleaved.")
        if not self.interleaved_data:
            self.load_interleaved_data()

        track_child_indices = self.get_track_child_indices(skeleton)
        root_track_indices = self.get_root_track_indices(skeleton)
        return self.local_transforms_to_armature_transforms(
            self.interleaved_data, track_child_indices, root_track_indices
        )

    @staticmethod
    def local_transforms_to_armature_transforms(
        local_space_frames: list[list[TRSTransform]],
        track_child_indices: list[list[int]],
        root_track_indices: list[int],
    ) -> list[list[TRSTransform]]:
        """Use given 'track hierarchy' to transform all frames from local space to armature space.

        The list of root tracks is required to start the recursive transformations.
        """
        arma_space_frames = []  # type: list[list[TRSTransform]]

        for frame_local_transforms in local_space_frames:

            arma_space_track_transforms = [TRSTransform.identity() for _ in range(len(frame_local_transforms))]

            def track_local_to_parent(track_index_: int, parent_transform: TRSTransform):
                arma_space_track_transforms[track_index_] = parent_transform @ frame_local_transforms[track_index_]
                # Recur on children, using this bone's just-computed armature-space transform.
                for child_track_index in track_child_indices[track_index_]:
                    track_local_to_parent(child_track_index, arma_space_track_transforms[track_index_])

            for root_track_index in root_track_indices:
                # Start recurring transformer on root tracks. (Their local space IS armature space.)
                track_local_to_parent(root_track_index, TRSTransform.identity())

            arma_space_frames.append(arma_space_track_transforms)

        return arma_space_frames

    def set_interleaved_data_from_armature_space(
        self, skeleton: Skeleton, armature_space_frames: list[list[TRSTransform]]
    ):
        """Convert `frames` (list of lists of transforms in armature space) to local HKX bone space and set to
        interleaved data of this animation."""
        if not self.is_interleaved:
            raise TypeError(f"Animation type `{type(self.animation).__name__}` is not interleaved.")
        if not self.interleaved_data:
            self.load_interleaved_data()

        track_parent_indices = self.get_track_parent_indices(skeleton)
        self.interleaved_data = self.armature_transforms_to_local_transforms(
            armature_space_frames, track_parent_indices
        )

    @staticmethod
    def armature_transforms_to_local_transforms(
        armature_space_frames: list[list[TRSTransform]],
        track_parent_indices: list[int],
    ) -> list[list[TRSTransform]]:
        """Use given 'track hierarchy' to transform all frames from armature space to each track's (bone's ) space."""
        local_space_frames = []  # type: list[list[TRSTransform]]

        for frame_armature_transforms in armature_space_frames:

            local_space_track_transforms = []

            # Converting back from complete armature space to local space is easy and requires no recursion, as we
            # only need to pre-multiply by the inverse of the parent's armature space transform (already known).
            parent_inverse_matrices = {}  # type: dict[int, TRSTransform]
            for track_index, armature_transform in enumerate(frame_armature_transforms):
                if track_parent_indices[track_index] == -1:
                    # Root track, so local space is armature space.
                    local_space_track_transforms.append(armature_transform)
                else:
                    # Non-root track, so local space is parent's local space.
                    parent_index = track_parent_indices[track_index]
                    if track_parent_indices[track_index] not in parent_inverse_matrices:
                        parent_inverse_matrices[parent_index] = frame_armature_transforms[parent_index].inverse()
                    inv_parent_armature_transform = parent_inverse_matrices[parent_index]
                    local_space_transform = inv_parent_armature_transform @ armature_transform
                    local_space_track_transforms.append(local_space_transform)

            local_space_frames.append(local_space_track_transforms)

        return local_space_frames

    def load_data(self):
        """Load managed spline or interleaved data. Should be called after reading HKX file."""
        if self.is_spline:
            self.load_spline_data()
        elif self.is_interleaved:
            self.load_interleaved_data()

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
