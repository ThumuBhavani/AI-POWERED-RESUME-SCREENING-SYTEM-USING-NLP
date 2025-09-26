# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Tuple
from uuid import uuid4

# --- core helpers (your files) ---
from core.parsing import extract_text
from core.cleaning import basic_clean
from core.skills import load_skills, extract_skills
from core.embedding import embed_text
from core.ranking import score_resume, explain_match
from core.softskills import extract_soft_skills
from core.duplicates import is_duplicate

# rapidfuzz for fuzzy filename matching
try:
    from rapidfuzz import process as rf_process
except Exception:
    rf_process = None

# -------------------------------
# Streamlit page setup + CSS
# -------------------------------
st.set_page_config(page_title="AI Resume Screening System Using NLP", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f7fbff 0%, #ffffff 40%);
    }
    .hero {
        background: linear-gradient(90deg,#ffffffaa,#e9f3ff);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 6px 18px rgba(46,134,193,0.08);
        margin-bottom: 20px;
        text-align: center;
    }
    .hero h1 {
        color: #113b5c;
        font-size: 38px;
        margin-bottom: 5px;
    }
    .hero h3 {
        color: #2E86C1;
        margin-top: 0;
    }
    .feature-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    [data-testid="stSidebar"] {
        background-color: #f1f6fb;
    }
    div.stButton > button {
        background-color: #2E86C1;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    .stDataFrame > div { 
        border-radius: 10px; 
        overflow: hidden; 
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# Sidebar navigation
# -------------------------------
st.sidebar.header("📂 Navigation")
page = st.sidebar.radio("Go to", ["Home", "Screening", "Dashboard", "Chatbot (Recruiter Assistant)"])

# Utility: fuzzy filename match
def fuzzy_pick_filename(query: str, files: List[str]) -> Tuple[str, float]:
    if not files or not query:
        return "", 0.0
    if rf_process:
        match, score, _ = rf_process.extractOne(query, files)
        return str(match), float(score) / 100.0
    query = query.lower().strip()
    for f in files:
        if query and query in f.lower():
            return f, 1.0
    return "", 0.0

# ==========================================================
# 0) HOME PAGE
# ==========================================================
if page == "Home":
    st.markdown(
        """
        <div class="hero">
            <h1>🤖 AI-Powered Resume Screening System</h1>
            <h3>Using NLP & Machine Learning</h3>
            <p>Automated, smart, and fair recruitment — faster screening, skill-gap analysis, dashboards, and a recruiter chatbot.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🔹 What this tool does")
        st.markdown(
            """
            - Extracts skills & soft skills from PDF/DOCX resumes  
            - Compares resumes with Job Descriptions using embeddings  
            - Ranks candidates with matched vs missing skills  
            - Detects duplicates automatically  
            - Provides recruiter chatbot for instant Q&A
            """
        )

        st.markdown("###  Quick Start")
        st.markdown(
            """
            1. Go to **Screening** → Enter Job Description → Upload resumes → Click **Run Screening**  
            2. Open **Dashboard** → See visual insights  
            3. Use **Chatbot** → Ask queries like *top 3 resumes* or *missing skills for X*
            """
        )
    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h4 style="margin:0">✨ Key Features</h4>
                <ul style="margin-top:8px">
                    <li>PDF/DOCX parsing</li>
                    <li>Explainable matching</li>
                    <li>Duplicate detection</li>
                    <li>Visual dashboards</li>
                    <li>Recruiter chatbot</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================================
# 1) SCREENING
# ==========================================================
elif page == "Screening":
    st.header("📂 Screening — Job Description & Upload Resumes")

    jd_text = st.text_area("Job Description", height=180, placeholder="E.g., Looking for Python Developer with SQL & ML experience.")
    files = st.file_uploader("Upload resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True)
    run = st.button("▶ Run Screening")

    if run:
        # --- Validation ---
        if not jd_text:
            st.error("⚠️ Please enter a Job Description before running screening.")
        elif not files:
            st.error("⚠️ Please upload at least one resume.")
        else:
            # --- Continue with screening ---
            skills_master = load_skills()
            jd_clean = basic_clean(jd_text)
            jd_vec = embed_text(jd_clean)
            jd_sk = set([s for cat in skills_master.values() for s in cat if s.lower() in jd_clean.lower()])

            rows, seen_texts = [], []
            for f in files:
                tmp_path = Path(f"tmp_{uuid4().hex}_{f.name}")
                with open(tmp_path, "wb") as out:
                    out.write(f.read())
                try:
                    raw = extract_text(str(tmp_path))
                finally:
                    tmp_path.unlink(missing_ok=True)

                txt = basic_clean(raw)
                if any(is_duplicate(txt, seen) for seen in seen_texts):
                    continue
                seen_texts.append(txt)

                vec = embed_text(txt)
                score = score_resume(vec, jd_vec)
                cand_sk = extract_skills(txt, skills_master)
                matched, missing = explain_match(cand_sk, jd_sk)
                softs = list(extract_soft_skills(txt))

                rows.append({
                    "file": f.name,
                    "score": round(score, 4),
                    "matched_skills": ", ".join(sorted(matched)),
                    "missing_skills": ", ".join(sorted(missing)),
                    "soft_skills": ", ".join(sorted(softs))
                })

            if not rows:
                st.warning("⚠ No valid resumes processed.")
            else:
                df = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
                st.session_state["results_df"] = df

                top_row = df.iloc[0]
                st.success(f"🏆 Top Match: **{top_row['file']}** — Score {top_row['score']:.2f}")

                st.dataframe(df, use_container_width=True)
                st.download_button("⬇ Download Results (CSV)", df.to_csv(index=False).encode("utf-8"), "results.csv", "text/csv")

                st.markdown("---")
                st.subheader("📌 Shortlist Candidates")
                threshold = st.slider("Minimum score", 0.0, 1.0, 0.50, 0.01)
                shortlisted = df[df["score"] >= threshold].reset_index(drop=True)
                st.write(f"{len(shortlisted)} candidate(s) shortlisted")
                st.dataframe(shortlisted, use_container_width=True)
                st.download_button("⬇ Download Shortlist", shortlisted.to_csv(index=False).encode("utf-8"), "shortlist.csv", "text/csv")

# ==========================================================
# 2) DASHBOARD
# ==========================================================
elif page == "Dashboard":
    st.header("📊 Dashboard — Visual Insights")
    if "results_df" not in st.session_state:
        st.warning("⚠ Run screening first.")
    else:
        df = st.session_state["results_df"]

        st.dataframe(df, use_container_width=True, height=220)

        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(5,3))
            ax.barh(df["file"], df["score"])
            ax.set_xlabel("Score"); ax.set_ylabel("Resume"); ax.invert_yaxis()
            st.pyplot(fig)
        with col2:
            total_matched = sum(df["matched_skills"].apply(lambda x: len(x.split(", ")) if x else 0))
            total_missing = sum(df["missing_skills"].apply(lambda x: len(x.split(", ")) if x else 0))
            fig2, ax2 = plt.subplots(figsize=(4,3))
            ax2.pie([max(total_matched,0.001), max(total_missing,0.001)], labels=["Matched","Missing"], autopct="%1.1f%%")
            st.pyplot(fig2)

        st.write("### 🧠 Soft Skills Distribution")
        all_soft = []
        for s in df["soft_skills"]:
            if isinstance(s,str) and s.strip():
                all_soft.extend(s.split(", "))
        if all_soft:
            counts = pd.Series(all_soft).value_counts()
            fig3, ax3 = plt.subplots(figsize=(6,3))
            ax3.bar(counts.index, counts.values)
            plt.xticks(rotation=30, ha="right")
            st.pyplot(fig3)
        else:
            st.info("No soft skills detected.")

# ==========================================================
# 3) CHATBOT
# ==========================================================
elif page == "Chatbot (Recruiter Assistant)":
    st.header("💬 Recruiter Assistant Chatbot")
    if "results_df" not in st.session_state:
        st.info("⚠ Run screening first.")
    else:
        df = st.session_state["results_df"].copy()
        files = df["file"].tolist()

        q = st.text_input("Ask your question (e.g., top 3 resumes, score of resume1.pdf)")
        ask = st.button("Get Answer")

        def answer_query(q: str) -> str:
            ql = q.lower().strip()
            import re
            m_num = re.search(r"top\s*(\d+)", ql)
            if "top" in ql or "best" in ql:
                n = int(m_num.group(1)) if m_num else 3
                top_df = df.nlargest(n, "score")[["file", "score"]]
                return "🏆 Top Matches:\n" + "\n".join([f"{r.file} — {r.score:.3f}" for r in top_df.itertuples()])

            cand_file, conf = fuzzy_pick_filename(ql, files)
            if cand_file and conf >= 0.5:
                row = df[df["file"] == cand_file].iloc[0]
                if "score" in ql: return f"📊 {cand_file}: {row['score']:.3f}"
                if "missing" in ql: return f"❌ Missing Skills: {row['missing_skills'] or '(none)'}"
                if "matched" in ql: return f"✅ Matched Skills: {row['matched_skills'] or '(none)'}"
                if "soft" in ql: return f"🧠 Soft Skills: {row['soft_skills'] or '(none)'}"
                return f"{cand_file}: Score={row['score']:.3f}, Matched={row['matched_skills']}, Missing={row['missing_skills']}, Soft={row['soft_skills']}"
            return "⚡ Try asking: *score of resume1.pdf*, *missing skills for candidateX*, *top 3 resumes*"

        if ask and q.strip():
            st.info(answer_query(q))
