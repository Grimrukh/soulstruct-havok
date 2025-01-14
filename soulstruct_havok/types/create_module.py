from __future__ import annotations

import inspect
from pathlib import Path

from soulstruct.utilities.binary import BinaryReader

from soulstruct_havok.enums import TagDataType
from soulstruct_havok.exceptions import HavokTypeError, TypeNotDefinedError, VersionModuleError
from soulstruct_havok.types.info import TypeInfo, HAVOK_TYPE_PREFIXES


def create_module_from_files(version: str, *file_paths: str | Path, is_tagfile=True, module_path: Path = None):
    """Create an actual Python module with a real class hierarchy that fully captures Havok types."""
    if not file_paths:
        raise ValueError("At least one file path must be given to create Havok types module.")

    if module_path is None:
        module_path = Path(__file__).parent / f"hk{version}.py"

    module_str = f"\"\"\"Auto-generated types for Havok {version}.\n\nGenerated from files:"
    for file_path in file_paths:
        module_str += f"\n    {file_path.name}"
    module_str += (
        "\n"
        "\"\"\"\n"
        "from __future__ import annotations\n"
        "\n"
        "from soulstruct_havok.enums import TagDataType, MemberFlags\n"
        "from .core import *\n"
    )

    # TODO: Detect if file is tag/pack, then open it, but extract `TypeInfo` list only. (Don't need any generic types.)
    #  Things to consider:
    #   - Only tagfiles have (and use) the "tag_format_flags" type attribute; it just indicates which other type
    #     attributes are present in the tagfile (as varints). These will need to be generated accurately if/when
    #     converting packfiles to tagfiles.

    # Next, we iterate over our types list, but we don't generate them in the random order in the XML. Instead, we use
    # `tag_type_flags` to load more primitive types first, then load classes afterwards.

    type_info_dict = {}  # type: dict[str, TypeInfo]
    from soulstruct_havok.packfile.unpacker import PackFileUnpacker
    from soulstruct_havok.tagfile.unpacker import TagFileUnpacker
    for file_path in file_paths:
        # TODO: Detect tagfile vs. packfile automatically.
        file_reader = BinaryReader(file_path)
        if is_tagfile:
            unpacker = TagFileUnpacker()
            unpacker.unpack(file_reader, compendium=None, types_only=True)
            raw_type_infos = unpacker.hk_type_infos[1:]  # skip `None` pad at index 0
        else:
            unpacker = PackFileUnpacker()
            unpacker.unpack(file_reader, types_only=True)
            if not unpacker.hk_type_infos:
                raise HavokTypeError(f"No Havok types defined in source packfile: {file_path}")
            raw_type_infos = unpacker.hk_type_infos[1:]  # skip `None` pad at index 0
        type_info_names = []
        for type_info in raw_type_infos:
            if type_info.name in TypeInfo.GENERIC_TYPE_NAMES:
                continue
            if type_info.name in type_info_names:
                raise ValueError(f"Repeated non-generic Python type name `{type_info.name}` in file {file_path}.")
            type_info_names.append(type_info.name)
            type_info_dict[type_info.py_name] = type_info

    # for t in type_info_dict:
    #     print(t)

    defined_py_names = ["hk"]

    if not is_tagfile:
        # Packfile base types must exist already and be imported.
        if version == "2010":
            from soulstruct_havok.types import hk2010 as base_module
            module_str += f"from soulstruct_havok.types.hk2010_base import *\n"
        elif version == "2014":
            from soulstruct_havok.types import hk2014 as base_module
            module_str += f"from soulstruct_havok.types.hk2014_base import *\n"
        else:
            raise VersionModuleError(
                f"No packfile `base` Havok types module for Havok version {version}. "
                f"Cannot generate full types module."
            )
        # Import all base classes from base module.
        base_types = {
            name: hk_type
            for name, hk_type in inspect.getmembers(
                base_module, lambda x: inspect.isclass(x) and issubclass(x, base_module.hk)
            )
        }
        # Indicate that these names are already defined.
        for base_type_name in base_types:
            defined_py_names.append(base_type_name)
        # TODO: Iterate over all members of all types and create/assign base `TypeInfo`s.
        #  Actually, maybe better to do this in `PackfileTypeUnpacker`, since arrays/structs/etc. of base types also
        #  need to be created dynamically and converted to `TypeInfo`s, and it may as well be done there where the rest
        #  of the type unpacking is being done.

    def define(_name: str, optional=False) -> str:
        if _name not in type_info_dict and optional:
            return ""
        _type_info = type_info_dict[_name]
        _py_name = _type_info.py_name
        if _py_name in defined_py_names:
            print(f"ALREADY DEFINED: {_py_name}")
            return ""
        class_str = "\n\n" + _type_info.get_class_py_def(defined_py_names)
        defined_py_names.append(_py_name)
        print(f"    BUILT: {_py_name}")
        return class_str

    def define_all(_names: list[str]):
        """Keep iterating over filtered type list, attempting to define them, until they can all be defined."""
        _names = [_name for _name in _names if _name not in defined_py_names]
        if not _names:
            return ""
        class_strs = []
        while True:
            new_definitions = []
            exceptions = []
            for _name in _names:
                _type_info = type_info_dict[_name]
                try:
                    class_str = define(_name)
                    class_strs.append(class_str)
                    new_definitions.append(_name)
                except TypeNotDefinedError as ex:
                    exceptions.append(f"{_name}: {str(ex)}")
                    continue  # try next type
            if not new_definitions:
                # Could not define anything on this pass. Raise all exceptions from this pass.
                ex_str = "\n    ".join(exceptions)
                print(f"Defined py names: {defined_py_names}")
                raise HavokTypeError(
                    f"Could not define any types remaining in list: {[_name for _name in _names]}.\n\n"
                    f"Last errors:\n    {ex_str}"
                )
            for _name in new_definitions:
                _names.remove(_name)
            if not _names:
                break
        return "".join(class_strs)

    print("\n--- Defining Invalid Types ---\n")

    module_str += f"\n\n# --- Invalid Types --- #\n"
    module_str += define_all([
        name for name, type_info in type_info_dict.items()
        if type_info.tag_data_type == TagDataType.Invalid
    ])

    print("\n--- Defining Primitive Types ---\n")

    module_str += f"\n\n# --- Primitive Types --- #\n"
    module_str += define_all([
        name for name, type_info in type_info_dict.items()
        if not any(type_info.name.startswith(s) for s in HAVOK_TYPE_PREFIXES)
    ])

    print("\n--- Defining Havok Struct Types ---\n")

    # Basic 'Struct' types.
    module_str += f"\n\n# --- Havok Struct Types --- #\n"
    module_str += define_all([
        name for name, type_info in type_info_dict.items()
        if type_info.get_parent_value("tag_data_type") == TagDataType.Struct
    ])
    module_str += define("hkQsTransformf", optional=True)  # bundles other structs together
    module_str += define("hkQsTransform", optional=True)  # alias for above

    print("\n--- Defining Havok Wrappers ---\n")

    # NOTE: It's tempting to simply assign these to their wrapped types, rather than subclassing them, but they
    # annoyingly can sometimes have unique `hsh` members.

    # Other shallow wrappers.
    module_str += define("hkUint32", optional=True)  # will be missing from packfiles
    module_str += define("hkHandle", optional=True)

    module_str += f"\n\n# --- Havok Wrappers --- #\n"
    module_str += define_all([
        name for name, type_info in type_info_dict.items()
        if type_info.tag_type_flags is None
    ])

    print("\n--- Defining Havok Core Types ---\n")

    # Core classes.
    module_str += f"\n\n# --- Havok Core Types --- #\n"
    module_str += define("hkBaseObject")
    # `hkReferencedObject` is left to its own devices, as in 2016 onwards, it has other `hkPropertyBag` dependencies.

    # Everything else.
    module_str += define_all([
        name for name, type_info in type_info_dict.items()
        if name not in defined_py_names
    ])

    with module_path.open("w") as f:
        f.write(module_str)


def create_2010_module():
    create_module_from_files(
        "2010",
        Path("../../tests/resources/PTDE/c2240/c2240.hkx"),
        is_tagfile=False,
        module_path=Path(__file__).parent / f"hk2010.py"
    )


def create_2014_module():
    """TODO: Only DS3 ragdoll HKX files seem to have types. This makes animation and cloth classes difficult."""
    create_module_from_files(
        "2014",
        Path("../../tests/resources/DS3/c1430/c1430.HKX"),
        # Path("../../tests/resources/DS3/c1430/c1430_c.hkx"),
        # Path("../../tests/resources/DS3/c1240/a00_3000.hkx"),
        is_tagfile=False,
        module_path=Path(__file__).parent / f"hk2014_new.py"
    )


def create_2015_module():
    create_module_from_files(
        "2015",
        Path("../../tests/resources/DSR/c2240/Skeleton.HKX"),
        Path("../../tests/resources/DSR/c2240/c2240.hkx"),
        Path("../../tests/resources/DSR/c2240/a00_3000.hkx"),
        is_tagfile=True,
        module_path=Path(__file__).parent / f"hk2015.py"
    )


def create_2018_module():
    create_module_from_files(
        "2018",
        Path(r"C:\Dark Souls\c2180-anibnd-dcx\GR\data\INTERROOT_ps4\chr\c2180\hkx\skeleton.hkx"),
        Path(r"C:\Dark Souls\c2180-chrbnd-dcx\GR\data\INTERROOT_ps4\chr\c2180\c2180_c.hkx"),
        Path(r"C:\Dark Souls\c2180-chrbnd-dcx\GR\data\INTERROOT_ps4\chr\c2180\c2180.hkx"),
        is_tagfile=True,
        module_path=Path(__file__).parent / f"hk2018.py"
    )


if __name__ == '__main__':
    # create_2010_module()
    create_2014_module()
    # create_2015_module()
    # create_2018_module()
