from __future__ import annotations

import collections
from dataclasses import dataclass, field

from nv2apretty.subprocessors.color_combiner import CombinerState
from nv2apretty.subprocessors.fixed_function_shader import FixedFunctionPipelineState


@dataclass
class FrameSummary:
    PIPELINE_UNKNOWN = "Unknown"
    PIPELINE_FIXED = "Fixed function"
    PIPELINE_PROGRAMMABLE = "Programmable"
    PIPELINE_ASSUMED_PROGRAMMABLE = "Programmable (assumed)"
    PIPELINE_ASSUMED_FIXED = "Fixed function (assumed)"

    active_shader: str | None = None
    surface_dump_count: int = 0
    frame_draw_count: int = 0
    combiner_state: CombinerState = field(default_factory=lambda: CombinerState())

    fixed_function_shader_state: FixedFunctionPipelineState = field(
        default_factory=lambda: FixedFunctionPipelineState()
    )

    pipeline: str = PIPELINE_UNKNOWN
    draws_by_pipeline: dict[str, int] = field(default_factory=lambda: collections.defaultdict(int))
    draw_summary_messages: list[str] = field(default_factory=list)

    # Counts the number of draws used by each unique pixel shader.
    draws_by_combiner: dict[str, int] = field(default_factory=lambda: collections.defaultdict(int))

    # Count the number of draws used by each unique vertex shader.
    draws_by_programmable_shader: dict[str, int] = field(default_factory=lambda: collections.defaultdict(int))

    unique_fixed_function_shaders: set[str] = field(default_factory=set)

    @property
    def is_fixed_function(self) -> bool:
        return self.pipeline in {FrameSummary.PIPELINE_FIXED, FrameSummary.PIPELINE_ASSUMED_FIXED}

    def reset(self):
        self.frame_draw_count = 0
        self.surface_dump_count = 0
        self.draws_by_pipeline.clear()
        self.draws_by_combiner.clear()
        self.draws_by_programmable_shader.clear()
        self.unique_fixed_function_shaders.clear()

    def update(self, nv_op: int, nv_param: int):
        self.combiner_state.update(nv_op, nv_param)
        self.fixed_function_shader_state.update(nv_op, nv_param)
