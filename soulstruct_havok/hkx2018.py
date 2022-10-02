"""Subclasses and tools for making work with Havok 2015 easier."""
from __future__ import annotations

__all__ = [
    "HKX2018",
    "SkeletonHKX",
    "AnimationHKX",
    "RagdollHKX",
    "ClothHKX",
    "CollisionHKX",
    "scale_chrbnd",
    "scale_anibnd",
]

import logging
import os
import subprocess as sp
import typing as tp
from pathlib import Path

from soulstruct.base.models.flver import FLVER
from soulstruct.containers import Binder
from soulstruct.containers.dcx import DCXType
from soulstruct.utilities.maths import QuatTransform, Vector3, Matrix3, Matrix4
from soulstruct.utilities.files import read_json

from soulstruct_havok.core import HKX
from soulstruct_havok.types.hk2018 import *
from soulstruct_havok.spline_compression import SplineCompressedAnimationData
from soulstruct_havok.utilities.wavefront import read_obj

_LOGGER = logging.getLogger(__name__)


class HKX2018(HKX):

    root: hkRootLevelContainer

    def __init__(self, file_source, dcx_type: None | DCXType = DCXType.Null, compendium: None | HKX = None):
        super().__init__(file_source, dcx_type=dcx_type, compendium=compendium, hk_format=self.TAGFILE)
        self.create_attributes()

    def create_attributes(self):
        pass


class SkeletonHKX(HKX2018):
    """Loads HKX objects that are found in a "Skeleton" HKX file (inside `anibnd` binder, usually `Skeleton.HKX`)."""

    animationContainer: hkaAnimationContainer
    skeleton: hkaSkeleton

    def create_attributes(self):
        self.set_variant_attribute("animationContainer", hkaAnimationContainer, 0)
        self.skeleton = self.animationContainer.skeletons[0]

    def scale(self, factor: float):
        """Scale all bone translations in place by `factor`."""
        for pose in self.skeleton.referencePose:
            pose.translation = tuple(x * factor for x in pose.translation)

    def find_bone_name(self, bone_name: str):
        matches = [bone for bone in self.skeleton.bones if bone.name == bone_name]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise ValueError(f"Multiple bones named '{bone_name}' in skeleton. This is unusual.")
        else:
            raise ValueError(f"Bone name not found: '{bone_name}'")

    def find_bone_name_index(self, bone_name: str):
        bone = self.find_bone_name(bone_name)
        return self.skeleton.bones.index(bone)

    def get_bone_parent_index(self, bone: tp.Union[hkaBone, str]) -> int:
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")
        bone_index = self.skeleton.bones.index(bone)
        return self.skeleton.parentIndices[bone_index]

    def get_bone_parent(self, bone: tp.Union[hkaBone, str]) -> tp.Optional[hkaBone]:
        parent_index = self.get_bone_parent_index(bone)
        if parent_index == -1:
            return None
        return self.skeleton.bones[parent_index]

    def get_immediate_bone_children(self, bone: tp.Union[hkaBone, str]) -> list[hkaBone]:
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")

        bone_index = self.skeleton.bones.index(bone)
        return [b for b in self.skeleton.bones if self.get_bone_parent_index(b) == bone_index]

    def get_all_bone_children(self, bone: tp.Union[hkaBone, str]) -> list[hkaBone]:
        """Recursively get all bones that are children of `bone`."""
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")

        children = []
        bone_index = self.skeleton.bones.index(bone)
        for bone in self.skeleton.bones:
            parent_index = self.get_bone_parent_index(bone)
            if parent_index == bone_index:
                children.append(bone)  # immediate child
                children += self.get_all_bone_children(bone)  # recur on child
        return children

    def get_bone_local_transform(self, bone: tp.Union[hkaBone, str]) -> QuatTransform:
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")
        bone_index = self.skeleton.bones.index(bone)
        qs_transform = self.skeleton.referencePose[bone_index]
        return QuatTransform(
            qs_transform.translation,
            qs_transform.rotation,
            qs_transform.scale,
        )

    def get_all_parents(self, bone: tp.Union[hkaBone, str]) -> list[hkaBone]:
        """Get all parents of `bone` in order from the highest down to itself."""
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")
        parents = [bone]
        bone_index = self.skeleton.bones.index(bone)
        parent_index = self.skeleton.parentIndices[bone_index]
        while parent_index != -1:
            bone = self.skeleton.bones[parent_index]
            parents.append(bone)
            bone_index = self.skeleton.bones.index(bone)
            parent_index = self.skeleton.parentIndices[bone_index]
        return list(reversed(parents))

    def get_bone_global_translate(self, bone: tp.Union[hkaBone, str]) -> Vector3:
        """Accumulates parents' transforms into a 4x4 matrix."""
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")
        absolute_translate = Vector3.zero()
        rotate = Matrix3.identity()
        for hierarchy_bone in self.get_all_parents(bone):
            local_transform = self.get_bone_local_transform(hierarchy_bone)
            absolute_translate += rotate @ Vector3(local_transform.translate)
            rotate @= local_transform.rotation.to_rotation_matrix()
        return absolute_translate

    def get_bone_transforms_and_parents(self):
        """Construct a dictionary that maps bone names to (`hkQsTransform`, `hkaBone`) pairs of transforms/parents."""
        bone_transforms = {}
        for i in range(len(self.skeleton.bones)):
            bone_name = self.skeleton.bones[i].name
            parent_index = self.skeleton.parentIndices[i]
            parent_bone = None if parent_index == -1 else self.skeleton.bones[parent_index]
            bone_transforms[bone_name] = (self.skeleton.referencePose[i], parent_bone)
        return bone_transforms

    def delete_bone(self, bone: tp.Union[hkaBone, str], indent="") -> int:
        """Delete a bone and all of its children. Returns the number of bones deleted."""
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone.name}' is not in this skeleton.")

        bones_deleted = 0
        children = self.get_immediate_bone_children(bone)
        for child_bone in children:
            bones_deleted += self.delete_bone(child_bone, indent + "    ")

        # Delete bone.
        bone_index = self.skeleton.bones.index(bone)
        self.skeleton.bones.pop(bone_index)
        self.skeleton.referencePose.pop(bone_index)
        self.skeleton.parentIndices.pop(bone_index)
        # Adjust parent indices. No danger of finding `bone_index` in here, as that child would have been deleted above.
        self.skeleton.parentIndices = [
            i - 1 if i > bone_index else i
            for i in self.skeleton.parentIndices
        ]

        return bones_deleted

    def print_bone_tree(self, bone: tp.Union[hkaBone, str] = None, indent=""):
        """Print indented tree of bone names."""
        if bone is None:
            bone = self.skeleton.bones[0]  # 'Master' usually
        elif isinstance(bone, str):
            bone = self.find_bone_name(bone)
        elif bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")

        print(indent + bone.name)
        for child in self.get_immediate_bone_children(bone):
            self.print_bone_tree(child, indent=indent + "    ")


class AnimationHKX(HKX2018):
    """Loads HKX objects that are found in an "Animation" HKX file (inside `anibnd` binder, e.g. `a00_3000.hkx`)."""

    animationContainer: hkaAnimationContainer
    animation: hkaAnimation
    animationBinder: hkaAnimationBinding
    reference_frame_samples: None | list[Vector4]

    def create_attributes(self):
        self.set_variant_attribute("animationContainer", hkaAnimationContainer, 0)
        self.animation = self.animationContainer.animations[0]
        self.animation_binding = self.animationContainer.bindings[0]
        if isinstance(self.animation, hkaSplineCompressedAnimation) and self.animation.extractedMotion:
            reference_frame = self.animation.extractedMotion
            if isinstance(reference_frame, hkaDefaultAnimatedReferenceFrame):
                self.reference_frame_samples = reference_frame.referenceFrameSamples
        else:
            self.reference_frame_samples = None

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
        if self.reference_frame_samples is not None:
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


class RagdollHKX(HKX2018):
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

            # TODO: Experimental. Possibly index 3 should not be scaled. (Maybe always zero for ragdolls anyway.)
            rigid_body.motion.inertiaAndMassInv *= factor

            scale_motion_state(rigid_body.motion.motionState, factor)

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


class ClothHKX(HKX2018):
    """Loads HKX objects that are found in a "Cloth" HKX file (inside `chrbnd` binder, e.g. `c2410_c.hkx`).

    This file is not used for every character - only those with cloth physics (e.g. capes).
    """

    physicsData: hkpPhysicsData

    def create_attributes(self):
        self.set_variant_attribute("physicsData", hkpPhysicsData, 0)

    def scale(self, factor: float):
        """Scale all translation information, including:
            - rigid body collidables
            - motion state transforms and swept transforms

        TODO: Since cloth is always in "ragdoll" mode, forces may need to be updated more cautiously here.
        """
        for rigid_body in self.physicsData.systems[0].rigidBodies:
            scale_shape(rigid_body.collidable.shape, factor)

            # TODO: Experimental. Possibly index 3 should not be scaled. (Also, maybe scales as cube?)
            rigid_body.motion.inertiaAndMassInv *= factor

            scale_motion_state(rigid_body.motion.motionState, factor)

        for constraint_instance in self.physicsData.systems[0].constraints:

            scale_constraint_data(constraint_instance.data, factor)

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


class CollisionHKX(HKX2018):
    """Loads HKX objects used as terrain 'hit' geometry, found in `map/mAA_BB_CC_DD` folders."""

    MOPPER_PATH = Path(r"C:\Users\Scott\Downloads\mopper-master\mopper-master\Release\mopper.exe")

    physicsData: hkpPhysicsData

    def create_attributes(self):
        self.set_variant_attribute("physicsData", hkpPhysicsData, 0)

    def get_child_shape(self) -> CustomParamStorageExtendedMeshShape:
        """Validates type of collision shape and returns `childShape`."""
        shape = self.physicsData.systems[0].rigidBodies[0].collidable.shape
        if not isinstance(shape, hkpMoppBvTreeShape):
            raise TypeError("Expected collision shape to be `hkpMoppBvTreeShape`.")
        child_shape = shape.child.childShape
        if not isinstance(child_shape, CustomParamStorageExtendedMeshShape):
            raise TypeError("Expected collision child shape to be `CustomParamStorageExtendedMeshShape`.")
        return child_shape

    def get_extended_mesh_meshstorage(self) -> list[hkpStorageExtendedMeshShapeMeshSubpartStorage]:
        """Validates type of collision shape and returns `meshstorage`."""
        return self.get_child_shape().meshstorage

    def get_mopp_code(self) -> hkpMoppCode:
        shape = self.physicsData.systems[0].rigidBodies[0].collidable.shape
        if not isinstance(shape, hkpMoppBvTreeShape):
            raise TypeError("Expected collision shape to be `hkpMoppBvTreeShape`.")
        return shape.code

    def regenerate_mopp_data(self):
        meshstorage = self.get_extended_mesh_meshstorage()
        mopp_code = self.get_mopp_code()

        mopper_input = [f"{len(meshstorage)}"]
        for mesh in meshstorage:
            mopper_input.append("")
            mopper_input.append(f"{len(mesh.vertices)}")
            for v in mesh.vertices:
                mopper_input.append(f"{v.x} {v.y} {v.z}")
            mopper_input.append("")
            mopper_input.append(f"{len(mesh.indices16) // 4}")
            faces = mesh.indices16.copy()
            while faces:
                mopper_input.append(f"{faces[0]} {faces[1]} {faces[2]}")
                faces = faces[4:]  # drop 0 after triple

        mopp = self.mopper(mopper_input, mode="-esm")
        new_mopp_code = mopp["hkpMoppCode"]["data"]
        new_offset = mopp["hkpMoppCode"]["offset"]
        mopp_code.data = new_mopp_code
        mopp_code.info.offset = Vector4(new_offset)

    def get_name(self) -> str:
        return self.physicsData.systems[0].rigidBodies[0].name

    @classmethod
    def from_binder(cls, binder_path: Path | str, entry_name: str, from_bak=False):
        """Pull HKX from binder. (Probably not that useful if you want to write that same binder back.)"""
        binder = Binder(binder_path, from_bak=from_bak)
        entry = binder.find_entry_matching_name(entry_name)
        return cls(entry)

    @classmethod
    def from_obj(
        cls,
        obj_path: Path | str,
        hkx_name: str,
        material_name_data: tuple[int] = (),
        template_hkx: CollisionHKX = None,
        invert_x=True,
        dcx_type: DCXType = DCXType.Null,
    ) -> CollisionHKX:
        """Convert an OBJ file containing vertices and faces for one or more meshes (subparts) to a HKX collision file.

        Uses default values for a bunch of fields, most of which don't matter. Also uses new and improved Mopper.

        If `template_hkx` is given, it will be used as the base for the new HKX, rather than the stock `template.hkx`.
        Note that if given, `template_hkx` will be modified in place AND returned.

        Inverts X axis by default, which should also be done in `to_obj()` if used again here (for accurate depiction
        in Blender, etc.).
        """
        obj_meshes = read_obj(obj_path, invert_x=invert_x)
        if not obj_meshes:
            raise ValueError("At least one mesh required in OBJ to convert to HKX.")

        if template_hkx is None:
            hkx = cls(Path(__file__).parent / "resources/CollisionTemplate2015.hkx")
        else:
            hkx = template_hkx
        child_shape = hkx.get_child_shape()
        if len(child_shape.meshstorage) != len(obj_meshes):
            raise ValueError(
                f"Number of OBJ meshes ({len(obj_meshes)}) does not match number of existing meshes in template "
                f"HKX ({len(child_shape.meshstorage)}). Omit `template_hkx` to allow any number of OBJ meshes."
            )

        if not material_name_data:
            material_name_data = [material.materialNameData for material in child_shape.materialArray]
        elif len(material_name_data) != len(obj_meshes):
            raise ValueError(
                f"Length of `material_name_data` ({len(material_name_data)}) does not match number of meshes in "
                f"OBJ ({len(obj_meshes)})."
            )
        else:
            material_name_data = [0] * len(obj_meshes)

        rigid_body = hkx.physicsData.systems[0].rigidBodies[0]
        rigid_body.name = hkx_name

        # TODO: rigid_body.motion.motionState.objectRadius?

        child_shape.cachedNumChildShapes = sum(len(faces) for _, faces in obj_meshes)
        child_shape.trianglesSubparts = []
        child_shape.meshstorage = []
        child_shape.materialArray = []
        for i, (vertices, faces) in enumerate(obj_meshes):

            subpart = cls.get_subpart(len(vertices), len(faces))
            child_shape.trianglesSubparts.append(subpart)

            indices = []
            for face in faces:
                indices.extend(face)
            storage = hkpStorageExtendedMeshShapeMeshSubpartStorage(
                memSizeAndFlags=0,
                refCount=0,
                vertices=vertices,
                indices8=[],
                indices16=indices,
                indices32=[],
                materialIndices=[],
                materials=[],
                namedMaterials=[],
                materialIndices16=[],
            )
            child_shape.meshstorage.append(storage)

            material = CustomMeshParameter(
                memSizeAndFlags=0,
                refCount=0,
                version=37120,
                vertexDataBuffer=[255] * len(vertices),
                vertexDataStride=1,
                primitiveDataBuffer=[],
                materialNameData=material_name_data[i],
            )
            child_shape.materialArray.append(material)

        # Havok docs say that embedded triangle subpart is only efficient for single-subpart shapes, but From disagrees.
        # Note that it is a fresh instance, not a copy of the first subpart.
        child_shape.embeddedTrianglesSubpart = cls.get_subpart(len(obj_meshes[0][0]), len(obj_meshes[0][1]))

        x_min = min([v.x for mesh, _ in obj_meshes for v in mesh])
        x_max = max([v.x for mesh, _ in obj_meshes for v in mesh])
        y_min = min([v.y for mesh, _ in obj_meshes for v in mesh])
        y_max = max([v.y for mesh, _ in obj_meshes for v in mesh])
        z_min = min([v.z for mesh, _ in obj_meshes for v in mesh])
        z_max = max([v.z for mesh, _ in obj_meshes for v in mesh])
        child_shape.aabbHalfExtents = Vector4((x_max - x_min) / 2, (y_max - y_min) / 2, (z_max - z_min) / 2, 0.0)
        child_shape.aabbCenter = Vector4((x_max + x_min) / 2, (y_max + y_min) / 2, (z_max + z_min) / 2, 0.0)

        hkx.regenerate_mopp_data()

        hkx.dcx_type = dcx_type

        return hkx

    @staticmethod
    def get_subpart(vertices_count: int, faces_count: int):
        return hkpExtendedMeshShapeTrianglesSubpart(
            typeAndFlags=2,
            shapeInfo=0,
            materialIndexBase=None,
            materialBase=None,
            vertexBase=None,
            indexBase=None,
            materialStriding=0,
            materialIndexStriding=0,
            userData=0,
            numTriangleShapes=faces_count,
            numVertices=vertices_count,
            vertexStriding=16,
            triangleOffset=2010252431,  # TODO: should be given in `mopp.json`
            indexStriding=8,
            stridingType=2,  # 16-bit
            flipAlternateTriangles=0,
            extrusion=Vector4(0.0, 0.0, 0.0, 0.0),
            transform=hkQsTransform(
                translation=Vector4(0.0, 0.0, 0.0, 0.0),
                rotation=(0.0, 0.0, 0.0, 1.0),
                scale=Vector4(1.0, 1.0, 1.0, 1.0),
            ),
        )

    def to_obj(self, invert_x=True) -> str:
        """Convert raw vertices and triangle faces (zero-separated triplets) from HKX meshes to OBJ file.

        Inverts (negates) X axis by default, which should be reversed on import.
        """
        name = self.get_name()
        obj_lines = [
            f"# OBJ file generated by Soulstruct from HKX with path: {self.path}",
            f"# Internal name: {name}"
        ]
        global_v_i = 0

        for i, mesh in enumerate(self.get_extended_mesh_meshstorage()):
            if len(mesh.indices16) % 4:
                raise ValueError("`indices16` length must be a multiple of 4.")
            obj_lines += ["", f"o {name} Subpart {i}"]
            for vert in mesh.vertices:
                obj_lines.append(f"v {-vert.x if invert_x else vert.x} {vert.y} {vert.z}")
            obj_lines.append("s off")
            for f in range(len(mesh.indices16) // 4):
                face = mesh.indices16[4 * f:4 * f + 3]
                obj_lines.append(
                    f"f {face[0] + global_v_i + 1} {face[1] + global_v_i + 1} {face[2] + global_v_i + 1}"
                )  # note 1-indexing of vertices in OBJ faces
            global_v_i += len(mesh.vertices)

        return "\n".join(obj_lines) + "\n"

    def write_obj(self, obj_path: Path | str):
        Path(obj_path).write_text(self.to_obj())

    @staticmethod
    def mopper(input_lines: list[str], mode: str) -> dict:
        if mode not in {"-ccm", "-msm", "-esm"}:
            raise ValueError("`mode` must be -ccm, -msm, or -esm.")
        if Path("mopp.json").exists():
            os.remove("mopp.json")
        input_text = "\n".join(input_lines) + "\n"
        # print(input_text)
        Path("mopper_input.txt").write_text(input_text)
        _LOGGER.info("# Running mopper...")
        sp.call([str(CollisionHKX.MOPPER_PATH), mode, "mopper_input.txt"])
        if not Path("mopp.json").exists():
            raise FileNotFoundError("Mopper did not produce `mopp.json`.")
        return read_json("mopp.json")


# region Utility Functions
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


def scale_transform_translation(transform: tuple[float], factor: float) -> tuple[float]:
    """Scale translation component of 16-float tuple that represents `hkTransform` or `hkTransformf` and return scaled
    tuple."""
    transform = Matrix4.from_flat_column_order(transform)
    transform[0, 3] *= factor  # x
    transform[1, 3] *= factor  # y
    transform[2, 3] *= factor  # z
    return tuple(transform.to_flat_column_order())


def scale_motion_state(motion_state: hkMotionState, factor: float):
    motion_state.transform = scale_transform_translation(motion_state.transform, factor)
    motion_state.objectRadius *= factor

    # Indices 2 and 3 are rotations.
    motion_state.sweptTransform = tuple(
        t * factor if i in {0, 1, 4} else t
        for i, t in enumerate(motion_state.sweptTransform)
    )


def scale_constraint_data(constraint_data: hkpConstraintData, factor: float):
    if isinstance(constraint_data, hkpRagdollConstraintData):
        # TODO: There are a bunch of forces/constraints in here that I'm not sure how to scale.
        atoms = constraint_data.atoms
        atoms.transforms.transformA = scale_transform_translation(atoms.transforms.transformA, factor)
        atoms.transforms.transformB = scale_transform_translation(atoms.transforms.transformB, factor)

        # TODO: I must've encountered some constraint class with `data.pivots` member. Scale if found again.
        # TODO: Ditto for `atoms.spring` (length and maxLength).

    elif isinstance(constraint_data, hkpBallSocketChainData):
        constraint_data.link0PivotBVelocity *= factor
        constraint_data.maxErrorDistance *= factor
        constraint_data.inertiaPerMeter *= factor
        # TODO: tau, damping, cfm?
        for info in constraint_data.infos:
            # TODO: Possibly don't want to scale `w`.
            info.pivotInA *= factor
            info.pivotInB *= factor
# endregion


# Helpers

def scale_chrbnd(chrbnd_path: Path | str, scale_factor: float, from_bak=True):
    """Scale FLVER, ragdoll, and (if present) cloth in CHRBND."""
    chrbnd = Binder(chrbnd_path, from_bak=from_bak)

    flver_entry = chrbnd.find_entry_matching_name(r".*\.flver")  # should be ID 200
    model = FLVER(flver_entry)
    model.scale(scale_factor)
    flver_entry.set_uncompressed_data(model.pack_dcx())
    _LOGGER.info(f"{flver_entry.name} model scaled by {scale_factor}.")

    model_name = flver_entry.name.split(".")[0]
    ragdoll_entry = chrbnd[f"{model_name}.hkx"]  # should be ID 300
    ragdoll_hkx = RagdollHKX(ragdoll_entry)
    ragdoll_hkx.scale(scale_factor)
    chrbnd[f"{model_name}.hkx"].set_uncompressed_data(ragdoll_hkx.pack_dcx())
    _LOGGER.info(f"{ragdoll_entry.name} ragdoll physics scaled by {scale_factor}.")

    try:
        cloth_entry = chrbnd.find_entry_matching_name(rf"{model_name}_c\.hkx")  # should be ID 700
    except KeyError:
        # No cloth data.
        _LOGGER.info("No cloth HKX found.")
    else:
        cloth_hkx = ClothHKX(cloth_entry)
        cloth_hkx.scale(scale_factor)
        cloth_entry.set_uncompressed_data(cloth_hkx.pack_dcx())
        _LOGGER.info(f"{cloth_entry.name} cloth physics scaled by {scale_factor}.")

    chrbnd.write()
    _LOGGER.info(f"Scaling complete. {chrbnd.path} written.")


def scale_anibnd(anibnd_path: Path | str, scale_factor: float, from_bak=True):
    """Scale skeleton and all animations."""
    anibnd = Binder(anibnd_path, from_bak=from_bak)

    skeleton_entry = anibnd.find_entry_matching_name(r"[Ss]keleton\.(HKX|hkx)")  # should be ID 1000000
    skeleton_hkx = SkeletonHKX(skeleton_entry)
    skeleton_hkx.scale(scale_factor)
    skeleton_entry.set_uncompressed_data(skeleton_hkx.pack_dcx())
    _LOGGER.info(f"{skeleton_entry.name} skeleton scaled by {scale_factor}.")

    animation_entries = anibnd.find_entries_matching_name(r"a.*\.hkx")
    for entry in animation_entries:
        _LOGGER.info(f"  Scaling animation {entry.id} by {scale_factor}...")
        animation_hkx = AnimationHKX(entry)  # "aXX_XXXX.hkx"
        animation_hkx.scale(scale_factor)
        entry.set_uncompressed_data(animation_hkx.pack_dcx())

    anibnd.write()
    _LOGGER.info(f"Scaling complete. {anibnd.path} written.")

# endregion
