"""Importing this package registers every table with SQLAlchemy."""
from .gmail import GmailConnection
from .report import Report
from .scan import AnalysisResult, Scan, ThreatIndicator
from .token_blocklist import TokenBlocklist
from .user import User

__all__ = [
    "User", "Scan", "AnalysisResult", "ThreatIndicator",
    "Report", "TokenBlocklist", "GmailConnection",
]
