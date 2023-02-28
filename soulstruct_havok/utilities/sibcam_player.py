"""Utility for getting the transform matrix on each frame from a SIBCAM camera animation file."""
from __future__ import annotations

__all__ = [
    "SIBCAM",
    "CameraView",
    "SibcamPlayer",
]

import math
import typing as tp
from dataclasses import dataclass

from soulstruct.base.animations import SIBCAM, CameraFrameTransform
from soulstruct.utilities.maths import Vector3
from soulstruct_havok.utilities.maths import TRSTransform, Quaternion, Matrix3


@dataclass(slots=True)
class CameraView:
    """Baked `TRSTransform` and field of view (`fov`) for an animation frame, ready for use in game space."""
    transform: TRSTransform
    fov: float

    @classmethod
    def DEFAULT(cls) -> tp.Self:
        return cls(transform=TRSTransform.identity(), fov=1.0)


class SibcamPlayer:

    FRAME_DELTA = 1.0 / 30.0

    sibcam: SIBCAM
    baked_view_frames: list[CameraView]

    # Playback properties.
    current_time: float
    current_view: None | CameraView
    is_playing: bool
    is_loop: bool
    is_finished: bool

    def __init__(self, sibcam: SIBCAM):
        self.sibcam = sibcam

        self.current_time = 0.0
        self.current_view = CameraView.DEFAULT()
        self.is_playing = self.is_loop = self.is_finished = False

        self.baked_view_frames = self.bake()

    def update_playback(self, time_delta: float):
        if self.is_playing:
            new_time = self.current_time + time_delta
            new_time = min(self.last_frame_time, new_time)
            self.set_time(new_time)

    def set_time(self, new_time: float):
        if self.is_loop:
            new_time %= self.sibcam.frame_count * self.FRAME_DELTA
        else:
            if new_time > self.sibcam.frame_count * self.FRAME_DELTA:
                self.is_finished = True

        self.current_time = new_time

        if not self.baked_view_frames:
            return

        frame = self.current_time / self.FRAME_DELTA
        if frame < 0:
            frame = 0.0
        elif frame > len(self.baked_view_frames):
            frame = len(self.baked_view_frames) - 1

        frame_floor = int(math.floor(frame))
        frame_ceil = int(math.ceil(frame))

        current_frame = self.baked_view_frames[frame_floor]

        if frame >= self.sibcam.frame_count - 1:
            next_frame = self.baked_view_frames[0].transform if self.is_loop else current_frame
        else:
            next_frame = self.baked_view_frames[frame_ceil]

        lerp_factor = frame % 1.0  # how far between frames are we?
        self.current_view.transform = TRSTransform.lerp(current_frame.transform, next_frame.transform, lerp_factor)
        self.current_view.fov = current_frame.fov + lerp_factor * (next_frame.fov - current_frame.fov)

    def bake(self) -> list[CameraView]:
        """Process attached `SIBCAM` file into a list of `CameraView`s to use each frame."""
        baked_view_frames = [CameraView.DEFAULT() for _ in range(self.sibcam.frame_count)]

        for frame_index in range(len(self.sibcam.camera_animation)):
            frame_sibcam_transform = self.sibcam.camera_animation[frame_index]
            frame_trs_transform = self.sibcam_frame_to_trs_transform(frame_sibcam_transform)
            baked_view_frames[frame_index].transform = frame_trs_transform
            # TODO: Meow's code seems to imply that interpolation might be needed here, but as far as I can tell, the
            #  SIBCAM `camera_animation` list contains a transform for EVERY frame (unlike FoV below).

        # FoV may need to be interpolated from fewer keyframes.
        last_keyframe_index = -1
        last_fov_value = self.sibcam.initial_fov
        for fov_keyframe in self.sibcam.fov_keyframes:
            frame_index = fov_keyframe.frame_index
            this_fov_value = fov_keyframe.fov
            if 0 <= frame_index < self.sibcam.frame_count:
                baked_view_frames[frame_index].fov = this_fov_value

            # Interpolate FoV values from last keyframe to this one.
            for i in range(last_keyframe_index + 1, min(frame_index - 1, self.sibcam.frame_count - 1)):
                t = (i - last_keyframe_index) / (frame_index - last_keyframe_index)
                lerped = last_fov_value + t * (this_fov_value - last_fov_value)
                baked_view_frames[i].fov = lerped

            last_keyframe_index = frame_index
            last_fov_value = this_fov_value

        # Apply final FoV keyframe value to remainder of camera animation.
        for i in range(last_keyframe_index + 1, self.sibcam.frame_count - 1):
            baked_view_frames[i].fov = last_fov_value

        return baked_view_frames

    @property
    def last_frame_time(self) -> float:
        return (len(self.baked_view_frames) - 1) * self.FRAME_DELTA

    @staticmethod
    def sibcam_frame_to_trs_transform(sibcam_frame_transform: CameraFrameTransform):
        translation = sibcam_frame_transform.position * Vector3((1, 1, -1))
        scale = sibcam_frame_transform.scale
        rotation_mat = Matrix3.from_euler_angles(
            rx=-(sibcam_frame_transform.rotation.x + math.pi / 2.0),
            ry=-sibcam_frame_transform.rotation.y,
            rz=sibcam_frame_transform.rotation.z,
            order="xzy",
        )
        rotation = Quaternion.from_matrix3(rotation_mat)
        return TRSTransform(translation, rotation, scale)
