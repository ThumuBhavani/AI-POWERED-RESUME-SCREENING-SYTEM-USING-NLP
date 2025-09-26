import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def score_resume(resume_vec: np.ndarray, jd_vec: np.ndarray) -> float:
    return float(cosine_similarity([resume_vec], [jd_vec])[0][0])

def explain_match(cand_skills, jd_skills):
    matched = sorted(cand_skills & jd_skills)
    missing = sorted(jd_skills - cand_skills)
    return matched, missing
