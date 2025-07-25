"""Setuptools entrypoint for debugger."""

# ruff: noqa: PLR2004 Magic value used in comparison

from __future__ import annotations

from nv2apretty import prettify


def prettify_file():
    """Generate a prettified version of the input."""
    prettify.entrypoint()
