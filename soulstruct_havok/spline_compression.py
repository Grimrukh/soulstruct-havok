"""Decompress and compress animations based on splines, which is most FromSoftware animations.

This code is adapted to Python from SoulsAssetPipeline by Meowmaritus and Katalash for C#:
    https://github.com/Meowmaritus/SoulsAssetPipeline/blob/master/SoulsAssetPipeline/Animation/HKX/SplineCompressedAnimation.cs
Their code was in turn adapted from the Havok Format Library for C++ by PredatorCZ (Lukas Cone):
    https://github.com/PredatorCZ/HavokLib/blob/master/source/hka_spline_decompressor.cpp

Original code is copyright (C) 2016-2019 Lukas Cone.
"""
from __future__ import annotations

__all__ = ["SplineCompressedAnimationData"]

import math
import struct
import typing as tp
from enum import IntEnum

from soulstruct.utilities.conversion import floatify
from soulstruct.utilities.binary import BinaryReader, BinaryWriter
from soulstruct.utilities.maths import Vector3, Quaternion, QuatTransform


class TrackFlags(IntEnum):
    StaticX = 0b00000001
    StaticY = 0b00000010
    StaticZ = 0b00000100
    StaticW = 0b00001000
    SplineX = 0b00010000
    SplineY = 0b00100000
    SplineZ = 0b01000000
    SplineW = 0b10000000

    @classmethod
    def has_spline_axis(cls, track_flags: int, axis: str) -> bool:
        return track_flags & getattr(cls, f"Spline{axis.upper()}")

    @classmethod
    def has_static_axis(cls, track_flags: int, axis: str) -> bool:
        return track_flags & getattr(cls, f"Static{axis.upper()}")


class ScalarQuantizationType(IntEnum):
    Bits8 = 0
    Bits16 = 1


class RotationQuantizationType(IntEnum):
    Polar32 = 0  # 4 bytes
    ThreeComp40 = 1  # 5 bytes
    ThreeComp48 = 2  # 6 bytes
    ThreeComp25 = 3  # 3 bytes
    Straight16 = 4  # 2 bytes
    Uncompressed = 5  # 16 bytes

    def get_rotation_align(self) -> int:
        if self == self.Polar32:
            return 4
        if self == self.ThreeComp40:
            return 1
        if self == self.ThreeComp48:
            return 2
        if self == self.ThreeComp25:
            return 1
        if self == self.Straight16:
            return 2
        if self == self.Uncompressed:
            return 4
        raise TypeError(f"Invalid `RotationQuantizationType`: {self}")

    def get_rotation_byte_count(self) -> int:
        if self == self.Polar32:
            return 4
        if self == self.ThreeComp40:
            return 5
        if self == self.ThreeComp48:
            return 6
        if self == self.ThreeComp25:
            return 3
        if self == self.Straight16:
            return 2
        if self == self.Uncompressed:
            return 16
        raise TypeError(f"Invalid `RotationQuantizationType`: {self}")


def read_quaternion_Polar32(reader: BinaryReader) -> Quaternion:
    r_mask = (1 << 10) - 1
    r_frac = 1.0 / r_mask
    phi_frac = math.pi / 4 / 511.0

    c_val = reader.unpack_value("I")
    r = floatify((c_val >> 18) & (r_mask & 0xFFFFFFFF)) * r_frac
    r = 1.0 - (r ** 2)

    phi_theta = float(c_val & 0x3FFFF)
    phi = float(math.floor(math.sqrt(phi_theta)))
    theta = 0

    if phi > 0.0:
        theta = (math.pi / 4) * (phi_theta - (phi * phi)) / phi
        phi = phi_frac * phi

    magnitude = float(math.sqrt(1.0 - (r ** 2)))

    value = Quaternion(
        x=math.sin(phi) * math.cos(theta) * magnitude,
        y=math.sin(phi) * math.sin(theta) * magnitude,
        z=math.cos(phi) * magnitude,
        w=r,
    )

    if (c_val & 0x10000000) > 0:
        value.x *= -1
    if (c_val & 0x20000000) > 0:
        value.y *= -1
    if (c_val & 0x40000000) > 0:
        value.z *= -1
    if (c_val & 0x80000000) > 0:
        value.w *= -1

    return value


def read_quaternion_ThreeComp48(reader: BinaryReader) -> Quaternion:
    mask = (1 << 15) - 1
    fractal = 0.000043161

    x, y, z = reader.unpack_value("3h")

    result_shift = ((y >> 14) & 2) | ((x >> 15) & 1)
    r_sign = (z >> 15) != 0

    x &= mask
    x -= mask >> 1
    y &= mask
    y -= mask >> 1
    z &= mask
    z -= mask >> 1

    temp_val = (x * fractal, y * fractal, z * fractal)

    float_value = [math.nan] * 4
    for i in range(4):
        if i < result_shift:
            float_value[i] = temp_val[i]
        elif i == result_shift:
            t = 1.0 - temp_val[0] * temp_val[0] - temp_val[1] * temp_val[1] - temp_val[2] * temp_val[2]
            float_value[i] = (0.0 if t <= 0.0 else math.sqrt(t)) * (-1 if r_sign else 1)
        elif i > result_shift:
            float_value[i] = temp_val[i - 1]

    return Quaternion(float_value)


def read_uint40(reader: BinaryReader) -> int:
    return struct.unpack("Q", reader.read(5) + b"\0\0\0")[0]


def read_quaternion_ThreeComp40(reader: BinaryReader) -> Quaternion:
    """
    Quaternion data packed into 40 bits.

    Bits 0-11 (first 12 minor) are X data.
    Bits 12-23 (second 12 minor) are Y data.
    Bits 24-35 (third 12 minor) are Z data.
    Bits 36-37 (four major) are "result shift".
    Bits 38-39 don't matter (zeroes).

    We then subtract a "positive mask" (4095) from X, Y, and Z.

    We calculate a "temp_val" 3-tuple by multiplying X, Y, and Z by a "fractal", `0.000345436`.

    More...
    """

    mask = (1 << 12) - 1  # eleven 1 bits
    positive_mask = mask >> 1  # ten 1 bits
    fractal = 0.000345436

    c_val = read_uint40(reader)  # "Read only the 5 bytes needed to prevent EndOfStreamException" -- Meow
    x = c_val & mask
    y = ((c_val >> 12) & mask)
    z = ((c_val >> 24) & mask)

    result_shift = ((c_val >> 36) & 3)

    x -= positive_mask
    y -= positive_mask
    z -= positive_mask

    temp_val = (x * fractal, y * fractal, z * fractal)

    float_value = [math.nan] * 4
    for i in range(4):
        if i < result_shift:
            float_value[i] = temp_val[i]
        elif i == result_shift:
            t = 1.0 - temp_val[0] * temp_val[0] - temp_val[1] * temp_val[1] - temp_val[2] * temp_val[2]
            float_value[i] = (0.0 if t <= 0.0 else math.sqrt(t)) * (-1 if ((c_val >> 38) & 1) > 0 else 1)
        elif i > result_shift:
            float_value[i] = temp_val[i - 1]

    return Quaternion(float_value)


def read_quantized_quaternion(reader: BinaryReader, rotation_quantization_type: RotationQuantizationType) -> Quaternion:
    if rotation_quantization_type == RotationQuantizationType.Polar32:
        return read_quaternion_Polar32(reader)
    elif rotation_quantization_type == RotationQuantizationType.ThreeComp40:
        return read_quaternion_ThreeComp40(reader)
    elif rotation_quantization_type == RotationQuantizationType.ThreeComp48:
        return read_quaternion_ThreeComp48(reader)
    elif rotation_quantization_type == RotationQuantizationType.Uncompressed:
        return Quaternion(reader.unpack("4f"))
    raise NotImplementedError(f"Cannot read quantized quaternion of type: {rotation_quantization_type}")


def find_knot_span(degree: int, value: float, c_points_size: int, knots: list[int]) -> int:
    """Algorithm A2.1 The NURBS Book 2nd edition, page 68"""
    if value >= knots[c_points_size]:
        return c_points_size - 1

    low = degree
    high = c_points_size
    mid = (low + high) // 2

    while value < knots[mid] or value >= knots[mid + 1]:
        if value < knots[mid]:
            high = mid
        else:
            low = mid
        mid = (low + high) // 2

    return mid


def get_single_point(
    knot_span_index: int, degree: int, frame: float, knots: list[int], control_points: list[tp.Union[float, Quaternion]]
) -> tp.Union[float, Quaternion]:
    """Basis_ITS1, GetPoint_NR1, TIME-EFFICIENT NURBS CURVE EVALUATION ALGORITHMS, pages 64 & 65

    Works for either `float` or `Quaternion` control points.
    """
    n = [1.0, 0.0, 0.0, 0.0, 0.0]

    for i in range(1, degree + 1):
        for j in range(i - 1, -1, -1):
            a = (frame - knots[knot_span_index - j]) / (knots[knot_span_index + i - j] - knots[knot_span_index - j])
            tmp = n[j] * a
            n[j + 1] += n[j] - tmp
            n[j] = tmp

    value = Quaternion.zero() if isinstance(control_points[0], Quaternion) else 0.0
    for i in range(0, degree + 1):
        value += control_points[knot_span_index - 1] * n[i]
    return value


class SplineHeader:
    """Holds information shared by all three axes of a translation/scale vector, or one rotation."""

    degree: int  # usually 3, i.e. fourth-order, i.e. cubic spline
    knots: list[int]

    def __init__(self, reader: BinaryReader):
        control_point_count = reader.unpack_value("h") + 1  # packed count seems to exclude a control point
        self.degree = reader.unpack_value("B")
        self.knots = [reader.unpack_value("B") for _ in range(control_point_count + self.degree + 1)]

    def pack(self, writer: BinaryWriter, alignment=4):
        writer.pack("HB", self.control_point_count - 1, self.degree)
        writer.pack(f"{len(self.knots)}B", *self.knots)
        writer.pad_align(alignment)

    @property
    def control_point_count(self) -> int:
        return len(self.knots) - self.degree - 1


class SplineQuaternion(list[Quaternion]):
    """List of 4D `Quaternion` control points."""


class SplineFloat(list[float]):
    """List of control points in a single axis."""


class TrackVector3:
    """Holds data for each axis X, Y, and Z.

    In every animation track, each axis of a partial transform vector (i.e. `translate` or `scale`) is represented by:
        (a) a default value (0.0 or 1.0),
        (b) a constant value, or
        (c) a `SplineFloat`.

    Any axes represented by a `SplineFloat` share the same degree, knots, and number of control points - only the
    control point values themselves change. That shared data is unpacked and stored here, along with any default or
    constant axis values.
    """

    spline_header: tp.Optional[SplineHeader]
    x: tp.Union[SplineFloat, float]
    y: tp.Union[SplineFloat, float]
    z: tp.Union[SplineFloat, float]

    quantized_bounds: dict[str, tp.Optional[list[int, int]]]  # maps axis names ("x") to an optional [min, max] list

    def __init__(
        self, reader: BinaryReader, track_flags: int, scalar_quantization: ScalarQuantizationType, default: float
    ):
        self.scalar_quantization = scalar_quantization
        self.default = default  # needed for checking on `pack()`
        if track_flags & (TrackFlags.SplineX | TrackFlags.SplineY | TrackFlags.SplineZ):
            self.spline_header = SplineHeader(reader)
            reader.align(4)
        else:
            self.spline_header = None

        self.quantized_bounds = {"x": None, "y": None, "z": None}
        for axis, spline_flag, static_flag in zip(
            ("x", "y", "z"),
            (TrackFlags.SplineX, TrackFlags.SplineY, TrackFlags.SplineZ),
            (TrackFlags.StaticX, TrackFlags.StaticY, TrackFlags.StaticZ),
        ):
            if track_flags & spline_flag:
                self.quantized_bounds[axis] = list(reader.unpack("2f"))
                setattr(self, axis, SplineFloat())
            elif track_flags & static_flag:
                setattr(self, axis, reader.unpack_value("f"))
            else:
                setattr(self, axis, default)  # generally 0.0 (translation) or 1.0 (scale)

        if self.spline_header:
            for c in range(self.spline_header.control_point_count):
                for axis, spline_flag in zip(
                    ("x", "y", "z"),
                    (TrackFlags.SplineX, TrackFlags.SplineY, TrackFlags.SplineZ),

                ):
                    if track_flags & spline_flag:
                        spline = getattr(self, axis)  # type: SplineFloat
                        spline.append(self.unpack_quantized_float(reader, *self.quantized_bounds[axis]))

    def get_value_at_frame(self, frame: float, axis: str) -> float:
        axis = axis.lower()
        if axis not in "xyz":
            raise ValueError(f"Axis must be 'x', 'y', or 'z', not: {axis}")
        axis_value = getattr(self, axis)
        if isinstance(axis_value, SplineFloat):
            knot_span = find_knot_span(self.spline_header.degree, frame, len(axis_value), self.spline_header.knots)
            return get_single_point(knot_span, self.spline_header.degree, frame, self.spline_header.knots, axis_value)
        else:
            return axis_value  # float

    def get_vector_at_frame(self, frame: float) -> Vector3:
        return Vector3(self.get_value_at_frame(frame, axis) for axis in "xyz")

    def unpack_quantized_float(self, reader: BinaryReader, minimum: float, maximum: float):
        ratio = -1.0
        if self.scalar_quantization == ScalarQuantizationType.Bits8:
            ratio = reader.unpack_value("B") / 255.0
        elif self.scalar_quantization == ScalarQuantizationType.Bits16:
            ratio = reader.unpack_value("H") / 65535.0
        return minimum + (maximum - minimum) * ratio

    def pack(self, writer: BinaryWriter) -> int:
        """Returns the `TrackFlags` bit field determined by current contents."""

        if self.spline_header:
            self.spline_header.pack(writer, alignment=4)

        track_flags = 0
        for axis in ("x", "y", "z"):
            axis_value = getattr(self, axis)
            if isinstance(axis_value, SplineFloat):
                # Compute new quantized bounds from final min/max in control points.
                min_control_point = min(axis_value)
                max_control_point = max(axis_value)
                self.quantized_bounds[axis] = [min_control_point, max_control_point]
                writer.pack("2f", min_control_point, max_control_point)
                track_flags |= getattr(TrackFlags, f"Spline{axis.upper()}")
            elif axis_value != self.default:
                writer.pack("f", axis_value)
                track_flags |= getattr(TrackFlags, f"Static{axis.upper()}")
            # don't write anything if value is default (no flags for axis)

        if self.spline_header:
            for i in range(self.spline_header.control_point_count):
                for axis in ("x", "y", "z"):
                    axis_value = getattr(self, axis)
                    if isinstance(axis_value, SplineFloat):
                        self.pack_quantized_float(writer, axis_value[i], *self.quantized_bounds[axis])

        return track_flags

    def pack_quantized_float(self, writer: BinaryWriter, q_float: float, minimum: float, maximum: float):
        if minimum == maximum:
            if q_float == minimum:
                ratio = 0.0
            else:
                raise ValueError(f"Min/max values for quantization of float {q_float} are equal: {minimum}")
        else:
            ratio = (q_float - minimum) / (maximum - minimum)
        if self.scalar_quantization == ScalarQuantizationType.Bits8:
            writer.pack("B", int(ratio * 255))
        elif self.scalar_quantization == ScalarQuantizationType.Bits16:
            writer.pack("H", int(ratio * 65535))
        else:
            raise ValueError(f"Invalid `ScalarQuantizationType`: {self.scalar_quantization}")

    def __repr__(self):
        return f"TrackVector3({self.x}, {self.y}, {self.z})"


class TrackQuaternion:

    spline_header: tp.Optional[SplineHeader]
    raw_value: tp.Union[None, bytes, list[bytes]]  # one or multiple quantized quaternions
    value: tp.Union[None, SplineQuaternion, Quaternion]

    def __init__(self, reader: BinaryReader, track_flags: int, rotation_quantization: RotationQuantizationType):
        """Holds data for a track's rotation. Could be one static `Quaternion` or a 4D `SplineQuaternion`."""
        self.rotation_quantization = rotation_quantization
        quantized_size = self.rotation_quantization.get_rotation_byte_count()
        if track_flags & (TrackFlags.SplineX | TrackFlags.SplineY | TrackFlags.SplineZ | TrackFlags.SplineW):
            self.spline_header = SplineHeader(reader)
            reader.align(rotation_quantization.get_rotation_align())
            with reader.temp_offset(reader.position):
                self.raw_value = [reader.read(quantized_size) for _ in range(self.spline_header.control_point_count)]
            self.value = SplineQuaternion(
                read_quantized_quaternion(reader, self.rotation_quantization)
                for _ in range(self.spline_header.control_point_count)
            )
        elif track_flags & (TrackFlags.StaticX | TrackFlags.StaticY | TrackFlags.StaticZ | TrackFlags.StaticW):
            self.spline_header = None
            with reader.temp_offset(reader.position):
                self.raw_value = reader.read(quantized_size)
            self.value = read_quantized_quaternion(reader, self.rotation_quantization)
        else:
            self.spline_header = None
            self.raw_value = None
            self.value = Quaternion.identity()

    def get_quaternion_at_frame(self, frame: float) -> Quaternion:
        if isinstance(self.value, SplineQuaternion):
            knot_span = find_knot_span(self.spline_header.degree, frame, len(self.value), self.spline_header.knots)
            return get_single_point(knot_span, self.spline_header.degree, frame, self.spline_header.knots, self.value)
        else:
            return self.value  # Quaternion

    def pack(self, writer: BinaryWriter):
        """TODO: Need to write quantized quaternions..."""
        raise NotImplementedError("Cannot pack spline quaternions yet, sorry.")

    def pack_raw(self, writer: BinaryWriter):
        """Substitute method that supports reversal, but not actual quaternion modification."""
        if self.spline_header:
            self.spline_header.pack(writer, alignment=self.rotation_quantization.get_rotation_align())

        if isinstance(self.raw_value, list):
            writer.append(b"".join(self.raw_value))
        elif isinstance(self.raw_value, bytes):
            writer.append(self.raw_value)
        else:
            pass  # identity, nothing to pack


class TransformFlags:

    translation_quantization: ScalarQuantizationType
    rotation_quantization: RotationQuantizationType
    scale_quantization: ScalarQuantizationType
    translation_track_flags: int
    rotation_track_flags: int
    scale_track_flags: int

    def __init__(self, reader: BinaryReader):
        """Holds information about how each track is compressed and packed (e.g. splines vs. static values)."""

        quantization_types = reader.unpack_value("B")
        self.translation_quantization = ScalarQuantizationType(quantization_types & 0b0000_0011)  # lowest two bits
        self.rotation_quantization = RotationQuantizationType(quantization_types >> 2 & 0b0000_1111)  # middle four bits
        self.scale_quantization = ScalarQuantizationType(quantization_types >> 6 & 0b0000_0011)  # highest two bits

        self.translation_track_flags = reader.unpack_value("B")
        self.rotation_track_flags = reader.unpack_value("B")
        self.scale_track_flags = reader.unpack_value("B")

    def __repr__(self) -> str:
        return (
            f"TransformFlags(\n"
            f"    translation_quantization = {self.translation_quantization.name}\n"
            f"       rotation_quantization = {self.rotation_quantization.name}\n"
            f"          scale_quantization = {self.scale_quantization.name}\n"
            f"     translation_track_types = {[flag for flag in TrackFlags if flag & self.translation_track_flags]}\n"
            f"        rotation_track_types = {[flag for flag in TrackFlags if flag & self.rotation_track_flags]}\n"
            f"           scale_track_types = {[flag for flag in TrackFlags if flag & self.scale_track_flags]}\n"
            f")"
        )


class TransformTrack:
    """Single track of animation data, usually corresponding to a single bone."""

    mask: TransformFlags
    translation: TrackVector3
    rotation: TrackQuaternion
    scale: TrackVector3

    def __init__(self, mask: TransformFlags, translation: TrackVector3, rotation: TrackQuaternion, scale: TrackVector3):
        self.mask = mask
        self.translation = translation
        self.rotation = rotation
        self.scale = scale

    def get_quat_transform_at_frame(self, frame: float) -> QuatTransform:
        translation = self.translation.get_vector_at_frame(frame)
        rotation = self.rotation.get_quaternion_at_frame(frame)
        scale = self.scale.get_vector_at_frame(frame)
        return QuatTransform(translation, rotation, scale)


class SplineCompressedAnimationData:

    blocks: list[list[TransformTrack]]

    def __init__(self, data: list[int], transform_track_count: int, block_count: int, big_endian=False):
        """Read a spline-compressed animation (e.g. `hkaSplineCompressedAnimation["data"]`) to a list of "blocks" of
        frames. Each block can hold some maximum number of frames (e.g. 256). There may only be one block.

        Each block in `blocks` is a list of `TransformTrack` instances.
        """

        self.raw_data = data
        self.transform_track_count = transform_track_count
        self.block_count = block_count
        self.big_endian = big_endian
        self.blocks = []  # type: list[list[TransformTrack]]
        reader = BinaryReader(bytearray(self.raw_data), byte_order=">" if big_endian else "<")
        self.unpack(reader)

    def unpack(self, reader: BinaryReader):

        for block_index in range(self.block_count):

            transform_tracks = []  # type: list[TransformTrack]
            transform_track_flags = [TransformFlags(reader) for _ in range(self.transform_track_count)]

            reader.align(4)

            for i in range(self.transform_track_count):
                mask = transform_track_flags[i]
                translation = TrackVector3(reader, mask.translation_track_flags, mask.translation_quantization, 0.0)
                reader.align(4)
                rotation = TrackQuaternion(reader, mask.rotation_track_flags, mask.rotation_quantization)
                reader.align(4)
                scale = TrackVector3(reader, mask.scale_track_flags, mask.scale_quantization, 1.0)
                reader.align(4)

                transform_tracks.append(TransformTrack(mask, translation, rotation, scale))

            reader.align(16)

            self.blocks.append(transform_tracks)

    def to_transform_track_lists(self, frame_count: int, max_frames_per_block: int) -> list[list[QuatTransform]]:
        """Decompresses the spline data by computing the `QuatTransform` at each frame from any splines.

        Returns a list of `QuatTransform` instances sorted into sub-lists by transform track. Each transform track
        affects a different bone, as mapped in the `AnimationBinding` HKX object.
        """

        track_transforms = [[] for _ in range(self.transform_track_count)]  # type: list[list[QuatTransform]]

        for i in range(frame_count):
            frame = float((i % frame_count) % max_frames_per_block)
            block_index = int((i % frame_count) / max_frames_per_block)
            block = self.blocks[block_index]

            for transform_track_index in range(self.transform_track_count):
                track = block[transform_track_index]
                if frame >= frame_count - 1:
                    # Need to interpolate between this final frame and the first frame.
                    current_frame_transform = track.get_quat_transform_at_frame(float(math.floor(frame)))
                    first_frame_transform = self.blocks[0][transform_track_index].get_quat_transform_at_frame(frame=0.0)
                    track_transforms[transform_track_index].append(
                        QuatTransform.lerp(current_frame_transform, first_frame_transform, t=frame % 1)
                    )
                else:
                    # Normal frame.
                    track_transforms[transform_track_index].append(track.get_quat_transform_at_frame(frame))

        return track_transforms

    def get_scaled_animation_data(self, factor: float) -> list[int]:
        """Unpacks the data like `unpack()`, but maintains a scaled version of it as it encounters data.

        Has no side effects (e.g. does NOT modify the raw animation data).
        """
        reader = BinaryReader(bytearray(self.raw_data), byte_order=">" if self.big_endian else "<")
        scaled_data = bytearray(self.raw_data)

        for block_index in range(self.block_count):

            transform_tracks = []  # type: list[TransformTrack]
            transform_track_masks = [TransformFlags(reader) for _ in range(self.transform_track_count)]

            reader.align(4)

            for i in range(self.transform_track_count):
                mask = transform_track_masks[i]

                translation_offset = reader.position
                translation = TrackVector3(reader, mask.translation_track_flags, mask.translation_quantization, 0.0)

                # Scale spline control points.
                writer = BinaryWriter()
                for axis in "xyz":
                    axis_value = getattr(translation, axis)
                    if isinstance(axis_value, SplineFloat):
                        scaled_axis_value = SplineFloat(c * factor for c in axis_value)
                    else:
                        scaled_axis_value = axis_value * factor
                    setattr(translation, axis, scaled_axis_value)
                translation.pack(writer)  # new quantization bounds are automatically computed
                scaled_position = writer.finish()
                scaled_data[translation_offset:translation_offset + len(scaled_position)] = scaled_position

                reader.align(4)

                rotation = TrackQuaternion(reader, mask.rotation_track_flags, mask.rotation_quantization)
                reader.align(4)

                scale = TrackVector3(reader, mask.scale_track_flags, mask.scale_quantization, 1.0)
                reader.align(4)

                transform_tracks.append(TransformTrack(mask, translation, rotation, scale))

            reader.align(16)

        return list(scaled_data)

    def get_reversed_animation_data(self) -> list[int]:
        """Unpacks the data like `unpack()`, but maintains a spline-reversed version of it as it encounters data.

        Has no side effects (e.g. does NOT modify the raw animation data).
        """
        reader = BinaryReader(bytearray(self.raw_data), byte_order=">" if self.big_endian else "<")
        reversed_data = bytearray(self.raw_data)

        for block_index in range(self.block_count):

            transform_track_masks = [TransformFlags(reader) for _ in range(self.transform_track_count)]

            reader.align(4)

            for i in range(self.transform_track_count):
                mask = transform_track_masks[i]

                translation_offset = reader.position
                translation = TrackVector3(reader, mask.translation_track_flags, mask.translation_quantization, 0.0)
                for axis in "xyz":
                    axis_value = getattr(translation, axis)
                    if isinstance(axis_value, SplineFloat):
                        reversed_axis_value = SplineFloat(reversed(axis_value))
                        setattr(translation, axis, reversed_axis_value)
                    # Else, no need to modify constant axis.
                writer = BinaryWriter()
                translation.pack(writer)  # new quantization bounds are automatically computed
                new_data_segment = writer.finish()
                reversed_data[translation_offset:translation_offset + len(new_data_segment)] = new_data_segment

                reader.align(4)

                rotation_offset = reader.position
                rotation = TrackQuaternion(reader, mask.rotation_track_flags, mask.rotation_quantization)
                if isinstance(rotation.value, SplineQuaternion):
                    rotation.raw_value = list(reversed(rotation.raw_value))
                    rotation.value = SplineQuaternion(reversed(rotation.value))
                # Else, no need to modify constant rotation.
                writer = BinaryWriter()
                rotation.pack_raw(writer)
                new_data_segment = writer.finish()
                reversed_data[rotation_offset:rotation_offset + len(new_data_segment)] = new_data_segment

                reader.align(4)

                scale_offset = reader.position
                scale = TrackVector3(reader, mask.scale_track_flags, mask.scale_quantization, 1.0)
                for axis in "xyz":
                    axis_value = getattr(scale, axis)
                    if isinstance(axis_value, SplineFloat):
                        reversed_axis_value = SplineFloat(reversed(axis_value))
                        setattr(scale, axis, reversed_axis_value)
                    # Else, no need to modify constant axis.
                writer = BinaryWriter()
                scale.pack(writer)  # new quantization bounds are automatically computed
                new_data_segment = writer.finish()
                reversed_data[scale_offset:scale_offset + len(new_data_segment)] = new_data_segment

                reader.align(4)

            reader.align(16)

        return list(reversed_data)
