Visualizer for nv2a logs (as written by [xemu](https://xemu.app)
or [xbdm_gdb_bridge](https://github.com/abaire/xbdm_gdb_bridge)) and other Microsoft Xbox data.

# Use

## With xemu/nv2a-trace style PGRAPH logs

Run `nv2apretty` with `--help` to see command line options.

Or use the Anvil hosted version at https://unfortunate-soupy-entry.anvil.app/

## With binary `D3DPIXELSHADERDEF` instances

Binary blobs (or b-prefixed byte strings) containing `D3DPIXELSHADERDEF` structs
may be expanded into color combiner explanations using the pixel shader def
tool, `nv2apretty-psd`.

# Development

See https://github.com/abaire/nv2a-define-collator for generation of most of the parsers/prettifiers.
