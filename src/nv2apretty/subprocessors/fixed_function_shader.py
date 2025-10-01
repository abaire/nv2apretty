from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Any

from nv2apretty.extracted_data import (
    _PROCESSORS,
    CLASS_TO_COMMAND_PROCESSOR_MAP,
    NV097_SET_COLOR_MATERIAL,
    NV097_SET_FOG_ENABLE,
    NV097_SET_FOG_GEN_MODE,
    NV097_SET_LIGHT_CONTROL,
    NV097_SET_LIGHT_ENABLE_MASK,
    NV097_SET_LIGHTING_ENABLE,
    NV097_SET_POINT_PARAMS,
    NV097_SET_POINT_PARAMS_ENABLE,
    NV097_SET_POINT_SIZE,
    NV097_SET_POINT_SMOOTH_ENABLE,
    NV097_SET_SKIN_MODE,
    NV097_SET_SPECULAR_ENABLE,
    NV097_SET_TEXGEN_Q,
    NV097_SET_TEXGEN_R,
    NV097_SET_TEXGEN_S,
    NV097_SET_TEXGEN_T,
    NV097_SET_TEXTURE_MATRIX_ENABLE,
    NV097_SET_TWO_SIDE_LIGHT_EN,
    StateArray,
    StructStateArray,
)

# A set of the base NV097 opcodes to be tracked.
# This list will be expanded by iterating through the CLASS_TO_COMMAND_PROCESSOR_MAP.
_BASE_TRACKED_NV097_OPS = {
    NV097_SET_COLOR_MATERIAL,
    NV097_SET_FOG_ENABLE,
    NV097_SET_FOG_GEN_MODE,
    NV097_SET_LIGHT_CONTROL,
    NV097_SET_LIGHT_ENABLE_MASK,
    NV097_SET_LIGHTING_ENABLE,
    NV097_SET_POINT_PARAMS,
    NV097_SET_POINT_PARAMS_ENABLE,
    NV097_SET_POINT_SIZE,
    NV097_SET_POINT_SMOOTH_ENABLE,
    NV097_SET_SKIN_MODE,
    NV097_SET_SPECULAR_ENABLE,
    NV097_SET_TWO_SIDE_LIGHT_EN,
    NV097_SET_TEXTURE_MATRIX_ENABLE,
    NV097_SET_TEXGEN_S,
    NV097_SET_TEXGEN_T,
    NV097_SET_TEXGEN_R,
    NV097_SET_TEXGEN_Q,
}

_TRACKED_NV097_OPS: set[int] = set()
_OP_TO_INFO_MAP: dict[int, Any] = {}


def _populate_tracked_ops():
    """Populates the _TRACKED_NV097_OPS set by expanding arrays."""
    if _TRACKED_NV097_OPS:
        return

    kelvin_ops = CLASS_TO_COMMAND_PROCESSOR_MAP.get(0x97, {})
    for op_info in kelvin_ops:
        op_type = type(op_info)

        base_op = op_info
        if op_type in [StateArray, StructStateArray]:
            base_op = op_info.base

        if base_op not in _BASE_TRACKED_NV097_OPS:
            continue

        _OP_TO_INFO_MAP[base_op] = op_info

        if op_type is int:
            _TRACKED_NV097_OPS.add(op_info)
            continue

        if op_type is StateArray:
            for i in range(op_info.num_elements):
                _TRACKED_NV097_OPS.add(op_info.base + i * op_info.stride)
            continue

        if op_type is StructStateArray:
            base = op_info.base
            for _ in range(op_info.struct_count):
                for i in range(op_info.num_elements):
                    _TRACKED_NV097_OPS.add(base + i * op_info.stride)
                base += op_info.struct_stride
            continue


_populate_tracked_ops()


def as_float(int_val: int) -> float:
    packed_bytes = struct.pack("!I", int_val)
    return struct.unpack("!f", packed_bytes)[0]


@dataclass
class FixedFunctionPipelineState:
    """Represents the fixed function pipeline state of a single frame."""

    _state: dict[int, int] = field(default_factory=dict)

    def update(self, nv_op: int, nv_param: int):
        if nv_op not in _TRACKED_NV097_OPS:
            return
        self._state[nv_op] = nv_param

    def get_raw_value(self, opcode: int, default: Any | None = None) -> Any | None:
        """Looks up a value or array of values for the given opcode, optionally expanding them into a string."""
        op_info = _OP_TO_INFO_MAP.get(opcode)
        op_type = type(op_info)

        if op_info is None or op_type is int:
            return self._state.get(opcode, default)

        if op_type is StateArray:
            raw_values = []
            for i in range(op_info.num_elements):
                val = self._state.get(op_info.base + i * op_info.stride, default)
                if val is None:
                    return None
                raw_values.append(val)

            return raw_values

        if op_type is StructStateArray:
            raw_values = []
            base = op_info.base
            for _ in range(op_info.struct_count):
                element_values = []
                for i in range(op_info.num_elements):
                    val = self._state.get(base + i * op_info.stride, default)
                    if val is None:
                        return None
                    element_values.append(val)
                raw_values.append(element_values)
                base += op_info.struct_stride

            return raw_values

        msg = f"Unsupported op_type '{op_type}'"
        raise ValueError(msg)

    def _process(
        self, opcode: int, default_raw_value: Any | None = None, default_string_value: str = "<UNKNOWN>"
    ) -> str | list[str] | list[list[str]]:
        raw_value = self.get_raw_value(opcode, default_raw_value)
        op_info = _OP_TO_INFO_MAP.get(opcode)
        op_type = type(op_info)

        if op_info is None or op_type is int:
            if raw_value is None:
                return default_string_value

            op = opcode
            processor = _PROCESSORS.get((0x97, op))

            return processor(0, 0x97, raw_value) if processor else f"0x{raw_value:X}"

        if op_type is StateArray:
            if raw_value is None:
                return [default_string_value] * op_info.num_elements

            processed_values: list[str] = []
            for i, param in enumerate(raw_value):
                op = op_info.base + i * op_info.stride
                processor = _PROCESSORS.get((0x97, op))
                processed_values.append(processor(0, 0x97, param) if processor else f"0x{param:X}")
            return processed_values

        if op_type is StructStateArray:
            if raw_value is None:
                return [default_string_value] * op_info.num_elements

            processed_struct_values: list[list[str]] = []
            base = op_info.base
            for struct_element in raw_value:
                processed_struct: list[str] = []
                for i, param in enumerate(struct_element):
                    op = base + i * op_info.stride
                    processor = _PROCESSORS.get((0x97, op))
                    processed_struct.append(processor(0, 0x97, param) if processor else f"0x{param:X}")
                processed_struct_values.append(processed_struct)
                base += op_info.struct_stride
            return processed_struct_values

        msg = f"Unsupported op_type '{op_type}'"
        raise ValueError(msg)

    def __str__(self):
        ret = []

        lighting_enabled = self.get_raw_value(NV097_SET_LIGHTING_ENABLE, 0) != 0
        ret.append(f"  Lighting: {lighting_enabled}")
        if lighting_enabled:
            ret.append(f"\tTwo sided: {bool(self.get_raw_value(NV097_SET_TWO_SIDE_LIGHT_EN, 0))}")
            ret.append(f"\tColor material: {self._process(NV097_SET_COLOR_MATERIAL)}")
            ret.append(f"\tLight control: {self._process(NV097_SET_LIGHT_CONTROL)}")
            ret.append(f"\tLight enable: {self._process(NV097_SET_LIGHT_ENABLE_MASK)}")

        ret.append(f"Specular enable: {bool(self.get_raw_value(NV097_SET_SPECULAR_ENABLE, 0))}")

        fog_enabled = self.get_raw_value(NV097_SET_FOG_ENABLE, 0) != 0
        ret.append(f"Fog enable: {fog_enabled}")
        if fog_enabled:
            ret.append(f"\tFog gen mode: {self._process(NV097_SET_FOG_GEN_MODE)}")

        ret.append(f"Skinning mode: {self._process(NV097_SET_SKIN_MODE)}")

        point_params_enabled = self.get_raw_value(NV097_SET_POINT_PARAMS_ENABLE, 0) != 0
        ret.append(f"Point params enable: {point_params_enabled}")
        if point_params_enabled:
            ret.append(f"\tPoint size: {self._process(NV097_SET_POINT_SIZE)}")

            params = self.get_raw_value(NV097_SET_POINT_PARAMS)
            if params:
                point_scale_factor_a = as_float(params[0])
                point_scale_factor_b = as_float(params[1])
                point_scale_factor_c = as_float(params[2])
                ret.append(
                    f"\tSize multiplier: sqrt(1/({point_scale_factor_a} + {point_scale_factor_b} * Deye + {point_scale_factor_c} * (Deye^2))"
                )

                point_size_range = as_float(params[3])
                ret.append(f"\tSize range: {point_size_range}")
                point_scale_bias = as_float(params[6])
                ret.append(f"\tScale bias: {point_scale_bias}")
                point_min_size = as_float(params[7])
                ret.append(f"\tMinimum size: {point_min_size}")

        if bool(self.get_raw_value(NV097_SET_POINT_SMOOTH_ENABLE, 0)):
            ret.append("Point smooth (point sprites) enabled")

        ret.append("TexGen: ")
        s_vals = self._process(NV097_SET_TEXGEN_S)
        t_vals = self._process(NV097_SET_TEXGEN_T)
        r_vals = self._process(NV097_SET_TEXGEN_R)
        q_vals = self._process(NV097_SET_TEXGEN_Q)
        if all([s_vals, t_vals, r_vals, q_vals]):
            ret.extend(
                f"\tS[{i}] {s_vals[i]}, T[{i}] {t_vals[i]} R[{i}]: {r_vals[i]} Q[{i}]: {q_vals[i]}"
                for i in range(len(s_vals))
            )

        tex_matrix_en = self.get_raw_value(NV097_SET_TEXTURE_MATRIX_ENABLE)
        if tex_matrix_en:
            texture_matrix_data = [f"[{index}: {bool(item)}]" for index, item in enumerate(tex_matrix_en)]
            ret.append(f"TextureMatrix: {', '.join(texture_matrix_data)}")

        return "\n  ".join(ret)
