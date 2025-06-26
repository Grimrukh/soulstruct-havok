from contextlib import redirect_stdout
from pathlib import Path

from soulstruct.utilities.window import SmartFrame

from soulstruct.havok.scripts import scale_dsr_character


class ResizeWindow(SmartFrame):

    _DEFAULT_PATH_CFG = Path(__file__).parent / "default_chr_path.cfg"
    _LOG_PATH = Path(__file__).parent / "resizer.log"

    def __init__(self):
        super().__init__(window_title="DSR Character Resizer")

        with self.set_master(padx=20, pady=10, auto_rows=0, grid_defaults={"pady": 5, "sticky": "e"}):
            self.chr_path = self.Entry(label="`chr` folder path:", initial_text=self._default_chr_path, width=50).var
            self.model_id = self.Entry(label="Model ID:", integers_only=True).var
            self.scale = self.Entry(label="Scale:", numbers_only=True)
            self.prefer_bak = self.Checkbutton(label="Prefer '.bak' sources:").var
            self.Button(text="RESIZE", label_font_size=24, bg="#822", width=20, command=self.resize)

        self.set_geometry()

    def resize(self):
        chr_path = self.chr_path.get()
        self._default_chr_path = chr_path
        with self._LOG_PATH.open("w") as log_f:
            with redirect_stdout(log_f):
                scale_dsr_character(
                    dsr_chr_path=chr_path,
                    model_id=int(self.model_id.get()),
                    scale_factor=float(self.scale.get()),
                    prefer_bak=self.prefer_bak.get()
                )

    @property
    def _default_chr_path(self) -> str:
        return "" if not self._DEFAULT_PATH_CFG.exists() else self._DEFAULT_PATH_CFG.read_text().strip("\n")

    @_default_chr_path.setter
    def _default_chr_path(self, chr_path: str):
        self._DEFAULT_PATH_CFG.write_text(chr_path + "\n")


if __name__ == '__main__':
    ResizeWindow().wait_window()
