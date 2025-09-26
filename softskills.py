SOFT_PATTERNS = {
    "teamwork": ["team player", "collaborated", "worked with", "teamwork", "team oriented"],
    "leadership": ["led", "mentored", "managed", "supervised", "headed"],
    "communication": ["presented", "communicated", "wrote", "spoke", "explained", "reporting"],
    "problem-solving": ["problem solving", "resolved", "troubleshot", "solved"],
    "adaptability": ["adapted", "flexible", "adjusted", "quick learner"],
    "creativity": ["creative", "innovative", "designed", "brainstormed"],
    "time management": ["organized", "prioritized", "planned", "time management"],
    "critical thinking": ["analyzed", "evaluated", "reviewed", "assessed"]
}

def extract_soft_skills(text: str):
    found = set()
    t = text.lower()
    for label, keys in SOFT_PATTERNS.items():
        if any(k in t for k in keys):
            found.add(label)
    return found
