import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from html import escape

from sidebar_ui import init_app_layout, render_app_footer
from ui_html import render_html

st.set_page_config("CareerSync - Smart Resume Classifier", layout="wide")
init_app_layout("classifier")

import fitz  # PyMuPDF
import joblib
import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher

from utils import comma_tokenizer  # noqa: F401 — required for TF-IDF unpickle

# Page-specific styles (visual only)
_classifier_css_path = Path(__file__).resolve().parent / "classifier.css"
if _classifier_css_path.exists():
    st.markdown(
        f"<style>{_classifier_css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

# Load immutable NLP/ML resources once and show progress on first load.
@st.cache_resource(show_spinner=False)
def load_runtime_resources():
    return (
        spacy.load("en_core_web_sm"),
        joblib.load(_ROOT / "Supervised" / "tfidf_vectorizer.pkl"),
        joblib.load(_ROOT / "Supervised" / "label_encoder.pkl"),
        joblib.load(_ROOT / "Supervised" / "logistic_regression_model.pkl"),
        joblib.load(_ROOT / "Supervised" / "random_forest_model.pkl"),
        joblib.load(_ROOT / "Supervised" / "svm_model.pkl"),
    )


with st.spinner("Loading resume classification models..."):
    nlp, vectorizer, label_encoder, lr_model, rf_model, svm_model = (
        load_runtime_resources()
    )

# Load skill vocabulary
def load_skill_list(file=_ROOT / "datasets" / "unique_skills.txt"):
    with open(file, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

skill_vocab = load_skill_list()

# Load dataset for calculating role-specific required skills
@st.cache_data
def load_dataset():
    df = pd.read_csv(_ROOT / "datasets" / "job_skills_dataset_corrected.csv")
    role_skills = {}
    for _, row in df.iterrows():
        title = row['Job Title'].strip().lower()
        skills = [s.strip().lower() for s in row['Skills Required'].split(',')]
        role_skills.setdefault(title, set()).update(skills)
    return role_skills

role_skill_map = load_dataset()


@st.cache_data
def load_resources():
    return pd.read_csv(_ROOT / "datasets" / "learning_resources_dataset.csv")

# Extract text from PDF using fitz
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.lower()

# Extract skills using spaCy PhraseMatcher
def extract_skills(text, skill_list):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in skill_list]
    matcher.add("SKILLS", patterns)
    doc = nlp(text)
    matches = matcher(doc)
    return sorted({doc[start:end].text.lower() for _, start, end in matches})

# Predict with weighted skills
def predict_with_models(parsed_skills, top_skills):
    final_skills = parsed_skills + top_skills + top_skills  # weight top skills
    text_input = ', '.join(final_skills)
    vec = vectorizer.transform([text_input])
    predictions = {
        "Logistic Regression": label_encoder.inverse_transform(lr_model.predict(vec))[0],
        "Random Forest": label_encoder.inverse_transform(rf_model.predict(vec))[0],
        "SVM": label_encoder.inverse_transform(svm_model.predict(vec))[0],
    }
    return predictions, text_input

# Match % between candidate skills and role skills
def match_score(candidate_skills, job_title):
    required = role_skill_map.get(job_title.lower())
    if not required:
        return "N/A"
    overlap = len(set(candidate_skills) & required)
    return f"{(overlap / len(required)) * 100:.1f}%" if required else "0%"


# --- Presentation helpers (visual only) ---

def _pills_html(skills, variant=""):
    if not skills:
        return ""
    variant_class = f" {variant}" if variant else ""
    return "".join(
        f'<span class="pg-cl-pill{variant_class}">{escape(skill)}</span>'
        for skill in skills
    )


def _themed_pills_html(skills, theme: str) -> str:
    """Skill chips styled for upskill column theme (presentation only)."""
    if not skills:
        return ""
    return "".join(
        f'<span class="pg-cl-pill pg-cl-pill--{theme}">{escape(skill)}</span>'
        for skill in skills
    )


def _skill_col_html(
    *,
    theme: str,
    title: str,
    badge: str,
    icon_svg: str,
    pills_html: str,
    empty_html: str,
) -> str:
    body = (
        f'<div class="pg-cl-pills pg-cl-pills--{theme}">{pills_html}</div>'
        if pills_html
        else empty_html
    )
    return (
        f'<article class="pg-cl-skill-col pg-cl-skill-col--{theme}">'
        f'<header class="pg-cl-skill-col-head">'
        f'<span class="pg-cl-skill-col-icon" aria-hidden="true">{icon_svg}</span>'
        f'<div class="pg-cl-skill-col-copy">'
        f'<h4 class="pg-cl-skill-col-title">{escape(title)}</h4>'
        f'<span class="pg-cl-skill-col-badge pg-cl-skill-col-badge--{theme}">{escape(badge)}</span>'
        f"</div></header>{body}</article>"
    )


def _parse_learning_resource(resource: str) -> tuple[str, str]:
    """Split existing resource label into platform and title (UI parsing only)."""
    if ": " in resource:
        platform, title = resource.split(": ", 1)
        return platform.strip(), title.strip()
    return "Online Learning", resource.strip()


def _course_ui_labels(resource: str, skill: str) -> tuple[str, str, str]:
    """Derive display labels from existing resource text — no data changes."""
    lower = resource.lower()
    if "beginner" in lower or "crash course" in lower:
        difficulty = "Beginner"
    elif "advanced" in lower or "professional certificate" in lower:
        difficulty = "Advanced"
    else:
        difficulty = "Intermediate"
    if "crash course" in lower:
        duration = "4–6 hrs"
    elif "specialization" in lower or "certificate" in lower:
        duration = "4–8 weeks"
    elif "masterclass" in lower:
        duration = "10–15 hrs"
    else:
        duration = "6–10 hrs"
    description = f"Build practical {escape(skill)} skills aligned with your target role through this curated learning path."
    return difficulty, duration, description


def _platform_slug(platform: str) -> str:
    return platform.lower().replace("linkedin learning", "linkedin").replace(" ", "-")


def _platform_initials(platform: str) -> str:
    slug = _platform_slug(platform)
    mapping = {
        "coursera": "C",
        "edx": "eX",
        "udemy": "U",
        "linkedin": "in",
    }
    return mapping.get(slug, platform[:2].upper())


def _course_card_html(skill: str, resource: str) -> str:
    platform, course_title = _parse_learning_resource(str(resource))
    difficulty, duration, description = _course_ui_labels(str(resource), str(skill))
    slug = _platform_slug(platform)
    return (
        '<article class="pg-cl-course-card">'
        '<div class="pg-cl-course-head">'
        f'<span class="pg-cl-course-logo pg-cl-course-logo--{escape(slug)}" aria-hidden="true">'
        f"{escape(_platform_initials(platform))}</span>"
        '<div class="pg-cl-course-head-copy">'
        f'<span class="pg-cl-course-platform">{escape(platform)}</span>'
        f'<span class="pg-cl-course-difficulty pg-cl-course-difficulty--{escape(difficulty.lower())}">'
        f"{escape(difficulty)}</span>"
        "</div></div>"
        f'<h5 class="pg-cl-course-title">{escape(course_title)}</h5>'
        f'<p class="pg-cl-course-desc">{description}</p>'
        f'<div class="pg-cl-course-tags"><span class="pg-cl-course-tag">{escape(str(skill))}</span></div>'
        '<footer class="pg-cl-course-foot">'
        f'<span class="pg-cl-course-duration">'
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
        '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'
        f"{escape(duration)}</span>"
        '<div class="pg-cl-course-actions">'
        f'<a class="pg-cl-course-btn" href="#" aria-label="View course for {escape(str(skill))}">View Course</a>'
        f'<a class="pg-cl-course-link" href="#" aria-label="Learn more about {escape(course_title)}">Learn More</a>'
        "</div></footer></article>"
    )


_SKILL_ICON_REQUIRED = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<path d="M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z"/></svg>'
)
_SKILL_ICON_HAVE = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">'
    '<path d="M20 6L9 17l-5-5"/></svg>'
)
_SKILL_ICON_MISSING = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
    '<line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
)


def _model_icon_svg():
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'aria-hidden="true"><path d="M12 2L2 7l10 5 10-5-10-5z"/>'
        '<path d="M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>'
    )


def _pred_card_html(model: str, role: str, score: str) -> str:
    """Compact HTML for one prediction card (no leading indent — avoids markdown code blocks)."""
    return (
        '<article class="pg-cl-pred-card">'
        f'<div class="pg-cl-pred-model">{_model_icon_svg()} {escape(model)}</div>'
        f'<p class="pg-cl-pred-role">{escape(role)}</p>'
        f'<span class="pg-cl-pred-score">Match {escape(score)}</span>'
        '</article>'
    )


# --- UI (presentation only) ---

st.markdown('<div class="pg-classifier">', unsafe_allow_html=True)

st.markdown(
    """
    <section class="pg-cl-hero" aria-labelledby="cl-title">
      <div class="pg-cl-hero-main">
        <div class="pg-cl-eyebrow">Supervised ML</div>
        <h2 id="cl-title" class="pg-cl-title">Smart Resume Classifier</h2>
        <p class="pg-cl-subtitle">
          Upload your resume, highlight your strongest skills, and get job role predictions
          from three classifiers — plus targeted upskilling recommendations when you choose a target role.
        </p>
      </div>
      <div class="pg-cl-hero-meta">
        <span class="pg-cl-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
          </svg>
          PDF parsing
        </span>
        <span class="pg-cl-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M4 19V5M10 19V9M16 19V13M22 19V7"/>
          </svg>
          3 models
        </span>
        <span class="pg-cl-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/>
          </svg>
          Skill gaps
        </span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True, key="classifier_form"):
    st.markdown(
        """
        <div class="pg-cl-form-intro" role="region" aria-label="Resume classifier form">
          <h3 class="pg-cl-form-intro-title">Analyze your resume</h3>
          <p class="pg-cl-form-intro-hint">
            Upload a PDF, optionally boost key skills, and run prediction. Select a target role to unlock upskilling suggestions.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    top_skills = st.multiselect(
        "Highlight Your Top Skills (these get extra weight)",
        options=sorted(skill_vocab),
    )
    all_roles = sorted(set(role_skill_map.keys()))
    target_role = st.selectbox(
        "Your Target Job Role (optional)",
        options=["None"] + all_roles,
    )
    predict_clicked = st.button("Predict Job Role", type="primary")

if predict_clicked:
    if uploaded_file is None:
        st.warning("Please upload a resume.")
    else:
        text = extract_text_from_pdf(uploaded_file)
        parsed_skills = extract_skills(text, skill_vocab)

        if not parsed_skills:
            st.error("No matching skills found in resume.")
        else:
            st.markdown('<div class="pg-cl-results">', unsafe_allow_html=True)

            preds, used_text = predict_with_models(parsed_skills, top_skills)

            # Extracted skills
            st.markdown(
                f"""
                <section class="pg-cl-section" aria-labelledby="cl-skills-title">
                  <div class="pg-cl-section-header">
                    <div class="pg-cl-section-icon success" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                      </svg>
                    </div>
                    <div>
                      <h3 id="cl-skills-title" class="pg-cl-section-title">Extracted Skills from Resume</h3>
                      <p class="pg-cl-section-desc">Skills identified via NLP phrase matching against our vocabulary.</p>
                    </div>
                  </div>
                  <div class="pg-cl-pills">{_pills_html(parsed_skills, "success")}</div>
                  <p class="pg-cl-pill-count">{len(parsed_skills)} skill{"s" if len(parsed_skills) != 1 else ""} detected</p>
                </section>
                """,
                unsafe_allow_html=True,
            )

            # Predictions
            pred_cards_html = "".join(
                _pred_card_html(model, role, match_score(parsed_skills + top_skills, role))
                for model, role in preds.items()
            )

            render_html(
                f"""
                <section class="pg-cl-section" aria-labelledby="cl-pred-title">
                  <div class="pg-cl-section-header">
                    <div class="pg-cl-section-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2a7 7 0 0 1 7 7c0 2.5-1.3 4.7-3.2 6L12 22l-3.8-7A7 7 0 0 1 12 2z"/>
                        <circle cx="12" cy="9" r="2.5"/>
                      </svg>
                    </div>
                    <div>
                      <h3 id="cl-pred-title" class="pg-cl-section-title">Final Prediction with Weighted Top Skills</h3>
                      <p class="pg-cl-section-desc">Role predictions from Logistic Regression, Random Forest, and SVM.</p>
                    </div>
                  </div>
                  <div class="pg-cl-predictions">{pred_cards_html}</div>
                </section>
                """
            )

            if target_role != "None":
                required = role_skill_map.get(target_role.lower(), set())
                current = set(parsed_skills + top_skills)
                missing = required - current
                have = current & required

                required_list = sorted(required)
                have_list = sorted(have)
                missing_list = sorted(missing)

                skill_grids_html = (
                    '<div class="pg-cl-skill-grids">'
                    + _skill_col_html(
                        theme="required",
                        title="Required Skills",
                        badge=f"{len(required_list)} skills for role",
                        icon_svg=_SKILL_ICON_REQUIRED,
                        pills_html=_themed_pills_html(required_list, "required"),
                        empty_html='<p class="pg-cl-skill-col-empty">No data.</p>',
                    )
                    + _skill_col_html(
                        theme="have",
                        title="You Already Have",
                        badge=f"{len(have_list)} matched",
                        icon_svg=_SKILL_ICON_HAVE,
                        pills_html=_themed_pills_html(have_list, "have"),
                        empty_html='<p class="pg-cl-skill-col-empty">None yet</p>',
                    )
                    + _skill_col_html(
                        theme="missing",
                        title="You Are Missing",
                        badge=f"{len(missing_list)} to learn",
                        icon_svg=_SKILL_ICON_MISSING,
                        pills_html=_themed_pills_html(missing_list, "missing"),
                        empty_html='<p class="pg-cl-skill-col-empty">You\'re all set!</p>',
                    )
                    + "</div>"
                )

                res_df = load_resources()
                suggestions = res_df[res_df["Skill"].str.lower().isin(missing)]

                if not suggestions.empty:
                    course_cards_html = "".join(
                        _course_card_html(row["Skill"], row["Learning Resource"])
                        for _, row in suggestions.iterrows()
                    )
                    courses_block = (
                        '<div class="pg-cl-courses-section">'
                        '<header class="pg-cl-courses-head">'
                        '<h4 class="pg-cl-courses-title">Suggested Courses</h4>'
                        '<p class="pg-cl-courses-lead">Curated learning paths to close your skill gaps.</p>'
                        "</header>"
                        f'<div class="pg-cl-courses">{course_cards_html}</div>'
                        "</div>"
                    )
                else:
                    courses_block = (
                        '<div class="pg-cl-empty pg-cl-empty--upskill" role="status">'
                        '<p class="pg-cl-empty-title">No courses needed</p>'
                        '<p class="pg-cl-empty-text">No courses found or you\'re already skilled enough.</p>'
                        "</div>"
                    )

                render_html(
                    f"""
                    <section class="pg-cl-section pg-cl-section--upskill" aria-labelledby="cl-upskill-title">
                      <div class="pg-cl-section-header">
                        <div class="pg-cl-section-icon warning" aria-hidden="true">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                          </svg>
                        </div>
                        <div>
                          <h3 id="cl-upskill-title" class="pg-cl-section-title">Learn &amp; Upskill Recommendations</h3>
                          <p class="pg-cl-section-desc">Compare your profile against required skills for your target role.</p>
                        </div>
                      </div>
                      {skill_grids_html}
                      {courses_block}
                    </section>
                    """
                )

            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

render_app_footer()
