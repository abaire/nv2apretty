"""Interprets PVIDEO register interactions."""

# ruff: noqa: PLR2004 Magic value used in comparison

from __future__ import annotations

import ctypes
import sys
from typing import NamedTuple


class StateArray(NamedTuple):
    base: int
    stride: int
    num_elements: int


def _make_fields(populated: list[tuple[str, int, int]]) -> list[tuple]:
    """Convert a tuple of the form (name, end_bit, start_bit) to a ctypes bitfield."""
    ret = []
    next_bit = 0
    next_reserved_index = 0
    for name, end, start in populated:
        if start > next_bit:
            ret.append((f"reserved{next_reserved_index}", ctypes.c_uint32, start - next_bit))
            next_reserved_index += 1

        ret.append((name, ctypes.c_uint32, 1 + end - start))
        next_bit = end + 1
    return ret


def _intr(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("BUFFER0", 0, 0),
                ("BUFFER1", 4, 4),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"Buffer0: {bool(self.BUFFER0)}, Buffer1: {bool(self.BUFFER1)}"

    fmt = _BitField(val)
    return f"[0x{addr:x}] = 0x{val:08x}: Interrupt reset: {fmt}"


def _intr_en(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("BUFFER0", 0, 0),
                ("BUFFER1", 4, 4),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"Buffer0: {bool(self.BUFFER0)}, Buffer1: {bool(self.BUFFER1)}"

    fmt = _BitField(val)
    return f"[0x{addr:x}] = 0x{val:08x}: Interrupt enabled: {fmt}"


def _buffer(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("BUFFER0", 0, 0),
                ("BUFFER1", 4, 4),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"Buffer0: {bool(self.BUFFER0)}, Buffer1: {bool(self.BUFFER1)}"

    fmt = _BitField(val)
    return f"[0x{addr:x}] = 0x{val:08x}: Use: {fmt}"


def _stop(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("OVERLAY", 0, 0),
                ("METHOD", 4, 4),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"Overlay active: {bool(self.OVERLAY)}, Stop immediately: {not bool(self.METHOD)}"

    fmt = _BitField(val)
    return f"[0x{addr:x}] = 0x{val:08x}: Stop: {fmt}"


def _base(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("BASE", 26, 6),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"{self.BASE} (0x{self.BASE:08x})"

    index = (addr - 0x900) // 4
    fmt = _BitField(val)

    return f"[0x{addr:x}] = 0x{val:08x}: base[{index}]: {fmt}"


def _limit(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("LIMIT", 26, 6),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"{self.LIMIT} (0x{self.LIMIT:08x})"

    index = (addr - 0x908) // 4
    fmt = _BitField(val)

    return f"[0x{addr:x}] = 0x{val:08x}: limit[{index}]: {fmt}"


def _luminance(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("CONTRAST", 12, 3),
                ("BRIGHTNESS", 25, 16),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"Contrast: 0x{self.CONTRAST:x}, Brightness: 0x{self.BRIGHTNESS:x}"

    index = (addr - 0x910) // 4
    fmt = _BitField(val)

    return f"[0x{addr:x}] = 0x{val:08x}: luminance[{index}]: {fmt}"


def _chrominance(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("SAT_COS", 13, 2),
                ("SAT_SIN", 29, 18),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"COS: 0x{self.SAT_COS:x}, SIN: 0x{self.SAT_SIN:x}"

    index = (addr - 0x918) // 4
    fmt = _BitField(val)

    return f"[0x{addr:x}] = 0x{val:08x}: chrominance[{index}]: {fmt}"


def _color_key(addr: int, size: int, val: int) -> str:
    del size
    return f"[0x{addr:x}] = 0x{val:08x}: color key: 0x{val:08x}"


def _offset(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("VALUE", 31, 6),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"Offset: 0x{self.VALUE:08x}"

    index = (addr - 0x920) // 4
    fmt = _BitField(val)

    return f"[0x{addr:x}] = 0x{val:08x}: offset[{index}]: {fmt}"


def _size_in(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("WIDTH", 11, 0),
                ("HEIGHT", 27, 16),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"{self.WIDTH} x {self.HEIGHT} 2x1 texels"

    index = (addr - 0x928) // 4
    fmt = _BitField(val)

    return f"[0x{addr:x}] = 0x{val:08x}: size_in[{index}]: {fmt}"


def _point_in(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("S", 14, 0),
                ("T", 31, 17),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"{self.S >> 4}.{self.S & 0xF} (0x{self.S:X}), {self.T >> 3}.{self.T & 0x7} (0x{self.T:X})"

    index = (addr - 0x930) // 4
    fmt = _BitField(val)

    return f"[0x{addr:x}] = 0x{val:08x}: point_in[{index}]: {fmt}"


def _ds_dx(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("RATIO", 24, 0),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            if self.RATIO == 0x00100000:
                return "UNITY"

            return f"{self.RATIO / (2**20)} (0x{self.RATIO:08x} {self.RATIO}))"

    index = (addr - 0x938) // 4
    fmt = _BitField(val)

    return f"[0x{addr:x}] = 0x{val:08x}: ds/dx[{index}]: {fmt}"


def _dt_dy(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("RATIO", 24, 0),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            if self.RATIO == 0x00100000:
                return "UNITY"

            return f"{self.RATIO / (2**20)} (0x{self.RATIO:08x} {self.RATIO})"

    index = (addr - 0x940) // 4
    fmt = _BitField(val)

    return f"[0x{addr:x}] = 0x{val:08x}: dt/dy[{index}]: {fmt}"


def _size_out(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("WIDTH", 11, 0),
                ("HEIGHT", 27, 16),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"{self.WIDTH} x {self.HEIGHT}"

    index = (addr - 0x950) // 4
    fmt = _BitField(val)

    return f"[0x{addr:x}] = 0x{val:08x}: size_out[{index}]: {fmt}"


def _point_out(addr: int, size: int, val: int) -> str:
    del size

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("X", 11, 0),
                ("Y", 27, 16),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            return f"{self.X}, {self.Y}"

    index = (addr - 0x948) // 4
    fmt = _BitField(val)

    return f"[0x{addr:x}] = 0x{val:08x}: point_out[{index}]: {fmt}"


def _format(addr: int, size: int, val: int) -> str:
    del size
    # See https://github.com/JayFoxRox/xbox-fps-overlay/blob/6fbbc3cbe947ff5f528218f9dc3de9747835dd7b/main.c#L72
    _colors = [
        "LE_YB8CR8YA8CB8",
        "LE_CR8YB8CB8YA8",
        "LE_EYB8ECR8EYA8ECB8",
        "LE_ECR8EYB8ECB8EYA8",
    ]
    _matrices = ["ITURBT601", "ITURBT709"]

    class _BitField(ctypes.LittleEndianStructure):
        _fields_ = _make_fields(
            [
                ("PITCH", 12, 0),
                ("COLOR", 16, 16),
                ("DISPLAY", 20, 20),
                ("MATRIX", 24, 24),
                ("FIELD", 28, 28),
            ]
        )

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__(**kwargs)

        def __str__(self):
            elements = [f"Pitch: {self.PITCH}", _colors[self.COLOR]]

            if self.DISPLAY == 1:
                elements.append("Color keyed")
            else:
                elements.append("Display always")
            elements.append(f"Matrix: {_matrices[self.MATRIX]}")

            return ", ".join(elements)

    index = (addr - 0x958) // 4
    fmt = _BitField(val)

    return f"[0x{addr:x}] = 0x{val:08x}: format[{index}]: {fmt}"


def _expand_processors(processors):
    ret = {}
    for key, value in processors.items():
        cmd_type = type(key)
        if cmd_type is int:
            ret[key] = value
            continue

        if cmd_type is StateArray:
            base = key.base
            stride = key.stride
            num_elements = key.num_elements
            for i in range(num_elements):
                ret[(base + i * stride)] = value
            continue

    return ret


_PROCESSORS = _expand_processors(
    {
        0x100: _intr,
        0x140: _intr_en,
        0x700: _buffer,
        0x704: _stop,
        StateArray(0x900, 4, 2): _base,
        StateArray(0x908, 4, 2): _limit,
        StateArray(0x910, 4, 2): _luminance,
        StateArray(0x918, 4, 2): _chrominance,
        StateArray(0x920, 4, 2): _offset,
        StateArray(0x928, 4, 2): _size_in,
        StateArray(0x930, 4, 2): _point_in,
        StateArray(0x938, 4, 2): _ds_dx,
        StateArray(0x940, 4, 2): _dt_dy,
        StateArray(0x948, 4, 2): _point_out,
        StateArray(0x950, 4, 2): _size_out,
        StateArray(0x958, 4, 2): _format,
        0xB00: _color_key,
    }
)


def process(address: int, size: int, val: int) -> str:
    """Return a description of the given register value."""
    processor = _PROCESSORS.get(address)
    if processor:
        return processor(address, size, val)

    return f"0x{address:08x}(UNKNOWN) = 0x{val:08x}"
