import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import tempfile
from html import escape

from sidebar_ui import init_app_layout, render_app_footer

st.set_page_config("CareerSync - Resume Cluster", layout="wide")
init_app_layout("cluster")

# Page-specific styles (visual only — reuses classifier feature-page shell)
_pages_dir = Path(__file__).resolve().parent
_css_parts = []
for _css_name in ("classifier.css", "cluster.css"):
    _css_path = _pages_dir / _css_name
    if _css_path.exists():
        _css_parts.append(_css_path.read_text(encoding="utf-8"))
if _css_parts:
    st.markdown(f"<style>{''.join(_css_parts)}</style>", unsafe_allow_html=True)

# These modules initialize spaCy and the clustering artifacts at import time.
# Import them after rendering the page shell so users see progress instead of
# an apparently blank page during first load.
with st.spinner("Loading resume clustering models..."):
    from resume_parser import parse_pdf_for_skills
    from Unsupervised.cluster_predictor import predict_resume_clusters


# --- Presentation helpers (visual only) ---

def _skills_pills_html(skills_csv):
    if not skills_csv:
        return ""
    skills = [s.strip() for s in str(skills_csv).split(",") if s.strip()]
    return "".join(
        f'<span class="pg-cl-pill success">{escape(skill)}</span>'
        for skill in skills
    )


def _cluster_cards_html(results):
    cards = []
    rank_labels = ("Best match", "2nd match", "3rd match")
    for index, (cluster_id, label, score) in enumerate(results):
        rank = index + 1
        rank_label = rank_labels[index] if index < len(rank_labels) else f"Rank {rank}"
        cards.append(
            f"""
            <article class="pg-rc-cluster-card rank-{rank}">
              <span class="pg-rc-cluster-rank">{escape(rank_label)}</span>
              <p class="pg-rc-cluster-id">Cluster {escape(str(cluster_id))}</p>
              <p class="pg-rc-cluster-label">{escape(str(label))}</p>
              <span class="pg-rc-cluster-score">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                  <path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/>
                </svg>
                Score {score:.3f}
              </span>
            </article>
            """
        )
    return "".join(cards)


# --- UI (presentation only) ---

st.markdown('<div class="pg-classifier pg-cluster">', unsafe_allow_html=True)

st.markdown(
    """
    <section class="pg-cl-hero" aria-labelledby="rc-title">
      <div class="pg-cl-hero-main">
        <div class="pg-cl-eyebrow">Unsupervised ML</div>
        <h2 id="rc-title" class="pg-cl-title">Resume Skill Cluster Predictor</h2>
        <p class="pg-cl-subtitle">
          Upload your resume PDF to extract skills and discover the top three job clusters
          that best match your profile using K-Means similarity scoring.
        </p>
      </div>
      <div class="pg-cl-hero-meta">
        <span class="pg-cl-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M2 12h4M18 12h4M4.9 19.1l2.8-2.8M16.3 7.7l2.8-2.8"/>
          </svg>
          K-Means
        </span>
        <span class="pg-cl-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          Top 3 clusters
        </span>
        <span class="pg-cl-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <path d="M14 2v6h6"/>
          </svg>
          Auto-analyze
        </span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True, key="cluster_form"):
    st.markdown(
        """
        <div class="pg-cl-form-intro" role="region" aria-label="Resume cluster upload">
          <h3 class="pg-cl-form-intro-title">Upload your resume</h3>
          <p class="pg-cl-form-intro-hint">
            Analysis begins automatically after upload — skills are extracted, then the top matching clusters are ranked.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Choose your resume PDF", type=["pdf"])

if uploaded_file is not None:
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.markdown(
        """
        <div class="pg-rc-results">
          <div class="pg-rc-upload-ok" role="status">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
            </svg>
            PDF uploaded successfully!
          </div>
        """,
        unsafe_allow_html=True,
    )

    # Extract skills and show them
    with st.spinner("Extracting skills..."):
        extracted_skills = parse_pdf_for_skills(tmp_path)

    if extracted_skills:
        pills = _skills_pills_html(extracted_skills)
        skill_count = len([s for s in str(extracted_skills).split(",") if s.strip()])
        st.markdown(
            f"""
            <section class="pg-cl-section" aria-labelledby="rc-skills-title">
              <div class="pg-cl-section-header">
                <div class="pg-cl-section-icon success" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  </svg>
                </div>
                <div>
                  <h3 id="rc-skills-title" class="pg-cl-section-title">Your Skills</h3>
                  <p class="pg-cl-section-desc">Skills extracted from your resume via NLP phrase matching.</p>
                </div>
              </div>
              <div class="pg-cl-pills">{pills}</div>
              <p class="pg-cl-pill-count">{skill_count} skill{"s" if skill_count != 1 else ""} detected</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("No recognizable skills found in the PDF.")

    # Predict clusters
    with st.spinner("Predicting clusters..."):
        results = predict_resume_clusters(tmp_path)

    if results:
        st.markdown(
            f"""
            <section class="pg-cl-section" aria-labelledby="rc-clusters-title">
              <div class="pg-cl-section-header">
                <div class="pg-cl-section-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                </div>
                <div>
                  <h3 id="rc-clusters-title" class="pg-cl-section-title">Top 3 Matching Clusters</h3>
                  <p class="pg-cl-section-desc">Ranked by cosine similarity to K-Means cluster centers.</p>
                </div>
              </div>
              <div class="pg-rc-clusters">{_cluster_cards_html(results)}</div>
            </section>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("No matching clusters found.")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

render_app_footer()
