from __future__ import annotations

__all__ = ["AnimationContainer"]

import copy
import logging
import typing as tp

import numpy as np

from soulstruct.havok.enums import HavokModule
from soulstruct.havok.exceptions import TypeNotDefinedError
from soulstruct.havok.spline_compression import SplineCompressedAnimationData
from soulstruct.havok.utilities.maths import TRSTransform, Vector3, Vector4

from soulstruct.havok.fromsoft.base.type_vars import (
    QS_TRANSFORM_T,
    ANIMATION_CONTAINER_T,
    ANIMATION_T,
    ANIMATION_BINDING_T,
    INTERLEAVED_ANIMATION_T,
    SPLINE_ANIMATION_T,
    DEFAULT_ANIMATED_REFERENCE_FRAME_T,
)

if tp.TYPE_CHECKING:
    from ..skeleton import Skeleton

_LOGGER = logging.getLogger(__name__)


class AnimationContainer(tp.Generic[
    ANIMATION_CONTAINER_T, ANIMATION_T, ANIMATION_BINDING_T,
    INTERLEAVED_ANIMATION_T, SPLINE_ANIMATION_T, DEFAULT_ANIMATED_REFERENCE_FRAME_T
]):
    """Manages/manipulates a Havok animation container containing a single animation and a single binding.

    NOTE: Does not manage `hkaSkeleton` inside container. See `fromsoft.base.skeleton.Skeleton` for that.
    """

    havok_module: HavokModule
    hkx_container: ANIMATION_CONTAINER_T

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

    def __init__(self, havok_module: HavokModule, hkx_animation_container: ANIMATION_CONTAINER_T):
        self.havok_module = havok_module
        self.hkx_container = hkx_animation_container
        self.spline_data = None
        self.interleaved_data = None

        if hkx_animation_container.animations and self.is_interleaved:  # basic enough to do outomatically
            self.load_interleaved_data()

    @property
    def hkx_animation(self) -> ANIMATION_T:
        if not self.hkx_container.animations:
            raise ValueError("No animation in container. Cannot use `hkx_animation` shortcut property or its wrappers.")
        return self.hkx_container.animations[0]

    @property
    def hkx_binding(self) -> ANIMATION_BINDING_T:
        return self.hkx_container.bindings[0]

    def load_spline_data(self, reload=False):
        """Spline-compressed data is not loaded automatically."""
        if self.is_spline:
            if self.spline_data is not None and not reload:
                # Already exists. Do nothing.
                return
            # Otherwise, regenerate spline data.
            self.spline_data = SplineCompressedAnimationData(
                data=self.hkx_animation.data,
                transform_track_count=self.hkx_animation.numberOfTransformTracks,
                block_count=self.hkx_animation.numBlocks,
            )
        else:
            raise TypeError(f"Animation type `{type(self.hkx_animation).__name__}` is not spline-compressed.")

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
            self.hkx_animation.data = data
            self.hkx_animation.numBlocks = block_count
            self.hkx_animation.floatBlockOffsets = [len(data) - 4]
            self.hkx_animation.numberOfTransformTracks = track_count
            _LOGGER.info("Saved spline data to animation.")
        else:
            raise TypeError(f"Animation type `{type(self.hkx_animation).__name__}` is not spline-compressed.")

    def load_interleaved_data(self, reload=False):
        if not self.is_interleaved:
            raise TypeError(f"Animation type `{type(self.hkx_animation).__name__}` is not interleaved.")

        if self.interleaved_data is not None and not reload:
            # Already exists. Do nothing.
            return
        # Otherwise, reorganize lists and convert transforms to `TRSTransform`.
        track_count = self.hkx_animation.numberOfTransformTracks
        transforms = self.hkx_animation.transforms
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
            raise TypeError(f"Animation type `{type(self.hkx_animation).__name__}` is not interleaved.")

        if not self.interleaved_data:
            raise ValueError("Interleaved data has not been loaded yet. Nothing to save.")
        qs_transform_type = self.havok_module.get_type_from_var(QS_TRANSFORM_T)
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
            transforms += [qs_transform_type.from_trs_transform(t) for t in frame]
        self.hkx_animation.transforms = transforms
        self.hkx_animation.numberOfTransformTracks = track_count  # guaranteed to be set above
        _LOGGER.info("Saved interleaved data to animation.")

    def get_reference_frame_samples(self) -> np.ndarray:
        """Get reference frame sample array ("root motion") from animation if available.

        The fourth column of the array is Y-axis rotation in radians.
        """
        if not self.hkx_animation.extractedMotion:
            raise ValueError("No `extractedMotion` reference frame exists for this animation.")

        extracted_motion = self.hkx_animation.extractedMotion
        if hasattr(extracted_motion, "referenceFrameSamples"):
            return extracted_motion.referenceFrameSamples

        cls_name = extracted_motion.get_type_name()
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

        if not self.hkx_animation.extractedMotion:
            try:
                ref_frame_type = self.havok_module.get_type_from_var(DEFAULT_ANIMATED_REFERENCE_FRAME_T)
            except TypeNotDefinedError:
                raise ValueError(
                    "No `extractedMotion` animated reference frame ('root motion') exists for this animation and its "
                    f"Havok version ({self.havok_module.get_version_string()}) has no "
                    f"`hkaDefaultAnimatedReferenceFrame` type to store root motion."
                )
            self.hkx_animation.extracted_motion = ref_frame_type(
                up=Vector4((0.0, 1.0, 0.0, 0.0)),
                forward=Vector4((0.0, 0.0, 1.0, 0.0)),
                duration=duration,
                referenceFrameSamples=samples,
            )
            _LOGGER.info("Created new `hkaDefaultAnimatedReferenceFrame` instance for animation root motion samples.")
            return

        extracted_motion = self.hkx_animation.extractedMotion
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
        self.hkx_animation.duration = duration
        extracted_motion = self.hkx_animation.extractedMotion
        if hasattr(extracted_motion, "duration"):
            extracted_motion.duration = duration

    def get_track_annotation_names(self) -> list[str]:
        """Annotations may not be present, which will make this list empty."""
        return [
            annotation_track.trackName
            for annotation_track in self.hkx_animation.annotationTracks
        ]

    def get_track_bone_indices(self) -> list[int]:
        return self.hkx_binding.transformTrackToBoneIndices

    def get_track_index_of_bone(self, bone_index: int):
        try:
            return self.hkx_binding.transformTrackToBoneIndices.index(bone_index)
        except IndexError:
            raise IndexError(f"Bone index {bone_index} has no corresponding track index.")

    def get_bone_index_of_track(self, track_index: int):
        try:
            return self.hkx_binding.transformTrackToBoneIndices[track_index]
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
                f"Animation is not interleaved or spline-compressed: {type(self.hkx_animation)}. Cannot transform data."
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
            self.hkx_animation.transforms = list(reversed(self.hkx_animation.transforms))
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

    def get_track_parent_indices(self, skeleton: Skeleton) -> list[int]:
        """Get a list of parent indices (-1 for root tracks) based on the parent bones of corresponding bones in
        `skeleton`.

        Note that not all bones may be animated! A parent bone of some child may not be animated, in which case the
        animated child bone will be treated as a root bone (-1).

        TODO: Tracks may sometimes 'skip' a generation of bones. I should use the reference pose in this case.
        """
        track_bone_indices = self.hkx_binding.transformTrackToBoneIndices
        track_parent_indices = []  # type: list[int]
        for track_index, bone_index in enumerate(track_bone_indices):
            bone = skeleton.bones[bone_index]
            if bone.parent and bone.parent.index in track_bone_indices:
                track_parent_indices.append(track_bone_indices.index(bone.parent.index))
            else:
                track_parent_indices.append(-1)  # root bone (or bone with non-animated parent)
        return track_parent_indices

    def get_track_child_indices(self, skeleton: Skeleton) -> list[list[int]]:
        """Get a list of lists of child indices for each track in the animation, based on children of corresponding
        bones in `skeleton`.

        Note that not all bones may be animated! A child bone may not be animated, in which case its index will not
        appear.

        TODO: Tracks may sometimes 'skip' a generation of bones. I should use the reference pose in this case.
        """
        track_bone_indices = self.hkx_binding.transformTrackToBoneIndices
        track_child_indices = []  # type: list[list[int]]
        for track_index, bone_index in enumerate(track_bone_indices):
            bone = skeleton.bones[bone_index]
            child_indices = []
            for child_bone in bone.children:
                if child_bone.index in track_bone_indices:
                    child_indices.append(track_bone_indices.index(child_bone.index))
                # Otherwise, ignore non-animated child.
            track_child_indices.append(child_indices)
        return track_child_indices

    def get_root_track_indices(self, skeleton: Skeleton) -> list[int]:
        """Get a list of track indices that correspond to root bones in `skeleton`."""
        track_bone_indices = self.hkx_binding.transformTrackToBoneIndices
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
            raise TypeError(f"Animation type `{type(self.hkx_animation).__name__}` is not interleaved.")
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
            raise TypeError(f"Animation type `{type(self.hkx_animation).__name__}` is not interleaved.")
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

    def to_interleaved_container(self) -> tp.Self:
        """Get a (deep) copy of this animation that uses the interleaved (uncompressed) format.

        These interleaved animations are not suitable for game use, as they are very large, but this is a far more
        useful format for editing (e.g. with Soulstruct for Blender).

        Re-compressing the animation (usually as spline, but as wavelet in Demon's Souls) is much more complicated and
        is handled on a per-game basis with other methods. (It generally involves use of an external Havok executable.)
        """
        if self.is_interleaved:
            raise ValueError("Animation is already interleaved. If you want a copy, do that explicitly.")

        # This base method can only handle spline animations.
        if not self.is_spline:
            raise ValueError(
                "This animation wrapper class can only convert spline-compressed animations to interleaved, not type: "
                f"{type(self.hkx_animation).__name__}"
            )
        if not self.spline_data:
            self.load_spline_data()

        try:
            interleaved_anim_type = self.havok_module.get_type_from_var(INTERLEAVED_ANIMATION_T)
        except TypeNotDefinedError:
            raise TypeNotDefinedError(
                f"No `hkaInterleavedUncompressedAnimation` class exists for "
                f"Havok version {self.havok_module.get_version_string()}."
            )

        interleaved_data = self.spline_data.to_interleaved_transforms(
            self.hkx_animation.numFrames,
            self.hkx_animation.maxFramesPerBlock,
        )

        # Save interleaved data to concatenated list (for writing directly to new Havok instance).
        qs_transform_type = self.havok_module.get_type_from_var(QS_TRANSFORM_T)
        transforms = []
        for frame in interleaved_data:
            transforms += [qs_transform_type.from_trs_transform(t) for t in frame]

        # All `hkaInterleavedUncompressedAnimation` instances have this conversion class method.
        interleaved_animation = interleaved_anim_type.from_spline_animation(self.hkx_animation, transforms)

        interleaved_self = copy.deepcopy(self)
        interleaved_self.hkx_binding.animation = interleaved_animation
        interleaved_self.hkx_container.animations = [interleaved_animation]
        interleaved_self.spline_data = None
        interleaved_self.interleaved_data = interleaved_data
        interleaved_self.save_data()

        return interleaved_self

    @property
    def is_spline(self) -> bool:
        """We check type name rather than animation enum, which is not consistent in all games."""
        return type(self.hkx_animation).__name__.startswith("hkaSpline")

    @property
    def is_interleaved(self) -> bool:
        """We check type name rather than animation enum, which is not consistent in all games."""
        return type(self.hkx_animation).__name__.startswith("hkaInterleaved")

    @property
    def is_wavelet(self) -> bool:
        """Only used in Demon's Souls."""
        return type(self.hkx_animation).__name__.startswith("hkaWavelet")

    @property
    def track_count(self):
        return self.hkx_animation.numberOfTransformTracks

    @property
    def frame_count(self):
        if self.is_spline:
            return self.hkx_animation.numFrames
        elif self.is_interleaved:
            return len(self.hkx_animation.transforms) // self.hkx_animation.numberOfTransformTracks
        raise TypeError("Cannot infer animation frame count from non-spline, non-interleaved animation type.")
