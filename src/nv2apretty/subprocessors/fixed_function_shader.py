from __future__ import annotations

from dataclasses import dataclass, field

NV097_SET_TEXTURE_MATRIX_ENABLE_0 = 0x420
NV097_SET_TEXTURE_MATRIX_ENABLE_1 = 0x424
NV097_SET_TEXTURE_MATRIX_ENABLE_2 = 0x428
NV097_SET_TEXTURE_MATRIX_ENABLE_3 = 0x42C

NV097_SET_LIGHTING_ENABLE = 0x314
NV097_SET_SKIN_MODE = 0x328
NV097_SET_TWO_SIDE_LIGHT_EN = 0x17C4


@dataclass
class TextureMatrixEnableState:
    ENABLE_STATE: list[bool] = field(default_factory=lambda: [False] * 4)

    def update(self, nv_op: int, nv_param: int) -> bool:
        if nv_op < NV097_SET_TEXTURE_MATRIX_ENABLE_0 or nv_op > NV097_SET_TEXTURE_MATRIX_ENABLE_3:
            return False
        index = (nv_op - NV097_SET_TEXTURE_MATRIX_ENABLE_0) // 4
        self.ENABLE_STATE[index] = nv_param != 0
        return True


NV097_SET_TEXGEN_S_0 = 0x3C0
NV097_SET_TEXGEN_T_0 = 0x3C4
NV097_SET_TEXGEN_R_0 = 0x3C8
NV097_SET_TEXGEN_Q_0 = 0x3CC

NV097_SET_TEXGEN_S_1 = 0x3D0
NV097_SET_TEXGEN_T_1 = 0x3D4
NV097_SET_TEXGEN_R_1 = 0x3D8
NV097_SET_TEXGEN_Q_1 = 0x3DC

NV097_SET_TEXGEN_S_2 = 0x3E0
NV097_SET_TEXGEN_T_2 = 0x3E4
NV097_SET_TEXGEN_R_2 = 0x3E8
NV097_SET_TEXGEN_Q_2 = 0x3EC

NV097_SET_TEXGEN_S_3 = 0x3F0
NV097_SET_TEXGEN_T_3 = 0x3F4
NV097_SET_TEXGEN_R_3 = 0x3F8
NV097_SET_TEXGEN_Q_3 = 0x3FC


@dataclass
class TexGenState:
    S_0: int = 0
    T_0: int = 0
    R_0: int = 0
    Q_0: int = 0
    S_1: int = 0
    T_1: int = 0
    R_1: int = 0
    Q_1: int = 0
    S_2: int = 0
    T_2: int = 0
    R_2: int = 0
    Q_2: int = 0
    S_3: int = 0
    T_3: int = 0
    R_3: int = 0
    Q_3: int = 0

    def update(self, nv_op: int, nv_param: int) -> bool:
        if nv_op < NV097_SET_TEXGEN_S_0 or nv_op > NV097_SET_TEXGEN_Q_3:
            return False

        if nv_op == NV097_SET_TEXGEN_S_0:
            self.S_0 = nv_param
        elif nv_op == NV097_SET_TEXGEN_T_0:
            self.T_0 = nv_param
        elif nv_op == NV097_SET_TEXGEN_R_0:
            self.R_0 = nv_param
        elif nv_op == NV097_SET_TEXGEN_Q_0:
            self.Q_0 = nv_param
        elif nv_op == NV097_SET_TEXGEN_S_1:
            self.S_1 = nv_param
        elif nv_op == NV097_SET_TEXGEN_T_1:
            self.T_1 = nv_param
        elif nv_op == NV097_SET_TEXGEN_R_1:
            self.R_1 = nv_param
        elif nv_op == NV097_SET_TEXGEN_Q_1:
            self.Q_1 = nv_param
        elif nv_op == NV097_SET_TEXGEN_S_2:
            self.S_2 = nv_param
        elif nv_op == NV097_SET_TEXGEN_T_2:
            self.T_2 = nv_param
        elif nv_op == NV097_SET_TEXGEN_R_2:
            self.R_2 = nv_param
        elif nv_op == NV097_SET_TEXGEN_Q_2:
            self.Q_2 = nv_param
        elif nv_op == NV097_SET_TEXGEN_S_3:
            self.S_3 = nv_param
        elif nv_op == NV097_SET_TEXGEN_T_3:
            self.T_3 = nv_param
        elif nv_op == NV097_SET_TEXGEN_R_3:
            self.R_3 = nv_param
        elif nv_op == NV097_SET_TEXGEN_Q_3:
            self.Q_3 = nv_param

        return True

    def data(self) -> list[str]:
        return [
            f"S[0] 0x{self.S_0:04X}, T[0] 0x{self.T_0:04X} R[0]: 0x{self.R_0:04X} Q[0]: 0x{self.Q_0:04X}",
            f"S[1] 0x{self.S_1:04X}, T[1] 0x{self.T_1:04X} R[1]: 0x{self.R_1:04X} Q[1]: 0x{self.Q_1:04X}",
            f"S[2] 0x{self.S_2:04X}, T[2] 0x{self.T_2:04X} R[2]: 0x{self.R_2:04X} Q[2]: 0x{self.Q_2:04X}",
            f"S[3] 0x{self.S_3:04X}, T[3] 0x{self.T_3:04X} R[3]: 0x{self.R_3:04X} Q[3]: 0x{self.Q_3:04X}",
        ]


NV097_SET_COLOR_MATERIAL = 0x298
NV097_SET_LIGHT_CONTROL = 0x294
NV097_SET_LIGHT_ENABLE_MASK = 0x3BC
NV097_SET_SPECULAR_ENABLE = 0x3B8
NV097_SET_FOG_ENABLE = 0x2A4
NV097_SET_FOG_GEN_MODE = 0x2A0
NV097_SET_POINT_PARAMS_ENABLE = 0x318
NV097_SET_POINT_SIZE = 0x198C


@dataclass
class FixedFunctionPipelineState:
    texgen_state: TexGenState = field(default_factory=lambda: TexGenState())
    texture_matrix_state: TextureMatrixEnableState = field(default_factory=lambda: TextureMatrixEnableState())

    lighting: bool = False
    two_sided_lighting: bool = False
    skin_mode: int = 0
    color_material: int = 0
    light_control: int = 0
    light_enable_mask: int = 0
    specular_enable: bool = False
    fog_enable: bool = False
    fog_gen_mode: int = 0
    point_params_enable: bool = False
    point_size: int = -1

    def update(self, nv_op: int, nv_param: int):
        if self.texgen_state.update(nv_op, nv_param):
            return
        if self.texture_matrix_state.update(nv_op, nv_param):
            return

        if nv_op == NV097_SET_POINT_SIZE:
            self.point_size = nv_param
            return

        if nv_op == NV097_SET_POINT_PARAMS_ENABLE:
            self.point_params_enable = bool(nv_param)
            return

        if nv_op == NV097_SET_FOG_GEN_MODE:
            self.fog_gen_mode = nv_param
            return

        if nv_op == NV097_SET_FOG_ENABLE:
            self.fog_enable = bool(nv_param)
            return

        if nv_op == NV097_SET_SPECULAR_ENABLE:
            self.specular_enable = bool(nv_param)
            return

        if nv_op == NV097_SET_TWO_SIDE_LIGHT_EN and nv_param:
            self.two_sided_lighting = bool(nv_param)
            return

        if nv_op == NV097_SET_LIGHTING_ENABLE:
            self.lighting = bool(nv_param)
            return

        if nv_op == NV097_SET_SKIN_MODE:
            self.skin_mode = nv_param
            return

        if nv_op == NV097_SET_COLOR_MATERIAL:
            self.color_material = nv_param
            return

        if nv_op == NV097_SET_LIGHT_CONTROL:
            self.light_control = nv_param
            return

        if nv_op == NV097_SET_LIGHT_ENABLE_MASK:
            self.light_enable_mask = nv_param
            return

    def __str__(self):
        ret = [
            f"  Lighting: {self.lighting}",
        ]
        if self.lighting:
            ret.append(f"\tTwo sided: {bool(self.two_sided_lighting)}")
            ret.append(f"\tColor material: 0x{self.color_material:X}")
            ret.append(f"\tLight control: 0x{self.light_control:X}")
            ret.append(f"\tLight enable: 0x{self.light_enable_mask:X}")

        ret.append(f"Specular enable: {self.specular_enable}")

        ret.append(f"Fog enable: {self.fog_enable}")
        if self.fog_enable:
            ret.append(f"\tFog gen mode: 0x{self.fog_gen_mode:X}")

        ret.append(f"Skinning mode: {self.skin_mode}")

        ret.append(f"Point params enable: {self.point_params_enable}")
        if self.point_params_enable:
            ret.append(f"\tPoint size: 0x{self.point_size:X}")

        ret.append("TexGen: ")
        ret.extend([f"\t{item}" for item in self.texgen_state.data()])

        texture_matrix_data = [f"[{index}: {item}" for item, index in enumerate(self.texture_matrix_state.ENABLE_STATE)]
        ret.append(f"TextureMatrix: {texture_matrix_data}")

        return "\n  ".join(ret)
