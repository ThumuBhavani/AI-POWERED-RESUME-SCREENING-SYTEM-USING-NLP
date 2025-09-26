import json
from typing import Dict, List, Set

def load_skills(path="data/skills_master.json") -> Dict[str, List[str]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_skills(text: str, skills_master: Dict[str, List[str]]) -> Set[str]:
    found = set()
    for cat, skills in skills_master.items():
        for sk in skills:
            if f" {sk.lower()} " in f" {text.lower()} ":
                found.add(sk.lower())
    return found

def skill_gap(cand_skills: Set[str], jd_skills: Set[str]) -> Set[str]:
    return jd_skills - cand_skills
