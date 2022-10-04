from __future__ import annotations

from pathlib import Path

from soulstruct.config import DSR_PATH
from soulstruct_havok.utilities.maths import *

from soulstruct_havok.wrappers.hkx2015.animation_manager import AnimationManager as AnimationManagerDS1
from soulstruct_havok.wrappers.hkx2018.animation_manager import AnimationManager as AnimationManagerER

GAME_CHR_PATH = DSR_PATH + "/chr"


DSR_CHR = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/chr")
DSR_VAN_CHR = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (Vanilla Backup)/chr")
ER_CHR = Path("C:/Steam/steamapps/common/ELDEN RING (Vanilla)/Game/chr")


def do_erdtree_retarget_and_adjustment():
    print("Reading 2015 animation...")
    asylum_manager = AnimationManagerDS1.from_anibnd(DSR_VAN_CHR / "c2230.anibnd.dcx", 3000, from_bak=True)
    print("Reading 2018 animation...")
    erdtree_manager = AnimationManagerER.from_anibnd(ER_CHR / "c4810.anibnd.dcx", 3000, from_bak=True)

    asylum_manager.animations[3000].load_spline_data()
    asylum_manager.animations[3000].save_spline_data()

    print("Converting 2015 spline to interleaved...")
    asylum_manager.animations[3000].spline_to_interleaved()
    print("Converting 2018 spline to interleaved...")
    erdtree_manager.animations[3000].spline_to_interleaved()

    print("Retargeting Erdtree animation...")
    asylum_manager.auto_retarget_interleaved_animation(erdtree_manager, 3000, 3000, RETARGET)
    asylum_manager.animations[3000].scale(1.17)

    # erdtree_manager.plot_hierarchy_interleaved_translation("L_Toe0", "y", ylim=(-1, 5))
    # asylum_manager.plot_hierarchy_interleaved_translation("L Toe0", "y", ylim=(-1, 5))
    # plt.show()
    # exit()

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

    # Weapon rotation.
    asylum_manager.rotate_bone_track(
        "R_weapon",
        rotation=Quaternion.axis(0, 0, 1, 90.0),
        compensate_children=False,  # no children
    )

    # TODO: I think the calf bone (from thigh) is stretching too much during the animation. I'd like to scale it in a
    #  way that fixes its length to whatever it has in the first frame, or at least 'dulls' it, while still compensating
    #  the child foot bones.

    # Shrink gut.
    # for bone in ("a", "b", "c"):
    #     asylum_manager.transform_bone_track(
    #         bone,
    #         QsTransform(scale=0.5),
    #     )

    def match_rotation(bone_, target_):
        bone_tfs_ = asylum_manager.get_bone_interleaved_transforms(bone_)
        target_tfs_ = asylum_manager.get_bone_interleaved_transforms(target_)
        for b_, t_ in zip(bone_tfs_, target_tfs_):
            b_.rotation = t_.rotation

    # TODO: Since the parent (L Clavicle) is being rotated, LUpArmTwist comes along for the ride here, but its own
    #  rotation does not change to orbit 'L Forearm'. Kind of an artifact of these twist bones being synchronized as
    #  they are... But I don't think they stay in sync the whole time.

    asylum_manager.proper_transform_bone_track(
        "L Clavicle",
        TRSTransform(
            rotation=Quaternion.axis(0, 0, 1, 110),
            scale=0.3,
        ),
        rotate_parent=False,  # do not rotate Neck
        compensate_children=True,
        rotation_orbits_child="L UpperArm",
    )
    asylum_manager.proper_transform_bone_track(
        "L UpperArm",
        TRSTransform(
            rotation=Quaternion.axis(0, 0, 1, 45),
            scale=0.6,
        ),
        rotate_parent=True,
        compensate_children=True,
        rotation_orbits_child="L Forearm",
    )
    asylum_manager.proper_transform_bone_track(
        "LUpArmTwist",
        TRSTransform(
            scale=0.6,
        ),
        rotate_parent=True,
        compensate_children=True,
    )
    match_rotation("LUpArmTwist", "L UpperArm")

    asylum_manager.proper_transform_bone_track(
        "R Clavicle",
        TRSTransform(
            rotation=Quaternion.axis(0, 0, 1, -110),
            scale=0.3,
        ),
        rotate_parent=False,  # do not rotate Neck
        compensate_children=True,
        rotation_orbits_child="R UpperArm",
    )
    asylum_manager.proper_transform_bone_track(
        "R UpperArm",
        TRSTransform(
            rotation=Quaternion.axis(0, 0, 1, -45),
            scale=0.6,
        ),
        rotate_parent=True,
        compensate_children=True,
        rotation_orbits_child="R Forearm",
    )
    asylum_manager.proper_transform_bone_track(
        "RUpArmTwist",
        TRSTransform(
            scale=0.6,
        ),
        rotate_parent=True,
        compensate_children=True,
    )
    match_rotation("RUpArmTwist", "R UpperArm")

    # Correct thigh twists.
    match_rotation("LThighTwist", "L Thigh")
    match_rotation("RThighTwist", "R Thigh")

    window = asylum_manager.plot_interleaved_skeleton_on_frame(0, focus_bone="Neck")
    window.show()
    window.run()

    # TODO: Don't need to convert back to splines for DSAS.
    # print(f"Converting interleaved anim to spline...")
    # asylum_manager.convert_interleaved_to_spline_anim(3000)

    print("Writing into ANIBND for DSR...")
    asylum_manager.write_anim_ids_into_anibnd(
        DSR_VAN_CHR / "c2230.anibnd.dcx", 3000, from_bak=True,
        write_path=DSR_CHR / "c2230.anibnd.dcx",
    )

    print("Done.")


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
    #  However, in Asylum animations, the twist always seems to be right on top of the Thigh.
    "LThighTwist": ["~Spine1", "~Spine", "Pelvis", "L_Thigh"],
    "RThighTwist": ["~Spine1", "~Spine", "Pelvis", "R_Thigh"],

    "Spine": ["~Pelvis", "Spine", "Spine1"],
    "Spine1": "Spine2",

    "L Thigh": ["~Spine1", "~Spine", "Pelvis", "L_Thigh"],
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

    "R Thigh": ["~Spine1", "~Spine", "Pelvis", "R_Thigh"],
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
    "L ForeTwist": "L_Forearm",
    "LUpArmTwist": "L_UpperArm",

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
    "R ForeTwist": "R_Forearm",
    "RUpArmTwist": "R_UpperArm",

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


if __name__ == '__main__':
    # examine_asylum_erdtree_skeletons()
    # do_erdtree_retarget_and_adjustment()
    do_erdtree_adjustment()
    # quat_test()
