ERROR_KEYWORDS = ["error", "exception", "fail", "denied", "timeout", "critical"]


def extract_issue_from_log(log_text: str, max_lines: int = 30) -> str:
    lines = log_text.splitlines()
    error_lines = []
    seen = set()

    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in ERROR_KEYWORDS):
            cleaned = line.strip()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                error_lines.append(cleaned)

    if not error_lines:
        fallback = [l.strip() for l in lines[-10:] if l.strip()]
        return "\n".join(fallback) if fallback else "No content found in log file."

    return "\n".join(error_lines[:max_lines])