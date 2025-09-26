import re

def basic_clean(s: str) -> str:
    s = s.lower()
    s = re.sub(r'\s+', ' ', s)
    return s.strip()
