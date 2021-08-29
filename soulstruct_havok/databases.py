from __future__ import annotations

__all__ = ["create_2010_database", "create_2014_database"]

from pathlib import Path

from soulstruct.base.models.hkx import HKX
from soulstruct.base.models.hkx.converter import resize_pointers, resize_types, realign_types
from soulstruct.base.models.hkx.nodes import NodeTypeReindexer
from soulstruct.base.models.hkx.types import HKXTypeList, TypeAdder


def create_2010_database(ptde_chrbnd_hkx_path: Path) -> str:
    """Any CHRBND HKX from PTDE contains (almost) all the 2010 types.

    The only ones missing are special pointers that cannot be detected (hkRefPtr, hkRefVariant) and hkaAnimation
    subtypes that are only used in animation files (added from 2015 database).
    """
    types_2010 = HKX(ptde_chrbnd_hkx_path).hkx_types
    types_2015 = HKXTypeList.load_2015()  # used to set member flags and add a few missing types

    for t in types_2010:
        for template in t.templates:
            if template.name[0] == "t" and template.type_index == 0:
                template.type_index = types_2010.get_type_index("void")
        if t.members:
            try:
                first_2015_type = [t_ for t_ in types_2015 if t_.name_without_colons == t.name_without_colons][0]
            except IndexError:
                continue  # deprecated type
            for member in t.members:
                try:
                    member_2015 = first_2015_type[member.name]
                except KeyError:
                    continue  # deprecated member
                member.flags = member_2015.flags

    TypeAdder(types_2015, types_2010).add(types_2015["hkRefVariant"])

    ref_variant_index = types_2010.get_type_index("hkRefVariant")

    ref_variant_members = (
        ("hkRootLevelContainerNamedVariant", "variant"),
        ("hkxMaterial", "extraData"),
        ("hkaBoneAttachment", "attachment"),
        ("hkxMaterialTextureStage", "texture"),
        ("hkxAttribute", "value"),
        # ("hkMemoryResourceHandle", "variant"),  # TODO: Not in 2010 types yet.
    )
    old_member_types = []
    for hkx_type_name, member_name in ref_variant_members:
        hkx_type = types_2010[hkx_type_name]
        member = hkx_type[member_name]
        old_member_types.append(member.get_type(types_2010))
        member.type_index = ref_variant_index

    original_types_2010 = types_2010.shallow_copy()
    for old_type in old_member_types:
        types_2010.remove(old_type)
        print(f"Removed old member type: {old_type.name}")
    types_2010 = NodeTypeReindexer(original_types_2010, new_types=types_2010).reindex()

    new_type_names = (
        "hkaSplineCompressedAnimation",
        "hkaInterleavedUncompressedAnimation",
        "hkaQuantizedAnimation",
        "hkaDefaultAnimatedReferenceFrame",
    )

    array_primitives = ("hkInt8", "hkUint8", "hkInt16", "hkUint16", "hkInt32", "hkUint32")
    for t_name in new_type_names:
        TypeAdder(types_2015, types_2010).add(types_2015[t_name], look_for_array_primitives=array_primitives)

    resize_pointers(types_2010, pointer_size=4)
    realign_types(types_2010, 4, "hkRootLevelContainer::NamedVariant", "hkBaseObject", "hkArray")
    realign_types(types_2010, 8, "hkaAnimation")
    resize_types(types_2010, "hkArray")
    resize_types(types_2010, *new_type_names)

    return types_2010.get_xml()


def create_2014_database(bb_chrbnd_hkx_path: Path) -> str:
    """Same as above, but the imported extra 2015 animation classes don't need adjustment (8-byte pointer size).

    Source HXK can be from Bloodborne or DS3. The bundled database used Bloodborne; not sure if there are any subtle
    differences, but there shouldn't be, as they are both version "hk_2014-1.0-r1".
    """
    types_2014 = HKX(bb_chrbnd_hkx_path).hkx_types
    types_2015 = HKXTypeList.load_2015()

    for t in types_2014:
        # No templates with missing types in BB.
        if t.members:
            # Use 2015 member flags.
            try:
                first_2015_type = [t_ for t_ in types_2015 if t_.name_without_colons == t.name_without_colons][0]
            except IndexError:
                continue  # deprecated type
            for member in t.members:
                try:
                    member_2015 = first_2015_type[member.name]
                except KeyError:
                    continue  # deprecated member
                member.flags = member_2015.flags

    # TODO: There are plenty of members defined in BB (`hknp` physics system) that are not in the BB database, and
    #  cannot be found in DSR CHRBND HKX files. I could presumably guess all their flags manually based on their types,
    #  but let's find out if that's necessary first (these `hknp` types won't appear in skeleton/animation files).

    TypeAdder(types_2015, types_2014).add(types_2015["hkRefVariant"])

    ref_variant_index = types_2014.get_type_index("hkRefVariant")

    ref_variant_members = (
        ("hkRootLevelContainerNamedVariant", "variant"),
        ("hkxMaterial", "extraData"),
        ("hkaBoneAttachment", "attachment"),
        ("hkxMaterialTextureStage", "texture"),
        ("hkxAttribute", "value"),
        # ("hkMemoryResourceHandle", "variant"),  # TODO: Not in 2014 types yet.
    )
    old_member_types = []
    for hkx_type_name, member_name in ref_variant_members:
        hkx_type = types_2014[hkx_type_name]
        member = hkx_type[member_name]
        old_member_types.append(member.get_type(types_2014))
        member.type_index = ref_variant_index

    original_types_2014 = types_2014.shallow_copy()
    for old_type in old_member_types:
        types_2014.remove(old_type)
        print(f"Removed old member type: {old_type.name}")
    types_2014 = NodeTypeReindexer(original_types_2014, new_types=types_2014).reindex()

    new_type_names = (
        "hkaSplineCompressedAnimation",
        "hkaInterleavedUncompressedAnimation",
        "hkaQuantizedAnimation",
        "hkaDefaultAnimatedReferenceFrame",
    )

    array_primitives = ("hkInt8", "hkUint8", "hkInt16", "hkUint16", "hkInt32", "hkUint32")
    for t_name in new_type_names:
        TypeAdder(types_2015, types_2014).add(types_2015[t_name], look_for_array_primitives=array_primitives)

    return types_2014.get_xml()
