from __future__ import annotations

__all__ = ["HKX", "AnimationHKX", "SkeletonHKX", "RagdollHKX", "ClothHKX"]

import io
import logging
import typing as tp
from pathlib import Path

from soulstruct.base.game_file import GameFile, InvalidGameFileTypeError
from soulstruct.containers import Binder
from soulstruct.containers.bnd import BaseBND
from soulstruct.containers.dcx import DCXType
from soulstruct.containers.bnd.entry import BNDEntry
from soulstruct.utilities.maths import QuatTransform, Vector4
from soulstruct.utilities.binary import BinaryReader

from .packfile.packer import PackFilePacker
from .packfile.structs import PackFileHeaderExtension
from .packfile.unpacker import PackFileUnpacker
from .spline_compression import SplineCompressedAnimationData
from .tagfile.packer import TagFilePacker
from .tagfile.unpacker import TagFileUnpacker
from .types import hk

from .objects.hka import *
from .objects.hkp import PhysicsData

_LOGGER = logging.getLogger(__name__)


class HKX(GameFile):
    """Havok data used in FromSoft games to hold model (FLVER) skeletons, animations, ragdoll physica, collisions, etc.

    HKX files are a form of compressed XML used by the Havok physics engine. This class can read from both pre-2015
    `packfile`-type HKX files (used up to and including DS3) and post-2015 `tagfile`-type HKX files (used in DSR and
    Sekiro), and freely write to either format.

    Use `write_packfile()` and `write_tagfile()` to specify the format you want to output. If you use `write()`, it will
    default to writing the format that was loaded. Same for `pack()` and its two variants.
    """
    root: None | hk
    hk_type_infos = list[tp.Type[hk]]
    hk_format: str  # "packfile" or "tagfile"
    hk_version: str
    unpacker: None | TagFileUnpacker | PackFileUnpacker
    is_compendium: bool
    compendium_ids: list[str]

    packfile_header_version: None | str
    packfile_pointer_size: None | int
    packfile_is_little_endian: None | bool
    packfile_padding_option: None | int
    packfile_contents_version_string: None | bytes
    packfile_flags: None | int
    packfile_header_extension: None | PackFileHeaderExtension

    def __init__(
        self,
        file_source: GameFile.Typing = None,
        dcx_type: None | DCXType = DCXType.Null,
        compendium: tp.Optional[HKX] = None,
        hk_format="",
    ):
        if hk_format not in {"", "tagfile", "packfile"}:
            raise ValueError(f"`hk_format` must be 'tagfile' or 'packfile' if given, not: {hk_format}")
        self.root = None  # type: tp.Optional[hk]
        self.all_nodes = []
        self.hk_type_infos = []  # type: list[tp.Type[hk]]
        self.hk_format = hk_format
        self.hk_version = ""
        self.is_compendium = False
        self.unpacker = None
        self.compendium_ids = []

        self.packfile_header_version = None
        self.packfile_pointer_size = None
        self.packfile_is_little_endian = None
        self.packfile_padding_option = None
        self.packfile_contents_version_string = None
        self.packfile_flags = None
        self.packfile_header_extension = None

        super().__init__(file_source, dcx_type=dcx_type, compendium=compendium, hk_format=hk_format)

    def _handle_other_source_types(self, file_source, compendium: tp.Optional[HKX] = None, hk_format=""):

        if isinstance(file_source, str):
            file_source = Path(file_source)
        if isinstance(file_source, BNDEntry):
            file_source = file_source.data
        if isinstance(file_source, Path):
            file_source = file_source.open("rb")
        if isinstance(file_source, (bytes, io.BufferedIOBase, BinaryReader)):
            reader = BinaryReader(file_source)
            detected_hk_format = self._detect_hk_format(reader)
            if detected_hk_format is None:
                raise InvalidGameFileTypeError("`file_source` was not an HKX packfile or tagfile.")
            elif self.hk_format and detected_hk_format != self.hk_format:
                raise ValueError(
                    f"Detected HKX format {detected_hk_format} does not match passed format: {self.hk_format}"
                )
            self.hk_format = detected_hk_format
            self.unpack(reader, compendium=compendium)
            return

        raise InvalidGameFileTypeError("`file_source` was not an `XML` file, `HKX` file/stream, or `HKXNode`.")

    @staticmethod
    def _detect_hk_format(reader: BinaryReader) -> None | str:
        """Peek into buffer to find out if it is a "packfile", "tagfile", or unknown (`None`)."""
        first_eight_bytes = reader.unpack_bytes(length=8, offset=reader.position)
        if first_eight_bytes == b"\x57\xE0\xE0\x57\x10\xC0\xC0\x10":
            return "packfile"
        elif first_eight_bytes[4:8] in {b"TAG0", b"TCRF"}:
            return "tagfile"
        return None

    def unpack(self, reader: BinaryReader, hk_format="", compendium: tp.Optional[HKX] = None):
        if not hk_format:
            hk_format = self.hk_format
        if hk_format == "packfile":
            if compendium is not None:
                raise ValueError("`compendium` was passed with HKX packfile source (used only by newer tagfiles).")
            self.unpack_packfile(reader)
        elif hk_format == "tagfile":
            self.unpack_tagfile(reader, compendium=compendium)
        else:
            raise ValueError(
                f"`hk_format` must be 'packfile' or 'tagfile' for `HKX.unpack()`, not {repr(hk_format)}."
            )

    def unpack_packfile(self, reader: BinaryReader):
        """Buffer is known to be `packfile`."""
        self.unpacker = PackFileUnpacker()
        self.unpacker.unpack(reader)
        self.root = self.unpacker.root
        self.hk_type_infos = self.unpacker.hk_type_infos
        self.hk_version = self.unpacker.hk_version
        self.is_compendium = False
        self.compendium_ids = []

        self.packfile_header_version = self.unpacker.header.version
        self.packfile_pointer_size = self.unpacker.header.pointer_size
        self.packfile_is_little_endian = self.unpacker.header.is_little_endian
        self.packfile_padding_option = self.unpacker.header.padding_option
        self.packfile_contents_version_string = self.unpacker.header.contents_version_string
        self.packfile_flags = self.unpacker.header.flags
        self.packfile_header_extension = self.unpacker.header_extension

    def unpack_tagfile(self, reader: BinaryReader, compendium: tp.Optional[HKX] = None):
        """Buffer is known to be `tagfile`."""
        self.unpacker = TagFileUnpacker()
        self.unpacker.unpack(reader, compendium=compendium)
        self.root = self.unpacker.root
        self.hk_type_infos = self.unpacker.hk_type_infos
        self.hk_version = self.unpacker.hk_version
        self.is_compendium = self.unpacker.is_compendium
        self.compendium_ids = self.unpacker.compendium_ids

    def pack(self, hk_format="") -> bytes:
        if hk_format == "":
            hk_format = self.hk_format
        if hk_format.lower() == "packfile":
            self._validate_packfile_header_info()
            return PackFilePacker(self).pack(
                header_version=self.packfile_header_version,
                pointer_size=self.packfile_pointer_size,
                is_little_endian=self.packfile_is_little_endian,
                padding_option=self.packfile_padding_option,
                contents_version_string=self.packfile_contents_version_string,
                flags=self.packfile_flags,
                header_extension=self.packfile_header_extension,  # may be None
            )
        elif hk_format.lower() == "tagfile":
            return TagFilePacker(self).pack()
        raise ValueError(f"Invalid `hk_format` for `HKX.pack()`: {hk_format}. Should be 'packfile' or 'tagfile'.")

    def pack_packfile(self) -> bytes:
        return self.pack("packfile")

    def pack_tagfile(self) -> bytes:
        return self.pack("tagfile")

    def write(self, file_path: tp.Union[None, str, Path] = None, make_dirs=True, check_hash=False, hk_format=""):
        super().write(file_path, make_dirs=make_dirs, check_hash=check_hash, hk_format=hk_format)

    def write_packfile(self, file_path: tp.Union[None, str, Path] = None, make_dirs=True, check_hash=False):
        self.write(file_path, make_dirs=make_dirs, check_hash=check_hash, hk_format="packfile")

    def write_tagfile(self, file_path: tp.Union[None, str, Path] = None, make_dirs=True, check_hash=False):
        self.write(file_path, make_dirs=make_dirs, check_hash=check_hash, hk_format="tagfile")

    def get_root_tree_string(self, max_primitive_sequence_size=-1) -> str:
        return self.root.get_tree_string(max_primitive_sequence_size=max_primitive_sequence_size)

    def _validate_packfile_header_info(self):
        if any(
            attr is None
            for attr in (
                self.packfile_header_version,
                self.packfile_pointer_size,
                self.packfile_is_little_endian,
                self.packfile_padding_option,
                self.packfile_contents_version_string,
                self.packfile_flags,
            )
        ):
            raise AttributeError("Not all packfile header information has been set.")

    # ~~~ CONVERSION METHODS ~~~ #

    # Call these to PERMANENTLY convert the HKX instance to the given Havok version. This works by iterating over all
    # the nodes and changing their type to the corresponding type in the requested version's type database. Only the
    # listed versions are available.

    # Packfile versions (up to 2014) use version string format "hk_YYYY.A.B-rC", where A and B are major/minor versions
    # and C is a "revision" (or maybe "release") version.

    # Tagfile versions (2015 and after) use version string format "YYYYAABB", where AA is a major version and BB is a
    # minor version (e.g. "20160100").

    # The default `hk_format` of the `HKX` will also be changed to "packfile" or "tagfile" whenever you use one of
    # these conversion methods.

    # Versions used by various FromSoftware games:
    #   Dark Souls Prepare to Die Edition:      hk_2010-2.0-r1
    #   Bloodborne:                             hk_2014-1.0-r1
    #   Dark Souls 3:                           hk_2014-1.0-r1
    #   Dark Souls Remastered:                  20150100
    #   Sekiro:                                 20160100 (I think, could be 20160200)

    def _update_animation_type_enum(self, new_enum=True):
        """In Havok 2010, and possibly Havok 2012 (TBC), the enumeration for `AnimationType` was different to all
        subsequent versions, and requires a simple update to the integer value of those nodes.

        Note that most Soulsborne animations are "hkaSplineCompressedAnimation", and occasionally
        "hkaInterleavedAnimation" (maybe in Demons' Souls). The other types should basically never appear, and in fact
        some of them are only defined before or after the enum update. You will run into type errors anyway if these are
        present in the HKX.
        """

        if new_enum:
            for animation in self.find_nodes("hkaMirroredAnimation"):
                animation.value["type"].value = 2
            for animation in self.find_nodes("hkaSplineCompressedAnimation"):
                animation.value["type"].value = 3
            for animation in self.find_nodes("hkaQuantizedAnimation"):
                animation.value["type"].value = 4
            for animation in self.find_nodes("hkaPredictiveAnimation"):
                animation.value["type"].value = 5
            for animation in self.find_nodes("hkaReferencePoseAnimation"):
                animation.value["type"].value = 6
        else:
            # Old enum.
            for animation in self.find_nodes("hkaDeltaCompressedAnimation"):
                animation.value["type"].value = 2
            for animation in self.find_nodes("hkaWaveletCompressedAnimation"):
                animation.value["type"].value = 3
            for animation in self.find_nodes("hkaMirroredAnimation"):
                animation.value["type"].value = 4
            for animation in self.find_nodes("hkaSplineCompressedAnimation"):
                animation.value["type"].value = 5

    def _convert_swept_transform_to_tuple(self):
        """Convert `hkSweptTransform` nodes (member "sweptTransform" of `hkMotionState` to a Tuple of five `hkVector4f`
        instances.

        The `hkSweptTransform` type is modified itself and replaced with the new `T[N]` Tuple type, and any node that
        had this type has its value changed from a dictionary to a tuple.
        """
        hkSweptTransform = self.hkx_types.get_type("hkSweptTransform")
        if hkSweptTransform is None:
            return  # nothing to change

        vector_index = self.hkx_types.get_type_index("hkVector4f")

        # Convert `hkSweptTransform` to `T[N]`.
        hkSweptTransform.name = "T[N]"
        hkSweptTransform.parent_type_index = 0
        hkSweptTransform.pointer_type_index = vector_index
        hkSweptTransform.byte_size = 80
        hkSweptTransform.alignment = 16
        hkSweptTransform.templates = [HKXTemplate(name="tT", type_index=vector_index), HKXTemplate(name="vN", value=5)]
        hkSweptTransform.tag_format_flags = 11
        hkSweptTransform.tag_type_flags = 1320

        for node in self.all_nodes:
            if node.get_type_name(self.hkx_types) == "hkMotionState":
                swept_transform_node = node.value["sweptTransform"]  # type: HKXNode
                # noinspection PyTypeChecker
                new_tuple = (
                    swept_transform_node.value["centerOfMass0"],
                    swept_transform_node.value["centerOfMass1"],
                    swept_transform_node.value["rotation0"],  # `hkQuaternionf` will become `hkVector4f`
                    swept_transform_node.value["rotation1"],  # `hkQuaternionf` will become `hkVector4f`
                    swept_transform_node.value["centerOfMassLocal"],
                )
                swept_transform_node.value = new_tuple
                for vector_node in swept_transform_node.value:
                    vector_node.type_index = vector_index

    def _convert_uint8_to_ufloat8(self):
        """A few nodes are unpacked in 2010 as primitive `hkUint8` nodes that need to become `hkUFloat8` Class nodes."""

        ufloat8_index = self.hkx_types.get_type_index("hkUFloat8")

        for node in self.all_nodes:
            node_type_name = node.get_type_name(self.hkx_types)

            if node_type_name == "hkMotionState":
                uint8_node = node.value["maxLinearVelocity"]
                node.value["maxLinearVelocity"] = HKXNode(
                    type_index=ufloat8_index,
                    value={"value": uint8_node},
                )
                self.all_nodes.append(node.value["maxLinearVelocity"])

                uint8_node = node.value["maxAngularVelocity"]
                node.value["maxAngularVelocity"] = HKXNode(
                    type_index=ufloat8_index,
                    value={"value": uint8_node},
                )
                self.all_nodes.append(node.value["maxAngularVelocity"])

            elif node_type_name == "hkpBallSocketConstraintAtom":
                uint8_node = node.value["velocityStabilizationFactor"]
                node.value["velocityStabilizationFactor"] = HKXNode(
                    type_index=ufloat8_index,
                    value={"value": uint8_node},
                )
                self.all_nodes.append(node.value["velocityStabilizationFactor"])


class SkeletonHKX(HKX):
    """Loads HKX objects that are found in a "Skeleton" HKX file (inside `anibnd` binder, usually `Skeleton.HKX`)."""

    animation_container: tp.Optional[AnimationContainer]
    skeleton: Skeleton

    def __init__(
        self,
        file_source: HKX.Typing = None,
        dcx_magic: tuple[int, int] = (),
        compendium: tp.Optional[HKX] = None,
    ):
        super().__init__(file_source, dcx_magic, compendium)
        self.animation_container = self.get_variant_node(0).get_py_object(AnimationContainer)
        self.skeleton = self.animation_container.skeletons[0]

    def scale(self, factor: float):
        """Scale all bone translations in place by `factor`."""
        for pose in self.skeleton.reference_pose:
            pose.node.value["translation"].value = tuple(x * factor for x in pose.translation)

    @classmethod
    def from_anibnd(cls, anibnd_path: tp.Union[Path, str], prefer_bak=False) -> SkeletonHKX:
        anibnd_path = Path(anibnd_path)
        anibnd = Binder(anibnd_path, from_bak=prefer_bak)
        return cls(anibnd[1000000])


class AnimationHKX(HKX):
    """Loads HKX objects that are found in an "Animation" HKX file (inside `anibnd` binder, e.g. `a00_3000.hkx`).

    Currently assumes the animation is spline-compressed; will fail to initialize for other animation types.
    """

    animation_container: tp.Optional[AnimationContainer]
    animation: tp.Optional[SplineCompressedAnimation]
    animation_binding: tp.Optional[AnimationBinding]
    reference_frame_samples: tp.Optional[list[Vector4]]

    _anibnd: tp.Optional[BaseBND]

    def __init__(
        self,
        file_source: HKX.Typing = None,
        dcx_magic: tuple[int, int] = (),
        compendium: tp.Optional[HKX] = None,
    ):
        super().__init__(file_source, dcx_magic, compendium)
        self.animation_container = self.get_variant_node(0).get_py_object(AnimationContainer)
        self.animation = self.animation_container.animations[0]
        self.animation_binding = self.animation_container.bindings[0]
        if self.animation.extracted_motion:
            self.reference_frame_samples = self.animation.extracted_motion.reference_frame_samples
        self._base_bnd = None

    def get_spline_compressed_animation_data(self) -> SplineCompressedAnimationData:
        return SplineCompressedAnimationData(
            data=self.animation.data,
            transform_track_count=self.animation.number_of_transform_tracks,
            block_count=self.animation.num_blocks,
        )

    def decompress_spline_animation_data(self) -> list[list[QuatTransform]]:
        """Convert spline-compressed animation data to a list of lists (per track) of `QuatTransform` instances."""
        return self.get_spline_compressed_animation_data().to_transform_track_lists(
            frame_count=self.animation.num_frames,
            max_frames_per_block=self.animation.max_frames_per_block
        )

    def scale(self, factor: float):
        """Modifies all spline/static animation tracks, and also root motion (reference frame samples)."""
        scaled_data = self.get_spline_compressed_animation_data().get_scaled_animation_data(factor)
        self.animation.node.value["data"].value = scaled_data

        # Root motion (if present), sans W.
        if extracted_motion := self.animation.extracted_motion:
            for sample_node in extracted_motion.node.value["referenceFrameSamples"].value:
                # Scale X, Y, and Z only, not W.
                vec = sample_node.value
                sample_node.value = (vec[0] * factor, vec[1] * factor, vec[2] * factor, vec[3])

    def reverse(self):
        """Reverses all control points in all spline tracks, and also root motion (reference frame samples)."""
        reversed_data = self.get_spline_compressed_animation_data().get_reversed_animation_data()
        self.animation.node.value["data"].value = reversed_data

        # Root motion (if present).
        if extracted_motion := self.animation.extracted_motion:
            reversed_motion = tuple(reversed(extracted_motion.node.value["referenceFrameSamples"].value))
            extracted_motion.node.value["referenceFrameSamples"].value = reversed_motion

    @property
    def root_motion(self):
        """Usual modding alias for reference frame samples."""
        return self.reference_frame_samples

    @classmethod
    def from_anibnd(
        cls, anibnd_path: tp.Union[Path, str], animation_id: tp.Union[int, str], prefer_bak=False
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


class RagdollHKX(HKX):
    """Loads HKX objects that are found in a "Ragdoll" HKX file (inside `chrbnd` binder, e.g. `c0000.hkx`)."""

    animation_container: tp.Optional[AnimationContainer]
    standard_skeleton: tp.Optional[Skeleton]
    ragdoll_skeleton: tp.Optional[Skeleton]
    physics_data: tp.Optional[PhysicsData]
    ragdoll_instance: tp.Optional[RagdollInstance]
    standard_to_ragdoll_skeleton_mapper: tp.Optional[SkeletonMapper]
    ragdoll_to_standard_skeleton_mapper: tp.Optional[SkeletonMapper]

    def __init__(
        self,
        file_source: HKX.Typing = None,
        dcx_type: None | DCXType = DCXType.Null,
        compendium: tp.Optional[HKX] = None,
    ):
        super().__init__(file_source, dcx_type=dcx_type, compendium=compendium)
        self.animation_container = self.get_variant_node(0).get_py_object(AnimationContainer)
        self.standard_skeleton = self.animation_container.skeletons[0]
        self.ragdoll_skeleton = self.animation_container.skeletons[1]
        self.physics_data = self.get_variant_node(1).get_py_object(PhysicsData)
        self.ragdoll_instance = self.get_variant_node(2).get_py_object(RagdollInstance)
        self.ragdoll_to_standard_skeleton_mapper = self.get_variant_node(3).get_py_object(SkeletonMapper)
        self.standard_to_ragdoll_skeleton_mapper = self.get_variant_node(4).get_py_object(SkeletonMapper)

    def scale(self, factor: float):
        """Scale all translation information, including:
            - bones in both the standard and ragdoll skeletons
            - rigid body collidables
            - motion state transforms and swept transforms
            - skeleton mapper transforms in both directions

        This is currently working well, though since actual "ragdoll mode" only occurs when certain enemies die, any
        mismatched (and probably harmless) physics will be more of an aesthetic issue.
        """
        for pose in self.standard_skeleton.reference_pose:
            pose.node.value["translation"].value = tuple(x * factor for x in pose.translation)
        for pose in self.ragdoll_skeleton.reference_pose:
            pose.node.value["translation"].value = tuple(x * factor for x in pose.translation)

        for rigid_body in self.physics_data.systems[0].rigid_bodies:
            self.scale_shape(rigid_body.collidable.shape, factor)

            # TODO: motion inertiaAndMassInv?

            motion_state = rigid_body.motion.motion_state
            flat_transform = motion_state.transform.to_flat_column_order()
            scaled_translate = tuple(x * factor for x in flat_transform[12:15]) + (1.0,)
            motion_state.node.value["transform"].value = tuple(flat_transform[:12]) + scaled_translate
            motion_state.node.value["objectRadius"].value *= factor

            swept_transform = rigid_body.motion.motion_state.swept_transform
            swept_transform.node.value[0].value = tuple(x * factor for x in swept_transform.center_of_mass_0)
            swept_transform.node.value[1].value = tuple(x * factor for x in swept_transform.center_of_mass_1)
            # Indices 3 and 4 are rotations.
            swept_transform.node.value[4].value = tuple(x * factor for x in swept_transform.center_of_mass_local)

        # TODO: constraint instance transforms?

        for mapper in (self.ragdoll_to_standard_skeleton_mapper, self.standard_to_ragdoll_skeleton_mapper):
            for simple in mapper.mapping.simple_mappings:
                self.scale_tuple_member(simple.node.value["aFromBTransform"], "translation", factor)
            for chain in mapper.mapping.chain_mappings:
                self.scale_tuple_member(chain.node.value["startAFromBTransform"], "translation", factor)

    def scale_shape(self, shape, factor: float):
        if "radius" in shape.node.value:  # hkpConvexShape
            shape.node.value["radius"].value = shape.radius * factor
            if "vertexA" in shape.node.value:  # hkpCapsuleShape
                self.scale_tuple_member(shape.node, "vertexA", factor)
                self.scale_tuple_member(shape.node, "vertexB", factor)
        elif "moppData" in shape.node.value:  # hkpMoppBvTreeShape
            self.scale_shape(shape.child.child_shape, factor)
        elif "embeddedTrianglesSubpart" in shape.node.value:  # hkpExtendedMeshShape
            ets_node = shape.node.value["embeddedTrianglesSubpart"]
            self.scale_tuple_member(ets_node.value["transform"], "translation", factor)
            self.scale_tuple_member(shape.node, "aabbHalfExtents", factor)
            self.scale_tuple_member(shape.node, "aabbCenter", factor)
            if "meshstorage" in shape.node.value:  # hkpStorageExtendedMeshShape
                for mesh_node in shape.node.value["meshstorage"].value:
                    for vertex_node in mesh_node.value["vertices"].value:
                        vertex_node.value = tuple(v * factor for v in vertex_node.value)

    @staticmethod
    def scale_tuple_member(node: HKXNode, member_name: str, factor: float):
        node.value[member_name].value = tuple(x * factor for x in node.value[member_name].value)

    @classmethod
    def from_chrbnd(cls, chrbnd_path: tp.Union[Path, str], prefer_bak=False) -> RagdollHKX:
        chrbnd_path = Path(chrbnd_path)
        if (bak_path := chrbnd_path.with_suffix(chrbnd_path.suffix + ".bak")).is_file() and prefer_bak:
            chrbnd_path = bak_path
        chrbnd = Binder(chrbnd_path)
        model_name = chrbnd_path.name.split(".")[0]  # e.g. "c0000"
        return cls(chrbnd[f"{model_name}.hkx"])


class ClothHKX(HKX):
    """Loads HKX objects that are found in a "Cloth" HKX file (inside `chrbnd` binder, e.g. `c2410_c.hkx`).

    This file is not used for every character - only those with cloth physics (e.g. capes).
    """

    physics_data: tp.Optional[PhysicsData]

    def __init__(
        self,
        file_source: HKX.Typing = None,
        dcx_type: None | DCXType = DCXType.Null,
        compendium: tp.Optional[HKX] = None,
    ):
        super().__init__(file_source, dcx_type=dcx_type, compendium=compendium)
        self.physics_data = self.get_variant_node(0).get_py_object(PhysicsData)

    def scale(self, factor: float):
        """Scale all translation information, including:
            - rigid body collidables
            - motion state transforms and swept transforms

        TODO: Since cloth is always in "ragdoll" mode, forces may need to be updated more cautiously here.
        """
        for rigid_body in self.physics_data.systems[0].rigid_bodies:
            shape = rigid_body.collidable.shape
            shape.node.value["radius"].value = shape.radius * factor
            if "vertexA" in shape.node.value:  # capsule
                shape.node.value["vertexA"].value = tuple(x * factor for x in shape.vertex_A)
                shape.node.value["vertexB"].value = tuple(x * factor for x in shape.vertex_B)

            # TODO: motion inertiaAndMassInv?

            motion_state = rigid_body.motion.motion_state
            flat_transform = motion_state.transform.to_flat_column_order()
            scaled_translate = tuple(x * factor for x in flat_transform[12:15]) + (1.0,)
            motion_state.node.value["transform"].value = tuple(flat_transform[:12]) + scaled_translate
            motion_state.node.value["objectRadius"].value *= factor

            swept_transform = rigid_body.motion.motion_state.swept_transform
            swept_transform.node.value[0].value = tuple(x * factor for x in swept_transform.center_of_mass_0)
            swept_transform.node.value[1].value = tuple(x * factor for x in swept_transform.center_of_mass_1)
            # Indices 3 and 4 are rotations.
            swept_transform.node.value[4].value = tuple(x * factor for x in swept_transform.center_of_mass_local)

        for constraint_instance in self.physics_data.systems[0].constraints:

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
    def from_chrbnd(cls, chrbnd_path: tp.Union[Path, str], prefer_bak=False) -> ClothHKX:
        chrbnd_path = Path(chrbnd_path)
        if (bak_path := chrbnd_path.with_suffix(chrbnd_path.suffix + ".bak")).is_file() and prefer_bak:
            chrbnd_path = bak_path
        chrbnd = Binder(chrbnd_path)
        model_name = chrbnd_path.name.split(".")[0]  # e.g. "c0000"
        try:
            return cls(chrbnd[f"{model_name}_c.hkx"])
        except KeyError:
            raise FileNotFoundError(f"No '*_c.hkx' cloth physics file found in chrbnd {chrbnd_path}.")
