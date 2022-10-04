"""Decompress and compress animations based on splines, which is most FromSoftware animations.

This code is adapted to Python from SoulsAssetPipeline by Meowmaritus and Katalash for C#:
    https://github.com/Meowmaritus/SoulsAssetPipeline/blob/master/SoulsAssetPipeline/Animation/HKX/SplineCompressedAnimation.cs
Their code was in turn adapted from the Havok Format Library for C++ by PredatorCZ (Lukas Cone):
    https://github.com/PredatorCZ/HavokLib/blob/master/source/hka_spline_decompressor.cpp

I have made many modifications and extensions, including convenience methods for manipulating data.

Original code is copyright (C) 2016-2019 Lukas Cone.
"""
from __future__ import annotations

__all__ = [
    "SplineCompressedAnimationData",
    "SplineTransformTrack",
]

import copy
import logging
import math
import struct
import typing as tp
from enum import IntEnum

from soulstruct.utilities.binary import BinaryReader, BinaryWriter

from soulstruct_havok.utilities.maths import Vector3, Vector4, Quaternion, TRSTransform

_LOGGER = logging.getLogger(__name__)


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

    @classmethod
    def to_string(cls, flags: int) -> str:
        s = " | ".join(flag.name for flag in cls if flag & flags)
        if not s:
            return "Default"
        return s


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


class UnsupportedRotationQuantizationError(Exception):
    """Raised when you try to call `TrackQuaternion.pack()` when its quantization type is not supported."""


def read_uint40(reader: BinaryReader) -> int:
    """Read five bytes, append three zeros, and get the resulting unsigned '64-bit' integer."""
    return struct.unpack("Q", reader.read(5) + b"\0\0\0")[0]


def write_uint40(writer: BinaryWriter, value: int):
    """Pack to 64-bit unsigned integer, then write first five bytes only."""
    if value > ((1 << 40) - 1):
        raise ValueError(f"Value {value} is too large for a 40-bit integer.")
    packed_uint64 = struct.pack("Q", value)
    writer.append(packed_uint64[:5])  # drop last three bytes


def unpack_quantized_quaternion(
    reader: BinaryReader, rotation_quantization_type: RotationQuantizationType
) -> Quaternion:
    if rotation_quantization_type == RotationQuantizationType.Polar32:
        c_val = reader.unpack_value("I")
        return Quaternion.decode_Polar32(c_val)
    elif rotation_quantization_type == RotationQuantizationType.ThreeComp40:
        c_val = read_uint40(reader)
        return Quaternion.decode_ThreeComp40(c_val)
    elif rotation_quantization_type == RotationQuantizationType.ThreeComp48:
        x, y, z = reader.unpack_value("3h")
        return Quaternion.decode_ThreeComp48(x, y, z)
    elif rotation_quantization_type == RotationQuantizationType.Uncompressed:
        return Quaternion(reader.unpack("4f"))
    raise NotImplementedError(f"Cannot read quantized quaternion of type: {rotation_quantization_type}")


def pack_quantized_quaternion(
    writer: BinaryWriter, quaternion: Quaternion, rotation_quantization_type: RotationQuantizationType
):
    if rotation_quantization_type == RotationQuantizationType.ThreeComp40:
        c_val = quaternion.encode_ThreeComp40()
        write_uint40(writer, c_val)
        return
    raise UnsupportedRotationQuantizationError(f"Cannot quantize quaternion type: {rotation_quantization_type}")


def find_knot_span(degree: int, value: float, control_point_count: int, knots: list[int]) -> int:
    """Find the starting knot index of the span that contains the parameter `value` using a binary search.

    Algorithm A2.1 The NURBS Book 2nd edition, page 68
    """
    if value >= knots[control_point_count]:
        return control_point_count - 1

    low = degree
    high = control_point_count
    guess = (low + high) // 2

    while value < knots[guess] or value >= knots[guess + 1]:
        if value < knots[guess]:
            high = guess  # search interval [low, guess]
        else:
            low = guess  # search interval [guess, high]
        guess = (low + high) // 2

    return guess  # found knot index


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
        value += control_points[knot_span_index - i] * n[i]
    return value


class SplineHeader:
    """Holds information shared by all three axes of a translation/scale vector, or one rotation."""

    degree: int  # usually 3, i.e. fourth-order, i.e. cubic spline
    knots: list[int]

    def __init__(self, reader: BinaryReader):
        control_point_count = reader.unpack_value("h") + 1  # packed count seems to exclude a control point
        self.degree = reader.unpack_value("B")
        self.knots = [reader.unpack_value("B") for _ in range(control_point_count + self.degree + 1)]

    def pack(self, big_endian=False) -> bytes:
        fmt = f"{'>' if big_endian else '<'}HB{len(self.knots)}B"
        return struct.pack(fmt, self.control_point_count - 1, self.degree, *self.knots)

    @property
    def control_point_count(self) -> int:
        return len(self.knots) - self.degree - 1

    def __repr__(self):
        return f"SplineHeader<{self.control_point_count}>(degree={self.degree}, knots={self.knots})"


class SplineQuaternion(list[Quaternion]):
    """List of 4D `Quaternion` control points."""

    def __repr__(self):
        return f"SplineQuaternion<{len(self)}>"


class SplineFloat(list[float]):
    """List of control points in a single axis."""

    def __repr__(self):
        return f"SplineFloat<{len(self)}>"


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
    scalar_quantization_type: ScalarQuantizationType

    quantized_bounds: dict[str, tp.Optional[list[int, int]]]  # maps axis names ("x") to an optional [min, max] list

    def __init__(
        self,
        x: SplineFloat | float,
        y: SplineFloat | float,
        z: SplineFloat | float,
        header: SplineHeader = None,
        scalar_quantization_type=ScalarQuantizationType.Bits16,
    ):
        self.x = x
        self.y = y
        self.z = z
        self.spline_header = header
        self.scalar_quantization_type = scalar_quantization_type

    @classmethod
    def unpack(
        cls, reader: BinaryReader, track_flags: int, scalar_quantization_type: ScalarQuantizationType, default: float
    ) -> TrackVector3:
        if track_flags & (TrackFlags.SplineX | TrackFlags.SplineY | TrackFlags.SplineZ):
            spline_header = SplineHeader(reader)
            reader.align(4)
        else:
            spline_header = None

        track_vector = cls(default, default, default, spline_header, scalar_quantization_type)

        quantized_bounds = {"x": None, "y": None, "z": None}
        for axis, spline_flag, static_flag in zip(
            ("x", "y", "z"),
            (TrackFlags.SplineX, TrackFlags.SplineY, TrackFlags.SplineZ),
            (TrackFlags.StaticX, TrackFlags.StaticY, TrackFlags.StaticZ),
        ):
            if track_flags & spline_flag:
                quantized_bounds[axis] = list(reader.unpack("2f"))
                setattr(track_vector, axis, SplineFloat())  # will be filled below
            elif track_flags & static_flag:
                setattr(track_vector, axis, reader.unpack_value("f"))
            else:
                setattr(track_vector, axis, default)  # generally 0.0 (translation) or 1.0 (scale)

        if spline_header:
            for c in range(spline_header.control_point_count):
                for axis, spline_flag in zip(
                    ("x", "y", "z"),
                    (TrackFlags.SplineX, TrackFlags.SplineY, TrackFlags.SplineZ),
                ):
                    if track_flags & spline_flag:
                        spline = getattr(track_vector, axis)  # type: SplineFloat
                        q_float = track_vector.unpack_quantized_float(reader, *quantized_bounds[axis])
                        spline.append(q_float)

        return track_vector

    def get_value_at_frame(self, frame: float, axis: str) -> float:
        axis = axis.lower()
        if axis not in "xyz":
            raise ValueError(f"Axis must be 'x', 'y', or 'z', not: {axis}")
        axis_value = getattr(self, axis)
        if isinstance(axis_value, SplineFloat):
            knot_span = find_knot_span(self.spline_header.degree, frame, len(axis_value), self.spline_header.knots)
            return get_single_point(knot_span, self.spline_header.degree, frame, self.spline_header.knots, axis_value)
            # return get_single_point_new(self.spline_header.degree, frame, self.spline_header.knots, axis_value)
        else:
            return axis_value  # float

    def get_vector_at_frame(self, frame: float) -> Vector3:
        return Vector3([self.get_value_at_frame(frame, axis) for axis in "xyz"])

    def set_to_static_vector(self, xyz):
        self.x, self.y, self.z = xyz
        self.spline_header = None

    def translate(self, translate: Vector3):
        """Simply add the appropriate component of `translate` to every value."""
        for axis in "xyz":
            axis_value = getattr(self, axis)
            delta_value = getattr(translate, axis)
            if isinstance(axis_value, SplineFloat):
                new_axis_value = SplineFloat(c + delta_value for c in axis_value)
            else:
                new_axis_value = axis_value + delta_value
            setattr(self, axis, new_axis_value)

    def rotate(self, rotate: Quaternion):
        """Rotate static values or control points around local origin (parent bone) with `rotate`.

        This is a little more complicated because we need to combine control points across splines, but ultimately not
        that difficult, since any splines in this track must have the same number of control points.
        """
        if not self.spline_header:
            # No splines. Can just rotate static vector.
            self.x, self.y, self.z = rotate.rotate_vector(Vector3(self.x, self.y, self.z))
            return

        # Static values may end up becoming splines, and (less likely) vice versa.
        old_splines = []  # will contain x, y, z splines
        for axis in "xyz":
            axis_value = getattr(self, axis)
            if isinstance(axis_value, SplineFloat):
                old_splines.append(axis_value)
            else:  # constant list for zipping below
                old_splines.append([axis_value] * self.spline_header.control_point_count)
        new_control_points = []  # will contain (x, y, z) control points to be unzipped below
        for x, y, z in zip(*old_splines):
            rotated_control_point = rotate.rotate_vector(Vector3(x, y, z))
            new_control_points.append(rotated_control_point)
        spline_x = SplineFloat([v.x for v in new_control_points])
        spline_y = SplineFloat([v.y for v in new_control_points])
        spline_z = SplineFloat([v.z for v in new_control_points])

        # Check if any of the new spline dimensions are static (unlikely, unless rotations are exactly axis-aligned).
        self.x = spline_x[0] if len(set(spline_x)) == 1 else spline_x
        self.y = spline_y[0] if len(set(spline_y)) == 1 else spline_y
        self.z = spline_z[0] if len(set(spline_z)) == 1 else spline_z
        if all(isinstance(v, float) for v in (self.x, self.y, self.z)):
            # Spline header no longer needed. (Though I don't see how this could possibly happen!)
            self.spline_header = None

    def scale(self, factor: float | Vector3):
        """Scale static values or control points by `factor` or its appropriate component if it's a vector."""
        for axis in "xyz":
            axis_value = getattr(self, axis)
            scale_value = factor if isinstance(factor, float) else getattr(factor, axis)
            if isinstance(axis_value, SplineFloat):
                scaled_axis_value = SplineFloat(c * scale_value for c in axis_value)
            else:
                scaled_axis_value = axis_value * scale_value
            setattr(self, axis, scaled_axis_value)

    def reverse(self):
        """Reverses all spline control points."""
        for axis in "xyz":
            axis_value = getattr(self, axis)
            if isinstance(axis_value, SplineFloat):
                reversed_axis_value = SplineFloat(reversed(axis_value))
                setattr(self, axis, reversed_axis_value)

    def swap_axes(self, axis1: str, axis2: str):
        axis1_value = getattr(self, axis1)
        axis2_value = getattr(self, axis2)
        setattr(self, axis1, axis2_value)
        setattr(self, axis2, axis1_value)

    def get_flags(self, default: float) -> int:
        track_flags = 0
        for axis in ("x", "y", "z"):
            axis_value = getattr(self, axis)
            if isinstance(axis_value, SplineFloat):
                track_flags |= getattr(TrackFlags, f"Spline{axis.upper()}")
            elif axis_value != default:
                track_flags |= getattr(TrackFlags, f"Static{axis.upper()}")
            # Otherwise, leave as zero (default static value).
        return track_flags

    def pack(self, default: float, big_endian=False) -> bytes:
        writer = BinaryWriter()

        if self.spline_header:
            writer.append(self.spline_header.pack(big_endian))
            writer.pad_align(4)

        quantized_bounds = {"x": None, "y": None, "z": None}

        for axis in ("x", "y", "z"):
            axis_value = getattr(self, axis)
            if isinstance(axis_value, SplineFloat):
                # Compute new quantized bounds from final min/max in control points.
                min_control_point = min(axis_value)
                max_control_point = max(axis_value)
                quantized_bounds[axis] = [min_control_point, max_control_point]
                writer.pack("2f", min_control_point, max_control_point)
            elif axis_value != default:
                writer.pack("f", axis_value)
            # don't write anything if value is default (no flags for axis)

        if self.spline_header is not None:
            for i in range(self.spline_header.control_point_count):
                for axis in ("x", "y", "z"):
                    axis_value = getattr(self, axis)
                    if isinstance(axis_value, SplineFloat):
                        self.pack_quantized_float(writer, axis_value[i], *quantized_bounds[axis])

        return writer.finish()

    def unpack_quantized_float(
        self, reader: BinaryReader, minimum: float, maximum: float,
    ):
        ratio = -1.0
        if self.scalar_quantization_type == ScalarQuantizationType.Bits8:
            ratio = reader.unpack_value("B") / 255.0
        elif self.scalar_quantization_type == ScalarQuantizationType.Bits16:
            ratio = reader.unpack_value("H") / 65535.0
        return minimum + (maximum - minimum) * ratio

    def pack_quantized_float(
        self, writer: BinaryWriter, q_float: float, minimum: float, maximum: float,
    ):
        if minimum == maximum:
            if q_float == minimum:
                ratio = 0.0
            else:
                raise ValueError(f"Min/max values for quantization of float {q_float} are equal: {minimum}")
        else:
            ratio = (q_float - minimum) / (maximum - minimum)
        if self.scalar_quantization_type == ScalarQuantizationType.Bits8:
            writer.pack("B", int(ratio * 255))
        elif self.scalar_quantization_type == ScalarQuantizationType.Bits16:
            writer.pack("H", int(ratio * 65535))
        else:
            raise ValueError(f"Invalid `ScalarQuantizationType`: {self.scalar_quantization_type}")

    def __repr__(self):
        return f"TrackVector3({self.x}, {self.y}, {self.z})"


class TrackQuaternion:

    spline_header: tp.Optional[SplineHeader]
    raw_value: tp.Union[None, bytes, list[bytes]]  # one or multiple quantized quaternions
    value: tp.Union[None, SplineQuaternion, Quaternion]

    def __init__(
        self,
        value: SplineQuaternion | Quaternion,
        header: SplineHeader = None,
        rotation_quantization_type=RotationQuantizationType.ThreeComp40,
        raw_value=b"",
    ):
        """Holds data for a track's rotation.

        Note that this is ALWAYS either one static `Quaternion` or a 4D `SplineQuaternion`, unlike `TrackVector3`, which
        can use static or spline data for each dimension. However, `track_flags` may still only mark certain dimensions
        as splines, using an algorithm that I have tried to replicate faithfully in `pack()`.

        We keep `raw_value` for encoded quaternions so the animation data can still be repacked (with quaternions not
        edited) if the quaternion type can't be encoded yet.
        """
        if isinstance(value, SplineQuaternion) and not header:
            raise ValueError("Must give a `header` to `TrackQuaterion` if `value` is a `SplineQuaterion`.")

        self.value = value
        self.spline_header = header
        self.rotation_quantization_type = rotation_quantization_type
        self.raw_value = raw_value

    @classmethod
    def unpack(cls, reader: BinaryReader, track_flags: int, rotation_quantization_type: RotationQuantizationType):

        quantized_size = rotation_quantization_type.get_rotation_byte_count()
        if track_flags & (TrackFlags.SplineX | TrackFlags.SplineY | TrackFlags.SplineZ | TrackFlags.SplineW):
            header = SplineHeader(reader)
            reader.align(rotation_quantization_type.get_rotation_align())
            with reader.temp_offset(reader.position):
                raw_value = [reader.read(quantized_size) for _ in range(header.control_point_count)]
            value = SplineQuaternion(
                unpack_quantized_quaternion(reader, rotation_quantization_type)
                for _ in range(header.control_point_count)
            )
        elif track_flags & (TrackFlags.StaticX | TrackFlags.StaticY | TrackFlags.StaticZ | TrackFlags.StaticW):
            header = None
            raw_value = reader.peek(quantized_size)
            value = unpack_quantized_quaternion(reader, rotation_quantization_type)
        else:
            header = None
            raw_value = b""
            value = Quaternion.identity()  # default rotation

        return TrackQuaternion(value, header, rotation_quantization_type, raw_value)

    def get_quaternion_at_frame(self, frame: float) -> Quaternion:
        if isinstance(self.value, SplineQuaternion):
            knot_span = find_knot_span(self.spline_header.degree, frame, len(self.value), self.spline_header.knots)
            return get_single_point(knot_span, self.spline_header.degree, frame, self.spline_header.knots, self.value)
        else:
            return self.value  # Quaternion

    def set_to_static_quaternion(self, xyzw):
        self.value = Quaternion(*xyzw)
        self.spline_header = None

    def rotate(self, rotate: Quaternion):
        """Simply left-multiply every value by `rotate`."""
        if isinstance(self.value, Quaternion):
            self.value = rotate * self.value
        else:
            self.value = SplineQuaternion([rotate * quat for quat in self.value])

    def reverse(self):
        """Reverses all control points if `value` is a `SplineQuaternion`.

        Changes both `value` and `raw_value`, so data with an unsupported quantization method can still be reversed.
        """
        if isinstance(self.value, SplineQuaternion):
            self.raw_value = list(reversed(self.raw_value))
            self.value = SplineQuaternion(reversed(self.value))

    def swap_axes(self, axis1: str, axis2: str):
        if isinstance(self.value, SplineQuaternion):
            for quat in self.value:
                axis1_value = getattr(quat, axis1)
                axis2_value = getattr(quat, axis2)
                setattr(quat, axis1, axis2_value)
                setattr(quat, axis2, axis1_value)
        else:
            quat = self.value
            axis1_value = getattr(quat, axis1)
            axis2_value = getattr(quat, axis2)
            setattr(quat, axis1, axis2_value)
            setattr(quat, axis2, axis1_value)

    def get_flags(self) -> int:
        """`SplineW` or `StaticW` is always flagged for the corresponding type, but other dimensions are only flagged
        if any control points (or the single static value) have non-zero data in that dimension."""
        if isinstance(self.value, SplineQuaternion):  # spline
            flags = TrackFlags.SplineW
            for quat in self.value:
                if quat.x != 0.0:
                    flags |= TrackFlags.SplineX
                if quat.y != 0.0:
                    flags |= TrackFlags.SplineY
                if quat.z != 0.0:
                    flags |= TrackFlags.SplineZ
            return flags
        elif isinstance(self.value, Quaternion):  # static
            if self.value == Quaternion.identity():
                return 0  # default
            flags = 0
            if self.value.x != 0.0:
                flags |= TrackFlags.StaticX
            if self.value.y != 0.0:
                flags |= TrackFlags.StaticY
            if self.value.z != 0.0:
                flags |= TrackFlags.StaticZ
            if self.value.w < 0.999:  # note 'default' value for W is 1.0 (with some tolerance)
                flags |= TrackFlags.StaticW
            return flags
        raise TypeError("`TrackQuaternion.value` was not a `Quaternion` or `SplineQuaternion`.")

    def pack(self, big_endian=False) -> bytes:
        """Write track quaternion data and return `TrackFlags` bit field for header.

        Uses an independent `BinaryWriter` in case an unsupported quantization error is raised.
        """
        writer = BinaryWriter(big_endian=big_endian)

        if isinstance(self.value, SplineQuaternion):  # spline
            if self.spline_header is None:
                raise ValueError("No `SplineHeader` present, but data is `SplineQuaternion`.")
            writer.append(self.spline_header.pack())
            writer.pad_align(self.rotation_quantization_type.get_rotation_align())
            for control_point_quaternion in self.value:
                pack_quantized_quaternion(writer, control_point_quaternion, self.rotation_quantization_type)
        elif isinstance(self.value, Quaternion):  # static
            # No spline header.
            if self.value != Quaternion.identity():
                pack_quantized_quaternion(writer, self.value, self.rotation_quantization_type)

        return writer.finish()

    def pack_raw(self, big_endian=False) -> bytes:
        """Substitute method that supports reversal, but not actual quaternion modification."""
        writer = BinaryWriter(big_endian=big_endian)

        if self.spline_header:
            writer.append(self.spline_header.pack())
            writer.pad_align(self.rotation_quantization_type.get_rotation_align())

        if isinstance(self.raw_value, list):
            writer.append(b"".join(self.raw_value))
        elif isinstance(self.raw_value, bytes):
            writer.append(self.raw_value)
        else:
            pass  # identity, nothing to pack

        return writer.finish()

    def __repr__(self) -> str:
        if isinstance(self.value, SplineQuaternion):
            # return f"TrackQuaternion(\n    " + "\n    ".join(str(v) for v in self.value) + "\n)"
            return f"TrackQuaternion({self.value})"
        return f"TrackQuaternion({self.value.x}, {self.value.y}, {self.value.z}, {self.value.w})"


class TrackHeader:

    translation_quantization: ScalarQuantizationType
    rotation_quantization: RotationQuantizationType
    scale_quantization: ScalarQuantizationType
    translation_track_flags: int
    rotation_track_flags: int
    scale_track_flags: int

    def __init__(self, reader: BinaryReader = None):
        """Holds information about how each track is compressed and packed (e.g. splines vs. static values)."""

        # Some sensible defaults.
        self.translation_quantization = ScalarQuantizationType.Bits16
        self.rotation_quantization = RotationQuantizationType.ThreeComp40
        self.scale_quantization = ScalarQuantizationType.Bits16
        self.translation_track_flags = 0
        self.rotation_track_flags = 0
        self.scale_track_flags = 0

        if reader is not None:
            self.unpack(reader)

    def unpack(self, reader: BinaryReader):
        quantization_types = reader.unpack_value("B")
        self.translation_quantization = ScalarQuantizationType(quantization_types & 0b0000_0011)  # lowest two
        self.rotation_quantization = RotationQuantizationType(quantization_types >> 2 & 0b0000_1111)  # middle four
        self.scale_quantization = ScalarQuantizationType(quantization_types >> 6 & 0b0000_0011)  # highest two
        self.translation_track_flags = reader.unpack_value("B")
        self.rotation_track_flags = reader.unpack_value("B")
        self.scale_track_flags = reader.unpack_value("B")

    def pack(self, big_endian=False) -> bytes:
        quantization_types = self.translation_quantization & 0b11
        quantization_types |= (self.rotation_quantization & 0b1111) << 2
        quantization_types |= (self.scale_quantization & 0b11) << 6
        fmt = ('>' if big_endian else '<') + "BBBB"
        return struct.pack(
            fmt, quantization_types, self.translation_track_flags, self.rotation_track_flags, self.scale_track_flags
        )

    @classmethod
    def from_track(cls, track: SplineTransformTrack):
        header = cls()
        header.translation_quantization = track.translation.scalar_quantization_type
        header.rotation_quantization = track.rotation.rotation_quantization_type
        header.scale_quantization = track.scale.scalar_quantization_type
        header.translation_track_flags = track.translation.get_flags(default=0.0)
        header.rotation_track_flags = track.rotation.get_flags()
        header.scale_track_flags = track.scale.get_flags(default=1.0)
        return header

    def __repr__(self) -> str:
        return (
            f"TrackHeader(\n"
            f"    translation_quantization = {self.translation_quantization.name}\n"
            f"       rotation_quantization = {self.rotation_quantization.name}\n"
            f"          scale_quantization = {self.scale_quantization.name}\n"
            f"     translation_track_flags = {TrackFlags.to_string(self.translation_track_flags)}\n"
            f"        rotation_track_flags = {TrackFlags.to_string(self.rotation_track_flags)}\n"
            f"           scale_track_flags = {TrackFlags.to_string(self.scale_track_flags)}\n"
            f")"
        )


class SplineTransformTrack:
    """Single track of animation data, usually corresponding to a single bone.

    Just a container for the three transform types.
    """

    translation: TrackVector3
    rotation: TrackQuaternion
    scale: TrackVector3

    def __init__(
        self, translation: TrackVector3, rotation: TrackQuaternion, scale: TrackVector3
    ):
        self.translation = translation
        self.rotation = rotation
        self.scale = scale

    @classmethod
    def from_static_transform(cls, translation: Vector3 | Vector4, rotation: Quaternion, scale: Vector3 | Vector4):
        """Construct simple static tracks from given values."""
        translation_track = TrackVector3(translation.x, translation.y, translation.z)
        rotation_track = TrackQuaternion(rotation)
        scale_track = TrackVector3(scale.x, scale.y, scale.z)
        return cls(translation_track, rotation_track, scale_track)

    def apply_transform(self, transform: TRSTransform):
        """Apply components of `transform` to all values in appropriate tracks."""
        self.translation.translate(transform.translation)
        self.rotation.rotate(transform.rotation)
        self.scale.scale(transform.scale)

    def apply_transform_to_translate(self, transform: TRSTransform):
        """Order is scale, rotation, translation."""
        self.translation.scale(transform.scale)
        self.translation.rotate(transform.rotation)
        self.translation.translate(transform.translation)

    def apply_transform_to_rotation(self, transform: TRSTransform):
        self.rotation.rotate(transform.rotation)

    def get_quat_transform_at_frame(self, frame: float) -> TRSTransform:
        translation = self.translation.get_vector_at_frame(frame)
        rotation = self.rotation.get_quaternion_at_frame(frame)
        scale = self.scale.get_vector_at_frame(frame)
        return TRSTransform(translation, rotation, scale)

    def copy(self) -> SplineTransformTrack:
        return copy.deepcopy(self)

    def __repr__(self) -> str:
        return (
            f"TransformTrack(\n"
            f"    translation={self.translation},\n"
            f"    rotation={self.rotation},\n"
            f"    scale={self.scale},\n"
            f")"
        )


class SplineCompressedAnimationData:

    blocks: list[list[SplineTransformTrack | None]]

    def __init__(self, data: list[int], transform_track_count: int, block_count: int, big_endian=False):
        """Read a spline-compressed animation (e.g. `hkaSplineCompressedAnimation["data"]`) to a list of "blocks" of
        frames. Each block can hold some maximum number of frames (e.g. 256). There may only be one block.

        Each block in `blocks` is a list of `TrackHeader` instances, then corresponding `TransformTrack` instances.
        """
        self.raw_data = data
        self.big_endian = big_endian
        self.blocks = []
        reader = BinaryReader(bytearray(self.raw_data), byte_order=">" if big_endian else "<")
        self.unpack(reader, block_count, transform_track_count)

    def unpack(self, reader: BinaryReader, block_count: int, transform_track_count: int):

        for block_index in range(block_count):

            # Track info (flags and quantization types) are stored first.
            track_headers = [TrackHeader(reader) for _ in range(transform_track_count)]
            reader.align(4)

            transform_tracks = []  # type: list[SplineTransformTrack]
            for i in range(transform_track_count):
                header = track_headers[i]
                translation = TrackVector3.unpack(
                    reader, header.translation_track_flags, header.translation_quantization, 0.0
                )
                reader.align(4)
                rotation = TrackQuaternion.unpack(
                    reader, header.rotation_track_flags, header.rotation_quantization
                )
                reader.align(4)
                scale = TrackVector3.unpack(
                    reader, header.scale_track_flags, header.scale_quantization, 1.0
                )
                reader.align(4)

                transform_tracks.append(SplineTransformTrack(translation, rotation, scale))

            reader.align(16)

            self.blocks.append(transform_tracks)

    def pack(self) -> tuple[list[int], int, int]:
        """Pack spline-compressed animation data to binary data, then return it as a list of integers for assignment
        to the `data` member of a `hkaSplineCompressedAnimation` object, along with the final transform track count and
        block count.
        """
        if not self.blocks:
            raise ValueError("Cannot pack empty spline-compressed animation data.")

        writer = BinaryWriter(big_endian=self.big_endian)
        block_count = len(self.blocks)
        transform_track_count = len(self.blocks[0])
        for block in self.blocks:
            if len(block) != transform_track_count:
                raise ValueError("Animation data blocks do not have equal numbers of transform tracks.")

        for block in self.blocks:
            for track in block:
                # Null track (permitted by this class) has a default header and no other data.
                # Represents zero translation, identity rotation, and identity scale.
                header = TrackHeader() if track is None else TrackHeader.from_track(track)
                packed_header = header.pack(self.big_endian)
                writer.append(packed_header)
            writer.pad_align(4)
            for track in block:
                if track is None:
                    continue  # null track (all defaults, no data written)
                writer.append(track.translation.pack(default=0.0, big_endian=self.big_endian))
                writer.pad_align(4)
                try:
                    writer.append(track.rotation.pack(self.big_endian))
                except UnsupportedRotationQuantizationError:
                    writer.append(track.rotation.pack_raw(self.big_endian))
                writer.pad_align(4)
                writer.append(track.scale.pack(default=1.0, big_endian=self.big_endian))
            writer.pad_align(16)

        data = list(writer.finish())

        return data, block_count, transform_track_count

    def to_interleaved_transforms(self, frame_count: int, max_frames_per_block: int) -> list[list[TRSTransform]]:
        """Decompresses the spline data by computing the `QsTransform` at each frame from any splines.

        Returns a list of lists (blocks) of `QsTransform` instances sorted into sub-lists by frame. Each list holds
        all the `QsTransforms` (generally one per bone) for that frame, as mapped by an `hkaAnimationBinding` instance
        in the HKX file.
        """
        # TODO: Track count should be passed in, rather than continuing to assume one block only.
        transform_track_count = len(self.blocks[0])
        for block in self.blocks:
            if len(block) != transform_track_count:
                _LOGGER.warning("Animation data blocks do not have equal numbers of transform tracks.")

        frame_transforms = [[] for _ in range(frame_count)]  # type: list[list[TRSTransform]]

        for frame_index in range(frame_count):
            frame = float((frame_index % frame_count) % max_frames_per_block)
            block_index = int((frame_index % frame_count) / max_frames_per_block)
            block = self.blocks[block_index]

            for transform_track_index in range(transform_track_count):
                track = block[transform_track_index]
                if frame >= frame_count - 1:
                    # Need to interpolate between this final frame and the first frame.
                    current_frame_transform = track.get_quat_transform_at_frame(float(math.floor(frame)))
                    first_frame_transform = self.blocks[0][transform_track_index].get_quat_transform_at_frame(frame=0.0)
                    frame_transforms[frame_index].append(
                        TRSTransform.lerp(current_frame_transform, first_frame_transform, t=frame % 1)
                    )
                else:
                    # Normal frame.
                    frame_transforms[frame_index].append(track.get_quat_transform_at_frame(frame))

        return frame_transforms

    def apply_transform_to_all_track_translations(self, transform: TRSTransform):
        """Apply `transform` to the translation data of each track.

        Use this to manipulate bone positions relative to their parents, rather than modifying their actual frames.
        """
        for block in self.blocks:
            for track in block:
                track.apply_transform_to_translate(transform)

    def apply_transform_to_all_track_rotations(self, transform: TRSTransform):
        for block in self.blocks:
            for track in block:
                track.apply_transform_to_rotation(transform)

    def apply_transform_to_all_tracks(self, transform: TRSTransform):
        """NOTE: This will apply the transform to the ENTIRE TRANSFORM of each track, not just the translation.

        Use this to modify bone frames directly.
        """
        for block in self.blocks:
            for track in block:
                track.apply_transform(transform)

    def reverse(self):
        """Reverses all spline data by simply reversing the lists of control points. Static values are unchanged."""
        for block in self.blocks:
            for track in block:
                track.translation.reverse()
                track.rotation.reverse()
                track.scale.reverse()

    def get_track_strings(self):
        s = f"SplineCompressedAnimationData<{len(self.blocks[0])} transform tracks>(\n"
        for b, block in enumerate(self.blocks):
            s += f"    Block {b} = [\n"
            for t, track in enumerate(block):
                header = TrackHeader.from_track(track)
                flags_lines = repr(header).split("\n")
                s += f"        Track {t}: {flags_lines[0]}\n"
                for line in flags_lines[1:]:
                    s += f"        {line}\n"
            s += f"    ]\n"
        s += ")"
        return s
