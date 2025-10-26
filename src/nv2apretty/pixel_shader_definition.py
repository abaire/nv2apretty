"""Prettify D3DPIXELSHADERDEF binary dumps.

This program reads packed D3DPIXELSHADERDEF structs and converts them to human-readable color combiner explanations.
"""

# ruff: noqa: T201 `print` found
# ruff: noqa: TRY300 Consider moving this statement to an `else` block
# ruff: noqa: PLR2004 Magic value used in comparison

from __future__ import annotations

import argparse
import ast
import logging
import os
import struct
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass
from typing import TYPE_CHECKING

from nv2apretty.subprocessors.color_combiner import (
    NV097_SET_COMBINER_ALPHA_ICW_0,
    NV097_SET_COMBINER_ALPHA_OCW_0,
    NV097_SET_COMBINER_COLOR_ICW_0,
    NV097_SET_COMBINER_COLOR_OCW_0,
    NV097_SET_COMBINER_CONTROL,
    NV097_SET_COMBINER_FACTOR0_0,
    NV097_SET_COMBINER_FACTOR1_0,
    NV097_SET_COMBINER_SPECULAR_FOG_CW0,
    NV097_SET_COMBINER_SPECULAR_FOG_CW1,
    NV097_SET_SPECULAR_FOG_FACTOR_0,
    NV097_SET_SPECULAR_FOG_FACTOR_1,
    CombinerState,
)

if TYPE_CHECKING:
    from collections.abc import Collection

logger = logging.getLogger(__name__)

_STRUCT_FORMAT = "<60I"
_STRUCT_SIZE = struct.calcsize(_STRUCT_FORMAT)

_DOT_MAPPING = [
    "ZERO_TO_ONE",
    "MINUS1_TO_1_D3D",
    "MINUS1_TO_1_GL",
    "MINUS1_TO_1",
    "HILO_1",
    "HILO_HEMISPHERE_D3D",
    "HILO_HEMISPHERE_GL",
    "HILO_HEMISPHERE",
]

_TEXTURE_MODE = [
    "NONE",
    "PROJECT2D",
    "PROJECT3D",
    "CUBEMAP",
    "PASSTHRU",
    "CLIPPLANE",
    "BUMPENVMAP",
    "BUMPENVMAP_LUM",
    "BRDF",
    "DOT_ST",
    "DOT_ZW",
    "DOT_RFLCT_DIFF",
    "DOT_RFLCT_SPEC",
    "DOT_STR_3D",
    "DOT_STR_CUBE",
    "DPNDNT_AR",
    "DPNDNT_GB",
    "DOTPRODUCT",
    "DOT_RFLCT_SPEC_CONST",
]


@dataclass(frozen=True)
class PixelShaderDefinition:
    """
    Python representation of the C D3DPIXELSHADERDEF struct.
    """

    ps_alpha_inputs: tuple[int, ...]
    ps_final_combiner_inputs_abcd: int
    ps_final_combiner_inputs_efg: int
    ps_constant_0: tuple[int, ...]
    ps_constant_1: tuple[int, ...]
    ps_alpha_outputs: tuple[int, ...]
    ps_rgb_inputs: tuple[int, ...]
    ps_compare_mode: int
    ps_final_combiner_constant_0: int
    ps_final_combiner_constant_1: int
    ps_rgb_outputs: tuple[int, ...]
    # flags << 8 | combiner stage count
    ps_combiner_count: int
    ps_texture_modes: int
    ps_dot_mapping: int
    ps_input_texture: int
    # Per combiner stage c0 mapping, 4 bits each
    ps_c0_mapping: int
    # Per combiner stage c1 mapping, 4 bits each
    ps_c1_mapping: int
    # Texmode_adjust << 8 | c1_mapping << 4 | c0_mapping
    ps_final_combiner_constants: int

    def _expand_dot_mappings(self) -> list[str]:
        t1: int = self.ps_dot_mapping & 0xF
        t2: int = (self.ps_dot_mapping >> 4) & 0xF
        t3: int = (self.ps_dot_mapping >> 8) & 0xF

        return ["", _DOT_MAPPING[t1], _DOT_MAPPING[t2], _DOT_MAPPING[t3]]

    def _expand_texture_modes(self) -> list[str]:
        t0: int = self.ps_texture_modes & 0x1F
        t1: int = (self.ps_texture_modes >> 5) & 0x1F
        t2: int = (self.ps_texture_modes >> 10) & 0x1F
        t3: int = (self.ps_texture_modes >> 15) & 0x1F

        return [_TEXTURE_MODE[t0], _TEXTURE_MODE[t1], _TEXTURE_MODE[t2], _TEXTURE_MODE[t3]]

    def _expand_compare_modes(self) -> list[str]:
        t0 = self.ps_compare_mode & 0x0F
        t1 = (self.ps_compare_mode >> 4) & 0x0F
        t2 = (self.ps_compare_mode >> 8) & 0x0F
        t3 = (self.ps_compare_mode >> 12) & 0x0F

        def _expand(val: int) -> str:
            s = ">=" if val & 1 else "<"
            t = ">=" if val & 2 else "<"
            r = ">=" if val & 4 else "<"
            q = ">=" if val & 8 else "<"

            return f"S: {s} T: {t} R: {r} Q: {q}"

        return [_expand(t0), _expand(t1), _expand(t2), _expand(t3)]

    def _expand_input_textures(self) -> list[str]:
        t2 = (self.ps_input_texture >> 16) & 0x0F
        t3 = (self.ps_input_texture >> 20) & 0x0F

        return ["", "0", str(t2), str(t3)]

    def prettify(self) -> str:
        state = CombinerState()

        def update_array(base: int, values: Collection[int]):
            for index, value in enumerate(values):
                state.update(base + 4 * index, value)

        update_array(NV097_SET_COMBINER_ALPHA_ICW_0, self.ps_alpha_inputs)
        update_array(NV097_SET_COMBINER_FACTOR0_0, self.ps_constant_0)
        update_array(NV097_SET_COMBINER_FACTOR1_0, self.ps_constant_1)
        update_array(NV097_SET_COMBINER_ALPHA_OCW_0, self.ps_alpha_outputs)
        update_array(NV097_SET_COMBINER_COLOR_ICW_0, self.ps_rgb_inputs)
        update_array(NV097_SET_COMBINER_COLOR_OCW_0, self.ps_rgb_outputs)

        state.update(NV097_SET_COMBINER_SPECULAR_FOG_CW0, self.ps_final_combiner_inputs_abcd)
        state.update(NV097_SET_COMBINER_SPECULAR_FOG_CW1, self.ps_final_combiner_inputs_efg)

        state.update(NV097_SET_SPECULAR_FOG_FACTOR_0, self.ps_final_combiner_constant_0)
        state.update(NV097_SET_SPECULAR_FOG_FACTOR_1, self.ps_final_combiner_constant_1)

        state.update(NV097_SET_COMBINER_CONTROL, self.ps_combiner_count)

        def _mapping_name(val: int) -> int | None:
            if val == 0xF:
                return None
            return val

        def _expand_constant_mapping(val: int) -> list[int | None]:
            def _extract(stage: int) -> int | None:
                return _mapping_name((val >> (4 * stage)) & 0xF)

            return [_extract(stage) for stage in range(8)]

        c0_mappings = _expand_constant_mapping(self.ps_c0_mapping)
        c1_mappings = _expand_constant_mapping(self.ps_c1_mapping)
        fc_c0_mapping = _mapping_name(self.ps_final_combiner_constants & 0x0F)
        fc_c1_mapping = _mapping_name((self.ps_final_combiner_constants >> 4) & 0x0F)
        fc_texmode_adjust = (self.ps_final_combiner_constants >> 8) & 0x0F

        ret = [
            state.explain(
                c0_mappings=c0_mappings,
                c1_mappings=c1_mappings,
                final_combiner_c0_mapping=fc_c0_mapping,
                final_combiner_c1_mapping=fc_c1_mapping,
            )
        ]

        dot_mappings = self._expand_dot_mappings()
        texture_modes = self._expand_texture_modes()
        clip_compare_modes = self._expand_compare_modes()
        input_textures = self._expand_input_textures()

        for texture_stage in range(4):
            texture_mode = texture_modes[texture_stage]
            if texture_mode == "NONE":
                continue
            ret.append("")
            ret.append(f"Tex{texture_stage}")
            ret.append(f"\tMode: {texture_mode}")

            # No dot product texture modes are available to stage 0
            if texture_stage > 0:
                ret.append(f"\tDot mapping: {dot_mappings[texture_stage]}")

            if texture_mode == "CLIPPLANE":
                ret.append(f"\tClip plane compare modes: {clip_compare_modes[texture_stage]}")

            # No inputs are available to stage 0
            if texture_stage > 0:
                ret.append(f"\tInput stage: {input_textures[texture_stage]}")

        if fc_texmode_adjust:
            ret.append("D3D texture mode remapping enabled")

        return "\n".join(ret)

    @classmethod
    def from_bytes(cls, data: bytes) -> PixelShaderDefinition:
        """
        Unpacks a raw `bytes` buffer into a PixelShaderDefinition instance.
        """
        if len(data) < _STRUCT_SIZE:
            msg = f"Buffer is too small! Expected {_STRUCT_SIZE}, got {len(data)}"
            raise ValueError(msg)
        unpacked_data = struct.unpack(_STRUCT_FORMAT, data[:_STRUCT_SIZE])
        it = iter(unpacked_data)

        return cls(
            ps_alpha_inputs=tuple(next(it) for _ in range(8)),
            ps_final_combiner_inputs_abcd=next(it),
            ps_final_combiner_inputs_efg=next(it),
            ps_constant_0=tuple(next(it) for _ in range(8)),
            ps_constant_1=tuple(next(it) for _ in range(8)),
            ps_alpha_outputs=tuple(next(it) for _ in range(8)),
            ps_rgb_inputs=tuple(next(it) for _ in range(8)),
            ps_compare_mode=next(it),
            ps_final_combiner_constant_0=next(it),
            ps_final_combiner_constant_1=next(it),
            ps_rgb_outputs=tuple(next(it) for _ in range(8)),
            ps_combiner_count=next(it),
            ps_texture_modes=next(it),
            ps_dot_mapping=next(it),
            ps_input_texture=next(it),
            ps_c0_mapping=next(it),
            ps_c1_mapping=next(it),
            ps_final_combiner_constants=next(it),
        )


def _load_binary(filename: str) -> bytes:
    with open(filename, "rb") as infile:
        prefix = infile.read(2)
        if prefix in {b'b"', b"b'"}:
            try:
                rest_of_file = infile.read()
                text_content = (prefix + rest_of_file).decode("utf-8")

                data = ast.literal_eval(text_content)

                if not isinstance(data, bytes):
                    msg = f"File evaluated to a {type(data)}, not bytes."
                    raise TypeError(msg)

                return data

            except (SyntaxError, ValueError, UnicodeDecodeError) as e:
                msg = f"File '{filename}' started with '{prefix.decode()}' but failed to parse as a bytes literal"
                raise OSError(msg) from e

        rest_of_file = infile.read()
        return prefix + rest_of_file


def prettify_file(filename: str, *args, **kwargs):
    """Prettifies the given D3DPIXELSHADERDEF dump."""
    binary_data = _load_binary(filename)

    if len(binary_data) % _STRUCT_SIZE != 0:
        print(
            f"Warning: Data size ({len(binary_data)}) is not a multiple of struct size ({_STRUCT_SIZE}). Trailing bytes will be ignored."
        )

    definitions = [
        PixelShaderDefinition.from_bytes(binary_data[i * _STRUCT_SIZE : (i + 1) * _STRUCT_SIZE])
        for i in range(len(binary_data) // _STRUCT_SIZE)
    ]

    return prettify(definitions, *args, **kwargs)


def prettify(
    structs: list[PixelShaderDefinition],
    output: str | None = None,
):
    """Prettifies the given PixelShaderDefinition structs."""

    def _process():
        for index, instance in enumerate(structs):
            print(f"== Combiner {index + 1} ==========================")
            print(instance.prettify())
            print()

    if output:
        output = os.path.realpath(os.path.expanduser(output))
        with open(output, "w") as out_file, redirect_stdout(out_file):
            _process()
    else:
        _process()


def _main(args):
    filename = args.input
    filename = os.path.realpath(os.path.expanduser(filename))

    prettify_file(
        filename,
        args.output,
    )


def entrypoint():
    def _parse_args():
        parser = argparse.ArgumentParser()

        parser.add_argument("input", help="Input file.")
        parser.add_argument("output", nargs="?", help="Output file.")
        return parser.parse_args()

    sys.exit(_main(_parse_args()))


if __name__ == "__main__":
    entrypoint()
