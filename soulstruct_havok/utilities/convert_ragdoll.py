"""Convert a `hk2014` ragdoll, using `hknp` physics, to a `hk2015` ragdoll using older `hkp` physics."""
from __future__ import annotations

import json
import re
import typing as tp
from pathlib import Path

from soulstruct.containers import Binder
from soulstruct.containers.bnd import BaseBND

from soulstruct_havok.core import HKX
from soulstruct_havok.types import hk2014


BLOODBORNE_CHR_PATH = Path("C:/Dark Souls/Other FromSoft Games/Bloodborne/DISC/Image0/dvdroot_ps4/chr")


# noinspection PyUnresolvedReferences,PyTypeChecker
def extract_info_to_json(ragdoll: HKX | BaseBND, output_json_path: Path | str):
    """Convert information required for DSR ragdoll generation to JSON."""
    if isinstance(ragdoll, BaseBND):
        # CHRBND
        for entry in ragdoll.entries:
            if re.match(r"c\d\d\d\d.[Hh][Kk][Xx]", entry.name):
                ragdoll = HKX(entry)
                break
        else:
            raise ValueError(f"Could not find a ragdoll HKX in given CHRBND.")

    info = {}  # type: dict[tp.Any, tp.Any]

    variants = ragdoll.root.namedVariants  # type: list[hk2014.hkRootLevelContainerNamedVariant]
    animation_container = variants[0].variant  # type: hk2014.hkaAnimationContainer
    physics_scene_data = variants[1].variant  # type: hk2014.hknpPhysicsSceneData   # just contains `ragdoll_data` again
    ragdoll_data = variants[2].variant  # type: hk2014.hknpRagdollData
    master_to_ragdoll_mapper = variants[3].variant  # type: hk2014.hkaSkeletonMapper
    ragdoll_to_master_mapper = variants[4].variant  # type: hk2014.hkaSkeletonMapper

    # Skeletons.
    for skeleton in animation_container.skeletons:
        skeleton: hk2014.hkaSkeleton
        info[skeleton.name] = []
        for bone, parent, ref_pose in zip(skeleton.bones, skeleton.parentIndices, skeleton.referencePose):
            info[skeleton.name].append({
                "name": bone.name,
                "lockTranslation": bone.lockTranslation,
                "parentIndex": parent,
                "translation": ref_pose.translation,
                "rotation": ref_pose.rotation,
                "scale": ref_pose.scale
            })

    info["physics"] = {"shapes": []}
    for body_c_info in ragdoll_data.bodyCinfos:
        info["physics"]["shapes"].append(
            {
                "class_name": body_c_info.shape.__class__.__name__,
                "convexRadius": body_c_info.shape.convexRadius,
                "position": body_c_info.position,
                "orientation": body_c_info.orientation,
                "name": body_c_info.name,
            }
        )
        if isinstance(body_c_info.shape, hk2014.hknpCapsuleShape):
            info["physics"]["shapes"][-1].update({"a": body_c_info.shape.a, "b": body_c_info.shape.b})
        elif isinstance(body_c_info.shape, hk2014.hknpConvexPolytopeShape):
            info["physics"]["shapes"][-1].update({"vertices": body_c_info.shape.vertices})
        else:
            raise TypeError(f"Unhandled `hknp` shape type: {type(body_c_info.shape).__name__}")
    shape_instances = [body_c_info.shape for body_c_info in ragdoll_data.bodyCinfos]
    info["physics"]["referencedObjects"] = [shape_instances.index(shape) for shape in ragdoll_data.referencedObjects]
    info["physics"]["boneToBodyMap"] = ragdoll_data.boneToBodyMap

    for name, mapper in zip(
        ("master_to_ragdoll_mapper", "ragdoll_to_master_mapper"),
        (master_to_ragdoll_mapper, ragdoll_to_master_mapper),
    ):
        info[name] = {"simpleMappings": [], "unmappedBones": mapper.mapping.unmappedBones}
        for simple_mapping in mapper.mapping.simpleMappings:
            info[name]["simpleMappings"].append({
                "boneA": simple_mapping.boneA,
                "boneB": simple_mapping.boneB,
                "translate": simple_mapping.aFromBTransform.translation,
                "rotation": simple_mapping.aFromBTransform.rotation,
                "scale": simple_mapping.aFromBTransform.scale,
            })
        # TODO: Should export `chainMappings` in case some other BB models use it (c2800 does not).

    # print(len(info["master_to_ragdoll_mapper"]["simpleMappings"]))
    # print(len(info["ragdoll_to_master_mapper"]["simpleMappings"]))

    with Path(output_json_path).open("w") as f:
        json.dump(info, f, indent=4)


if __name__ == '__main__':
    # nf_chr_path = Path("F:/Steam/steamapps/common/DARK SOULS REMASTERED (Nightfall)/chr")
    # c2240_chrbnd = BND3(nf_chr_path / "c2240.chrbnd.dcx.bak")

    extract_info_to_json(
        Binder(BLOODBORNE_CHR_PATH / "c2310.chrbnd.dcx"),
        Path("C:/Dark Souls/havok-old/soulstruct_havok/BB_c2310_ragdoll.json"),
    )
