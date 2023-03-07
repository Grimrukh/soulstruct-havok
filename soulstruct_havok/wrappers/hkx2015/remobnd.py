"""Support for REMO binders, which each contain animation data and TAE for a single cutscene.

Adapted from Meowmaritus at:
    https://github.com/Meowmaritus/DSAnimStudio/blob/master/DSAnimStudioNETCore/RemoManager.cs

Only developed for DSR so far.
"""
import re
import typing as tp
from dataclasses import dataclass, field

from soulstruct.containers import Binder, BinderEntry, BinderEntryNotFoundError
from soulstruct.base.animations import SIBCAM
from soulstruct.darksouls1r.maps import MSB
from soulstruct.darksouls1r.maps.parts import MSBPart

from soulstruct_havok.utilities.maths import TRSTransform
from .file_types import RemoAnimationHKX, Bone

CUT_HKX_RE = re.compile(r"^a(\d+)\.hkx")


@dataclass(slots=True)
class RemoPart:
    """Manages `MSBPart` reference and animation data for a single `RemoCut`."""
    part_name: str  # e.g. 'c5260_0000' or 'd0000_0010'
    part: MSBPart | None  # `None` for dummies
    # Maps cut names to animation data for this part in that cut, which maps standard bone names to lists of transforms.
    cut_arma_transforms: dict[str, dict[str, list[TRSTransform]]]


@dataclass(slots=True)
class RemoCut:
    """Data for a single continuous camera cut in a cutscene."""
    ROOT_BONE_NAME: tp.ClassVar[str] = "master"

    name: str  # e.g. 'cut0050'
    animation: RemoAnimationHKX
    sibcam: SIBCAM

    # PART LISTS
    player: RemoPart | None = None
    map_pieces: list[RemoPart] = field(default_factory=list)
    other_map_pieces: list[RemoPart] = field(default_factory=list)  # TODO: Support map pieces from other map blocks.
    characters: list[RemoPart] = field(default_factory=list)
    objects: list[RemoPart] = field(default_factory=list)
    dummies: list[RemoPart] = field(default_factory=list)  # 'd0000_0010' entities in HKX
    collision_draw_groups: set[int] = field(default_factory=set)  # TODO: not display groups...?

    def load_remo_parts(self, msb: MSB, existing_remo_parts: dict[str, RemoPart]):
        """Look up part names in MSB and create `RemoPart` instances (sorted by part subtype) with their bones and
        animation tracks for this cut (and visibility from collisions).
        """

        m_names = [part.name for part in msb.map_pieces]
        c_names = [part.name for part in msb.characters]
        o_names = [part.name for part in msb.objects]
        h_names = [part.name for part in msb.collisions]
        # TODO: Support map pieces from other map blocks (would need access to `MapStudioDirectory` instance).

        self.map_pieces = []
        self.characters = []
        self.objects = []
        self.collision_draw_groups = set()

        for part_name in self.animation.get_named_root_bones():
            # Detect subtype of MSB part and load bones and armature space frame transforms into `RemoPart`.

            if part_name == "c0000_0000":  # PLAYER
                self.player = self._load_remo_part_transforms(part_name, None, existing_remo_parts)
            elif part_name in m_names:
                map_piece = msb.map_pieces[m_names.index(part_name)]
                remo_part = self._load_remo_part_transforms(part_name, map_piece, existing_remo_parts)
                self.map_pieces.append(remo_part)
            elif part_name in c_names:
                character = msb.characters[c_names.index(part_name)]
                remo_part = self._load_remo_part_transforms(part_name, character, existing_remo_parts)
                self.map_pieces.append(remo_part)
            elif part_name in o_names:
                obj = msb.objects[o_names.index(part_name)]
                remo_part = self._load_remo_part_transforms(part_name, obj, existing_remo_parts)
                self.objects.append(remo_part)
            elif part_name in h_names:
                collision = msb.collisions[h_names.index(part_name)]
                self.collision_draw_groups |= collision.draw_groups.enabled_bits
                remo_part = self._load_remo_part_transforms(part_name, collision, existing_remo_parts)
                self.objects.append(remo_part)
            elif part_name.startswith("d"):
                remo_part = self._load_remo_part_transforms(part_name, None, existing_remo_parts)
                self.dummies.append(remo_part)
            else:
                raise ValueError(f"Part name '{part_name}' not found in MSB.")

    # TODO: Method that returns camera transform and a dictionary of all part armature space transforms for a given
    #  frame index. (Or just a list of all transforms, and the camera transform is the first one?)

    def _load_remo_part_transforms(
        self,
        part_name: str,
        part: MSBPart | None,
        existing_remo_parts: dict[str, RemoPart],
    ) -> RemoPart:
        if part_name in existing_remo_parts:
            # `RemoPart` created by a previous cut in this binder. Reuse that.
            remo_part = existing_remo_parts[part_name]
        else:
            # Create new `RemoPart` and cache it for future `RemoCut`s to be loaded.
            # (NOTE: This is the only place where `RemoPart` instances are actually created.)
            remo_part = RemoPart(part_name, part, {})
            existing_remo_parts[part_name] = remo_part

        # TODO: Check that bones that aren't even animated still have tracks. (They just wouldn't be in `mapping`
        #  otherwise, presumably.)
        part_bones = self.animation.get_part_bones(part_name, root_bone_name=self.ROOT_BONE_NAME)

        print(f"Getting animation frames for part {part_name}...")

        arma_transforms = {bone_name: [] for bone_name in part_bones} | {self.ROOT_BONE_NAME: []}
        track_bone_indices = self.animation.animation_container.animation_binding.transformTrackToBoneIndices

        for frame_index in range(len(self.animation.animation_container.interleaved_data)):
            frame_local_transforms = self.animation.animation_container.interleaved_data[frame_index]
            bone_world_transforms = {bone.name: TRSTransform.identity() for bone in part_bones.values()}

            def bone_local_to_world(bone: Bone, arma_transform: TRSTransform):
                track_index = track_bone_indices.index(bone.index)
                bone_world_transforms[bone.name] = arma_transform @ frame_local_transforms[track_index]
                # Recur on children, using this bone's just-computed world transform.
                for child_bone in bone.children:
                    bone_local_to_world(child_bone, bone_world_transforms[bone.name])

            bone_local_to_world(part_bones[self.ROOT_BONE_NAME], TRSTransform.identity())
            for part_bone_name, bone in part_bones.items():
                arma_transforms[part_bone_name].append(bone_world_transforms[bone.name])

        remo_part.cut_arma_transforms[self.name] = arma_transforms
        return remo_part


@dataclass(slots=True)
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

    def __post_init__(self):
        try:
            self.tae_entry = self.find_entry_matching_name(r".*\.tae")
        except BinderEntryNotFoundError:
            raise ValueError("Could not find TAE file in `RemoBND` binder.")
        # Cutscene name can be detected from the binder's TAE file stem.
        self.cutscene_name = self.tae_entry.stem

        self.cuts = []
        for entry in self.entries:
            if match := CUT_HKX_RE.match(entry.name):
                cut_name = "cut" + match.group(1)
                try:
                    sibcam_entry = self.entries_by_path[f"\\{cut_name}\\camera_win32.sibcam"]
                except KeyError:
                    raise KeyError(f"Could not find SIBCAM file corresponding to cut HKX entry: {entry.name}")
                sibcam = sibcam_entry.to_game_file(SIBCAM)
                animation = entry.to_game_file(RemoAnimationHKX)
                animation.animation_container.spline_to_interleaved()
                cut = RemoCut(cut_name, animation, sibcam)
                print(f"Loaded Remo cut: {cut_name}")
                self.cuts.append(cut)

    def load_remo_parts(self, msb: MSB):
        """Use given `MSB` to load `RemoPart` instances for all MSB parts used in this cutscene."""
        # TODO: Should actually take a `MapStudioDirectory` so other maps' map pieces can be loaded too.
        for cut in self.cuts:
            print(f"Loaded parts for Remo cut: {cut.name}")
            cut.load_remo_parts(msb, self.remo_parts)

    @property
    def map_area(self):
        return int(self.cutscene_name[3:5])

    @property
    def map_block(self):
        return int(self.cutscene_name[5:7])

    @property
    def map_name(self):
        return f"{self.map_area}_{self.map_block}_00_00"
