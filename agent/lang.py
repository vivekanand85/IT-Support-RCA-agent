# agent/lang.py
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ja": "Japanese",
}

def language_instruction(code: str) -> str:
    name = LANGUAGE_NAMES.get(code, "English")
    if code == "en":
        return ""
    return f"\n\nWrite all human-readable text values in {name}. Keep any enum-like keys (issue_type, team names) in English exactly as specified."