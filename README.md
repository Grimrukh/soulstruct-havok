# soulstruct-havok
Extra Havok classes and tools for [Soulstruct](https://github.com/Grimrukh/soulstruct).

This is a namespace extension package for the `soulstruct` namespace. Once installed, you can import its contents
from `soulstruct.havok`.

The central class is `HKX`, which is a very general class that can be used to read/write all supported Havok files
(most of which use the `.hkx` extension).

Subclasses of `HKX` that target specific games and file types (map collision, character collision, animation, etc.) are
available in the `soulstruct.havok.fromsoft` modules.