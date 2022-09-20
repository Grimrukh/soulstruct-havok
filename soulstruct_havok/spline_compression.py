"""Decompress and compress animations based on splines, which is most FromSoftware animations.

This code is adapted to Python from SoulsAssetPipeline by Meowmaritus and Katalash for C#:
    https://github.com/Meowmaritus/SoulsAssetPipeline/blob/master/SoulsAssetPipeline/Animation/HKX/SplineCompressedAnimation.cs
Their code was in turn adapted from the Havok Format Library for C++ by PredatorCZ (Lukas Cone):
    https://github.com/PredatorCZ/HavokLib/blob/master/source/hka_spline_decompressor.cpp

I have made many modifications and extensions, including convenience methods for manipulating data.

Original code is copyright (C) 2016-2019 Lukas Cone.
"""
from __future__ import annotations

__all__ = ["SplineCompressedAnimationData"]

import logging
import math
import struct
import typing as tp
from enum import IntEnum

from soulstruct.utilities.conversion import floatify
from soulstruct.utilities.binary import BinaryReader, BinaryWriter
from soulstruct.utilities.maths import Vector3, Quaternion, QuatTransform

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


def decode_quat_Polar32(c_val: int) -> Quaternion:
    r_mask = (1 << 10) - 1
    r_frac = 1.0 / r_mask
    phi_frac = math.pi / 4 / 511.0

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


def decode_quat_ThreeComp48(x: int, y: int, z: int) -> Quaternion:
    mask = (1 << 15) - 1
    fractal = 0.000043161

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
    """Read five bytes, append three zeros, and get the resulting unsigned '64-bit' integer."""
    return struct.unpack("Q", reader.read(5) + b"\0\0\0")[0]


def write_uint40(writer: BinaryWriter, value: int):
    """Pack to 64-bit unsigned integer, then write first five bytes only."""
    if value > ((1 << 40) - 1):
        raise ValueError(f"Value {value} is too large for a 40-bit integer.")
    packed_uint64 = struct.pack("Q", value)
    writer.append(packed_uint64[:40])  # drop last three bytes


def decode_quat_ThreeComp40(c_val: int) -> Quaternion:
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

    mask = (1 << 12) - 1  # twelve 1-bits (4095)
    positive_mask = mask >> 1  # eleven 1-bits (2047)
    fractal = math.sqrt(2) / 4096  # min and max values in signed 12-bits integer are [-sqrt(2), sqrt(2)].

    x = c_val & mask  # lowest twelve bits
    y = (c_val >> 12) & mask  # next twelve bits
    z = (c_val >> 24) & mask  # next twelve bits
    implicit_dimension = (c_val >> 36) & 0b0011  # next two bits
    implicit_negative = ((c_val >> 38) & 1) > 0  # final two bits

    # Subtract positive mask from raw 12-bit values (make them signed).
    x -= positive_mask
    y -= positive_mask
    z -= positive_mask

    # Multiply masked values by fractal to convert to [-sqrt(2), sqrt(2)] range.
    quaternion = [x * fractal, y * fractal, z * fractal]  # still missing implicit dimension

    # Calculate implicit dimension from unit magnitude.
    # The implicit dimension is always the one with the largest absolute value (outside the +/- sqrt(2) range).
    implicit_squared = 1.0 - quaternion[0] ** 2 - quaternion[1] ** 2 - quaternion[2] ** 2
    # Clamp to zero (means this was NOT a unit quaternion!) or square root.
    implicit = 0.0 if implicit_squared <= 0.0 else math.sqrt(implicit_squared)
    # Apply sign.
    if implicit_negative:
        implicit *= -1
    # Insert implicit dimension.
    quaternion.insert(implicit_dimension, implicit)
    q = Quaternion(quaternion)

    return q


def encode_quat_ThreeComp40(quaternion: Quaternion) -> int:
    """Pack `quaternion` into a 40-bit value using ThreeComp40 method."""
    mask = (1 << 12) - 1  # twelve 1-bits (4095)
    positive_mask = mask >> 1  # eleven 1-bits (2047)
    fractal = math.sqrt(2) / 4096
    implicit_dimension = quaternion.largest_abs_value_index()
    implicit_negative = int(quaternion[implicit_dimension] < 0)
    encoded_floats = []  # type: list[int]
    for i in range(4):
        if i == implicit_dimension:
            continue  # skipped
        encoded = round(quaternion[i] / fractal)  # int between -2048 and +2047
        encoded += positive_mask  # signed to unsigned (range 0-4095)
        encoded_floats.append(encoded)

    # Join everything together.
    c_val = encoded_floats[0] & mask
    c_val += (encoded_floats[1] & mask) << 12
    c_val += (encoded_floats[2] & mask) << 24
    c_val += implicit_dimension << 36
    c_val += implicit_negative << 38
    return c_val


def unpack_quantized_quaternion(
    reader: BinaryReader, rotation_quantization_type: RotationQuantizationType
) -> Quaternion:
    if rotation_quantization_type == RotationQuantizationType.Polar32:
        c_val = reader.unpack_value("I")
        return decode_quat_Polar32(c_val)
    elif rotation_quantization_type == RotationQuantizationType.ThreeComp40:
        c_val = read_uint40(reader)
        return decode_quat_ThreeComp40(c_val)
    elif rotation_quantization_type == RotationQuantizationType.ThreeComp48:
        x, y, z = reader.unpack_value("3h")
        return decode_quat_ThreeComp48(x, y, z)
    elif rotation_quantization_type == RotationQuantizationType.Uncompressed:
        return Quaternion(reader.unpack("4f"))
    raise NotImplementedError(f"Cannot read quantized quaternion of type: {rotation_quantization_type}")


def pack_quantized_quaternion(
    writer: BinaryWriter, quaternion: Quaternion, rotation_quantization_type: RotationQuantizationType
):
    if rotation_quantization_type == RotationQuantizationType.ThreeComp40:
        c_val = encode_quat_ThreeComp40(quaternion)
        write_uint40(writer, c_val)
        return
    raise UnsupportedRotationQuantizationError(f"Cannot quantize quaternion type: {rotation_quantization_type}")


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

    def scale(self, factor: float):
        """Scale static values or control points by `factor`."""
        for axis in "xyz":
            axis_value = getattr(self, axis)
            if isinstance(axis_value, SplineFloat):
                scaled_axis_value = SplineFloat(c * factor for c in axis_value)
            else:
                scaled_axis_value = axis_value * factor
            setattr(self, axis, scaled_axis_value)

    def reverse(self):
        """Reverses all spline control points."""
        for axis in "xyz":
            axis_value = getattr(self, axis)
            if isinstance(axis_value, SplineFloat):
                reversed_axis_value = SplineFloat(reversed(axis_value))
                setattr(self, axis, reversed_axis_value)

    def get_flags(self) -> int:
        track_flags = 0
        for axis in ("x", "y", "z"):
            axis_value = getattr(self, axis)
            if isinstance(axis_value, SplineFloat):
                track_flags |= getattr(TrackFlags, f"Spline{axis.upper()}")
            elif axis_value != self.default:
                track_flags |= getattr(TrackFlags, f"Static{axis.upper()}")
            # Otherwise, leave as zero (default static value).
        return track_flags

    def pack(self, writer: BinaryWriter):
        if self.spline_header:
            self.spline_header.pack(writer, alignment=4)

        for axis in ("x", "y", "z"):
            axis_value = getattr(self, axis)
            if isinstance(axis_value, SplineFloat):
                # Compute new quantized bounds from final min/max in control points.
                min_control_point = min(axis_value)
                max_control_point = max(axis_value)
                self.quantized_bounds[axis] = [min_control_point, max_control_point]
                writer.pack("2f", min_control_point, max_control_point)
            elif axis_value != self.default:
                writer.pack("f", axis_value)
            # don't write anything if value is default (no flags for axis)

        if self.spline_header:
            for i in range(self.spline_header.control_point_count):
                for axis in ("x", "y", "z"):
                    axis_value = getattr(self, axis)
                    if isinstance(axis_value, SplineFloat):
                        self.pack_quantized_float(writer, axis_value[i], *self.quantized_bounds[axis])

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
        """Holds data for a track's rotation.

        Note that this is ALWAYS either one static `Quaternion` or a 4D `SplineQuaternion`, unlike `TrackVector3`, which
        can use static or spline data for each dimension.

        We keep `raw_value` for encoded quaternions so the animation data can still be repacked (with quaternions not
        edited) if the quaternion type can't be encoded yet.
        """
        self.rotation_quantization = rotation_quantization
        quantized_size = self.rotation_quantization.get_rotation_byte_count()
        if track_flags & (TrackFlags.SplineX | TrackFlags.SplineY | TrackFlags.SplineZ | TrackFlags.SplineW):
            self.spline_header = SplineHeader(reader)
            reader.align(rotation_quantization.get_rotation_align())
            with reader.temp_offset(reader.position):
                self.raw_value = [reader.read(quantized_size) for _ in range(self.spline_header.control_point_count)]
            self.value = SplineQuaternion(
                unpack_quantized_quaternion(reader, self.rotation_quantization)
                for _ in range(self.spline_header.control_point_count)
            )
        elif track_flags & (TrackFlags.StaticX | TrackFlags.StaticY | TrackFlags.StaticZ | TrackFlags.StaticW):
            self.spline_header = None
            self.raw_value = reader.read_without_advancing(quantized_size)
            self.value = unpack_quantized_quaternion(reader, self.rotation_quantization)
        else:
            self.spline_header = None
            self.raw_value = None
            self.value = Quaternion.identity()  # default rotation

    def get_quaternion_at_frame(self, frame: float) -> Quaternion:
        if isinstance(self.value, SplineQuaternion):
            knot_span = find_knot_span(self.spline_header.degree, frame, len(self.value), self.spline_header.knots)
            return get_single_point(knot_span, self.spline_header.degree, frame, self.spline_header.knots, self.value)
        else:
            return self.value  # Quaternion

    def reverse(self):
        """Reverses all control points if `value` is a `SplineQuaternion`.

        Changes both `value` and `raw_value`, so data with an unsupported quantization method can still be reversed.
        """
        if isinstance(self.value, SplineQuaternion):
            self.raw_value = list(reversed(self.raw_value))
            self.value = SplineQuaternion(reversed(self.value))

    def get_flags(self) -> int:
        if isinstance(self.value, SplineQuaternion):  # spline
            return TrackFlags.SplineX | TrackFlags.SplineY | TrackFlags.SplineZ | TrackFlags.SplineW
        elif isinstance(self.value, Quaternion):  # static
            return TrackFlags.StaticX | TrackFlags.StaticY | TrackFlags.StaticZ | TrackFlags.StaticW
        else:
            return 0  # default

    def pack(self, big_endian=False) -> bytes:
        """Write track quaternion data and return `TrackFlags` bit field for header.

        Uses an independent `BinaryWriter` in case an unsupported quantization error is raised.
        """
        writer = BinaryWriter(big_endian=big_endian)

        if isinstance(self.value, SplineQuaternion):  # spline
            if self.spline_header is None:
                raise ValueError("No `SplineHeader` present, but data is `SplineQuaternion`.")
            self.spline_header.pack(writer, alignment=self.rotation_quantization.get_rotation_align())
            for control_point_quaternion in self.value:
                pack_quantized_quaternion(writer, control_point_quaternion, self.rotation_quantization)
        elif isinstance(self.value, Quaternion):  # static
            # No spline header.
            pack_quantized_quaternion(writer, self.value, self.rotation_quantization)
        else:
            # Default static quaternion (identity). Nothing to write.
            pass

        return writer.finish()

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

    def pack(self, writer: BinaryWriter):
        quantization_types = self.translation_quantization & 0b11
        quantization_types |= (self.rotation_quantization & 0b1111) << 2
        quantization_types |= (self.scale_quantization & 0b11) << 6
        writer.pack("B", quantization_types)
        writer.pack("B", self.translation_track_flags)
        writer.pack("B", self.rotation_track_flags)
        writer.pack("B", self.scale_track_flags)

    @classmethod
    def from_track(cls, track: TransformTrack):
        header = cls()
        header.translation_quantization = track.translation.scalar_quantization
        header.rotation_quantization = track.rotation.rotation_quantization
        header.scale_quantization = track.scale.scalar_quantization
        header.translation_track_flags = track.translation.get_flags()
        header.rotation_track_flags = track.rotation.get_flags()
        header.scale_track_flags = track.scale.get_flags()
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


class TransformTrack:
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

        Each block in `blocks` is a list of `TrackHeader` instances, then corresponding `TransformTrack` instances.
        """
        self.raw_data = data
        self.big_endian = big_endian
        self.blocks = []  # type: list[list[TransformTrack]]
        reader = BinaryReader(bytearray(self.raw_data), byte_order=">" if big_endian else "<")
        self.unpack(reader, block_count, transform_track_count)

    def unpack(self, reader: BinaryReader, block_count: int, transform_track_count: int):

        for block_index in range(block_count):

            # Track info (flags and quantization types) are stored first.
            track_headers = [TrackHeader(reader) for _ in range(transform_track_count)]
            reader.align(4)

            transform_tracks = []  # type: list[TransformTrack]
            for i in range(transform_track_count):
                header = track_headers[i]
                translation = TrackVector3(reader, header.translation_track_flags, header.translation_quantization, 0.0)
                reader.align(4)
                rotation = TrackQuaternion(reader, header.rotation_track_flags, header.rotation_quantization)
                reader.align(4)
                scale = TrackVector3(reader, header.scale_track_flags, header.scale_quantization, 1.0)
                reader.align(4)

                transform_tracks.append(TransformTrack(translation, rotation, scale))

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
                header = TrackHeader.from_track(track)
                header.pack(writer)
            writer.pad_align(4)
            for track in block:
                track.translation.pack(writer)
                writer.pad_align(4)
                try:
                    writer.append(track.rotation.pack(self.big_endian))
                except UnsupportedRotationQuantizationError:
                    track.rotation.pack_raw(writer)
                writer.pad_align(4)
                track.scale.pack(writer)
            writer.pad_align(16)

        data = list(writer.finish())

        return data, block_count, transform_track_count

    def to_transform_track_lists(self, frame_count: int, max_frames_per_block: int) -> list[list[QuatTransform]]:
        """Decompresses the spline data by computing the `QuatTransform` at each frame from any splines.

        Returns a list of lists (blocks) of `QuatTransform` instances sorted into sub-lists by transform track. Each
        transform track affects a different bone, as mapped by a `hkaAnimationBinding` instance in animation HKX.
        """
        transform_track_count = len(self.blocks[0])
        for block in self.blocks:
            if len(block) != transform_track_count:
                _LOGGER.warning("Animation data blocks do not have equal numbers of transform tracks.")

        track_transforms = [[] for _ in range(transform_track_count)]  # type: list[list[QuatTransform]]

        for i in range(frame_count):
            frame = float((i % frame_count) % max_frames_per_block)
            block_index = int((i % frame_count) / max_frames_per_block)
            block = self.blocks[block_index]

            for transform_track_index in range(transform_track_count):
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

    def scale(self, factor: float):
        """Multiply all translation static values and control points by `factor`, in place.

        Note that this does NOT touch transform scale data, despite the name. It scales all translations directly and
        leaves transform scales as-is.
        """
        for block in self.blocks:
            for track in block:
                track.translation.scale(factor)

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
