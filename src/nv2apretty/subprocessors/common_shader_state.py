from __future__ import annotations

# ruff: noqa: PLR2004 Magic value used in comparison
import re
from dataclasses import dataclass

from nv2apretty.extracted_data import (
    NV097_SET_ANTI_ALIASING_CONTROL,
    NV097_SET_EYE_VECTOR,
    NV097_SET_SHADER_OTHER_STAGE_INPUT,
    NV097_SET_SHADER_STAGE_PROGRAM,
    NV097_SET_TEXTURE_ADDRESS,
    NV097_SET_TEXTURE_BORDER_COLOR,
    NV097_SET_TEXTURE_CONTROL0,
    NV097_SET_TEXTURE_CONTROL1,
    NV097_SET_TEXTURE_FILTER,
    NV097_SET_TEXTURE_FORMAT,
    NV097_SET_TEXTURE_IMAGE_RECT,
    NV097_SET_TEXTURE_OFFSET,
    NV097_SET_TEXTURE_PALETTE,
    NV097_SET_TEXTURE_SET_BUMP_ENV_MAT,
    NV097_SET_TEXTURE_SET_BUMP_ENV_OFFSET,
    NV097_SET_TEXTURE_SET_BUMP_ENV_SCALE,
)
from nv2apretty.subprocessors.pipeline_state import PipelineState

_BITVECTOR_EXPANSION_RE = re.compile(r".*\{(.+)}")


@dataclass
class CommonShaderState(PipelineState):
    """Captures state that is common to both the fixed function and programmable pipelines."""

    def __post_init__(self):
        self._initialize(
            {
                NV097_SET_ANTI_ALIASING_CONTROL,
                NV097_SET_EYE_VECTOR,
                NV097_SET_SHADER_OTHER_STAGE_INPUT,
                NV097_SET_SHADER_STAGE_PROGRAM,
                NV097_SET_TEXTURE_ADDRESS,
                NV097_SET_TEXTURE_BORDER_COLOR,
                NV097_SET_TEXTURE_CONTROL0,
                NV097_SET_TEXTURE_CONTROL1,
                NV097_SET_TEXTURE_FILTER,
                NV097_SET_TEXTURE_FORMAT,
                NV097_SET_TEXTURE_IMAGE_RECT,
                NV097_SET_TEXTURE_OFFSET,
                NV097_SET_TEXTURE_PALETTE,
                NV097_SET_TEXTURE_SET_BUMP_ENV_MAT,
                NV097_SET_TEXTURE_SET_BUMP_ENV_OFFSET,
                NV097_SET_TEXTURE_SET_BUMP_ENV_SCALE,
            }
        )

    def _expand_texture_stage_states(self, texture_stage_program_string: str) -> list[str]:
        light_enabled_state_pairs = texture_stage_program_string.split(", ")

        ret: list[str] = []
        for index, status_string in enumerate(light_enabled_state_pairs):
            elements = status_string.split(":")
            if len(elements) != 2 or elements[1] == "NONE":
                continue

            if not ret:
                ret.append("\tShader stages:")

            pixel_shader_mode = elements[1]
            ret.append(f"\t\tStage {index}: {pixel_shader_mode}")

            def explain(label: str, value: str | list[str] | list[list[str]]):
                ret.append(f"\t\t\t{label}: {value}")

            explain("Offset", self._process(NV097_SET_TEXTURE_OFFSET, default_raw_value=-1)[index])

            format_str = self._process(NV097_SET_TEXTURE_FORMAT, default_raw_value=0)[index]
            explain("Format", format_str)

            address_str = self._process(NV097_SET_TEXTURE_ADDRESS, default_raw_value=0)[index]
            explain("Address", address_str)
            explain("Filter", self._process(NV097_SET_TEXTURE_FILTER, default_raw_value=0)[index])

            explain("Control0", self._process(NV097_SET_TEXTURE_CONTROL0, default_raw_value=0)[index])
            # Linear texture modes all contain the word "_IMAGE" and are prefixed by LU or LC
            if "_IMAGE_" in format_str:
                explain("Control1", self._process(NV097_SET_TEXTURE_CONTROL1, default_raw_value=0)[index])
                explain("Image rect", self._process(NV097_SET_TEXTURE_IMAGE_RECT, default_raw_value=0)[index])

            # Palette is only interesting if the mode is indexed color
            if "SZ_I8_A8R8G8B8" in format_str:
                explain("Palette", self._process(NV097_SET_TEXTURE_PALETTE, default_raw_value=0)[index])

            # Border color is only interesting if it is potentially used
            if "Border" in address_str:
                explain("Border color", self._process(NV097_SET_TEXTURE_BORDER_COLOR, default_raw_value=0)[index])

            if pixel_shader_mode in {"BUMPENVMAP", "BUMPENVMAP_LUMINANCE"}:
                explain(
                    "Bump env matrix", self._process(NV097_SET_TEXTURE_SET_BUMP_ENV_MAT, default_raw_value=0)[index]
                )
                if pixel_shader_mode == "BUMPENVMAP_LUMINANCE":
                    explain(
                        "Bump env luminance scale",
                        self._process(NV097_SET_TEXTURE_SET_BUMP_ENV_SCALE, default_raw_value=0)[index],
                    )
                    explain(
                        "Bump env luminance offset",
                        self._process(NV097_SET_TEXTURE_SET_BUMP_ENV_OFFSET, default_raw_value=0)[index],
                    )
            elif pixel_shader_mode in {
                "DOT_REFLECT_DIFFUSE",
                "DOT_REFLECT_SPECULAR",
                "?0x11" "DOT_REFLECT_SPECULAR_CONST",
            }:
                explain("Eye vector", self._process(NV097_SET_EYE_VECTOR))

        return ret

    def __str__(self):
        ret = []

        match = _BITVECTOR_EXPANSION_RE.match(self._process(NV097_SET_SHADER_STAGE_PROGRAM))
        if match:
            ret.extend(self._expand_texture_stage_states(match.group(1)))

        if self._get_raw_value(NV097_SET_ANTI_ALIASING_CONTROL) is not None:
            ret.append(f"\tAnti-aliasing control: {self._process(NV097_SET_ANTI_ALIASING_CONTROL)}")

        return "\n  ".join(ret)
