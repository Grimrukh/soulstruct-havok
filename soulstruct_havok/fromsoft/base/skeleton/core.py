from __future__ import annotations

__all__ = ["BaseSkeletonHKX"]

import abc
from dataclasses import dataclass

from ..core import BaseWrappedHKX
from ..type_vars import ANIMATION_CONTAINER_T
from .skeleton import Skeleton


class BaseSkeletonHKX(BaseWrappedHKX, abc.ABC):
    """Skeleton HKX file, usually inside a `.chrbnd` Binder."""

    skeleton: Skeleton = None

    def __post_init__(self):
        hka_animation_container = self.get_variant(0, *ANIMATION_CONTAINER_T.__constraints__)
        self.skeleton = Skeleton(self.HAVOK_MODULE, hka_animation_container.skeletons[0])
