from __future__ import annotations

# ruff: noqa: PLR2004 Magic value used in comparison
import struct
from dataclasses import dataclass
from typing import NamedTuple

from nv2apretty.extracted_data import (
    NV097_SET_VERTEX_DATA_ARRAY_FORMAT,
)

# Vertex data array format constants
# Opcode range: NV097_SET_VERTEX_DATA_ARRAY_FORMAT (0x1760) .. (0x179C) for 16 vertex inputs
NV097_SET_VERTEX_DATA_ARRAY_FORMAT_BASE = NV097_SET_VERTEX_DATA_ARRAY_FORMAT
NV097_SET_VERTEX_DATA_ARRAY_FORMAT_COUNT = 16
NV097_SET_VERTEX_DATA_ARRAY_FORMAT_STRIDE = 4

# Vertex attribute types
TYPE_UB_D3D = 0
TYPE_SHORT_NORMALIZE = 1
TYPE_FLOAT = 2
TYPE_UB_OPENGL = 4
TYPE_SHORT = 5
TYPE_3_COMPONENT_PACKED = 6

_TYPE_NAMES = {
    TYPE_UB_D3D: "UB D3D",
    TYPE_SHORT_NORMALIZE: "ShortNormalize",
    TYPE_FLOAT: "Float",
    TYPE_UB_OPENGL: "UB OpenGL",
    TYPE_SHORT: "Short",
    TYPE_3_COMPONENT_PACKED: "3ComponentPacked",
}


@dataclass
class VertexFormat:
    attr_type: int
    size: int
    stride: int

    @property
    def is_disabled(self) -> bool:
        return self.size == 0

    @classmethod
    def from_param(cls, param: int) -> VertexFormat:
        attr_type = param & 0xF
        size = (param >> 4) & 0xF
        stride = (param >> 8) & 0x00FFFFFF
        return cls(attr_type=attr_type, size=size, stride=stride)


class DwordTarget(NamedTuple):
    input_index: int
    attr_type: int
    description: str


class InlineArrayTracker:
    """Tracks vertex array format assignments and decodes INLINE_ARRAY dwords."""

    def __init__(self) -> None:
        self._formats: dict[int, VertexFormat] = {}
        self._draw_active: bool = False
        self._layout_dwords: list[DwordTarget] = []
        self._layout_index: int = 0

    def set_format(self, input_index: int, format_param: int) -> None:
        """Records an NV097_SET_VERTEX_DATA_ARRAY_FORMAT register assignment."""
        fmt = VertexFormat.from_param(format_param)
        self._formats[input_index] = fmt
        self._rebuild_layout()

    def begin_draw(self) -> None:
        """Called on NV097_SET_BEGIN_END (start of draw)."""
        self._draw_active = True
        self._layout_index = 0

    def end_draw(self) -> None:
        """Called on NV097_SET_BEGIN_END (end of draw)."""
        self._draw_active = False
        self._layout_index = 0

    def _rebuild_layout(self) -> None:
        """Reconstructs the expected sequence of dwords per vertex from active formats."""
        self._layout_dwords = []

        # Inputs are processed in ascending order: v0 .. v15
        for input_index in range(NV097_SET_VERTEX_DATA_ARRAY_FORMAT_COUNT):
            fmt = self._formats.get(input_index)
            if not fmt or fmt.is_disabled:
                continue

            attr_type = fmt.attr_type
            size = fmt.size

            if attr_type == TYPE_FLOAT:
                # 1 dword per component
                for comp in range(size):
                    self._layout_dwords.append(
                        DwordTarget(
                            input_index=input_index,
                            attr_type=attr_type,
                            description=f"v{input_index}[{comp}]" if size > 1 else f"v{input_index}",
                        )
                    )
            elif attr_type in (TYPE_UB_D3D, TYPE_UB_OPENGL):
                # 4 bytes = 1 dword for size <= 4
                self._layout_dwords.append(
                    DwordTarget(
                        input_index=input_index,
                        attr_type=attr_type,
                        description=f"v{input_index}",
                    )
                )
            elif attr_type in (TYPE_SHORT, TYPE_SHORT_NORMALIZE):
                # 2 shorts per dword
                if size <= 2:
                    self._layout_dwords.append(
                        DwordTarget(
                            input_index=input_index,
                            attr_type=attr_type,
                            description=f"v{input_index}[0..{size - 1}]" if size > 1 else f"v{input_index}[0]",
                        )
                    )
                else:
                    self._layout_dwords.append(
                        DwordTarget(
                            input_index=input_index,
                            attr_type=attr_type,
                            description=f"v{input_index}[0..1]",
                        )
                    )
                    self._layout_dwords.append(
                        DwordTarget(
                            input_index=input_index,
                            attr_type=attr_type,
                            description=f"v{input_index}[2..{size - 1}]" if size > 3 else f"v{input_index}[2]",
                        )
                    )
            elif attr_type == TYPE_3_COMPONENT_PACKED:
                self._layout_dwords.append(
                    DwordTarget(
                        input_index=input_index,
                        attr_type=attr_type,
                        description=f"v{input_index}",
                    )
                )
            else:
                # Unknown / unhandled type: fallback single dword
                self._layout_dwords.append(
                    DwordTarget(
                        input_index=input_index,
                        attr_type=attr_type,
                        description=f"v{input_index}",
                    )
                )

    def process_inline_array_param(self, nv_param: int) -> str:
        """Formats an INLINE_ARRAY param based on current vertex attribute expectations."""
        if not self._layout_dwords:
            # Fallback to standard float param expansion if no formats configured
            val = struct.unpack("<f", struct.pack("<I", nv_param))[0]
            return f"{val} <0x{nv_param:x}>"

        target = self._layout_dwords[self._layout_index]
        self._layout_index = (self._layout_index + 1) % len(self._layout_dwords)

        formatted_val = self._format_value(target.attr_type, nv_param)
        return f"{target.description}: {formatted_val} <0x{nv_param:x}>"

    @staticmethod
    def _format_value(attr_type: int, nv_param: int) -> str:
        if attr_type == TYPE_FLOAT:
            val = struct.unpack("<f", struct.pack("<I", nv_param))[0]
            return f"{val}"
        if attr_type in (TYPE_UB_D3D, TYPE_UB_OPENGL):
            # 4 unsigned bytes
            b = list(struct.unpack("<4B", struct.pack("<I", nv_param)))
            return f"{b}"
        if attr_type in (TYPE_SHORT, TYPE_SHORT_NORMALIZE):
            s = list(struct.unpack("<2h", struct.pack("<I", nv_param)))
            return f"{s}"
        if attr_type == TYPE_3_COMPONENT_PACKED:
            # 11-11-10 signed packed normal components
            # Bits: X[0..10], Y[11..21], Z[22..31]
            x_raw = nv_param & 0x7FF
            y_raw = (nv_param >> 11) & 0x7FF
            z_raw = (nv_param >> 22) & 0x3FF
            # Sign extend 11 bits:
            x = x_raw - 0x800 if (x_raw & 0x400) else x_raw
            y = y_raw - 0x800 if (y_raw & 0x400) else y_raw
            z = z_raw - 0x400 if (z_raw & 0x200) else z_raw
            return f"[{x}, {y}, {z}]"

        # Fallback
        val = struct.unpack("<f", struct.pack("<I", nv_param))[0]
        return f"{val}"
