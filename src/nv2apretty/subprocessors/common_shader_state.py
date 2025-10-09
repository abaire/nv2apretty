from __future__ import annotations

# ruff: noqa: PLR2004 Magic value used in comparison
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from nv2apretty.extracted_data import (
    NV097_DRAW_ARRAYS,
    NV097_SET_ALPHA_FUNC,
    NV097_SET_ALPHA_REF,
    NV097_SET_ALPHA_TEST_ENABLE,
    NV097_SET_ANTI_ALIASING_CONTROL,
    NV097_SET_BACK_POLYGON_MODE,
    NV097_SET_BLEND_COLOR,
    NV097_SET_BLEND_ENABLE,
    NV097_SET_BLEND_EQUATION,
    NV097_SET_BLEND_FUNC_DFACTOR,
    NV097_SET_BLEND_FUNC_SFACTOR,
    NV097_SET_CULL_FACE,
    NV097_SET_CULL_FACE_ENABLE,
    NV097_SET_DEPTH_FUNC,
    NV097_SET_DEPTH_MASK,
    NV097_SET_DEPTH_TEST_ENABLE,
    NV097_SET_EYE_VECTOR,
    NV097_SET_FRONT_POLYGON_MODE,
    NV097_SET_SHADER_OTHER_STAGE_INPUT,
    NV097_SET_SHADER_STAGE_PROGRAM,
    NV097_SET_STENCIL_FUNC_MASK,
    NV097_SET_STENCIL_FUNC_REF,
    NV097_SET_STENCIL_MASK,
    NV097_SET_STENCIL_OP_FAIL,
    NV097_SET_STENCIL_OP_ZFAIL,
    NV097_SET_STENCIL_OP_ZPASS,
    NV097_SET_STENCIL_TEST_ENABLE,
    NV097_SET_SURFACE_COLOR_OFFSET,
    NV097_SET_SURFACE_FORMAT,
    NV097_SET_SURFACE_PITCH,
    NV097_SET_SURFACE_ZETA_OFFSET,
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
    NV097_SET_VERTEX_DATA_ARRAY_FORMAT,
    NV097_SET_VERTEX_DATA_ARRAY_OFFSET,
)
from nv2apretty.subprocessors.pipeline_state import PipelineState

if TYPE_CHECKING:
    from collections.abc import Callable

_BITVECTOR_EXPANSION_RE = re.compile(r".*\{(.+)}")


@dataclass
class CommonShaderState(PipelineState):
    """Captures state that is common to both the fixed function and programmable pipelines."""

    def __post_init__(self):
        self._initialize(
            {
                NV097_DRAW_ARRAYS,
                NV097_SET_ALPHA_FUNC,
                NV097_SET_ALPHA_REF,
                NV097_SET_ALPHA_TEST_ENABLE,
                NV097_SET_ANTI_ALIASING_CONTROL,
                NV097_SET_BACK_POLYGON_MODE,
                NV097_SET_BLEND_COLOR,
                NV097_SET_BLEND_ENABLE,
                NV097_SET_BLEND_EQUATION,
                NV097_SET_BLEND_FUNC_DFACTOR,
                NV097_SET_BLEND_FUNC_SFACTOR,
                NV097_SET_CULL_FACE,
                NV097_SET_CULL_FACE_ENABLE,
                NV097_SET_DEPTH_FUNC,
                NV097_SET_DEPTH_MASK,
                NV097_SET_DEPTH_TEST_ENABLE,
                NV097_SET_EYE_VECTOR,
                NV097_SET_FRONT_POLYGON_MODE,
                NV097_SET_SHADER_OTHER_STAGE_INPUT,
                NV097_SET_SHADER_STAGE_PROGRAM,
                NV097_SET_STENCIL_FUNC_MASK,
                NV097_SET_STENCIL_FUNC_REF,
                NV097_SET_STENCIL_MASK,
                NV097_SET_STENCIL_OP_FAIL,
                NV097_SET_STENCIL_OP_ZFAIL,
                NV097_SET_STENCIL_OP_ZPASS,
                NV097_SET_STENCIL_TEST_ENABLE,
                NV097_SET_SURFACE_COLOR_OFFSET,
                NV097_SET_SURFACE_FORMAT,
                NV097_SET_SURFACE_PITCH,
                NV097_SET_SURFACE_ZETA_OFFSET,
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
                NV097_SET_VERTEX_DATA_ARRAY_FORMAT,
                NV097_SET_VERTEX_DATA_ARRAY_OFFSET,
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

    def _expand_vertex_array_info(self) -> list[str]:
        ret = ["\tVertex data array format:"]
        format_strings = self._process(NV097_SET_VERTEX_DATA_ARRAY_FORMAT, default_raw_value=0)
        offset_strings = self._process(NV097_SET_VERTEX_DATA_ARRAY_OFFSET, default_raw_value=0)
        for index, vertex_format in enumerate(format_strings):
            if not isinstance(vertex_format, str):
                msg = f"Unexpected type for NV097_SET_VERTEX_DATA_ARRAY_FORMAT data: `{vertex_format}`"
                raise TypeError(msg)
            if vertex_format.endswith("{Disabled}"):
                continue

            ret.append(f"\t\tv{index}: {vertex_format} @ {offset_strings[index]}")
        return ret

    def __str__(self):
        ret = [
            f"\tSurface format: {self._process(NV097_SET_SURFACE_FORMAT)}",
            f"\tSurface pitch: {self._process(NV097_SET_SURFACE_PITCH)}",
            f"\tSurface color offset: {self._process(NV097_SET_SURFACE_COLOR_OFFSET)}",
            f"\tSurface zeta offset: {self._process(NV097_SET_SURFACE_ZETA_OFFSET)}",
        ]

        def render_unusual_only(
            state_guard_op: int, render_func: Callable[[str, int], None], uninteresting_state: int = 0
        ):
            guard_state = self._get_raw_value(state_guard_op, -1)
            if guard_state is None:
                raise ValueError
            if guard_state == uninteresting_state:
                return

            suffix = " <ENABLE STATE UNKNOWN>" if guard_state < 0 else ""
            render_func(suffix, guard_state)

        render_unusual_only(
            NV097_SET_CULL_FACE_ENABLE,
            lambda suffix, _: ret.append(f"\tCull face: {self._process(NV097_SET_CULL_FACE)}{suffix}"),
        )

        render_unusual_only(
            NV097_SET_DEPTH_TEST_ENABLE,
            lambda suffix, _: ret.append(f"\tDepth test: {self._process(NV097_SET_DEPTH_FUNC)}{suffix}"),
        )

        render_unusual_only(
            NV097_SET_DEPTH_MASK,
            lambda _, state: ret.append(f"\tDepth write: {'<MATBE OFF>' if state < 0 else 'OFF'}"),
            uninteresting_state=1,
        )

        def render_stencil_state(suffix: str, _: int):
            ret.append(f"\tStencil testing:{suffix}")
            ret.append(f"\t\tTest mask: {self._process(NV097_SET_STENCIL_FUNC_MASK)}")
            ret.append(f"\t\tRef value: {self._process(NV097_SET_STENCIL_FUNC_REF)}")
            ret.append(f"\t\tFail op: {self._process(NV097_SET_STENCIL_OP_FAIL)}")
            ret.append(f"\t\tDepth fail op: {self._process(NV097_SET_STENCIL_OP_ZFAIL)}")
            ret.append(f"\t\tPass op: {self._process(NV097_SET_STENCIL_OP_ZPASS)}")

        render_unusual_only(NV097_SET_STENCIL_TEST_ENABLE, render_stencil_state)

        render_unusual_only(
            NV097_SET_STENCIL_MASK,
            lambda _, state: ret.append(f"\tStencil write: {'<MATBE OFF>' if state < 0 else 'OFF'}"),
            uninteresting_state=1,
        )

        def render_alpha_test_state(suffix: str, _: int):
            ret.append(f"\tAlpha testing:{suffix}")
            ret.append(f"\t\tTest func: {self._process(NV097_SET_ALPHA_FUNC)}")
            ret.append(f"\t\tRef value: {self._process(NV097_SET_ALPHA_REF)}")

        render_unusual_only(NV097_SET_ALPHA_TEST_ENABLE, render_alpha_test_state)

        def render_alpha_blend_state(suffix: str, _: int):
            ret.append(f"\tAlpha blending:{suffix}")
            ret.append(f"\t\tEquation: {self._process(NV097_SET_BLEND_EQUATION)}")
            ret.append(f"\t\tSource factor: {self._process(NV097_SET_BLEND_FUNC_SFACTOR)}")
            ret.append(f"\t\tDestination factor: {self._process(NV097_SET_BLEND_FUNC_DFACTOR)}")
            ret.append(f"\t\tColor constant: {self._process(NV097_SET_BLEND_COLOR)}")

        render_unusual_only(NV097_SET_BLEND_ENABLE, render_alpha_blend_state)

        poly_front_mode = self._process(NV097_SET_FRONT_POLYGON_MODE)
        if poly_front_mode != "V_FILL":
            ret.append(f"\tPolygon front mode: {poly_front_mode}")
        poly_back_mode = self._process(NV097_SET_BACK_POLYGON_MODE)
        if poly_back_mode != "V_FILL":
            ret.append(f"\tPolygon back mode: {poly_back_mode}")

        if self._get_count(NV097_DRAW_ARRAYS):
            ret.extend(self._expand_vertex_array_info())

        match = _BITVECTOR_EXPANSION_RE.match(self._process(NV097_SET_SHADER_STAGE_PROGRAM))
        if match:
            ret.extend(self._expand_texture_stage_states(match.group(1)))

        if self._get_raw_value(NV097_SET_ANTI_ALIASING_CONTROL) is not None:
            ret.append(f"\tAnti-aliasing control: {self._process(NV097_SET_ANTI_ALIASING_CONTROL)}")

        return "\n  ".join(ret)
