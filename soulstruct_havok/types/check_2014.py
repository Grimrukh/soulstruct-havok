import inspect

from soulstruct_havok.types.core import hk
from soulstruct_havok.types import hk2014 as old
from soulstruct_havok.types import hk2014_new as new


if __name__ == '__main__':
    new_types = {
        name: cls
        for name, cls in inspect.getmembers(new, lambda x: inspect.isclass(x) and issubclass(x, hk))
    }
    missing_old_types = []
    for name, cls in inspect.getmembers(old, lambda x: inspect.isclass(x) and issubclass(x, hk)):
        if name not in new_types:
            missing_old_types.append(name)
            continue
        new_cls = new_types[name]

        for field in ("byte_size", "alignment", "tag_type_flags"):
            old_value = getattr(cls, field)
            new_value = getattr(new_cls, field)
            if old_value != new_value:
                print(f"{field} CLASH in {name}: {old_value} vs. {new_value}")

        if len(cls.local_members) != len(new_cls.local_members):
            raise ValueError(
                f"Type {name} has {len(cls.members)} members in old module, but {len(new_cls.members)} in new."
            )
        for old_m, new_m in zip(cls.local_members, new_cls.local_members):
            if old_m.name != new_m.name:
                print(f"NAME CLASH in {name}: {old_m.name} vs. {new_m.name}")
            elif old_m.offset != new_m.offset:
                print(f"OFFSET CLASH in {name}.{old_m.name}: {old_m.offset} vs. {new_m.offset}")

    if missing_old_types:
        missing = "\n    ".join(missing_old_types)
        print(f"TYPES MISSING FROM NEW MODULE: {missing}")
