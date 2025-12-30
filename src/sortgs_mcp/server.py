"""MCP server entry point for Sort Google Scholar."""

import logging
import sys

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:

    class FastMCP:
        """Fallback MCP stub for environments without the mcp package."""

        def __init__(self, *args, **kwargs) -> None:
            pass

        def tool(self):
            def decorator(func):
                return func

            return decorator

        def run(self, *args, **kwargs) -> None:
            raise RuntimeError("mcp package is required to run the MCP server")


from sortgs_mcp.config import settings

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging() -> logging.Logger:
    """Configure logging to file (DEBUG) and stderr (WARNING+)."""
    log_dir = settings.data_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logfile = log_dir / "sortgs_mcp.log"

    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = logging.FileHandler(logfile)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    return logging.getLogger(__name__)


logger = setup_logging()
mcp = FastMCP("sortgs-mcp")


def main() -> None:
    """Entry point for the MCP server."""
    from sortgs_mcp.tools import (
        download,
    )  # noqa: F401  # Registers tools via decorators
    from sortgs_mcp.tools import search  # noqa: F401  # Registers tools via decorators

    logger.info("Starting Sort Google Scholar MCP Server")
    if settings.openai_api_key is None:
        logger.warning("OPENAI_API_KEY not set - LLM-based tools will not work")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
