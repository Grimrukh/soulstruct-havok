from __future__ import annotations

import abc
import copy
import logging
import typing as tp
from functools import wraps
from pathlib import Path
from xml.etree import ElementTree

from .enums import TagFormatFlags, TagDataType

_LOGGER = logging.getLogger("soulstruct_havok")


def _cache_type(cache_key: str):
    """Produces a decorator for a `HKXType` method that returns another `HKXType` from given `hkx_type_list`.

    If the given list is the same as the one already cached, the cached type is used. Otherwise, the cached list and
    type are regenerated.
    """

    def decorator(func: tp.Callable[[HKXType, HKXTypeList], HKXType]):

        @wraps(func)
        def decorated(self: HKXType, hkx_type_list: HKXTypeList):
            if self._cached_hkx_type_list is not hkx_type_list:
                self._cached_hkx_type_list = hkx_type_list
                self._cached_types = {}
            return self._cached_types.setdefault(cache_key, func(self, hkx_type_list))

        return decorated

    return decorator


class HKXType:
    """Type of node that appears in HKX files."""

    name: str
    parent_type_index: int
    pointer_type_index: int
    version: int
    byte_size: int
    alignment: int
    abstract_value: int
    hsh: int
    members: list[HKXMember]
    interfaces: list[HKXInterface]
    templates: list[HKXTemplate]

    # Types read from `packfile`-type HKX files are converted to these flags.
    tag_format_flags: int  # tells tagfile unpacker which type fields to expect (version, alignment, etc.)
    tag_type_flags: int  # four bytes read in type declaration in tagfile HKX

    # Internal XML use.
    tag: str  # TODO: Use a dictionary in XMLSerializer instead of abusing this class.
    _cached_hkx_type_list: tp.Optional[HKXTypeList]
    _cached_types: dict[str, HKXType]

    def __init__(
        self,
        name: str,
        parent_type_index=0,
        pointer_type_index=0,
        version: tp.Optional[int] = None,
        byte_size=0,
        alignment=0,
        abstract_value: tp.Optional[int] = None,
        hsh: tp.Optional[int] = None,
        templates: list[HKXTemplate] = (),
        members: list[HKXMember] = (),
        interfaces: list[HKXInterface] = (),
        tag_format_flags=1,  # default is `SubType`
        tag_type_flags=0,  # default is `Void`
        tag="",
    ):
        if not isinstance(parent_type_index, int):
            raise TypeError(f"`parent_type_index` must be an integer, not {parent_type_index}.")
        if not isinstance(pointer_type_index, int):
            raise TypeError(f"`pointer_type_index` must be an integer, not {pointer_type_index}.")

        self._name = name  # accessed via property so `name_without_colons` is set
        self.name_without_colons = name.replace("::", "")
        self.parent_type_index = parent_type_index
        self.pointer_type_index = pointer_type_index
        self.version = version
        self.byte_size = byte_size
        self.members = list(members)
        self.templates = list(templates)
        self.interfaces = list(interfaces)
        self.tag_format_flags = tag_format_flags
        self._tag_type_flags = tag_type_flags  # accessed via property so `tag_data_type` is set
        self.tag_data_type = TagDataType(self._tag_type_flags & 0xFF)
        self.alignment = alignment
        self.abstract_value = abstract_value
        self.hsh = hsh

        # Internal use for XML.
        self.tag = tag

        self._cached_hkx_type_list = None
        self._cached_types = {}

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        self.name_without_colons = value.replace("::", "")

    @property
    def tag_type_flags(self) -> int:
        return self._tag_type_flags

    @tag_type_flags.setter
    def tag_type_flags(self, value: int):
        self._tag_type_flags = value
        self.tag_data_type = TagDataType(self.tag_type_flags & 0xFF)

    def reindex(self, old_hkx_types: HKXTypeList, new_hkx_types: HKXTypeList):
        """Change type index, currently relative to `old_hkx_types`, to point to the same `HKXType` object in
        `new_hkx_types.`

        The `HKXType` instance must be the same - it cannot be looked up by name.
        """
        if self.parent_type_index:
            parent_type = old_hkx_types[self.parent_type_index]
            self.parent_type_index = new_hkx_types.get_type_index(parent_type)
        if self.pointer_type_index:
            pointer_type = old_hkx_types[self.pointer_type_index]
            self.pointer_type_index = new_hkx_types.get_type_index(pointer_type)
        for t in self.templates:
            t.reindex(old_hkx_types, new_hkx_types)
        for m in self.members:
            m.reindex(old_hkx_types, new_hkx_types)
        for i in self.interfaces:
            i.reindex(old_hkx_types, new_hkx_types)

    @_cache_type("parent_type")
    def get_parent_type(self, hkx_types: HKXTypeList) -> tp.Optional[HKXType]:
        if self.parent_type_index:
            return hkx_types[self.parent_type_index]
        return None

    def get_parent_name(self, hkx_types: HKXTypeList) -> str:
        return str(self.get_parent_type(hkx_types))

    @_cache_type("pointer_type")
    def get_pointer_type(self, hkx_types: HKXTypeList) -> tp.Optional[HKXType]:
        if self.pointer_type_index:
            return hkx_types[self.pointer_type_index]
        return None

    def get_pointer_name(self, hkx_types: HKXTypeList) -> str:
        return str(self.get_pointer_type(hkx_types))

    @_cache_type("pointer_base_type")
    def get_pointer_base_type(self, hkx_types: HKXTypeList) -> tp.Optional[HKXType]:
        """Get the base type of this type's pointer type. NOT the same as `get_base_pointer_type`."""
        if self.pointer_type_index:
            return hkx_types[self.pointer_type_index].get_base_type(hkx_types)
        return None

    def get_member(self, name: str, allow_missing=False) -> tp.Optional[HKXMember]:
        """Return first and (as enforced) only member of this node type with the given `name`."""
        hits = [member for member in self.members if member.name == name]
        if len(hits) > 1:
            raise KeyError(f"Multiple members of HKX type {self.name} with name: {name}")
        elif not hits:
            if allow_missing:
                return None
            raise KeyError(f"No members of HKX type {self.name} with name: {name}")
        return hits[0]

    def get_member_type(self, name: str, hkx_types: HKXTypeList) -> HKXType:
        member = self.get_member(name)
        return member.get_type(hkx_types)

    def get_member_type_name(self, name: str, hkx_types: HKXTypeList) -> str:
        member = self.get_member(name)
        return member.get_type_name(hkx_types)

    def __getitem__(self, member_name: str) -> HKXMember:
        return self.get_member(member_name)

    def copy(self) -> HKXType:
        return copy.deepcopy(self)

    @_cache_type("base_type")
    def get_base_type(self, hkx_type_list: HKXTypeList) -> HKXType:
        """A few types (those without the `SubType` flag) are bare wrappers around a base type. This recursively
        searches for the base type."""
        if self.tag_format_flags & TagFormatFlags.SubType:
            return self
        return self.get_parent_type(hkx_type_list).get_base_type(hkx_type_list)

    @_cache_type("base_pointer_type")
    def get_base_pointer_type(self, hkx_type_list: HKXTypeList) -> HKXType:
        """Get pointer type of base type. NOT the same thing as from `get_pointer_base_type`."""
        return self.get_base_type(hkx_type_list).get_pointer_type(hkx_type_list)

    def get_all_members(self, hkx_types: HKXTypeList) -> tp.Iterator[HKXMember]:
        """Iterate over all members, including members of parent types."""
        if self.parent_type_index:
            for member in self.get_parent_type(hkx_types).get_all_members(hkx_types):
                yield member

        for member in self.members:
            yield member

    def get_type_hierarchy(self, hkx_types: HKXTypeList) -> list[HKXType]:
        hierarchy = [self]
        parent = self.get_parent_type(hkx_types)
        while parent is not None:
            hierarchy.append(parent)
            parent = parent.get_parent_type(hkx_types)
        return list(reversed(hierarchy))

    @property
    def tuple_size(self) -> int:
        return self.tag_type_flags >> 8

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def get_xml_string(self, hkx_types: HKXTypeList, indent=0) -> str:
        ind = " " * indent
        type_line = "<type"
        if self.abstract_value:
            type_line += f' abstractValue="{self.abstract_value}"'
        if self.alignment:
            type_line += f' alignment="{self.alignment}"'
        if self.byte_size:
            type_line += f' byteSize="{self.byte_size}"'
        if self.tag_format_flags:
            type_line += f' flags="{self.tag_format_flags}"'
        if self.hsh:
            type_line += f' hash="{self.hsh}"'
        type_line += f' id="{hkx_types.index(self)}"'
        type_line += f' name="{self.name}"'
        if self.pointer_type_index:
            type_line += f' pointer="{self.pointer_type_index}"'
        if self.parent_type_index:
            type_line += f' parent="{self.parent_type_index}"'
        if self.tag_type_flags:
            type_line += f' subTypeFlags="{self.tag_type_flags}"'
        if self.version:
            type_line += f' version="{self.version}"'
        if not (self.templates or self.members or self.interfaces):
            return ind + type_line + " />"
        lines = [type_line + ">"]
        for t in self.templates:
            if t.type_index:
                lines.append(f'    <template name="{t.name}" value="{t.type_index}" />')
            else:  # value template
                lines.append(f'    <template name="{t.name}" value="{t.value}" />')
        for m in self.members:
            lines.append(
                f'    <member flags="{m.flags}" name="{m.name}" offset="{m.offset}" type="{m.type_index}" />'
            )
        for i in self.interfaces:
            lines.append(f'    <interface flags="{i.flags}" type="{i.type_index}" />')
        lines.append("</type>")
        return "\n".join(ind + line for line in lines)

    def get_full_string(self, hkx_types: HKXTypeList) -> str:
        tag_flags_b = f"{self.tag_type_flags:032b}"
        tag_flags = "_".join([tag_flags_b[0:8], tag_flags_b[8:16], tag_flags_b[16:24], tag_flags_b[24:32]])
        all_members = self.get_all_members(hkx_types)
        if all_members:
            max_name_length = max(len(m.name) for m in self.members)
            member_lines = []
            local_members = self.members
            for member in all_members:
                member_type_name = member.get_type_name(hkx_types)
                if member in local_members:
                    member_lines.append(
                        f"{' ' * 12}{member.name:<{max_name_length}} ({member.offset}): {member_type_name}"
                    )
                else:
                    member_lines.append(
                        f"{' ' * 10}* {member.name:<{max_name_length}} ({member.offset}): {member_type_name}"
                    )

            members = "{\n" + "\n".join(member_lines) + "           }"
        else:
            members = "{}"
        return (
            f"Type({self.name}):\n"
            f"            parent = {self.get_parent_type(hkx_types)}\n"
            f"           pointer = {self.get_pointer_type(hkx_types)}\n"
            f"  tag_format_flags = {self.tag_format_flags:08b} ({self.tag_format_flags})\n"
            f"    tag_type_flags = {tag_flags} ({self.tag_type_flags})\n"
            f"           version = {self.version}\n"
            f"         byte_size = {self.byte_size}\n"
            f"         alignment = {self.alignment}\n"
            f"    abstract_value = {self.abstract_value}\n"
            f"               hsh = {self.hsh}\n"
            f"         templates = {self.templates}\n"
            f"           members = {members}\n"
            f"        interfaces = {self.interfaces}\n"
            f"               tag = {self.tag}\n"
        )


class HKXTypeList:
    """Wrapper for a list of `HKXType` instances that supports name-based indexing and manages type conversion.

    HKX files use one-indexing for types, so in order to emulate that here, the first type in the list is always `None`
    and should never be used or accessed.
    """

    # Set of type names that are not unique (in my full 2015 database, at least).
    GENERIC_TYPE_NAMES = {
        "hkcdStaticTreeDynamicStorage",
        "hkcdStaticTreeTree",
        "hkArray",
        "hkEnum",
        "hkRefPtr",
        "T[N]",
        "T*",
    }

    _hkx_types: list[HKXType]

    def __init__(self, hkx_type_list: list[HKXType] = ()):
        # noinspection PyTypeChecker
        self._hkx_types = [None] + list(hkx_type_list)
        # Map non-generic type names to their indices for faster retrieval.
        self._cached_type_indices = {}  # type: dict[str, int]
        for i, hkx_type in enumerate(self._hkx_types[1:]):
            if hkx_type.name_without_colons not in self.GENERIC_TYPE_NAMES:
                self._cached_type_indices[hkx_type.name_without_colons] = i + 1

    def __getitem__(self, index_or_name: tp.Union[int, str]):
        if isinstance(index_or_name, str):
            return self.get_type(index_or_name, allow_missing=False)
        elif isinstance(index_or_name, int) and index_or_name == 0:
            raise ValueError(f"Cannot get index 0 of `HKXTypeList`. Use a one-indexed syntax.")
        return self._hkx_types[index_or_name]

    def __iter__(self) -> tp.Iterator[HKXType]:
        return iter(self._hkx_types[1:])

    def __len__(self) -> int:
        return len(self._hkx_types)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self._hkx_types)})"

    def index(self, hkx_type: HKXType) -> int:
        """Get index of HKX type. Note that it is one-indexed, like HKX files."""
        return self._hkx_types.index(hkx_type)

    def append(self, hkx_type: HKXType):
        self._hkx_types.append(hkx_type)
        if hkx_type.name_without_colons not in self.GENERIC_TYPE_NAMES:
            self._cached_type_indices[hkx_type.name_without_colons] = len(self._hkx_types) - 1

    def extend(self, hkx_types: list[HKXType]):
        start_index = len(self._hkx_types)
        self._hkx_types.extend(hkx_types)
        for i, new_type in enumerate(hkx_types):
            if new_type.name_without_colons not in self.GENERIC_TYPE_NAMES:
                self._cached_type_indices[new_type.name_without_colons] = start_index + i

    def remove(self, hkx_type: HKXType):
        """Use `NodeTypeReindexer` to fix type/node type indices after removing any types.

        Name indices in `self._cached_type_indices` are updated here automatically.
        """
        removed_type_index = self.index(hkx_type)
        self._hkx_types.remove(hkx_type)
        if hkx_type.name_without_colons not in self.GENERIC_TYPE_NAMES:
            self._cached_type_indices.pop(hkx_type.name_without_colons)  # should always be present
        for type_name, type_index in self._cached_type_indices.items():
            if type_index > removed_type_index:
                self._cached_type_indices[type_name] = type_index - 1

    def shallow_copy(self) -> HKXTypeList:
        return HKXTypeList(self._hkx_types[1:])

    def get_type(self, name: str, allow_missing=True) -> tp.Optional[HKXType]:
        """Retrieve HKX type with given `name`. The type's name must be unique (i.e. not in `GENERIC_TYPE_NAMES`), or a
        `TypeError` will be raised.

        Colons are removed from the name before lookup.

        If `allow_missing=True`, `None` is returned if the name is missing.
        """
        name = name.replace("::", "")
        try:
            return self._hkx_types[self._cached_type_indices[name]]
        except KeyError:
            if name in self.GENERIC_TYPE_NAMES:
                raise TypeError(f"Cannot access generic HKX type \"{name}\" by name.")
            if allow_missing:
                return None
            raise KeyError(f"No HKX type named \"{name}\".")

    def get_type_index(self, type_or_name: tp.Union[HKXType, str]) -> int:
        """Get index of given type (or unique type with given name).

        Index returned will match the one-indexing system used by HKX files - that is, this will never return 0.
        """
        if isinstance(type_or_name, str):
            try:
                return self._cached_type_indices[type_or_name]
            except KeyError:
                if type_or_name in self.GENERIC_TYPE_NAMES:
                    raise TypeError(f"Cannot access generic HKX type \"{type_or_name}\" by name.")
                raise KeyError(f"No HKX type named \"{type_or_name}\".")
        return self._hkx_types.index(type_or_name)

    def get_primitive_array(self, primitive_type_name: str) -> tp.Optional[HKXType]:
        """Find a `hkArray` type that points to the given `primitive_type_name`.

        Useful for adding new types, which often use existing array types (e.g. for `hkUint16`). Multiple arrays may
        already exist; this returns the first (shouldn't be an issue).

        Returns `None` if no type is found (unlikely for a standard database), in which case you should create it.
        """
        for hkx_type in self._hkx_types[1:]:
            if hkx_type.name == "hkArray" and hkx_type.get_pointer_name(self) == primitive_type_name:
                return hkx_type
        return None

    def get_xml(self) -> str:
        xml_types = "\n".join(
            hkx_type.get_xml_string(self, indent=4) for i, hkx_type in enumerate(self._hkx_types[1:])
        )
        return '<?xml version="1.0" encoding="utf-8"?>\n' + "<types>\n" + xml_types + "\n</types>\n"

    @staticmethod
    def resolve_version(version: str):
        version = str(version)
        if version in {"2015", "2016"}:
            if version != "2015":
                _LOGGER.warning(
                    f"{version} HKX node types were requested. Returning 2015 types (no known differences)."
                )
            return "2015"
        elif version in {"2014"}:
            return "2014"
        elif version in {"2011", "2012", "2013"}:
            if version != "2012":
                _LOGGER.warning(
                    f"{version} HKX node types were requested. Returning 2012 types (no known differences)."
                )
            return "2012"
        elif version in {"2010"}:
            return "2010"
        else:
            raise ValueError(f"HKX node type `version` must be a year between 2010-2016, not {repr(version)}.")

    @classmethod
    def load(cls, version: str, type_database_path: tp.Union[str, Path] = None) -> HKXTypeList:
        """Load `HKXTypeList` instance from `type_database_path` XML (defaults to bundled `Types2015.xml`, which has all
        2015 types seen thus far), then convert types if necessary for other requested versions.

        Supported versions right now, and their aliases (until further differences are identified):
            2015 (also 2016)
            2014
            2012 (also 2013)
            2010 (also 2011)
        """
        version = cls.resolve_version(version)

        if type_database_path is None:
            if version == "2015":
                type_database_path = Path(__file__).parent / "Types2015.xml"
            elif version == "2014":
                type_database_path = Path(__file__).parent / "Types2014.xml"
            elif version == "2010":
                type_database_path = Path(__file__).parent / "Types2010.xml"
            else:
                raise NotImplementedError(f"No type database for version {version} yet.")

        root_element = ElementTree.parse(str(type_database_path))
        type_elements = list(root_element.findall("type"))
        type_elements.sort(key=lambda x: int(x.get("id")))

        hkx_types = []

        for type_element in type_elements:

            hkx_type = HKXType(
                name=_get_element_attrib(type_element, "name", ""),
                parent_type_index=_get_element_attrib(type_element, "parent", 0, int),
                tag_format_flags=_get_element_attrib(type_element, "flags", 0, int),
                tag_type_flags=_get_element_attrib(type_element, "subTypeFlags", 0, int),
                pointer_type_index=_get_element_attrib(type_element, "pointer", 0, int),
                version=_get_element_attrib(type_element, "version", None, int),
                byte_size=_get_element_attrib(type_element, "byteSize", 0, int),
                alignment=_get_element_attrib(type_element, "alignment", 0, int),
                abstract_value=_get_element_attrib(type_element, "abstractValue", None, int),
                hsh=_get_element_attrib(type_element, "hash", None, int),
            )

            for template_element in type_element.findall("template"):
                template_name = _get_element_attrib(template_element, "name", "v")
                template_value = _get_element_attrib(template_element, "value", 0, int)
                if template_name[0] == "t":
                    template = HKXTemplate(template_name, type_index=template_value)
                elif template_name[0] == "v":
                    template = HKXTemplate(template_name, value=template_value)
                else:
                    raise TypeError(f"Template in XML does not have 't' or 'v' type: {template_name}")
                hkx_type.templates.append(template)

            for member_element in type_element.findall("member"):
                member = HKXMember(
                    name=_get_element_attrib(member_element, "name", ""),
                    flags=_get_element_attrib(member_element, "flags", 0, int),
                    offset=_get_element_attrib(member_element, "offset", 0, int),
                    type_index=_get_element_attrib(member_element, "type", 0, int),
                )
                hkx_type.members.append(member)

            for interface_element in type_element.findall("interface"):
                interface = HKXInterface(
                    type_index=_get_element_attrib(interface_element, "type", 0, int),
                    flags=_get_element_attrib(interface_element, "flags", 0, int),
                )
                hkx_type.interfaces.append(interface)

            hkx_types.append(hkx_type)

        hkx_types = cls(hkx_types)

        return hkx_types

    # noinspection PyTypeChecker
    def get_deferenced_primitives(self) -> list[HKXType]:
        """Return a list of 'primitive' HKX types, with all type indices set to the actual type. Should be converted
        to references again once inserted into your list.
        """
        primitives = [
            hkx_type for hkx_type in self._hkx_types[1:]
            if (not hkx_type.tag_format_flags & TagFormatFlags.SubType and hkx_type.name not in {"hkEnum", "hkFlags"})
            or (not hkx_type.name.startswith("hk") and hkx_type.name not in {"T*", "T[N]"})
            or hkx_type.name in {
                "hkContainerHeapAllocator",
                "hkStringPtr",
                "hkBool",
                # "hkRefVariant",
                "hkHalf16",
                "hkUFloat8",
                "hkQuaternionf",
                "hkVector4f",
                "hkMatrix4f",
                "hkQsTransformf",
                "hkTransformf",
                "hkRotationImpl",
                "hkMatrix3Impl",
                # "hkViewPtr",
               }
        ]

        for p in primitives:
            p.parent_type_index = self[p.parent_type_index] if p.parent_type_index else None
            p.pointer_type_index = self[p.pointer_type_index] if p.pointer_type_index else None
            for t in p.templates:
                if t.name[0] == "t":
                    t.type_index = self[t.type_index]
            for m in p.members:
                m.type_index = self[m.type_index]
            for i in p.interfaces:
                i.type_index = self[i.type_index]

        return primitives

    @classmethod
    def load_2015(cls, type_database_path: tp.Union[str, Path] = None) -> HKXTypeList:
        return cls.load("2015", type_database_path)

    @classmethod
    def load_2012(cls, type_database_path: tp.Union[str, Path] = None) -> HKXTypeList:
        return cls.load("2012", type_database_path)

    @classmethod
    def load_2010(cls, type_database_path: tp.Union[str, Path] = None) -> HKXTypeList:
        return cls.load("2010", type_database_path)


class HKXTypeAttribute(abc.ABC):
    name: str
    type_index: tp.Union[int, HKXType]

    def __init__(self, name: str, type_index: int):
        self.name = name
        self.type_index = type_index

    def get_type(self, hkx_types: HKXTypeList) -> HKXType:
        return hkx_types[self.type_index]

    def get_type_name(self, hkx_types: HKXTypeList) -> str:
        return hkx_types[self.type_index].name

    def get_base_type(self, hkx_types: HKXTypeList) -> HKXType:
        return hkx_types[self.type_index].get_base_type(hkx_types)

    def reindex(self, old_hkx_types: HKXTypeList, new_hkx_types: HKXTypeList):
        if self.type_index:
            hkx_type = old_hkx_types[self.type_index]
            self.type_index = new_hkx_types.get_type_index(hkx_type)


class HKXInterface(HKXTypeAttribute):
    flags: int

    def __init__(self, type_index: int, flags: int):
        super().__init__("Interface", type_index)
        self.flags = flags


class HKXMember(HKXTypeAttribute):
    flags: int
    offset: int
    hkx_enum: tp.Optional[HKXEnum]

    def __init__(
        self,
        name: str,
        flags: int,
        offset: int,
        type_index: int,
        hkx_enum: tp.Optional[HKXEnum] = None,
    ):
        super().__init__(name, type_index)
        self.flags = flags
        self.offset = offset
        self.hkx_enum = hkx_enum


class HKXTemplate(HKXTypeAttribute):
    """Can be a "t" (type) or "v" (value) template. `type_index` is only available for "t" templates, and `value` is
    only available to "v" templates, to ensure you don't make an incorrect assumption about the template."""

    type_index: tp.Optional[int]
    value: tp.Optional[int]  # could be a real value or a `HKXType` index

    def __init__(self, name: str, *, type_index: int = None, value: int = None):
        if name[0] == "t" and (value is not None or type_index is None):
            raise TypeError("Template of 't' type requires `type_index` argument, not `value` argument.")
        elif name[0] == "v" and (value is None or type_index is not None):
            raise TypeError("Template of 'v' type requires `value` argument, not `type_index` argument.")
        elif name[0] not in {"t", "v"}:
            raise TypeError(f"`HKXTemplate` name must start with 't' or 'v': {name}")
        super().__init__(name, type_index)
        self.value = value

    def get_type(self, hkx_types: HKXTypeList):
        if self.type_index is None:
            raise ValueError("Cannot get type of 'v' (value) template.")
        return hkx_types[self.type_index]

    def __repr__(self) -> str:
        if self.name[0] == "v":
            return f"HKXTemplate(name={repr(self.name)}, value={self.value})"
        return f"HKXTemplate(name={repr(self.name)}, type_index={self.type_index})"


class HKXEnum(dict[str, int]):

    def __init__(self, name: str, items: tp.Sequence[tuple[str, int]]):
        super().__init__()
        self.name = name
        for item in items:
            self[item[0]] = item[1]

    def __repr__(self):
        items = ", ".join(f"{k}={v}" for k, v in self.items())
        return f"{self.name}({items})"


def _get_element_attrib(element: ElementTree.Element, name: str, default=None, method=None) -> tp.Any:
    try:
        attrib_value = element.attrib[name]
    except KeyError:
        return default
    return method(attrib_value) if method is not None else attrib_value


def _is_property_bag_type(hkx_type: HKXType) -> bool:
    return (
        hkx_type.name in {
            "hkDefaultPropertyBag",
            "hkTuple",
            "hkPropertyId",
            "hkPtrAndInt",
            "hkPropertyDesc",
        } or hkx_type.name.startswith("hkHash")
    )


DEPRECATED_TYPES = {
    "hkSweptTransform",
    "hkpWorldCinfoTreeUpdateType",
}


def convert_types(hkx_types: HKXTypeList, match_types: HKXTypeList):
    """Modifies all non-generic type attributes in `hkx_types` to match their corresponding types in `match_types`,
    and modifies all generic types' pointer sizes, etc.

    Additional version-specific modification may be needed prior to this, e.g. renaming `hkpProperty` in 2010 to
    `hkSimpleProperty` in 2015+, and renaming "referenceCount" member to "refCount".
    """
    array_exemplar = [ht for ht in match_types if ht.name == "hkArray"][0]
    pointer_examplar = match_types["hkStringPtr"]

    new_pointer_size = pointer_examplar.byte_size
    new_pointer_alignment = pointer_examplar.alignment
    new_array_size = array_exemplar.byte_size
    new_array_alignment = array_exemplar.byte_size

    for hkx_type in hkx_types:

        if hkx_type.name == "hkArray":
            hkx_type.byte_size = new_array_size
            hkx_type.alignment = new_array_alignment
        elif hkx_type.name in {"T*", "hkRefPtr", "T[N]"}:
            hkx_type.byte_size = new_pointer_size
            hkx_type.alignment = new_pointer_alignment
        elif hkx_type.name == "hkEnum":
            pass  # no need to change anything
        elif hkx_type.name in HKXTypeList.GENERIC_TYPE_NAMES:
            raise NotImplementedError(f"Cannot support conversion of generic type: {hkx_type.name}")
        else:
            try:
                match_type = match_types[hkx_type.name]
            except KeyError:
                if hkx_type.name_without_colons not in DEPRECATED_TYPES:
                    _LOGGER.error(f"Encountered an error while converting type: {hkx_type.name}")
                    raise
                continue  # type deprecated
            for attr in ("byte_size", "alignment", "version", "abstract_value", "hsh"):
                # All things that may have changed in the destination version.
                setattr(hkx_type, attr, getattr(match_type, attr))

            # Update members. Any deprecated members will be naturally dropped; new members will be created and have all
            # their new types recursively added.

            current_members = {m.name: m for m in hkx_type.members}  # type: dict[str, HKXMember]
            hkx_type.members = []
            for i, member_name in enumerate(m.name for m in match_type.members):
                match_member = match_type.get_member(member_name)
                match_member_type = match_member.get_type(match_types)
                if member_name not in current_members:
                    # Add new member type and assign it to new member.
                    try:
                        member_type_index = hkx_types.get_type_index(match_member_type.name)
                    except KeyError:
                        # Member's type is generic or absent.
                        TypeAdder(match_types, hkx_types).add(match_member_type)
                        member_type_index = hkx_types.index(match_member_type)
                    member = HKXMember(
                        name=member_name,
                        flags=match_member.flags,
                        offset=match_member.offset,
                        type_index=member_type_index,
                        hkx_enum=match_member.hkx_enum,
                    )
                else:
                    # Keep current member and modify it. (Existing type index is still correct.)
                    member = current_members[member_name]
                    member.flags = match_member.flags
                    member.offset = match_member.offset
                    # TODO: Do I need to update `hkx_enum`?

                    # Update member type's hash. TODO: May not be a sufficiently deep search for hashed types.
                    if match_member_type.hsh:
                        current_member_type = member.get_type(hkx_types)
                        current_member_type.hsh = match_member_type.hsh
                        if match_member_type.tag_data_type == TagDataType.Array:
                            match_member_array_type = match_member_type.get_pointer_type(match_types)
                            if match_member_array_type.hsh:
                                current_member_array_type = current_member_type.get_pointer_type(hkx_types)
                                current_member_array_type.hsh = match_member_array_type.hsh
                hkx_type.members.append(member)


class TypeAdder:
    """Adds a given new `HKXType`, `new_type`, from a `source_types` `HKXTypeList` to a `dest_types` `HKXTypeList`.

    Iterates through all child types of `new_type` and (a) uses `source_types` to add types that are missing or generic
    or (b) redirects non-generic types to types that already exist in `dest_types`.

    `source_types` and `new_type` should be throwaway instances, as `new_type` will be modified in-place as it is
    inserted into `dest_types`.
    """

    _DEBUG_PRINT = False

    def __init__(self, source_hkx_types: HKXTypeList, dest_hkx_types: HKXTypeList):
        self.dest_types = dest_hkx_types
        self.source_types = source_hkx_types

    def add(self, new_type: HKXType, look_for_array_primitives=()) -> int:
        """If you pass any strings in `look_for_array_primitives`, an existing `hkArray` type containing any of those
        primitives will be searched for first before creating a new one."""
        self._array_primitives = look_for_array_primitives
        old_size = len(self.dest_types)
        if new_type.name not in HKXTypeList.GENERIC_TYPE_NAMES and new_type in self.dest_types:
            raise ValueError(f"Non-generic type {new_type.name} is already in destination types.")
        self.dest_types.append(new_type)
        self._scan_type(new_type)
        if self._DEBUG_PRINT:
            print(f"Added {len(self.dest_types) - old_size} new types with `TypeAdder`.")
        return self.dest_types.index(new_type)

    def _scan_type(self, source_type: HKXType, indent=0):
        ind = " " * indent
        if self._DEBUG_PRINT:
            print(f"{ind}Scanning type: {source_type.name}")

        for template in source_type.templates:
            self._scan_type_attribute(template, indent=indent + 4)

        if source_type.parent_type_index:

            parent_type = source_type.get_parent_type(self.source_types)

            if parent_type in self.dest_types:
                source_type.parent_type_index = self.dest_types.index(parent_type)
            elif parent_type.name in HKXTypeList.GENERIC_TYPE_NAMES:
                # Add and scan.
                if self._DEBUG_PRINT:
                    print(f"{ind}Adding generic type: {parent_type.name}")
                self.dest_types.append(parent_type)
                self._scan_type(parent_type, indent=indent + 4)
                source_type.parent_type_index = self.dest_types.index(parent_type)
            elif existing_parent_type := self.dest_types.get_type(parent_type.name):
                # Redirect to existing type.
                source_type.parent_type_index = self.dest_types.index(existing_parent_type)
            else:
                # Add and scan.
                if self._DEBUG_PRINT:
                    print(f"{ind}Adding new type: {parent_type.name}")
                self.dest_types.append(parent_type)
                self._scan_type(parent_type, indent=indent + 4)
                source_type.parent_type_index = self.dest_types.index(parent_type)

        if source_type.pointer_type_index:

            pointer_type = source_type.get_pointer_type(self.source_types)

            if pointer_type in self.dest_types:
                source_type.pointer_type_index = self.dest_types.index(pointer_type)
            elif pointer_type.name in HKXTypeList.GENERIC_TYPE_NAMES:
                # Add and scan.
                if self._DEBUG_PRINT:
                    print(f"{ind}Adding generic type: {pointer_type.name}")
                self.dest_types.append(pointer_type)
                self._scan_type(pointer_type, indent=indent + 4)
                source_type.pointer_type_index = self.dest_types.index(pointer_type)
            elif existing_pointer_type := self.dest_types.get_type(pointer_type.name):
                # Redirect to existing type.
                source_type.pointer_type_index = self.dest_types.index(existing_pointer_type)
            else:
                # Add and scan.
                if self._DEBUG_PRINT:
                    print(f"{ind}Adding new type: {pointer_type.name}")
                self.dest_types.append(pointer_type)
                self._scan_type(pointer_type, indent=indent + 4)
                source_type.pointer_type_index = self.dest_types.index(pointer_type)

        for member in source_type.members:
            self._scan_type_attribute(member, indent=indent + 4)

        for interface in source_type.interfaces:
            self._scan_type_attribute(interface, indent=indent + 4)

    def _scan_type_attribute(self, attribute: HKXTypeAttribute, indent: int):
        ind = " " * indent
        if self._DEBUG_PRINT:
            print(f"{ind}Scanning attribute: {attribute.name}")
        if not attribute.type_index:
            return
        attribute_type = attribute.get_type(self.source_types)

        if attribute_type in self.dest_types:
            attribute.type_index = self.dest_types.index(attribute_type)
        elif attribute_type.name in HKXTypeList.GENERIC_TYPE_NAMES:
            if attribute_type.name == "hkArray":
                array_element_type_name = attribute_type.get_pointer_name(self.source_types)
                if array_element_type_name in self._array_primitives:
                    # Check for existing array of primitives first.
                    existing_array_type = self.dest_types.get_primitive_array(array_element_type_name)
                    if existing_array_type is not None:
                        if self._DEBUG_PRINT:
                            print(f"{ind}Using existing `hkArray` type ({array_element_type_name}).")
                        attribute.type_index = self.dest_types.index(existing_array_type)
                        return
            # Add and scan generic type.
            if self._DEBUG_PRINT:
                print(f"{ind}Adding generic type: {attribute_type.name}")
            self.dest_types.append(attribute_type)
            self._scan_type(attribute_type, indent=indent + 4)
            attribute.type_index = self.dest_types.index(attribute_type)
        elif existing_type := self.dest_types.get_type(attribute_type.name):
            # Redirect to existing type.
            attribute.type_index = self.dest_types.index(existing_type)
        else:
            # Add and scan new type.
            if self._DEBUG_PRINT:
                print(f"{ind}Adding new type: {attribute_type.name}")
            self.dest_types.append(attribute_type)
            self._scan_type(attribute_type, indent=indent + 4)
            attribute.type_index = self.dest_types.index(attribute_type)
