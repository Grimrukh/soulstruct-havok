import typing as tp

from soulstruct.utilities.maths import Matrix3, QuatTransform, Vector3
from soulstruct_havok.types import hk2010, hk2014, hk2015, hk2018

from .core import BaseWrapperHKX


SKELETON_TYPING = tp.Union[
    hk2010.hkaSkeleton, hk2014.hkaSkeleton, hk2015.hkaSkeleton, hk2018.hkaSkeleton,
]
BONE_TYPING = tp.Union[
    hk2010.hkaBone, hk2014.hkaBone, hk2015.hkaBone, hk2018.hkaBone,
]
BONE_OR_NAME = tp.Union[BONE_TYPING, str]


class SkeletonHKX(BaseWrapperHKX):
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

    def find_bone_name(self, bone_name: str):
        matches = [bone for bone in self.skeleton.bones if bone.name == bone_name]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise ValueError(f"Multiple bones named '{bone_name}' in skeleton. This is unusual.")
        else:
            raise ValueError(f"Bone name not found: '{bone_name}'")

    def find_bone_name_index(self, bone_name: str):
        bone = self.find_bone_name(bone_name)
        return self.skeleton.bones.index(bone)

    def get_bone_parent_index(self, bone: BONE_OR_NAME) -> int:
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")
        bone_index = self.skeleton.bones.index(bone)
        return self.skeleton.parentIndices[bone_index]

    def get_bone_parent(self, bone: BONE_OR_NAME) -> tp.Optional[BONE_TYPING]:
        parent_index = self.get_bone_parent_index(bone)
        if parent_index == -1:
            return None
        return self.skeleton.bones[parent_index]

    def get_immediate_bone_children(self, bone: BONE_OR_NAME) -> list[BONE_TYPING]:
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")

        bone_index = self.skeleton.bones.index(bone)
        return [b for b in self.skeleton.bones if self.get_bone_parent_index(b) == bone_index]

    def get_all_bone_children(self, bone: BONE_OR_NAME) -> list[BONE_TYPING]:
        """Recursively get all bones that are children of `bone`."""
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")

        children = []
        bone_index = self.skeleton.bones.index(bone)
        for bone in self.skeleton.bones:
            parent_index = self.get_bone_parent_index(bone)
            if parent_index == bone_index:
                children.append(bone)  # immediate child
                children += self.get_all_bone_children(bone)  # recur on child
        return children

    def get_bone_local_transform(self, bone: BONE_OR_NAME) -> QuatTransform:
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")
        bone_index = self.skeleton.bones.index(bone)
        qs_transform = self.skeleton.referencePose[bone_index]
        return QuatTransform(
            qs_transform.translation,
            qs_transform.rotation,
            qs_transform.scale,
        )

    def get_all_parents(self, bone: BONE_OR_NAME) -> list[BONE_TYPING]:
        """Get all parents of `bone` in order from the highest down to itself."""
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")
        parents = [bone]
        bone_index = self.skeleton.bones.index(bone)
        parent_index = self.skeleton.parentIndices[bone_index]
        while parent_index != -1:
            bone = self.skeleton.bones[parent_index]
            parents.append(bone)
            bone_index = self.skeleton.bones.index(bone)
            parent_index = self.skeleton.parentIndices[bone_index]
        return list(reversed(parents))

    def get_bone_global_translate(self, bone: BONE_OR_NAME) -> Vector3:
        """Accumulates parents' transforms into a 4x4 matrix."""
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")
        absolute_translate = Vector3.zero()
        rotate = Matrix3.identity()
        for hierarchy_bone in self.get_all_parents(bone):
            local_transform = self.get_bone_local_transform(hierarchy_bone)
            absolute_translate += rotate @ Vector3(local_transform.translate)
            rotate @= local_transform.rotation.to_rotation_matrix(real_last=True)
        return absolute_translate

    def get_bone_transforms_and_parents(self):
        """Construct a dictionary that maps bone names to (`hkQsTransform`, `hkaBone`) pairs of transforms/parents."""
        bone_transforms = {}
        for i in range(len(self.skeleton.bones)):
            bone_name = self.skeleton.bones[i].name
            parent_index = self.skeleton.parentIndices[i]
            parent_bone = None if parent_index == -1 else self.skeleton.bones[parent_index]
            bone_transforms[bone_name] = (self.skeleton.referencePose[i], parent_bone)
        return bone_transforms

    def delete_bone(self, bone: BONE_OR_NAME) -> int:
        """Delete a bone and all of its children. Returns the number of bones deleted."""
        if isinstance(bone, str):
            bone = self.find_bone_name(bone)
        if bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")

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

    def print_bone_tree(self, bone: BONE_OR_NAME = None, indent=""):
        """Print indented tree of bone names."""
        if bone is None:
            bone = self.skeleton.bones[0]  # 'Master' usually
        elif isinstance(bone, str):
            bone = self.find_bone_name(bone)
        elif bone not in self.skeleton.bones:
            raise ValueError(f"Bone '{bone}' is not in this skeleton.")

        print(indent + bone.name)
        for child in self.get_immediate_bone_children(bone):
            self.print_bone_tree(child, indent=indent + "    ")
