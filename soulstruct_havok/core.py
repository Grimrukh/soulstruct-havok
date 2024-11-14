from __future__ import annotations

__all__ = ["HKX", "HKX_ROOT_TYPING", "HavokFileFormat"]

import logging
import re
import typing as tp
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from types import ModuleType

from soulstruct.base.game_file import GameFile
from soulstruct.containers import Binder, BinderEntry, EntryNotFoundError
from soulstruct.dcx import DCXType, decompress, is_dcx
from soulstruct.utilities.binary import *

from soulstruct_havok.enums import PyHavokModule
from soulstruct_havok.packfile.packer import PackFilePacker
from soulstruct_havok.packfile.structs import PackfileHeaderInfo
from soulstruct_havok.packfile.unpacker import PackFileUnpacker
from soulstruct_havok.tagfile.packer import TagFilePacker
from soulstruct_havok.tagfile.unpacker import TagFileUnpacker, MissingCompendiumError
from soulstruct_havok.types import hk2010, hk2014, hk2015, hk2016, hk2018
from soulstruct_havok.types.info import TypeInfo

_LOGGER = logging.getLogger("soulstruct_havok")

HKX_ROOT_TYPING = tp.Union[
    None,
    hk2010.hkRootLevelContainer,
    hk2014.hkRootLevelContainer,
    hk2015.hkRootLevelContainer,
    hk2016.hkRootLevelContainer,
    hk2018.hkRootLevelContainer,
]


class HavokFileFormat(StrEnum):
    """Enum of the two types of Havok files used in FromSoft games."""
    Packfile = "packfile"
    Tagfile = "tagfile"


@dataclass(slots=True)
class HKX(GameFile):
    """Havok data used in FromSoft games to hold model skeletons, animations, ragdoll physics, collisions, etc.

    HKX files are a form of binary XML used by the Havok physics engine. This class can read from both pre-2015
    `packfile`-type HKX files (used up to and including DS3) and post-2015 `tagfile`-type HKX files (used in DSR,
    Sekiro, and Elden Ring), and freely write to either format.

    Use `write_packfile()` and `write_tagfile()` to specify the format you want to output. If you use `write()`, it will
    default to writing the format that was loaded and set to `hk_format`. Same for `pack()` and its two variants.

    Versions used by various FromSoftware games:
        Demon's Souls (PSE):                    Havok-5.5.0-r1 (packfile)
        Dark Souls Prepare to Die Edition:      hk_2010-2.0-r1 (packfile)
        Bloodborne:                             hk_2014-1.0-r1 (packfile)
        Dark Souls 3:                           hk_2014-1.0-r1 (packfile)
        Dark Souls Remastered:                  20150100 (tagfile)
        Sekiro:                                 20160200 (tagfile)
        Elden Ring:                             20180100 (tagfile)
    """
    EXT: tp.ClassVar[str] = ".hkx"

    # Can be defined by subclasses with utility methods for specific versions of Havok.
    TYPES_MODULE: tp.ClassVar[ModuleType | None] = None

    root: HKX_ROOT_TYPING = None
    hk_format: HavokFileFormat = None
    # Havok version string. Packfiles support any format (e.g. 'Havok-5.5.0-r1' or 'hk_2010.2.0-r1'), but tagfiles
    # require the format 'YYYYVVvv' (e.g. '20150100' for DSR) and will raise an error if not in this format.
    hk_version: str = ""
    unpacker: None | TagFileUnpacker | PackFileUnpacker = None
    is_big_endian: bool = False
    is_compendium: bool = False
    compendium_ids: list[bytes] = field(default_factory=list)
    # Maps `hk` type names to non-standard hash values found in file.
    hsh_overrides: dict[str, int] = field(default_factory=dict)

    # Extra information retained from the packfile header, if loaded from a packfile.
    packfile_header_info: None | PackfileHeaderInfo = None

    @classmethod
    def from_reader(cls, reader: BinaryReader, hk_format: HavokFileFormat = None, compendium: HKX = None) -> tp.Self:
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
    ) -> tp.Self:
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
    def from_path(cls, path: str | Path, hk_format: HavokFileFormat = None, compendium: HKX = None) -> tp.Self:
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
        entry_spec: int | Path | str | re.Pattern = None,
        hk_format: HavokFileFormat = None,
        compendium_name: str = "",
    ) -> tp.Self:
        """Use or auto-detect `{binder_source.name}.compendium` file in binder, if present."""
        compendium, compendium_name = cls.get_compendium_from_binder(binder, compendium_name)

        entry = binder[entry_spec]
        try:
            hkx = cls.from_bytes(entry, hk_format=hk_format, compendium=compendium)
        except MissingCompendiumError:
            if compendium_name != "":
                raise MissingCompendiumError(
                    f"Binder entry '{entry_spec}' requires a compendium, but compendium '{compendium_name}' "
                    f"could not be found in given binder. Use `compendium_name` argument if it has another name."
                )
            raise MissingCompendiumError(
                f"Binder entry '{entry_spec}' requires a compendium, but `compendium_name` was not given and a "
                f"'.compendium' entry could not be found in the given binder."
            )
        hkx.path = entry.path
        return hkx

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
                # This can happen in `DivBinder`s, where the same compendium is duplicated into every written Binder.
                # We allow this if their data are identical.
                if len(set(e.data for e in compendium_entries)) > 1:
                    raise ValueError(
                        f"Multiple '.compendium' files found in binder: {[e.name for e in compendium_entries]}."
                    )
                else:
                    compendium = HKX.from_bytes(compendium_entries[0])
                    compendium_name = compendium_entries[0].name
            else:
                # Otherwise, no compendiums found; assume not needed and complain below if otherwise.
                compendium = None
        else:
            try:
                compendium_entry = binder.find_entry_name(compendium_name)
            except EntryNotFoundError:
                raise MissingCompendiumError(f"Compendium file '{compendium_name}' not present in given binder.")
            compendium = compendium_entry.to_binary_file(HKX)  # always base `HKX` class
        return compendium, compendium_name

    @classmethod
    def from_packfile_reader(cls, reader: BinaryReader) -> tp.Self:
        """`reader` HKX file format is known to be `packfile`."""
        unpacker = PackFileUnpacker()
        unpacker.unpack(reader)

        return cls(
            unpacker=unpacker,
            hk_version=unpacker.hk_version,  # packfile format (e.g. 'Havok-5.5.0-r1' or 'hk_2010.2.0-r1')
            hk_format=HavokFileFormat.Packfile,
            is_big_endian=unpacker.byte_order == ByteOrder.BigEndian,
            root=unpacker.root,
            packfile_header_info=unpacker.get_header_info(),
        )

    @classmethod
    def from_tagfile_reader(cls, reader: BinaryReader, compendium: tp.Optional[HKX] = None) -> tp.Self:
        """Buffer is known to be `tagfile`."""
        unpacker = TagFileUnpacker()
        unpacker.unpack(reader, compendium=compendium)

        return cls(
            unpacker=unpacker,
            hk_version=unpacker.hk_version,  # tagfile format 'YYYYVVvv'
            hk_format=HavokFileFormat.Tagfile,
            is_big_endian=unpacker.byte_order == ByteOrder.BigEndian,
            root=unpacker.root,
            is_compendium=unpacker.is_compendium,
            compendium_ids=unpacker.compendium_ids,
            hsh_overrides=unpacker.hsh_overrides,
        )

    def to_writer(self) -> BinaryWriter:
        if self.hk_format == HavokFileFormat.Packfile:
            if not self.packfile_header_info:
                raise ValueError("You must set `hkx.packfile_header_info` before you can write to packfile format.")
            # Update endianness of packfile header info.
            self.packfile_header_info.is_little_endian = not self.is_big_endian
            return PackFilePacker(self).to_writer(self.packfile_header_info)
        elif self.hk_format == HavokFileFormat.Tagfile:
            # TODO: Can't automatically detect `byte_order` or `long_varints` for tagfiles.
            #  But since it's a new format (2015+), it's probably always long, and little-endian for PC at least.
            return TagFilePacker(self).to_writer(
                hsh_overrides=self.hsh_overrides,
                byte_order=ByteOrder.big_endian_bool(self.is_big_endian),
                long_varints=True,
            )
        raise ValueError(f"Invalid `hk_format`: {self.hk_format}. Should be 'packfile' or 'tagfile'.")

    @property
    def py_havok_module(self) -> PyHavokModule:
        """Currently only have one Havok types module per release year.

        Trivially retrieved from tagfile version strings. For packfile version strings, the first four digits before the
        first '-' are used (so '-r1' suffix is ignored).
        """
        if self.hk_format == HavokFileFormat.Tagfile:
            return PyHavokModule(self.hk_version[:4])
        prefix = self.hk_version.removeprefix("Havok-").removeprefix("hk_").split("-")[0]
        digits = re.findall(r"\d+", prefix)
        first_four = "".join(digits)[:4]  # e.g. '2010' or '550'
        if len(first_four) < 3:
            raise ValueError(f"Could not find year/version in Havok version string: {self.hk_version}")

        # NOTE: Some old Demon's Souls map collisions use Havok 5.1.0, but the relevant classes are unchanged.
        # Doing a hacky redirect here for now, since I doubt I will ever support 5.1.0 properly.
        if first_four == "510":
            first_four = "550"

        return PyHavokModule(first_four)

    def get_root_tree_string(
        self,
        max_primitive_sequence_size=-1,
        max_nonprimitive_sequence_size=-1,
    ) -> str:
        return self.root.get_tree_string(
            max_primitive_sequence_size=max_primitive_sequence_size,
            max_nonprimitive_sequence_size=max_nonprimitive_sequence_size,
        )

    def __repr__(self) -> str:
        """Returns names of root variant classes."""
        if self.root is None:
            root = "None"
        elif self.root.__class__.__name__ == "hkRootLevelContainer":
            variant_cls_names = ",\n    ".join(f"{c.className}(\"{c.name}\")" for c in self.root.namedVariants)
            root = f"{self.root.__class__.__name__}(\n    {variant_cls_names},\n  )"
        else:
            root = self.root.__class__.__name__

        return (
            f"{self.cls_name}(\n"
            f"  dcx={self.dcx_type.name},\n"
            f"  path={self.path},\n"
            f"  hk_format={self.hk_format},\n"
            f"  hk_version={self.hk_version},\n"
            f"  root={root},\n"
            f")"
        )

    base_hkx_repr = __repr__
