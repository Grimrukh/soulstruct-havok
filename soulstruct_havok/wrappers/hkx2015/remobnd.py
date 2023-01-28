"""Support for REMO binders, which each contain animation data and TAE for a single cutscene.

Adapted from Meowmaritus at:
    https://github.com/Meowmaritus/DSAnimStudio/blob/master/DSAnimStudioNETCore/RemoManager.cs

Only developed for DSR so far.
"""
from dataclasses import dataclass

from soulstruct.containers import Binder
from soulstruct.base.animations import SIBCAM
from soulstruct.base.game_file import GameFile
from soulstruct.utilities.binary import BinaryReader

from .core import RemoAnimationHKX


@dataclass(slots=True)
class RemoPart:
    """Manages `MSB` part name and animation data for a single `RemoCut`."""


@dataclass(slots=True)
class RemoCut:
    """Data for a single continuous camera cut in a cutscene."""
    name: str  # e.g. 'cut0050'
    animation: RemoAnimationHKX
    sibcam: SIBCAM
    collisions: list[str]  # list of collision names whose draw groups apply in this cut  # TODO: not display groups?
    other_blocks: list[int]  # list of other map blocks referenced in this cut (if applicable)


class RemoBND(GameFile):
    """Manages HKX files inside a `remobnd[.dcx]` binder and allows easy access to animation data for the corresponding
    MSB parts used in the cutscene.

    Each 'cutXXXX' subfolder in the binder contains HKX and SIBCAM animation data for a single continuous camera cut
    within the cutscene, held here in `RemoCut` instances.
    """

    cutscene_name: str  # e.g. 'scn100100'
    parts: dict[str, RemoPart]  # TODO: should go in `RemoCut`? or cached here for multiple cuts? or both?
    cuts: list[RemoCut]

    def unpack(self, reader: BinaryReader, **kwargs):
        remobnd = Binder(reader)
        for hkx_entry in remobnd.find_entries_matching_name(r"a0020\.hkx"):
            hkx = RemoAnimationHKX(hkx_entry)
            hkx.spline_to_interleaved()
            print(hkx_entry.name)
            world_transforms = hkx.get_all_part_world_space_transforms_in_frame("c5260_0000", 0)
            for bone, transform in world_transforms.items():
                print(f"{bone}: {transform}")

    def pack(self, **kwargs) -> bytes:
        pass

    # def load_cut(self, name: str, hkx: AnimationHKX, sibcam: SIBCAM) -> RemoCut:

    @property
    def map_area(self):
        return int(self.cutscene_name[3:5])

    @property
    def map_block(self):
        return int(self.cutscene_name[5:7])

    @property
    def map_name(self):
        return f"{self.map_area}_{self.map_block}_00_00"
