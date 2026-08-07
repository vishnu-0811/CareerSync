import streamlit as st
from html import escape
from pathlib import Path

from sidebar_ui import APP_NAME, brand_logo_html, init_app_layout, render_app_footer

st.set_page_config(page_title=APP_NAME, layout="wide", initial_sidebar_state="expanded")

# Shared layout chrome (sidebar)
init_app_layout("home")

# Page-specific styles (visual only)
_home_css_path = Path(__file__).resolve().parent / "pages" / "home.css"
if _home_css_path.exists():
    st.markdown(
        f"<style>{_home_css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )


# --- UI (presentation only) ---

st.markdown('<div class="pg-home">', unsafe_allow_html=True)

# Hero Section
st.markdown(
    f"""
    <section class="pg-home-hero" aria-labelledby="home-title">
      <div class="pg-home-hero-decor" aria-hidden="true">
        <div class="pg-home-hero-glow pg-home-hero-glow--left"></div>
        <div class="pg-home-hero-glow pg-home-hero-glow--right"></div>
        <div class="pg-home-hero-grid-pattern"></div>
      </div>
      <div class="pg-home-hero-grid">
        <div class="pg-home-hero-content">
          <div class="pg-home-hero-badge">
            <span class="pg-home-hero-badge-dot" aria-hidden="true"></span>
            AI-Powered Career Intelligence
          </div>
          <h1 id="home-title" class="pg-home-hero-title">
            Discover Your <span class="pg-home-hero-gradient">Ideal Career</span> with AI
          </h1>
          <p class="pg-home-hero-desc">
            Analyze resumes, evaluate job compatibility, identify skill gaps, and receive
            personalized career recommendations powered by {escape(APP_NAME)}.
          </p>
          <ul class="pg-home-hero-features" aria-label="Platform features">
            <li class="pg-home-hero-feature">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
                <path d="M20 6L9 17l-5-5"/>
              </svg>
              Resume Analysis
            </li>
            <li class="pg-home-hero-feature">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
                <path d="M20 6L9 17l-5-5"/>
              </svg>
              Job Match
            </li>
            <li class="pg-home-hero-feature">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
                <path d="M20 6L9 17l-5-5"/>
              </svg>
              Skill Gap Detection
            </li>
            <li class="pg-home-hero-feature">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
                <path d="M20 6L9 17l-5-5"/>
              </svg>
              Career Insights
            </li>
          </ul>
          <div class="pg-home-hero-actions">
            <a class="pg-btn pg-btn-primary pg-home-hero-cta" href="/1_Resume_Classifier" target="_self">
              Analyze Resume
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M5 12h14"/><path d="M13 6l6 6-6 6"/>
              </svg>
            </a>
            <a class="pg-btn pg-btn-outline pg-home-hero-cta" href="#capabilities-title">
              Explore Features
            </a>
          </div>
        </div>
        <div class="pg-home-hero-visual" aria-hidden="true">
          <div class="pg-home-ai-card">
            <header class="pg-home-ai-card-head">
              <div class="pg-home-ai-card-brand">
                <span class="pg-home-ai-card-icon">
                  {brand_logo_html("pg-home-ai-card-logo")}
                </span>
                <div>
                  <strong>{escape(APP_NAME)} AI</strong>
                  <span class="pg-home-ai-card-status">
                    <span class="pg-home-ai-card-pulse"></span>
                    Analyzing resume…
                  </span>
                </div>
              </div>
            </header>
            <div class="pg-home-ai-progress" role="progressbar" aria-valuenow="78" aria-valuemin="0" aria-valuemax="100">
              <span class="pg-home-ai-progress-bar"></span>
            </div>
            <div class="pg-home-ai-skeleton">
              <span></span><span></span><span></span>
            </div>
            <div class="pg-home-ai-tags">
              <span class="pg-home-ai-tag">Python</span>
              <span class="pg-home-ai-tag">Machine Learning</span>
              <span class="pg-home-ai-tag">React</span>
              <span class="pg-home-ai-tag">Data Science</span>
              <span class="pg-home-ai-tag">SQL</span>
            </div>
            <div class="pg-home-ai-stats">
              <div class="pg-home-ai-stat">
                <span class="pg-home-ai-stat-value pg-home-ai-stat-value--success">94%</span>
                <span class="pg-home-ai-stat-label">Resume Score</span>
              </div>
              <div class="pg-home-ai-stat">
                <span class="pg-home-ai-stat-value pg-home-ai-stat-value--primary">87%</span>
                <span class="pg-home-ai-stat-label">Job Match</span>
              </div>
              <div class="pg-home-ai-stat">
                <span class="pg-home-ai-stat-value pg-home-ai-stat-value--warning">3</span>
                <span class="pg-home-ai-stat-label">Skill Gaps</span>
              </div>
            </div>
          </div>
          <div class="pg-home-hero-float pg-home-hero-float--role">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
              <path d="M20 6L9 17l-5-5"/>
            </svg>
            Data Scientist
          </div>
          <div class="pg-home-hero-float pg-home-hero-float--confidence">97% confidence</div>
        </div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

# Stats Section
st.markdown(
    """
    <section class="pg-home-stats" aria-label="Platform statistics">
      <article class="pg-home-stat">
        <div class="pg-home-stat-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>
          </svg>
        </div>
        <span class="pg-home-stat-value">100+</span>
        <span class="pg-home-stat-label">Resumes Analyzed</span>
      </article>
      <article class="pg-home-stat">
        <div class="pg-home-stat-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
          </svg>
        </div>
        <span class="pg-home-stat-value">95%</span>
        <span class="pg-home-stat-label">Accuracy Rate</span>
      </article>
      <article class="pg-home-stat">
        <div class="pg-home-stat-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h10"/>
          </svg>
        </div>
        <span class="pg-home-stat-value">50+</span>
        <span class="pg-home-stat-label">Job Categories</span>
      </article>
      <article class="pg-home-stat">
        <div class="pg-home-stat-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>
          </svg>
        </div>
        <span class="pg-home-stat-value">24/7</span>
        <span class="pg-home-stat-label">AI Assistant</span>
      </article>
    </section>
    """,
    unsafe_allow_html=True,
)

# Features Section
st.markdown(
    """
    <section class="pg-home-capabilities" aria-labelledby="capabilities-title">
      <header class="pg-home-capabilities-head">
        <h2 id="capabilities-title" class="pg-home-capabilities-title">Capabilities</h2>
        <p class="pg-home-capabilities-lead">Your Career Toolkit</p>
        <p class="pg-home-capabilities-desc">
          Four AI tools in the sidebar — classify, match, cluster, and analyze your career data.
        </p>
      </header>
      <div class="pg-home-features-grid">
        <article class="pg-home-feature">
          <div class="pg-home-feature-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
            </svg>
          </div>
          <h3 class="pg-home-feature-title">Resume Classifier</h3>
          <p class="pg-home-feature-desc">
            Predict job roles from your resume using three ML models, with skill extraction and gap analysis.
          </p>
          <span class="pg-home-feature-nav">
            Sidebar
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            Resume Classifier
          </span>
        </article>
        <article class="pg-home-feature">
          <div class="pg-home-feature-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/>
              <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2"/>
            </svg>
          </div>
          <h3 class="pg-home-feature-title">Job Fit Analyzer</h3>
          <p class="pg-home-feature-desc">
            Compare your resume to any job description and get a clear compatibility score with fit insights.
          </p>
          <span class="pg-home-feature-nav">
            Sidebar
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            Job Fit Analyzer
          </span>
        </article>
        <article class="pg-home-feature">
          <div class="pg-home-feature-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M2 12h4M18 12h4M4.9 19.1l2.8-2.8M16.3 7.7l2.8-2.8"/>
            </svg>
          </div>
          <h3 class="pg-home-feature-title">Resume Cluster</h3>
          <p class="pg-home-feature-desc">
            Extract skills from your resume and find the top three career clusters that best match your profile.
          </p>
          <span class="pg-home-feature-nav">
            Sidebar
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            Resume Cluster
          </span>
        </article>
        <article class="pg-home-feature">
          <div class="pg-home-feature-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19V5M10 19V9M16 19V13M22 19V7"/>
            </svg>
          </div>
          <h3 class="pg-home-feature-title">Analytics Dashboard</h3>
          <p class="pg-home-feature-desc">
            Explore model accuracy, success rates, and performance charts to understand how CareerSync works.
          </p>
          <span class="pg-home-feature-nav">
            Sidebar
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            Dashboard
          </span>
        </article>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

# How it works section
st.markdown(
    """
    <section class="pg-home-workflow" aria-labelledby="workflow-title">
      <header class="pg-home-workflow-head">
        <span class="pg-home-section-eyebrow">Workflow</span>
        <h2 id="workflow-title" class="pg-home-section-title">How It Works</h2>
        <p class="pg-home-section-desc">From upload to actionable insights in four simple steps.</p>
      </header>
      <ol class="pg-home-workflow-track">
        <li class="pg-home-step">
          <span class="pg-home-step-num" aria-hidden="true">1</span>
          <div class="pg-home-step-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          <h3 class="pg-home-step-title">Upload</h3>
          <p>Upload your resume or paste job description</p>
        </li>
        <li class="pg-home-step">
          <span class="pg-home-step-num" aria-hidden="true">2</span>
          <div class="pg-home-step-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.3-4.3"/>
            </svg>
          </div>
          <h3 class="pg-home-step-title">Analyze</h3>
          <p>AI processes and analyzes your content</p>
        </li>
        <li class="pg-home-step">
          <span class="pg-home-step-num" aria-hidden="true">3</span>
          <div class="pg-home-step-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18h6M10 22h4M12 2a7 7 0 0 1 7 7c0 2.5-1.3 4.7-3.2 6L12 22l-3.8-7A7 7 0 0 1 12 2z"/>
            </svg>
          </div>
          <h3 class="pg-home-step-title">Insights</h3>
          <p>Get personalized recommendations</p>
        </li>
        <li class="pg-home-step">
          <span class="pg-home-step-num" aria-hidden="true">4</span>
          <div class="pg-home-step-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>
              <path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.4 22.4 0 0 1-4 2z"/>
            </svg>
          </div>
          <h3 class="pg-home-step-title">Succeed</h3>
          <p>Land your dream job with confidence</p>
        </li>
      </ol>
    </section>
    """,
    unsafe_allow_html=True,
)

# How CareerSync helps users
st.markdown(
    f"""
    <section class="pg-home-benefits" aria-labelledby="benefits-title">
      <header class="pg-home-benefits-head">
        <span class="pg-home-section-eyebrow">User value</span>
        <h2 id="benefits-title" class="pg-home-section-title">How {escape(APP_NAME)} Helps Users</h2>
        <p class="pg-home-section-desc">
          Smart tools that turn your resume and skills into clear, actionable career direction.
        </p>
      </header>
      <div class="pg-home-benefits-grid">
        <article class="pg-home-benefit">
          <div class="pg-home-benefit-icon" aria-hidden="true">🎯</div>
          <h3 class="pg-home-benefit-title">Personalized Job Recommendations</h3>
          <p class="pg-home-benefit-desc">
            {escape(APP_NAME)} analyzes your resume and skills to recommend job roles that closely match
            your qualifications and career goals.
          </p>
        </article>
        <article class="pg-home-benefit">
          <div class="pg-home-benefit-icon" aria-hidden="true">📄</div>
          <h3 class="pg-home-benefit-title">Intelligent Resume Analysis</h3>
          <p class="pg-home-benefit-desc">
            The system extracts key information from your resume using Natural Language Processing (NLP)
            to provide accurate career insights.
          </p>
        </article>
        <article class="pg-home-benefit">
          <div class="pg-home-benefit-icon" aria-hidden="true">📊</div>
          <h3 class="pg-home-benefit-title">Skill Gap Identification</h3>
          <p class="pg-home-benefit-desc">
            Identify missing or in-demand skills required for your desired job roles, helping you focus
            on the right areas for improvement.
          </p>
        </article>
        <article class="pg-home-benefit">
          <div class="pg-home-benefit-icon" aria-hidden="true">{brand_logo_html("pg-home-benefit-logo")}</div>
          <h3 class="pg-home-benefit-title">AI-Powered Career Guidance</h3>
          <p class="pg-home-benefit-desc">
            Machine Learning algorithms evaluate your profile and suggest suitable career paths based on
            your experience and technical skills.
          </p>
        </article>
        <article class="pg-home-benefit">
          <div class="pg-home-benefit-icon" aria-hidden="true">⚡</div>
          <h3 class="pg-home-benefit-title">Faster Job Search Process</h3>
          <p class="pg-home-benefit-desc">
            Reduce the time spent searching through irrelevant job listings by receiving targeted
            recommendations tailored to your profile.
          </p>
        </article>
        <article class="pg-home-benefit">
          <div class="pg-home-benefit-icon" aria-hidden="true">📈</div>
          <h3 class="pg-home-benefit-title">Data-Driven Decision Making</h3>
          <p class="pg-home-benefit-desc">
            Interactive dashboards and visualizations help users understand their strengths, skill
            distribution, and career opportunities.
          </p>
        </article>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

# Call to Action
st.markdown(
    f"""
    <section class="pg-home-cta" aria-labelledby="home-cta-title">
      <div class="pg-home-cta-inner">
        <span class="pg-home-cta-eyebrow">Next step</span>
        <div class="pg-home-cta-icon" aria-hidden="true">
          {brand_logo_html("pg-home-cta-logo")}
        </div>
        <h2 id="home-cta-title" class="pg-home-cta-title">Begin Your AI-Powered Career Journey</h2>
        <p class="pg-home-cta-lead">
          Upload your resume, discover suitable career opportunities, analyze your job compatibility,
          and gain personalized insights to advance your professional growth with
          <strong class="pg-home-cta-brand">{escape(APP_NAME)}</strong>.
        </p>
        <div class="pg-home-cta-hints" aria-label="Available tools">
          <span class="pg-home-cta-hint">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M9 18l6-6-6-6"/>
            </svg>
            Open the sidebar to get started
          </span>
          <span class="pg-home-cta-hint">Resume Classifier</span>
          <span class="pg-home-cta-hint">Job Fit Analyzer</span>
          <span class="pg-home-cta-hint">Resume Cluster</span>
          <span class="pg-home-cta-hint">Dashboard</span>
        </div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

# Start exploring tools
st.markdown(
    f"""
    <section class="pg-home-explore" aria-labelledby="home-explore-title">
      <div class="pg-home-explore-glow" aria-hidden="true"></div>
      <header class="pg-home-explore-head">
        <span class="pg-home-section-eyebrow">Get started</span>
        <h2 id="home-explore-title" class="pg-home-explore-title">
          <span class="pg-home-explore-emoji" aria-hidden="true">🚀</span>
          Start Exploring {escape(APP_NAME)}
        </h2>
        <p class="pg-home-explore-lead">
          Choose one of the intelligent tools below to begin your career analysis.
        </p>
      </header>
      <div class="pg-home-explore-grid">
        <article class="pg-home-explore-card">
          <div class="pg-home-explore-card-top">
            <div class="pg-home-explore-icon" aria-hidden="true">📄</div>
            <h3 class="pg-home-explore-card-title">Resume Classifier</h3>
          </div>
          <p class="pg-home-explore-card-desc">
            Classify your resume into suitable career domains using supervised Machine Learning
            algorithms.
          </p>
          <a class="pg-home-explore-cta" href="/1_Resume_Classifier" target="_self">
            <span>Launch Module</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M5 12h14"/><path d="M13 6l6 6-6 6"/>
            </svg>
          </a>
        </article>
        <article class="pg-home-explore-card">
          <div class="pg-home-explore-card-top">
            <div class="pg-home-explore-icon" aria-hidden="true">🎯</div>
            <h3 class="pg-home-explore-card-title">Job Fit Analyzer</h3>
          </div>
          <p class="pg-home-explore-card-desc">
            Compare your resume with a job description and receive a compatibility score along with
            skill gap analysis.
          </p>
          <a class="pg-home-explore-cta" href="/2_Job_Fit_Analyzer" target="_self">
            <span>Analyze Job Fit</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M5 12h14"/><path d="M13 6l6 6-6 6"/>
            </svg>
          </a>
        </article>
        <article class="pg-home-explore-card">
          <div class="pg-home-explore-card-top">
            <div class="pg-home-explore-icon" aria-hidden="true">📊</div>
            <h3 class="pg-home-explore-card-title">Analytics Dashboard</h3>
          </div>
          <p class="pg-home-explore-card-desc">
            Explore interactive charts, recommendation insights, and prediction results.
          </p>
          <a class="pg-home-explore-cta" href="/4_Dashboard" target="_self">
            <span>View Dashboard</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M5 12h14"/><path d="M13 6l6 6-6 6"/>
            </svg>
          </a>
        </article>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

render_app_footer()
