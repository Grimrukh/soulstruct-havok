"""Call `mopper.exe` (compiled with Havok 2012) to generate MOPP code for collision meshes."""
import logging
import os
import subprocess as sp
from pathlib import Path

from soulstruct.utilities.files import read_json

_LOGGER = logging.getLogger(__name__)
_MOPPER_PATH = Path(__file__).parent / "../resources/mopper.exe"


def mopper(input_lines: list[str], mode: str) -> dict:
    if mode not in {"-ccm", "-msm", "-esm"}:
        raise ValueError("`mode` must be -ccm, -msm, or -esm.")
    if Path("mopp.json").exists():
        os.remove("mopp.json")
    input_text = "\n".join(input_lines) + "\n"
    # print(input_text)
    Path("mopper_input.txt").write_text(input_text)
    _LOGGER.info("Running mopper...")
    sp.call([str(_MOPPER_PATH), mode, "mopper_input.txt"])
    if not Path("mopp.json").exists():
        raise FileNotFoundError("Mopper did not produce `mopp.json`.")
    return read_json("mopp.json")
