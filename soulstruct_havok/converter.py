"""Methods that operate on `HKXTypeList` instances and modify types to be compatible with a certain HK version."""
from __future__ import annotations

__all__ = ["resize_pointers", "resize_types", "realign_types"]

import typing as tp

if tp.TYPE_CHECKING:
    from .types import HKXType, HKXTypeList


def convert_types_to_2015(hkx_types: HKXTypeList):
    """The bundled XML type database already provides 2015 types, so this is only needed to modify types that have
    previously been explicitly converted to or loaded in other versions.
    """

    hkx_types_2015 = HKXTypeList.load_2015()

    # Restore versions and members to 2015.
    # TODO
    # _update_version_and_members(
    #     hkx_types,
    #     hkx_types_2015,
    #     "hkReferencedObject",  # will rename `referenceCount` to `refCount` as well
    #     "hkxMeshSection",
    #     "hkxVertexBuffer::VertexData",
    #     "hkxVertexDescription::ElementDecl",
    #     "hkxMaterial",
    #     "hkaSkeleton",
    #     "hkcdStaticMeshTreeBase",
    #     "hkaInterleavedUncompressedAnimation",
    #     "hkpStaticCompoundShape",
    #     "hkpStaticCompoundShape::Instance",
    # )
    resize_pointers(hkx_types, 8)
    realign_types(
        hkx_types,
        8,
        "hkRootLevelContainer::NamedVariant",
        "hkBaseObject",
        "hkArray",
    )
    resize_types(hkx_types, "hkArray")  # resized first, as it appears in types below
    resize_types(
        hkx_types,
        "hkRootLevelContainer::NamedVariant",
        "hkaAnimationContainer",
        "hkaSkeleton",
        "hkaSplineCompressedAnimation",
        "hkaDefaultAnimatedReferenceFrame",
        "hkaAnnotationTrack",
        "hkaAnimationBinding",
        "hkaBone",
    )


def convert_types_to_2014(hkx_types: HKXTypeList):
    """Bloodborne and Dark Souls 3."""

    _set_max_version(hkx_types, "hkReferencedObject", 0)
    _remove_member(hkx_types, "hkReferencedObject", "propertyBag")
    if hkx_type := hkx_types.get_type("hkReferencedObject"):
        hkx_type.get_member("refCount").name = "referenceCount"

    _set_max_version(hkx_types, "hkxMeshSection", 4)
    _remove_member(hkx_types, "hkxMeshSection", "boneMatrixMap")

    _set_max_version(hkx_types, "hkxVertexBuffer::VertexData", 0)

    _set_max_version(hkx_types, "hkxVertexDescription::ElementDecl", 3)
    _remove_member(hkx_types, "hkxVertexDescription::ElementDecl", "channelID")

    _set_max_version(hkx_types, "hkxMaterial", 4)
    _remove_member(hkx_types, "hkxMaterial", "userData")

    _set_max_version(hkx_types, "hkaSkeleton", 5)

    _set_max_version(hkx_types, "hkcdStaticMeshTreeBase", 0)
    _remove_member(hkx_types, "hkcdStaticMeshTreeBase", "primitiveStoresIsFlatConvex")

    _set_max_version(hkx_types, "hkaInterleavedUncompressedAnimation", 0)

    # TODO: Resolve this in XML databases.
    if hkx_type := hkx_types.get_type("hkpStaticCompoundShape"):
        backported_tag = hkx_type.get_member_type("instanceExtraInfos", hkx_types).pointer_type_index
        hkx_type.get_member("numBitsForChildShapeKey").tag = backported_tag

    _set_max_version(hkx_types, "hkpStaticCompoundShape::Instance", 0)

    _remove_member(hkx_types, "hkaAnimationBinding", "originalSkeletonName")

    # _set_alignment(
    #     4,
    #     "hkRootLevelContainer::NamedVariant",
    #     "hkBaseObject",
    #     "hkArray",
    # )
    # _resize("hkArray")  # resized first, as it appears in types below
    resize_types(
        hkx_types,
        # "hkRootLevelContainer::NamedVariant",
        "hkaAnimationContainer",
        "hkaSkeleton",
        # "hkaDefaultAnimatedReferenceFrame",
        # "hkaAnnotationTrack",
        # "hkaBone",
    )

    _resize_with_custom_member_offset(
        hkx_types,
        "hkaSplineCompressedAnimation",
        member_name="blockOffsets",
        force_member_offset=88,  # not 84
    )

    _resize_with_custom_member_offset(
        hkx_types,
        "hkaAnimationBinding",
        member_name="animation",
        force_member_offset=24,  # not 16 ("originalSkeletonName" member gone)
    )

    # for m in self["hkaAnimationContainer"].all_members:
    #     print(m.name, m.byte_offset)


def convert_types_to_2012(hkx_types: HKXTypeList):
    """Modify all HKX node types to make them compatible for 2012 `packfile`-type Havok.
    TODO: Unsure exactly which versions of Havok this will work for, outside 2012. Definitely works for Dark Souls
     PTDE at least (2010).
    """

    _set_max_version(hkx_types, "hkReferencedObject", 0)
    _remove_member(hkx_types, "hkReferencedObject", "propertyBag")
    if hkx_type := hkx_types.get_type("hkReferencedObject"):
        hkx_type.get_member("refCount").name = "referenceCount"

    # I don't remove the "propertyBag" types (or any types - just the members that reference them).

    _set_max_version(hkx_types, "hkxMeshSection", 4)
    _remove_member(hkx_types, "hkxMeshSection", "boneMatrixMap")

    _set_max_version(hkx_types, "hkxVertexBuffer::VertexData", 0)

    _set_max_version(hkx_types, "hkxVertexDescription::ElementDecl", 3)
    _remove_member(hkx_types, "hkxVertexDescription::ElementDecl", "channelID")

    _set_max_version(hkx_types, "hkxMaterial", 4)
    _remove_member(hkx_types, "hkxMaterial", "userData")

    _set_max_version(hkx_types, "hkaSkeleton", 5)
    _remove_member(hkx_types, "hkaSkeleton", "partitions")

    _set_max_version(hkx_types, "hkcdStaticMeshTreeBase", 0)
    _remove_member(hkx_types, "hkcdStaticMeshTreeBase", "primitiveStoresIsFlatConvex")

    _set_max_version(hkx_types, "hkaInterleavedUncompressedAnimation", 0)

    if hkx_type := hkx_types.get_type("hkpStaticCompoundShape"):
        backported_tag = hkx_type.get_member_type("instanceExtraInfos", hkx_types).pointer_type_index
        hkx_type.get_member("numBitsForChildShapeKey").tag = backported_tag

    _set_max_version(hkx_types, "hkpStaticCompoundShape::Instance", 0)

    # Convert `hkReflect::Detail::Opaque` pointers to `void`.
    for hkx_type in hkx_types:
        if hkx_type.pointer_type_index and hkx_type.get_pointer_type(hkx_types).name_without_colons == "hkReflectDetailOpaque":
            hkx_type.pointer = hkx_types["void"]

    # Simplify `hkpShape` hierarchy.
    if hkx_type := hkx_types.get_type("hkpShape"):
        hkx_type.parent_type_index = hkx_types.get_type_index("hkReferencedObject")  # not hkpShapeBase/hkcdShape
        # hkpShape technically has a `type` enum member in 2010 (instead of `hkcdShape` having it), but I believe it
        # is never used and can be ignored here.

    # Rename `hkSimpleProperty`.
    if hkx_type := hkx_types.get_type("hkSimpleProperty"):
        hkx_type.name = "hkpProperty"

    # Add "npData" member to `hkpEntity`.
    if hkx_type := hkx_types.get_type("hkpEntity"):
        if hkx_type.members[-1].name == "extendedListeners":
            # TODO
            # byte_offset = hkx_type.members[-1].offset + 4  # last member is "extendedListeners" pointer
            # hkx_type.members.append(HKXMember("npData", 32, byte_offset, self["hkUint32"]))
            pass

    # SIZING

    resize_pointers(hkx_types, 4)
    realign_types(
        hkx_types,
        4,
        "hkRootLevelContainer::NamedVariant",
        "hkBaseObject",
        "hkArray",
    )
    resize_types(hkx_types, "hkArray")  # resized first, as it appears in types below
    resize_types(
        hkx_types,
        "hkRootLevelContainer::NamedVariant",
        "hkaAnimationContainer",
        "hkaSkeleton",
        "hkaSplineCompressedAnimation",
        "hkaDefaultAnimatedReferenceFrame",
        "hkaAnnotationTrack",
        "hkaAnimationBinding",
        "hkaBone",
    )

    # TODO: hkaBone actually has byte size 12 (not 8) after DS1 (2010).


def convert_types_to_2010(hkx_types):
    convert_types_to_2012(hkx_types)

    _remove_member(hkx_types, "hkaAnimationBinding", "partitionIndices")
    # TODO: I believe "blendHint" member is still present here (now moved up).


def resize_pointers(hkx_types: HKXTypeList, pointer_size: int):
    """Find all pointer types and set their `byte_size` and `alignment` to the given `pointer_size`.

    Modifies all node types that end with "*" and all node types with a single member whose type ends with "*".
    """
    if pointer_size not in {4, 8}:
        raise ValueError(f"Invalid pointer size: {pointer_size}. Should be 4 or 8.")
    for hkx_type in hkx_types:
        if hkx_type.name.endswith("*"):
            hkx_type.byte_size = 4
            hkx_type.alignment = 4
        elif len(hkx_type.members) == 1 and hkx_type.members[0].get_type_name(hkx_types)[-1] == "*":
            # e.g. hkStringPtr, hkRefVariant, hkRefPtr
            hkx_type.byte_size = 4
            hkx_type.alignment = 4


def realign_types(hkx_types: HKXTypeList, alignment: int, *hkx_type_names: str):
    """Set all the given node types' alignment to `alignment`."""
    for hkx_type in hkx_types:
        if hkx_type.name in hkx_type_names:
            hkx_type.alignment = alignment


def resize_types(hkx_types: HKXTypeList, *hkx_type_names: str):
    """Adjust `offset` of each member (in full type hierarchy) of all node types with one of the given names,
    and their overall `byte_size`, by iterating over all members and assuming tight packing.

    Type alignment is applied after each parent type in the hierarchy.
    """
    for hkx_type in hkx_types:
        if hkx_type.name in hkx_type_names:
            member_offset = 0
            for base_type in hkx_type.get_type_hierarchy(hkx_types):
                for member in base_type.members:
                    member.offset = member_offset
                    member_offset += member.get_base_type(hkx_types).byte_size
                if base_type.alignment != 0:
                    if member_offset == 0:
                        member_offset += base_type.alignment  # e.g. for "hkBaseObject"
                    else:
                        while member_offset % base_type.alignment:
                            member_offset += 1  # align to parent
            hkx_type.byte_size = member_offset  # total size


def _resize_with_custom_member_offset(
    hkx_types: HKXTypeList, hkx_type_name: str, member_name: str, force_member_offset: int
):
    """Adjust `byte_offset` of each member (in full type hierarchy) of all node types with one of the given names,
    and their overall `byte_size`, by iterating over all members and assuming tight packing.

    This version also forcibly sets a custom offset, `member_offset`, when it encounters `member_name`, which will
    also push back all the members after that.

    Type alignment is applied after each parent type in the hierarchy.
    """
    if hkx_type := hkx_types.get_type(hkx_type_name):
        member_offset = 0
        for base_type in hkx_type.get_type_hierarchy(hkx_types):
            for member in base_type.members:
                if member.name == member_name:
                    member_offset = force_member_offset
                member.offset = member_offset
                member_offset += member.get_base_type(hkx_types).byte_size
            if base_type.alignment != 0:
                if member_offset == 0:
                    member_offset += base_type.alignment  # e.g. for "hkBaseObject"
                else:
                    while member_offset % base_type.alignment:
                        member_offset += 1  # align to parent
        hkx_type.byte_size = member_offset  # total size


def _update_version_and_members(hkx_types, source_hkx_types: HKXTypeList, *hkx_type_names: str):
    # TODO: Not what I actually want. Just create the converted XML databases.
    """Update all given node types to have the same version and members as their corresponding entry in
    `source_hkx_types`.

    You are technically permitted to pass non-unique node type names to this method, but the type MUST be unique in
    `source_hkx_types` so the exact match can be found, which will generally not be the case if it is not unique
    in this instance.
    """
    for hkx_type in hkx_types:
        if hkx_type.name in hkx_type_names:
            source_hkx_type = source_hkx_types.get_type(hkx_type.name, allow_missing=False)
            hkx_type.version = source_hkx_type.version
            current_member_dict = {member.name: member for member in hkx_type.members}
            hkx_type.members = []
            for member in source_hkx_type.members:
                if member.name in current_member_dict:
                    hkx_type.members.append(current_member_dict[member.name])
                else:
                    hkx_type.members.append(member)
                    # TODO
                    # if member.hkx_type not in hkx_types:  # somehow
                    #     type_repairer = NodeTypeRepairer(source_hkx_types)
                    #     type_repairer.repair(hkx_types, member.hkx_type, replace_unique_types=False)


def _set_max_version(hkx_types: HKXTypeList, hkx_type: tp.Union[HKXType, str], max_version: int):
    if isinstance(hkx_type, str):
        hkx_type = hkx_types.get_type(hkx_type)
    if hkx_type:
        hkx_type.version = min(hkx_type.version, max_version)


def _remove_member(hkx_types: HKXTypeList, hkx_type: tp.Union[HKXType, str], member_name: str):
    """Remove the `HKXMember` with given `member_name` from node type with name `hkx_type_name`."""
    if isinstance(hkx_type, str):
        hkx_type = hkx_types.get_type(hkx_type)
    if hkx_type:
        if member := hkx_type.get_member(member_name, allow_missing=True):
            hkx_type.members.remove(member)
