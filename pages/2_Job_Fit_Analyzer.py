import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from html import escape

from sidebar_ui import init_app_layout, render_app_footer

st.set_page_config("CareerSync - Job Fit Analyzer", layout="wide")
init_app_layout("job_fit")

import fitz  # PyMuPDF
import spacy
from spacy.matcher import PhraseMatcher
import numpy as np
import joblib
import pandas as pd
import re

from utils import comma_tokenizer  # noqa: F401 — required for vectorizer unpickle

# Page-specific styles (visual only — reuses classifier feature-page shell)
_pages_dir = Path(__file__).resolve().parent
_css_parts = []
for _css_name in ("classifier.css", "job_fit.css"):
    _css_path = _pages_dir / _css_name
    if _css_path.exists():
        _css_parts.append(_css_path.read_text(encoding="utf-8"))
if _css_parts:
    st.markdown(f"<style>{''.join(_css_parts)}</style>", unsafe_allow_html=True)

# Load immutable NLP/ML resources once. TensorFlow is imported lazily so the
# page shell and loading indicator render before its comparatively slow startup.
@st.cache_resource(show_spinner=False)
def load_runtime_resources():
    import tensorflow as tf

    model = tf.keras.models.load_model(
        _ROOT / "Neural_Networks" / "match_score_model.h5",
        compile=False,
    )
    model.compile(optimizer="adam", loss="mean_squared_error", metrics=["mae"])
    return (
        spacy.load("en_core_web_sm"),
        model,
        joblib.load(_ROOT / "Neural_Networks" / "match_vectorizer.pkl"),
    )


with st.spinner("Loading job-fit analysis model..."):
    nlp, match_model, match_vectorizer = load_runtime_resources()

# Load skill vocabulary and job roles
@st.cache_data
def load_skill_list():
    with open(
        _ROOT / "datasets" / "unique_skills.txt",
        "r",
        encoding="utf-8",
    ) as f:
        return [line.strip().lower() for line in f if line.strip()]


@st.cache_data
def load_role_skills():
    df = pd.read_csv(_ROOT / "datasets" / "job_skills_dataset_corrected.csv")
    role_map = {}
    for _, row in df.iterrows():
        title = row['Job Title'].strip().lower()
        skills = [s.strip().lower() for s in row['Skills Required'].split(',')]
        role_map.setdefault(title, set()).update(skills)
    return role_map

skill_vocab = load_skill_list()
role_skill_map = load_role_skills()

# Skill extractor
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = "".join([page.get_text() for page in doc])
    doc.close()
    return text.lower()

def extract_skills(text, skill_list):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in skill_list]
    matcher.add("SKILLS", patterns)
    doc = nlp(text)
    matches = matcher(doc)
    return sorted({doc[start:end].text.lower() for _, start, end in matches})

def extract_experience_from_text(text):
    """
    Extracts years of experience from a job description using regex.
    Returns the first found integer (years), or None if not found.
    """
    # Common patterns: "X years", "X+ years", "at least X years", "minimum X years"
    patterns = [
        r'(\d+)\s*\+\s*years',
        r'at least\s+(\d+)\s*years',
        r'minimum\s+of\s+(\d+)\s*years',
        r'minimum\s+(\d+)\s*years',
        r'(\d+)\s*years'
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


# --- Presentation helpers (visual only) ---

_EXP_ALERT_ICONS = {
    "success": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
        '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>'
    ),
    "warning": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
        '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
        '<path d="M12 9v4M12 17h.01"/></svg>'
    ),
    "info": (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
        '<circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16h.01"/></svg>'
    ),
}


def _exp_alert_html(message, variant):
    icon = _EXP_ALERT_ICONS.get(variant, _EXP_ALERT_ICONS["info"])
    return (
        f'<div class="pg-jf-exp-alert {variant}" role="status">'
        f"{icon}<span>{escape(message)}</span></div>"
    )


# --- UI (presentation only) ---

st.markdown('<div class="pg-classifier pg-jobfit">', unsafe_allow_html=True)

st.markdown(
    """
    <section class="pg-cl-hero" aria-labelledby="jf-title">
      <div class="pg-cl-hero-main">
        <div class="pg-cl-eyebrow">Neural Network</div>
        <h2 id="jf-title" class="pg-cl-title">Job Fit Analyzer</h2>
        <p class="pg-cl-subtitle">
          Compare your resume against a job description and target role. Get skill overlap metrics,
          experience alignment feedback, and an overall profile fit score powered by a feedforward ANN.
        </p>
      </div>
      <div class="pg-cl-hero-meta">
        <span class="pg-cl-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M12 2a7 7 0 0 1 7 7c0 2.5-1.3 4.7-3.2 6L12 22l-3.8-7A7 7 0 0 1 12 2z"/>
          </svg>
          JD matching
        </span>
        <span class="pg-cl-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
          TensorFlow ANN
        </span>
        <span class="pg-cl-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>
          </svg>
          Experience factor
        </span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True, key="jobfit_form"):
    st.markdown(
        """
        <div class="pg-cl-form-intro" role="region" aria-label="Job fit analyzer form">
          <h3 class="pg-cl-form-intro-title">Analyze job fit</h3>
          <p class="pg-cl-form-intro-hint">
            Upload your resume, select a target role, paste the job description, and enter your years of experience.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    job_title = st.selectbox("Target Job Role", sorted(role_skill_map.keys()))
    job_desc = st.text_area("Paste Job Description")
    top_skills = st.multiselect(
        "Highlight Top Skills",
        options=sorted(skill_vocab),
    )
    experience = st.number_input(
        "Years of Experience",
        min_value=0,
        max_value=50,
        value=0,
    )
    analyze_clicked = st.button("Analyze Fit", type="primary")


if analyze_clicked:
    if not uploaded_file or not job_desc:
        st.warning("Please upload resume and enter job description.")
    else:
        text = extract_text_from_pdf(uploaded_file)
        resume_skills = extract_skills(text, skill_vocab)
        jd_skills = extract_skills(job_desc.lower(), skill_vocab)
        role_skills = role_skill_map.get(job_title.lower(), set())

        resume_str = ", ".join(resume_skills + top_skills + top_skills)
        jd_str = ", ".join(jd_skills)
        role_str = ", ".join(role_skills)

        # Experience matching logic
        required_exp = extract_experience_from_text(job_desc)
        if required_exp is not None:
            # Give more weight if candidate meets or exceeds required experience
            if experience >= required_exp:
                exp_weight = 1.0
                exp_feedback = f"✅ Your experience ({experience} yrs) meets or exceeds the job's requirement ({required_exp} yrs)."
            else:
                exp_weight = experience / required_exp  # 0.0–1.0
                exp_feedback = f"⚠️ Job requires {required_exp} yrs, you have {experience} yrs."
        else:
            exp_weight = experience / 10  # fallback, scale to 0–1
            exp_feedback = "ℹ️ No explicit experience requirement found in job description."

        # Prepare input for model, using weighted experience
        vec_resume = match_vectorizer.transform([resume_str]).toarray()[0]
        vec_jd = match_vectorizer.transform([jd_str]).toarray()[0]
        vec_role = match_vectorizer.transform([role_str]).toarray()[0]
        final_input = np.concatenate([vec_resume, vec_jd, vec_role, [exp_weight]])
        score = match_model.predict(np.array([final_input]))[0][0]

        # Display values (same formulas as before)
        jd_match_display = (
            f"{len(set(resume_skills) & set(jd_skills)) / len(jd_skills) * 100:.1f}%"
            if jd_skills else "No JD skills found."
        )
        role_match_display = (
            f"{len(set(resume_skills) & set(role_skills)) / len(role_skills) * 100:.1f}%"
            if role_skills else "No role skills found."
        )
        score_pct = score * 100
        progress_value = float(score) if 0.0 <= score <= 1.0 else float(score) / 100

        if exp_feedback.startswith("✅"):
            exp_variant = "success"
        elif exp_feedback.startswith("⚠️"):
            exp_variant = "warning"
        else:
            exp_variant = "info"

        jd_is_pct = bool(jd_skills)
        role_is_pct = bool(role_skills)

        st.markdown('<div class="pg-jf-results">', unsafe_allow_html=True)

        st.markdown(
            f"""
            <section class="pg-cl-section" aria-labelledby="jf-results-title">
              <div class="pg-cl-section-header">
                <div class="pg-cl-section-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 19V5M10 19V9M16 19V13M22 19V7"/>
                  </svg>
                </div>
                <div>
                  <h3 id="jf-results-title" class="pg-cl-section-title">Results</h3>
                  <p class="pg-cl-section-desc">Skill overlap and experience alignment for {escape(job_title)}.</p>
                </div>
              </div>
              <div class="pg-jf-metrics">
                <article class="pg-jf-metric">
                  <div class="pg-jf-metric-head">
                    <div class="pg-jf-metric-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <path d="M14 2v6h6"/>
                      </svg>
                    </div>
                    <span class="pg-jf-metric-label">JD Skill Match</span>
                  </div>
                  <div class="pg-jf-metric-value{" text" if not jd_is_pct else ""}">{escape(jd_match_display)}</div>
                  <p class="pg-jf-metric-caption">Resume vs job description skills</p>
                </article>
                <article class="pg-jf-metric">
                  <div class="pg-jf-metric-head">
                    <div class="pg-jf-metric-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2a7 7 0 0 1 7 7c0 2.5-1.3 4.7-3.2 6L12 22l-3.8-7A7 7 0 0 1 12 2z"/>
                      </svg>
                    </div>
                    <span class="pg-jf-metric-label">Role Skill Match</span>
                  </div>
                  <div class="pg-jf-metric-value{" text" if not role_is_pct else ""}">{escape(role_match_display)}</div>
                  <p class="pg-jf-metric-caption">Resume vs target role skills</p>
                </article>
                <article class="pg-jf-metric">
                  <div class="pg-jf-metric-head">
                    <div class="pg-jf-metric-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>
                      </svg>
                    </div>
                    <span class="pg-jf-metric-label">Experience Factor</span>
                  </div>
                  <div class="pg-jf-metric-value">{experience} <span class="pg-type-kpi-unit">yrs</span></div>
                  <p class="pg-jf-metric-caption">Your declared experience</p>
                </article>
              </div>
              {_exp_alert_html(exp_feedback, exp_variant)}
            </section>
            """,
            unsafe_allow_html=True,
        )

        clamped = max(0.0, min(1.0, float(progress_value)))
        st.markdown(
            f"""
            <section class="pg-jf-score-panel" aria-labelledby="jf-score-title">
              <div class="pg-jf-score-header">
                <div>
                  <h3 id="jf-score-title" class="pg-jf-score-title">Overall Profile Fit Score</h3>
                  <p class="pg-jf-score-desc">Neural network compatibility score across resume, JD, role, and experience.</p>
                </div>
                <div class="pg-jf-score-value" aria-label="Overall fit score">{score_pct:.2f}<span>%</span></div>
              </div>
              <div class="pg-jf-progress-wrap">
                <div class="pg-jf-progress-label">
                  <span>Fit level</span>
                  <span>{score_pct:.1f}%</span>
                </div>
                <div class="progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{score_pct:.1f}">
                  <div class="progress-fill" style="width: {clamped * 100:.2f}%;"></div>
                </div>
              </div>
            </section>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)

render_app_footer()
