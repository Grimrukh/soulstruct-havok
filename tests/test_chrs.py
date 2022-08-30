from pathlib import Path

from soulstruct_havok.hkx2015 import scale_chrbnd, scale_anibnd

GAME_CHR_PATH = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/chr")


if __name__ == '__main__':
    # Testing Ornstein scaling for cloth physics.
    scale_chrbnd(GAME_CHR_PATH / "c5270.chrbnd.dcx", 5.0)
    scale_anibnd(GAME_CHR_PATH / "c5270.anibnd.dcx", 5.0)
