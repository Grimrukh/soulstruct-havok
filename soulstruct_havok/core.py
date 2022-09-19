from __future__ import annotations

__all__ = ["HKX"]

import io
import logging
import typing as tp
from pathlib import Path

from soulstruct.base.game_file import GameFile, InvalidGameFileTypeError
from soulstruct.containers.dcx import DCXType
from soulstruct.containers.entry import BinderEntry
from soulstruct.utilities.binary import BinaryReader

from .packfile.packer import PackFilePacker
from .packfile.structs import PackFileHeaderExtension, PackFileVersion
from .packfile.unpacker import PackFileUnpacker
from .tagfile.packer import TagFilePacker
from .tagfile.unpacker import TagFileUnpacker
from .types import hk, hk2010, hk2014, hk2015, hk2018
from .types.info import TypeInfo


_LOGGER = logging.getLogger(__name__)

ROOT_TYPING = (
    None
    | hk2010.hkRootLevelContainer
    | hk2014.hkRootLevelContainer
    | hk2015.hkRootLevelContainer
    | hk2018.hkRootLevelContainer
)


class HKX(GameFile):
    """Havok data used in FromSoft games to hold model (FLVER) skeletons, animations, ragdoll physica, collisions, etc.

    HKX files are a form of compressed XML used by the Havok physics engine. This class can read from both pre-2015
    `packfile`-type HKX files (used up to and including DS3) and post-2015 `tagfile`-type HKX files (used in DSR and
    Sekiro), and freely write to either format.

    Use `write_packfile()` and `write_tagfile()` to specify the format you want to output. If you use `write()`, it will
    default to writing the format that was loaded. Same for `pack()` and its two variants.
    """
    PACKFILE = "packfile"
    TAGFILE = "tagfile"

    root: ROOT_TYPING
    hk_format: str  # "packfile" or "tagfile"
    unpacker: None | TagFileUnpacker | PackFileUnpacker
    is_compendium: bool
    compendium_ids: list[bytes]
    hsh_overrides: dict[str, int]  # maps `hk` type names to non-standard hash values found in file

    packfile_header_version: None | PackFileVersion
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
        if hk_format not in {"", self.TAGFILE, self.PACKFILE}:
            raise ValueError(f"`hk_format` must be 'tagfile' or 'packfile' if given, not: {hk_format}")
        self.root = None
        self.all_nodes = []
        self.hk_format = hk_format
        self.is_compendium = False
        self.unpacker = None
        self.compendium_ids = []
        self.hsh_overrides = {}

        self.packfile_header_version = None
        self.packfile_pointer_size = None
        self.packfile_is_little_endian = None
        self.packfile_padding_option = None
        self.packfile_contents_version_string = None
        self.packfile_flags = None
        self.packfile_header_extension = None

        super().__init__(file_source, dcx_type=dcx_type, compendium=compendium, hk_format=hk_format)

    @property
    def hk_version(self) -> str:
        if not self.unpacker:
            raise AttributeError("Unpacker not created. Cannot retrieve Havok version.")
        return self.unpacker.hk_version

    @property
    def hk_type_infos(self) -> list[TypeInfo]:
        if not self.unpacker:
            raise AttributeError("Unpacker not created. Cannot retrieve Havok `TypeInfo`s.")
        return self.unpacker.hk_type_infos

    def _handle_other_source_types(self, file_source, compendium: tp.Optional[HKX] = None, hk_format=""):

        if isinstance(file_source, str):
            file_source = Path(file_source)
        if isinstance(file_source, BinderEntry):
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

    @classmethod
    def _detect_hk_format(cls, reader: BinaryReader) -> None | str:
        """Peek into buffer to find out if it is a "packfile", "tagfile", or unknown (`None`)."""
        first_eight_bytes = reader.unpack_bytes(length=8, offset=reader.position)
        if first_eight_bytes == b"\x57\xE0\xE0\x57\x10\xC0\xC0\x10":
            return cls.PACKFILE
        elif first_eight_bytes[4:8] in {b"TAG0", b"TCM0"}:  # why was 'TCRF' accepted here? Sekiro?
            return cls.TAGFILE
        return None

    def unpack(self, reader: BinaryReader, hk_format="", compendium: tp.Optional[HKX] = None):
        if not hk_format:
            hk_format = self.hk_format
        if hk_format == self.PACKFILE:
            if compendium is not None:
                raise ValueError("`compendium` was passed with HKX packfile source (used only by newer tagfiles).")
            self.unpack_packfile(reader)
        elif hk_format == self.TAGFILE:
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
        self.is_compendium = self.unpacker.is_compendium
        self.compendium_ids = self.unpacker.compendium_ids
        self.hsh_overrides = self.unpacker.hsh_overrides

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
            return TagFilePacker(self).pack(hsh_overrides=self.hsh_overrides)
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

    def set_variant_attribute(self, attr_name: str, hk_type: tp.Type[hk], variant_index: int):
        variant = self.root.namedVariants[variant_index].variant
        if not isinstance(variant, hk_type):
            raise TypeError(
                f"HKX variant index {variant_index} did not have type {hk_type.__name__} ({variant.__class__.__name__})"
            )
        setattr(self, attr_name, variant)

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
