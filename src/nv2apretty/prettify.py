#!/usr/bin/env python3

"""Prettify nv2a_trace log.

This program reads nv2a_trace information (as emitted from xemu) and extends it with user-friendly information.

E.g., expanding things like:

nv2a_pgraph_method 0: 0x97 -> 0x0288 NV097_SET_COMBINER_SPECULAR_FOG_CW0[0] 0xc

to:

nv2a_pgraph_method 0: NV20_KELVIN_PRIMITIVE<0x97> -> NV097_SET_COMBINER_SPECULAR_FOG_CW0<0x288> (0xC {[A: Zero], [B: Zero], [C: Zero], [D: R0Temp]})
"""

# ruff: noqa: T201 `print` found
# ruff: noqa: PLR2004 Magic value used in comparison
# ruff: noqa: FBT001 Boolean-typed positional argument in function definition
# ruff: noqa: FBT002 Boolean default positional argument in function definition
# ruff: noqa: UP031 Use format specifiers instead of percent format

from __future__ import annotations

import argparse
import copy
import logging
import os
import re
import sys
from collections import defaultdict
from contextlib import redirect_stdout
from enum import Enum, auto
from typing import TYPE_CHECKING
from xml.sax import saxutils

from nv2a_vsh import disassemble

from nv2apretty import deep_processing, pvideo
from nv2apretty.deep_processing import process_shader_stage_program
from nv2apretty.subprocessors.frame_summary import FrameSummary

if TYPE_CHECKING:
    from typing import TextIO

logger = logging.getLogger(__name__)

_HEX_VALUE = r"0x[0-9a-fA-F]+"
_CAP_HEX_VALUE = r"(" + _HEX_VALUE + r")"

_SUBCHANNEL = r"(\d+)"
_CLASS = _CAP_HEX_VALUE
_OP = _CAP_HEX_VALUE
_OPNAME = r"(?:\S+\s+)?"
_PARAM = _CAP_HEX_VALUE

# nv2a_pgraph_method -1: 0x0 -> 0x0000 message [0] 0x0
_PGRAPH_MESSAGE_HACK_RE = re.compile(r"nv2a_pgraph_method -1: 0x0 -> 0x0000\s+(.+)\[0\]\s+0x0$")

# nv2a_pgraph_method 0: 0x97 -> 0x0680 NV097_SET_COMPOSITE_MATRIX[0] 0x43d0841d
_PGRAPH_METHOD_RE = re.compile(
    r"nv2a_pgraph_method\s+" + _SUBCHANNEL + r":\s+" + _CLASS + r"\s+->\s+" + _OP + r"\s+" + _OPNAME + _PARAM
)

_UNHANDLED_METHOD_RE = re.compile(
    r"nv2a_pgraph_method_unhandled\s+" + _SUBCHANNEL + r":\s+" + _CLASS + r"\s+->\s+" + _OP + r"\s+" + _PARAM
)

# nv2a_reg_write PVIDEO addr 0xb00 size 4 val 0x0
_PVIDEO_REG_WRITE_RE = re.compile(
    r"nv2a_reg_write PVIDEO addr " + _CAP_HEX_VALUE + r" size (\d+) val " + _CAP_HEX_VALUE
)

# nv2a_reg_write PCRCT addr 0x800 size 4 val 0x0
_PCRTC_REG_WRITE_RE = re.compile(r"nv2a_reg_write PCRTC addr " + _CAP_HEX_VALUE + r" size (\d+) val " + _CAP_HEX_VALUE)

# nv2a_reg_write PMC addr 0x200 size 4 val 0x0
_PMC_REG_WRITE_RE = re.compile(r"nv2a_reg_write PMC addr " + _CAP_HEX_VALUE + r" size (\d+) val " + _CAP_HEX_VALUE)

# <command op="0x310" name="?[0]" value="0x7ed4c40f"/>
_CONTEXT_COMMAND_RE = re.compile(
    r"\s*<command op=\""
    + _CAP_HEX_VALUE
    + r'"\s+channel="'
    + _SUBCHANNEL
    + r'"\s+class="'
    + _CAP_HEX_VALUE
    + '".*value="'
    + _CAP_HEX_VALUE
    + '"/>'
)


def _prettify_pgraph_method(channel: int, nv_class: int, nv_op: int, nv_param: int) -> deep_processing.CommandInfo:
    return deep_processing.get_command_info(channel, nv_class, nv_op, nv_param)


class Tag(Enum):
    BEGIN_TAG = auto()
    END_TAG = auto()
    FLIP_STALL_TAG = auto()
    CLEAR_SURFACE_TAG = auto()
    SEMAPHORE_RELEASE_TAG = auto()
    PIPELINE = auto()
    SHADER_STAGE_PROGRAM = auto()
    SET_TEXGEN = auto()


NV097_SET_NORMALIZATION_ENABLE = 0x3A4
NV097_SET_SHADER_STAGE_PROGRAM = 0x1E70


def _process_pgraph_command(channel, nv_class, nv_op, nv_param) -> tuple[Tag | None, str | None]:
    """Extracts extra information about a pgraph command.

    Returns an optional tag providing meta information and an optional string providing summary text."""
    if channel != 0x00:
        return None, None
    if nv_class != 0x97:
        return None, None

    if nv_op == 0x17FC:
        return Tag.END_TAG if not nv_param else Tag.BEGIN_TAG, None

    if nv_op == 0x130:
        return Tag.FLIP_STALL_TAG, None

    if nv_op == 0x1D70:
        return Tag.SEMAPHORE_RELEASE_TAG, None

    if nv_op == 0x1D94:
        return Tag.CLEAR_SURFACE_TAG, None

    if nv_op == 0x1E94:
        if (nv_param & 0x02) == 0x00:
            return Tag.PIPELINE, FrameSummary.PIPELINE_FIXED
        return Tag.PIPELINE, FrameSummary.PIPELINE_PROGRAMMABLE

    if nv_op == NV097_SET_SHADER_STAGE_PROGRAM:
        return (
            None,
            f"Texture stage setup: {process_shader_stage_program(nv_class, nv_op, nv_param)}",
        )

    if nv_op == NV097_SET_NORMALIZATION_ENABLE:
        return (None, f"Normalization: {nv_param}")

    return None, None


NV097_SET_TRANSFORM_PROGRAM_START = 0x1EA0
NV097_SET_TRANSFORM_PROGRAM_RANGE_BASE = 0x0B00
NV097_SET_TRANSFORM_PROGRAM_RANGE_END = 0x0B7C


def _disassemble_vertex_shader(machine_code: list[int], *, explain: bool = False) -> list[str]:
    num_values = len(machine_code)

    # Split the 16-byte instructions into sublists.
    if (num_values % 4) != 0:
        msg = f"Invalid input, {num_values} is not divisible by 4."
        raise ValueError(msg)

    opcodes = [machine_code[start : start + 4] for start in range(0, num_values, 4)]
    try:
        return disassemble.disassemble(opcodes, explain=explain)
    except ValueError:
        logger.exception("Failed to disassmble:\n%s\n", opcodes)
        raise


def _print_file_summary(frame_summaries: list[FrameSummary], print_fun, output_stream):
    print_fun("-- File summary --------", file=output_stream)
    print_fun(f"{len(frame_summaries)} frames total", file=output_stream)

    unique_combiners: set[str] = set()
    unique_fixed_function_shaders: set[str] = set()
    unique_programmable_shaders: set[str] = set()

    for summary in frame_summaries:
        unique_combiners.update(summary.draws_by_combiner.keys())
        unique_programmable_shaders.update(summary.draws_by_programmable_shader.keys())
        unique_fixed_function_shaders.update(summary.unique_fixed_function_shaders)

    print_fun(f"Unique combiners: {len(unique_combiners)}")
    print_fun(f"Unique programmable shaders: at least {len(unique_programmable_shaders)}")
    print_fun(f"Unique fixed function shaders: at least {len(unique_fixed_function_shaders)}")


def _process_file(
    lines: list[str],
    elide_draw_contents: bool,
    add_blank_after_end: bool,
    add_blanks_after_flip: bool,
    decompile_shaders: bool,
    explain_combiners: bool,
    tracer_mode: bool,
    summarize: bool,
    suppress_raw_commands: bool = False,
    suppress_draw_summaries: bool = False,
    suppress_frame_summaries: bool = False,
    suppress_file_summaries: bool = False,
    summary_output_stream: TextIO = sys.stderr,
) -> None:
    inside_begin_end = False
    elided_commands: dict[tuple[int, int, int], list[int]] = defaultdict(list)

    shader_program: list[int] = []

    log_frame_summaries: list[FrameSummary] = []
    current_frame_summary = FrameSummary()

    def nop(*args, **kwargs):
        del args
        del kwargs

    raw = nop if suppress_raw_commands else print
    draw_summary = nop if suppress_draw_summaries else print
    frame_summary = nop if suppress_frame_summaries else print
    file_summary = nop if suppress_file_summaries else print

    def _print_elided_command_summary(elided_commands):
        for (channel, nv_class, nv_op), params in elided_commands.items():
            result = _prettify_pgraph_method(channel, nv_class, nv_op, params[0])
            result = result.get_pretty_string()
            raw(f"  ... Skipped {len(params)} commands like {result[22:]} ...")

    def _print_pretty_context_tag(command_info: deep_processing.CommandInfo):
        if not command_info.nv_op_name:
            raw(
                f"WARNING: UNKNOWN 0x{command_info.nv_class:x}:0x{command_info.nv_op:x}",
                file=sys.stderr,
            )
        raw(
            "        <command "
            f'op="0x{command_info.nv_op:x}" '
            f'channel="{command_info.channel}" '
            f'class="0x{command_info.nv_class:x}" '
            f'class_name="{saxutils.escape(command_info.nv_class_name)}" '
            f'name="{saxutils.escape(command_info.nv_op_name)}" '
            f'value="0x{command_info.nv_param:x}" '
            f'value_info="{saxutils.escape(command_info.param_info)}" '
            "/>"
        )

    def _print_unhandled_method(subchannel, nv_class, nv_op, nv_param=None):
        if not subchannel:
            subchannel = 0
        param_text = (" 0x%X" % nv_param) if nv_param is not None else ""
        entry = deep_processing.get_command_info(subchannel, nv_class, nv_op, nv_param)
        if entry is None:
            raw("nv2a_pgraph_method_unhandled %d: 0x%X -> 0x%X%s" % (subchannel, nv_class, nv_op, param_text))
            return
        raw(f"nv2a_pgraph_method_unhandled {entry.pretty_suffix}{param_text}")

    for line in lines:
        match = _PGRAPH_MESSAGE_HACK_RE.match(line)
        if match:
            raw(match.group(1))
            continue

        match = _PVIDEO_REG_WRITE_RE.match(line)
        if match:
            entry = pvideo.process(int(match.group(1), 16), int(match.group(2)), int(match.group(3), 16))
            raw("nv2a_reg_write PVIDEO " + entry)
            continue

        match = _PCRTC_REG_WRITE_RE.match(line)
        if match:
            continue

        match = _PMC_REG_WRITE_RE.match(line)
        if match:
            continue

        match = _PGRAPH_METHOD_RE.match(line)
        if match:
            channel = int(match.group(1), 0)
            nv_class = int(match.group(2), 16)
            nv_op = int(match.group(3), 16)
            nv_param = int(match.group(4), 16)

            is_vertex_shader_upload = (
                nv_op >= NV097_SET_TRANSFORM_PROGRAM_RANGE_BASE and nv_op <= NV097_SET_TRANSFORM_PROGRAM_RANGE_END
            )
            if decompile_shaders:
                if is_vertex_shader_upload:
                    shader_program.append(nv_param)
                elif shader_program:
                    disassembled = _disassemble_vertex_shader(shader_program)
                    current_frame_summary.active_shader = "\n".join(disassembled)
                    raw()
                    raw(f"//! Vertex shader program [{len(disassembled)}]")
                    raw(current_frame_summary.active_shader)
                    raw()
                    shader_program.clear()
            elif current_frame_summary.pipeline == FrameSummary.PIPELINE_UNKNOWN and is_vertex_shader_upload:
                # Assume that the pipeline is programmable if the program is uploading a vertex shader.
                current_frame_summary.pipeline = FrameSummary.PIPELINE_ASSUMED_PROGRAMMABLE

            if nv_class == 0x97:
                current_frame_summary.update(nv_op, nv_param)

            block_marker, summary_text = _process_pgraph_command(channel, nv_class, nv_op, nv_param)

            if block_marker == Tag.END_TAG:
                if elided_commands:
                    _print_elided_command_summary(elided_commands)
                    elided_commands = defaultdict(list)
                inside_begin_end = False
            elif block_marker == Tag.BEGIN_TAG and explain_combiners:
                raw(current_frame_summary.combiner_state.explain())
            elif block_marker == Tag.PIPELINE:
                if summary_text:
                    current_frame_summary.pipeline = summary_text
            elif summary_text:
                current_frame_summary.draw_summary_messages.append(summary_text)

            if elide_draw_contents and inside_begin_end and nv_class == 0x97:
                elided_commands[(channel, nv_class, nv_op)].append(nv_param)
            else:
                result = _prettify_pgraph_method(channel, nv_class, nv_op, nv_param)
                raw(result.get_pretty_string())

            if block_marker == Tag.BEGIN_TAG:
                inside_begin_end = True
                if tracer_mode:
                    raw(
                        f"frame_draw {current_frame_summary.frame_draw_count} surface_dump {current_frame_summary.surface_dump_count}"
                    )
                    current_frame_summary.surface_dump_count += 1
                current_frame_summary.frame_draw_count += 1
            elif block_marker == Tag.END_TAG:
                if summarize:
                    draw_summary(
                        f"== Draw {current_frame_summary.frame_draw_count - 1} summary: ============",
                        file=summary_output_stream,
                    )
                    draw_summary(f"  Pipeline: {current_frame_summary.pipeline}", file=summary_output_stream)
                    if current_frame_summary.pipeline == FrameSummary.PIPELINE_UNKNOWN:
                        current_frame_summary.pipeline = FrameSummary.PIPELINE_ASSUMED_FIXED
                    if current_frame_summary.is_fixed_function:
                        draw_summary(str(current_frame_summary.fixed_function_shader_state), file=summary_output_stream)
                    for summary_message in sorted(current_frame_summary.draw_summary_messages):
                        draw_summary(f"  {summary_message}", file=summary_output_stream)
                    draw_summary("\n", file=summary_output_stream)
                if add_blank_after_end:
                    raw("\n")
                current_frame_summary.draws_by_pipeline[current_frame_summary.pipeline] += 1
                current_frame_summary.draws_by_combiner[current_frame_summary.combiner_state.explain()] += 1
                current_frame_summary.draw_summary_messages.clear()

                if current_frame_summary.pipeline == "Programmable":
                    if current_frame_summary.active_shader:
                        current_frame_summary.draws_by_programmable_shader[current_frame_summary.active_shader] += 1
                else:
                    current_frame_summary.unique_fixed_function_shaders.add(
                        str(current_frame_summary.fixed_function_shader_state)
                    )

            elif block_marker == Tag.FLIP_STALL_TAG:
                if summarize:
                    frame_summary("== Frame summary: ================", file=summary_output_stream)
                    frame_summary(f"  {current_frame_summary.frame_draw_count} draws", file=summary_output_stream)
                    fixed_function_draws = (
                        current_frame_summary.draws_by_pipeline[FrameSummary.PIPELINE_FIXED]
                        + current_frame_summary.draws_by_pipeline[FrameSummary.PIPELINE_ASSUMED_FIXED]
                    )
                    programmable_draws = (
                        current_frame_summary.draws_by_pipeline[FrameSummary.PIPELINE_PROGRAMMABLE]
                        + current_frame_summary.draws_by_pipeline[FrameSummary.PIPELINE_ASSUMED_PROGRAMMABLE]
                    )
                    frame_summary(
                        f"    Fixed function: {fixed_function_draws}  Programmable: {programmable_draws}",
                        file=summary_output_stream,
                    )
                    if current_frame_summary.draws_by_programmable_shader:
                        frame_summary(
                            f"      {len(current_frame_summary.draws_by_programmable_shader)} unique vertex shader programs",
                            file=summary_output_stream,
                        )
                    if current_frame_summary.draws_by_combiner:
                        frame_summary(
                            f"    {len(current_frame_summary.draws_by_combiner)} unique combiners",
                            file=summary_output_stream,
                        )
                    if len(current_frame_summary.unique_fixed_function_shaders) > 1:
                        frame_summary(
                            f"    At least {len(current_frame_summary.unique_fixed_function_shaders)} unique fixed function shaders",
                            file=summary_output_stream,
                        )
                    frame_summary("\n", file=summary_output_stream)
                if add_blanks_after_flip:
                    raw("\n")

                log_frame_summaries.append(current_frame_summary)
                current_frame_summary = copy.deepcopy(current_frame_summary)
                current_frame_summary.reset()
            elif tracer_mode and block_marker in {
                Tag.CLEAR_SURFACE_TAG,
                Tag.SEMAPHORE_RELEASE_TAG,
            }:
                raw(f"surface_dump {current_frame_summary.surface_dump_count}")
                current_frame_summary.surface_dump_count += 1

            continue

        match = _CONTEXT_COMMAND_RE.match(line)
        if match:
            nv_op = int(match.group(1), 16)
            channel = int(match.group(2), 0)
            nv_class = int(match.group(3), 16)
            nv_param = int(match.group(4), 16)
            command_info = _prettify_pgraph_method(channel, nv_class, nv_op, nv_param)
            _print_pretty_context_tag(command_info)
            continue

        match = _UNHANDLED_METHOD_RE.match(line)
        if match:
            _print_unhandled_method(
                int(match.group(1), 10),
                int(match.group(2), 16),
                int(match.group(3), 16),
                int(match.group(4), 16),
            )
            continue

        raw(line)

    if summarize and not suppress_file_summaries:
        _print_file_summary(log_frame_summaries, file_summary, summary_output_stream)


def prettify(
    filename: str,
    output: str | None = None,
    *,
    elide: bool = False,
    insert_space_after_ends: bool = False,
    add_blanks_after_flip: bool = False,
    decompile_shaders: bool = False,
    explain_combiners: bool = False,
    tracer_mode: bool = False,
    summarize: bool = False,
    suppress_raw_commands: bool = False,
    suppress_draw_summaries: bool = False,
    suppress_frame_summaries: bool = False,
    suppress_file_summaries: bool = False,
    summary_output_stream: TextIO = sys.stderr,
):
    """Prettifies the given nv2a log file."""

    with open(filename, encoding="utf-8") as infile:
        lines = [line.rstrip() for line in infile]

    if output:
        output = os.path.realpath(os.path.expanduser(output))
        with open(output, "w") as out_file, redirect_stdout(out_file):
            _process_file(
                lines,
                elide,
                insert_space_after_ends,
                add_blanks_after_flip,
                decompile_shaders,
                explain_combiners,
                tracer_mode,
                summarize,
                suppress_raw_commands=suppress_raw_commands,
                suppress_draw_summaries=suppress_draw_summaries,
                suppress_frame_summaries=suppress_frame_summaries,
                suppress_file_summaries=suppress_file_summaries,
                summary_output_stream=summary_output_stream,
            )
    else:
        _process_file(
            lines,
            elide,
            insert_space_after_ends,
            add_blanks_after_flip,
            decompile_shaders,
            explain_combiners,
            tracer_mode,
            summarize,
            suppress_raw_commands=suppress_raw_commands,
            suppress_draw_summaries=suppress_draw_summaries,
            suppress_frame_summaries=suppress_frame_summaries,
            suppress_file_summaries=suppress_file_summaries,
            summary_output_stream=summary_output_stream,
        )


def _main(args):
    filename = args.input
    filename = os.path.realpath(os.path.expanduser(filename))

    def get_arg(explicit_opt) -> bool:
        if explicit_opt is not None:
            return explicit_opt
        return args.extra_info

    summary_output_stream = sys.stderr if args.summarize_to_stderr else sys.stdout

    prettify(
        filename,
        args.output,
        elide=args.elide,
        insert_space_after_ends=get_arg(args.insert_space_after_ends),
        add_blanks_after_flip=get_arg(args.insert_space_after_flips),
        decompile_shaders=get_arg(args.decompile_shaders),
        explain_combiners=get_arg(args.explain_combiners),
        tracer_mode=args.tracer_mode,
        summarize=get_arg(args.summarize) or get_arg(args.summarize_frames_only),
        suppress_raw_commands=args.summarize_frames_only,
        suppress_draw_summaries=args.summarize_frames_only,
        summary_output_stream=summary_output_stream,
    )


def entrypoint():
    def _parse_args():
        parser = argparse.ArgumentParser()

        parser.add_argument("input", help="Input file.")
        parser.add_argument("output", nargs="?", help="Output file.")
        parser.add_argument(
            "--elide",
            "-e",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="Elide geometry commands within BEGIN_END blocks.",
        )
        parser.add_argument(
            "--insert-space-after-ends",
            "-i",
            action=argparse.BooleanOptionalAction,
            help="Insert blank lines after BEGIN_END end statements.",
        )
        parser.add_argument(
            "--insert-space-after-flips",
            "-I",
            action=argparse.BooleanOptionalAction,
            help="Insert blank lines after FLIP_STALL statements.",
        )
        parser.add_argument(
            "--decompile-shaders",
            "-S",
            action=argparse.BooleanOptionalAction,
            help="Decompile vertex shaders (NV097_SET_TRANSFORM_PROGRAM) inline.",
        )
        parser.add_argument(
            "--explain-combiners",
            "-C",
            action=argparse.BooleanOptionalAction,
            help="Summarize color combiners.",
        )
        parser.add_argument(
            "-T",
            "--tracer-mode",
            action=argparse.BooleanOptionalAction,
            help="Insert surface dump counting statements (for use with ntrc_dyndxt traces).",
        )
        parser.add_argument(
            "-s",
            "--summarize",
            action=argparse.BooleanOptionalAction,
            help="Generates per-draw/per-frame summarization information.",
        )
        parser.add_argument(
            "--summarize-frames-only",
            action="store_true",
            help="Generates per-frame summaries and suppresses other output.",
        )
        parser.add_argument(
            "-X",
            "--extra-info",
            action="store_true",
            help="Enables formatting, shader and combiner decompilation, and per-draw/per-frame summaries.",
        )
        parser.add_argument(
            "--summarize-to-stderr", action="store_true", help="Writes summary information to stderr instead of stdout"
        )
        return parser.parse_args()

    sys.exit(_main(_parse_args()))


if __name__ == "__main__":
    entrypoint()
