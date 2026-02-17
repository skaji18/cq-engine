"""CQ Engine MCP Server — Cognitive Quality Engineering for LLM Agents.

Provides cognitive quality tools, resources, and telemetry for Claude Code.
Install: claude mcp add cq-engine -- python server.py
"""

import functools
import json
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Import tools
from tools.decompose import decompose
from tools.gate import gate
from tools.persona import persona
from tools.cqlint_tool import cqlint
from tools.mutate import mutate
from tools.learn import learn

# Import resources
from resources.patterns import patterns_catalog
from resources.learned import learned_entries

# Import telemetry
from telemetry.collector import TelemetryCollector

# --- Initialize ---

mcp = FastMCP(
    "cq-engine",
    description="Cognitive Quality Engineering for LLM Agents",
)
telemetry = TelemetryCollector()


# --- Telemetry wrapper ---

def wrap_with_telemetry(tool_func, tool_name):
    """Wrap a tool function with telemetry emission."""

    @functools.wraps(tool_func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await tool_func(*args, **kwargs)
            duration_ms = int((time.time() - start) * 1000)
            telemetry.emit("tool_invocation", f"cq_engine__{tool_name}", {
                "_duration_ms": duration_ms,
                "status": "success",
            })
            return result
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            telemetry.emit("tool_invocation", f"cq_engine__{tool_name}", {
                "_duration_ms": duration_ms,
                "status": "error",
                "error": str(e),
            })
            return json.dumps({"error": str(e)})

    return wrapper


# --- Register tools with telemetry ---

mcp.tool()(wrap_with_telemetry(decompose, "decompose"))
mcp.tool()(wrap_with_telemetry(gate, "gate"))
mcp.tool()(wrap_with_telemetry(persona, "persona"))
mcp.tool()(wrap_with_telemetry(cqlint, "cqlint"))
mcp.tool()(wrap_with_telemetry(mutate, "mutate"))
mcp.tool()(wrap_with_telemetry(learn, "learn"))


# --- Register resources ---

@mcp.resource("cq_engine://patterns")
async def patterns_resource() -> str:
    """CQE Pattern catalog — 8 cognitive quality patterns."""
    return await patterns_catalog()


@mcp.resource("cq_engine://learned")
async def learned_resource() -> str:
    """Accumulated learnings from agent sessions."""
    return await learned_entries()


@mcp.resource("cq_engine://health")
async def health_resource() -> str:
    """CQ Health Dashboard — 4-axis cognitive quality scores."""
    weekly = telemetry.get_weekly_summary()
    pattern_usage = telemetry.get_pattern_usage()
    return json.dumps({
        "weekly_summary": weekly,
        "pattern_usage": pattern_usage,
        "version": "0.1.0",
    }, indent=2)


# --- Entry point ---

def main():
    """Run the CQ Engine MCP Server."""
    mcp.run()


if __name__ == "__main__":
    main()
