"""Reusable CareerSync layout chrome (styles + sidebar).

Does not change routing, permissions, authentication, API calls,
or page business logic. Feature pages stay intact.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from functools import lru_cache
from html import escape
from pathlib import Path
from ui_html import render_html

# Ensure project root is importable when Streamlit runs pages/ scripts.
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

_PAGES_DIR = _ROOT / "pages"
_TOKENS_PATH = _PAGES_DIR / "design_tokens.css"
_TYPOGRAPHY_PATH = _PAGES_DIR / "typography.css"
_LAYOUT_PATH = _PAGES_DIR / "layout.css"
_COMPONENTS_PATH = _PAGES_DIR / "components.css"
_STYLES_PATH = _PAGES_DIR / "styles.css"

__all__ = [
    "APP_NAME",
    "APP_TAGLINE",
    "MAIN_PAGE_LABEL",
    "brand_logo_html",
    "apply_sidebar_styles",
    "init_app_layout",
    "inject_early_styles",
    "render_app_footer",
    "render_html",
    "render_sidebar_panels",
]

APP_NAME = "CareerSync"
APP_TAGLINE = "Where AI Meets Career Success"
MAIN_PAGE_LABEL = "Main"

_BRAND_LOGO_PATH = _ROOT / "static" / "careersync-logo.png"
_BRAND_LOGO_FALLBACK = _ROOT / "static" / "careersync-ai-logo.png"
_BRAND_LOGO_CANDIDATES = (_BRAND_LOGO_PATH, _BRAND_LOGO_FALLBACK)


@lru_cache(maxsize=8)
def brand_logo_html(css_class: str = "pg-brand-logo") -> str:
    """Inline the official CareerSync logo (shared asset, location-specific CSS class)."""
    logo_path = next((path for path in _BRAND_LOGO_CANDIDATES if path.is_file()), None)
    alt = f"{APP_NAME} logo"
    if logo_path is None:
        return (
            f'<img class="pg-brand-logo {css_class}" '
            f'alt="{escape(alt)}" decoding="async" />'
        )

    encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
    data_uri = f"data:image/png;base64,{encoded}"
    return (
        f'<img class="pg-brand-logo {css_class}" '
        f'src="{data_uri}" alt="{escape(alt)}" decoding="async" />'
    )


def _sidebar_brand_logo_html() -> str:
    return brand_logo_html("pg-sidebar-brand-logo")


def _footer_brand_logo_html() -> str:
    return brand_logo_html("pg-footer-brand-logo")

_STATIC_CSS_HREF = "/app/static/careersync.css"

# Minimal sidebar/nav rules — also injected into document.head so they survive tab switches.
_CRITICAL_CSS_RAW = f"""
html:not(.pg-styles-ready) [data-testid="stSidebarNav"] {{
  opacity: 0 !important;
  pointer-events: none !important;
}}
html.pg-styles-ready [data-testid="stSidebarNav"] {{
  opacity: 1 !important;
  transition: opacity 0.12s ease;
}}
:root {{
  --pg-primary: #2563eb;
  --pg-primary-700: #1d4ed8;
  --pg-sidebar-bg: #f8fafc;
  --pg-sidebar-border: #e2e8f0;
  --pg-sidebar-text: #0f172a;
  --pg-sidebar-muted: #64748b;
  --pg-sidebar-accent: #2563eb;
  --pg-sidebar-accent-soft: rgba(37, 99, 235, 0.1);
  --pg-sidebar-accent-strong: #1d4ed8;
  --pg-sidebar-hover: rgba(15, 23, 42, 0.04);
  --pg-main-nav-label: "{MAIN_PAGE_LABEL}";
  --pg-radius-lg: 0.75rem;
  --pg-radius-full: 9999px;
  --pg-font-semibold: 600;
  --pg-font-medium: 500;
  --pg-text-2xs: 0.6875rem;
  --pg-text-sm: 0.875rem;
  --pg-type-nav-size: var(--pg-text-sm);
  --pg-type-nav-weight: var(--pg-font-medium);
  --pg-type-nav-leading: 1.375;
  --pg-type-overline-size: var(--pg-text-2xs);
  --pg-type-overline-weight: var(--pg-font-semibold);
  --pg-type-overline-tracking: var(--pg-tracking-wider);
  --pg-shadow-xs: 0 1px 2px rgba(15, 23, 42, 0.06);
  --pg-shadow-focus: 0 0 0 3px rgba(37, 99, 235, 0.25);
  --pg-duration-normal: 180ms;
  --pg-duration-fast: 120ms;
  --pg-ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
  --pg-tracking-wider: 0.06em;
}}
section[data-testid="stSidebar"] {{
  background: var(--pg-sidebar-bg) !important;
  border-right: 1px solid var(--pg-sidebar-border) !important;
}}
[data-testid="stSidebarNav"] {{
  padding: 0 0 0.45rem !important;
  margin: 0 0 0.45rem !important;
  border-bottom: 1px solid var(--pg-sidebar-border) !important;
  overflow: hidden !important;
}}
[data-testid="stSidebarNav"]::before {{
  content: "Navigation";
  display: block;
  font-size: var(--pg-type-overline-size);
  font-weight: var(--pg-type-overline-weight);
  letter-spacing: var(--pg-type-overline-tracking);
  text-transform: uppercase;
  color: var(--pg-sidebar-muted);
  padding: 0 0.65rem 0.35rem;
}}
[data-testid="stSidebarNav"] ul > li:first-child [data-testid="stSidebarNavLink"] span,
[data-testid="stSidebarNav"] ul > li:first-child [data-testid="stSidebarNavLink"] p {{
  font-size: 0 !important;
  line-height: 0 !important;
  opacity: 0 !important;
  width: 0 !important;
  overflow: hidden !important;
  display: inline-block !important;
}}
[data-testid="stSidebarNav"] ul > li:first-child [data-testid="stSidebarNavLink"]::after {{
  content: "{MAIN_PAGE_LABEL}";
  font-size: var(--pg-type-nav-size);
  line-height: var(--pg-type-nav-leading);
  font-weight: inherit;
  color: inherit;
}}
[data-testid="stSidebarNavLink"] {{
  position: relative !important;
  display: flex !important;
  align-items: center !important;
  gap: 0.7rem !important;
  padding: 0.5rem 0.75rem !important;
  margin: 0 !important;
  border: 1px solid transparent !important;
  border-left: none !important;
  border-image: none !important;
  border-radius: var(--pg-radius-lg) !important;
  color: var(--pg-sidebar-text) !important;
  background: transparent !important;
  box-shadow: none !important;
  font-size: var(--pg-type-nav-size) !important;
  font-weight: var(--pg-type-nav-weight) !important;
  line-height: var(--pg-type-nav-leading) !important;
  letter-spacing: var(--pg-tracking-wide) !important;
  text-decoration: none !important;
  transition: background var(--pg-duration-normal) var(--pg-ease-standard),
    border-color var(--pg-duration-normal) var(--pg-ease-standard),
    color var(--pg-duration-normal) var(--pg-ease-standard) !important;
}}
[data-testid="stSidebarNavLink"]::before {{
  content: none !important;
}}
[data-testid="stSidebarNavLink"]:hover {{
  background: var(--pg-sidebar-hover) !important;
  border-color: var(--pg-sidebar-border) !important;
}}
[data-testid="stSidebarNavLink"][aria-current="page"],
[data-testid="stSidebarNavLink"][aria-selected="true"] {{
  background: var(--pg-sidebar-accent-soft) !important;
  border-color: rgba(37, 99, 235, 0.28) !important;
  color: var(--pg-sidebar-accent-strong) !important;
  font-weight: var(--pg-font-semibold) !important;
  box-shadow: var(--pg-shadow-xs) !important;
}}
[data-testid="stSidebarNavLink"][aria-current="page"]::before,
[data-testid="stSidebarNavLink"][aria-selected="true"]::before {{
  content: "" !important;
  position: absolute;
  left: 0.35rem;
  top: 22%;
  bottom: 22%;
  width: 3px;
  border-radius: var(--pg-radius-full);
  background: var(--pg-sidebar-accent);
}}
.pg-brand-logo {{
  display: block;
  width: 100%;
  height: 100%;
  max-width: 100%;
  object-fit: contain;
  object-position: center;
}}
"""

_CRITICAL_CSS = f'<style id="pg-critical-styles">{_CRITICAL_CSS_RAW}</style>'


def _asset_revision() -> str:
    """Revision token so CSS/Python label changes invalidate cached bundles."""
    parts: list[str] = [MAIN_PAGE_LABEL]
    for path in (
        _TOKENS_PATH,
        _TYPOGRAPHY_PATH,
        _LAYOUT_PATH,
        _COMPONENTS_PATH,
        _STYLES_PATH,
        Path(__file__),
        *_BRAND_LOGO_CANDIDATES,
    ):
        try:
            stat = path.stat()
            parts.append(f"{path.name}:{stat.st_mtime_ns}:{stat.st_size}")
        except OSError:
            continue
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


@st.cache_resource(show_spinner=False)
def _load_stylesheet_bundle(revision: str) -> str:
    _ = revision
    parts: list[str] = []
    for path in (_TOKENS_PATH, _LAYOUT_PATH, _COMPONENTS_PATH, _STYLES_PATH, _TYPOGRAPHY_PATH):
        try:
            parts.append(path.read_text(encoding="utf-8"))
        except OSError:
            continue
    return "\n".join(parts)


@st.cache_resource(show_spinner=False)
def _ensure_static_stylesheet(revision: str) -> str:
    """Write bundled CSS to static/ and return a short content hash for cache busting."""
    css = _load_stylesheet_bundle(revision)
    static_path = _ROOT / "static" / "careersync.css"
    static_path.parent.mkdir(parents=True, exist_ok=True)
    static_path.write_text(css, encoding="utf-8")
    return hashlib.sha256(css.encode("utf-8")).hexdigest()[:12]


def _inject_persistent_styles(stylesheet_version: str) -> None:
    """Persist CareerSync CSS in document.head so tab switches keep sidebar styling."""
    payload = json.dumps(
        {
            "critical": _CRITICAL_CSS_RAW,
            "href": f"{_STATIC_CSS_HREF}?v={stylesheet_version}",
            "mainPageLabel": MAIN_PAGE_LABEL,
        }
    )
    st.html(
        f"""<script>
(function () {{
  var payload = {payload};
  var doc = window.parent && window.parent.document ? window.parent.document : document;

  function upsertStyle(id, css) {{
    var node = doc.getElementById(id);
    if (!node) {{
      node = doc.createElement("style");
      node.id = id;
      doc.head.appendChild(node);
    }}
    if (node.textContent !== css) {{
      node.textContent = css;
    }}
  }}

  function upsertStylesheet(id, href) {{
    var node = doc.getElementById(id);
    if (!node) {{
      node = doc.createElement("link");
      node.id = id;
      node.rel = "stylesheet";
      doc.head.appendChild(node);
    }}
    if (node.getAttribute("href") !== href) {{
      node.setAttribute("href", href);
    }}
  }}

  function syncMainPageLabel() {{
    var label = payload.mainPageLabel || "Main";
    doc.querySelectorAll('.pg-footer-link[href="/"]').forEach(function (node) {{
      if (node.textContent.trim() === "Home") {{
        node.textContent = label;
      }}
    }});
    doc.querySelectorAll(
      '[data-testid="stSidebarNav"] ul > li:first-child [data-testid="stSidebarNavLink"]'
    ).forEach(function (node) {{
      node.setAttribute("aria-label", label);
      node.setAttribute("title", label);
    }});
  }}

  upsertStyle("pg-critical-styles", payload.critical);
  upsertStylesheet("pg-app-stylesheet-link", payload.href);
  syncMainPageLabel();
  function markStylesReady(targetDoc) {{
    if (targetDoc && targetDoc.documentElement) {{
      targetDoc.documentElement.classList.add("pg-styles-ready");
    }}
  }}
  markStylesReady(document);
  markStylesReady(doc);
}})();
</script>""",
        unsafe_allow_javascript=True,
    )


def inject_early_styles() -> None:
    """Apply sidebar-critical CSS immediately (before heavy page imports complete)."""
    revision = _asset_revision()
    brand_logo_html.cache_clear()
    version = _ensure_static_stylesheet(revision)
    bundle = _load_stylesheet_bundle(revision)

    # Drop legacy session keys from older builds (they blocked CSS re-injection).
    for legacy_key in (
        "_pg_styles_head_ready",
        "_pg_styles_version",
        "_pg_inline_styles_version",
    ):
        st.session_state.pop(legacy_key, None)

    # Must run every Streamlit rerun — session guards caused styles to vanish after
    # the first interaction/navigation (DOM is rebuilt each run).
    st.markdown(_CRITICAL_CSS, unsafe_allow_html=True)
    st.markdown(
        f'<style id="pg-app-styles-inline">{bundle}</style>',
        unsafe_allow_html=True,
    )
    _inject_persistent_styles(version)


def apply_sidebar_styles() -> None:
    """Inject design tokens + layout + shared components + page CSS."""
    inject_early_styles()


def init_app_layout(page_id: str = "home", *, show_sidebar_panels: bool = True) -> None:
    """Apply shared layout chrome for the current page.

    Call once near the top of each page (after set_page_config when used).
    Does not alter feature widgets, models, or routing.
    """
    _ = page_id
    apply_sidebar_styles()
    if show_sidebar_panels:
        render_sidebar_panels()


def render_sidebar_panels() -> None:
    """Render brand, stats, and tips below Streamlit's automatic page navigation."""
    with st.sidebar:
        st.html(
            f"""
            <div class="pg-sidebar-brand" role="banner">
                <div class="pg-sidebar-brand-mark" aria-hidden="true">{_sidebar_brand_logo_html()}</div>
                <div class="pg-sidebar-brand-text">
                    <div class="pg-sidebar-brand-title">{escape(APP_NAME)}</div>
                    <div class="pg-sidebar-brand-sub">Career navigation</div>
                </div>
            </div>
            <div class="pg-sidebar-divider" role="separator"></div>
            <div class="pg-sidebar-section">
                <div class="pg-sidebar-section-label">Quick stats</div>
                <ul class="pg-sidebar-stats">
                    <li><span class="pg-stat-value">95%</span><span class="pg-stat-label">Accuracy</span></li>
                    <li><span class="pg-stat-value">100+</span><span class="pg-stat-label">Resumes</span></li>
                    <li><span class="pg-stat-value">50+</span><span class="pg-stat-label">Categories</span></li>
                </ul>
            </div>
            <div class="pg-sidebar-tip">
                <div class="pg-sidebar-section-label">Tip</div>
                <p>Upload a well-formatted resume for the best results.</p>
            </div>
            """
        )


_FOOTER_LINKS: tuple[tuple[str, str], ...] = (
    (MAIN_PAGE_LABEL, "/"),
    ("Resume Classifier", "/1_Resume_Classifier"),
    ("Job Fit Analyzer", "/2_Job_Fit_Analyzer"),
    ("Resume Cluster", "/3_Resume_Cluster"),
    ("Dashboard", "/4_Dashboard"),
)


def _footer_nav_links() -> str:
    return "".join(
        f'<a class="pg-footer-link" href="{escape(href, quote=True)}">{escape(label)}</a>'
        for label, href in _FOOTER_LINKS
    )


def render_app_footer() -> None:
    """Render the shared application footer (presentational only)."""
    st.html(
        f"""
        <footer class="pg-footer" role="contentinfo">
          <div class="pg-footer-accent" aria-hidden="true"></div>
          <div class="pg-footer-inner">
            <div class="pg-footer-grid">
              <div class="pg-footer-brand-col">
                <div class="pg-footer-logo">
                  <span class="pg-footer-logo-mark" aria-hidden="true">{_footer_brand_logo_html()}</span>
                  <span class="pg-footer-logo-text">{escape(APP_NAME)}</span>
                </div>
                <p class="pg-footer-tagline">{escape(APP_TAGLINE)}</p>
                <p class="pg-footer-desc">
                  Powered by advanced machine learning algorithms and designed for career
                  professionals.
                </p>
              </div>
              <div class="pg-footer-links-col">
                <h3 class="pg-footer-col-title">Explore</h3>
                <nav class="pg-footer-nav" aria-label="Footer navigation">
                  {_footer_nav_links()}
                </nav>
              </div>
              <div class="pg-footer-stats-col">
                <h3 class="pg-footer-col-title">Platform</h3>
                <ul class="pg-footer-pills">
                  <li><span class="pg-footer-pill">95% Accuracy</span></li>
                  <li><span class="pg-footer-pill">100+ Resumes</span></li>
                  <li><span class="pg-footer-pill">50+ Categories</span></li>
                </ul>
              </div>
            </div>
            <div class="pg-footer-bottom">
              <p class="pg-footer-meta">
                &copy; 2026 {escape(APP_NAME)} &middot; AI-powered career intelligence
              </p>
            </div>
          </div>
        </footer>
        """
    )
