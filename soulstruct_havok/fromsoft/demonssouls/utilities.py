__all__ = [
    "convert_big_to_little_endian_hkx_file",
    "convert_little_to_big_endian_hkx_file",
]

import logging
from pathlib import Path

from soulstruct_havok.core import HKX

_LOGGER = logging.getLogger("soulstruct_havok")


def convert_big_to_little_endian_hkx_file(hkx_path: Path | str, output_path: Path | str, disable_padding_option=True):
    """Demon's Souls HKX files are big-endian (PS3), but tools built using the Havok 5.5.0 SDK on PC do not natively
    support a way to read big-endian files. This function converts a big-endian HKX file to little-endian by simply
    loading and saving it.

    By default, the packfile header `padding_option` is disabled, as it is not necessary for PC tools.

    NOTE: Fortunately, we don't have to worry about the endianness of compressed animation data buffers.
    """
    hkx = HKX.from_path(hkx_path)
    if hkx.is_big_endian:
        hkx.is_big_endian = False
    else:
        raise ValueError(f"HKX file is already little-endian: {hkx_path}")

    if disable_padding_option:
        hkx.packfile_header_info.reuse_padding_optimization = 0

    hkx.write(output_path)
    _LOGGER.info(f"Converted big-endian HKX file to little-endian: {output_path}")


def convert_little_to_big_endian_hkx_file(hkx_path: Path | str, output_path: Path | str, enable_padding_option=True):
    """Opposite of above, obviously for creating functional PS3 Demon's Souls animations.

    By default, automatically sets packfile header `padding_option` to 1 as well.

    NOTE: Fortunately, we don't have to worry about the endianness of compressed animation data buffers.
    """
    hkx = HKX.from_path(hkx_path)
    if not hkx.is_big_endian:
        hkx.is_big_endian = True
    else:
        raise ValueError(f"HKX file is already big-endian: {hkx_path}")

    if enable_padding_option:
        hkx.packfile_header_info.reuse_padding_optimization = 1  # for Demon's Souls

    hkx.write(output_path)
    _LOGGER.info(f"Converted little-endian HKX file to big-endian: {output_path}")
