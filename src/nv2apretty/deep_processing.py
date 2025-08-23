# Defines processors for class/op/param tuples.

# ruff: noqa: PLR2004 Magic value used in comparison
# ruff: noqa: RUF012 Mutable class attributes should be annotated with `typing.ClassVar`
# ruff: noqa: ARG003 Unused class method argument
# ruff: noqa: UP031 Use format specifiers instead of percent format
# ruff: noqa: F403 `import *` used; unable to detect undefined names

from __future__ import annotations

import ctypes
import sys

from nv2apretty.extracted_data import *


def _process_transform_execution_mode(_nv_class, _nv_op, nv_param):
    param_info = "0x%X" % nv_param

    class BitField(ctypes.LittleEndianStructure):
        _fields_ = [
            ("MODE", ctypes.c_uint32, 2),
            ("RANGE_MODE", ctypes.c_uint32, 30),
        ]

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__()

        def __str__(self):
            elements = []

            if not self.MODE:
                elements.append("Fixed")
            elif self.MODE == 2:
                elements.append("Program")

            if not self.RANGE_MODE:
                elements.append("Range:User")
            else:
                elements.append("Range:Priv")

            return "{%s}" % ", ".join(elements)

    fmt = BitField(nv_param)
    return param_info + f" {fmt}"


def _process_set_zmin_max_control(_nv_class, _nv_op, nv_param):
    param_info = "0x%X" % nv_param

    class BitField(ctypes.LittleEndianStructure):
        _fields_ = [
            ("CULL_NEAR_FAR", ctypes.c_uint32, 4),
            ("ZCLAMP", ctypes.c_uint32, 4),
            ("CULL_IGNORE_W", ctypes.c_uint32, 4),
        ]

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__()

        def __str__(self):
            elements = []

            elements.append(f"Cull near/far:{bool(self.CULL_NEAR_FAR)}")

            zclamp = "Clamp" if self.ZCLAMP else "Cull"
            elements.append(f"ZClamp:{zclamp}")
            elements.append(f"IgnoreW:{bool(self.CULL_IGNORE_W)}")

            return "{%s}" % ", ".join(elements)

    fmt = BitField(nv_param)
    return param_info + f" {fmt}"


def _process_set_occlude_zstencil(_nv_class, _nv_op, nv_param):
    param_info = "0x%X" % nv_param

    class BitField(ctypes.LittleEndianStructure):
        _fields_ = [
            ("Z", ctypes.c_uint32, 1),
            ("STENCIL", ctypes.c_uint32, 1),
        ]

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__()

        def __str__(self):
            elements = []

            elements.append("OccludeZ: %d" % self.Z)
            elements.append("OccludeStencil: %d" % self.STENCIL)
            return "{%s}" % ", ".join(elements)

    fmt = BitField(nv_param)
    return param_info + f" {fmt}"


def _process_set_dot_rgbmapping(_nv_class, _nv_op, nv_param):
    param_info = "0x%X" % nv_param

    class BitField(ctypes.LittleEndianStructure):
        _fields_ = [
            ("STAGE_1", ctypes.c_uint32, 4),
            ("STAGE_2", ctypes.c_uint32, 4),
            ("STAGE_3", ctypes.c_uint32, 4),
        ]

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__()

        def __str__(self):
            elements = []

            mode = [
                "0:1",
                "-1:1 MS",
                "-1:1 GL",
                "-1:1 NV",
                "HiLo 1",
                "HiLo Hemisphere MS",
                "HiLo Hemisphere GL",
                "HiLo Hemisphere NV",
            ]
            elements.append(f"Stage1: {mode[self.STAGE_1]}")
            elements.append(f"Stage2: {mode[self.STAGE_2]}")
            elements.append(f"Stage3: {mode[self.STAGE_3]}")

            return "{%s}" % ", ".join(elements)

    fmt = BitField(nv_param)
    return param_info + f" {fmt}"


def expand_vertex_data_format(nv_param):
    param_info = "0x%X" % nv_param

    class BitField(ctypes.LittleEndianStructure):
        _fields_ = [
            ("TYPE", ctypes.c_uint32, 4),
            ("SIZE", ctypes.c_uint32, 4),
            ("STRIDE", ctypes.c_uint32, 24),
        ]

        def __new__(cls, *args, **kwargs):
            if args:
                return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
            return super().__new__()

        def __str__(self):
            elements = []

            if self.SIZE == 0:
                elements.append("DISABLED")
            else:
                if self.TYPE == 0:
                    elements.append("Type:uint8-D3D")
                elif self.TYPE == 1:
                    elements.append("Type:S1")
                elif self.TYPE == 2:
                    elements.append("Type:Float")
                elif self.TYPE == 4:
                    elements.append("Type:uint8-Ogl")
                elif self.TYPE == 5:
                    elements.append("Type:S32K")
                elif self.TYPE == 6:
                    elements.append("Type:CMP")

                elif self.SIZE == 1:
                    elements.append("Size:1")
                elif self.SIZE == 2:
                    elements.append("Size:2")
                elif self.SIZE == 3:
                    elements.append("Size:3")
                elif self.SIZE == 4:
                    elements.append("Size:4")
                elif self.SIZE == 7:
                    elements.append("Size:3W")

                elements.append("Stride:%d" % self.STRIDE)

            return "{%s}" % ", ".join(elements)

    fmt = BitField(nv_param)
    return param_info + f" {fmt}"
