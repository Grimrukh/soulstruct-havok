from __future__ import annotations

import typing as tp
from pathlib import Path

from soulstruct.containers import Binder
from soulstruct.containers.dcx import DCXType
from soulstruct.utilities.maths import QuatTransform, Vector4

from soulstruct_havok.core import HKX
from soulstruct_havok.types.hk2015 import *
from soulstruct_havok.spline_compression import SplineCompressedAnimationData


class HKX2015(HKX):

    root: hkRootLevelContainer

    def __init__(self, file_source, dcx_type: None | DCXType = DCXType.Null, compendium: None | HKX = None):
        super().__init__(file_source, dcx_type=dcx_type, compendium=compendium, hk_format=self.TAGFILE)
        self.create_attributes()

    def create_attributes(self):
        pass


class SkeletonHKX(HKX2015):
    """Loads HKX objects that are found in a "Skeleton" HKX file (inside `anibnd` binder, usually `Skeleton.HKX`)."""

    animationContainer: hkaAnimationContainer
    skeleton: hkaSkeleton

    def create_attributes(self):
        self.skeleton = self.animationContainer.skeletons[0]

    def scale(self, factor: float):
        """Scale all bone translations in place by `factor`."""
        for pose in self.skeleton.referencePose:
            pose.translation = tuple(x * factor for x in pose.translation)

    @classmethod
    def from_anibnd(cls, anibnd_path: Path | str, prefer_bak=False) -> SkeletonHKX:
        anibnd_path = Path(anibnd_path)
        anibnd = Binder(anibnd_path, from_bak=prefer_bak)
        return cls(anibnd[1000000])


class AnimationHKX(HKX2015):
    """Loads HKX objects that are found in an "Animation" HKX file (inside `anibnd` binder, e.g. `a00_3000.hkx`)."""

    animationContainer: hkaAnimationContainer
    animation: hkaAnimation
    animationBinder: hkaAnimationBinding
    reference_frame_samples: list[Vector4]

    def create_attributes(self):
        self.set_variant_attribute("animationContainer", hkaAnimationContainer, 0)
        self.animation = self.animationContainer.animations[0]
        self.animation_binding = self.animationContainer.bindings[0]
        if isinstance(self.animation, hkaSplineCompressedAnimation) and self.animation.extractedMotion:
            reference_frame = self.animation.extractedMotion
            if isinstance(reference_frame, hkaDefaultAnimatedReferenceFrame):
                self.reference_frame_samples = reference_frame.referenceFrameSamples

    def get_spline_compressed_animation_data(self) -> SplineCompressedAnimationData:
        if isinstance(self.animation, hkaSplineCompressedAnimation):
            return SplineCompressedAnimationData(
                data=self.animation.data,
                transform_track_count=self.animation.numberOfTransformTracks,
                block_count=self.animation.numBlocks,
            )
        raise TypeError("Animation is not spline-compressed. Cannot get data.")

    def decompress_spline_animation_data(self) -> list[list[QuatTransform]]:
        """Convert spline-compressed animation data to a list of lists (per track) of `QuatTransform` instances."""
        if isinstance(self.animation, hkaSplineCompressedAnimation):
            return self.get_spline_compressed_animation_data().to_transform_track_lists(
                frame_count=self.animation.numFrames,
                max_frames_per_block=self.animation.maxFramesPerBlock
            )
        raise TypeError("Animation is not spline-compressed. Cannot decompress data.")

    def scale(self, factor: float):
        """Modifies all spline/static animation tracks, and also root motion (reference frame samples)."""
        if not isinstance(self.animation, hkaSplineCompressedAnimation):
            raise TypeError("Animation is not spline-compressed. Cannot scale data.")
        scaled_data = self.get_spline_compressed_animation_data().get_scaled_animation_data(factor)
        self.animation.data = scaled_data

        # Root motion (if present), sans W.
        if self.reference_frame_samples:
            for sample in self.reference_frame_samples:
                # Scale X, Y, and Z only, not W.
                sample.x *= factor
                sample.y *= factor
                sample.z *= factor

    def reverse(self):
        """Reverses all control points in all spline tracks, and also root motion (reference frame samples)."""
        if not isinstance(self.animation, hkaSplineCompressedAnimation):
            raise TypeError("Animation is not spline-compressed. Cannot reverse data.")
        reversed_data = self.get_spline_compressed_animation_data().get_reversed_animation_data()
        self.animation.data = reversed_data

        # Root motion (if present).
        if self.reference_frame_samples:
            extracted_motion = self.animation.extractedMotion
            if isinstance(extracted_motion, hkaDefaultAnimatedReferenceFrame):
                extracted_motion.referenceFrameSamples = list(reversed(self.reference_frame_samples))

    @property
    def root_motion(self):
        """Usual modding alias for reference frame samples."""
        return self.reference_frame_samples

    @classmethod
    def from_anibnd(
        cls, anibnd_path: Path | str, animation_id: tp.Union[int, str], prefer_bak=False
    ) -> AnimationHKX:
        if isinstance(animation_id, int):
            prefix = animation_id // 10000 * 10000
            base_id = animation_id % 10000
            animation_path = f"a{prefix:02d}_{base_id:04d}.hkx"
        else:
            animation_path = animation_id
            if not animation_path.endswith(".hkx"):
                animation_path += ".hkx"
        anibnd_path = Path(anibnd_path)
        anibnd = Binder(anibnd_path, from_bak=prefer_bak)
        return cls(anibnd[animation_path])


class RagdollHKX(HKX2015):
    """Loads HKX objects that are found in a "Ragdoll" HKX file (inside `chrbnd` binder, e.g. `c0000.hkx`)."""

    animationContainer: hkaAnimationContainer
    standard_skeleton: hkaSkeleton
    ragdoll_skeleton: hkaSkeleton
    physicsData: hkpPhysicsData
    ragdollInstance: hkaRagdollInstance
    ragdoll_to_standard_skeleton_mapper: hkaSkeletonMapper
    standard_to_ragdoll_skeleton_mapper: hkaSkeletonMapper

    def create_attributes(self):
        self.set_variant_attribute("animationContainer", hkaAnimationContainer, 0)
        self.standard_skeleton = self.animationContainer.skeletons[0]
        self.ragdoll_skeleton = self.animationContainer.skeletons[1]
        self.set_variant_attribute("physicsData", hkpPhysicsData, 1)
        self.set_variant_attribute("ragdollInstance", hkaRagdollInstance, 2)
        # TODO: Is this the correct order?
        self.set_variant_attribute("ragdoll_to_standard_skeleton_mapper", hkaSkeletonMapper, 3)
        self.set_variant_attribute("standard_to_ragdoll_skeleton_mapper", hkaSkeletonMapper, 4)

    def scale(self, factor: float):
        """Scale all translation information, including:
            - bones in both the standard and ragdoll skeletons
            - rigid body collidables
            - motion state transforms and swept transforms
            - skeleton mapper transforms in both directions

        This is currently working well, though since actual "ragdoll mode" only occurs when certain enemies die, any
        mismatched (and probably harmless) physics will be more of an aesthetic issue.
        """
        for pose in self.standard_skeleton.referencePose:
            pose.translation = tuple(x * factor for x in pose.translation)
        for pose in self.ragdoll_skeleton.referencePose:
            pose.translation = tuple(x * factor for x in pose.translation)

        for rigid_body in self.physicsData.systems[0].rigidBodies:
            scale_shape(rigid_body.collidable.shape, factor)

            # TODO: motion inertiaAndMassInv?

            motion_state = rigid_body.motion.motionState
            motion_state.transform.translation.x *= factor
            motion_state.transform.translation.y *= factor
            motion_state.transform.translation.z *= factor  # not W
            motion_state.objectRadius *= factor

            swept_transform = motion_state.sweptTransform
            swept_transform[0] *= factor
            swept_transform[1] *= factor
            # Indices 2 and 3 are rotations.
            swept_transform[4] *= factor

        # TODO: constraint instance transforms?

        for mapper in (self.ragdoll_to_standard_skeleton_mapper, self.standard_to_ragdoll_skeleton_mapper):
            for simple in mapper.mapping.simpleMappings:
                simple.aFromBTransform.translation *= factor
            for chain in mapper.mapping.chainMappings:
                chain.startAFromBTransform.translation *= factor

    @classmethod
    def from_chrbnd(cls, chrbnd_path: Path | str, prefer_bak=False) -> RagdollHKX:
        chrbnd_path = Path(chrbnd_path)
        if (bak_path := chrbnd_path.with_suffix(chrbnd_path.suffix + ".bak")).is_file() and prefer_bak:
            chrbnd_path = bak_path
        chrbnd = Binder(chrbnd_path)
        model_name = chrbnd_path.name.split(".")[0]  # e.g. "c0000"
        return cls(chrbnd[f"{model_name}.hkx"])


class ClothHKX(HKX2015):
    """Loads HKX objects that are found in a "Cloth" HKX file (inside `chrbnd` binder, e.g. `c2410_c.hkx`).

    This file is not used for every character - only those with cloth physics (e.g. capes).
    """

    physicsData: hkpPhysicsData

    def create_attributes(self):
        self.set_variant_attribute("physicasData", hkpPhysicsData, 0)

    def scale(self, factor: float):
        """Scale all translation information, including:
            - rigid body collidables
            - motion state transforms and swept transforms

        TODO: Since cloth is always in "ragdoll" mode, forces may need to be updated more cautiously here.
        """
        for rigid_body in self.physicsData.systems[0].rigidBodies:
            scale_shape(rigid_body.collidable.shape, factor)

            # TODO: motion inertiaAndMassInv?

            motion_state = rigid_body.motion.motionState
            motion_state.transform.translation.x *= factor
            motion_state.transform.translation.y *= factor
            motion_state.transform.translation.z *= factor  # not W
            motion_state.objectRadius *= factor

            swept_transform = motion_state.sweptTransform
            swept_transform[0] *= factor
            swept_transform[1] *= factor
            # Indices 2 and 3 are rotations.
            swept_transform[4] *= factor

        for constraint_instance in self.physicsData.systems[0].constraints:

            # TODO: Missing some types here.

            constraint_instance.data.link_0_pivot_b_velocity

            try:
                infos = constraint_instance.data.infos
            except AttributeError:
                pass
            else:
                for info in infos:
                    info.pivot_in_a = tuple(x * factor for x in info.pivot_in_a)
                    info.pivot_in_b = tuple(x * factor for x in info.pivot_in_b)
                constraint_instance.data.link_0_pivot_b_velocity = tuple(
                    x * factor for x in constraint_instance.data.link_0_pivot_b_velocity
                )
                # TODO: scale tau, damping, cfm?
                constraint_instance.data.max_error_distance *= factor
                constraint_instance.data.inertia_per_meter *= factor

            try:
                atoms = constraint_instance.data.atoms
            except AttributeError:
                continue

            if "transforms" in atoms.node.value:
                transforms = atoms.transforms

                old_transform_A = transforms.transform_a.to_flat_column_order()
                scaled_translate = tuple(x * factor for x in old_transform_A[12:15]) + (1.0,)
                transforms.node.value["transformA"].value = tuple(old_transform_A[:12]) + scaled_translate

                old_transform_B = transforms.transform_b.to_flat_column_order()
                scaled_translate = tuple(x * factor for x in old_transform_B[12:15]) + (1.0,)
                transforms.node.value["transformB"].value = tuple(old_transform_B[:12]) + scaled_translate

            if "pivots" in atoms.node.value:
                pivots = atoms.pivots

                scaled_translate = tuple(x * factor for x in pivots.translation_a)
                pivots.node.value["translationA"].value = scaled_translate

                scaled_translate = tuple(x * factor for x in pivots.translation_b)
                pivots.node.value["translationB"].value = scaled_translate

            if "spring" in atoms.node.value:
                spring = atoms.spring
                spring.length *= factor
                spring.max_length *= factor

    @classmethod
    def from_chrbnd(cls, chrbnd_path: Path | str, prefer_bak=False) -> ClothHKX:
        chrbnd_path = Path(chrbnd_path)
        if (bak_path := chrbnd_path.with_suffix(chrbnd_path.suffix + ".bak")).is_file() and prefer_bak:
            chrbnd_path = bak_path
        chrbnd = Binder(chrbnd_path)
        model_name = chrbnd_path.name.split(".")[0]  # e.g. "c0000"
        try:
            return cls(chrbnd[f"{model_name}_c.hkx"])
        except KeyError:
            raise FileNotFoundError(f"No '*_c.hkx' cloth physics file found in chrbnd {chrbnd_path}.")


class CollisionHKX(HKX2015):
    """Loads HKX objects used as terrain 'hit' geometry, found in `map/mAA_BB_CC_DD` folders."""

    physicsData: hkpPhysicsData

    def create_attributes(self):
        self.set_variant_attribute("physicsData", hkpPhysicsData, 0)

    # TODO: from BXF?


# TODO: Move to some utility module.
def scale_shape(shape: hkpShape, factor: float):
    if isinstance(shape, hkpConvexShape):
        shape.radius *= factor
        if isinstance(shape, hkpCapsuleShape):
            shape.vertexA *= factor
            shape.vertexB *= factor
    elif isinstance(shape, hkpMoppBvTreeShape):
        scale_shape(shape.child.childShape, factor)
    elif isinstance(shape, hkpExtendedMeshShape):
        shape.embeddedTrianglesSubpart.transform.translation *= factor
        shape.aabbHalfExtents *= factor
        shape.aabbCenter *= factor
        if isinstance(shape, hkpStorageExtendedMeshShape):
            for mesh in shape.meshstorage:
                for vertex in mesh.vertices:
                    vertex *= factor
