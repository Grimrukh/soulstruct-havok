"""Call `mopper.exe` (compiled with Havok 2012) to generate MOPP code for collision meshes."""
import logging
import subprocess as sp
import tempfile
from pathlib import Path

from soulstruct.utilities.files import read_json

from soulstruct.havok.utilities.files import SOULSTRUCT_HAVOK_PATH

_LOGGER = logging.getLogger(__name__)
_MOPPER_PATH = SOULSTRUCT_HAVOK_PATH("havok/resources/mopper.exe")


def mopper(input_lines: list[str], mode: str) -> dict:
    if mode not in {"-ccm", "-msm", "-esm"}:
        raise ValueError("`mode` must be -ccm, -msm, or -esm.")
    input_text = "\n".join(input_lines) + "\n"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        mopper_input = tmp_path / "mopper_input.txt"
        mopp_output = tmp_path / "mopp.json"

        mopper_input.write_text(input_text)

        _LOGGER.debug("Running mopper to generated Havok Collision MOPP code...")
        try:
            result = sp.run(
                [str(_MOPPER_PATH), mode, str(mopper_input)],
                cwd=tmp_dir,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
                check=True,
            )
        except sp.CalledProcessError as ex:
            stderr_output = ex.stderr.decode(errors="replace").strip()
            raise RuntimeError(
                f"`mopper.exe` did not run successfully. Return code: {ex.returncode}\nStderr: {stderr_output}"
            )

        if not mopp_output.exists():
            raise FileNotFoundError("`mopper.exe` ran successfully but did not produce `mopp.json`.")

        return read_json(mopp_output)
