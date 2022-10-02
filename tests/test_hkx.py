from __future__ import annotations

from pathlib import Path

from soulstruct.base.models.flver import FLVER
from soulstruct.config import DSR_PATH
from soulstruct.containers import Binder
from soulstruct.utilities.maths import *

from soulstruct_havok.core import HKX
from soulstruct_havok.wrappers.base import AnimationHKX, SkeletonHKX
from soulstruct_havok.wrappers.hkx2015.animation_manager import AnimationManager as AnimationManagerDS1
from soulstruct_havok.wrappers.hkx2018.animation_manager import AnimationManager as AnimationManagerER

GAME_CHR_PATH = DSR_PATH + "/chr"


def retarget():
    """Challenges:

    - Scaling will be easy, but figuring out the bone mapping is harder.

    - Firstly, I need the ability to just remove tracks from the spline animation data without fully repacking it.
    Shouldn't be too hard using the same method as by scaling trick: unpack the data, keeping a separate writer, and
    only copy the data into the writer if it isn't one of the `excluded` track indices.

    - How do I handle missing bones in the dest model? That's fairly easy - just remove those tracks from the animation
    and ensure the rest are bound to the correct bones (as the indices of shared bones may change). This mapping can
    probably be handled by just looking up the index of the bone with the same name in the dest model (ignoring case).

    - How do I handle EXTRA bones in the dest model? That's a much harder issue, since the data for animating those
    bones just isn't there, yet those bones need to do something. It's POSSIBLE that Havok will just interpolate the
    movement of any bones that don't have a track in the animation. That's worth testing out. I don't really have any
    other option right now, since generating a new track would require new spline compression. We'll see what happens.

    - Anyway, for testing, we want two models with skeletons as similar as possible. Any differences should err toward
    less bones in the destination model. This is trickier than it sounds because a lot of humanoids have "cloth bones"
    that can vary a lot.
    """

    MODEL_1 = "c4100"
    MODEL_2 = "c2240"

    skeleton_1 = SkeletonHKX.from_anibnd(GAME_CHR_PATH / f"{MODEL_1}.anibnd.dcx", prefer_bak=True)
    print(f"{len(skeleton_1.skeleton.bones)} bones:")
    for bone, pose in zip(skeleton_1.skeleton.bones, skeleton_1.skeleton.reference_pose):
        print(f"    {bone.name}")
        # print("  ", pose.translation)

    print()
    skeleton_2 = SkeletonHKX.from_anibnd(GAME_CHR_PATH / f"{MODEL_2}.anibnd.dcx", prefer_bak=True)
    print(f"{len(skeleton_2.skeleton.bones)} bones:")
    for bone, pose in zip(skeleton_2.skeleton.bones, skeleton_2.skeleton.reference_pose):
        print(f"    {bone.name}")
        # print("  ", pose.translation)

    model_1_3000 = AnimationHKX.from_anibnd(GAME_CHR_PATH / f"{MODEL_1}.anibnd.dcx", 3000, prefer_bak=True)
    print(model_1_3000.animation_binding.transform_track_to_bone_indices)

    model_2_3000 = AnimationHKX.from_anibnd(GAME_CHR_PATH / f"{MODEL_2}.anibnd.dcx", 3000, prefer_bak=True)
    print(model_2_3000.animation_binding.transform_track_to_bone_indices)


def examine_asylum_erdtree_skeletons():
    """My attempts to retarget Erdtree Avatar animations (c4810 in ER) to Stray Demon (c2230 in DSR).

    - Erdtree Avatar has more bones, unsurprisingly. Some are also renamed.
    -
    """
    er_chr = Path("C:/Steam/steamapps/common/ELDEN RING (Vanilla)/Game/chr")
    dsr_chr = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/chr")

    er_bnd = Binder(er_chr / "c4810.anibnd.dcx")
    er_compendium = HKX(er_bnd["c4810.compendium"])
    er_skeleton = SkeletonHKX(er_bnd["skeleton.hkx"], compendium=er_compendium)

    dsr_bnd = Binder(dsr_chr / "c2230.anibnd.dcx")
    dsr_skeleton = SkeletonHKX(dsr_bnd["Skeleton.HKX"])

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


def asylum_retarget_test():

    er_chr = Path("C:/Steam/steamapps/common/ELDEN RING (Vanilla)/Game/chr")
    dsr_chr = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/chr")

    erdtree_manager = AnimationManagerER.from_anibnd(er_chr / "c4810.anibnd.dcx", 3000, from_bak=True)
    asylum_manager = AnimationManagerDS1.from_anibnd(dsr_chr / "c2230.anibnd.dcx", 3000, from_bak=True)

    asylum_manager.auto_retarget_animation(erdtree_manager, 3000, 3000, RETARGET)
    asylum_manager.scale_animation_data(1.17, 3000)

    # TODO: Testing adjustments.
    asylum_manager.transform_bone_track(
        "Master",
        QuatTransform(
            Vector3.zero(),
            Quaternion.from_axis_angle(Vector3(0, 1, 0), -90.0),
            Vector3.ones(),
        ),
    )
    asylum_manager.rotate_bone_track(
        "R Clavicle",
        Quaternion.from_axis_angle(Vector3(0, 0, 1), -60.0),
    )
    asylum_manager.rotate_bone_track(
        "L Clavicle",
        Quaternion.from_axis_angle(Vector3(0, 0, 1), 60.0),
    )

    asylum_manager.save_animation_data()
    asylum_manager.write_anim_ids_into_anibnd(dsr_chr / "c2230.anibnd.dcx", 3000, from_bak=True)


# Maps Asylum Demon bones to Erdtree Avatar bones.
RETARGET = {

    "Master": "Root",  # TODO: possibly should be 'Root'
    "Pelvis": "Pelvis",
    "a": None,
    "b": None,
    "c": None,
    "d": "L_Hip2",
    "e": "R_Hip2",

    # TODO: Erdtree Avatar thighs and wings are children of 'Pelvis', not 'Spine'.

    # TODO: Erdtree Avatar 'L_ThighTwist' is a child of 'L_Thigh' rather than next to it.
    "LThighTwist": None,  # "L_ThighTwist",
    "RThighTwist": None,  # "R_ThighTwist",

    # TODO: Erdtree Avatar 'Spine' is an extra bone added between 'Pelvis' and 'Spine1'.
    "Spine": "Spine1",
    "Spine1": "Spine2",

    "L Thigh": "L_Thigh",
    "L Calf": "L_Calf",
    "L Foot": "L_Foot",
    # TODO: Erdtree Avatar 'L_Toe0' is between 'L_Foot' and all three toes.
    "L Toe0": "L_FootFinger1",
    "L Toe01": "L_FootFinger102",
    "L Toe02": "L_FootFinger103",
    "L Toe0Nub": None,
    "L Toe1": "L_FootFinger2",
    "L Toe11": "L_FootFinger202",
    "L Toe12": "L_FootFinger203",
    "L Toe1Nub": None,
    "L Toe2": "L_FootFinger3",
    "L Toe21": "L_FootFinger302",
    "L Toe22": "L_FootFinger303",
    "L Toe2Nub": None,

    "R Thigh": "R_Thigh",
    "R Calf": "R_Calf",
    "R Foot": "R_Foot",
    # TODO: Erdtree Avatar 'R_Toe0' is between 'R_Foot' and all three toes.
    "R Toe0": "R_FootFinger1",
    "R Toe01": "R_FootFinger102",
    "R Toe02": "R_FootFinger103",
    "R Toe0Nub": None,
    "R Toe1": "R_FootFinger2",
    "R Toe11": "R_FootFinger202",
    "R Toe12": "R_FootFinger203",
    "R Toe1Nub": None,
    "R Toe2": "R_FootFinger3",
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
    "LUpArmTwist": None,  # "L_UpArmTwist",

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
    "RUpArmTwist": None,  # "R_UpArmTwist",

    "R_weapon": "R_Club",

    "L_wing_00": "L_Wing1",
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

    "R_wing_00": "R_Wing1",
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


def draw_skeleton(
    skeleton: SkeletonHKX,
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


def test2010():
    """Confirm I can still read and write 2010 HKX animation files..."""
    from soulstruct import PTDE_PATH
    ptde_2230 = Binder(PTDE_PATH + "/chr/c2230.anibnd")
    anim = AnimationHKX(ptde_2230["a00_0000.hkx"])

    anim.write("test2010_anim.hkx")

    repacked = AnimationHKX("test2010_anim.hkx")
    print("Read repacked 2010 packfile successfully. Bone track 0:")
    print(repacked.get_spline_compressed_animation_data().blocks[0][0])


if __name__ == '__main__':
    # new_tag_unpacker()
    # examine_asylum_erdtree_skeletons()
    # asylum_retarget_test()
    test2010()
