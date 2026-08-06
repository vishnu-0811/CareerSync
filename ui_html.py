"""Small HTML rendering helper for Streamlit UI markup."""

from __future__ import annotations

import textwrap

import streamlit as st


def render_html(fragment: str) -> None:
    """Render raw HTML without markdown code-block escaping."""
    st.markdown(textwrap.dedent(fragment).strip(), unsafe_allow_html=True)
