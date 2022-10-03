import abc
import typing as tp
from types import ModuleType

from soulstruct.base.game_file import GameFile
from soulstruct.containers.dcx import DCXType
from soulstruct_havok.core import HKX
from soulstruct_havok.types import hk
from soulstruct_havok.types.hk2010 import hkRootLevelContainer as hk2010RootLevelContainer
from soulstruct_havok.types.hk2014 import hkRootLevelContainer as hk2014RootLevelContainer
from soulstruct_havok.types.hk2015 import hkRootLevelContainer as hk2015RootLevelContainer
from soulstruct_havok.types.hk2018 import hkRootLevelContainer as hk2018RootLevelContainer

ROOT_LEVEL_CONTAINER_TYPING = tp.Union[
    hk2010RootLevelContainer,
    hk2014RootLevelContainer,
    hk2015RootLevelContainer,
    hk2018RootLevelContainer,
]


class BaseWrapperHKX(HKX, abc.ABC):
    """Base class for various wrappers designed for specific types of HKX files across different Havok versions."""

    root: ROOT_LEVEL_CONTAINER_TYPING
    TYPES_MODULE: ModuleType = None  # must be mixed in by subclasses

    def __init__(
        self,
        file_source: GameFile.Typing = None,
        dcx_type: None | DCXType = DCXType.Null,
        compendium: tp.Optional[HKX] = None,
        hk_format="",
    ):
        super().__init__(file_source, dcx_type=dcx_type, compendium=compendium, hk_format=hk_format)

        if self.root:
            # Create shortcut class attributes if data is present. Use `set_root()` later to do this.
            self.create_attributes()

    @abc.abstractmethod
    def create_attributes(self):
        """Called by constructor to assign various convenience attributes, which should be type-hinted in class body."""

    def get_variant_index(self, variant_index: int, check_type: str | tp.Type[hk] = None) -> tp.Any:
        variant = self.root.namedVariants[variant_index].variant
        if isinstance(check_type, str):
            if variant.__class__.__name__ != check_type:
                raise TypeError(
                    f"HKX variant index {variant_index} did not have asserted type name {check_type}."
                )
        elif check_type and not isinstance(variant, check_type):
            raise TypeError(
                f"HKX variant index {variant_index} did not have asserted type {check_type.__name__}."
            )
        return variant

    def set_variant_attribute(self, attr_name: str, hk_type: tp.Type[hk], variant_index: int):
        variant = self.root.namedVariants[variant_index].variant
        if not isinstance(variant, hk_type):
            raise TypeError(
                f"HKX variant index {variant_index} did not have type {hk_type.__name__} ({variant.__class__.__name__})"
            )
        setattr(self, attr_name, variant)

    def set_root(self, root: ROOT_LEVEL_CONTAINER_TYPING):
        self.root = root
        self.create_attributes()
