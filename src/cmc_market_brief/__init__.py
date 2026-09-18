"""CoinMarketCap-powered market brief utilities."""

from .analysis import build_brief, format_markdown
from .client import CMCClient

__all__ = ["CMCClient", "build_brief", "format_markdown"]
__version__ = "0.1.0"
