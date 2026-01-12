from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from nv2apretty.extracted_data import (
    CLASS_TO_COMMAND_PROCESSOR_MAP,
    PROCESSORS,
    StateArray,
    StructStateArray,
)

if TYPE_CHECKING:
    from collections.abc import Callable


def as_float(int_val: int) -> float:
    packed_bytes = struct.pack("!I", int_val)
    return struct.unpack("!f", packed_bytes)[0]


def _expand_command_map(nv_commands: set[int]) -> tuple[dict[int, int | StateArray | StructStateArray], set[int]]:
    """Expands nv_commands into {command_address: info_struct} and {expanded command ID}."""

    command_to_info: dict[int, Any] = {}
    expanded_commands: set[int] = set()

    kelvin_ops: dict[int | StateArray | StructStateArray, Callable] = CLASS_TO_COMMAND_PROCESSOR_MAP.get(0x97, {})
    for op_info in kelvin_ops:
        base_op = op_info.base if isinstance(op_info, StateArray | StructStateArray) else op_info

        if base_op not in nv_commands:
            continue

        command_to_info[base_op] = op_info

        if isinstance(op_info, int):
            expanded_commands.add(op_info)
            continue

        if isinstance(op_info, StateArray):
            for i in range(op_info.num_elements):
                expanded_commands.add(op_info.base + i * op_info.stride)
            continue

        if isinstance(op_info, StructStateArray):
            base = op_info.base
            for _ in range(op_info.struct_count):
                for i in range(op_info.num_elements):
                    expanded_commands.add(base + i * op_info.stride)
                base += op_info.struct_stride
            continue

    return command_to_info, expanded_commands


@dataclass
class PipelineState:
    """Baseclass for capture of nv2a GPU state."""

    # Maps NV097 operations to a raw invocation count
    _counter_state: dict[int, int] = field(default_factory=dict)

    # Maps NV097 operations to the most recently set parameter value
    _state: dict[int, int] = field(default_factory=dict)

    _command_to_info: dict[int, int | StateArray | StructStateArray] = field(default_factory=dict)
    _command_filter: set[int] = field(default_factory=set)

    _last_draw_primitive: int | None = None

    def _initialize(self, tracked_ops: set[int]):
        self.command_to_info, self.command_filter = _expand_command_map(tracked_ops)

    def update(self, nv_op: int, nv_param: int):
        self._counter_state[nv_op] = self._counter_state.get(nv_op, 0) + 1
        if nv_op not in self.command_filter:
            return
        self._state[nv_op] = nv_param

    def draw_begin(self, primitive_mode: int):
        """Should be invoked whenever a NV097_SET_BEGIN_END with a non-end parameter is processed"""
        self._last_draw_primitive = primitive_mode

    def draw_end(self):
        """Should be invoked whenever a NV097_SET_BEGIN_END with an 'end' parameter is processed."""
        self._counter_state.clear()

    def get_total_command_count(self) -> int:
        """Returns the total number of unfiltered commands processed since the last draw ended."""
        return sum(self._counter_state.values())

    def _get_count(self, opcode: int) -> int:
        """Looks up the number of times that the given opcode was called since the current draw started."""
        return self._counter_state.get(opcode, 0)

    def _get_raw_value(self, opcode: int, default: Any | None = None) -> Any | None:
        """Looks up a value or array of values for the given opcode, optionally expanding them into a string."""
        op_info = self.command_to_info.get(opcode)

        if op_info is None or isinstance(op_info, int):
            return self._state.get(opcode, default)

        if isinstance(op_info, StateArray):
            raw_values = []
            for i in range(op_info.num_elements):
                val = self._state.get(op_info.base + i * op_info.stride, default)
                if val is None:
                    return None
                raw_values.append(val)

            return raw_values

        if isinstance(op_info, StructStateArray):
            raw_values = []
            base = op_info.base
            for _ in range(op_info.struct_count):
                element_values: list[Any] = []
                for i in range(op_info.num_elements):
                    val = self._state.get(base + i * op_info.stride, default)
                    if val is None:
                        element_values = [None] * op_info.num_elements
                        break
                    element_values.append(val)
                raw_values.append(element_values)
                base += op_info.struct_stride

            return raw_values

        msg = f"Unsupported op_info type '{type(op_info)}'"
        raise ValueError(msg)

    def _process(
        self, opcode: int, default_raw_value: Any | None = None, default_string_value: str = "<UNKNOWN>"
    ) -> str | list[str] | list[list[str]]:
        raw_value = self._get_raw_value(opcode, default_raw_value)
        op_info = self.command_to_info.get(opcode)
        op_type = type(op_info)

        if op_info is None or op_type is int:
            if raw_value is None:
                return default_string_value

            op = opcode
            processor = PROCESSORS.get((0x97, op))

            return processor(0, 0x97, raw_value) if processor else f"0x{raw_value:X}"

        if isinstance(op_info, StateArray):
            if raw_value is None:
                return [default_string_value] * op_info.num_elements

            processed_values: list[str] = []
            for i, param in enumerate(raw_value):
                op = op_info.base + i * op_info.stride
                processor = PROCESSORS.get((0x97, op))
                processed_values.append(processor(0, 0x97, param) if processor else f"0x{param:X}")
            return processed_values

        if isinstance(op_info, StructStateArray):
            if raw_value is None:
                return [default_string_value] * op_info.num_elements

            processed_struct_values: list[list[str]] = []
            base = op_info.base
            for struct_element in raw_value:
                processed_struct: list[str] = []
                for i, param in enumerate(struct_element):
                    op = base + i * op_info.stride
                    if param is None:
                        processed_struct.append(default_string_value)
                    else:
                        processor = PROCESSORS.get((0x97, op))
                        processed_struct.append(processor(0, 0x97, param) if processor else f"0x{param:X}")
                processed_struct_values.append(processed_struct)
                base += op_info.struct_stride
            return processed_struct_values

        msg = f"Unsupported op_type '{op_type}'"
        raise ValueError(msg)
