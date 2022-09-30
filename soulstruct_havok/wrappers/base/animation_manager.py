"""Manager class that combines various HKX files to make animation modification easier.

Currently mainly set up for Havok 2015 (for Nightfall/DSR).
"""
from __future__ import annotations

import abc
import copy
import logging
from pathlib import Path

from soulstruct.base.game_file import GameFile
from soulstruct.containers import Binder

from soulstruct_havok.tagfile.unpacker import MissingCompendiumError
from soulstruct_havok.wrappers.base import AnimationHKX, SkeletonHKX
from soulstruct_havok.spline_compression import *

_LOGGER = logging.getLogger(__name__)


class BaseAnimationManager(abc.ABC):

    skeleton: SkeletonHKX
    animations: dict[int, AnimationHKX]
    animation_data: dict[int, SplineCompressedAnimationData]
    default_anim_id: int | None

    def __init__(self, skeleton: SkeletonHKX, animations: dict[int, AnimationHKX]):
        self.skeleton = skeleton
        self.animations = animations
        self.animation_data = {}
        if len(animations) == 1:
            self.default_anim_id = list(animations)[0]
        else:
            self.default_anim_id = None  # undecided

    def get_default_anim_id(self) -> int:
        if self.default_anim_id is not None:
            return self.default_anim_id
        raise ValueError("Default animation ID has not been set.")

    def scale_animation_data(self, factor: float, *anim_ids: int):
        """Load, scale, and save animation data for given IDs.

        Also scales root motion (`referenceFrameSamples`) if present.
        """
        if not anim_ids:
            anim_ids = [self.get_default_anim_id()]
        for anim_id in anim_ids:
            self.animations[anim_id].scale(factor)

    def copy_animation(self, anim_id: int, new_anim_id: int, overwrite=False):
        """Make a copy of an animation. Will also copy its raw data, if loaded."""
        if new_anim_id in self.animations and not overwrite:
            raise ValueError(f"Animation ID {new_anim_id} already exists, and `overwrite=False`.")
        self.animations[new_anim_id] = self.animations[anim_id].copy()
        if anim_id in self.animation_data:
            self.animation_data[new_anim_id] = copy.deepcopy(self.animation_data[anim_id])

    def auto_retarget_animation(
        self,
        source_manager: BaseAnimationManager,
        source_anim_id: int,
        dest_anim_id: int,
        bone_name_mapping: dict[str, str | None],
        scale_factor=1.0,
    ):
        """Read `source_anim_id` from `source_manager` and use `bone_name_mapping` to convert the animation tracks to
        `new_anim_id` in this manager.

        `bone_name_mapping` should map the names of bones in THIS skeleton to those in `source_manager`'s skeleton.
        """
        if source_anim_id not in source_manager.animation_data:
            source_manager.load_animation_data(source_anim_id)
        if dest_anim_id not in self.animation_data:
            self.load_animation_data(dest_anim_id)
        source_animation = source_manager.animations[source_anim_id]
        source_animation_data = source_manager.animation_data[source_anim_id]
        source_tracks = source_animation_data.blocks[0]
        dest_animation = self.animations[dest_anim_id]
        dest_animation_data = self.animation_data[dest_anim_id]

        new_block = []  # type: list[TransformTrack]
        for i, bone in enumerate(self.skeleton.bones):
            try:
                source_bone_name = bone_name_mapping[bone.name]
            except KeyError:
                raise KeyError(f"Target skeleton bone '{bone.name}' has no key in mapping to source bone names.")
            if source_bone_name is None:
                # Bone has no corresponding bone in source skeleton.
                # We default to the bone's skeleton reference pose (T-pose).
                # Use static bone transform from skeleton.

                # TODO: Currently copying and modifying a track, because there's a bug with creation of tracks from
                #  scratch. Figure it out!
                dummy_track = copy.deepcopy(source_tracks[21])
                bone_qs_transform = self.skeleton.skeleton.referencePose[i]
                dummy_track.translation.set_to_static_vector(bone_qs_transform.translation[:3])
                dummy_track.rotation.set_to_static_quaternion(bone_qs_transform.rotation)
                dummy_track.scale.set_to_static_vector(bone_qs_transform.scale[:3])
                new_block.append(dummy_track)
                _LOGGER.info(f"Using default reference pose for unmapped bone '{bone.name}'.")
            else:
                _LOGGER.info(f"Bone '{bone.name}' mapped to source bone '{source_bone_name}'.")
                source_track = source_manager.get_bone_animation_track(source_bone_name, source_anim_id)
                new_block.append(copy.deepcopy(source_track))

        dest_animation_data.blocks[0] = new_block

        # Copy over root motion (modify list in place).
        if dest_animation.reference_frame_samples is not None:
            dest_animation.reference_frame_samples[:] = source_animation.reference_frame_samples[:]
            _LOGGER.info("Retargeted animation reference frame samples.")
            if scale_factor != 1.0:
                if dest_animation.reference_frame_samples is not None:
                    for sample in dest_animation.reference_frame_samples:
                        # Scale X, Y, and Z only, not W.
                        sample.x *= scale_factor
                        sample.y *= scale_factor
                        sample.z *= scale_factor
                _LOGGER.info(f"Scaled animation reference frame samples by {scale_factor}.")

        if scale_factor != 1.0:
            self.animation_data[dest_anim_id].scale(scale_factor)
            _LOGGER.info(f"Scaled animation data by {scale_factor}.")

        self.save_animation_data(dest_anim_id)

        _LOGGER.info(f"Auto-retarget complete. Animation {dest_anim_id} saved.")

    def get_bone_animation_track(self, bone_name_or_index: str | int, anim_id: int = None) -> TransformTrack:
        if anim_id is None:
            anim_id = self.get_default_anim_id()
        if anim_id not in self.animation_data:
            self.load_animation_data(anim_id)
        if isinstance(bone_name_or_index, str):
            bone_index = self.skeleton.find_bone_name_index(bone_name_or_index)
        else:
            bone_index = bone_name_or_index
        mapping = self.animations[anim_id].animation_binding.transformTrackToBoneIndices
        track_index = mapping.index(bone_index)
        return self.animation_data[anim_id].blocks[0][track_index]

    def validate_track_count(self, anim_id: int = None):
        """Check that the number of animation tracks matches the number of skeleton bones.

        TODO: Technically, the track count can be less than the bone count, as the mapping may simply omit some bones.
         To be accurate, we would only need to check the largest index in the mapping does not exceed the bone count.
        """
        if anim_id is None:
            anim_id = self.get_default_anim_id()
        if anim_id not in self.animation_data:
            self.load_animation_data(anim_id)
        track_count = len(self.animation_data[anim_id].blocks[0])
        bone_count = len(self.skeleton.bones)
        if track_count != bone_count:
            raise ValueError(f"Animation ID {anim_id} has {track_count} tracks, but skeleton has {bone_count} bones.")

    def load_animation_data(self, *anim_ids: int):
        for anim_id in anim_ids:
            animation = self.animations[anim_id]
            self.animation_data[anim_id] = animation.get_spline_compressed_animation_data()

    def save_animation_data(self, *anim_ids: int):
        for anim_id in anim_ids:
            if anim_id not in self.animation_data:
                raise KeyError(f"Animation ID {anim_id} has not had its raw data loaded yet.")
            animation_data = self.animation_data[anim_id]
            self.animations[anim_id].set_spline_compressed_animation_data(animation_data)

    # region Read/Write Methods
    @classmethod
    def from_anibnd(cls, anibnd_source: GameFile.Typing, *animation_ids: int, from_bak=False, compendium_name=""):
        anibnd = Binder(anibnd_source, from_bak=from_bak)
        compendium, compendium_name = AnimationHKX.get_compendium_from_binder(anibnd, compendium_name)
        try:
            skeleton = SkeletonHKX(anibnd.find_entry_matching_name(r"[Ss]keleton\.[HKX|hkx]"), compendium=compendium)
            animations = {
                anim_id: AnimationHKX(anibnd[cls.animation_id_to_entry_basename(anim_id)], compendium=compendium)
                for anim_id in animation_ids
            }
        except MissingCompendiumError:
            if compendium_name != "":
                raise MissingCompendiumError(
                    f"Binder HKX entry requires a compendium, but compendium '{compendium_name}' "
                    f"could not be found in given binder. Use `compendium_name` argument if it has another name."
                )
            raise MissingCompendiumError(
                f"Binder HKX entry requires a compendium, but `compendium_name` was not given and a "
                f"'.compendium' entry could not be found in the given binder."
            )

        return cls(skeleton, animations)

    def write_anim_ids_into_anibnd(
        self, anibnd_path: Path | str, *anim_ids: int, from_bak=False, write_path: Path | str = None
    ):
        anibnd = Binder(anibnd_path, from_bak=from_bak)
        for anim_id in anim_ids:
            animation = self.animations[anim_id]
            anibnd[self.animation_id_to_entry_basename(anim_id)].set_uncompressed_data(animation.pack_dcx())
        if write_path is None:
            write_path = anibnd_path
        anibnd.write(file_path=anibnd_path)  # will default to same path
        if write_path != anibnd_path:
            _LOGGER.info(f"Animations {', '.join(str(x) for x in anim_ids)} written to {anibnd_path} at {write_path}.")
        else:
            _LOGGER.info(f"Animations {', '.join(str(x) for x in anim_ids)} written into {anibnd_path}.")

    def write_all_into_anibnd(self, anibnd_path: Path | str, from_bak=False, write_path: Path | str = None):
        anibnd = Binder(anibnd_path, from_bak=from_bak)
        anibnd.find_entry_matching_name(r"[Ss]keleton\.[HKX|hkx]").set_uncompressed_data(self.skeleton.pack_dcx())
        for anim_id, animation in self.animations.items():
            anibnd[self.animation_id_to_entry_basename(anim_id)].set_uncompressed_data(animation.pack_dcx())
        anibnd.write(file_path=write_path)  # will default to same path
    # endregion

    @staticmethod
    @abc.abstractmethod
    def animation_id_to_entry_basename(animation_id: int) -> str:
        if animation_id >= 999999:
            raise ValueError("Max animation ID for DS1 is 999999.")
        return f"a{animation_id // 10000:02d}_{animation_id % 10000:04d}.hkx"
