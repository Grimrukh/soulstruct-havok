from __future__ import annotations

__all__ = ["HKX", "HKX_ROOT_TYPING"]

import logging
import typing as tp
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

from soulstruct.base.game_file import GameFile
from soulstruct.containers import Binder, BinderEntry
from soulstruct.containers.dcx import DCXType, decompress, is_dcx
from soulstruct.utilities.binary import *
from soulstruct.utilities.future import StrEnum

from .packfile.packer import PackFilePacker
from .packfile.structs import PackfileHeaderInfo
from .packfile.unpacker import PackFileUnpacker
from .tagfile.packer import TagFilePacker
from .tagfile.unpacker import TagFileUnpacker, MissingCompendiumError
from .types import hk2010, hk2014, hk2015, hk2018
from .types.info import TypeInfo

try:
    Self = tp.Self
except AttributeError:  # < Python 3.11
    Self = "HKX"


_LOGGER = logging.getLogger(__name__)

HKX_ROOT_TYPING = tp.Union[
    None,
    hk2010.hkRootLevelContainer,
    hk2014.hkRootLevelContainer,
    hk2015.hkRootLevelContainer,
    hk2018.hkRootLevelContainer,
]


class HavokFileFormat(StrEnum):
    """Enum of the two types of Havok files used in FromSoft games."""
    Packfile = "packfile"
    Tagfile = "tagfile"


@dataclass(slots=True)
class HKX(GameFile):
    """Havok data used in FromSoft games to hold model skeletons, animations, ragdoll physics, collisions, etc.

    HKX files are a form of compressed XML used by the Havok physics engine. This class can read from both pre-2015
    `packfile`-type HKX files (used up to and including DS3) and post-2015 `tagfile`-type HKX files (used in DSR and
    Sekiro), and freely write to either format.

    Use `write_packfile()` and `write_tagfile()` to specify the format you want to output. If you use `write()`, it will
    default to writing the format that was loaded. Same for `pack()` and its two variants.
    """
    # Can be defined by subclasses with utility methods for specific versions of Havok.
    TYPES_MODULE: tp.ClassVar[ModuleType | None] = None

    root: HKX_ROOT_TYPING = None
    hk_format: HavokFileFormat = None
    hk_version: str = ""  # e.g. "2010"
    unpacker: None | TagFileUnpacker | PackFileUnpacker = None
    is_compendium: bool = False
    compendium_ids: list[bytes] = field(default_factory=list)
    # Maps `hk` type names to non-standard hash values found in file.
    hsh_overrides: dict[str, int] = field(default_factory=dict)

    # Extra information retained from the packfile header, if loaded from a packfile.
    packfile_header_info: None | PackfileHeaderInfo = None

    @classmethod
    def from_reader(cls, reader: BinaryReader, hk_format: HavokFileFormat = None, compendium: HKX = None) -> Self:
        if hk_format is None:
            # Auto-detect format.
            hk_format = cls._detect_hk_format(reader)
            if hk_format is None:
                raise TypeError("Could not detect if HKX binary data is a packfile or tagfile.")

        if hk_format == HavokFileFormat.Packfile:
            if compendium is not None:
                raise ValueError("`compendium` was passed with HKX packfile source (used only by newer tagfiles).")
            return cls.from_packfile_reader(reader)
        elif hk_format == HavokFileFormat.Tagfile:
            return cls.from_tagfile_reader(reader, compendium=compendium)

        raise ValueError(f"Invalid `hk_format` value: {hk_format}")

    @classmethod
    def from_bytes(
        cls,
        data: bytes | bytearray | tp.BinaryIO | BinaryReader | BinderEntry,
        hk_format: HavokFileFormat = None,
        compendium: HKX = None,
    ) -> Self:
        """Load instance from binary data or binary stream (or `BinderEntry.data`)."""
        reader = BinaryReader(data) if not isinstance(data, BinaryReader) else data  # type: BinaryReader

        if is_dcx(reader):
            try:
                data, dcx_type = decompress(reader)
            finally:
                reader.close()
            reader = BinaryReader(data)
        else:
            dcx_type = DCXType.Null

        try:
            binary_file = cls.from_reader(reader, hk_format, compendium)
            binary_file.dcx_type = dcx_type
        except Exception:
            _LOGGER.error(f"Error occurred while reading `{cls.__name__}` from binary data. See traceback.")
            raise
        finally:
            reader.close()
        return binary_file

    @classmethod
    def from_path(cls, path: str | Path, hk_format: HavokFileFormat = None, compendium: HKX = None) -> Self:
        path = Path(path)
        try:
            game_file = cls.from_bytes(BinaryReader(path), hk_format, compendium)
        except Exception:
            _LOGGER.error(f"Error occurred while reading `{cls.__name__}` with path '{path}'. See traceback.")
            raise
        game_file.path = path
        return game_file

    @property
    def hk_type_infos(self) -> list[TypeInfo]:
        if not self.unpacker:
            raise AttributeError("Unpacker not created. Cannot retrieve Havok `TypeInfo`s.")
        return self.unpacker.hk_type_infos

    @classmethod
    def _detect_hk_format(cls, reader: BinaryReader) -> None | HavokFileFormat:
        """Peek into HKX `reader` to find out if it is a "packfile", "tagfile", or unknown (`None`)."""
        first_eight_bytes = reader.unpack_bytes(length=8, offset=reader.position)
        if first_eight_bytes == b"\x57\xE0\xE0\x57\x10\xC0\xC0\x10":
            return HavokFileFormat.Packfile
        elif first_eight_bytes[4:8] in {b"TAG0", b"TCM0"}:
            return HavokFileFormat.Tagfile
        return None

    @classmethod
    def from_binder(
        cls,
        binder: Binder,
        entry_id_or_name: int | str,
        hk_format: HavokFileFormat = None,
        compendium_name: str = "",
    ):
        """Use or auto-detect `{binder_source.name}.compendium` file in binder, if present."""
        compendium, compendium_name = cls.get_compendium_from_binder(binder, compendium_name)

        try:
            return cls.from_bytes(binder[entry_id_or_name], hk_format=hk_format, compendium=compendium)
        except MissingCompendiumError:
            if compendium_name != "":
                raise MissingCompendiumError(
                    f"Binder entry '{entry_id_or_name}' requires a compendium, but compendium '{compendium_name}' "
                    f"could not be found in given binder. Use `compendium_name` argument if it has another name."
                )
            raise MissingCompendiumError(
                f"Binder entry '{entry_id_or_name}' requires a compendium, but `compendium_name` was not given and a "
                f"'.compendium' entry could not be found in the given binder."
            )

    @staticmethod
    def get_compendium_from_binder(binder: Binder, compendium_name="") -> tuple[HKX, str]:
        """Search for '.compendium' HKX type file in `binder`. Name may be given, or the extension alone may be sought.

        Returns the compendium found (may be `None`) and its name.
        """
        if compendium_name == "":
            # Search for '*.compendium' binder entry.
            compendium_entries = binder.find_entries_matching_name(r".*\.compendium")
            if len(compendium_entries) == 1:
                compendium = HKX.from_bytes(compendium_entries[0])
                compendium_name = compendium_entries[0].name
            elif len(compendium_entries) > 1:
                raise ValueError(
                    f"Multiple '.compendium' files found in binder: {[e.name for e in compendium_entries]}."
                )
            else:
                # Otherwise, no compendiums found; assume not needed and complain below if otherwise.
                compendium = None
        else:
            if compendium_name in binder.entries_by_name:
                compendium = HKX.from_bytes(binder.entries_by_name[compendium_name])  # always HKX base class
            else:
                raise ValueError(f"Compendium file '{compendium_name}' not present in given binder.")
        return compendium, compendium_name

    @classmethod
    def from_packfile_reader(cls, reader: BinaryReader) -> Self:
        """`reader` HKX file format is known to be `packfile`."""
        unpacker = PackFileUnpacker()
        unpacker.unpack(reader)

        return cls(
            unpacker=unpacker,
            hk_format=HavokFileFormat.Packfile,
            root=unpacker.root,
            packfile_header_info=unpacker.get_header_info(),
        )

    @classmethod
    def from_tagfile_reader(cls, reader: BinaryReader, compendium: tp.Optional[HKX] = None) -> Self:
        """Buffer is known to be `tagfile`."""
        unpacker = TagFileUnpacker()
        unpacker.unpack(reader, compendium=compendium)

        return cls(
            unpacker=unpacker,
            hk_format=HavokFileFormat.Tagfile,
            root=unpacker.root,
            is_compendium=unpacker.is_compendium,
            compendium_ids=unpacker.compendium_ids,
            hsh_overrides=unpacker.hsh_overrides,
        )

    def to_writer(self) -> BinaryWriter:
        if self.hk_format == HavokFileFormat.Packfile:
            if not self.packfile_header_info:
                raise ValueError("You must set `hkx.packfile_header_info` before you can write to packfile format.")
            return PackFilePacker(self).to_writer(self.packfile_header_info)
        elif self.hk_format == HavokFileFormat.Tagfile:
            return TagFilePacker(self).to_writer(hsh_overrides=self.hsh_overrides)
        raise ValueError(f"Invalid `hk_format`: {self.hk_format}. Should be 'packfile' or 'tagfile'.")

    def get_root_tree_string(self, max_primitive_sequence_size=-1) -> str:
        return self.root.get_tree_string(max_primitive_sequence_size=max_primitive_sequence_size)

    # region OUTDATED CONVERSION METHODS
    # TODO: All ridiculously outdated, but contains info I need to move elsewhere.

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
    # endregion
