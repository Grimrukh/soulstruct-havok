from __future__ import annotations

from pathlib import Path

from soulstruct.config import DSR_PATH
from soulstruct.containers import Binder
from soulstruct.utilities.maths import *

from soulstruct_havok.core import HKX
from soulstruct_havok.wrappers.base import BaseSkeletonHKX
from soulstruct_havok.wrappers.hkx2015.animation_manager import AnimationManager as AnimationManagerDS1
from soulstruct_havok.wrappers.hkx2018.animation_manager import AnimationManager as AnimationManagerER

GAME_CHR_PATH = DSR_PATH + "/chr"


def examine_asylum_erdtree_skeletons():
    """My attempts to retarget Erdtree Avatar animations (c4810 in ER) to Stray Demon (c2230 in DSR).

    - Erdtree Avatar has more bones, unsurprisingly. Some are also renamed.
    -
    """
    er_chr = Path("C:/Steam/steamapps/common/ELDEN RING (Vanilla)/Game/chr")
    dsr_chr = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/chr")

    er_bnd = Binder(er_chr / "c4810.anibnd.dcx")
    er_compendium = HKX(er_bnd["c4810.compendium"])
    er_skeleton = BaseSkeletonHKX(er_bnd["skeleton.hkx"], compendium=er_compendium)

    dsr_bnd = Binder(dsr_chr / "c2230.anibnd.dcx")
    dsr_skeleton = BaseSkeletonHKX(dsr_bnd["Skeleton.HKX"])

    # Remove "new" Erdtree Avatar bone hierarchies.
    # er_skeleton.delete_bone("[cloth]_c4810_skirt_01")
    # er_skeleton.delete_bone("[cloth]_c4810_skirt_04")
    # er_skeleton.delete_bone("[cloth]_c4810_skirt_07")
    # er_skeleton.delete_bone("[cloth]_c4810_skirt_leaf_01")
    # er_skeleton.delete_bone("[cloth]_c4810_body_01")
    # er_skeleton.delete_bone("[cloth]_c4810_body_03")
    # er_skeleton.delete_bone("[cloth]_c4810_arm_01")
    # er_skeleton.delete_bone("[cloth]_c4810_arm_03")
    # er_skeleton.delete_bone("[cloth]_c4810_arm_05")
    # er_skeleton.delete_bone("[cloth]_c4810_arm_07")
    # er_skeleton.delete_bone("[cloth]_c4810_arm_09")
    # er_skeleton.delete_bone("[cloth]_c4810_arm_11")
    #
    # er_skeleton.delete_bone("Stomach1")
    # er_skeleton.delete_bone("Stomach2")
    # er_skeleton.delete_bone("Stomach3")
    #
    # er_skeleton.delete_bone("L_Foot_Target2")
    # er_skeleton.delete_bone("R_Foot_Target2")
    #
    # for arm in "LR":
    #     er_skeleton.delete_bone(f"{arm}_Shoulder")
    #     # er_skeleton.delete_bone(f"{arm}_Elbow")
    #     er_skeleton.delete_bone(f"{arm}_ForeArmTwist1")

    # TODO: Skeletons do have some minor changes that will need to be handled.
    #  - First goal should be to just get the closest Asylum bones possible, even if imperfect.
    #  - Port over anim 3000 first.

    dsr_skeleton.print_bone_tree()
    er_skeleton.print_bone_tree()

    print(f"Avatar has {len(er_skeleton.skeleton.bones)}")
    print(f"Demon has {len(dsr_skeleton.skeleton.bones)}")

    draw_skeleton(
        dsr_skeleton, auto_show=False, scatter_color="red", line_color="red", z_bounds=(0, 8),
        # bone_names=[b.name for b in dsr_skeleton.skeleton.bones if "tail" in b.name.lower()],
    )
    draw_skeleton(
        er_skeleton, auto_show=True, scatter_color="green", line_color="green", z_bounds=(0, 8), scale=1.17,
        # bone_names=[b.name for b in er_skeleton.skeleton.bones if "tail" in b.name.lower()],
    )


def draw_skeleton(
    skeleton: BaseSkeletonHKX,
    x_bounds=(-5, 5),
    y_bounds=(-5, 5),
    z_bounds=(0, 10),
    bone_names=(),
    scale=1.0,
    ax=None,
    auto_show=False,
    scatter_color="red",
    line_color="black"
):
    """Figure out how to properly resolve bones in a nice way, with connected heads and tails, for Blender."""
    # noinspection PyPackageRequirements
    import matplotlib.pyplot as plt
    if ax is None:
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection="3d")

    bone_translates = [
        skeleton.get_bone_global_transform(bone).translate * scale
        for bone in skeleton.skeleton.bones
    ]

    if not bone_names:
        bone_names = [bone.name for bone in skeleton.skeleton.bones]

    for bone_name in bone_names:
        bone = skeleton.resolve_bone_spec(bone_name)
        bone_index = skeleton.skeleton.bones.index(bone)

        translate = bone_translates[bone_index]
        ax.scatter(translate[0], translate[2], translate[1], c=scatter_color)
        ax.text(translate[0], translate[2], translate[1], bone.name)

        parent_index = skeleton.get_bone_parent_index(bone)
        if parent_index != -1:
            parent_translate = bone_translates[parent_index]
            ax.plot(
                [translate[0], parent_translate[0]],
                [translate[2], parent_translate[2]],
                [translate[1], parent_translate[1]],
                c=line_color,
            )

    # Quick way to expand axes.
    for x in x_bounds:
        for y in y_bounds:
            for z in z_bounds:
                ax.scatter(x, y, z)

    if auto_show:
        plt.show()
    return ax


DSR_CHR = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/chr")
DSR_VAN_CHR = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (Vanilla Backup)/chr")
ER_CHR = Path("C:/Steam/steamapps/common/ELDEN RING (Vanilla)/Game/chr")


def plot_interleaved_translations(transforms: list[QuatTransform], title: str, autoshow=False):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots()
    x = [t.translate.x for t in transforms]
    y = [t.translate.y for t in transforms]
    z = [t.translate.z for t in transforms]
    fig.suptitle(title)
    axes.plot(x, label="X")
    axes.plot(y, label="Y")
    axes.plot(z, label="Z")
    axes.legend()
    if autoshow:
        plt.show()


def do_erdtree_retarget():
    print("Reading 2015 animation...")
    asylum_manager = AnimationManagerDS1.from_anibnd(DSR_VAN_CHR / "c2230.anibnd.dcx", 3000, from_bak=True)
    print("Reading 2018 animation...")
    erdtree_manager = AnimationManagerER.from_anibnd(ER_CHR / "c4810.anibnd.dcx", 3000, from_bak=True)

    print("Converting 2015 spline to interleaved...")
    asylum_manager.animations[3000].spline_to_interleaved()
    print("Converting 2018 spline to interleaved...")
    erdtree_manager.animations[3000].spline_to_interleaved()

    print([b.name for b in asylum_manager.skeleton.get_hierarchy_to_bone("L Toe0")])
    print([b.name for b in erdtree_manager.skeleton.get_hierarchy_to_bone("L_Toe0")])
    exit()

    # plot_interleaved_translations(asylum_manager.get_bone_interleaved_transforms("Master"), "Asylum Master")
    # plot_interleaved_translations(asylum_manager.get_bone_interleaved_transforms("Pelvis"), "Asylum Pelvis")
    # plot_interleaved_translations(erdtree_manager.get_bone_interleaved_transforms("Master"), "Erdtree Master")
    # plot_interleaved_translations(erdtree_manager.get_bone_interleaved_transforms("Root"), "Erdtree Root")
    # plot_interleaved_translations(erdtree_manager.get_bone_interleaved_transforms("Pelvis"), "Erdtree Pelvis", True)
    # exit()

    print("Retargeting Erdtree animation...")
    asylum_manager.auto_retarget_interleaved_animation(erdtree_manager, 3000, 3000, RETARGET)
    asylum_manager.animations[3000].scale(1.17)

    # print("Correcting Master transform...")
    asylum_manager.transform_bone_track(
        "Master",
        QuatTransform(translate=Vector3(0, -1, 0)),
    )

    # Weapon rotation.
    asylum_manager.rotate_bone_track(
        "R_weapon",
        Quaternion.from_axis_angle(Vector3(0, 0, 1), angle=90.0),
    )

    # Shrink gut.
    for bone in ("a", "b", "c"):
        asylum_manager.transform_bone_track(
            bone,
            QuatTransform(scale=0.5),
        )

    asylum_manager.write_anim_ids_into_anibnd(
        DSR_VAN_CHR / "c2230.anibnd.dcx", 3000, from_bak=True,
        write_path=DSR_CHR / "c2230_erdtree_interleaved.anibnd.dcx",
    )

    do_erdtree_adjustment(asylum_manager)


# TODO: Random note: I can speed up Havok array reading with better `struct.unpack` calls. For example, don't call
#  unpack 2000 times for an array of 2000 floats! Call it once with "2000f" format.


def do_erdtree_adjustment(asylum_manager: AnimationManagerDS1 = None):
    if asylum_manager is None:
        print("Reading 2015 animation...")
        asylum_manager = AnimationManagerDS1.from_anibnd(
            DSR_CHR / "c2230_erdtree_interleaved.anibnd.dcx", 3000, from_bak=False
        )

    print("Making edits to bones...")
    # asylum_manager.transform_bone_track(
    #     "L Clavicle",
    #     QuatTransform(translate=Vector3(-0.2, 0.8, 0.0)),
    #     compensate_child_bones=True,
    # )
    # asylum_manager.transform_bone_track(
    #     "R Clavicle",
    #     QuatTransform(translate=Vector3(-0.2, -0.8, 0.0)),
    #     compensate_child_bones=True,
    # )
    # asylum_manager.transform_bone_track(
    #     "L UpperArm",
    #     QuatTransform(translate=Vector3(-0.2, 0.8, 0.0)),
    #     compensate_child_bones=True,
    # )
    # asylum_manager.transform_bone_track(
    #     "R UpperArm",
    #     QuatTransform(translate=Vector3(-0.2, -0.8, 0.0)),
    #     compensate_child_bones=True,
    # )

    # TODO: Don't need to convert back to splines for DSAS.
    # print(f"Converting interleaved anim to spline...")
    # asylum_manager.convert_interleaved_to_spline_anim(3000)

    print("Writing into ANIBND for DSR...")
    asylum_manager.write_anim_ids_into_anibnd(
        DSR_VAN_CHR / "c2230.anibnd.dcx", 3000, from_bak=True,
        write_path=DSR_CHR / "c2230.anibnd.dcx",
    )

    print("Done.")

    # print(hkx2015_spline.get_root_tree_string())


"""
I'm convinced I can improve this retarget.

By omitting Erdtree bones that Asylum doesn't have, I'm losing valuable animation information (obviously - those bones
aren't going to coincidentally have null transforms). This is probably responsible for most of my mismatch.

I should be able to handle new and moved bones with some clever bone transformations. I also have access to purely
interleaved data now, which should support some more grandious retargeting approaches.

Simple example:
    - If the retarget source has bone B inserted between A and C, I need to make sure that child C "inherits" all the
    information bone B.
        - In this case, the new local transform for bone C should be (B @ C). This will mean C effectively has the same
        frame of reference that it had in the source skeleton: the absolute position of C is (A @ B @ C) in both cases
        now. 
    -  

Example:
    - Interleave all data and create a "rig":
        - Scale Erdtree skeleton up by 17% to roughly match.
        - For
"""


# Maps Asylum Demon bones to Erdtree Avatar bones.
RETARGET = {

    # Erdtree Master contains some rotation only, which we absorb into Root (now Master).
    "Master": ("Master", "Root"),
    "Pelvis": "Pelvis",
    "a": None,
    "b": None,
    "c": None,
    "d": None,  # "L_Hip2",
    "e": None,  # "R_Hip2",

    # TODO: Erdtree Avatar thighs and wings are children of 'Pelvis', not 'Spine'.
    #  I *think* this means that I want to "erase" the effects of Spine on thighs/wings.
    #  By mapping, e.g., L Thigh to (~Spine, L_Thigh), I am making the Asylum root space:
    #    Master @ Pelvis @ Spine @ (~Spine @ L_Thigh)
    #  which looks like it would have the effect I want.

    # TODO: Actually, more importantly: Erdtree Spine is NEXT TO Pelvis, not a child of it.
    #  That's my issue: Pelvis rotation is affecting the thighs (and wings, less importantly).
    #  So I ALSO want to

    # TODO: Erdtree Avatar 'L_ThighTwist' is a child of 'L_Thigh' rather than next to it.
    "LThighTwist": ["L_Thigh", "L_ThighTwist"],
    "RThighTwist": ["R_Thigh", "R_ThighTwist"],

    "Spine": ["~Pelvis", "Spine", "Spine1"],
    "Spine1": "Spine2",

    "L Thigh": ["~Spine", "L_Thigh"],
    "L Calf": "L_Calf",
    "L Foot": "L_Foot",
    "L Toe0": ["L_Toe0", "L_FootFinger1"],
    "L Toe01": "L_FootFinger102",
    "L Toe02": "L_FootFinger103",
    "L Toe0Nub": None,
    "L Toe1": ["L_Toe0", "L_FootFinger2"],
    "L Toe11": "L_FootFinger202",
    "L Toe12": "L_FootFinger203",
    "L Toe1Nub": None,
    "L Toe2": ["L_Toe0", "L_FootFinger3"],
    "L Toe21": "L_FootFinger302",
    "L Toe22": "L_FootFinger303",
    "L Toe2Nub": None,

    "R Thigh": ["~Spine", "R_Thigh"],
    "R Calf": "R_Calf",
    "R Foot": "R_Foot",
    "R Toe0": ["R_Toe0", "R_FootFinger1"],
    "R Toe01": "R_FootFinger102",
    "R Toe02": "R_FootFinger103",
    "R Toe0Nub": None,
    "R Toe1": ["R_Toe0", "R_FootFinger2"],
    "R Toe11": "R_FootFinger202",
    "R Toe12": "R_FootFinger203",
    "R Toe1Nub": None,
    "R Toe2": ["R_Toe0", "R_FootFinger3"],
    "R Toe21": "R_FootFinger302",
    "R Toe22": "R_FootFinger303",
    "R Toe2Nub": None,

    "L Clavicle": "L_Clavicle",
    "L UpperArm": "L_UpperArm",
    "L Forearm": "L_Forearm",
    "L Hand": "L_Hand",
    "L Finger0": "L_Finger0",
    "L Finger01": "L_Finger01",
    "L Finger02": "L_Finger02",
    "L Finger0Nub": None,
    "L Finger1": "L_Finger1",
    "L Finger11": "L_Finger11",
    "L Finger12": "L_Finger12",
    "L Finger1Nub": None,
    "L Finger2": "L_Finger2",
    "L Finger21": "L_Finger21",
    "L Finger22": "L_Finger22",
    "L Finger2Nub": None,
    "L Finger3": "L_Finger3",
    "L Finger31": "L_Finger31",
    "L Finger32": "L_Finger32",
    "L Finger3Nub": None,
    "L ForeTwist": "L_Elbow",
    "LUpArmTwist": "L_UpArmTwist",

    "R Clavicle": "R_Clavicle",
    "R UpperArm": "R_UpperArm",
    "R Forearm": "R_Forearm",
    "R Hand": "R_Hand",
    "R Finger0": "R_Finger0",
    "R Finger01": "R_Finger01",
    "R Finger02": "R_Finger02",
    "R Finger0Nub": None,
    "R Finger1": "R_Finger1",
    "R Finger11": "R_Finger11",
    "R Finger12": "R_Finger12",
    "R Finger1Nub": None,
    "R Finger2": "R_Finger2",
    "R Finger21": "R_Finger21",
    "R Finger22": "R_Finger22",
    "R Finger2Nub": None,
    "R Finger3": "R_Finger3",
    "R Finger31": "R_Finger31",
    "R Finger32": "R_Finger32",
    "R Finger3Nub": None,
    "R ForeTwist": "R_Elbow",
    "RUpArmTwist": "R_UpArmTwist",

    "R_weapon": "R_Club",

    "L_wing_00": ("~Spine", "L_Wing1"),
    "L_wing_01": "L_Wing102",
    "L_wing_02": "L_Wing103",
    "L_wing_03": "L_Wing104",
    "L_wing_04": "L_Wing105",
    "L_wingNub": None,
    "L_wing_digit_a_00": "L_Wing3",
    "L_wing_digit_a_01": "L_Wing302",
    "L_wing_digit_a_02": "L_Wing303",
    "L_wing_digit_aNub": None,
    "L_wing_digit_b_00": "L_Wing4",
    "L_wing_digit_b_01": "L_Wing402",
    "L_wing_digit_bNub": None,
    "L_wing_digit_c": "L_Wing2",
    "L_wing_digit_cNub": None,

    "R_wing_00": ["~Spine", "R_Wing1"],
    "R_wing_01": "R_Wing102",
    "R_wing_02": "R_Wing103",
    "R_wing_03": "R_Wing104",
    "R_wing_04": "R_Wing105",
    "R_wingNub": None,
    "R_wing_digit_a_00": "R_Wing3",
    "R_wing_digit_a_01": "R_Wing302",
    "R_wing_digit_a_02": "R_Wing303",
    "R_wing_digit_aNub": None,
    "R_wing_digit_b_00": "R_Wing4",
    "R_wing_digit_b_01": "R_Wing402",
    "R_wing_digit_bNub": None,
    "R_wing_digit_c": "R_Wing2",
    "R_wing_digit_cNub": None,

    "tail_00": "Tail",
    "tail_01": "Tail02",
    "tail_02": "Tail03",
    "tail_03": "Tail04",
    "tail_04": "Tail05",
    "tail_05": "Tail06",
    "tail_06": "Tail07",
    "tail_07": "Tail08",
    "tailNub": None,

    "Neck": "Neck",
    "Head": "Head",
    "HeadNub": None,
    "Jaw": "Jaw",
    "Jaw2": "Jaw2",
    "JawNub": None,
    "Tongue_00": "Tongue",
    "Tongue_01": "Tongue02",
    "TongueNub": None,

    "R_ear_00": "R_Ear",
    "R_ear_01": "R_Ear02",
    "R_ear_02": "R_Ear03",
    "R_earNub": None,
    "L_ear_00": "L_Ear",
    "L_ear_01": "L_Ear02",
    "L_ear_02": "L_Ear03",
    "L_earNub": None,
}


def quat_test():
    qt = QuatTransform(
        translate=Vector3(1, 2, 3),
        rotation=Quaternion.from_axis_angle(Vector3(1, 1, 0), angle=45),
        scale=Vector3(2, 1, 1),
    )
    print(qt)
    mat = (qt @ QuatTransform.identity()).to_matrix4()
    inv_mat = qt.inverse_mul(QuatTransform.identity()).to_matrix4()
    print(mat)
    print(inv_mat)
    print(inv_mat @ mat)


if __name__ == '__main__':
    # examine_asylum_erdtree_skeletons()
    # do_erdtree_retarget()
    # do_erdtree_adjustment()
    quat_test()
