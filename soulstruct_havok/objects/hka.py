from __future__ import annotations

__all__ = [
    "AnimationContainer",
    "Skeleton",
    "SplineCompressedAnimation",
    "AnimationBinding",
    "RagdollInstance",
    "SkeletonMapper",
]

import typing as tp
from enum import IntEnum

from soulstruct.utilities.maths import Vector4
from .base import HKXObject, QsTransform
from .hkp import RigidBody, ConstraintInstance

if tp.TYPE_CHECKING:
    from ..nodes import HKXNode


class AnimationContainer(HKXObject):
    """hkaAnimationContainer"""

    skeletons: list[tp.Optional[Skeleton]]
    animations: list[tp.Union[InterleavedUncompressedAnimation, SplineCompressedAnimation]]
    bindings: list[tp.Optional[AnimationBinding]]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.skeletons = [n.get_py_object(Skeleton) for n in node["skeletons"]]
        self.animations = [Animation.auto_animation_type(n) for n in node["animations"]]
        self.bindings = [n.get_py_object(AnimationBinding) for n in node["bindings"]]
        self.attachments = node["attachments"]  # TODO
        self.skins = node["skins"]  # TODO


class Skeleton(HKXObject):
    """hkaSkeleton"""

    bones: list[tp.Optional[Bone]]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.name = node["name"]
        self.parent_indices = node["parentIndices"]
        self.bones = [n.get_py_object(Bone) for n in node["bones"]]
        self.reference_pose = [QsTransform(n) for n in node["referencePose"]]
        self.reference_floats = node["referenceFloats"]
        self.float_slots = node["floatSlots"]
        self.local_frames = node["localFrames"]
        self.partitions = node["partitions"]


class Bone(HKXObject):
    """hkaBone"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.name = node["name"]
        self.lock_translation = node["lockTranslation"]


class Animation(HKXObject):
    """hkaAnimation"""

    extracted_motion: tp.Optional[DefaultAnimatedReferenceFrame]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.type = node["type"]
        self.duration = node["duration"]
        self.number_of_transform_tracks = node["numberOfTransformTracks"]
        self.number_of_float_tracks = node["numberOfFloatTracks"]
        self.extracted_motion = node["extractedMotion"].get_py_object(DefaultAnimatedReferenceFrame)
        self.annotation_tracks = node["annotationTracks"]

    @staticmethod
    def auto_animation_type(node: HKXNode) -> tp.Union[None, SplineCompressedAnimation]:
        animation_type = node["type"]
        if animation_type == 3:
            return node.get_py_object(SplineCompressedAnimation)
        # TODO: Support Interleaved, at least.
        raise TypeError(f"Cannot load class for Animation type: {animation_type}")


class DefaultAnimatedReferenceFrame(HKXObject):
    """hkaDefaultAnimatedReferenceFrame

    Holds "root motion" data, which modifies the reference frame (actual map translate) of the model during the
    animation.
    """

    frame_type: int  # enum
    up: Vector4
    forward: Vector4
    duration: float
    reference_frame_samples: list[Vector4]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.frame_type = node["frameType"]
        self.up = Vector4(node["up"])
        self.forward = Vector4(node["forward"])
        self.duration = node["duration"]
        self.reference_frame_samples = [Vector4(n) for n in node["referenceFrameSamples"]]


class InterleavedUncompressedAnimation(Animation):
    """hkaInterleavedUncompressedAnimation

    Holds a raw sequence of `QsTransform`s (translate vector, rotate quaternion, scale vector) for a single bone. I
    don't believe this is actually used anywhere in FromSoft games - the file would be massive without using spline
    compression (see `SplineCompressedAnimation`).
    """


class SplineCompressedAnimation(Animation):
    """hkaSplineCompressedAnimation"""

    data: list[int]  # list of raw bytes of spline-compressed data

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.num_frames = node["numFrames"]
        self.num_blocks = node["numBlocks"]
        self.max_frames_per_block = node["maxFramesPerBlock"]
        self.mask_and_quantization_size = node["maskAndQuantizationSize"]
        self.block_duration = node["blockDuration"]
        self.block_inverse_duration = node["blockInverseDuration"]
        self.frame_duration = node["frameDuration"]
        self.block_offsets = node["blockOffsets"]
        self.float_block_offsets = node["floatBlockOffsets"]
        self.transform_offsets = node["transformOffsets"]
        self.float_offsets = node["floatOffsets"]
        self.data = node["data"]
        self.endian = node["endian"]


class AnimationBinding(HKXObject):
    """hkaAnimationBinding"""

    original_skeleton_name: str
    animation: tp.Optional[Animation]
    transform_track_to_bone_indices: list[int]
    float_track_to_float_slot_indices: list[int]
    partition_indices: list[int]
    blend_hint: BlendHint

    def __init__(self, node: HKXNode):
        super().__init__(node)

        self.original_skeleton_name = node["originalSkeletonName"]
        self.animation = Animation.auto_animation_type(node["animation"])
        self.transform_track_to_bone_indices = node["transformTrackToBoneIndices"]
        self.float_track_to_float_slot_indices = node["floatTrackToFloatSlotIndices"]
        self.partition_indices = node["partitionIndices"]
        self.blend_hint = BlendHint(node["blendHint"])


class BlendHint(IntEnum):
    Normal = 0
    AdditiveDeprecated = 1
    Additive = 2


class RagdollInstance(HKXObject):
    """hkaRagdollInstance"""

    def __init__(self, node: HKXNode):
        super().__init__(node)

        self.rigid_bodies = [
            n.get_py_object(RigidBody) for n in node["rigidBodies"]
        ]
        # TODO: these seem to be NEW constaint instances, but they look identical to the ones in `PhysicsSystem`...
        self.constraints = [
            n.get_py_object(ConstraintInstance) for n in node["constraints"]
        ]
        self.bone_to_rigid_body_map = node["boneToRigidBodyMap"]  # array of bone indices
        self.skeleton = node["skeleton"].get_py_object(Skeleton)


class SkeletonMapper(HKXObject):
    """hkaSkeletonMapper

    CHRBND HKX files have two of these: one mapping the normal Skeleton to the (lower-res) ragdoll Skeleton, and one
    doing the inverse mapping.
    """

    mapping: tp.Optional[SkeletonMapperData]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.mapping = node["mapping"].get_py_object(SkeletonMapperData)


class SkeletonMapperData(HKXObject):
    """hkaSkeletonMapperData"""

    simple_mappings: list[tp.Optional[SkeletonMapperDataSimpleMapping]]
    chain_mappings: list[tp.Optional[SkeletonMapperDataChainMapping]]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.skeleton_A = node["skeletonA"].get_py_object(Skeleton)
        self.skeleton_B = node["skeletonB"].get_py_object(Skeleton)
        self.partition_map = node["partitionMap"]
        self.simple_mapping_partition_ranges = node["simpleMappingPartitionRanges"].value  # TODO
        self.chain_mapping_partition_ranges = node["chainMappingPartitionRanges"].value  # TODO
        self.simple_mappings = [n.get_py_object(SkeletonMapperDataSimpleMapping) for n in node["simpleMappings"]]
        self.chain_mappings = [n.get_py_object(SkeletonMapperDataChainMapping) for n in node["chainMappings"]]
        self.unmapped_bones = node["unmappedBones"]
        self.extracted_motion_mapping = QsTransform(node["extractedMotionMapping"])
        self.keep_unmapped_local = node["keepUnmappedLocal"]
        self.mapping_type = node["mappingType"]


class SkeletonMapperDataSimpleMapping(HKXObject):
    """hkaSkeletonMapperDataSimpleMapping"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.bone_A_index = node["boneA"]
        self.bone_B_index = node["boneB"]
        self.A_from_B_transform = QsTransform(node["aFromBTransform"])


class SkeletonMapperDataChainMapping(HKXObject):
    """hkaSkeletonMapperDataChainMapping"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.start_bone_A_index = node["startBoneA"]
        self.end_bone_A_index = node["endBoneA"]
        self.start_bone_B_index = node["startBoneB"]
        self.end_bone_B_index = node["endBoneB"]
        self.start_A_from_B_transform = QsTransform(node["startAFromBTransform"])
