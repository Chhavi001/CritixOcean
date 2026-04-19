from __future__ import annotations

import re
from typing import Any

import streamlit as st

from pipeline import run_research_pipeline


st.set_page_config(
  page_title="CritixOcean",
  page_icon="🌊",
  layout="wide",
  initial_sidebar_state="collapsed",
)


def _inject_styles() -> None:
  st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

      :root {
        --bg: #000000;
        --bg-2: #050505;
        --panel: rgba(255, 255, 255, 0.04);
        --panel-strong: rgba(255, 255, 255, 0.06);
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.08);
        --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
        --text: #f0ece4;
        --text-dim: rgba(255, 255, 255, 0.5);
        --muted: #a09890;
        --accent: #ffb65e;
        --accent-glow: rgba(255, 160, 50, 0.5);
        --accent-2: #ff7d5c;
        --accent-3: #c4a1ff;
        --accent-4: #66d8c7;
        --border: rgba(255, 182, 94, 0.12);
        --border-subtle: rgba(255, 255, 255, 0.06);
      }

      /* ─── GLOBAL RESET ─── */
      html, body, [class*="css"] {
        font-family: 'Inter', 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }

      /* Hide default streamlit elements */
      #MainMenu, header[data-testid="stHeader"], footer, .stDeployButton {
        display: none !important;
      }

      [data-testid="stSidebar"] {
        display: none;
      }

      /* ─── ANIMATED BACKGROUND ─── */
      .stApp {
        background: #000000;
        color: var(--text);
        overflow-x: hidden;
      }

      /* Kill default Streamlit top padding */
      .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
      }

      /* ─── AMBIENT CANVAS ─── */
      .ambient-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100vh;
        z-index: 0;
        pointer-events: none;
        overflow: hidden;
      }

      .ambient-orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(80px);
        opacity: 0;
        animation: orbFloat 12s ease-in-out infinite;
      }

      .ambient-orb-1 {
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255, 140, 50, 0.4) 0%, rgba(255, 100, 30, 0.15) 40%, transparent 70%);
        top: -5%;
        left: 35%;
        animation-delay: 0s;
        opacity: 0.7;
      }

      .ambient-orb-2 {
        width: 350px;
        height: 350px;
        background: radial-gradient(circle, rgba(255, 120, 40, 0.35) 0%, rgba(200, 80, 20, 0.1) 50%, transparent 70%);
        top: 5%;
        left: 55%;
        animation-delay: -3s;
        opacity: 0.5;
      }

      .ambient-orb-3 {
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(100, 120, 255, 0.12) 0%, rgba(80, 100, 200, 0.05) 50%, transparent 70%);
        top: 2%;
        left: 20%;
        animation-delay: -6s;
        opacity: 0.35;
      }

      .ambient-streak {
        position: absolute;
        width: 600px;
        height: 3px;
        background: linear-gradient(90deg, transparent, rgba(255, 160, 60, 0.6), rgba(255, 120, 40, 0.3), transparent);
        top: 18%;
        left: 15%;
        transform: rotate(-15deg);
        filter: blur(2px);
        animation: streakGlow 8s ease-in-out infinite;
        opacity: 0.5;
      }

      .ambient-streak-2 {
        position: absolute;
        width: 450px;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255, 140, 50, 0.4), rgba(200, 100, 30, 0.2), transparent);
        top: 25%;
        left: 40%;
        transform: rotate(-20deg);
        filter: blur(1.5px);
        animation: streakGlow 10s ease-in-out infinite;
        animation-delay: -4s;
        opacity: 0.4;
      }

      /* ─── NOISE TEXTURE OVERLAY ─── */
      .noise-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1;
        pointer-events: none;
        opacity: 0.025;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
        background-repeat: repeat;
        background-size: 256px 256px;
      }

      /* ─── BADGE PILL ─── */
      .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 8px 18px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.06em;
        animation: pillFloat 4s ease-in-out infinite;
        margin-bottom: 1rem;
      }

      .badge-pill .badge-icon {
        font-size: 0.85rem;
      }

      /* ─── HERO BRAND ─── */
      .hero-container {
        position: relative;
        z-index: 2;
        padding-top: 1.5vh;
        padding-bottom: 0.5rem;
      }

      .brand-stage {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 0;
        position: relative;
        text-align: center;
      }

      .brand-word {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(3.5rem, 8vw, 7.5rem);
        font-weight: 700;
        line-height: 1;
        letter-spacing: -0.04em;
        margin: 0;
        background: linear-gradient(
          180deg,
          #ffffff 0%,
          #ffe4c4 25%,
          #ffb86c 50%,
          #ff9a44 75%,
          #e8d5b8 100%
        );
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: titleShimmer 8s ease-in-out infinite;
        position: relative;
      }

      .brand-word::after {
        content: '';
        display: block;
        margin: 1rem auto 0;
        width: min(36vw, 280px);
        height: 2px;
        border-radius: 999px;
        background: linear-gradient(90deg, transparent, rgba(255, 170, 70, 0.7), rgba(255, 120, 60, 0.5), transparent);
        animation: lineShimmer 6s ease-in-out infinite;
      }

      .brand-subtle {
        margin-top: 0.6rem;
        color: rgba(255, 255, 255, 0.25);
        font-size: 0.72rem;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        font-weight: 500;
      }

      /* ─── HIDDEN HELPERS ─── */
      .command-title,
      .command-copy,
      .command-divider,
      .prompt-title,
      .prompt-note,
      .mini-title,
      .mini-copy,
      .topic-direction {
        display: none !important;
      }

      .deck-inner-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--text);
        margin: 0 0 0.3rem 0;
        text-align: center;
      }

      .deck-inner-subtitle {
        font-size: 0.88rem;
        color: var(--text-dim);
        text-align: center;
        margin: 0 0 1rem 0;
        line-height: 1.5;
      }

      /* ─── CENTER SHELL ─── */
      .center-shell {
        max-width: 960px;
        margin: 0 auto;
        position: relative;
        z-index: 2;
      }

      /* ─── FORM = GLASSMORPHISM CARD ─── */
      /* ─── PROMPT BAR (ChatGPT / Gemini style) ─── */
      .stForm {
        max-width: 720px;
        margin: 0 auto;
      }

      div[data-testid="stForm"] {
        position: relative;
        z-index: 2;
        max-width: 720px;
        margin: 0.8rem auto 0;
        background: rgba(255, 255, 255, 0.045) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 28px !important;
        padding: 6px 6px 6px 12px !important;
        backdrop-filter: blur(30px) saturate(1.3);
        -webkit-backdrop-filter: blur(30px) saturate(1.3);
        box-shadow:
          0 4px 24px rgba(0, 0, 0, 0.3),
          inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
        overflow: visible;
        animation: fadeInUp 0.8s ease-out 0.15s both;
      }

      div[data-testid="stForm"]:focus-within {
        border-color: rgba(255, 182, 94, 0.35) !important;
        box-shadow:
          0 4px 24px rgba(0, 0, 0, 0.3),
          0 0 0 3px rgba(255, 182, 94, 0.07),
          0 0 40px rgba(255, 182, 94, 0.04),
          inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
      }

      div[data-testid="stForm"]::before {
        display: none !important;
      }

      /* Remove column gap inside form for unified bar look */
      div[data-testid="stForm"] [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        align-items: center !important;
      }

      /* ─── SEND BUTTON (circular, in column) ─── */
      div[data-testid="stForm"] .stFormSubmitButton {
        margin: 0 !important;
        padding: 0 !important;
      }

      div[data-testid="stForm"] .stFormSubmitButton button {
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        max-width: 44px !important;
        min-height: 44px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        background: linear-gradient(135deg, #ffb65e 0%, #ff9a44 100%) !important;
        color: #000000 !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 16px rgba(255, 150, 50, 0.3) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: none !important;
        letter-spacing: 0 !important;
        line-height: 1 !important;
        margin-left: auto !important;
      }

      div[data-testid="stForm"] .stFormSubmitButton button:hover {
        box-shadow: 0 6px 24px rgba(255, 150, 50, 0.45) !important;
        background: linear-gradient(135deg, #ffc878 0%, #ffaa55 100%) !important;
        transform: scale(1.06);
      }

      div[data-testid="stForm"] .stFormSubmitButton button:active {
        transform: scale(0.94) !important;
      }

      /* ─── INPUT STYLING (borderless inside bar) ─── */
      div[data-testid="stForm"] .stTextInput input {
        min-height: 52px;
        border-radius: 22px !important;
        border: none !important;
        background: transparent !important;
        color: var(--text) !important;
        font-size: 1.02rem !important;
        font-weight: 400 !important;
        padding: 0 62px 0 1.2rem !important;
        box-shadow: none !important;
        outline: none !important;
        transition: none;
      }

      div[data-testid="stForm"] .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.28) !important;
        font-weight: 400;
      }

      div[data-testid="stForm"] .stTextInput input:focus {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
      }

      div[data-testid="stForm"] .stTextInput label {
        display: none !important;
      }

      div[data-testid="stForm"] div[data-testid="stTextInput"] {
        margin-top: 0;
      }

      /* Hide Streamlit's default 'Press Enter to submit form' text */
      div[data-testid="stForm"] .stFormSubmitButton + div,
      div[data-testid="stForm"] [data-testid="stFormSubmitButton"] + div,
      div[data-testid="stForm"] .stMarkdown:last-child,
      div[data-testid="stForm"] [data-testid="stFormSubmitMessage"],
      div[data-testid="stForm"] > div > div:last-child > div[data-testid="stMarkdownContainer"],
      div[data-testid="stForm"] small,
      div[data-testid="stForm"] .stFormSubmitButton ~ div:not(.stTextInput):not(.stExpander) {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
      }
      /* Also hide the inline instruction that sits near the input */
      div[data-testid="stForm"] [data-testid="InputInstructions"],
      div[data-testid="stForm"] [data-testid="InputInstructions"] * {
        display: none !important;
      }

      /* ─── PROMPT HINT ─── */
      .prompt-hint {
        text-align: center;
        color: rgba(255, 255, 255, 0.2);
        font-size: 0.76rem;
        margin: 0.7rem 0 0.3rem;
        letter-spacing: 0.04em;
        font-weight: 400;
        font-style: italic;
      }

      /* ─── RESET BUTTON GHOST STYLE + CENTERING ─── */
      /* Center: target the parent element container */
      .stMainBlockContainer [data-testid="stElementContainer"]:has(.stButton) {
        display: flex !important;
        justify-content: center !important;
      }

      .stMainBlockContainer .stButton > button {
        background: transparent !important;
        color: rgba(255, 255, 255, 0.28) !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 0.82rem !important;
        font-weight: 400 !important;
        padding: 0.3rem 1rem !important;
        letter-spacing: 0.02em;
        transition: color 0.2s ease !important;
      }

      .stMainBlockContainer .stButton > button:hover {
        color: rgba(255, 255, 255, 0.55) !important;
        background: rgba(255, 255, 255, 0.04) !important;
        transform: none !important;
        box-shadow: none !important;
      }

      /* ─── SETTINGS EXPANDER (outside form, constrained) ─── */
      .stMainBlockContainer .stExpander {
        max-width: 720px !important;
        margin: 0.4rem auto 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        background: rgba(255, 255, 255, 0.02) !important;
        transition: border-color 0.3s ease;
      }

      .stMainBlockContainer .stExpander:hover {
        border-color: rgba(255, 182, 94, 0.12) !important;
      }

      .stExpander summary {
        color: rgba(255, 255, 255, 0.4) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
      }

      .stExpander summary span {
        color: rgba(255, 255, 255, 0.4) !important;
      }



      /* ─── GENERAL INPUT STYLING (outside form) ─── */
      .stTextInput input {
        min-height: 52px;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(0, 0, 0, 0.4) !important;
        color: var(--text) !important;
        font-size: 1rem !important;
        font-weight: 400 !important;
        padding: 0 1.2rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }

      .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.3) !important;
      }

      .stTextInput input:focus {
        border-color: rgba(255, 182, 94, 0.4) !important;
        box-shadow: 0 0 0 3px rgba(255, 182, 94, 0.08) !important;
        outline: none !important;
      }

      /* ─── EXPANDER (Advanced tuning) ─── */
      .stExpander {
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 16px !important;
        background: rgba(255, 255, 255, 0.02) !important;
        margin-top: 0.8rem !important;
        transition: all 0.3s ease;
      }

      .stExpander:hover {
        border-color: rgba(255, 182, 94, 0.15) !important;
      }

      .stExpander summary {
        color: rgba(255, 255, 255, 0.5) !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
      }

      .stExpander summary span {
        color: rgba(255, 255, 255, 0.5) !important;
      }

      /* ─── BUTTON SYSTEM ─── */
      .stButton > button {
        border-radius: 14px;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 0.92rem;
        letter-spacing: 0.01em;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
      }

      /* Primary button — only form submit buttons, NOT regular st.button() */
      .stButton > button[kind="primaryFormSubmit"] {
        background: #ffffff !important;
        color: #000000 !important;
        box-shadow: 0 4px 16px rgba(255, 255, 255, 0.1);
      }

      .stButton > button[kind="primaryFormSubmit"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(255, 255, 255, 0.15);
        background: #f0e8dc !important;
      }

      .stButton > button[kind="primaryFormSubmit"]:active {
        transform: translateY(0);
      }

      /* Download button */
      .stDownloadButton > button {
        background: rgba(255, 182, 94, 0.12) !important;
        color: var(--accent) !important;
        border: 1px solid rgba(255, 182, 94, 0.2) !important;
        border-radius: 14px;
      }

      .stDownloadButton > button:hover {
        background: rgba(255, 182, 94, 0.2) !important;
        transform: translateY(-1px);
      }

      /* ─── GLASS CARDS ─── */
      .glass {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 24px;
        padding: 1.5rem 1.8rem;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow:
          0 8px 32px rgba(0, 0, 0, 0.3),
          inset 0 1px 0 rgba(255, 255, 255, 0.05);
        animation: none;
      }

      /* ─── METRIC CARDS ─── */
      .metric-card {
        padding: 1.2rem 1.4rem;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
      }

      .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 182, 94, 0.3), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
      }

      .metric-card:hover {
        border-color: rgba(255, 182, 94, 0.15);
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
      }

      .metric-card:hover::before {
        opacity: 1;
      }

      .metric-label {
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.78rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
      }

      .metric-value {
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
        background: linear-gradient(135deg, #ffffff 0%, #ffb86c 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
      }

      .metric-note {
        color: rgba(255, 255, 255, 0.35);
        font-size: 0.82rem;
        margin-top: 0.3rem;
        font-weight: 400;
      }

      /* ─── SECTION TITLES ─── */
      .section-title {
        color: var(--text);
        font-weight: 700;
        font-size: 1.15rem;
        letter-spacing: -0.01em;
        margin: 0 0 0.3rem 0;
      }

      .section-subtitle {
        color: rgba(255, 255, 255, 0.4);
        margin-top: 0;
        font-size: 0.9rem;
        font-weight: 400;
      }

      .card-note {
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.9rem;
      }

      .compact-note {
        color: rgba(255, 255, 255, 0.3);
        font-size: 0.82rem;
      }

      /* ─── TABS ─── */
      .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 14px;
        padding: 4px;
        border: 1px solid rgba(255, 255, 255, 0.06);
      }

      .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        font-size: 0.88rem;
        color: rgba(255, 255, 255, 0.4) !important;
        transition: all 0.2s ease;
      }

      .stTabs [data-baseweb="tab"]:hover {
        color: rgba(255, 255, 255, 0.7) !important;
        background: rgba(255, 255, 255, 0.04);
      }

      .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
      }

      .stTabs [data-baseweb="tab-highlight"] {
        display: none;
      }

      .stTabs [data-baseweb="tab-border"] {
        display: none;
      }

      /* ─── SLIDERS ─── */
      .stSlider [data-baseweb="slider"] [role="slider"] {
        background: var(--accent) !important;
        border-color: var(--accent) !important;
      }

      .stSlider [data-testid="stTickBar"] > div {
        background: rgba(255, 182, 94, 0.3) !important;
      }

      /* ─── TOGGLE ─── */
      div[data-testid="stToggle"] label span {
        color: rgba(255, 255, 255, 0.6) !important;
      }

      /* ─── SELECTBOX / MULTISELECT ─── */
      .stSelectbox div[data-baseweb="select"] > div,
      .stMultiSelect div[data-baseweb="select"] > div {
        background: rgba(0, 0, 0, 0.5) !important;
        color: var(--text) !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
      }

      /* ─── TEXT AREA ─── */
      .stTextArea textarea {
        background: rgba(0, 0, 0, 0.5) !important;
        color: var(--text) !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
      }

      /* ─── STATUS COMPONENT ─── */
      div[data-testid="stStatusWidget"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 16px !important;
      }

      /* ─── FOOTER ─── */
      .footer-wrap {
        text-align: center;
        padding: 3rem 1rem 2rem;
        position: relative;
        z-index: 2;
      }

      .footer-line {
        width: 60px;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
        margin: 0 auto 1rem;
      }

      .footer-note {
        color: rgba(255, 255, 255, 0.2);
        font-size: 0.78rem;
        font-weight: 400;
        letter-spacing: 0.02em;
      }

      /* ─── BIG GHOST TEXT ─── */
      .ghost-text {
        position: relative;
        z-index: 1;
        text-align: center;
        margin-top: 2rem;
        overflow: hidden;
        padding: 0 2rem;
      }

      .ghost-text span {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(4rem, 12vw, 12rem);
        font-weight: 900;
        letter-spacing: -0.04em;
        color: transparent;
        -webkit-text-stroke: 1px rgba(255, 255, 255, 0.03);
        text-transform: uppercase;
        line-height: 0.9;
        display: block;
        user-select: none;
      }

      /* ─── SOCIAL ICONS ROW ─── */
      .social-row {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin: 1.2rem 0;
        position: relative;
        z-index: 2;
      }

      .social-dot {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: center;
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.9rem;
        transition: all 0.3s ease;
        cursor: pointer;
      }

      .social-dot:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
        color: #ffffff;
        transform: translateY(-2px);
      }

      /* ─── KEYFRAME ANIMATIONS ─── */
      @keyframes orbFloat {
        0%, 100% {
          transform: translate(0, 0) scale(1);
          opacity: 0.5;
        }
        25% {
          transform: translate(15px, -20px) scale(1.05);
          opacity: 0.7;
        }
        50% {
          transform: translate(-10px, -35px) scale(1.08);
          opacity: 0.6;
        }
        75% {
          transform: translate(8px, -15px) scale(1.02);
          opacity: 0.55;
        }
      }

      @keyframes streakGlow {
        0%, 100% {
          opacity: 0.2;
          transform: rotate(-15deg) scaleX(0.8);
        }
        50% {
          opacity: 0.6;
          transform: rotate(-15deg) scaleX(1.1);
        }
      }

      @keyframes titleShimmer {
        0%, 100% {
          filter: drop-shadow(0 0 8px rgba(255, 160, 50, 0.08));
        }
        50% {
          filter: drop-shadow(0 0 24px rgba(255, 160, 50, 0.2));
        }
      }

      @keyframes lineShimmer {
        0%, 100% {
          opacity: 0.5;
          transform: scaleX(0.85);
        }
        50% {
          opacity: 1;
          transform: scaleX(1.05);
        }
      }

      @keyframes pillFloat {
        0%, 100% {
          transform: translateY(0);
        }
        50% {
          transform: translateY(-3px);
        }
      }

      @keyframes fadeInUp {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      /* fade-in for main content */
      .hero-container {
        animation: fadeInUp 0.8s ease-out;
      }


      .glass {
        animation: fadeInUp 0.6s ease-out;
      }

      /* ─── LINK BUTTONS ─── */
      .stLinkButton a {
        color: var(--accent) !important;
        border: 1px solid rgba(255, 182, 94, 0.2) !important;
        border-radius: 12px !important;
        background: rgba(255, 182, 94, 0.05) !important;
        transition: all 0.2s ease;
      }

      .stLinkButton a:hover {
        background: rgba(255, 182, 94, 0.12) !important;
        border-color: rgba(255, 182, 94, 0.35) !important;
      }

      /* ─── JSON VIEWER ─── */
      .stJson {
        background: rgba(0, 0, 0, 0.3) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
      }

      /* ─── RESPONSIVE ─── */
      @media (max-width: 768px) {
        .command-deck {
          margin: 1rem 0.5rem 0;
          padding: 1.5rem 1.2rem;
          border-radius: 20px;
        }

        .brand-word {
          font-size: clamp(2.5rem, 10vw, 4rem);
        }

        .ghost-text span {
          font-size: clamp(2.5rem, 15vw, 6rem);
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
  )


def _parse_score(feedback: str) -> str:
  match = re.search(r"Score:\s*([0-9]+(?:\.[0-9]+)?/10)", feedback)
  return match.group(1) if match else "N/A"


def _progress_callback(stage: str, message: str, payload: dict[str, Any]) -> None:
  status = st.session_state.get("_critixocean_status")
  if status is None:
    return
  if stage == "search":
    status.update(label=f"Search: {message}", state="running")
  elif stage == "scrape":
    status.update(label=f"Scrape: {message}", state="running")
  elif stage == "write":
    status.update(label=f"Write: {message}", state="running")
  elif stage == "critic":
    status.update(label=f"Critic: {message}", state="running")
  elif stage == "error":
    status.update(label=f"Error: {message}", state="error")


def _render_report_card(label: str, value: str, note: str) -> None:
  st.markdown(
    f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-note">{note}</div>
    </div>
    """,
    unsafe_allow_html=True,
  )


def _render_ambient_bg() -> None:
  st.markdown(
    """
    <div class="ambient-canvas">
      <div class="ambient-orb ambient-orb-1"></div>
      <div class="ambient-orb ambient-orb-2"></div>
      <div class="ambient-orb ambient-orb-3"></div>
      <div class="ambient-streak"></div>
      <div class="ambient-streak-2"></div>
    </div>
    <div class="noise-overlay"></div>
    """,
    unsafe_allow_html=True,
  )


def main() -> None:
  _inject_styles()
  _render_ambient_bg()

  # ─── HERO ───
  st.markdown('<div class="hero-container">', unsafe_allow_html=True)
  st.markdown('<div class="center-shell">', unsafe_allow_html=True)
  st.markdown(
    """
    <div class="brand-stage">
      <h1 class="brand-word">CritixOcean</h1>
      <div class="brand-subtle">research mode</div>
    </div>
    """,
    unsafe_allow_html=True,
  )
  st.markdown('</div>', unsafe_allow_html=True)
  st.markdown('</div>', unsafe_allow_html=True)

  # ─── PROMPT BAR (ChatGPT / Gemini style) ───
  st.markdown('<div class="center-shell">', unsafe_allow_html=True)

  with st.form("research_form", clear_on_submit=False):
    input_col, btn_col = st.columns([0.92, 0.08])
    with input_col:
      topic = st.text_input(
        "Topic",
        placeholder="Ask CritixOcean to research anything...",
        label_visibility="collapsed",
      )
    with btn_col:
      run_clicked = st.form_submit_button("↑")

  st.markdown('<div class="prompt-hint">Engineered for Precise Insights</div>', unsafe_allow_html=True)

  # Settings & Reset outside the form
  with st.expander("⚙ Advanced settings", expanded=False):
    a1, a2, a3 = st.columns(3)
    with a1:
      max_search_results = st.slider("Search results", 3, 10, 5)
    with a2:
      max_scrape_urls = st.slider("Pages to scrape", 1, 6, 4)
    with a3:
      max_chars_each = st.slider("Chars per page", 1000, 5000, 2500, step=250)
    b1, b2 = st.columns(2)
    with b1:
      show_diagnostics = st.toggle("Show diagnostics", value=True)
    with b2:
      show_raw_sources = st.toggle("Show raw search items", value=False)
    st.markdown('<div class="compact-note">Fine-tune the research pipeline parameters.</div>', unsafe_allow_html=True)

  left_pad, center_btn, right_pad = st.columns([5, 2, 5])
  with center_btn:
    reset_clicked = st.button("↺ Reset", use_container_width=True)

  st.markdown('</div>', unsafe_allow_html=True)  # close center-shell

  # ─── ACTIONS ───
  if reset_clicked:
    for key in ["critixocean_result", "critixocean_error", "_critixocean_status", "critixocean_topic"]:
      st.session_state.pop(key, None)
    st.rerun()

  if run_clicked:
    if not topic.strip():
      st.error("Enter a research topic before running the pipeline.")
    else:
      st.session_state["critixocean_topic"] = topic.strip()
      status = st.status("Booting CritixOcean...", expanded=True)
      st.session_state["_critixocean_status"] = status
      try:
        result = run_research_pipeline(
          topic.strip(),
          progress_callback=_progress_callback,
          max_search_results=max_search_results,
          max_scrape_urls=max_scrape_urls,
          max_chars_each=max_chars_each,
        )
        st.session_state["critixocean_result"] = result
        st.session_state.pop("critixocean_error", None)
        status.update(label="CritixOcean finished successfully.", state="complete")
      except Exception as exc:
        st.session_state["critixocean_error"] = str(exc)
        status.update(label="CritixOcean hit a problem.", state="error")
      finally:
        st.session_state.pop("_critixocean_status", None)

  # ─── RESULTS ───
  result = st.session_state.get("critixocean_result")
  error = st.session_state.get("critixocean_error")

  if result:
    st.markdown(
      """
      <div class="glass">
        <div class="section-title">Control Room</div>
        <p class="section-subtitle">Your latest run summary and outputs.</p>
      </div>
      """,
      unsafe_allow_html=True,
    )
    score = _parse_score(result.get("feedback", ""))
    m1, m2, m3, m4 = st.columns(4)
    with m1:
      _render_report_card("Score", score, "Critic verdict")
    with m2:
      _render_report_card("Sources", str(len(result.get("used_source_urls", []))), "Used URLs")
    with m3:
      _render_report_card("Scraped", str(result.get("scrape_diagnostics", {}).get("succeeded", 0)), "Pages")
    with m4:
      _render_report_card("Search Hits", str(len(result.get("search_items", []))), "Candidate links")

    st.write("")
    tabs = st.tabs(["Final Brief", "Sources", "Diagnostics", "Critic"])

    with tabs[0]:
      st.markdown(result.get("report", ""))
      download_topic = st.session_state.get("critixocean_topic", "research-topic")
      st.download_button(
        "Download final brief",
        data=result.get("report", ""),
        file_name=f"CritixOcean-{download_topic.replace(' ', '-')}.md",
        mime="text/markdown",
      )

    with tabs[1]:
      st.markdown("### Successfully scraped sources")
      for url in result.get("used_source_urls", []):
        st.link_button(url, url)
      if show_raw_sources:
        st.markdown("### Raw search items")
        st.code(result.get("search_results", ""), language="text")

    with tabs[2]:
      st.json(result.get("scrape_diagnostics", {}))
      if show_diagnostics:
        st.markdown("### Scraped content preview")
        st.text_area("", result.get("scraped_content", ""), height=260, label_visibility="collapsed")

    with tabs[3]:
      st.markdown(result.get("feedback", ""))

  if error:
    st.error(error)

  # ─── FOOTER ───
  st.markdown(
    """
    <div class="footer-wrap">
      <div class="footer-line"></div>
      <div class="footer-note">Build by <span style="color: rgba(255,182,94,0.7); font-weight: 500;">Chhavi Gautam</span></div>
    </div>
    """,
    unsafe_allow_html=True,
  )


if __name__ == "__main__":
  main()