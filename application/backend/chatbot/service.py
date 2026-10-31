"""Application-facing adapter for the existing RetailAI chatbot service."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CHATBOT_SERVICE_DIR = REPO_ROOT / "python-ai" / "chatbot"

if str(CHATBOT_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(CHATBOT_SERVICE_DIR))

from integration import process_project_message

__all__ = ["process_project_message"]
