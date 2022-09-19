import inspect
import typing as tp
from pathlib import Path
from soulstruct_havok.types.core import hk, TemplateType


def main():
    from soulstruct_havok.types import hk2018_old, core
    new_submodule = Path("hk2018")

    imports = [
        "from __future__ import annotations",
        "",
        "from soulstruct_havok.types.core import *",
        "from soulstruct_havok.enums import *",
        "from .core import *",
    ]

    init_imports = []

    for cls_name, cls in vars(hk2018_old).items():
        if inspect.isclass(cls) and cls.__module__ == "soulstruct_havok.types.hk2018_old":
            new_file = new_submodule / f"{cls_name}.py"
            source = inspect.getsource(cls)
            init_imports.append(cls_name)

            base_names = list(vars(core))  # + list(vars(base))

            imported_types, view_types = get_imported_types(cls, base_names)

            if view_types:
                lines = imports[:2] + ["import typing as tp", ""] + imports[2:]
            else:
                lines = imports.copy()
            lines += [f"from .{t} import {t}" for t in imported_types]
            if view_types:
                lines += ["", "if tp.TYPE_CHECKING:"] + [f"    from .{t} import {t}" for t in view_types]
            lines += [""] * 3
            new_file.write_text("\n".join(lines) + source)

    init_file = new_submodule / "__init__.py"
    init_file.write_text(
        "from .core import *\n\n"
        + "\n".join(f"from .{t} import {t}" for t in sorted(init_imports)) + "\n"
    )


def get_imported_types(cls: tp.Type[hk], base_names: list[str]) -> tuple[list[str], list[str]]:
    imported_types = []
    view_types = []  # for TYPE_CHECKING only
    parent = cls.__bases__[0]
    if parent != object and parent.__name__ not in base_names:
        imported_types.append(parent.__name__)
    for member in cls.local_members:
        hk_type_name, is_view = get_hk_type(member.type.__name__)
        if hk_type_name not in base_names and hk_type_name not in imported_types and hk_type_name != cls.__name__:
            if is_view:
                view_types.append(hk_type_name)
            else:
                imported_types.append(hk_type_name)
    for interface in cls.get_interfaces():
        hk_type_name, _ = get_hk_type(interface.type.__name__)
        if hk_type_name not in base_names and hk_type_name not in imported_types and hk_type_name != cls.__name__:
            imported_types.append(hk_type_name)
    for template in cls.get_templates():
        if isinstance(template, TemplateType):
            hk_type_name, _ = get_hk_type(template.type.__name__)
            if hk_type_name not in base_names and hk_type_name not in imported_types and hk_type_name != cls.__name__:
                imported_types.append(hk_type_name)

    return imported_types, view_types


WRAPPERS = (
    "hkArray", "Ptr", "hkEnum", "hkStruct", "hkFlags",
    "hkRelArray", "hkRefPtr", "hkRefVariant", "hkViewPtr", "hkFreeListArray"
)


def get_hk_type(type_name: str) -> tuple[str, bool]:
    while True:
        for wrapper in WRAPPERS:
            if type_name.startswith(wrapper + "["):
                if wrapper == "hkStruct":
                    type_name = type_name[len(wrapper) + 1:].split(", ")[0]
                    break
                else:
                    type_name = type_name[len(wrapper) + 1:-1]
                    if wrapper == "hkViewPtr":
                        return type_name, True
                    break
        else:
            break
    return type_name, False


if __name__ == '__main__':
    main()
