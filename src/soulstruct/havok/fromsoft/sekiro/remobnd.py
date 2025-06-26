"""Support for REMO binders, which each contain animation data and TAE for a single cutscene.

Adapted from Meowmaritus at:
    https://github.com/Meowmaritus/DSAnimStudio/blob/master/DSAnimStudioNETCore/RemoManager.cs

Only developed for DSR so far.
"""
__all__ = ["RemoBND", "RemoPart", "RemoCut", "RemoPartType"]

import re
import typing as tp
from dataclasses import dataclass, field
from enum import Enum

from soulstruct.containers import Binder, BinderEntry, EntryNotFoundError
from soulstruct.base.animations import SIBCAM
from soulstruct.darksouls1r.maps import MSB, MapStudioDirectory, get_map
from soulstruct.darksouls1r.maps.parts import MSBPart

from soulstruct.havok.utilities.maths import TRSTransform
from soulstruct.havok.fromsoft.base.skeleton import Bone
from .core import RemoAnimationHKX

CUT_HKX_RE = re.compile(r"^a(\d+)\.hkx")
OTHER_MAP_RE = re.compile(r"^A(\d\d)B(\d\d)_(.*)$")


class RemoPartType(Enum):
    Dummy = 0
    Player = 1
    MapPiece = 2
    Object = 3
    Character = 4
    OtherMapPiece = 5


@dataclass(slots=True)
class RemoPart:
    """Manages `MSBPart` reference and animation data for a single `RemoCut`."""
    name: str  # raw name of root bone in REMO, e.g. 'm2450B2A10', 'c5260_0000', 'd0000_0010', 'A10B02_m2350B2A10'
    map_part_name: str  # has 'AXXBXX_' prefix removed for other-map parts (empty for player/dummies)
    part_type: RemoPartType
    map_area_block: tuple[int, int]  # e.g. `(10, 2)`
    part: MSBPart | None  # `None` for dummies
    # Maps cut names to animation data for this part in that cut: lists of `{bone: TRSTransform}` dictionaries.
    cut_arma_frames: dict[str, list[dict[str, TRSTransform]]]


@dataclass(slots=True)
class RemoCut:
    """Data for a single continuous camera cut in a cutscene."""
    CHR_ROOT_BONE_NAME: tp.ClassVar[str] = "master"

    name: str  # e.g. 'cut0050'
    animation: RemoAnimationHKX
    sibcam: SIBCAM

    # PART LISTS
    player: RemoPart | None = None
    map_pieces: list[RemoPart] = field(default_factory=list)
    other_map_pieces: list[RemoPart] = field(default_factory=list)  # from other map blocks' MSBs
    characters: list[RemoPart] = field(default_factory=list)
    objects: list[RemoPart] = field(default_factory=list)
    dummies: list[RemoPart] = field(default_factory=list)  # 'd0000_0010' entities in HKX
    collision_draw_groups: set[int] = field(default_factory=set)  # TODO: not display groups...?

    def load_remo_parts(
        self,
        msbs: dict[tuple[int, int], MSB],
        main_map_area_block: tuple[int, int],
        existing_remo_parts: dict[str, RemoPart],
    ):
        """Look up part names in appropriate MSB and create `RemoPart` instances (sorted by part subtype) with their
        bones and animation tracks for this cut (and visibility from collisions).

        Supports cutscenes that reference Map Pieces in other MSBs (which are always in the same area, but should be
        keyed by `(area, block)` in `other_msbs` dictionary anyway).
        """

        all_msb_parts_by_name = {}  # type: dict[tuple[int, int], dict[str, dict[str, MSBPart]]]

        self.map_pieces = []
        self.characters = []
        self.objects = []
        self.collision_draw_groups = set()

        for remo_part_name in self.animation.get_root_bones_by_name():
            # Detect subtype of MSB part and load bones and armature space frame transforms into `RemoPart`.

            if remo_part_name == "c0000_0000":  # PLAYER
                self.player = self._create_remo_part(
                    existing_remo_parts, remo_part_name, "", RemoPartType.Player, None, main_map_area_block,
                )
                root_bone_name = self._get_root_bone_name(RemoPartType.Player, None, main_map_area_block)
                self._add_cut_arma_frames(self.player, root_bone_name)
                continue

            if remo_part_name.startswith("d"):
                remo_part = self._create_remo_part(
                    existing_remo_parts, remo_part_name, "", RemoPartType.Dummy, None, main_map_area_block,
                )
                # TODO: Can dummies have animation data? (would be applied to object transform)
                self.dummies.append(remo_part)
                continue

            if match := OTHER_MAP_RE.match(remo_part_name):
                # Find map piece in another MSB.
                area = int(match.group(1))
                block = int(match.group(2))
                try:
                    msb = msbs[area, block]
                except KeyError:
                    raise ValueError(f"Could not find MSB with area/block ({area}, {block}) for part {remo_part_name}.")
                map_part_name = match.group(3)
            else:
                area, block = main_map_area_block
                msb = msbs[main_map_area_block]
                map_part_name = remo_part_name  # no prefix

            msb_parts_by_name = all_msb_parts_by_name.setdefault((area, block), {})

            remo_part = None  # type: RemoPart | None
            root_bone_name = ""

            if map_part_name.startswith("c"):
                # Character or Unused Character
                msb_characters = msb_parts_by_name.setdefault(
                    "characters", {c.name: c for c in msb.characters} | {c.name: c for c in msb.dummy_characters}
                )
                if map_part_name in msb_characters:
                    character = msb_characters[map_part_name]
                    remo_part = self._create_remo_part(
                        existing_remo_parts, remo_part_name, map_part_name,
                        RemoPartType.Character, character, (area, block),
                    )
                    root_bone_name = self.CHR_ROOT_BONE_NAME
                    self.characters.append(remo_part)
            elif map_part_name.startswith("m"):
                msb_map_pieces = msb_parts_by_name.setdefault("map_pieces", {m.name: m for m in msb.map_pieces})
                if map_part_name in msb_map_pieces:
                    map_piece = msb_map_pieces[map_part_name]
                    remo_part = self._create_remo_part(
                        existing_remo_parts, remo_part_name, map_part_name,
                        RemoPartType.MapPiece, map_piece, main_map_area_block,
                    )
                    root_bone_name = f"{map_piece.model.name}A{area:02d}"
                    self.map_pieces.append(remo_part)
            elif map_part_name.startswith("o"):
                msb_objects = msb_parts_by_name.setdefault(
                    "objects", {o.name: o for o in msb.objects} | {o.name: o for o in msb.dummy_objects}
                )
                if map_part_name in msb_objects:
                    obj = msb_objects[map_part_name]
                    remo_part = self._create_remo_part(
                        existing_remo_parts, remo_part_name, map_part_name,
                        RemoPartType.Object, obj, (area, block),
                    )
                    root_bone_name = obj.model.name
                    self.objects.append(remo_part)
            elif map_part_name.startswith("h"):
                # Collisions are just used for draw groups. TODO: surely it's display groups?
                msb_collisions = msb_parts_by_name.setdefault("collisions", {c.name: c for c in msb.collisions})
                if map_part_name in msb_collisions:
                    collision = msb_collisions[map_part_name]
                    self.collision_draw_groups |= collision.draw_groups.enabled_bits
                    continue  # no RemoPart for collision
                else:
                    raise ValueError(
                        f"Part name '{map_part_name}' ({remo_part_name}) not found in MSB for ({area}, {block})."
                    )

            if remo_part is None:
                raise ValueError(f"Part name '{map_part_name}' ({remo_part_name}) not found in MSB ({area}, {block}).")

            self._add_cut_arma_frames(remo_part, root_bone_name)

    # TODO: Method that returns camera transform and a dictionary of all part armature space transforms for a given
    #  frame index. (Or just a list of all transforms, and the camera transform is the first one?)

    @staticmethod
    def _create_remo_part(
        existing_remo_parts: dict[str, RemoPart],
        remo_part_name: str,
        map_part_name: str,
        part_type: RemoPartType,
        part: MSBPart | None,
        map_area_block: tuple[int, int],
    ) -> RemoPart:
        if remo_part_name in existing_remo_parts:
            # `RemoPart` created by a previous cut in this binder. Reuse that.
            remo_part = existing_remo_parts[remo_part_name]
        else:
            # Create new `RemoPart` and cache it for future `RemoCut`s to be loaded.
            # (NOTE: This is the only place where `RemoPart` instances are actually created.)
            remo_part = RemoPart(remo_part_name, map_part_name, part_type, map_area_block, part, {})
            existing_remo_parts[remo_part_name] = remo_part
        return remo_part

    @classmethod
    def _get_root_bone_name(cls, part_type: RemoPartType, part: MSBPart | None, map_area_block: tuple[int, int]) -> str:
        if part_type in {RemoPartType.Player, RemoPartType.Dummy, RemoPartType.Character}:
            # Root bone name is 'master' (or irrelevant)
            return cls.CHR_ROOT_BONE_NAME
        if part_type in {RemoPartType.MapPiece, RemoPartType.OtherMapPiece}:
            # Root bone name is map piece model name with 'AXX' suffix.
            return f"{part.model.name}A{map_area_block[0]:02d}"
        # Object: root bone name is object model name.
        return part.model.name

    def _add_cut_arma_frames(
        self,
        remo_part: RemoPart,
        root_bone_name: str,
    ):
        part_bones = self.animation.get_part_bones(
            remo_part.name, root_bone_name=root_bone_name, bone_prefix=remo_part.map_part_name + "_"
        )

        # print(f"Getting animation frames for part {remo_part.name} (root bone name {root_bone_name})...")

        # NOTE: Some bones may not be referenced in cutscene animation data.
        arma_frames = []  # type: list[dict[str, TRSTransform]]
        bone_track_indices = {
            v: i for i, v in enumerate(self.animation.animation_container.hkx_binding.transformTrackToBoneIndices)
        }

        for frame_index in range(len(self.animation.animation_container.interleaved_data)):

            frame_local_transforms = self.animation.animation_container.interleaved_data[frame_index]
            # Only bones with tracks have keys.
            bone_world_transforms = {bone.name: TRSTransform.identity() for bone in part_bones.values()}

            def bone_local_to_world(bone: Bone, arma_transform: TRSTransform):
                try:
                    track_index = bone_track_indices[bone.index]
                except KeyError:
                    # Bone has no track (not animated). We don't recur on child bones below.
                    return
                else:
                    bone_world_transforms[bone.name] = arma_transform @ frame_local_transforms[track_index]
                # Recur on children, using this bone's just-computed world transform.
                for child_bone in bone.children:
                    bone_local_to_world(child_bone, bone_world_transforms[bone.name])

            bone_local_to_world(part_bones[root_bone_name], TRSTransform.identity())

            # Remap prefixed cutscene bone names to real part bone names (used in actual part model).
            frame = {
                part_bone_name: bone_world_transforms[bone.name]
                for part_bone_name, bone in part_bones.items()
            }
            arma_frames.append(frame)

        remo_part.cut_arma_frames[self.name] = arma_frames


class RemoBND(Binder):
    """Manages HKX files inside a `remobnd[.dcx]` binder and allows easy access to animation data for the corresponding
    MSB parts used in the cutscene.

    Each 'cutXXXX' subfolder in the binder contains HKX and SIBCAM animation data for a single continuous camera cut
    within the cutscene, held here in `RemoCut` instances.
    """

    tae_entry: BinderEntry = None
    cutscene_name: str = ""  # e.g. 'scn100100'
    # All `RemoPart` instances created for this cutscene (across all cuts). Their `cut_arma_transforms` dictionary maps
    # cut names (e.g. 'cut0050') to animation transforms for that cut, keyed by standard part bone name.
    remo_parts: dict[str, RemoPart] = field(default_factory=dict)
    cuts: list[RemoCut] = field(default_factory=list)

    # Map getter function (e.g. needed to resolve m12_00_00_01 MSB name)
    GET_MAP = staticmethod(get_map)

    def __post_init__(self):
        try:
            self.tae_entry = self.find_entry_matching_name(r".*\.tae")
        except EntryNotFoundError:
            raise ValueError("Could not find TAE file in `RemoBND` binder.")
        # Cutscene name can be detected from the binder's TAE file stem.
        self.cutscene_name = self.tae_entry.stem

        self.cuts = []
        for entry in self.entries:
            if match := CUT_HKX_RE.match(entry.name):
                cut_name = "cut" + match.group(1)
                try:
                    sibcam_entry = self.find_entry_path(f"\\{cut_name}\\camera_win32.sibcam")
                except EntryNotFoundError:
                    raise ValueError(f"Could not find SIBCAM file corresponding to cut HKX entry: {entry.name}")
                sibcam = sibcam_entry.to_binary_file(SIBCAM)
                animation = entry.to_binary_file(RemoAnimationHKX)
                animation.animation_container = animation.animation_container.to_interleaved_container()
                cut = RemoCut(cut_name, animation, sibcam)
                print(f"Loaded Remo cut: {cut_name}")
                self.cuts.append(cut)

    def load_remo_parts(self, map_studio_directory: MapStudioDirectory):
        """Use all MSBs in given `MapStudioDirectory` to load `RemoPart` instances for all MSB parts used in this
        cutscene."""
        main_map_area_block = self.get_map_area_block()
        msbs = {}  # type: dict[tuple[int, int], MSB]
        for msb_stem, msb in map_studio_directory.files.items():
            area = int(msb_stem[1:3])
            block = int(msb_stem[4:6])
            msbs[area, block] = msb
        for cut in self.cuts:
            print(f"Loading parts for Remo cut: {cut.name}")
            cut.load_remo_parts(msbs, main_map_area_block, self.remo_parts)

    def load_remo_parts_from_msb(self, msb: MSB):
        """Use given `MSB` to load `RemoPart` instances for all MSB parts used in this cutscene.

        All cutscene parts must be from `msb`, which must match the cutscene area/block. Otherwise, an error will occur.
        """
        map_area_block = self.get_map_area_block()
        msbs = {map_area_block: msb}
        for cut in self.cuts:
            print(f"Loading parts (from single MSB) for Remo cut: {cut.name}")
            cut.load_remo_parts(msbs, map_area_block, self.remo_parts)

    def get_msb_stem(self) -> str:
        try:
            game_map = self.GET_MAP(self.get_map_area_block())
        except ValueError as ex:
            raise ValueError(f"Could not find MSB stem for cutscene: {self.cutscene_name}. Error: {ex}")
        return game_map.msb_file_stem

    def get_map_area_block(self) -> tuple[int, int]:
        return int(self.cutscene_name[3:5]), int(self.cutscene_name[5:7])
