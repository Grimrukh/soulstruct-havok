from __future__ import annotations

import abc
import typing as tp

from soulstruct_havok.utilities.maths import TRSTransform, Vector3
from soulstruct_havok.types import hk2010, hk2014, hk2015, hk2018

from .core import BaseWrapperHKX


SKELETON_TYPING = tp.Union[
    hk2010.hkaSkeleton, hk2014.hkaSkeleton, hk2015.hkaSkeleton, hk2018.hkaSkeleton,
]
BONE_TYPING = tp.Union[
    hk2010.hkaBone, hk2014.hkaBone, hk2015.hkaBone, hk2018.hkaBone,
]
BONE_SPEC_TYPING = tp.Union[BONE_TYPING, int, str]


class BaseSkeletonHKX(BaseWrapperHKX, abc.ABC):
    """Loads HKX objects that are found in a "Skeleton" HKX file (inside `anibnd` binder, usually `Skeleton.HKX`)."""

    skeleton: SKELETON_TYPING
    bones: list[BONE_TYPING]

    def create_attributes(self):
        animation_container = self.get_variant_index(0, "hkaAnimationContainer")
        self.skeleton = animation_container.skeletons[0]
        self.bones = self.skeleton.bones

    def scale(self, factor: float):
        """Scale all bone translations in place by `factor`."""
        for pose in self.skeleton.referencePose:
            pose.translation = tuple(x * factor for x in pose.translation)

    def get_bone_index(self, bone: BONE_SPEC_TYPING):
        bone = self.resolve_bone_spec(bone)
        return self.skeleton.bones.index(bone)

    def get_bone_parent_index(self, bone: BONE_SPEC_TYPING) -> int:
        bone = self.resolve_bone_spec(bone)
        bone_index = self.skeleton.bones.index(bone)
        return self.skeleton.parentIndices[bone_index]

    def get_bone_parent(self, bone: BONE_SPEC_TYPING) -> tp.Optional[BONE_TYPING]:
        parent_index = self.get_bone_parent_index(bone)
        if parent_index == -1:
            return None
        return self.skeleton.bones[parent_index]

    def get_bone_highest_parent(self, bone: BONE_SPEC_TYPING) -> tp.Optional[BONE_TYPING]:
        parent_bone = bone
        parent_index = self.get_bone_parent_index(bone)
        while parent_index != -1:
            parent_bone = self.skeleton.bones[parent_index]
            parent_index = self.get_bone_parent_index(parent_bone)
        return parent_bone

    def get_immediate_bone_children_indices(self, bone: BONE_SPEC_TYPING) -> list[int]:
        bone = self.resolve_bone_spec(bone)
        bone_index = self.skeleton.bones.index(bone)
        return [i for i, b in enumerate(self.skeleton.bones) if self.get_bone_parent_index(b) == bone_index]

    def get_immediate_bone_children(self, bone: BONE_SPEC_TYPING) -> list[BONE_TYPING]:
        bone = self.resolve_bone_spec(bone)
        bone_index = self.skeleton.bones.index(bone)
        return [b for b in self.skeleton.bones if self.get_bone_parent_index(b) == bone_index]

    def get_all_bone_children(self, bone: BONE_SPEC_TYPING) -> list[BONE_TYPING]:
        """Recursively get all bones that are children of `bone`."""
        bone = self.resolve_bone_spec(bone)
        children = []
        bone_index = self.skeleton.bones.index(bone)
        for bone in self.skeleton.bones:
            parent_index = self.get_bone_parent_index(bone)
            if parent_index == bone_index:
                children.append(bone)  # immediate child
                children += self.get_all_bone_children(bone)  # recur on child
        return children

    def get_bone_reference_pose_transform(self, bone: BONE_SPEC_TYPING, world_space=False) -> TRSTransform:
        bone = self.resolve_bone_spec(bone)
        if world_space:
            transform = TRSTransform.identity()
            for hierarchy_transform in self.get_hierarchy_transforms(bone):
                transform = transform @ hierarchy_transform
            return transform
        else:
            bone_index = self.skeleton.bones.index(bone)
            return self.skeleton.referencePose[bone_index].to_trs_transform()

    def get_hierarchy_to_bone(self, bone: BONE_SPEC_TYPING) -> list[BONE_TYPING]:
        """Get all parents of `bone` in order from the highest down to itself."""
        bone = self.resolve_bone_spec(bone)
        parents = [bone]
        bone_index = self.skeleton.bones.index(bone)
        parent_index = self.skeleton.parentIndices[bone_index]
        while parent_index != -1:
            bone = self.skeleton.bones[parent_index]
            parents.append(bone)
            bone_index = self.skeleton.bones.index(bone)
            parent_index = self.skeleton.parentIndices[bone_index]
        return list(reversed(parents))

    def get_bone_ascending_parent_indices(self, bone: BONE_SPEC_TYPING, include_self=False) -> list[int]:
        """Get indices of bone's parents in ascending order.

        Useful for applying parent transforms in the correct order to get a world space transform of `bone`.
        """
        bone = self.resolve_bone_spec(bone)
        bone_index = self.skeleton.bones.index(bone)
        parent_indices = []
        if include_self:
            parent_indices.append(bone_index)
        parent_index = self.skeleton.parentIndices[bone_index]
        while parent_index != -1:
            parent_indices.append(parent_index)
            bone = self.skeleton.bones[parent_index]
            bone_index = self.skeleton.bones.index(bone)
            parent_index = self.skeleton.parentIndices[bone_index]
        return parent_indices

    def get_bone_descending_parent_indices(self, bone: BONE_SPEC_TYPING, include_self=False) -> list[int]:
        """Get indices of bone's parents in descending order from root bone.

        Useful for applying inverse parent transforms in the correcet order to change world space back to local space.
        """
        ascending_indices = self.get_bone_ascending_parent_indices(bone, include_self=include_self)
        return ascending_indices[::-1]

    def get_all_bone_parent_indices(self) -> list[list[int]]:
        """Returns a list of lists of the hierarchical indices up to each bone (inclusive)."""
        all_indices = []
        for bone_index, bone in enumerate(self.skeleton.bones):
            indices = []
            parent_index = bone_index
            while parent_index != -1:
                indices.append(parent_index)
                parent_index = self.get_bone_parent_index(parent_index)
            all_indices.append(list(reversed(indices)))
        return all_indices

    def get_hierarchy_transforms(self, bone: BONE_SPEC_TYPING) -> list[TRSTransform]:
        """Get all transforms of all parent bones down to `bone`, including it."""
        return [self.get_bone_reference_pose_transform(b) for b in self.get_hierarchy_to_bone(bone)]

    def get_bone_transforms_and_parents(self):
        """Construct a dictionary that maps bone names to (`hkQsTransform`, `hkaBone`) pairs of transforms/parents."""
        bone_transforms = {}
        for i in range(len(self.skeleton.bones)):
            bone_name = self.skeleton.bones[i].name
            parent_index = self.skeleton.parentIndices[i]
            parent_bone = None if parent_index == -1 else self.skeleton.bones[parent_index]
            bone_transforms[bone_name] = (self.skeleton.referencePose[i], parent_bone)
        return bone_transforms

    def delete_bone(self, bone: BONE_SPEC_TYPING) -> int:
        """Delete a bone and all of its children. Returns the number of bones deleted."""
        bone = self.resolve_bone_spec(bone)
        bones_deleted = 0
        children = self.get_all_bone_children(bone)
        for child_bone in children:
            bones_deleted += self.delete_bone(child_bone)

        # Delete bone.
        bone_index = self.skeleton.bones.index(bone)
        self.skeleton.referencePose.pop(bone_index)
        self.skeleton.parentIndices.pop(bone_index)
        self.skeleton.bones.pop(bone_index)

        return bones_deleted

    def print_bone_tree(self, bone: BONE_SPEC_TYPING = None, indent=""):
        """Print indented tree of bone names."""
        bone = self.skeleton.bones[0] if bone is None else self.resolve_bone_spec(bone)  # 'Master' usually
        print(indent + bone.name)
        for child in self.get_immediate_bone_children(bone):
            self.print_bone_tree(child, indent=indent + "    ")

    def resolve_bone_spec(self, bone_spec: BONE_SPEC_TYPING) -> BONE_TYPING:
        if isinstance(bone_spec, int):
            if bone_spec < 0:
                raise ValueError(f"Can only use non-negative bone indices, not: {bone_spec}")
            bone = self.bones[bone_spec]
        elif isinstance(bone_spec, str):
            bone = self._find_bone_name(bone_spec)
        elif isinstance(bone_spec, BONE_TYPING):
            bone = bone_spec
        else:
            raise TypeError(f"Invalid specification type for `hkaBone`: {type(bone_spec).__name__}")
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")
        return bone

    def _find_bone_name(self, bone_name: str):
        matches = [bone for bone in self.skeleton.bones if bone.name == bone_name]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise ValueError(f"Multiple bones named '{bone_name}' in skeleton. This is unusual.")
        else:
            raise ValueError(f"Bone name not found: '{bone_name}'")
