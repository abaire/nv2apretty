# ruff: noqa: RUF012 Mutable class attributes should be annotated with `typing.ClassVar`
# ruff: noqa: UP031 Use format specifiers instead of percent format
# ruff: noqa: FBT001 Boolean-typed positional argument in function definition
# ruff: noqa: FBT002 Boolean default positional argument in function definition
# ruff: noqa: PLR2004 Magic value used in comparison

from __future__ import annotations

import ctypes
import sys
from dataclasses import dataclass, field

# Sets the final combiner stage
NV097_SET_COMBINER_SPECULAR_FOG_CW0 = 0x288
NV097_SET_COMBINER_SPECULAR_FOG_CW1 = 0x28C

# Sets final combiner C0 constant
NV097_SET_SPECULAR_FOG_FACTOR_0 = 0x1E20
# Sets the C1 constant
NV097_SET_SPECULAR_FOG_FACTOR_1 = 0x1E24

NV097_SET_COMBINER_ALPHA_ICW_0 = 0x260
NV097_SET_COMBINER_ALPHA_ICW_1 = 0x264
NV097_SET_COMBINER_ALPHA_ICW_2 = 0x268
NV097_SET_COMBINER_ALPHA_ICW_3 = 0x26C
NV097_SET_COMBINER_ALPHA_ICW_4 = 0x270
NV097_SET_COMBINER_ALPHA_ICW_5 = 0x274
NV097_SET_COMBINER_ALPHA_ICW_6 = 0x278
NV097_SET_COMBINER_ALPHA_ICW_7 = 0x27C
NV097_SET_COMBINER_FACTOR0_0 = 0xA60
NV097_SET_COMBINER_FACTOR0_1 = 0xA64
NV097_SET_COMBINER_FACTOR0_2 = 0xA68
NV097_SET_COMBINER_FACTOR0_3 = 0xA6C
NV097_SET_COMBINER_FACTOR0_4 = 0xA70
NV097_SET_COMBINER_FACTOR0_5 = 0xA74
NV097_SET_COMBINER_FACTOR0_6 = 0xA78
NV097_SET_COMBINER_FACTOR0_7 = 0xA7C
NV097_SET_COMBINER_FACTOR1_0 = 0xA80
NV097_SET_COMBINER_FACTOR1_1 = 0xA84
NV097_SET_COMBINER_FACTOR1_2 = 0xA88
NV097_SET_COMBINER_FACTOR1_3 = 0xA8C
NV097_SET_COMBINER_FACTOR1_4 = 0xA90
NV097_SET_COMBINER_FACTOR1_5 = 0xA94
NV097_SET_COMBINER_FACTOR1_6 = 0xA98
NV097_SET_COMBINER_FACTOR1_7 = 0xA9C
NV097_SET_COMBINER_ALPHA_OCW_0 = 0xAA0
NV097_SET_COMBINER_ALPHA_OCW_1 = 0xAA4
NV097_SET_COMBINER_ALPHA_OCW_2 = 0xAA8
NV097_SET_COMBINER_ALPHA_OCW_3 = 0xAAC
NV097_SET_COMBINER_ALPHA_OCW_4 = 0xAB0
NV097_SET_COMBINER_ALPHA_OCW_5 = 0xAB4
NV097_SET_COMBINER_ALPHA_OCW_6 = 0xAB8
NV097_SET_COMBINER_ALPHA_OCW_7 = 0xABC
NV097_SET_COMBINER_COLOR_ICW_0 = 0xAC0
NV097_SET_COMBINER_COLOR_ICW_1 = 0xAC4
NV097_SET_COMBINER_COLOR_ICW_2 = 0xAC8
NV097_SET_COMBINER_COLOR_ICW_3 = 0xACC
NV097_SET_COMBINER_COLOR_ICW_4 = 0xAD0
NV097_SET_COMBINER_COLOR_ICW_5 = 0xAD4
NV097_SET_COMBINER_COLOR_ICW_6 = 0xAD8
NV097_SET_COMBINER_COLOR_ICW_7 = 0xADC
NV097_SET_COMBINER_COLOR_OCW_0 = 0x1E40
NV097_SET_COMBINER_COLOR_OCW_1 = 0x1E44
NV097_SET_COMBINER_COLOR_OCW_2 = 0x1E48
NV097_SET_COMBINER_COLOR_OCW_3 = 0x1E4C
NV097_SET_COMBINER_COLOR_OCW_4 = 0x1E50
NV097_SET_COMBINER_COLOR_OCW_5 = 0x1E54
NV097_SET_COMBINER_COLOR_OCW_6 = 0x1E58
NV097_SET_COMBINER_COLOR_OCW_7 = 0x1E5C

NV097_SET_COMBINER_CONTROL = 0x1E60

_ICW_SRC_VALUES = [
    "Zero",  # 0
    "C0",  # 1
    "C1",  # 2
    "Fog",  # 3
    "V0_Diffuse",  # 4
    "V1_Specular",  # 5
    "?6",
    "?7",
    "Tex0",  # 8
    "Tex1",  # 9
    "Tex2",  # 10
    "Tex3",  # 11
    "R0Temp",  # 12
    "R1Temp",  # 13
    "Specular_R0_Sum",  # 14
    "EF_Prod",  # 15
]

_ICW_MAP_VALUES = [
    "UNSIGNED_IDENTITY",
    "UNSIGNED_INVERT",
    "EXPAND_NORMAL",
    "EXPAND_NEGATE",
    "HALFBIAS_NORMAL",
    "HALFBIAS_NEGATE",
    "SIGNED_IDENTITY",
    "SIGNED_NEGATE",
]

_OCW_DST_VALUES = list(_ICW_SRC_VALUES)
_OCW_DST_VALUES[0] = "Discard"


class PGRAPHBitField(ctypes.LittleEndianStructure):
    def __new__(cls, *args):
        if args:
            return cls.from_buffer_copy(args[0].to_bytes(4, byteorder=sys.byteorder))
        return super().__new__()


class CombinerControlBitField(PGRAPHBitField):
    _fields_ = [
        ("COUNT", ctypes.c_uint32, 8),
        ("MUX_SELECT", ctypes.c_uint32, 4),
        ("FACTOR_0", ctypes.c_uint32, 4),
        ("FACTOR_1", ctypes.c_uint32, 16),
    ]


class FinalCombiner0BitField(PGRAPHBitField):
    _fields_ = [
        ("D_SOURCE", ctypes.c_uint32, 4),
        ("D_ALPHA", ctypes.c_uint32, 1),
        ("D_INVERSE", ctypes.c_uint32, 3),
        ("C_SOURCE", ctypes.c_uint32, 4),
        ("C_ALPHA", ctypes.c_uint32, 1),
        ("C_INVERSE", ctypes.c_uint32, 3),
        ("B_SOURCE", ctypes.c_uint32, 4),
        ("B_ALPHA", ctypes.c_uint32, 1),
        ("B_INVERSE", ctypes.c_uint32, 3),
        ("A_SOURCE", ctypes.c_uint32, 4),
        ("A_ALPHA", ctypes.c_uint32, 1),
        ("A_INVERSE", ctypes.c_uint32, 3),
    ]


class FinalCombiner1BitField(PGRAPHBitField):
    _fields_ = [
        ("SPECULAR_ADD_INVERT_R12", ctypes.c_uint32, 6),
        ("SPECULAR_ADD_INVERT_R5", ctypes.c_uint32, 1),
        ("SPECULAR_CLAMP", ctypes.c_uint32, 1),
        ("G_SOURCE", ctypes.c_uint32, 4),
        ("G_ALPHA", ctypes.c_uint32, 1),
        ("G_INVERSE", ctypes.c_uint32, 3),
        ("F_SOURCE", ctypes.c_uint32, 4),
        ("F_ALPHA", ctypes.c_uint32, 1),
        ("F_INVERSE", ctypes.c_uint32, 3),
        ("E_SOURCE", ctypes.c_uint32, 4),
        ("E_ALPHA", ctypes.c_uint32, 1),
        ("E_INVERSE", ctypes.c_uint32, 3),
    ]


class ICWBitField(PGRAPHBitField):
    _fields_ = [
        ("D_SOURCE", ctypes.c_uint32, 4),
        ("D_ALPHA", ctypes.c_uint32, 1),
        ("D_MAP", ctypes.c_uint32, 3),
        ("C_SOURCE", ctypes.c_uint32, 4),
        ("C_ALPHA", ctypes.c_uint32, 1),
        ("C_MAP", ctypes.c_uint32, 3),
        ("B_SOURCE", ctypes.c_uint32, 4),
        ("B_ALPHA", ctypes.c_uint32, 1),
        ("B_MAP", ctypes.c_uint32, 3),
        ("A_SOURCE", ctypes.c_uint32, 4),
        ("A_ALPHA", ctypes.c_uint32, 1),
        ("A_MAP", ctypes.c_uint32, 3),
    ]


class AlphaOCWBitField(PGRAPHBitField):
    _fields_ = [
        ("CD_DST_REG", ctypes.c_uint32, 4),
        ("AB_DST_REG", ctypes.c_uint32, 4),
        ("SUM_DST_REG", ctypes.c_uint32, 4),
        ("CD_DOT", ctypes.c_uint32, 1),
        ("AB_DOT", ctypes.c_uint32, 1),
        ("MUX", ctypes.c_uint32, 1),
        ("OP", ctypes.c_uint32, 3),
    ]


class ColorOCWBitField(PGRAPHBitField):
    _fields_ = [
        ("CD_DST_REG", ctypes.c_uint32, 4),
        ("AB_DST_REG", ctypes.c_uint32, 4),
        ("SUM_DST_REG", ctypes.c_uint32, 4),
        ("CD_DOT", ctypes.c_uint32, 1),
        ("AB_DOT", ctypes.c_uint32, 1),
        ("MUX", ctypes.c_uint32, 1),
        ("OP", ctypes.c_uint32, 3),
        ("CD_BLUE_TO_ALPHA", ctypes.c_uint32, 1),
        ("AB_BLUE_TO_ALPHA", ctypes.c_uint32, 13),
    ]


class ColorFactorBitField(PGRAPHBitField):
    _fields_ = [
        ("BLUE", ctypes.c_uint32, 8),
        ("GREEN", ctypes.c_uint32, 8),
        ("RED", ctypes.c_uint32, 8),
        ("ALPHA", ctypes.c_uint32, 8),
    ]

    def __str__(self):
        elements = []

        elements.append("BLUE:%02X %f" % (self.BLUE, self.BLUE / 255.0))
        elements.append("GREEN:%02X %f" % (self.GREEN, self.GREEN / 255.0))
        elements.append("RED:%02X %f" % (self.RED, self.RED / 255.0))
        elements.append("ALPHA:%02X %f" % (self.ALPHA, self.ALPHA / 255.0))

        flat = ", ".join(elements)
        return f"({flat})"


@dataclass
class CombinerState:
    """Tracks state of the nv2a color combiner (pixel shader)."""

    control: int = 0

    final_combiner_0: int = 0
    final_combiner_1: int = 0
    final_combiner_constant0: int = 0
    final_combiner_constant1: int = 0

    color_inputs: list[int] = field(default_factory=lambda: [0] * 8)
    color_outputs: list[int] = field(default_factory=lambda: [0] * 8)
    alpha_inputs: list[int] = field(default_factory=lambda: [0] * 8)
    alpha_outputs: list[int] = field(default_factory=lambda: [0] * 8)
    factor0s: list[int] = field(default_factory=lambda: [0] * 8)
    factor1s: list[int] = field(default_factory=lambda: [0] * 8)

    def update(self, nv_op: int, nv_param: int):
        if nv_op == NV097_SET_COMBINER_CONTROL:
            self.control = nv_param
            return

        if nv_op == NV097_SET_SPECULAR_FOG_FACTOR_0:
            self.final_combiner_constant0 = nv_param
            return
        if nv_op == NV097_SET_SPECULAR_FOG_FACTOR_1:
            self.final_combiner_constant1 = nv_param
            return

        if nv_op == NV097_SET_COMBINER_SPECULAR_FOG_CW0:
            self.final_combiner_0 = nv_param
            return
        if nv_op == NV097_SET_COMBINER_SPECULAR_FOG_CW1:
            self.final_combiner_1 = nv_param
            return

        if nv_op >= NV097_SET_COMBINER_ALPHA_ICW_0 and nv_op <= NV097_SET_COMBINER_ALPHA_ICW_7:
            index = (nv_op - NV097_SET_COMBINER_ALPHA_ICW_0) // 4
            self.alpha_inputs[index] = nv_param
            return

        if nv_op >= NV097_SET_COMBINER_ALPHA_OCW_0 and nv_op <= NV097_SET_COMBINER_ALPHA_OCW_7:
            index = (nv_op - NV097_SET_COMBINER_ALPHA_OCW_0) // 4
            self.alpha_outputs[index] = nv_param
            return

        if nv_op >= NV097_SET_COMBINER_COLOR_ICW_0 and nv_op <= NV097_SET_COMBINER_COLOR_ICW_7:
            index = (nv_op - NV097_SET_COMBINER_COLOR_ICW_0) // 4
            self.color_inputs[index] = nv_param
            return

        if nv_op >= NV097_SET_COMBINER_COLOR_OCW_0 and nv_op <= NV097_SET_COMBINER_COLOR_OCW_7:
            index = (nv_op - NV097_SET_COMBINER_COLOR_OCW_0) // 4
            self.color_outputs[index] = nv_param
            return

        if nv_op >= NV097_SET_COMBINER_FACTOR0_0 and nv_op <= NV097_SET_COMBINER_FACTOR0_7:
            index = (nv_op - NV097_SET_COMBINER_FACTOR0_0) // 4
            self.factor0s[index] = nv_param
            return
        if nv_op >= NV097_SET_COMBINER_FACTOR1_0 and nv_op <= NV097_SET_COMBINER_FACTOR1_7:
            index = (nv_op - NV097_SET_COMBINER_FACTOR1_0) // 4
            self.factor1s[index] = nv_param
            return

    def explain(self) -> str:
        ret = ["// Color combiner:"]

        control = CombinerControlBitField(self.control)

        mux_type = "mux_MSB" if control.MUX_SELECT else "mux_LSB"

        def fixup_input(src: str, mapping: str) -> tuple[str, str]:
            if mapping == "UNSIGNED_IDENTITY":
                mapping = ""

            if src != "Zero":
                return src, mapping
            if mapping in {"", "SIGNED_IDENTITY"}:
                return "0", ""
            if mapping == "UNSIGNED_INVERT":
                return "1", ""
            return src, mapping

        def render_input(src: str, alpha: bool, mapping: str) -> str:
            alpha_str = ".a" if alpha else ".rgb"
            src, mapping = fixup_input(src, mapping)
            return f"{mapping}({src}{alpha_str})"

        for i in range(control.COUNT):
            ret.append(f"{i}:")

            factor_0 = ColorFactorBitField(self.factor0s[i] if control.FACTOR_0 else self.factor0s[0])
            factor_1 = ColorFactorBitField(self.factor1s[i] if control.FACTOR_1 else self.factor1s[0])

            def _process_icw(bitfield: ICWBitField):
                a_src = _ICW_SRC_VALUES[bitfield.A_SOURCE]
                a_map = _ICW_MAP_VALUES[bitfield.A_MAP]
                b_src = _ICW_SRC_VALUES[bitfield.B_SOURCE]
                b_map = _ICW_MAP_VALUES[bitfield.B_MAP]
                c_src = _ICW_SRC_VALUES[bitfield.C_SOURCE]
                c_map = _ICW_MAP_VALUES[bitfield.C_MAP]
                d_src = _ICW_SRC_VALUES[bitfield.D_SOURCE]
                d_map = _ICW_MAP_VALUES[bitfield.D_MAP]

                return (
                    render_input(a_src, bitfield.A_ALPHA, a_map),
                    render_input(b_src, bitfield.B_ALPHA, b_map),
                    render_input(c_src, bitfield.C_ALPHA, c_map),
                    render_input(d_src, bitfield.D_ALPHA, d_map),
                )

            def render_raw_op(value: str, op: int) -> str:
                if op == 1:
                    return f"({value}) - 0.5"
                if op == 2:
                    return f"({value}) * 2.0"
                if op == 3:
                    return f"(({value}) - 0.5) * 2.0"
                if op == 4:
                    return f"({value}) * 4.0"
                if op == 6:
                    return f"({value}) * 0.5"
                return f"{value}"

            def render_op(a: str, b: str, is_dot: bool, op: int) -> str:
                dot_str = " dot " if is_dot else " * "
                return render_raw_op(f"{a}{dot_str}{b}", op)

            def _append_output(
                a,
                b,
                c,
                d,
                output,
                factor_0: str,
                factor_1: str,
                swizzle: str,
                has_blue_to_alpha: bool,
                keep_discarded: bool = False,
            ):
                ab_dst = _OCW_DST_VALUES[output.AB_DST_REG]
                cd_dst = _OCW_DST_VALUES[output.CD_DST_REG]
                sum_dst = _OCW_DST_VALUES[output.SUM_DST_REG]
                ab_dot = " dot " if output.AB_DOT else " * "
                cd_dot = " dot " if output.CD_DOT else " * "
                mux = f" `{mux_type}` " if output.MUX else " + "

                if any(result != "Discard" or keep_discarded for result in (ab_dst, cd_dst, sum_dst)):
                    ret.append(f"  C0 = {factor_0}")
                    ret.append(f"  C1 = {factor_1}")
                if ab_dst != "Discard" or keep_discarded:
                    ret.append(f"  {ab_dst}.{swizzle} = {render_op(a, b, output.AB_DOT, output.OP)}")
                if cd_dst != "Discard" or keep_discarded:
                    ret.append(f"  {cd_dst}.{swizzle} = {render_op(c, d, output.CD_DOT, output.OP)}")
                if sum_dst != "Discard" or keep_discarded:
                    value = f"{a}{ab_dot}{b}{mux}{c}{cd_dot}{d}"
                    ret.append(f"  {sum_dst}.{swizzle} = {render_raw_op(value, output.OP)}")

                if has_blue_to_alpha:
                    if output.AB_BLUE_TO_ALPHA:
                        ret.append("  {ab_dst}.a = {ab_dst}.b")
                    if output.CD_BLUE_TO_ALPHA:
                        ret.append("  {cd_dst}.a = {cd_dst}.b")

            color_a, color_b, color_c, color_d = _process_icw(ICWBitField(self.color_inputs[i]))
            color_output = ColorOCWBitField(self.color_outputs[i])
            _append_output(
                color_a,
                color_b,
                color_c,
                color_d,
                color_output,
                str(factor_0),
                str(factor_1),
                "rgb",
                True,
            )

            alpha_a, alpha_b, alpha_c, alpha_d = _process_icw(ICWBitField(self.alpha_inputs[i]))
            alpha_output = AlphaOCWBitField(self.alpha_outputs[i])
            _append_output(
                alpha_a,
                alpha_b,
                alpha_c,
                alpha_d,
                alpha_output,
                str(factor_0),
                str(factor_1),
                "a",
                False,
            )

        output_0 = FinalCombiner0BitField(self.final_combiner_0)
        a_src = _ICW_SRC_VALUES[output_0.A_SOURCE]
        a_inverse = output_0.A_INVERSE
        a_alpha = output_0.A_ALPHA
        b_src = _ICW_SRC_VALUES[output_0.B_SOURCE]
        b_inverse = output_0.B_INVERSE
        b_alpha = output_0.B_ALPHA
        c_src = _ICW_SRC_VALUES[output_0.C_SOURCE]
        c_inverse = output_0.C_INVERSE
        c_alpha = output_0.C_ALPHA
        d_src = _ICW_SRC_VALUES[output_0.D_SOURCE]
        d_inverse = output_0.D_INVERSE
        d_alpha = output_0.D_ALPHA

        output_1 = FinalCombiner1BitField(self.final_combiner_1)
        e_src = _ICW_SRC_VALUES[output_1.E_SOURCE]
        e_alpha = output_1.E_ALPHA
        e_inverse = output_1.E_INVERSE
        f_src = _ICW_SRC_VALUES[output_1.F_SOURCE]
        f_alpha = output_1.F_ALPHA
        f_inverse = output_1.F_INVERSE
        g_src = _ICW_SRC_VALUES[output_1.G_SOURCE]
        g_alpha = output_1.G_ALPHA
        g_inverse = output_1.G_INVERSE

        def render_final_input(src: str, invert: bool, alpha: bool) -> str:
            mapping = _ICW_MAP_VALUES[0] if not invert else _ICW_MAP_VALUES[1]
            return render_input(src, alpha, mapping)

        a_component = render_final_input(a_src, a_inverse, a_alpha)
        b_component = render_final_input(b_src, b_inverse, b_alpha)
        c_component = render_final_input(c_src, c_inverse, c_alpha)
        d_component = render_final_input(d_src, d_inverse, d_alpha)
        e_component = render_final_input(e_src, e_inverse, e_alpha)
        f_component = render_final_input(f_src, f_inverse, f_alpha)
        g_component = render_final_input(g_src, g_inverse, g_alpha)

        flags = []
        if output_1.SPECULAR_ADD_INVERT_R12 == 0x20:
            flags.append("specular_add_invert_r0")
        if output_1.SPECULAR_ADD_INVERT_R5:
            flags.append("spec_add_invert_specular")
        if output_1.SPECULAR_CLAMP:
            flags.append("specular_clamp")

        ret.append(f"EFProd = {e_component} * {f_component}")
        ret.append(f"C0 = {ColorFactorBitField(self.final_combiner_constant0)}")
        ret.append(f"C1 = {ColorFactorBitField(self.final_combiner_constant1)}")
        if flags:
            flags_str = ", ".join(flags)
            ret.append(f"Flags = {flags_str}")
        ret.append(f"out.rgb = {d_component} + mix({c_component}, {b_component}, {a_component}")
        ret.append(f"out.a = {g_component}")
        ret.append("")

        return "\n".join(ret)
