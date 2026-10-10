from __future__ import annotations

import io
from contextlib import redirect_stdout

from nv2apretty.inline_array import (
    TYPE_FLOAT,
    TYPE_UB_D3D,
    InlineArrayTracker,
    VertexFormat,
)
from nv2apretty.prettify import _process_file


def test_vertex_format_parsing():
    # param = 0x2240 -> type=0 (UB D3D), size=4, stride=0x22 (34)
    vf = VertexFormat.from_param(0x2240)
    assert vf.attr_type == TYPE_UB_D3D
    assert vf.size == 4
    assert vf.stride == 34
    assert not vf.is_disabled

    # param = 0x2202 -> type=2 (Float), size=0 (disabled)
    vf_disabled = VertexFormat.from_param(0x2202)
    assert vf_disabled.attr_type == TYPE_FLOAT
    assert vf_disabled.size == 0
    assert vf_disabled.is_disabled

    # param = 0x2242 -> type=2 (Float), size=4
    vf_float = VertexFormat.from_param(0x2242)
    assert vf_float.attr_type == TYPE_FLOAT
    assert vf_float.size == 4
    assert not vf_float.is_disabled


def test_inline_array_tracker_basic():
    tracker = InlineArrayTracker()
    tracker.set_format(0, 0x2242)  # v0: Float, 4 components
    tracker.set_format(2, 0x2240)  # v2: UB D3D, 4 components (1 dword)

    tracker.begin_draw()
    # First vertex
    assert tracker.process_inline_array_param(0x0).startswith("v0[0]: 0.0")
    assert tracker.process_inline_array_param(0x0).startswith("v0[1]: 0.0")
    assert tracker.process_inline_array_param(0x3F800000).startswith("v0[2]: 1.0")
    assert tracker.process_inline_array_param(0x3F800000).startswith("v0[3]: 1.0")
    assert tracker.process_inline_array_param(0x40000000).startswith("v2: [0, 0, 0, 64]")

    # Second vertex (wraps around to v0[0])
    assert tracker.process_inline_array_param(0x0).startswith("v0[0]: 0.0")
    assert tracker.process_inline_array_param(0x43EF8000).startswith("v0[1]: 479.0")
    assert tracker.process_inline_array_param(0x3F800000).startswith("v0[2]: 1.0")
    assert tracker.process_inline_array_param(0x3F800000).startswith("v0[3]: 1.0")
    assert tracker.process_inline_array_param(0x40000000).startswith("v2: [0, 0, 0, 64]")

    tracker.end_draw()


def test_inline_array_tracker_short_and_packed():
    tracker = InlineArrayTracker()
    # v1: Short (type 5), size 2 (1 dword)
    # format: size=2 (0x20), type=5 (0x5) -> 0x25
    tracker.set_format(1, 0x0025)
    # v3: 3ComponentPacked (type 6), size 1 (1 dword)
    tracker.set_format(3, 0x0016)

    tracker.begin_draw()
    # Short: two 16-bit integers
    res = tracker.process_inline_array_param(0x00020001)
    assert res.startswith("v1[0..1]: [1, 2]")

    # 3ComponentPacked: 11-11-10
    res_packed = tracker.process_inline_array_param(0x00000000)
    assert res_packed.startswith("v3: [0, 0, 0]")

    tracker.end_draw()


def test_prettify_inline_array_issue_39_trace():
    trace = """nv2a_pgraph_method 0: 0x97 -> 0x1760 NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[0] 0x2242
nv2a_pgraph_method 0: 0x97 -> 0x1764 NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[1] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x1768 NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[2] 0x2240
nv2a_pgraph_method 0: 0x97 -> 0x176c NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[3] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x1770 NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[4] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x1774 NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[5] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x1778 NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[6] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x177c NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[7] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x1780 NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[8] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x1784 NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[9] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x1788 NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[10] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x178c NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[11] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x1790 NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[12] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x1794 NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[13] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x1798 NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[14] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x179c NV097_SET_VERTEX_DATA_ARRAY_FORMAT__POS[15] 0x2202
nv2a_pgraph_method 0: 0x97 -> 0x1720 NV097_SET_VERTEX_DATA_ARRAY_OFFSET__POS[0] 0x035c1000
nv2a_pgraph_method 0: 0x97 -> 0x1728 NV097_SET_VERTEX_DATA_ARRAY_OFFSET__POS[2] 0x035c1010
nv2a_pgraph_method 0: 0x97 -> 0x17fc NV097_SET_BEGIN_END 0x6
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x0
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x0
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x3f800000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x3f800000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x40000000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x0
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x43ef8000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x3f800000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x3f800000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x40000000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x441fc000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x0
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x3f800000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x3f800000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x40000000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x441fc000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x43ef8000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x3f800000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x3f800000
nv2a_pgraph_method 0: 0x97 -> 0x1818 NV097_INLINE_ARRAY 0x40000000
nv2a_pgraph_method 0: 0x97 -> 0x17fc NV097_SET_BEGIN_END 0x0
"""
    output = io.StringIO()
    with redirect_stdout(output):
        _process_file(
            trace.splitlines(),
            elide_draw_contents=False,
            add_blank_after_end=False,
            add_blanks_after_flip=False,
            decompile_shaders=False,
            explain_combiners=False,
            tracer_mode=False,
            summarize=False,
        )

    lines = output.getvalue().splitlines()
    inline_array_lines = [line for line in lines if "NV097_INLINE_ARRAY" in line]

    assert len(inline_array_lines) == 20
    # First vertex
    assert "(v0[0]: 0.0 <0x0>)" in inline_array_lines[0]
    assert "(v0[1]: 0.0 <0x0>)" in inline_array_lines[1]
    assert "(v0[2]: 1.0 <0x3f800000>)" in inline_array_lines[2]
    assert "(v0[3]: 1.0 <0x3f800000>)" in inline_array_lines[3]
    assert "(v2: [0, 0, 0, 64] <0x40000000>)" in inline_array_lines[4]

    # Second vertex
    assert "(v0[0]: 0.0 <0x0>)" in inline_array_lines[5]
    assert "(v0[1]: 479.0 <0x43ef8000>)" in inline_array_lines[6]
    assert "(v0[2]: 1.0 <0x3f800000>)" in inline_array_lines[7]
    assert "(v0[3]: 1.0 <0x3f800000>)" in inline_array_lines[8]
    assert "(v2: [0, 0, 0, 64] <0x40000000>)" in inline_array_lines[9]
