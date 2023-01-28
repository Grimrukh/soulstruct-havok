from __future__ import annotations

import abc

from .animation import BaseAnimationHKX
from .skeleton import BaseSkeletonHKX, BoneWrapper
from soulstruct_havok.utilities.maths import TRSTransform


class BaseRemoAnimationHKX(BaseAnimationHKX, BaseSkeletonHKX, abc.ABC):
    """HKX file that contains a skeleton AND animation data.

    Here, each root bone is the name of an `MSBPart` model manipulated in this camera cut of the REMO cutscene (each
    with child bones corresponding to the actual bones of that model, if applicable).
    """
    def create_attributes(self):
        animation_container = self.get_variant_index(0, "hkaAnimationContainer")
        self.skeleton = animation_container.skeletons[0]
        self.animation = animation_container.animations[0]
        self.animation_binding = animation_container.bindings[0]

        self.regenerate_bone_wrappers()

        if self.is_interleaved:  # basic enough to do outomatically
            self.load_interleaved_data()

    # TODO: What does the top-level name of this skeleton mean? Seems to just be first bone, but that's also usually a
    #  collision, so it could be used...?

    def get_named_root_bones(self) -> dict[str, BoneWrapper]:
        """Returns a dictionary mapping each root bone part name to its root bone, for easy access from FLVER."""
        return {bone.name: bone for bone in self.get_root_bones()}

    def get_part_bones(self, part_name: str, root_bone_name="master") -> dict[str, BoneWrapper]:
        """Returns a dictionary mapping standard bone names to the name-prefixed bones in this HKX."""
        part_root_bones = self.get_named_root_bones()
        if part_name not in part_root_bones:
            raise ValueError(f"Part name '{part_name}' does not have a root bone in this `RemoAnimationHKX`.")
        part_bones = {root_bone_name: part_root_bones[part_name]}
        prefix = part_name + "_"
        part_bones |= {bone.name.removeprefix(prefix): bone for bone in part_root_bones[part_name].get_all_children()}
        return part_bones

    def get_all_part_world_space_transforms_in_frame(
        self, part_name: str, frame_index: int, root_bone_name="master"
    ) -> dict[str, TRSTransform]:
        """Resolve all transforms to get world space transforms of `part_name` at the given `frame_index`.

        Returns a dictionary mapping non-prefixed part bone names to their world space transforms in this frame.

        Avoid recomputing transforms multiple times; each bone is only processed once, using parents' accumulating
        world transforms.

        NOTE: Unlike the 'local to world' transformations found elsewhere, which are really 'local to armature',
        these REMO animation coordinates are ACTUALLY world space transforms (due to the world space transform applied
        to the root bone).
        """
        part_bones = self.get_part_bones(part_name, root_bone_name)
        if not self.is_interleaved:
            raise TypeError("Can only get bone animation tracks for interleaved animation.")
        self.load_interleaved_data()
        if frame_index > len(self.interleaved_data):
            raise ValueError(f"Frame must be between 0 and {len(self.interleaved_data)}, not {frame_index}.")

        frame_local_transforms = self.interleaved_data[frame_index]
        bone_world_transforms = {bone.name: TRSTransform.identity() for bone in part_bones.values()}
        track_bone_indices = self.animation_binding.transformTrackToBoneIndices

        def bone_local_to_world(bone: BoneWrapper, world_transform: TRSTransform):
            track_index = track_bone_indices.index(bone.index)
            bone_world_transforms[bone.name] = world_transform @ frame_local_transforms[track_index]
            # Recur on children, using this bone's just-computed world transform.
            for child_bone in bone.children:
                bone_local_to_world(child_bone, bone_world_transforms[bone.name])

        bone_local_to_world(part_bones[root_bone_name], TRSTransform.identity())

        # Map standard FLVER bone names to their world transforms computed above.
        return {
            part_bone_name: bone_world_transforms[part_bones[part_bone_name].name]
            for part_bone_name in part_bones
        }
