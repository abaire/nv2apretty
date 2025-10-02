from __future__ import annotations

# ruff: noqa: PLR2004 Magic value used in comparison
import re
from dataclasses import dataclass

from nv2apretty.extracted_data import (
    NV097_SET_BACK_LIGHT_AMBIENT_COLOR,
    NV097_SET_BACK_LIGHT_DIFFUSE_COLOR,
    NV097_SET_BACK_LIGHT_SPECULAR_COLOR,
    NV097_SET_BACK_MATERIAL_ALPHA,
    NV097_SET_BACK_MATERIAL_EMISSION,
    NV097_SET_BACK_SCENE_AMBIENT_COLOR,
    NV097_SET_BACK_SPECULAR_PARAMS,
    NV097_SET_COLOR_MATERIAL,
    NV097_SET_FOG_ENABLE,
    NV097_SET_FOG_GEN_MODE,
    NV097_SET_LIGHT_AMBIENT_COLOR,
    NV097_SET_LIGHT_CONTROL,
    NV097_SET_LIGHT_DIFFUSE_COLOR,
    NV097_SET_LIGHT_ENABLE_MASK,
    NV097_SET_LIGHT_INFINITE_DIRECTION,
    NV097_SET_LIGHT_INFINITE_HALF_VECTOR,
    NV097_SET_LIGHT_LOCAL_ATTENUATION,
    NV097_SET_LIGHT_LOCAL_POSITION,
    NV097_SET_LIGHT_LOCAL_RANGE,
    NV097_SET_LIGHT_SPECULAR_COLOR,
    NV097_SET_LIGHT_SPOT_DIRECTION,
    NV097_SET_LIGHT_SPOT_FALLOFF,
    NV097_SET_LIGHTING_ENABLE,
    NV097_SET_MATERIAL_ALPHA,
    NV097_SET_MATERIAL_EMISSION,
    NV097_SET_POINT_PARAMS,
    NV097_SET_POINT_PARAMS_ENABLE,
    NV097_SET_POINT_SIZE,
    NV097_SET_POINT_SMOOTH_ENABLE,
    NV097_SET_SCENE_AMBIENT_COLOR,
    NV097_SET_SHADER_OTHER_STAGE_INPUT,
    NV097_SET_SHADER_STAGE_PROGRAM,
    NV097_SET_SKIN_MODE,
    NV097_SET_SPECULAR_ENABLE,
    NV097_SET_SPECULAR_PARAMS,
    NV097_SET_TEXGEN_Q,
    NV097_SET_TEXGEN_R,
    NV097_SET_TEXGEN_S,
    NV097_SET_TEXGEN_T,
    NV097_SET_TEXTURE_ADDRESS,
    NV097_SET_TEXTURE_MATRIX_ENABLE,
    NV097_SET_TWO_SIDE_LIGHT_EN,
)
from nv2apretty.subprocessors.pipeline_state import PipelineState, as_float

_LIGHT_STATUS_RE = re.compile(r".*\{(.+)}")


@dataclass
class FixedFunctionPipelineState(PipelineState):
    """Represents the fixed function pipeline state of a single frame."""

    def __post_init__(self):
        self._initialize(
            {
                NV097_SET_BACK_LIGHT_AMBIENT_COLOR,
                NV097_SET_BACK_LIGHT_DIFFUSE_COLOR,
                NV097_SET_BACK_LIGHT_SPECULAR_COLOR,
                NV097_SET_BACK_MATERIAL_ALPHA,
                NV097_SET_BACK_MATERIAL_EMISSION,
                NV097_SET_BACK_SCENE_AMBIENT_COLOR,
                NV097_SET_BACK_SPECULAR_PARAMS,
                NV097_SET_COLOR_MATERIAL,
                NV097_SET_FOG_ENABLE,
                NV097_SET_FOG_GEN_MODE,
                NV097_SET_LIGHTING_ENABLE,
                NV097_SET_LIGHT_AMBIENT_COLOR,
                NV097_SET_LIGHT_CONTROL,
                NV097_SET_LIGHT_DIFFUSE_COLOR,
                NV097_SET_LIGHT_ENABLE_MASK,
                NV097_SET_LIGHT_INFINITE_DIRECTION,
                NV097_SET_LIGHT_INFINITE_HALF_VECTOR,
                NV097_SET_LIGHT_LOCAL_ATTENUATION,
                NV097_SET_LIGHT_LOCAL_POSITION,
                NV097_SET_LIGHT_LOCAL_RANGE,
                NV097_SET_LIGHT_SPECULAR_COLOR,
                NV097_SET_LIGHT_SPOT_DIRECTION,
                NV097_SET_LIGHT_SPOT_FALLOFF,
                NV097_SET_MATERIAL_ALPHA,
                NV097_SET_MATERIAL_EMISSION,
                NV097_SET_POINT_PARAMS,
                NV097_SET_POINT_PARAMS_ENABLE,
                NV097_SET_POINT_SIZE,
                NV097_SET_POINT_SMOOTH_ENABLE,
                NV097_SET_SCENE_AMBIENT_COLOR,
                NV097_SET_SHADER_OTHER_STAGE_INPUT,
                NV097_SET_SHADER_STAGE_PROGRAM,
                NV097_SET_SKIN_MODE,
                NV097_SET_SPECULAR_ENABLE,
                NV097_SET_SPECULAR_PARAMS,
                NV097_SET_TEXGEN_Q,
                NV097_SET_TEXGEN_R,
                NV097_SET_TEXGEN_S,
                NV097_SET_TEXGEN_T,
                NV097_SET_TEXTURE_ADDRESS,
                NV097_SET_TEXTURE_MATRIX_ENABLE,
                NV097_SET_TWO_SIDE_LIGHT_EN,
            }
        )

    def _expand_light_states(self, light_status_string: str, *, two_sided_lighting: bool = False) -> list[str]:
        light_enabled_state_pairs = light_status_string.split(", ")

        ret: list[str] = []
        for index, status_string in enumerate(light_enabled_state_pairs):
            elements = status_string.split(":")
            if len(elements) != 2 or elements[1] == "OFF":
                continue

            light_name, light_type = elements
            ret.append(f"\t{light_name}: {light_type}")

            ret.append(f"\t\tAmbient: {self._process(NV097_SET_LIGHT_AMBIENT_COLOR)[index]}")
            ret.append(f"\t\tDiffuse: {self._process(NV097_SET_LIGHT_DIFFUSE_COLOR)[index]}")
            ret.append(f"\t\tSpecular: {self._process(NV097_SET_LIGHT_SPECULAR_COLOR)[index]}")

            if two_sided_lighting:
                ret.append(f"\t\tBack ambient: {self._process(NV097_SET_BACK_LIGHT_AMBIENT_COLOR)[index]}")
                ret.append(f"\t\tBack diffuse: {self._process(NV097_SET_BACK_LIGHT_DIFFUSE_COLOR)[index]}")
                ret.append(f"\t\tBack specular: {self._process(NV097_SET_BACK_LIGHT_SPECULAR_COLOR)[index]}")

            if light_type == "INFINITE":
                ret.append(f"\t\tDirection: {self._process(NV097_SET_LIGHT_INFINITE_DIRECTION)[index]}")
                ret.append(f"\t\tHalf-vector: {self._process(NV097_SET_LIGHT_INFINITE_HALF_VECTOR)[index]}")
            else:
                ret.append(f"\t\tPosition: {self._process(NV097_SET_LIGHT_LOCAL_POSITION)[index]}")
                ret.append(f"\t\tRange: {self._process(NV097_SET_LIGHT_LOCAL_RANGE)[index]}")
                ret.append(f"\t\tAttenuation: {self._process(NV097_SET_LIGHT_LOCAL_ATTENUATION)[index]}")

                if light_type == "SPOT":
                    ret.append(f"\t\tSpot direction: {self._process(NV097_SET_LIGHT_SPOT_DIRECTION)[index]}")
                    ret.append(f"\t\tSpot falloff: {self._process(NV097_SET_LIGHT_SPOT_FALLOFF)[index]}")

        return ret

    def __str__(self):
        ret = []

        lighting_enabled = self._get_raw_value(NV097_SET_LIGHTING_ENABLE, 0) != 0
        two_sided_lighting = self._get_raw_value(NV097_SET_TWO_SIDE_LIGHT_EN, 0)
        ret.append(f"Lighting: {lighting_enabled}")
        if lighting_enabled:
            ret.append(f"\tColor material: {self._process(NV097_SET_COLOR_MATERIAL)}")
            ret.append(f"\tLight control: {self._process(NV097_SET_LIGHT_CONTROL)}")
            ret.append(f"\tScene ambient: {self._process(NV097_SET_SCENE_AMBIENT_COLOR)}")
            ret.append(f"\tMaterial emission: {self._process(NV097_SET_MATERIAL_EMISSION)}")
            ret.append(f"\tMaterial alpha: {self._process(NV097_SET_MATERIAL_ALPHA)}")
            ret.append(f"\tSpecular params: {self._process(NV097_SET_SPECULAR_PARAMS)}")

            ret.append(f"\tTwo sided: {bool(two_sided_lighting)}")
            if two_sided_lighting:
                ret.append(f"\t\tBack scene ambient: {self._process(NV097_SET_BACK_SCENE_AMBIENT_COLOR)}")
                ret.append(f"\t\tBack material emission: {self._process(NV097_SET_BACK_MATERIAL_EMISSION)}")
                ret.append(f"\t\tBack material alpha: {self._process(NV097_SET_BACK_MATERIAL_ALPHA)}")

            match = _LIGHT_STATUS_RE.match(self._process(NV097_SET_LIGHT_ENABLE_MASK))
            if match:
                ret.extend(self._expand_light_states(match.group(1), two_sided_lighting=two_sided_lighting))

        specular_enable = self._get_raw_value(NV097_SET_SPECULAR_ENABLE, 0)
        ret.append(f"Specular enable: {bool(specular_enable)}")
        if specular_enable:
            ret.append(f"\tSpecular params: {self._process(NV097_SET_SPECULAR_PARAMS)}")
            if two_sided_lighting:
                ret.append(f"\tBack specular params: {self._process(NV097_SET_BACK_SPECULAR_PARAMS)}")

        fog_enabled = self._get_raw_value(NV097_SET_FOG_ENABLE, 0) != 0
        ret.append(f"Fog enable: {fog_enabled}")
        if fog_enabled:
            ret.append(f"\tFog gen mode: {self._process(NV097_SET_FOG_GEN_MODE)}")

        ret.append(f"Skinning mode: {self._process(NV097_SET_SKIN_MODE)}")

        point_params_enabled = self._get_raw_value(NV097_SET_POINT_PARAMS_ENABLE, 0) != 0
        ret.append(f"Point params enable: {point_params_enabled}")
        if point_params_enabled:
            ret.append(f"\tPoint size: {self._process(NV097_SET_POINT_SIZE)}")

            params = self._get_raw_value(NV097_SET_POINT_PARAMS)
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

        if bool(self._get_raw_value(NV097_SET_POINT_SMOOTH_ENABLE, 0)):
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

        tex_matrix_en = self._get_raw_value(NV097_SET_TEXTURE_MATRIX_ENABLE)
        if tex_matrix_en:
            texture_matrix_data = [f"[{index}: {bool(item)}]" for index, item in enumerate(tex_matrix_en)]
            ret.append(f"TextureMatrix: {', '.join(texture_matrix_data)}")

        return "\t" + "\n\t".join(ret)
