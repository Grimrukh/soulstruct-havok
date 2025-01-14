"""Base classes for various common Havok file types, with wrappers and variant indices for their basic contents.

Must be overridden by each Havok version to provide the correct `hk` types module.
"""
from __future__ import annotations

__all__ = ["BaseWrappedHKX"]

import abc
import logging
import typing as tp

from soulstruct_havok.core import HKX, HavokFileFormat
from soulstruct_havok.enums import PyHavokModule
from soulstruct_havok.types import hk

_LOGGER = logging.getLogger("soulstruct_havok")


HK_T = tp.TypeVar("HK_T", bound=hk)


class BaseWrappedHKX(HKX, abc.ABC):

    # Assigned for version-specific subclasses.
    HAVOK_MODULE: tp.ClassVar[PyHavokModule]

    def get_variant(self, variant_index: int, *valid_types: type[HK_T]) -> HK_T:
        """Get variant at `variant_index`, check that it is one of the given `valid_types`, and return its type."""
        variant = self.root.namedVariants[variant_index].variant
        valid_type_names_modules = [f"{t.__name__} ({t.__module__})" for t in valid_types]
        if not any(type(variant) is t for t in valid_types):
            raise TypeError(
                f"HKX variant index {variant_index} has type `{variant.__class__.__name__}` from module "
                f"`{variant.__class__.__module__}`, which is not a valid type. Valid names and modules: "
                f"{valid_type_names_modules}"
            )
        return variant

    @classmethod
    def get_version_string(cls) -> str:
        return cls.HAVOK_MODULE.get_version_string()

    @classmethod
    def get_default_hk_format(cls) -> HavokFileFormat:
        if cls.HAVOK_MODULE.get_version_string().startswith("20"):
            return HavokFileFormat.Tagfile
        return HavokFileFormat.Packfile
