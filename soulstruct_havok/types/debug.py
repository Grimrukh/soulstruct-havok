"""Special logging state, with indentation, for packing/unpacking HKX files.

Almost certainly achieveable with the `logging` module, but I don't know how to do it.
"""
__all__ = [
    "SET_DEBUG_PRINT",
    "DEBUG_PRINT_PACK",
    "DEBUG_PRINT_UNPACK",
    "DO_NOT_DEBUG_PRINT_PRIMITIVES",
    "REQUIRE_INPUT",
    "increment_debug_indent",
    "decrement_debug_indent",
    "debug_print",
]


DEBUG_PRINT_UNPACK = False
DEBUG_PRINT_PACK = False
DO_NOT_DEBUG_PRINT_PRIMITIVES = False
REQUIRE_INPUT = False


_INDENT = 0


def SET_DEBUG_PRINT(unpack=False, pack=False):
    global DEBUG_PRINT_UNPACK, DEBUG_PRINT_PACK
    DEBUG_PRINT_UNPACK = unpack
    DEBUG_PRINT_PACK = pack


def increment_debug_indent():
    global _INDENT
    _INDENT += 4


def decrement_debug_indent():
    global _INDENT
    _INDENT -= 4


def debug_print(msg):
    print(" " * _INDENT + str(msg))
