"""In-memory session store for the AI advisor chat.

Sessions are kept in a simple process-local dict — no external service required.
Each session is a list of chat messages ({"role": ..., "content": ...}).
"""

AI_SESSIONS: dict[str, list] = {}


def session_get(session_id: str) -> list | None:
    return AI_SESSIONS.get(session_id)


def session_set(session_id: str, messages: list) -> None:
    """Write a full message list, replacing any existing session."""
    AI_SESSIONS[session_id] = messages


def session_append(session_id: str, message: dict) -> None:
    """Append a single message to an existing (or new) session."""
    AI_SESSIONS.setdefault(session_id, []).append(message)
