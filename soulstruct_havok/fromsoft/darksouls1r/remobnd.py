"""Support for REMO binders, which each contain animation data and TAE for a single cutscene.

Adapted from Meowmaritus at:
    https://github.com/Meowmaritus/DSAnimStudio/blob/master/DSAnimStudioNETCore/RemoManager.cs

Only developed for DSR so far.
"""
__all__ = [
    "RemoBND",
    "RemoPart",
    "RemoPartAnimationFrame",
    "RemoCut",
    "RemoPartType",
]

import logging
import re
from dataclasses import dataclass, field
from enum import StrEnum

from soulstruct.containers import Binder, BinderEntry, EntryNotFoundError
from soulstruct.base.animations import SIBCAM
from soulstruct.darksouls1r.maps import MSB, MapStudioDirectory, get_map
from soulstruct.darksouls1r.maps.parts import MSBPart

from soulstruct_havok.utilities.maths import TRSTransform
from .core import RemoAnimationHKX, Bone

_LOGGER = logging.getLogger("soulstruct_havok")

CUT_HKX_RE = re.compile(r"^a(\d+)\.hkx")
OTHER_MAP_RE = re.compile(r"^A(\d\d)B(\d\d)_(.*)$")


class RemoPartType(StrEnum):
    """For Soulstruct use only. Part types are fully detected from their names in `RemoCut` HKX files."""
    Dummy = "d"  # animated generic reference point for use by cutscene TAE
    Player = "c0000_0000"
    MapPiece = "m"
    Object = "o"  # includes `MSBDummyObject` Parts
    Character = "c"  # includes `MSBDummyCharacter` Parts
    Collision = "h"  # only used for their display groups (I assume)


@dataclass(slots=True)
class RemoPartAnimationFrame:
    """Bundles root motion and bone transforms for a single frame of a `RemoPart` animation (within a `RemoCut`).

    Bone transforms are already in Armature space, not local Bone space. Root motion is in WORLD space (or map space,
    at least, in later games).
    """
    root_motion: TRSTransform  # NOTE: better than standard root motion, which only supports vertical axis rotation
    bone_transforms: dict[str, TRSTransform]


@dataclass(slots=True)
class RemoPart:
    """Manages `MSBPart` reference and animation data for a single `RemoCut`."""
    name: str  # raw name of root bone in REMO, e.g. 'm2450B2A10', 'c5260_0000', 'd0000_0010', 'A10B02_m2350B2A10'
    map_part_name: str  # has 'AXXBXX_' prefix removed for other-map parts (empty for player/dummies)
    part_type: RemoPartType
    map_area_block: tuple[int, int]  # e.g. `(10, 2)`
    part: MSBPart | None  # `None` for dummies

    # Maps cut names to animation data for this part in that cut.
    cut_arma_frames: dict[str, list[RemoPartAnimationFrame]]

    def __repr__(self) -> str:
        part_repr = f"{self.part.cls_name}(\"{self.part.name}\")" if self.part else "None"
        cuts_repr = "".join(
            f"\n        \"{cut_name}\": <{len(frames)} frames>,"
            for cut_name, frames in self.cut_arma_frames.items()
        )
        lines = [f"RemoPart(", f"    \"{self.name}\","]
        if self.map_part_name != self.name:
            lines.append(f"    map_part_name=\"{self.map_part_name}\",")
        lines.extend([
            f"    part_type=RemoPartType.{self.part_type.name},",
            f"    map_area_block={self.map_area_block},",
            f"    part={part_repr},",
            f"    cut_arma_frames={{"
            f"        {cuts_repr}\n"
            f"    }},",
            f")",
        ])
        return "\n".join(lines)

    def get_cut_repr(self, cut_name: str) -> str:
        """Abbreviated repr specific to `cut_name`."""
        return (
            f"RemoPart(\"{self.name}\", \"{self.map_part_name}\", {self.part_type.name}, "
            f"<{len(self.cut_arma_frames[cut_name])} frames>"
        )


@dataclass(slots=True)
class RemoCut:
    """Data for a single continuous camera cut in a cutscene."""
    name: str  # e.g. 'cut0050'
    animation: RemoAnimationHKX
    sibcam: SIBCAM

    # Dictionary maps `RemoPartType` enum to lists of corresponding `RemoPart` instances.
    remo_parts: dict[RemoPartType, list[RemoPart]] = field(
        default_factory=lambda: {part_type: [] for part_type in RemoPartType}
    )

    @property
    def player(self) -> RemoPart | None:
        """Shortcut for getting the lone `RemoPart` of type `RemoPartType.Player` (usually present)."""
        try:
            return self.remo_parts[RemoPartType.Player][0]
        except IndexError:
            return None

    def get_collision_display_groups(self) -> set[int]:
        """Get all display groups enabled by collisions in this cutscene.

        Will raise a ValueError if any collision part has no `MSBPart` reference.
        """
        display_groups = set()
        for collision in self.remo_parts[RemoPartType.Collision]:
            if collision.part:
                display_groups |= collision.part.display_groups.enabled_bits
            else:
                raise ValueError(f"Collision part {collision.name} has no `MSBPart` reference in `RemoCut`.")
        return display_groups

    def load_remo_parts(
        self,
        main_map_area_block: tuple[int, int],
        all_remo_parts: dict[RemoPartType, dict[str, RemoPart]],
        msbs: dict[tuple[int, int], MSB] | None = None,
        allow_missing_msb_parts=False,
    ):
        """Parse the cut's HKX animation data into `RemoPart` instances for each part used in the cutscene.

        Converts animation data to Armature space, and stores root motion from the root bones (named for the Part). Also
        handles 'AXXBXX' other-map prefixes and stores that with the `RemoPart`. Uses existing `RemoPart` instances if
        present in `all_remo_parts` dictionary (just adds this cut's animation data to them).

        If `msbs` is given, will also find and attach the corresponding `MSBPart` instance to the `RemoPart`. If a
        `RemoPart` cannot be found in any of the given `msbs`, a `ValueError` will be raised unless
        `allow_missing_msb_parts` is True (in which case a warning will be logged).
        """

        if msbs:
            all_msbs_parts_by_name = {}
            for (area, block), msb in msbs.items():
                all_characters = {c.name: c for c in msb.characters} | {c.name: c for c in msb.dummy_characters}
                all_objects = {o.name: o for o in msb.objects} | {o.name: o for o in msb.dummy_objects}
                msb_parts_by_name = {
                    RemoPartType.Player: {p.name: p for p in msb.player_starts},
                    RemoPartType.MapPiece: {m.name: m for m in msb.map_pieces},
                    RemoPartType.Character: all_characters,
                    RemoPartType.Object: all_objects,
                    RemoPartType.Collision: {o.name: o for o in msb.collisions},
                }
                all_msbs_parts_by_name[area, block] = msb_parts_by_name
        else:
            all_msbs_parts_by_name = {}

        for remo_part_name in self.animation.get_root_bones_by_name():
            # Detect subtype of MSB part and load bones and armature space frame transforms into `RemoPart`.

            if match := OTHER_MAP_RE.match(remo_part_name):
                # Find MSB Part in another MSB (assumed to be loaded). Doesn't have to be a Map Piece.
                area, block = int(match.group(1)), int(match.group(2))
                msb_part_name = match.group(3)
                if msb_part_name.startswith(RemoPartType.Dummy):
                    _LOGGER.warning(
                        f"RemoPart Dummy '{remo_part_name}' appears to belong to another map. If valid, this has not "
                        f"been seen before (by Grimrukh) and so may not be handled correctly."
                    )
            else:
                # Use cutscene's default MSB and assume RemoPart name is the same as the Map Part name.
                area, block = main_map_area_block
                msb_part_name = remo_part_name  # no prefix

            for remo_part_type in RemoPartType:

                if remo_part_name in all_remo_parts.get(remo_part_type, {}):
                    # Load this `RemoCut`'s frame data into existing `RemoPart` instance.
                    remo_part = all_remo_parts[remo_part_type][remo_part_name]
                    self.remo_parts[remo_part.part_type].append(remo_part)
                    self._add_cut_arma_frames(remo_part)
                    break

                # NOTE: Order of `RemoPartType` is important here, so player 'c0000_0000' is checked before generic
                # Character prefix 'c'.
                if msb_part_name.startswith(remo_part_type):

                    if all_msbs_parts_by_name:
                        if (area, block) not in all_msbs_parts_by_name:
                            msg = (f"Could not find MSB for area/block ({area}, {block}) in `msbs` (used by RemoPart "
                                   f"'{remo_part_name}').")
                            if allow_missing_msb_parts:
                                _LOGGER.warning(msg)
                            else:
                                raise ValueError(msg)
                        msb_parts = all_msbs_parts_by_name[area, block][remo_part_type]
                        try:
                            part = msb_parts[msb_part_name]
                        except KeyError:
                            msg = (
                                f"Could not find MSB part '{msb_part_name}' of type {remo_part_type} in MSB for "
                                f"area/block ({area}, {block}), used by RemoPart '{remo_part_name}'."
                            )
                            if allow_missing_msb_parts:
                                _LOGGER.warning(msg)
                                part = None
                            else:
                                raise ValueError(msg)
                    else:
                        part = None

                    remo_part = RemoPart(remo_part_name, msb_part_name, remo_part_type, (area, block), part, {})
                    self.remo_parts[remo_part_type].append(remo_part)
                    all_remo_parts.setdefault(remo_part_type, {})[remo_part_name] = remo_part
                    self._add_cut_arma_frames(remo_part)
                    break
            else:
                raise ValueError(
                    f"Could not detect a supported `RemoPart` type from HKX root bone name: {remo_part_name}"
                )

    def __repr__(self) -> str:
        lines = ["RemoCut(", f"    \"{self.name}\","]
        if self.player:
            lines.append(f"    player={self.player.get_cut_repr(self.name)},")
        for remo_part_list_name in ["map_pieces", "characters", "objects", "dummies", "collisions"]:
            remo_part_list = getattr(self, remo_part_list_name)
            if remo_part_list:
                lines.append(f"    {remo_part_list_name}=[")
                for rp in remo_part_list:
                    lines.append(f"        {rp.get_cut_repr(self.name)},")
                lines.append(f"    ],")
        lines.append(")")
        return "\n".join(lines)

    # TODO: Method that returns camera transform and a dictionary of all part armature space transforms for a given
    #  frame index. (Or just a list of all transforms, and the camera transform is the first one?)

    def _add_cut_arma_frames(self, remo_part: RemoPart):
        """Add Armature-space frame transforms (`list[dict[bone_name: TRSTransform]]`) to `remo_part` for this cut."""

        # To keep bone names unique, the cut HKX animation data uses the Part name (possibly prefixed with 'AXXBXX_') as
        # a prefix for every child bone name, with root motion stored under the root Part bone.
        # TODO: Is the other-map prefix included in every bone prefix as well? Or just the root bone?
        #  This call suggests the latter... but that would permit object name clashes between maps?
        remo_part_root_bone, part_bones = self.animation.get_root_and_part_bones(
            remo_part.name, bone_prefix=remo_part.map_part_name + "_"
        )

        if not self.animation.animation_container.is_interleaved:
            self.animation.animation_container = self.animation.animation_container.to_interleaved_container()

        # As always, not all FLVER bones need to be animated or referenced by the HKX animation.
        arma_frames = []  # type: list[RemoPartAnimationFrame]
        bone_track_indices = {
            bone_index: track_index
            for track_index, bone_index in enumerate(
                self.animation.animation_container.hkx_binding.transformTrackToBoneIndices
            )
        }
        remo_part_root_track_index = bone_track_indices[remo_part_root_bone.index]

        if remo_part.name == "o1303":
            pass

        for frame_local_transforms in self.animation.animation_container.interleaved_data:

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

            for part_root_bone in remo_part_root_bone.children:
                # Immediate children of `remo_part_root_bone` are the true root bones of the Part.
                bone_local_to_world(part_root_bone, TRSTransform.identity())

            # Remap prefixed cutscene bone names to real part bone names (used in actual part model).
            frame = {
                real_flver_bone_name: bone_world_transforms[bone.name]
                for real_flver_bone_name, bone in part_bones.items()
            }
            # Root motion exists as-is.
            root_motion = frame_local_transforms[remo_part_root_track_index]
            arma_frames.append(RemoPartAnimationFrame(root_motion, frame))

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
    all_remo_parts: dict[RemoPartType, dict[str, RemoPart]] = field(default_factory=dict)
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
                animation = entry.to_binary_file(RemoAnimationHKX)  # we only convert to interleaved when required
                cut = RemoCut(cut_name, animation, sibcam)
                self.cuts.append(cut)

    def load_remo_parts(self):
        """Load placeholder `RemoPart`s for each cut, without `MSB` references."""
        main_map_area_block = self.get_map_area_block()
        self.all_remo_parts = {}  # reset
        for cut in self.cuts:
            cut.load_remo_parts(main_map_area_block, self.all_remo_parts, msbs=None)

    def load_remo_parts_from_mapstudio(self, map_studio_directory: MapStudioDirectory, allow_missing_parts=False):
        """Use all MSBs in given `MapStudioDirectory` to load `RemoPart` instances for all MSB parts used in this
        cutscene."""
        main_map_area_block = self.get_map_area_block()
        msbs = {}  # type: dict[tuple[int, int], MSB]
        self.all_remo_parts = {}  # clear old/placeholder parts
        for msb_stem, msb in map_studio_directory.files.items():
            area = int(msb_stem[1:3])
            block = int(msb_stem[4:6])
            msbs[area, block] = msb
        for cut in self.cuts:
            print(f"Loading parts for Remo cut: {cut.name}")
            cut.load_remo_parts(main_map_area_block, self.all_remo_parts, msbs, allow_missing_parts)

    def load_remo_parts_from_msb(self, msb: MSB, allow_missing_parts=False):
        """Use given `MSB` to load `RemoPart` instances for all MSB parts used in this cutscene.

        All cutscene parts must be from `msb`, which must match the cutscene area/block. Otherwise, an error will occur.
        """
        map_area_block = self.get_map_area_block()
        msbs = {map_area_block: msb}
        self.all_remo_parts = {}  # clear old/placeholder parts
        for cut in self.cuts:
            print(f"Loading parts (from single MSB) for Remo cut: {cut.name}")
            cut.load_remo_parts(map_area_block, self.all_remo_parts, msbs, allow_missing_parts)

    def get_msb_stem(self) -> str:
        try:
            game_map = self.GET_MAP(self.get_map_area_block())
        except ValueError as ex:
            raise ValueError(f"Could not find MSB stem for cutscene: {self.cutscene_name}. Error: {ex}")
        return game_map.msb_file_stem

    def get_map_area_block(self) -> tuple[int, int]:
        return int(self.cutscene_name[3:5]), int(self.cutscene_name[5:7])
