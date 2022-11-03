"""Call `mopper.exe` (compiled with Havok 2012) to generate MOPP code for collision meshes."""
import logging
import subprocess as sp
from pathlib import Path

from soulstruct.utilities.files import read_json

_LOGGER = logging.getLogger(__name__)
_MOPPER_PATH = Path(__file__).parent / "../resources/mopper.exe"


def mopper(input_lines: list[str], mode: str) -> dict:
    if mode not in {"-ccm", "-msm", "-esm"}:
        raise ValueError("`mode` must be -ccm, -msm, or -esm.")
    input_text = "\n".join(input_lines) + "\n"
    # print(input_text)
    mopper_input = Path("~/AppData/Local/Temp/mopper_input.txt").expanduser()
    mopp_output = Path("~/AppData/Local/Temp/mopp.json").expanduser()
    with mopper_input.open("w") as f:
        f.write(input_text)
    _LOGGER.info("Running mopper...")
    try:
        sp.run([str(_MOPPER_PATH), mode, str(mopper_input)], cwd=str(mopper_input.parent), stdout=sp.PIPE, check=True)
    except sp.CalledProcessError as ex:
        raise RuntimeError(f"`mopper.exe` did not run successfully. Return code: {ex.returncode}")
    if not mopp_output.exists():
        raise FileNotFoundError("`mopper.exe` did not produce `mopp.json`.")
    return read_json(mopp_output)
