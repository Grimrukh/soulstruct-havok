
import typing as tp
from collections import deque

from colorama import init as colorama_init, Fore

from soulstruct_havok.packfile.structs import PackFileItem
from soulstruct_havok.tagfile.structs import TagFileItem

from .base import *
from .hk import *
from .info import *

if tp.TYPE_CHECKING:
    from soulstruct_havok.packfile.structs import PackFileItem


colorama_init()


class TypeInfoGenerator:
    """Builds ordered types by searching each `TagFileItem`, in order."""

    _DEBUG_PRINT = False

    def __init__(self, items: list[TagFileItem | PackFileItem], hk_types_module):
        self.type_infos = {}  # type: dict[str, TypeInfo]
        self._module = hk_types_module
        self._scanned_type_names = set()

        for item in items:
            if isinstance(item.value, hk):
                item_type = type(item.value)  # may be a child class of permitted `item.hk_type`
            else:
                item_type = item.hk_type
            if self._DEBUG_PRINT:
                print(f"{Fore.BLUE}Scanning item: {item_type.__name__}{Fore.RESET}")
            self._scan_hk_type_queue(deque([item_type]), indent=0)
            if item_type.__name__ == "hkRootLevelContainer":
                self._add_type(getattr(self._module, "_char"))

    def _add_type(self, hk_type: tp.Type[hk], indent=0):
        if hk_type.__name__ in self.type_infos:
            raise KeyError(f"Type named '{hk_type.__name__}' was collected more than once.")

        type_info_index = len(self.type_infos) + 1
        self.type_infos[hk_type.__name__] = hk_type.get_type_info()
        if self._DEBUG_PRINT:
            print(f"{' ' * indent}  {Fore.GREEN}Created TypeInfo {type_info_index}: {hk_type.__name__}{Fore.RESET}")

    def _scan_hk_type_queue(self, hk_type_queue: deque[tp.Type[hk]], indent=0):
        hk_type_subqueue = deque()  # type: deque[tp.Type[hk]]

        # Exhaust input queue while constructing the next 'subqueue' to recur on below.
        while hk_type_queue:
            hk_type = hk_type_queue.popleft()
            self._scan_hk_type(hk_type, hk_type_subqueue, indent + 4)

        if hk_type_subqueue:
            self._scan_hk_type_queue(hk_type_subqueue, indent + 4)

    def _scan_hk_type(self, hk_type: tp.Type[hk], hk_type_queue: deque[tp.Type[hk]], indent=0):
        if hk_type.__name__ in self._scanned_type_names:
            return  # type already scanned
        if self._DEBUG_PRINT:
            print(f"{' ' * indent}{Fore.YELLOW}Scanning type: {hk_type.__name__}{Fore.RESET}")
        self._scanned_type_names.add(hk_type.__name__)

        # Add this type itself (though it most likely was already added when queued).
        if hk_type.__name__ not in self.type_infos:
            self._add_type(hk_type, indent)

        if issubclass(hk_type, hkEnum_):
            # Add and queue storage and enum types.
            if hk_type.storage_type.__name__ not in self.type_infos:
                self._add_type(hk_type.storage_type, indent)
                hk_type_queue.append(hk_type.storage_type)
            if hk_type.enum_type.__name__ not in self.type_infos:
                self._add_type(hk_type.enum_type, indent)
                hk_type_queue.append(hk_type.enum_type)

        # We don't queue the entire type hierarchy here. The next parent up will be queued when this parent is added.
        parent_hk_type = hk_type.get_immediate_parent()
        if parent_hk_type and parent_hk_type.__name__ not in self.type_infos:
            self._add_type(parent_hk_type, indent)
            hk_type_queue.append(parent_hk_type)

        for template_info in hk_type.get_templates():
            if isinstance(template_info, TemplateType):
                if issubclass(template_info.type, hk) and template_info.type.__name__ not in self.type_infos:
                    # Add and queue template type.
                    self._add_type(template_info.type, indent)
                    hk_type_queue.append(template_info.type)

        if issubclass(hk_type, hkBasePointer):
            data_type = hk_type.get_data_type()  # type: tp.Type[hk]

            if issubclass(data_type, hk) and data_type.__name__ not in self.type_infos:
                # Add and queue data type.
                self._add_type(data_type, indent)
                hk_type_queue.append(data_type)

            if issubclass(hk_type, hkArray_):
                if "hkContainerHeapAllocator" not in self.type_infos:
                    # First `hkArray` found. Add allocator type.
                    self._add_type(getattr(self._module, "hkContainerHeapAllocator"), indent)
                    # Does not need to be queued.
                if f"Ptr[{data_type.__name__}]" not in self.type_infos:
                    # Add generic pointer type (only once per data type).
                    self._add_type(Ptr(data_type), indent)
                    # Does not need to be queued.
                if "_int" not in self.type_infos:
                    # First `hkArray` found. Add `_int` type.
                    self._add_type(getattr(self._module, "_int"), indent)
                    # Does not need to be queued.

            if issubclass(hk_type, (hkRefPtr_, hkRefVariant_, hkViewPtr_)):
                if f"Ptr[{data_type.__name__}]" not in self.type_infos:
                    # Add generic pointer type (once once per data type).
                    self._add_type(Ptr(data_type), indent)
                    # Does not need to be queued.

        # if not issubclass(hk_type, hkStruct_):  # struct member types are covered by pointer data type above

        for member in hk_type.local_members:
            if issubclass(member.type, hk) and member.type.__name__ not in self.type_infos:
                # Add and queue member type.
                self._add_type(member.type, indent)
                hk_type_queue.append(member.type)

        for interface in hk_type.get_interfaces():
            if issubclass(interface.type, hk) and interface.type.__name__ not in self.type_infos:
                # Add and queue interface type.
                self._add_type(interface.type, indent)
                hk_type_queue.append(interface.type)