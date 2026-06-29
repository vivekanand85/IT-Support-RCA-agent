# Tracks which (user_id, issue_type) combos already had an automated fix tried.
# If the same combo shows up again, that's the signal the fix didn't actually
# work - same idea as your AWS example: automated check first, real person
# steps in only once it's clear the automated pass didn't resolve it.

_resolved_before: set[tuple[str, str]] = set()


def mark_as_attempted(user_id: str, issue_type: str) -> None:
    _resolved_before.add((user_id, issue_type))


def was_already_attempted(user_id: str, issue_type: str) -> bool:
    return (user_id, issue_type) in _resolved_before