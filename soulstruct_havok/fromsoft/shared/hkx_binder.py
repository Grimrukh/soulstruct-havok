"""Wrapper for both the hi-res and lo-res HKXBHD binders in DSR.

Only loads `MapCollisionModel` instances as they are requested, from either the `.hires` or `.lores` dict attributes.
"""
from __future__ import annotations

__all__ = [
    "HKXBHD",
    "BothResHKXBHD",
]

import typing as tp

from dataclasses import dataclass, field
from pathlib import Path

from soulstruct.containers import Binder, BinderVersion, BinderVersion4Info, EntryNotFoundError
from soulstruct.dcx import DCXType
from .map_collision import MapCollisionModel


class HKXBHD(Binder):
    """Wraps a single HKXBHD, either hi-res or lo-res. Only loads `MapCollisionModel` instances as they are requested by
    the `get_hkx()` method.

    Any loaded HKX instances in the `.hkxs` attribute will be saved to the Binder's entries when it is written.
    """

    # Override defaults.
    version: BinderVersion = BinderVersion.V3
    v4_info: BinderVersion4Info | None = None
    is_split_bxf: bool = True
    dcx_type: DCXType = DCXType.Null  # no DCX compression on binder (but on HKX entries)

    map_stem: str = ""
    hkxs: dict[str, MapCollisionModel] = field(default_factory=dict)  # model stems only (e.g. 'h1000B1A10') -> `HKX`

    def get_hkx(self, hkx_stem: str):
        """Load `MapCollisionModel` instance from this `HKXBHD` if it was loaded before, otherwise return `None`."""
        hkx_stem = hkx_stem.removesuffix(".dcx").removesuffix(".hkx")  # clean up suffixes
        return self.hkxs.setdefault(
            hkx_stem,
            self.find_entry_name(f"{hkx_stem}.hkx.dcx").to_binary_file(MapCollisionModel)
        )

    def set_hkx(self, hkx_stem: str, hkx: MapCollisionModel):
        """Explicitly set the `MapCollisionModel` instance for the given stem, e.g. to replace whatever is loaded."""
        self.hkxs[hkx_stem] = hkx

    def load_all(self, overwrite=False):
        """Load all HKX entries from this HKXBHD."""
        for entry in self.entries:
            if entry.name.endswith(".hkx.dcx"):
                hkx_stem = entry.name[:-8]  # remove '.hkx.dcx'
                if overwrite or hkx_stem not in self.hkxs:
                    self.hkxs[hkx_stem] = entry.to_binary_file(MapCollisionModel)

    def entry_autogen(self):
        """Overwrite Binder entries from loaded `HKX` instances."""
        for hkx_stem, hkx in self.hkxs.items():
            hkx_stem = hkx_stem.removesuffix(".dcx").removesuffix(".hkx")
            self.set_default_entry(
                self.get_hkx_entry_path(hkx_stem), new_id=len(self.entries), new_flags=0x2
            ).set_from_binary_file(hkx)

        # Sort all final entries.
        self.auto_enumerate_entries(sort_key=lambda e: e.name)

    def get_hkx_entry_path(self, hkx_stem: str) -> str:
        """Get full Binder entry path of HKX from just the model stem."""

        if not self.map_stem:
            if self.path:
                map_stem = "m" + self.path.name.split(".")[0][1:]
            else:
                raise ValueError(
                    "HKXBHD must have a `map_stem` (or `path` whose stem can be used) for HKX entry paths."
                )
        else:
            map_stem = self.map_stem

        return f"{map_stem}\\{hkx_stem}.hkx.dcx"  # has DCX


@dataclass(slots=True)
class BothResHKXBHD:
    """Wraps hi-res and lo-res `HKXBHD` instances from a particular DSR map."""

    hi_res: HKXBHD
    lo_res: HKXBHD
    path: Path | None = None

    @classmethod
    def from_map_path(cls, map_path: Path | str) -> tp.Self:
        """Will raise a `FileNotFoundError` if (half of) either Binder file is missing."""
        map_path = Path(map_path)
        hi_res_path = Path(map_path, f"h{map_path.name[1:]}.hkxbhd")
        lo_res_path = Path(map_path, f"l{map_path.name[1:]}.hkxbhd")
        return cls(HKXBHD.from_path(hi_res_path), HKXBHD.from_path(lo_res_path), path=map_path)

    @classmethod
    def from_both_paths(cls, hi_res_path: Path | str, lo_res_path: Path | str, map_path: Path | str = None) -> tp.Self:
        """Will raise a `FileNotFoundError` if (half of) either Binder file is missing."""
        hi_res_path = Path(hi_res_path)
        lo_res_path = Path(lo_res_path)
        map_path = Path(map_path) if map_path else hi_res_path.parent
        return cls(HKXBHD.from_path(hi_res_path), HKXBHD.from_path(lo_res_path), path=map_path)

    def get_hi_hkx(self, hkx_stem: str) -> MapCollisionModel:
        return self.hi_res.get_hkx(hkx_stem)

    def get_lo_hkx(self, hkx_stem: str) -> MapCollisionModel:
        return self.lo_res.get_hkx(hkx_stem)

    def get_both_hkx(
        self, hkx_stem: str, allow_missing_hi=False, allow_missing_lo=False
    ) -> tuple[MapCollisionModel | None, MapCollisionModel | None]:
        """Get both HKX, with the option to permit either or both (not recommended) to be missing."""
        if hkx_stem.startswith(("h", "l")):
            hkx_stem = hkx_stem[1:]
        try:
            hi_res = self.get_hi_hkx(f"h{hkx_stem}")
        except EntryNotFoundError:
            if allow_missing_hi:
                hi_res = None
            else:
                raise
        try:
            lo_res = self.get_lo_hkx(f"l{hkx_stem}")
        except EntryNotFoundError:
            if allow_missing_lo:
                lo_res = None
            else:
                raise

        return hi_res, lo_res

    def get_both_res_dict(self) -> dict[str, tuple[MapCollisionModel | None, MapCollisionModel | None]]:
        """Return a list of all pairs of matching LOADED hi-res and lo-res collisions, including single-res."""
        pair_dict = {}
        for hi_name, hi_hkx in self.hi_res.hkxs.items():
            lo_name = f"l{hi_name[1:]}"
            if lo_name in self.lo_res.hkxs:
                pair_dict[hi_name[1:]] = (hi_hkx, self.lo_res.hkxs[lo_name])
            else:
                pair_dict[hi_name[1:]] = (hi_hkx, None)
        for lo_name, lo_hkx in self.lo_res.hkxs.items():
            if lo_name[1:] in pair_dict:
                continue  # already found from matching hi-res
            pair_dict[lo_name[1:]] = (None, lo_hkx)
        return {k: pair_dict[k] for k in sorted(pair_dict)}

    def get_both_res_entries_dict(self) -> dict[str, tuple[str | None, str | None]]:
        """Return a list of all pairs of matching hi-res and lo-res ENTRY NAMES, including single-res."""
        pair_dict = {}
        hi_entry_names = self.hi_res.get_entry_names()
        lo_entry_names = self.lo_res.get_entry_names()
        for hi_name in hi_entry_names:
            lo_name = f"l{hi_name[1:]}"
            if lo_name in lo_entry_names:
                pair_dict[hi_name[1:]] = (hi_name, lo_name)
            else:
                pair_dict[hi_name[1:]] = (hi_name, None)
        for lo_name in lo_entry_names:
            if lo_name[1:] in pair_dict:
                continue  # already found from matching hi-res
            pair_dict[lo_name[1:]] = (None, lo_name)
        return {k: pair_dict[k] for k in sorted(pair_dict)}

    def write_to_map_path(self, map_path: Path | str = None):
        path = Path(map_path) if map_path else self.path
        if not path:
            raise ValueError("No map path provided or stored in instance.")
        written = []
        written.extend(self.hi_res.write(path / f"h{path.name[1:]}.hkxbhd"))
        written.extend(self.lo_res.write(path / f"l{path.name[1:]}.hkxbhd"))
        return written
