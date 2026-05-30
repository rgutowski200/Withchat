import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import io
from xml.sax.saxutils import escape as xml_escape
from datetime import date

from db import supabase

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)

st.set_page_config(page_title="Retirement Blueprint 101", layout="wide", initial_sidebar_state="collapsed")


st.markdown("""
<style>
/* App shell closer to a modern SaaS product */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border-right: 1px solid #E2E8F0;
}
section[data-testid="stSidebar"] div.stButton > button {
    justify-content: flex-start;
    min-height: 46px;
    border-radius: 12px;
    background: transparent;
    color: #0F172A;
    border: 1px solid transparent;
    box-shadow: none;
    font-weight: 750;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: #EEF6FF;
    border-color: #DBEAFE;
    color: #1D4ED8;
    transform: none;
    box-shadow: none;
}
section[data-testid="stSidebar"] div.stButton > button:disabled {
    background: linear-gradient(135deg,#2563EB,#1D4ED8);
    color: white;
    border-color: #1D4ED8;
    opacity: 1;
}

/* Hide old top nav wrapper if any legacy markup remains */
.rb-nav-intro, .rb-nav-wrap { display:none !important; }

.rb-saas-hero {
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:18px;
    margin-bottom:18px;
}
.rb-saas-title {
    color:#0F172A;
    font-size:2rem;
    font-weight:900;
    letter-spacing:-.03em;
    margin-bottom:6px;
}
.rb-saas-sub {
    color:#64748B;
    font-size:1rem;
    max-width:720px;
}
.rb-roadmap-v2 {
    position:relative;
    overflow:hidden;
    background:linear-gradient(135deg,#FFFFFF 0%,#F6FBFF 55%,#ECFDF5 100%);
    border:1px solid #E2E8F0;
    border-radius:24px;
    padding:24px;
    box-shadow:0 12px 32px rgba(15,23,42,.06);
    margin-bottom:18px;
}
.rb-roadmap-v2:after {
    content:"";
    position:absolute;
    right:-80px;
    bottom:-120px;
    width:520px;
    height:300px;
    border-radius:50%;
    background:radial-gradient(circle,#BBF7D0 0%,rgba(187,247,208,.0) 68%);
    opacity:.55;
}
.rb-roadmap-v2-title {
    position:relative;
    z-index:1;
    font-size:1.45rem;
    font-weight:900;
    color:#0F172A;
    margin-bottom:18px;
}
.rb-roadmap-steps {
    position:relative;
    z-index:1;
    display:grid;
    grid-template-columns:repeat(6,minmax(0,1fr));
    gap:12px;
}
.rb-roadmap-step {
    text-align:center;
    padding:8px;
}
.rb-roadmap-num {
    width:42px;
    height:42px;
    border-radius:999px;
    margin:0 auto 10px auto;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#fff;
    font-weight:900;
    background:#2563EB;
    box-shadow:0 10px 22px rgba(37,99,235,.18);
}
.rb-roadmap-step.done .rb-roadmap-num { background:#16A34A; box-shadow:0 10px 22px rgba(22,163,74,.18); }
.rb-roadmap-step-title {
    font-weight:850;
    color:#0F172A;
    font-size:.9rem;
    line-height:1.25;
}
.rb-roadmap-step-copy {
    color:#64748B;
    font-size:.8rem;
    line-height:1.35;
    margin-top:4px;
}
.rb-kpi-card-v2 {
    border:1px solid #E2E8F0;
    border-radius:22px;
    background:#FFFFFF;
    padding:20px;
    min-height:178px;
    box-shadow:0 12px 28px rgba(15,23,42,.055);
}
.rb-kpi-label {
    color:#334155;
    font-weight:850;
    font-size:.96rem;
    margin-bottom:12px;
}
.rb-kpi-value {
    font-size:2.25rem;
    font-weight:950;
    color:#0F172A;
    line-height:1;
    margin-bottom:10px;
}
.rb-kpi-value.green { color:#15803D; }
.rb-kpi-note {
    color:#64748B;
    font-size:.92rem;
    line-height:1.4;
}
.rb-kpi-pill {
    display:inline-block;
    padding:5px 10px;
    border-radius:999px;
    background:#DCFCE7;
    color:#166534;
    font-size:.8rem;
    font-weight:800;
    margin-bottom:10px;
}
.rb-next-panel-v2 {
    border:1px solid #D9F99D;
    border-radius:24px;
    background:linear-gradient(180deg,#F7FEE7,#ECFDF5);
    padding:24px;
    box-shadow:0 12px 28px rgba(22,163,74,.08);
}
.rb-next-title-v2 {
    color:#166534;
    font-size:1.35rem;
    font-weight:900;
    margin-bottom:8px;
}
.rb-chart-card-v2 {
    border:1px solid #E2E8F0;
    border-radius:24px;
    background:#FFFFFF;
    padding:18px;
    box-shadow:0 12px 28px rgba(15,23,42,.055);
}
.rb-premium-title-row {
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin:22px 0 12px 0;
}
.rb-premium-title-main {
    color:#0F172A;
    font-size:1.25rem;
    font-weight:900;
}
.rb-premium-see-all {
    color:#2563EB;
    font-size:.92rem;
    font-weight:800;
}
.rb-premium-grid-v2 {
    display:grid;
    grid-template-columns:repeat(6,minmax(0,1fr));
    gap:14px;
}
.rb-premium-mini {
    border:1px solid #E2E8F0;
    border-radius:18px;
    padding:16px;
    background:#FFFFFF;
    min-height:260px;
    height:260px;
    display:flex;
    flex-direction:column;
    box-shadow:0 10px 24px rgba(15,23,42,.045);
}
.rb-premium-mini-icon {
    width:38px;
    height:38px;
    border-radius:999px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#EFF6FF;
    margin-bottom:10px;
    font-size:18px;
}
.rb-premium-mini-title {
    color:#0F172A;
    font-weight:900;
    line-height:1.18;
    font-size:.88rem;
    margin-bottom:6px;
}
.rb-premium-mini-copy {
    color:#64748B;
    font-size:.8rem;
    line-height:1.35;
    margin-bottom:8px;
    flex:1 1 auto;
}
.rb-premium-mini-badge {
    display:inline-block;
    width:fit-content;
    padding:4px 9px;
    border-radius:999px;
    background:#EEF2FF;
    color:#2563EB;
    font-size:.72rem;
    font-weight:850;
    margin-top:auto;
}
@media (max-width: 1100px) {
    .rb-roadmap-steps { grid-template-columns:repeat(3,minmax(0,1fr)); }
    .rb-premium-grid-v2 { grid-template-columns:repeat(3,minmax(0,1fr)); }
}
@media (max-width: 700px) {
    .rb-roadmap-steps { grid-template-columns:repeat(2,minmax(0,1fr)); }
    .rb-premium-grid-v2 { grid-template-columns:repeat(2,minmax(0,1fr)); }
}

.rb-qs-step-text b {
    color: #0f172a;
    font-weight: 900;
}


/* Hide Streamlit's 'Press Enter to submit form' placeholder text in all input boxes */
input::placeholder,
textarea::placeholder {
    color: transparent !important;
    opacity: 0 !important;
}
input::-webkit-input-placeholder,
textarea::-webkit-input-placeholder {
    color: transparent !important;
    opacity: 0 !important;
}
input::-moz-placeholder,
textarea::-moz-placeholder {
    color: transparent !important;
    opacity: 0 !important;
}
input:-ms-input-placeholder,
textarea:-ms-input-placeholder {
    color: transparent !important;
    opacity: 0 !important;
}


/* Stronger cleanup for Streamlit form placeholder/helper text */
[data-baseweb="input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder,
.stNumberInput input::placeholder,
.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
input[placeholder="Press Enter to submit form"]::placeholder {
    color: transparent !important;
    opacity: 0 !important;
}
[data-baseweb="input"] input::-webkit-input-placeholder,
.stNumberInput input::-webkit-input-placeholder,
.stTextInput input::-webkit-input-placeholder {
    color: transparent !important;
    opacity: 0 !important;
}


.rb-progress-wrap {
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    background: #FFFFFF;
    padding: 14px 16px;
    margin: 12px 0 18px 0;
    box-shadow: 0 8px 22px rgba(15,23,42,.04);
}
.rb-progress-title {
    font-size: .86rem;
    font-weight: 900;
    color: #334155;
    margin-bottom: 10px;
    letter-spacing: .02em;
}
.rb-progress-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 10px;
}
.rb-progress-step {
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 10px;
    background: #F8FAFC;
}
.rb-progress-step.active {
    border-color: #93C5FD;
    background: #EFF6FF;
}
.rb-progress-step.done {
    border-color: #BBF7D0;
    background: #F0FDF4;
}
.rb-progress-num {
    display: inline-flex;
    width: 24px;
    height: 24px;
    border-radius: 999px;
    align-items: center;
    justify-content: center;
    background: #CBD5E1;
    color: #0F172A;
    font-size: .78rem;
    font-weight: 900;
    margin-bottom: 6px;
}
.rb-progress-step.active .rb-progress-num {
    background: #2563EB;
    color: #FFFFFF;
}
.rb-progress-step.done .rb-progress-num {
    background: #16A34A;
    color: #FFFFFF;
}
.rb-progress-label {
    color: #0F172A;
    font-weight: 850;
    font-size: .82rem;
    line-height: 1.2;
}
.rb-progress-copy {
    color: #64748B;
    font-size: .74rem;
    line-height: 1.25;
    margin-top: 3px;
}
@media (max-width: 900px) {
    .rb-progress-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}


/* Keep radio/segmented choices side-by-side for short two-option selectors */
div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    gap: 10px !important;
    align-items: center !important;
}
div[role="radiogroup"] label {
    margin-right: 0 !important;
}

</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
.rb-roadmap {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1px solid #E2E8F0;
    border-radius: 22px;
    padding: 22px 22px 20px 22px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
    margin-bottom: 18px;
}
.rb-roadmap-title {
    font-size: 1.55rem;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 8px;
}
.rb-roadmap-sub {
    color: #64748B;
    font-size: 0.98rem;
    margin-bottom: 16px;
}
.rb-roadmap-grid {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 10px;
    align-items: start;
}
.rb-step {
    text-align: center;
    position: relative;
    padding-top: 4px;
}
.rb-step-num {
    width: 42px;
    height: 42px;
    border-radius: 999px;
    margin: 0 auto 10px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 800;
    font-size: 1rem;
    background: #3B82F6;
    box-shadow: 0 10px 22px rgba(59, 130, 246, 0.18);
}
.rb-step.done .rb-step-num { background: #16A34A; box-shadow: 0 10px 22px rgba(22, 163, 74, 0.18); }
.rb-step-title {
    color: #0F172A;
    font-weight: 700;
    font-size: 0.98rem;
    line-height: 1.25;
    margin-bottom: 4px;
}
.rb-step-copy {
    color: #64748B;
    font-size: 0.88rem;
    line-height: 1.35;
}
.rb-step-line {
    height: 3px;
    background: linear-gradient(90deg, #22C55E 0%, #3B82F6 100%);
    border-radius: 999px;
    margin: 0 0 16px 0;
}
.rb-modern-card {
    border: 1px solid #E2E8F0;
    border-radius: 22px;
    background: #FFFFFF;
    padding: 20px;
    min-height: 180px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
}
.rb-modern-card h4 {
    margin: 0;
    color: #0F172A;
    font-size: 1rem;
    font-weight: 800;
}
.rb-modern-muted {
    color: #64748B;
    font-size: 0.95rem;
}
.rb-modern-value {
    font-size: 2rem;
    font-weight: 800;
    color: #0F172A;
    margin: 14px 0 4px 0;
}
.rb-modern-value.green { color: #16A34A; }
.rb-pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: #E8F5EC;
    color: #15803D;
    font-size: 0.85rem;
    font-weight: 700;
    margin-top: 4px;
}
.rb-next-step {
    border: 1px solid #D9F0E0;
    border-radius: 22px;
    background: linear-gradient(180deg, #F7FCF8 0%, #EEF9F1 100%);
    padding: 22px;
    min-height: 260px;
}
.rb-next-step-title {
    color: #166534;
    font-size: 1.45rem;
    font-weight: 800;
    margin-bottom: 8px;
}
.rb-section-title {
    color: #0F172A;
    font-size: 1.35rem;
    font-weight: 800;
    margin-top: 8px;
    margin-bottom: 10px;
}
.rb-premium-card-compact {
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    background: #FFFFFF;
    padding: 16px;
    min-height: 280px;
    height: 280px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}
.rb-premium-icon {
    width: 36px;
    height: 36px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #F1F5F9;
    font-size: 18px;
    margin-bottom: 10px;
}
.rb-premium-title {
    color: #0F172A;
    font-size: 0.98rem;
    font-weight: 800;
    line-height: 1.25;
    margin-bottom: 6px;
}
.rb-premium-copy {
    color: #64748B;
    font-size: 0.9rem;
    line-height: 1.4;
    margin-bottom: 8px;
    flex: 1 1 auto;
}
.rb-premium-badge {
    display: inline-block;
    width: fit-content;
    padding: 4px 10px;
    border-radius: 999px;
    background: #EEF2FF;
    color: #1D4ED8;
    font-size: 0.76rem;
    font-weight: 700;
    margin-top: auto;
}
@media (max-width: 1100px) {
    .rb-roadmap-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 700px) {
    .rb-roadmap-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
/* =========================
   Modern SaaS button system
   ========================= */
div.stButton > button {
    width: 100%;
    min-height: 54px;
    border-radius: 16px;
    border: 1px solid rgba(59, 130, 246, 0.12);
    background: linear-gradient(180deg, #3B82F6 0%, #2563EB 100%);
    color: #ffffff;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    padding: 0.85rem 1.1rem;
    box-shadow:
        0 12px 24px rgba(37, 99, 235, 0.18),
        inset 0 1px 0 rgba(255, 255, 255, 0.16);
    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        filter 0.18s ease,
        background 0.18s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    filter: brightness(1.02);
    box-shadow:
        0 16px 28px rgba(37, 99, 235, 0.22),
        inset 0 1px 0 rgba(255, 255, 255, 0.18);
}

div.stButton > button:active {
    transform: translateY(0px);
    box-shadow:
        0 8px 18px rgba(37, 99, 235, 0.18),
        inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

div.stButton > button:focus {
    outline: none !important;
    box-shadow:
        0 0 0 4px rgba(59, 130, 246, 0.16),
        0 16px 28px rgba(37, 99, 235, 0.20);
}

/* Secondary buttons */
div.stButton > button[kind="secondary"] {
    background: #ffffff;
    color: #0F172A;
    border: 1px solid rgba(148, 163, 184, 0.35);
    box-shadow:
        0 8px 18px rgba(15, 23, 42, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

div.stButton > button[kind="secondary"]:hover {
    background: #F8FAFC;
    color: #0F172A;
    border-color: rgba(148, 163, 184, 0.45);
    box-shadow:
        0 12px 24px rgba(15, 23, 42, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.85);
}

div.stButton > button[kind="secondary"]:focus {
    box-shadow:
        0 0 0 4px rgba(148, 163, 184, 0.14),
        0 12px 24px rgba(15, 23, 42, 0.08);
}

/* Slightly cleaner spacing for stacked button rows */
div.stButton {
    margin-top: 0.15rem;
    margin-bottom: 0.15rem;
}

/* Optional: help nav / section buttons feel more SaaS */
button p {
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)



# -----------------------------
# Visual polish / design system
# -----------------------------
def inject_app_styles():
    st.markdown("""
    <style>
    :root {
        --rb-primary: #0f62fe;
        --rb-primary-dark: #0842a0;
        --rb-teal: #0891b2;
        --rb-green: #15803d;
        --rb-ink: #0f172a;
        --rb-muted: #64748b;
        --rb-line: #e2e8f0;
        --rb-soft: #f8fafc;
        --rb-card: #ffffff;
        --rb-warn-bg: #fffbeb;
        --rb-warn-border: #fbbf24;
    }

    .block-container {
        padding-top: 1.3rem;
        padding-bottom: 3rem;
        max-width: 1320px;
    }

    h1, h2, h3 {
        color: var(--rb-ink);
        letter-spacing: -0.035em;
    }

    p, div, label, span {
        font-size: 1rem;
    }

    div[data-testid="stTabs"] button {
        min-height: 46px;
        border-radius: 14px 14px 0 0;
        font-weight: 650;
        color: #334155;
        padding-left: 16px;
        padding-right: 16px;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        background: #eff6ff;
        color: #0f62fe;
        border-bottom: 3px solid #0f62fe;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 18px 18px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.055);
        min-height: 142px;
    }

    div[data-testid="stMetricLabel"] p {
        color: #475569;
        font-weight: 700;
    }

    div[data-testid="stMetricValue"] {
        color: #0f172a;
        font-weight: 850;
    }

    .rb-hero {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 20px;
        border: 1px solid #e5e7eb;
        border-radius: 22px;
        padding: 24px 26px;
        background: linear-gradient(135deg, #ffffff 0%, #f8fbff 70%, #ecfeff 100%);
        box-shadow: 0 10px 35px rgba(15, 23, 42, 0.06);
        margin-bottom: 18px;
    }

    .rb-logo-row {
        display: flex;
        gap: 16px;
        align-items: center;
    }

    .rb-logo {
        width: 58px;
        height: 58px;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #0f62fe, #14b8a6);
        color: white;
        font-size: 30px;
        font-weight: 900;
        box-shadow: 0 10px 22px rgba(15, 98, 254, 0.22);
    }

    .rb-hero-title {
        font-size: 2.1rem;
        line-height: 1.1;
        font-weight: 850;
        color: var(--rb-ink);
        margin: 0 0 6px 0;
    }

    .rb-hero-subtitle {
        max-width: 900px;
        color: #64748b;
        font-size: 0.98rem;
        line-height: 1.45;
        margin: 0;
    }

    .rb-account-chip {
        white-space: nowrap;
        border: 1px solid #dbeafe;
        border-radius: 16px;
        background: #ffffff;
        padding: 12px 15px;
        min-width: 150px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
        color: #0f172a;
        font-weight: 800;
        text-align: center;
    }

    .rb-account-chip small {
        display: block;
        margin-top: 3px;
        color: #0f62fe;
        font-weight: 800;
    }

    .rb-page-title {
        font-size: 2rem;
        line-height: 1.15;
        font-weight: 850;
        color: var(--rb-ink);
        margin: 18px 0 4px 0;
    }

    .rb-accent-line {
        width: 34px;
        height: 4px;
        border-radius: 999px;
        background: linear-gradient(90deg, #0f62fe, #14b8a6);
        margin: 8px 0 12px 0;
    }

    .rb-muted {
        color: var(--rb-muted);
        line-height: 1.45;
    }

    .rb-banner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        border: 1px solid #bfdbfe;
        border-radius: 16px;
        background: #eff6ff;
        padding: 16px 18px;
        margin: 22px 0 20px 0;
    }

    .rb-banner-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .rb-info-dot {
        width: 38px;
        height: 38px;
        min-width: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #0f62fe;
        color: white;
        font-weight: 900;
        font-size: 1.15rem;
    }

    .rb-banner-title {
        font-weight: 850;
        color: #0f2f6a;
        margin-bottom: 2px;
    }

    .rb-btn-fake {
        display: inline-block;
        border-radius: 12px;
        background: #0f62fe;
        color: #ffffff !important;
        padding: 10px 16px;
        font-weight: 850;
        text-decoration: none !important;
        box-shadow: 0 8px 18px rgba(15, 98, 254, 0.2);
    }

    .rb-card-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 18px;
        margin: 8px 0 22px 0;
    }

    .rb-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.055);
        min-height: 150px;
    }

    .rb-card-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
    }

    .rb-card-label {
        color: #475569;
        font-weight: 800;
        font-size: 0.98rem;
    }

    .rb-icon {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        background: #e0f2fe;
    }

    .rb-card-value {
        color: #0f172a;
        font-size: 1.9rem;
        line-height: 1.05;
        font-weight: 900;
        margin-top: 18px;
    }

    .rb-card-note {
        color: #64748b;
        font-size: 0.96rem;
        line-height: 1.45;
        margin-top: 12px;
    }

    .rb-warning-panel {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
        border: 1px solid var(--rb-warn-border);
        border-radius: 17px;
        background: linear-gradient(135deg, #fffbeb 0%, #fff7ed 100%);
        padding: 18px 22px;
        margin: 10px 0 22px 0;
        box-shadow: 0 8px 20px rgba(251, 191, 36, 0.12);
    }

    .rb-warning-left {
        display: flex;
        gap: 16px;
        align-items: center;
    }

    .rb-warning-icon {
        width: 46px;
        height: 46px;
        min-width: 46px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #fef3c7;
        color: #d97706;
        font-size: 1.4rem;
    }

    .rb-warning-title {
        font-weight: 900;
        color: #92400e;
        margin-bottom: 3px;
    }

    .rb-outline-btn {
        display: inline-block;
        border: 1px solid #f59e0b;
        background: #ffffff;
        color: #0f172a !important;
        border-radius: 12px;
        padding: 10px 14px;
        text-decoration: none !important;
        font-weight: 850;
        white-space: nowrap;
    }

    .rb-lower-grid {
        display: grid;
        grid-template-columns: 1.35fr 1fr;
        gap: 22px;
        margin-top: 8px;
    }

    .rb-panel {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        padding: 22px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.055);
    }

    .rb-panel-title {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.35rem;
        font-weight: 900;
        color: #0f172a;
        margin-bottom: 15px;
        padding-bottom: 14px;
        border-bottom: 1px solid #e5e7eb;
    }

    .rb-step {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin: 12px 0;
        color: #334155;
        line-height: 1.35;
    }

    .rb-step-num {
        width: 25px;
        height: 25px;
        min-width: 25px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #0f62fe;
        color: #ffffff;
        font-size: 0.85rem;
        font-weight: 900;
    }

    .rb-step b {
        color: #0f62fe;
    }

    .rb-qs-step {
        display: grid;
        grid-template-columns: 38px 1fr;
        align-items: start;
        gap: 12px;
        margin: 14px 0;
        color: #334155;
        line-height: 1.4;
    }

    .rb-qs-step-num {
        width: 30px;
        height: 30px;
        min-width: 30px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #2563eb;
        color: #ffffff;
        font-size: 0.88rem;
        font-weight: 900;
        margin-top: 1px;
    }

    .rb-qs-step-text {
        color: #334155;
        font-size: 1rem;
        line-height: 1.42;
        padding-top: 2px;
    }

    .rb-next-box {
        border: 1px solid #86efac;
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfeff 100%);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 14px;
    }

    .rb-next-heading {
        color: #15803d;
        font-weight: 900;
        font-size: 1.08rem;
        margin-bottom: 5px;
    }

    .rb-green-btn {
        display: inline-block;
        border-radius: 12px;
        background: #15803d;
        color: white !important;
        padding: 10px 18px;
        font-weight: 850;
        text-decoration: none !important;
        margin-top: 12px;
    }

    .rb-tips {
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 14px 16px;
        color: #475569;
        background: #fbfdff;
    }

    .rb-tips-title {
        font-weight: 900;
        color: #0f62fe;
        margin-bottom: 6px;
    }

    .account-bar {
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 18px;
        background: #ffffff;
        box-shadow: 0 1px 8px rgba(15, 23, 42, 0.04);
    }

    .account-pill {
        display: inline-block;
        padding: 5px 11px;
        border-radius: 999px;
        background: #dcfce7;
        color: #15803d;
        font-size: 0.82rem;
        font-weight: 800;
        margin-right: 8px;
    }

    .rb-auth-panel {
        border: 1px solid #bfdbfe;
        border-radius: 16px;
        background: #f8fbff;
        padding: 16px 18px;
        margin: 4px 0 14px 0;
    }

    .rb-auth-title {
        font-weight: 900;
        color: #0f2f6a;
        font-size: 1.05rem;
        margin-bottom: 4px;
    }

    div.stButton > button[kind="secondary"] {
        border-radius: 12px;
        background: #0f62fe;
        color: #ffffff;
        border: 1px solid #0f62fe;
        font-weight: 850;
        box-shadow: 0 8px 18px rgba(15, 98, 254, 0.20);
    }

    div.stButton > button[kind="secondary"]:hover {
        background: #004fd6;
        color: #ffffff;
        border-color: #004fd6;
    }



    /* Better tabs and page polish */
    div[data-testid="stTabs"] {
        margin-top: 10px;
    }

    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 10px;
        background: linear-gradient(180deg, #f8fbff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 8px;
        overflow-x: auto;
        scrollbar-width: none;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.85), 0 8px 20px rgba(15, 23, 42, 0.04);
    }

    div[data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none;
    }

    div[data-testid="stTabs"] button {
        min-height: 42px;
        border-radius: 12px;
        border: 1px solid transparent;
        font-weight: 750;
        color: #334155;
        padding: 0.45rem 0.95rem;
        background: rgba(255,255,255,0.92);
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
        white-space: nowrap;
        flex: 0 0 auto;
        font-size: 0.93rem;
        transition: all 0.18s ease;
    }

    div[data-testid="stTabs"] button:hover {
        color: #0f62fe;
        border-color: #dbeafe;
        background: #ffffff;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #0f62fe 0%, #3b82f6 55%, #14b8a6 100%);
        color: #ffffff;
        border-color: transparent;
        box-shadow: 0 10px 22px rgba(15, 98, 254, 0.24);
    }

    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        display: none;
    }

    div[data-testid="stForm"] {
        background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
        border: 1px solid #e2e8f0;
        border-radius: 22px;
        padding: 1.25rem 1.15rem 0.8rem 1.15rem;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.055);
        margin-top: 0.65rem;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        background: #ffffff;
        overflow: hidden;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
    }

    details {
        border-radius: 16px;
    }

    summary {
        font-weight: 750;
        color: #0f172a;
    }

    label[data-testid="stWidgetLabel"] p {
        color: #334155;
        font-weight: 700;
        letter-spacing: -0.01em;
    }

    div[data-baseweb="input"] {
        border-radius: 14px !important;
        border: 1px solid #dbe3ef !important;
        background: #fbfdff !important;
        box-shadow: inset 0 1px 2px rgba(15,23,42,0.03);
    }

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"] > div:focus-within,
    textarea:focus,
    input:focus {
        border-color: #93c5fd !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    }

    div[data-baseweb="select"] > div {
        border-radius: 14px !important;
        border: 1px solid #dbe3ef !important;
        background: #fbfdff !important;
        min-height: 44px;
    }

    textarea, input {
        border-radius: 14px !important;
    }

    div[data-testid="stNumberInput"] button {
        border-radius: 10px !important;
    }

    div[data-testid="stRadio"] [role="radiogroup"] {
        gap: 10px;
    }

    div[data-testid="stRadio"] label {
        background: #ffffff;
        border: 1px solid #dbe3ef;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
    }

    div[data-testid="stAlert"] {
        border-radius: 16px;
        border: 1px solid #e2e8f0;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }

    .rb-page-shell {
        border: 1px solid #e2e8f0;
        border-radius: 22px;
        padding: 1.15rem 1.2rem;
        background: linear-gradient(135deg, #ffffff 0%, #f8fbff 70%, #f0fdfa 100%);
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
        margin: 0.4rem 0 1rem 0;
    }

    .rb-page-shell-row {
        display: flex;
        gap: 14px;
        align-items: flex-start;
    }

    .rb-page-icon {
        width: 48px;
        height: 48px;
        min-width: 48px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        background: linear-gradient(135deg, #dbeafe 0%, #ccfbf1 100%);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.85);
    }

    .rb-page-kicker {
        display: inline-block;
        background: #eff6ff;
        color: #0f62fe;
        border: 1px solid #dbeafe;
        border-radius: 999px;
        padding: 0.18rem 0.55rem;
        font-size: 0.78rem;
        font-weight: 800;
        margin-bottom: 0.45rem;
    }

    .rb-page-title-lg {
        color: #0f172a;
        font-size: 1.65rem;
        line-height: 1.15;
        font-weight: 850;
        margin-bottom: 0.3rem;
        letter-spacing: -0.03em;
    }

    .rb-page-desc {
        color: #64748b;
        line-height: 1.45;
        max-width: 980px;
    }

    .rb-soft-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(15,98,254,0.10), rgba(20,184,166,0.10), rgba(15,23,42,0.02));
        margin: 1rem 0 0.4rem 0;
    }

    .rb-nav-wrap {
        margin: 10px 0 18px 0;
    }

    .rb-nav-wrap div[data-testid="stRadio"] [role="radiogroup"] {
        display: flex;
        flex-wrap: nowrap;
        gap: 10px;
        overflow-x: auto;
        padding: 8px;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        background: linear-gradient(180deg, #f8fbff 0%, #f8fafc 100%);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.9), 0 8px 20px rgba(15,23,42,0.04);
        scrollbar-width: thin;
    }

    .rb-nav-wrap div[data-testid="stRadio"] label {
        flex: 0 0 auto;
        margin: 0;
        border: 1px solid #dbe3ef;
        border-radius: 14px;
        background: #ffffff;
        padding: 0.58rem 0.95rem;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
        transition: all 0.18s ease;
    }

    .rb-nav-wrap div[data-testid="stRadio"] label:hover {
        border-color: #93c5fd;
        background: #eff6ff;
    }

    .rb-nav-wrap div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #0f62fe 0%, #3b82f6 55%, #14b8a6 100%);
        border-color: transparent;
        color: #ffffff !important;
        box-shadow: 0 10px 22px rgba(15,98,254,0.24);
    }

    .rb-nav-wrap div[data-testid="stRadio"] label:has(input:checked) p,
    .rb-nav-wrap div[data-testid="stRadio"] label:has(input:checked) span {
        color: #ffffff !important;
    }





    /* Phase 2 navigation polish: cleaner real-tabs look, no radio dots */
    .rb-nav-wrap {
        margin: 18px 0 30px 0 !important;
        padding: 0 !important;
    }

    .rb-nav-wrap div[data-testid="stRadio"] [role="radiogroup"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 4px 8px !important;
        overflow-x: visible !important;
        padding: 0 0 0 0 !important;
        border: 0 !important;
        border-bottom: 1px solid #dbe3ef !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        scrollbar-width: none !important;
    }

    .rb-nav-wrap div[data-testid="stRadio"] [role="radiogroup"]::-webkit-scrollbar {
        display: none !important;
    }

    .rb-nav-wrap div[data-testid="stRadio"] label {
        position: relative !important;
        flex: 0 0 auto !important;
        margin: 0 !important;
        border: 0 !important;
        border-radius: 13px 13px 0 0 !important;
        background: transparent !important;
        padding: 0.74rem 0.95rem 0.82rem 0.95rem !important;
        box-shadow: none !important;
        color: #475569 !important;
        transition: background 0.16s ease, color 0.16s ease, transform 0.16s ease !important;
    }

    /* Hide Streamlit's radio circle so this looks like app navigation, not form controls */
    .rb-nav-wrap div[data-testid="stRadio"] label > div:first-child {
        display: none !important;
    }

    .rb-nav-wrap div[data-testid="stRadio"] input[type="radio"] {
        display: none !important;
    }

    .rb-nav-wrap div[data-testid="stRadio"] label p,
    .rb-nav-wrap div[data-testid="stRadio"] label span {
        font-size: 0.94rem !important;
        font-weight: 750 !important;
        color: #475569 !important;
        white-space: nowrap !important;
        line-height: 1.2 !important;
    }

    .rb-nav-wrap div[data-testid="stRadio"] label:hover {
        border: 0 !important;
        background: #f1f5f9 !important;
        color: #0f62fe !important;
        transform: translateY(-1px) !important;
    }

    .rb-nav-wrap div[data-testid="stRadio"] label:hover p,
    .rb-nav-wrap div[data-testid="stRadio"] label:hover span {
        color: #0f62fe !important;
    }

    .rb-nav-wrap div[data-testid="stRadio"] label:has(input:checked) {
        background: #eff6ff !important;
        border: 0 !important;
        color: #0f62fe !important;
        box-shadow: none !important;
    }

    .rb-nav-wrap div[data-testid="stRadio"] label:has(input:checked)::after {
        content: "";
        position: absolute;
        left: 12px;
        right: 12px;
        bottom: -1px;
        height: 4px;
        border-radius: 999px 999px 0 0;
        background: linear-gradient(90deg, #0f62fe 0%, #14b8a6 100%);
    }

    .rb-nav-wrap div[data-testid="stRadio"] label:has(input:checked) p,
    .rb-nav-wrap div[data-testid="stRadio"] label:has(input:checked) span {
        color: #0f62fe !important;
        font-weight: 900 !important;
    }

    @media (max-width: 900px) {
        .rb-nav-wrap div[data-testid="stRadio"] [role="radiogroup"] {
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            padding-bottom: 3px !important;
        }
        .rb-nav-wrap div[data-testid="stRadio"] label {
            padding: 0.78rem 0.9rem 0.86rem 0.9rem !important;
        }
    }




    /* Phase 2.1: modern navigation and segmented controls */
    .rb-nav-intro {
        margin-top: 1.1rem;
        margin-bottom: 0.45rem;
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 850;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .rb-nav-wrap {
        margin: 0.3rem 0 2rem 0 !important;
        padding: 0.8rem !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 22px !important;
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%) !important;
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.055) !important;
    }

    .rb-nav-wrap div[data-testid="stHorizontalBlock"] {
        gap: 0.55rem !important;
        margin-bottom: 0.55rem !important;
    }

    .rb-nav-wrap div[data-testid="stHorizontalBlock"]:last-child {
        margin-bottom: 0 !important;
    }

    .rb-nav-wrap div.stButton > button {
        min-height: 46px !important;
        border-radius: 15px !important;
        border: 1px solid #dbe3ef !important;
        background: #ffffff !important;
        color: #334155 !important;
        font-weight: 800 !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
        transition: all 0.16s ease !important;
        white-space: nowrap !important;
    }

    .rb-nav-wrap div.stButton > button:hover {
        border-color: #93c5fd !important;
        background: #eff6ff !important;
        color: #0f62fe !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 18px rgba(15, 98, 254, 0.10) !important;
    }

    .rb-nav-wrap div.stButton > button:disabled,
    .rb-nav-wrap div.stButton > button[disabled] {
        opacity: 1 !important;
        cursor: default !important;
        color: #ffffff !important;
        border-color: transparent !important;
        background: linear-gradient(135deg, #0f62fe 0%, #3b82f6 55%, #14b8a6 100%) !important;
        box-shadow: 0 12px 24px rgba(15, 98, 254, 0.24) !important;
    }

    /* Sleek segmented radio controls for Login/Create Account, Budget mode, Income mode, etc. */
    div[data-testid="stRadio"] [role="radiogroup"] {
        display: inline-flex !important;
        flex-wrap: wrap !important;
        gap: 0.45rem !important;
        padding: 0.35rem !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 999px !important;
        background: #f8fafc !important;
        box-shadow: inset 0 1px 1px rgba(15, 23, 42, 0.03) !important;
    }

    div[data-testid="stRadio"] label {
        position: relative !important;
        margin: 0 !important;
        border: 0 !important;
        border-radius: 999px !important;
        background: transparent !important;
        padding: 0.48rem 0.9rem !important;
        box-shadow: none !important;
        transition: all 0.16s ease !important;
        cursor: pointer !important;
    }

    div[data-testid="stRadio"] label > div:first-child {
        display: none !important;
    }

    div[data-testid="stRadio"] input[type="radio"] {
        display: none !important;
    }

    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span {
        color: #475569 !important;
        font-weight: 800 !important;
        white-space: nowrap !important;
    }

    div[data-testid="stRadio"] label:hover {
        background: #eef6ff !important;
    }

    div[data-testid="stRadio"] label:hover p,
    div[data-testid="stRadio"] label:hover span {
        color: #0f62fe !important;
    }

    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #0f62fe 0%, #3b82f6 55%, #14b8a6 100%) !important;
        box-shadow: 0 8px 18px rgba(15, 98, 254, 0.20) !important;
    }

    div[data-testid="stRadio"] label:has(input:checked) p,
    div[data-testid="stRadio"] label:has(input:checked) span {
        color: #ffffff !important;
        font-weight: 900 !important;
    }

    @media (max-width: 900px) {
        .rb-nav-wrap {
            padding: 0.65rem !important;
        }
        .rb-nav-wrap div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        .rb-nav-wrap div.stButton > button {
            min-height: 44px !important;
            font-size: 0.88rem !important;
        }
    }

    /* Make the top-right account action look like a real clickable account card */
    div[data-testid="column"] div.stButton > button {
        border-radius: 16px;
    }

    @media (max-width: 900px) {
        .rb-hero, .rb-banner, .rb-warning-panel { flex-direction: column; align-items: stretch; }
        .rb-card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .rb-lower-grid { grid-template-columns: 1fr; }
        .rb-hero-title { font-size: 1.55rem; }
    }

    @media (max-width: 560px) {
        .rb-card-grid { grid-template-columns: 1fr; }
    }


    /* Premium product polish */
    .rb-premium-badge { display:inline-flex; align-items:center; gap:6px; background:linear-gradient(135deg,#fef3c7,#fde68a); color:#92400e; border:1px solid #fcd34d; border-radius:999px; padding:4px 10px; font-size:0.78rem; font-weight:900; letter-spacing:.01em; }
    .rb-insight-card { border:1px solid #bfdbfe; border-left:6px solid #0f62fe; border-radius:20px; background:linear-gradient(135deg,#eff6ff 0%,#ffffff 72%,#ecfeff 100%); box-shadow:0 12px 28px rgba(15,23,42,.06); padding:18px 20px; margin:16px 0 20px 0; }
    .rb-insight-kicker { color:#0f62fe; font-weight:900; font-size:.82rem; text-transform:uppercase; letter-spacing:.08em; margin-bottom:6px; }
    .rb-insight-title { color:#0f172a; font-size:1.12rem; font-weight:900; margin-bottom:6px; }
    .rb-insight-copy { color:#475569; line-height:1.45; }
    .rb-lock-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin:16px 0 22px 0; }
    .rb-lock-card { background:#fff; border:1px solid #e2e8f0; border-radius:18px; padding:16px; box-shadow:0 8px 22px rgba(15,23,42,.055); position:relative; min-height:128px; }
    .rb-lock-card:before { content:"Premium"; position:absolute; right:14px; top:12px; background:#fef3c7; color:#92400e; border:1px solid #fde68a; border-radius:999px; padding:3px 8px; font-size:.72rem; font-weight:900; }
    .rb-lock-icon { font-size:1.45rem; margin-bottom:6px; }
    .rb-lock-title { font-weight:900; color:#0f172a; margin-bottom:4px; padding-right:80px; }
    .rb-lock-copy { color:#64748b; font-size:.9rem; line-height:1.38; }
    .rb-meter-grid { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:12px; margin:16px 0 22px 0; }
    .rb-meter-card { border:1px solid #e2e8f0; border-radius:18px; background:#fff; padding:14px; box-shadow:0 8px 20px rgba(15,23,42,.045); }
    .rb-meter-label { font-weight:900; color:#334155; font-size:.86rem; margin-bottom:8px; }
    .rb-meter-value { font-size:1.45rem; font-weight:950; color:#0f172a; margin-bottom:8px; }
    .rb-meter-track { height:9px; border-radius:999px; background:#e2e8f0; overflow:hidden; }
    .rb-meter-fill { height:100%; border-radius:999px; background:linear-gradient(90deg,#0f62fe,#14b8a6); }
    .rb-bucket-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin:14px 0 18px 0; }
    .rb-bucket-card { border:1px solid #dbeafe; border-radius:20px; background:linear-gradient(180deg,#ffffff,#f8fbff); padding:18px; box-shadow:0 10px 26px rgba(15,23,42,.055); }
    .rb-bucket-num { width:36px; height:36px; border-radius:12px; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#0f62fe,#14b8a6); color:#fff; font-weight:950; margin-bottom:10px; }
    .rb-bucket-title { font-weight:950; color:#0f172a; margin-bottom:4px; }
    .rb-bucket-amount { font-size:1.35rem; font-weight:950; color:#0f62fe; margin:6px 0; }
    .rb-bucket-copy { color:#64748b; font-size:.92rem; line-height:1.4; }
    @media (max-width: 900px) { .rb-lock-grid,.rb-meter-grid,.rb-bucket-grid { grid-template-columns:1fr; } }

    </style>
    """, unsafe_allow_html=True)


inject_app_styles()


# -----------------------------
# Modern blue slider styling
# -----------------------------
st.markdown("""
<style>
/* Modern blue/teal slider polish */
div[data-testid="stSlider"] {
    padding: 0.25rem 0.15rem 0.55rem 0.15rem;
}

div[data-testid="stSlider"] [data-baseweb="slider"] {
    padding-top: 0.8rem !important;
    padding-bottom: 0.25rem !important;
}

/* Slider track container */
div[data-testid="stSlider"] [data-baseweb="slider"] > div {
    min-height: 10px !important;
}

/* Thumb / handle */
div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    width: 22px !important;
    height: 22px !important;
    border-radius: 999px !important;
    background: linear-gradient(135deg, #2563EB 0%, #14B8A6 100%) !important;
    border: 4px solid #FFFFFF !important;
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.28) !important;
}

/* Thumb focus state */
div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"]:focus {
    outline: none !important;
    box-shadow: 0 0 0 5px rgba(37, 99, 235, 0.16), 0 8px 18px rgba(37, 99, 235, 0.28) !important;
}

/* Slider value bubble/text */
div[data-testid="stSlider"] [data-testid="stThumbValue"],
div[data-testid="stSlider"] [data-testid="stTickBarMin"],
div[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: #2563EB !important;
    font-weight: 900 !important;
}

/* Try to override the default red active range in recent Streamlit builds */
div[data-testid="stSlider"] [data-baseweb="slider"] div[style*="background"] {
    border-radius: 999px !important;
}

/* Visual card wrapper around each slider so it feels more premium */
div[data-testid="stSlider"] > label {
    margin-bottom: 0.3rem !important;
}

/* Small note: the exact inner slider DOM can vary by Streamlit version.
   These selectors safely improve the handle/value across versions. */
</style>
""", unsafe_allow_html=True)


def auth_box():
    """Keep authentication state available without rendering a second account/logout bar.

    The visible account controls live in the hero area. Rendering another Logout
    button here can create duplicate Streamlit element IDs when a user is signed in.
    """
    if "user" not in st.session_state:
        st.session_state.user = None
    if "show_auth_form" not in st.session_state:
        st.session_state.show_auth_form = False
    return st.session_state.user


def render_auth_form():
    """Sign-in/create-account form shown only after the Home blue button is clicked."""
    st.markdown("""
    <div class="rb-auth-panel">
      <div class="rb-auth-title">Sign in or create an account</div>
      <div class="rb-muted">Save blueprints, reload plans, and compare retirement options later.</div>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio(
        "Account action",
        ["Login", "Create Account"],
        horizontal=True,
        key="home_auth_mode"
    )

    c1, c2, c3 = st.columns([2, 2, 1])

    with c1:
        email = st.text_input("Email", key="home_auth_email")
    with c2:
        password = st.text_input("Password", type="password", key="home_auth_password")
    with c3:
        st.write("")
        st.write("")
        action_clicked = st.button(mode, use_container_width=True, key="home_auth_submit")

    if action_clicked:
        if not email or not password:
            st.error("Enter both email and password.")
        elif mode == "Create Account":
            try:
                supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                st.success("Account created. Check email if confirmation is required, then log in.")
            except Exception as e:
                st.error(f"Create account failed: {e}")
        else:
            try:
                res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user = res.user
                st.session_state.show_auth_form = False
                st.success("Logged in.")
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")



user = auth_box()

# Account controls
# Keep sign-in visible at the very top so users can save and reload blueprints.
acct_left, acct_right = st.columns([5.5, 1.4])
with acct_right:
    if user:
        user_email = getattr(user, "email", "Signed in")
        st.caption(f"Signed in as {user_email}")
        if st.button("Sign out", use_container_width=True, key="top_sign_out"):
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
            st.session_state.user = None
            st.session_state.show_auth_form = False
            st.rerun()
    else:
        if st.button("Sign In / Create Account", use_container_width=True, key="top_open_auth"):
            st.session_state.show_auth_form = not st.session_state.get("show_auth_form", False)

if not user and st.session_state.get("show_auth_form"):
    render_auth_form()

# Header / hero area
hero_left = st.container()

with hero_left:
    st.markdown("""
    <div class="rb-hero" style="margin-top: 8px; margin-bottom: 10px;">
      <div class="rb-logo-row">
        <div class="rb-logo">↗</div>
        <div>
          <div class="rb-hero-title">Retirement Blueprint 101</div>
          <p class="rb-hero-subtitle">See when you can retire, how long your money may last, and what to improve before you make the leap.</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)



def money(x):
    try:
        return f"${float(x):,.0f}"
    except Exception:
        return "$0"




def calculate_risk_scores(summary):
    sequence_risk = max(0, min(100, round(summary["rough_wr"] * 1200)))
    tax_risk = 85 if summary["traditional"] > summary["roth"] * 4 else 55
    healthcare_risk = 75 if summary["retire_age"] < 65 else 40
    longevity_risk = 70 if summary["end_age"] >= 95 else 45
    income_risk = max(0, 100 - round(summary["income_coverage"] * 100))

    return {
        "Sequence Risk": sequence_risk,
        "Tax Risk": tax_risk,
        "Healthcare Risk": healthcare_risk,
        "Longevity Risk": longevity_risk,
        "Income Stability Risk": income_risk,
    }


def explain_scenario_changes(current_summary, compare_summary):
    changes = []

    score_diff = current_summary["score"] - compare_summary["score"]

    if current_summary["retire_age"] > compare_summary["retire_age"]:
        changes.append(
            f"Retirement age increased from {compare_summary['retire_age']} to "
            f"{current_summary['retire_age']}, improving portfolio longevity."
        )

    elif current_summary["retire_age"] < compare_summary["retire_age"]:
        changes.append(
            f"Earlier retirement increased pressure on the portfolio."
        )

    spending_diff = current_summary["monthly_spending"] - compare_summary["monthly_spending"]

    if spending_diff < -500:
        changes.append(
            f"Monthly spending decreased by {money(abs(spending_diff))}, helping improve retirement sustainability."
        )

    elif spending_diff > 500:
        changes.append(
            f"Monthly spending increased by {money(spending_diff)}, creating more max withdrawal rate."
        )

    assets_diff = current_summary["total_assets"] - compare_summary["total_assets"]

    if assets_diff > 50000:
        changes.append(
            f"Total investable assets increased by {money(assets_diff)}, strengthening retirement flexibility."
        )

    income_diff = current_summary["annual_income"] - compare_summary["annual_income"]

    if income_diff > 5000:
        changes.append(
            f"Guaranteed and outside income increased by {money(income_diff)} annually."
        )

    wr_diff = current_summary["rough_wr"] - compare_summary["rough_wr"]

    if wr_diff < -0.005:
        changes.append(
            f"Estimated max withdrawal rate improved from {pct(compare_summary['rough_wr'])} "
            f"to {pct(current_summary['rough_wr'])}."
        )

    elif wr_diff > 0.005:
        changes.append(
            f"Estimated max withdrawal rate increased from {pct(compare_summary['rough_wr'])} "
            f"to {pct(current_summary['rough_wr'])}."
        )

    if not changes:
        changes.append("No major structural differences were detected between these scenarios.")

    headline = (
        f"RTV changed from {compare_summary['score']} to {current_summary['score']} "
        f"({score_diff:+} points)."
    )

    return headline, changes

def pct(x):
    try:
        return f"{float(x):.1%}"
    except Exception:
        return "0.0%"


# -----------------------------
# Social Security Timing Helper
# -----------------------------
def estimate_social_security_by_claim_age(annual_benefit_at_62, claim_age):
    """Approximate annual Social Security benefit if the user-entered amount is the age-62 benefit.

    Assumption: the benefit entered is the age-62 annual benefit. We approximate age 62 as
    70% of full retirement age benefit, full retirement age as 67, and delayed credits as
    8% per year from 67 through 70. This keeps the app educational and avoids needing a
    separate full-retirement-age slider.
    """
    base = max(float(annual_benefit_at_62 or 0), 0)
    age = max(62, min(int(claim_age or 62), 70))
    if base <= 0:
        return 0.0

    fra_benefit = base / 0.70
    if age <= 67:
        factor = 0.70 + ((age - 62) / 5.0) * 0.30
    else:
        factor = 1.00 + ((age - 67) * 0.08)
    return fra_benefit * factor


def social_security_for_age(current_age, start_age, annual_benefit_at_62):
    if int(current_age) < int(start_age or 62):
        return 0.0
    return estimate_social_security_by_claim_age(annual_benefit_at_62, start_age)


def inflation_factor_from_today(projected_age):
    """Inflate today's-dollar amounts from the user's current age to projected_age."""
    current_age = int(st.session_state.get("current_age", projected_age) or projected_age)
    years_from_today = max(int(projected_age or current_age) - current_age, 0)
    return (1 + float(st.session_state.get("inflation", 0.0) or 0.0)) ** years_from_today


def apply_cola_to_social_security(amount, projected_age):
    """Apply a simplified COLA assumption using the app's inflation rate."""
    return float(amount or 0.0) * inflation_factor_from_today(projected_age)


# -----------------------------
# RMD Helper - simplified Uniform Lifetime Table
# -----------------------------
def get_rmd_start_age():
    """Estimate the user's RMD start age from current age and the current calendar year.

    SECURE 2.0 generally moved the RMD start age to 73 for people born 1951-1959
    and 75 for people born 1960 or later. The app does not collect birth date, so
    this uses a best-effort birth-year estimate from current age. Users should
    verify their exact RMD year with a tax professional.
    """
    manual_value = st.session_state.get("rmd_start_age", None)
    if manual_value not in (None, "", 0):
        return int(manual_value)

    current_age = int(st.session_state.get("current_age", 0) or 0)
    if current_age <= 0:
        return 75

    estimated_birth_year = date.today().year - current_age
    if estimated_birth_year >= 1960:
        return 75
    if estimated_birth_year >= 1951:
        return 73
    return 72


def uniform_lifetime_divisor(age):
    """IRS Uniform Lifetime Table divisors for common RMD ages.

    Returns None before RMD age. For very old ages beyond the table below, use
    the last divisor as a conservative fallback.
    """
    divisors = {
        72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0,
        79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0,
        86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8,
        93: 10.1, 94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8,
        100: 6.4, 101: 6.0, 102: 5.6, 103: 5.2, 104: 4.9, 105: 4.6,
        106: 4.3, 107: 4.1, 108: 3.9, 109: 3.7, 110: 3.5, 111: 3.4,
        112: 3.3, 113: 3.1, 114: 3.0, 115: 2.9, 116: 2.8, 117: 2.7,
        118: 2.5, 119: 2.3, 120: 2.0,
    }
    age = int(age or 0)
    if age < get_rmd_start_age():
        return None
    return divisors.get(age, divisors[max(divisors)])


def calculate_required_minimum_distribution(age, traditional_balance):
    """Simplified annual RMD estimate from the pre-tax balance."""
    balance = max(float(traditional_balance or 0), 0)
    divisor = uniform_lifetime_divisor(age)
    if divisor is None or divisor <= 0 or balance <= 0:
        return 0.0
    return min(balance, balance / divisor)


# -----------------------------
# Federal Tax Engine - Phase 2
# -----------------------------
# Update this one section annually when the IRS publishes new brackets.
# Assumptions for Phase 1:
# - Federal ordinary income tax only.
# - Uses standard deduction and marginal brackets.
# - Traditional withdrawals, Roth conversions, and taxable other income are treated as ordinary taxable income.
# - Roth withdrawals, cash/Bucket 1 withdrawals, and taxable brokerage withdrawals are treated as tax-free for this simplified phase.
# - Social Security taxation is estimated using provisional/combined income thresholds.
# - Capital gains, state taxes, itemized deductions, IRMAA, credits, and penalties are future phases.
TAX_TABLES = {
    2025: {
        "single": {
            "label": "Single",
            "standard_deduction": 15750,
            "brackets": [(0, 11925, 0.10), (11925, 48475, 0.12), (48475, 103350, 0.22), (103350, 197300, 0.24), (197300, 250525, 0.32), (250525, 626350, 0.35), (626350, None, 0.37)],
        },
        "married_joint": {
            "label": "Married Filing Jointly",
            "standard_deduction": 31500,
            "brackets": [(0, 23850, 0.10), (23850, 96950, 0.12), (96950, 206700, 0.22), (206700, 394600, 0.24), (394600, 501050, 0.32), (501050, 751600, 0.35), (751600, None, 0.37)],
        },
        "married_separate": {
            "label": "Married Filing Separately",
            "standard_deduction": 15750,
            "brackets": [(0, 11925, 0.10), (11925, 48475, 0.12), (48475, 103350, 0.22), (103350, 197300, 0.24), (197300, 250525, 0.32), (250525, 375800, 0.35), (375800, None, 0.37)],
        },
        "head_of_household": {
            "label": "Head of Household",
            "standard_deduction": 23625,
            "brackets": [(0, 17000, 0.10), (17000, 64850, 0.12), (64850, 103350, 0.22), (103350, 197300, 0.24), (197300, 250500, 0.32), (250500, 626350, 0.35), (626350, None, 0.37)],
        },
    },
    2026: {
        "single": {
            "label": "Single",
            "standard_deduction": 16100,
            "brackets": [(0, 12400, 0.10), (12400, 50400, 0.12), (50400, 105700, 0.22), (105700, 201775, 0.24), (201775, 256225, 0.32), (256225, 640600, 0.35), (640600, None, 0.37)],
        },
        "married_joint": {
            "label": "Married Filing Jointly",
            "standard_deduction": 32200,
            "brackets": [(0, 24800, 0.10), (24800, 100800, 0.12), (100800, 211400, 0.22), (211400, 403550, 0.24), (403550, 512450, 0.32), (512450, 768700, 0.35), (768700, None, 0.37)],
        },
        "married_separate": {
            "label": "Married Filing Separately",
            "standard_deduction": 16100,
            "brackets": [(0, 12400, 0.10), (12400, 50400, 0.12), (50400, 105700, 0.22), (105700, 201775, 0.24), (201775, 256225, 0.32), (256225, 384350, 0.35), (384350, None, 0.37)],
        },
        "head_of_household": {
            "label": "Head of Household",
            "standard_deduction": 24150,
            "brackets": [(0, 17700, 0.10), (17700, 67450, 0.12), (67450, 105700, 0.22), (105700, 201775, 0.24), (201775, 256200, 0.32), (256200, 640600, 0.35), (640600, None, 0.37)],
        },
    },
}

FILING_STATUS_OPTIONS = {
    "single": "Single",
    "married_joint": "Married Filing Jointly",
    "married_separate": "Married Filing Separately",
    "head_of_household": "Head of Household",
}


def get_tax_year():
    year = int(st.session_state.get("tax_year", max(TAX_TABLES.keys())))
    return year if year in TAX_TABLES else max(TAX_TABLES.keys())


def get_filing_status():
    status = st.session_state.get("filing_status", "married_joint")
    return status if status in FILING_STATUS_OPTIONS else "married_joint"


def get_tax_settings(tax_year=None, filing_status=None):
    tax_year = int(tax_year or get_tax_year())
    filing_status = filing_status or get_filing_status()
    if tax_year not in TAX_TABLES:
        tax_year = max(TAX_TABLES.keys())
    if filing_status not in TAX_TABLES[tax_year]:
        filing_status = "married_joint"
    return TAX_TABLES[tax_year][filing_status]


def calculate_marginal_tax(taxable_income, brackets):
    taxable_income = max(float(taxable_income or 0), 0)
    tax = 0.0
    for lower, upper, rate in brackets:
        if taxable_income <= lower:
            break
        top = taxable_income if upper is None else min(taxable_income, upper)
        tax += max(top - lower, 0) * rate
        if upper is not None and taxable_income <= upper:
            break
    return max(tax, 0.0)


def social_security_tax_thresholds(filing_status=None):
    """
    IRS simplified Social Security taxation thresholds.
    Uses combined/provisional income: other income + tax-exempt interest + 50% of Social Security.
    This app does not yet model tax-exempt interest, so provisional income uses ordinary income plus 50% of SS.
    """
    status = filing_status or get_filing_status()
    if status == "married_joint":
        return 32000.0, 44000.0, 6000.0
    if status == "married_separate":
        # Conservative simplified treatment. Actual treatment depends on whether spouses lived together.
        return 0.0, 0.0, 0.0
    return 25000.0, 34000.0, 4500.0


def estimate_taxable_social_security(other_ordinary_income, social_security_income, filing_status=None):
    """
    Estimate federally taxable Social Security benefits using the standard worksheet-style rules.
    The taxable amount is capped at 85% of total Social Security benefits.
    """
    other_income = max(float(other_ordinary_income or 0), 0)
    ss = max(float(social_security_income or 0), 0)
    if ss <= 0:
        return {
            "social_security_income": 0.0,
            "provisional_income": other_income,
            "taxable_social_security": 0.0,
            "taxable_social_security_rate": 0.0,
        }

    base1, base2, first_tier_cap = social_security_tax_thresholds(filing_status)
    provisional_income = other_income + 0.5 * ss

    if provisional_income <= base1:
        taxable_ss = 0.0
    elif provisional_income <= base2:
        taxable_ss = min(0.5 * ss, 0.5 * (provisional_income - base1))
    else:
        taxable_ss = min(0.85 * ss, 0.85 * (provisional_income - base2) + min(first_tier_cap, 0.5 * ss))

    taxable_ss = max(min(taxable_ss, 0.85 * ss), 0.0)
    return {
        "social_security_income": ss,
        "provisional_income": provisional_income,
        "taxable_social_security": taxable_ss,
        "taxable_social_security_rate": taxable_ss / max(ss, 1),
    }


def estimate_federal_tax(gross_ordinary_income, filing_status=None, tax_year=None, social_security_income=0):
    settings = get_tax_settings(tax_year, filing_status)
    ordinary_excluding_ss = max(float(gross_ordinary_income or 0), 0)
    ss_tax = estimate_taxable_social_security(ordinary_excluding_ss, social_security_income, filing_status)
    taxable_social_security = ss_tax["taxable_social_security"]
    gross_taxable_ordinary_income = ordinary_excluding_ss + taxable_social_security
    standard_deduction = float(settings["standard_deduction"])
    taxable_income = max(gross_taxable_ordinary_income - standard_deduction, 0)
    federal_tax = calculate_marginal_tax(taxable_income, settings["brackets"])
    effective_rate = federal_tax / max(gross_taxable_ordinary_income, 1)
    return {
        "gross_ordinary_income": gross_taxable_ordinary_income,
        "ordinary_income_excluding_social_security": ordinary_excluding_ss,
        "social_security_income": float(social_security_income or 0),
        "taxable_social_security": taxable_social_security,
        "taxable_social_security_rate": ss_tax["taxable_social_security_rate"],
        "provisional_income": ss_tax["provisional_income"],
        "standard_deduction": standard_deduction,
        "taxable_income": taxable_income,
        "federal_tax": federal_tax,
        "effective_rate": effective_rate,
        "tax_year": int(tax_year or get_tax_year()),
        "filing_status": filing_status or get_filing_status(),
    }


def incremental_federal_tax(base_ordinary_income, added_ordinary_income, filing_status=None, tax_year=None, social_security_income=0):
    base = estimate_federal_tax(base_ordinary_income, filing_status, tax_year, social_security_income)["federal_tax"]
    after = estimate_federal_tax(float(base_ordinary_income or 0) + float(added_ordinary_income or 0), filing_status, tax_year, social_security_income)["federal_tax"]
    return max(after - base, 0.0)


def net_after_federal_tax(base_ordinary_income, gross_traditional_withdrawal, filing_status=None, tax_year=None, social_security_income=0):
    gross = max(float(gross_traditional_withdrawal or 0), 0)
    return max(gross - incremental_federal_tax(base_ordinary_income, gross, filing_status, tax_year, social_security_income), 0.0)


def gross_traditional_needed_for_net(net_needed, base_ordinary_income, available_traditional, filing_status=None, tax_year=None, social_security_income=0):
    """Find the gross traditional withdrawal needed to net a target amount after federal tax."""
    net_needed = max(float(net_needed or 0), 0)
    available_traditional = max(float(available_traditional or 0), 0)
    if net_needed <= 0 or available_traditional <= 0:
        return 0.0, 0.0

    # If all available traditional dollars still cannot cover the net need, use all available.
    max_net = net_after_federal_tax(base_ordinary_income, available_traditional, filing_status, tax_year, social_security_income)
    if max_net <= net_needed:
        return available_traditional, max_net

    low, high = 0.0, available_traditional
    for _ in range(32):
        mid = (low + high) / 2
        if net_after_federal_tax(base_ordinary_income, mid, filing_status, tax_year, social_security_income) >= net_needed:
            high = mid
        else:
            low = mid

    gross = min(high, available_traditional)
    net = net_after_federal_tax(base_ordinary_income, gross, filing_status, tax_year, social_security_income)
    return gross, net


def tax_assumption_note():
    settings = get_tax_settings()
    return (
        f"Federal tax estimate uses {get_tax_year()} brackets, {settings['label']} filing status, "
        f"and a standard deduction of {money(settings['standard_deduction'])}. "
        "Phase 2 estimates taxable Social Security using provisional income thresholds, applies a simplified Social Security COLA using the app inflation rate, includes taxable Social Security in federal taxable income, and models RMDs using a simplified Uniform Lifetime Table. "
        "Capital gains, state taxes, credits, itemized deductions, IRMAA, and tax penalties are still simplified/future enhancements."
    )


# -----------------------------
# User Help / Tooltips
# -----------------------------
FIELD_HELP = {
    "current_age": "Enter your current age today. This is the starting age for the retirement projection.",
    "retire_age": "Enter the age you want to stop working or begin relying on retirement income.",
    "end_age": "Enter the age the plan should last through. Many people use 90, 95, or 100 for conservative planning.",
    "traditional": "Total balance in pre-tax accounts such as traditional 401(k), traditional IRA, 403(b), or rollover IRA.",
    "roth": "Total balance in Roth accounts such as Roth IRA or Roth 401(k). These are generally tax-free in retirement if rules are met.",
    "taxable": "Total balance in regular brokerage or investment accounts outside retirement accounts.",
    "cash": "Cash, CDs, money market, short-term bonds, or other safer assets used as Bucket 1.",
    "annual_contribution": "How much you expect to add to retirement accounts each year until retirement.",
    "healthcare": "Estimated annual healthcare cost after retirement before Medicare or in addition to Medicare.",
    "user_ss_age": "Age when you expect to start Social Security. Earlier usually means lower benefits; later usually means higher benefits.",
    "user_ss": "Estimated annual Social Security benefit at age 62 in today’s dollars. The app adjusts it upward if you choose a later claiming age.",
    "growth_return": "Expected annual return for growth assets. This is only an assumption, not a guarantee.",
    "safe_return": "Expected annual return for Bucket 1 or safer assets.",
    "inflation": "Expected annual inflation rate used to increase future spending.",
    "annual_conversion": "Annual amount to test moving from traditional retirement accounts into Roth accounts.",
    "bucket1_years": "How many years of spending you want protected in safer assets.",
    "tax_year": "Choose the tax year used for the federal tax bracket estimate. Update the tax table annually as IRS brackets change.",
    "filing_status": "Choose the federal filing status used to estimate ordinary income taxes in the projection.",
    "flat_monthly_spending": "Your estimated monthly lifestyle spending before healthcare. Do not include retirement contributions.",
    "survivor_spending": "Optional annual spending estimate after one spouse passes away.",
    "simple_income": "Other annual income besides Social Security, such as pension, rent, consulting, or part-time work.",
    "simple_income_start": "Age when this other income begins.",
    "simple_income_end": "Age when this income ends. Use 0 if it continues for life.",
    "simple_income_inflation": "Check this if the income is expected to rise with inflation.",
    "simple_income_reliability": "Guaranteed means reliable income like pension. Variable means uncertain income like side work.",
    "spouse_age": "Your spouse or partner’s current age.",
    "spouse_retire_age": "Age your spouse or partner expects to retire.",
    "spouse_plan_age": "Age your spouse’s part of the plan should last through.",
    "spouse_annual_contribution": "Spouse or partner’s expected annual retirement contributions before retirement.",
    "spouse_healthcare": "Estimated spouse or partner annual healthcare cost in retirement.",
    "spouse_ss_age": "Age when spouse or partner expects to start Social Security.",
    "spouse_ss": "Estimated annual spouse or partner Social Security benefit at age 62 in today’s dollars. The app adjusts it upward if they choose a later claiming age.",
}

def page_help(title, body):
    with st.expander(f"💬 What this page means: {title}", expanded=False):
        st.write(body)

def section_note(text):
    st.info(f"💬 {text}")


def render_page_shell(title, description, icon="📘", kicker="Planner Section"):
    st.markdown(f"""
    <div class="rb-page-shell">
      <div class="rb-page-shell-row">
        <div class="rb-page-icon">{icon}</div>
        <div>
          <div class="rb-page-kicker">{kicker}</div>
          <div class="rb-page-title-lg">{title}</div>
          <div class="rb-page-desc">{description}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def premium_badge(text="Premium Preview"):
    st.markdown(f'<span class="rb-premium-badge">✨ {text}</span>', unsafe_allow_html=True)



def render_premium_lock_cards():
    main_tools = [
        ("🎯", "Smart Retirement Age Optimizer", "Find the retirement age that gives the best balance of retiring sooner, safety, and long-term cushion.", "Open Age Optimizer", "age"),
        ("🪣", "2-Bucket Strategy", "Split retirement money into safer spending money and long-term growth money.", "Open 2-Bucket Strategy", "bucket"),
        ("🔁", "Scenario Comparison", "Compare retirement ages, spending changes, and Social Security timing side by side.", "Open Scenario Comparison", "scenario"),
        ("💸", "Tax-Aware Withdrawal Plan", "See which accounts may make sense to draw from first: taxable, traditional, or Roth.", "Open Tax-Aware Plan", "tax"),
        ("📄", "Full Blueprint Report", "Export a polished report with executive summary, risks, action plan, taxes, and location insights.", "Open Blueprint Report", "report"),
        ("🤖", "Blueprint Coach", "Ask plain-English questions about your retirement blueprint and get educational guidance.", "Open Blueprint Coach", "coach"),
    ]

    for row_start in [0, 3]:
        cols = st.columns(3)
        for col, tool in zip(cols, main_tools[row_start:row_start+3]):
            icon, title, copy, button_label, key = tool
            with col:
                st.markdown(
                    "<div class='rb-premium-card-compact'>"
                    + f"<div class='rb-premium-icon'>{icon}</div>"
                    + f"<div class='rb-premium-title'>{title}</div>"
                    + f"<div class='rb-premium-copy'>{copy}</div>"
                    + "<div class='rb-premium-badge'>Premium</div>"
                    + "</div>",
                    unsafe_allow_html=True,
                )
                if key == "age":
                    if st.button(button_label, key="premium_main_age", use_container_width=True):
                        go_to_page("Retirement Age Optimizer")
                elif key == "bucket":
                    if st.button(button_label, key="premium_main_bucket", use_container_width=True):
                        st.session_state.dashboard_focus = "2-Bucket Strategy"
                        go_to_page("Retirement Dashboard")
                elif key == "scenario":
                    if st.button(button_label, key="premium_main_scenario", use_container_width=True):
                        st.session_state.dashboard_focus = "Scenario Comparison"
                        go_to_page("Retirement Dashboard")
                elif key == "tax":
                    if st.button(button_label, key="premium_main_tax", use_container_width=True):
                        st.session_state.projection_focus = "Tax-Aware Withdrawal Plan"
                        go_to_page("Projection Table")
                elif key == "report":
                    if st.button(button_label, key="premium_main_report", use_container_width=True):
                        go_to_page("PDF Report")
                elif key == "coach":
                    if st.button(button_label, key="premium_main_coach", use_container_width=True):
                        go_to_page("AI Retirement Coach")

    with st.expander("More Premium Tools", expanded=False):
        more_tools = [
            ("🔄", "Roth Conversion Explorer", "Estimate whether Roth conversions may help lower future taxes and reduce RMD pressure.", "Open Roth Conversion Explorer", "roth"),
            ("📍", "Best Places to Retire", "Compare retirement locations using taxes, cost of living, healthcare, climate, and lifestyle fit.", "Open Best Places to Retire", "places"),
            ("📈", "Projection Table", "Review the year-by-year math behind balances, income, withdrawals, taxes, and projected money left.", "Open Projection Table", "projection"),
        ]
        cols = st.columns(3)
        for col, tool in zip(cols, more_tools):
            icon, title, copy, button_label, key = tool
            with col:
                st.markdown(
                    "<div class='rb-premium-card-compact'>"
                    + f"<div class='rb-premium-icon'>{icon}</div>"
                    + f"<div class='rb-premium-title'>{title}</div>"
                    + f"<div class='rb-premium-copy'>{copy}</div>"
                    + "<div class='rb-premium-badge'>Premium</div>"
                    + "</div>",
                    unsafe_allow_html=True,
                )
                if key == "roth":
                    if st.button(button_label, key="premium_more_roth", use_container_width=True):
                        st.session_state.dashboard_focus = "Roth Conversion Explorer"
                        go_to_page("Retirement Dashboard")
                elif key == "places":
                    if st.button(button_label, key="premium_more_places", use_container_width=True):
                        go_to_page("Best Places to Retire")
                elif key == "projection":
                    if st.button(button_label, key="premium_more_projection", use_container_width=True):
                        st.session_state.projection_focus = "Projection Table"
                        go_to_page("Projection Table")


def build_blueprint_insight(df=None, page="general"):
    if df is None or getattr(df, "empty", True):
        return "Complete your blueprint inputs to unlock personalized insights."
    score, label, reasons = calculate_rtv_score(df)
    ending = float(df["End Total"].iloc[-1])
    max_wr = float(df["Withdrawal Rate"].max())
    avg_cov = float(df["Income Coverage Ratio"].mean())
    tax_total = float(df.get("Estimated Federal Tax", pd.Series(dtype=float)).sum()) if "Estimated Federal Tax" in df.columns else 0
    if page == "tax":
        return f"Taxes become most important once traditional withdrawals and taxable Social Security begin. This blueprint currently estimates {money(tax_total)} of federal tax across the plan."
    if page == "bucket":
        return "Premium bucket planning separates near-term safety, medium-term income, and long-term growth so the plan is easier to understand and stress test."
    if page == "places":
        return "Location planning can change the plan through state taxes, property taxes, housing costs, healthcare access, and lifestyle fit."
    if max_wr > 0.07:
        return f"Your biggest pressure point is withdrawal risk. The max projected withdrawal rate is {pct(max_wr)}, so spending, retirement age, income, or bucket design deserve attention."
    if ending > float(df["Start Total"].iloc[0]) and score >= 80:
        return f"Your plan has strong flexibility. It ends with {money(ending)}, which may create room for lifestyle upgrades, Roth conversions, gifting, or legacy planning."
    if avg_cov < 0.35:
        return f"Your portfolio is doing most of the heavy lifting. Average outside-income coverage is {pct(avg_cov)}, so sequence risk and withdrawal order matter."
    return f"Your current blueprint is rated {label} at {score}/100. The next best step is comparing nearby retirement ages and stress testing bad market years."


def render_premium_insight(title="Blueprint Insight", df=None, page="general"):
    insight = build_blueprint_insight(df, page)
    st.markdown(f"""
    <div class="rb-insight-card">
      <div class="rb-insight-kicker">Premium Insight</div>
      <div class="rb-insight-title">{title}</div>
      <div class="rb-insight-copy">{insight}</div>
    </div>
    """, unsafe_allow_html=True)


def render_confidence_meters(df):
    if df is None or df.empty:
        return
    score, label, _ = calculate_rtv_score(df)
    income_cov = min(max(float(df["Income Coverage Ratio"].mean()) * 100, 0), 100)
    max_wr = float(df["Withdrawal Rate"].max())
    tax_total = float(df.get("Estimated Federal Tax", pd.Series(dtype=float)).sum()) if "Estimated Federal Tax" in df.columns else 0
    ordinary_total = float(df.get("Taxable Ordinary Income", pd.Series(dtype=float)).sum()) if "Taxable Ordinary Income" in df.columns else 0
    tax_eff = max(0, min(100, 100 - (tax_total / max(ordinary_total, 1) * 100 * 4)))
    healthcare_risk = 75 if float(st.session_state.get("healthcare", 0) or 0) > 0 and int(st.session_state.get("retire_age", 65) or 65) < 65 else 35
    withdrawal_strength = max(0, min(100, 100 - max_wr * 1000))
    meters = [
        ("Readiness", f"{score}/100", score),
        ("Income Coverage", f"{income_cov:.0f}%", income_cov),
        ("Withdrawal Safety", f"{withdrawal_strength:.0f}%", withdrawal_strength),
        ("Tax Efficiency", f"{tax_eff:.0f}%", tax_eff),
        ("Healthcare Risk", "Elevated" if healthcare_risk >= 70 else "Moderate", 100-healthcare_risk),
    ]
    html = '<div class="rb-meter-grid">'
    for label, value, fill in meters:
        html += f'<div class="rb-meter-card"><div class="rb-meter-label">{label}</div><div class="rb-meter-value">{value}</div><div class="rb-meter-track"><div class="rb-meter-fill" style="width:{max(0,min(100,fill))}%"></div></div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)



def build_two_bucket_strategy(df=None, view_mode="retirement", return_context=False):
    """
    Build a simple, consumer-friendly 2-bucket retirement framework.

    Default view is at the selected retirement age, because that is the
    clearest user question: "When I retire, how much goes in each bucket?"

    - Bucket 1: the selected number of years of retirement expenses.
    - Bucket 2: everything else.
    """
    current_assets = (
        float(st.session_state.get("traditional", 0) or 0)
        + float(st.session_state.get("roth", 0) or 0)
        + float(st.session_state.get("taxable", 0) or 0)
        + float(st.session_state.get("cash", 0) or 0)
    )

    b1_years = float(st.session_state.get("bucket1_years", 3) or 3)
    retire_age = int(st.session_state.get("retire_age", st.session_state.get("current_age", 0)) or 0)

    context = {
        "view_label": "Today",
        "age": int(st.session_state.get("current_age", 0) or 0),
        "total_assets": current_assets,
        "annual_expenses": annual_household_spending() + float(st.session_state.get("healthcare", 0) or 0),
        "bucket1_years": b1_years,
        "explanation": "Based on the retirement savings entered today."
    }

    # For the main app view, show the suggested bucket setup at retirement,
    # not the current account allocation. This avoids confusing users.
    if view_mode == "retirement" and df is not None and not df.empty and "Age" in df.columns:
        retirement_rows = df[df["Age"] >= retire_age]
        if not retirement_rows.empty:
            retirement_row = retirement_rows.iloc[0]

            projected_assets_at_retirement = float(
                retirement_row.get("Start Total", retirement_row.get("End Total", current_assets)) or 0
            )

            # Use total retirement expenses, not just the portfolio withdrawal gap.
            # This matches the plain-English idea: Bucket 1 holds X years of expenses.
            annual_expenses_at_retirement = float(retirement_row.get("Total Spending", 0) or 0)
            if annual_expenses_at_retirement <= 0:
                annual_expenses_at_retirement = (
                    annual_spending_for_age(retire_age)
                    + float(st.session_state.get("healthcare", 0) or 0)
                    + float(st.session_state.get("spouse_healthcare", 0) or 0)
                )

            context = {
                "view_label": "At Retirement",
                "age": retire_age,
                "total_assets": projected_assets_at_retirement,
                "annual_expenses": annual_expenses_at_retirement,
                "bucket1_years": b1_years,
                "explanation": "Based on the projected portfolio and estimated first-year expenses at the selected retirement age."
            }

    total_assets = max(float(context["total_assets"] or 0), 0)
    annual_expenses = max(float(context["annual_expenses"] or 0), 0)

    # Core rule: Bucket 1 should equal only the selected number of years of expenses.
    # Everything else goes to Bucket 2.
    bucket1_target = min(total_assets, max(0, annual_expenses * b1_years))
    bucket2_target = max(total_assets - bucket1_target, 0)

    strategy_df = pd.DataFrame([
        {
            "Bucket": "Bucket 1",
            "Plain-English Name": "Safety Bucket",
            "Purpose": f"{b1_years:g} years of estimated retirement expenses",
            "Suggested Amount": bucket1_target,
            "Target Years": b1_years,
            "Example Holdings": "Cash, money market, CDs, short-term bonds",
            "Risk Level": "Lower",
            "Assumed Return": float(st.session_state.get("safe_return", 0.045) or 0.045)
        },
        {
            "Bucket": "Bucket 2",
            "Plain-English Name": "Growth Bucket",
            "Purpose": "Everything else, invested for longer-term growth and future refills",
            "Suggested Amount": bucket2_target,
            "Target Years": "Long term",
            "Example Holdings": "Diversified stock/bond portfolio based on risk tolerance",
            "Risk Level": "Moderate to higher",
            "Assumed Return": float(st.session_state.get("growth_return", 0.07) or 0.07)
        },
    ])

    if return_context:
        return strategy_df, context
    return strategy_df


# Backward-compatible alias so older report code still works after the simplification.
def build_three_bucket_strategy(df=None):
    return build_two_bucket_strategy(df)


def render_two_bucket_strategy(df=None):
    premium_badge("Premium 2-Bucket Strategy")
    st.markdown(
        """
        The 2-bucket system keeps retirement simple:

        **Bucket 1 = Safety money.** At retirement, this should hold only the number of years of expenses the user chooses, such as 3 years.

        **Bucket 2 = Growth money.** This is everything else, invested for longer-term growth and used to refill Bucket 1 over time.
        """
    )

    strat, context = build_two_bucket_strategy(df, view_mode="retirement", return_context=True)

    st.markdown("#### Suggested setup at retirement")
    st.caption(
        f"These amounts are based on the projected portfolio at age {int(context['age'])}, "
        "not simply the money entered today."
    )

    b1_amount = float(strat.loc[strat["Bucket"] == "Bucket 1", "Suggested Amount"].iloc[0])
    b2_amount = float(strat.loc[strat["Bucket"] == "Bucket 2", "Suggested Amount"].iloc[0])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Retirement Age Used", int(context["age"]))
    m1.caption("Selected retirement age")
    m2.metric("Projected Portfolio", money(context["total_assets"]))
    m2.caption("Estimated balance at retirement")
    m3.metric("Annual Expenses Used", money(context["annual_expenses"]))
    m3.caption("Estimated first-year retirement expenses")
    m4.metric("Bucket 1 Target", f"{float(context['bucket1_years']):g} years")
    m4.caption("User-selected safety years")

    st.info(
        f"At retirement, Bucket 1 is set to **{money(b1_amount)}**, which equals about "
        f"**{float(context['bucket1_years']):g} years of estimated expenses**. "
        f"The remaining **{money(b2_amount)}** goes into Bucket 2 for longer-term growth."
    )

    cards = ''
    for i, row in strat.iterrows():
        target_years = row['Target Years']
        target_text = f"{target_years:g} years" if isinstance(target_years, (int, float)) else str(target_years)
        cards += f"""<div class="rb-bucket-card"><div class="rb-bucket-num">{i+1}</div><div class="rb-bucket-title">{row['Bucket']}: {row['Plain-English Name']}</div><div class="rb-bucket-amount">{money(row['Suggested Amount'])}</div><div class="rb-bucket-copy"><b>Purpose:</b> {row['Purpose']}<br/><b>Target:</b> {target_text}<br/><b>Assumed return:</b> {pct(row['Assumed Return'])}<br/><b>Examples:</b> {row['Example Holdings']}<br/><b>Risk:</b> {row['Risk Level']}</div></div>"""
    st.markdown(f'<div class="rb-bucket-grid">{cards}</div>', unsafe_allow_html=True)

    show = strat.copy()
    show["Suggested Amount"] = show["Suggested Amount"].map(money)
    show["Target Years"] = show["Target Years"].map(lambda x: f"{x:g}" if isinstance(x, (int, float)) else x)
    if "Assumed Return" in show.columns:
        show["Assumed Return"] = show["Assumed Return"].map(pct)
    st.dataframe(show, use_container_width=True, hide_index=True)

    st.info(
        "Simple version: Bucket 1 holds only the chosen number of years of expenses. Bucket 2 holds the rest."
    )
    st.warning(
        "Educational purposes only. This bucket framework is not financial, tax, investment, or legal advice and does not replace guidance from a qualified professional."
    )
    st.caption("Phase 1 displays suggested bucket targets without reclassifying tax accounts or guaranteeing investment results.")


# Backward-compatible alias so old calls render the new simplified experience.
def render_three_bucket_strategy(df=None):
    render_two_bucket_strategy(df)



def _bucket_strategy_first_need(df=None):
    """Estimate the first-year retirement expense need for the bucket comparison model."""
    fallback = annual_household_spending() + float(st.session_state.get("healthcare", 0) or 0)
    if df is not None and not df.empty:
        retired = df[df.get("Household Retired", False) == True] if "Household Retired" in df.columns else df
        if not retired.empty:
            if "Total Spending" in retired.columns:
                val = float(retired["Total Spending"].replace([np.inf, -np.inf], np.nan).dropna().head(1).mean() or 0)
                if val > 0:
                    return val
            if "Portfolio Withdrawal" in retired.columns:
                val = float(retired["Portfolio Withdrawal"].replace([np.inf, -np.inf], np.nan).dropna().head(1).mean() or 0)
                if val > 0:
                    return val
    return max(fallback, 1.0)


def simulate_bucket_strategy(strategy="2 Bucket", df=None, stress=False):
    """
    Educational bucket comparison simulator.
    It uses the app's projected annual portfolio withdrawal needs, then applies simple virtual
    return/refill rules so users can compare a single portfolio against a 2-bucket structure.
    This does not replace the tax-aware account projection; it is a strategy overlay.
    """
    if df is None or df.empty:
        df = run_projection()
    if df is None or df.empty:
        return pd.DataFrame(), {}

    total_assets = (
        float(st.session_state.get("traditional", 0) or 0)
        + float(st.session_state.get("roth", 0) or 0)
        + float(st.session_state.get("taxable", 0) or 0)
        + float(st.session_state.get("cash", 0) or 0)
    )
    safe_return = float(st.session_state.get("safe_return", 0.04) or 0.04)
    growth_return = float(st.session_state.get("growth_return", 0.07) or 0.07)
    first_need = _bucket_strategy_first_need(df)
    b1_years = float(st.session_state.get("bucket1_years", 3) or 3)

    if strategy == "1 Bucket":
        b1 = 0.0
        b2 = total_assets
        target_b1 = 0.0
    else:
        # Keep Bucket 1 limited to the user's selected safety years.
        # Do not automatically overfill Bucket 1 because the user happens to have more cash today.
        target_b1 = min(total_assets, max(0.0, first_need * b1_years))
        b1 = target_b1
        b2 = max(total_assets - b1, 0.0)

    rows = []
    depleted_age = None
    cumulative_shortfall = 0.0
    total_withdrawals = 0.0
    total_refills = 0.0
    worst_start_total = total_assets

    for idx, row in df.reset_index(drop=True).iterrows():
        age = int(row.get("Age", int(st.session_state.get("current_age", 0) or 0) + idx))
        start_total = b1 + b2
        worst_start_total = min(worst_start_total, start_total)

        # Contributions before retirement go to the long-term growth bucket.
        if age < int(st.session_state.get("retire_age", 0) or 0):
            b2 += float(st.session_state.get("annual_contribution", 0) or 0)
        spouse_age = row.get("Spouse Age", "")
        try:
            spouse_age_num = int(spouse_age)
            if bool(st.session_state.get("has_spouse", False)) and spouse_age_num < int(st.session_state.get("spouse_retire_age", 0) or 0):
                b2 += float(st.session_state.get("spouse_annual_contribution", 0) or 0)
        except Exception:
            pass

        # Stress version: bad first three market years after retirement for growth assets.
        is_retired_year = bool(row.get("Household Retired", False))
        years_after_retire = max(age - int(st.session_state.get("retire_age", age) or age), 0)
        if stress and is_retired_year and years_after_retire < 3:
            g_ret = -0.15
        else:
            g_ret = growth_return

        b1 *= (1 + safe_return)
        b2 *= (1 + g_ret)

        need = float(row.get("Portfolio Withdrawal", 0) or 0)
        shortfall = 0.0
        used_b1 = used_b2 = 0.0

        if strategy == "1 Bucket":
            take = min(b2, need)
            b2 -= take
            used_b2 += take
            shortfall = max(need - take, 0)
        else:
            take = min(b1, need)
            b1 -= take
            used_b1 += take
            need -= take
            if need > 0:
                take = min(b2, need)
                b2 -= take
                used_b2 += take
                need -= take
            shortfall = max(need, 0)

            # Refill Bucket 1 after the annual withdrawal if the growth bucket can support it.
            refill = min(max(target_b1 - b1, 0.0), b2)
            b2 -= refill
            b1 += refill
            total_refills += refill

        actual = used_b1 + used_b2
        total_withdrawals += actual
        cumulative_shortfall += shortfall
        end_total = b1 + b2
        if depleted_age is None and (end_total <= 0 or shortfall > 0):
            depleted_age = age
        rows.append({
            "Age": age,
            "Strategy": strategy,
            "Start Total": start_total,
            "End Total": end_total,
            "Bucket 1 — Safety": b1,
            "Bucket 2 — Growth": b2,
            "Portfolio Withdrawal Need": float(row.get("Portfolio Withdrawal", 0) or 0),
            "Actual Withdrawal": actual,
            "Shortfall": shortfall,
            "Withdrawal Rate": actual / max(start_total, 1),
        })
        if end_total <= 0 and shortfall > 0:
            break

    out = pd.DataFrame(rows)
    if out.empty:
        summary = {}
    else:
        summary = {
            "Strategy": strategy,
            "Ending Portfolio": float(out["End Total"].iloc[-1]),
            "Lowest Portfolio": float(out["End Total"].min()),
            "Max Withdrawal Rate": float(out["Withdrawal Rate"].max()),
            "Total Withdrawals": float(total_withdrawals),
            "Total Refills": float(total_refills),
            "Shortfall": float(cumulative_shortfall),
            "Depletion Age": depleted_age if depleted_age is not None else "Not depleted",
            "Years Funded": len(out),
            "Stress Test": "Bad first 3 retired years" if stress else "Normal returns",
            "Safety Bucket Return": safe_return if strategy == "2 Bucket" else None,
            "Growth Bucket Return": growth_return,
            "Bucket 1 Years": b1_years if strategy == "2 Bucket" else 0,
        }
    return out, summary


def build_bucket_strategy_comparison(df=None, stress=False):
    strategies = ["1 Bucket", "2 Bucket"]
    summaries = []
    paths = []
    for strategy in strategies:
        path, summary = simulate_bucket_strategy(strategy, df=df, stress=stress)
        if summary:
            summaries.append(summary)
            paths.append(path)
    summary_df = pd.DataFrame(summaries)
    paths_df = pd.concat(paths, ignore_index=True) if paths else pd.DataFrame()
    if not summary_df.empty:
        base_end = float(summary_df.loc[summary_df["Strategy"] == "1 Bucket", "Ending Portfolio"].iloc[0]) if "1 Bucket" in summary_df["Strategy"].values else float(summary_df["Ending Portfolio"].iloc[0])
        base_short = float(summary_df.loc[summary_df["Strategy"] == "1 Bucket", "Shortfall"].iloc[0]) if "1 Bucket" in summary_df["Strategy"].values else float(summary_df["Shortfall"].iloc[0])
        summary_df["Ending Change vs 1 Bucket"] = summary_df["Ending Portfolio"] - base_end
        summary_df["Shortfall Change vs 1 Bucket"] = summary_df["Shortfall"] - base_short
        summary_df["Plain-English Meaning"] = summary_df["Strategy"].map({
            "1 Bucket": "Everything stays together. Simple, but more exposed if the market drops early in retirement.",
            "2 Bucket": "A safety bucket covers near-term spending while the rest stays invested for growth."
        })
    return summary_df, paths_df


def render_bucket_strategy_comparison_panel(df=None):
    if not can_run:
        st.info("Complete your core inputs to compare a 1-bucket approach against the 2-bucket strategy.")
        return
    if df is None or df.empty:
        df = run_projection()

    premium_badge("Premium 2-Bucket Comparison")

    st.markdown("### Compare the retirement withdrawal system")
    st.markdown(
        """
        This compares **how retirement money is organized and withdrawn**.

        **1 Bucket** keeps everything together in one investment portfolio.  
        **2 Bucket** separates the money into:
        - **Bucket 1: Safety Bucket** — the next few years of planned spending
        - **Bucket 2: Growth Bucket** — everything else, invested for longer-term growth

        The 2-bucket system is designed to make retirement easier to understand and less stressful during market drops.

        **Key idea:** 2 Bucket is not always designed to make the user richer. It is designed to make retirement withdrawals safer, clearer, and easier to stick with during bad markets.
        """
    )

    with st.expander("Simple explanation of the system", expanded=True):
        st.markdown(
            """
            | **Strategy** | **How spending works** | **Why someone might choose it** |
            |---|---|---|
            | **1 Bucket** | Withdraw money from one combined portfolio every year | Simple and may grow more if markets do well |
            | **2 Bucket** | Spend from Bucket 1 first; refill it from Bucket 2 over time | Keeps near-term spending money safer so the user may avoid selling growth investments during bad markets |
            """
        )
        st.info(
            "Think of Bucket 1 like a retirement paycheck reserve. "
            "Bucket 2 is the long-term engine that is meant to keep growing and refill Bucket 1 later."
        )

    with st.expander("When is 2 Bucket better than 1 Bucket?", expanded=False):
        st.markdown(
            """
            A 2-bucket system may be better when the user cares more about **retirement stability and peace of mind** than getting the highest possible ending balance.

            It is especially useful when:
            - The user is retiring soon or newly retired
            - The market performs badly in the first few retirement years
            - The user wants a few years of spending kept safer
            - The user may panic if all their retirement money rises and falls together
            - The user is bridging years before Social Security or Medicare
            - The user wants retirement to feel like a more predictable paycheck system

            **Simple takeaway:**  
            **1 Bucket may be best for maximum long-term growth. 2 Bucket may be best for a smoother, easier-to-understand retirement paycheck system.**
            """
        )

    view = st.radio(
        "Comparison view",
        ["Normal return assumptions", "Bad first 3 retirement years (-15% growth return each year)"],
        horizontal=True,
        key="bucket_compare_view",
        help="Normal returns show the base case. The bad-start view assumes growth investments lose 15% per year for the first 3 retired years while Bucket 1 still earns the safer return."
    )

    stress = view.startswith("Bad first 3 retirement years")

    if stress:
        st.warning(
            "Stress test assumption: for the first 3 years after retirement, the growth portfolio is modeled at **-15% per year**. "
            "Bucket 1 still uses the safer return assumption. This is not a prediction — it is an educational downside test."
        )
    else:
        st.caption(
            "Normal view uses the return assumptions entered in the app: the full portfolio for 1 Bucket, and Bucket 1 / Bucket 2 returns for the 2-bucket system."
        )

    summary_df, paths_df = build_bucket_strategy_comparison(df, stress=stress)
    if summary_df.empty:
        st.info("Not enough projection data to compare bucket strategies yet.")
        return

    one = summary_df[summary_df["Strategy"] == "1 Bucket"].iloc[0]
    two = summary_df[summary_df["Strategy"] == "2 Bucket"].iloc[0]

    one_ending = float(one.get("Ending Portfolio", 0) or 0)
    two_ending = float(two.get("Ending Portfolio", 0) or 0)
    one_shortfall = float(one.get("Shortfall", 0) or 0)
    two_shortfall = float(two.get("Shortfall", 0) or 0)
    one_depletion = one.get("Depletion Age", "Not depleted")
    two_depletion = two.get("Depletion Age", "Not depleted")

    delta = two_ending - one_ending
    abs_delta = abs(delta)

    growth_return = float(st.session_state.get("growth_return", 0.07) or 0.07)
    safe_return = float(st.session_state.get("safe_return", 0.045) or 0.045)
    bucket1_years = float(st.session_state.get("bucket1_years", 3) or 3)

    st.markdown("### Big picture result")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            f"""
            <div style="border:1px solid #e5e7eb;border-radius:18px;padding:22px;background:#fff;box-shadow:0 10px 24px rgba(15,23,42,.06);min-height:265px;">
                <div style="color:#6b7280;font-size:15px;">1 Bucket System</div>
                <div style="font-size:36px;font-weight:800;color:#111827;margin:8px 0;">{money(one_ending)}</div>
                <div style="color:#6b7280;">Projected money left at the end of the plan</div>
                <hr style="border:none;border-top:1px solid #eef2f7;margin:16px 0;">
                <b>How it works:</b><br>
                All money stays in one portfolio and withdrawals come from that same portfolio each year.<br><br>
                <b>Return used:</b> {pct(growth_return)} on the full portfolio
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        if delta < 0:
            comparison_sentence = f"Projected to end with {money(abs_delta)} less than 1 Bucket, mainly because Bucket 1 uses a safer/lower return."
        elif delta > 0:
            comparison_sentence = f"Projected to end with {money(abs_delta)} more than 1 Bucket in this test."
        else:
            comparison_sentence = "Projected to end with about the same amount as 1 Bucket."

        st.markdown(
            f"""
            <div style="border:1px solid #e5e7eb;border-radius:18px;padding:22px;background:#fff;box-shadow:0 10px 24px rgba(15,23,42,.06);min-height:265px;">
                <div style="color:#6b7280;font-size:15px;">2 Bucket System</div>
                <div style="font-size:36px;font-weight:800;color:#111827;margin:8px 0;">{money(two_ending)}</div>
                <div style="color:#6b7280;">Projected money left at the end of the plan</div>
                <hr style="border:none;border-top:1px solid #eef2f7;margin:16px 0;">
                <b>How it works:</b><br>
                Bucket 1 holds {bucket1_years:g} years of safer spending money. Bucket 2 holds the rest for growth.<br><br>
                <b>Return used:</b> {pct(safe_return)} on Bucket 1 / {pct(growth_return)} on Bucket 2
            </div>
            """,
            unsafe_allow_html=True
        )

    if stress:
        st.warning(
            "This view tests a rough market start to retirement: growth investments are modeled at **-15% per year for the first 3 retired years**. "
            "A 2-bucket system is meant to help here because near-term spending can come from Bucket 1 instead of selling growth investments while they are down."
        )
    else:
        st.info(
            "Under normal returns, 1 Bucket may show more money left because more of the portfolio stays invested for growth. "
            "That does not automatically make it better. The 2-bucket system may show less money left because some money is kept safer, "
            "but its purpose is to protect near-term spending and make the plan easier to live with."
        )

    st.markdown("### What the numbers mean")

    simple_rows = [
        {
            "Question": "How is the money organized?",
            "1 Bucket": "Everything stays in one portfolio",
            "2 Bucket": f"Bucket 1 = {bucket1_years:g} years of expenses; Bucket 2 = everything else"
        },
        {
            "Question": "Where does spending come from?",
            "1 Bucket": "The same portfolio every year",
            "2 Bucket": "Bucket 1 first, then Bucket 2 refills Bucket 1 over time"
        },
        {
            "Question": "What return is assumed?",
            "1 Bucket": f"{'-15.0% for first 3 retired years, then ' if stress else ''}{pct(growth_return)} on the full portfolio",
            "2 Bucket": f"{pct(safe_return)} on Bucket 1; {'-15.0% for first 3 retired years, then ' if stress else ''}{pct(growth_return)} on Bucket 2"
        },
        {
            "Question": "Projected money left",
            "1 Bucket": money(one_ending),
            "2 Bucket": money(two_ending)
        },
        {
            "Question": "Does it run out?",
            "1 Bucket": "No" if one_shortfall <= 0 and one_depletion == "Not depleted" else f"Yes, around age {one_depletion}",
            "2 Bucket": "No" if two_shortfall <= 0 and two_depletion == "Not depleted" else f"Yes, around age {two_depletion}"
        },
        {
            "Question": "Plain-English takeaway",
            "1 Bucket": "More growth-focused, but more exposed to early market drops",
            "2 Bucket": comparison_sentence
        }
    ]

    st.dataframe(pd.DataFrame(simple_rows), use_container_width=True, hide_index=True)

    st.markdown("### Bottom line")
    if one_shortfall > 0 and two_shortfall > 0:
        st.error(
            "Both strategies run out in this test. The user may need to retire later, spend less, save more, or use different assumptions."
        )
    elif one_shortfall > 0 and two_shortfall <= 0:
        st.success(
            "In this test, the 2-bucket system helps the plan last longer than the 1-bucket system."
        )
    elif two_shortfall > 0 and one_shortfall <= 0:
        st.warning(
            "In this test, the 1-bucket system lasts longer, but it may be more exposed to market drops. Review the return assumptions and Bucket 1 size."
        )
    elif delta < 0:
        st.info(
            "Both strategies last through the plan. The 1-bucket system ends with more money, while the 2-bucket system trades some growth "
            "for clearer near-term spending safety. This can still be a good tradeoff for someone who wants retirement withdrawals to feel more stable."
        )
    else:
        st.success(
            "Both strategies last through the plan, and the 2-bucket system also provides clearer near-term spending protection."
        )

    with st.expander("Show advanced numbers", expanded=False):
        st.caption("Advanced numbers are useful for deeper analysis, but the simple comparison above is the user-friendly summary.")
        show = summary_df.copy()
        for money_col in ["Ending Portfolio", "Lowest Portfolio", "Total Withdrawals", "Total Refills", "Shortfall", "Ending Change vs 1 Bucket", "Shortfall Change vs 1 Bucket"]:
            if money_col in show.columns:
                show[money_col] = show[money_col].map(money)
        if "Max Withdrawal Rate" in show.columns:
            show["Max Withdrawal Rate"] = show["Max Withdrawal Rate"].map(pct)
        for rate_col in ["Safety Bucket Return", "Growth Bucket Return"]:
            if rate_col in show.columns:
                show[rate_col] = show[rate_col].map(lambda x: "N/A" if pd.isna(x) else pct(x))
        st.dataframe(show, use_container_width=True, hide_index=True)

    if not paths_df.empty:
        fig, ax = plt.subplots(figsize=(9, 4.5))
        for strategy, group in paths_df.groupby("Strategy"):
            ax.plot(group["Age"], group["End Total"], label=strategy, linewidth=2)
        ax.set_title("Projected Money Left Over Time: 1 Bucket vs 2 Bucket")
        ax.set_xlabel("Age")
        ax.set_ylabel("Projected Money Left")
        ax.legend()
        ax.grid(True, alpha=0.25)
        st.pyplot(fig, use_container_width=True)

    st.warning(
        "Educational purposes only. This comparison is a simplified planning illustration, not financial, tax, investment, or legal advice. "
        "It does not guarantee results or replace guidance from a qualified professional."
    )
    st.caption("The main projection remains the source of truth for tax-aware withdrawals. This bucket comparison is a strategy overlay using the return assumptions shown above.")

def run_projection_with_temp_retire_age(test_age):
    original = st.session_state.retire_age
    try:
        st.session_state.retire_age = int(test_age)
        temp_df = run_projection()
        if temp_df.empty:
            return None
        score, label, _ = calculate_rtv_score(temp_df)
        return {
            "Retirement Age": int(test_age),
            "Blueprint Score": score,
            "Label": label,
            "Ending Portfolio": float(temp_df["End Total"].iloc[-1]),
            "Max Withdrawal Rate": float(temp_df["Withdrawal Rate"].max()),
            "Avg Income Coverage": float(temp_df["Income Coverage Ratio"].mean()),
            "Estimated Federal Tax": float(temp_df.get("Estimated Federal Tax", pd.Series(dtype=float)).sum()) if "Estimated Federal Tax" in temp_df.columns else 0,
        }
    finally:
        st.session_state.retire_age = original


def render_scenario_comparison_panel():
    if not can_run:
        st.info("Complete your core inputs to compare retirement scenarios.")
        return

    premium_badge("Premium Scenario Comparison")
    st.caption(
        "Simple view: this shows whether retiring a little earlier or later improves the plan. "
        "The goal is to make the tradeoff easy to understand, not overwhelm users with every calculation."
    )

    current = int(st.session_state.retire_age or st.session_state.current_age or 0)
    current_age = int(st.session_state.current_age or 0)
    planning_age = int(st.session_state.end_age or 90)

    starting_nest_egg = (
        float(st.session_state.get("traditional", 0) or 0)
        + float(st.session_state.get("roth", 0) or 0)
        + float(st.session_state.get("taxable", 0) or 0)
        + float(st.session_state.get("cash", 0) or 0)
    )
    yearly_spending = annual_household_spending()
    growth_return = float(st.session_state.get("growth_return", 0.07) or 0.07)
    safe_return = float(st.session_state.get("safe_return", 0.045) or 0.045)
    safety_assets = float(st.session_state.get("cash", 0) or 0)
    growth_assets = max(starting_nest_egg - safety_assets, 0)
    if starting_nest_egg > 0:
        blended_return = ((growth_assets * growth_return) + (safety_assets * safe_return)) / starting_nest_egg
    else:
        blended_return = growth_return

    st.markdown("#### Scenario assumptions")
    st.caption("These are the main numbers this comparison is using, so users can understand the story before looking at the results.")

    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Your Current Age", int(current_age))
    a1.caption("Starting age for this plan")
    a2.metric("Starting Nest Egg", money(starting_nest_egg))
    a2.caption("Retirement savings entered today")
    a3.metric("Yearly Spending", money(yearly_spending))
    a3.caption("Planned lifestyle spending per year")
    a4.metric("Avg Return Used", pct(blended_return))
    a4.caption("Blended from growth and safety assumptions")

    # Keep the default comparison simple and close to the user's selected age.
    ages = sorted(set([
        max(current_age + 1, current - 2),
        max(current_age + 1, current),
        max(current_age + 1, current + 2),
        max(current_age + 1, current + 5),
    ]))

    rows = []
    for age in ages:
        if age <= planning_age:
            result = run_projection_with_temp_retire_age(age)
            if result:
                rows.append(result)

    if not rows:
        st.info("Not enough data to compare retirement ages yet.")
        return

    comp = pd.DataFrame(rows)
    base = comp[comp["Retirement Age"] == current]
    base_score = int(base["Blueprint Score"].iloc[0]) if not base.empty else int(comp["Blueprint Score"].iloc[0])
    comp["Score Change"] = comp["Blueprint Score"] - base_score

    def simple_status(score, ending_portfolio):
        if score >= 90:
            return "Very Strong"
        if score >= 80:
            return "Strong"
        if score >= 60:
            return "Possible, but tight"
        if ending_portfolio <= 0:
            return "High Risk"
        return "Needs work"

    def simple_takeaway(row):
        age = int(row["Retirement Age"])
        score = int(row["Blueprint Score"])
        score_change = int(row["Score Change"])
        withdrawal_rate = float(row.get("Max Withdrawal Rate", 0) or 0)
        ending = float(row.get("Ending Portfolio", 0) or 0)

        if ending <= 0 or score < 60:
            return "Likely too risky with current inputs."
        if score_change >= 10:
            return "Working longer materially improves the plan."
        if score_change >= 3:
            return "Some improvement versus the current age."
        if score_change <= -10:
            return "Earlier retirement adds meaningful risk."
        if withdrawal_rate > 0.07:
            return "Watch withdrawals; spending may be too high."
        if score >= 90:
            return "Strong option based on current inputs."
        return "Possible option; review details."

    comp["Simple Status"] = comp.apply(lambda r: simple_status(r["Blueprint Score"], r["Ending Portfolio"]), axis=1)
    comp["Plain-English Takeaway"] = comp.apply(simple_takeaway, axis=1)

    # Pick the best tested age using score first, then ending portfolio.
    best = comp.sort_values(["Blueprint Score", "Ending Portfolio"], ascending=False).iloc[0]
    current_row = comp.iloc[(comp["Retirement Age"] - current).abs().argsort()].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Current Test Age", int(current_row["Retirement Age"]), f"Score {int(current_row['Blueprint Score'])}/100")
    c2.metric("Best Tested Age", int(best["Retirement Age"]), f"Score {int(best['Blueprint Score'])}/100")
    c3.metric("Plan Strength", best["Simple Status"], f"{money(best['Ending Portfolio'])} at age {planning_age}")

    st.success(
        f"Best tested age: **{int(best['Retirement Age'])}**. "
        f"Blueprint Score: **{int(best['Blueprint Score'])}/100**. "
        f"Simple takeaway: **{best['Plain-English Takeaway']}**"
    )

    st.markdown("#### Simple comparison")
    money_left_col = f"Projected Money Left at {planning_age}"
    comp[money_left_col] = comp["Ending Portfolio"].map(lambda x: "Runs out" if float(x or 0) <= 0 else money(float(x)))

    simple_show = comp[[
        "Retirement Age",
        "Blueprint Score",
        money_left_col,
        "Score Change",
        "Simple Status",
        "Plain-English Takeaway",
    ]].copy()
    simple_show["Blueprint Score"] = simple_show["Blueprint Score"].map(lambda x: f"{int(x)}/100")
    simple_show["Score Change"] = simple_show["Score Change"].map(lambda x: f"{int(x):+}")
    simple_show = simple_show.rename(columns={
        "Retirement Age": "Retire at Age",
        "Score Change": "Score Change vs Current",
        "Simple Status": "Status",
        "Plain-English Takeaway": "What it means",
    })
    st.dataframe(simple_show, use_container_width=True, hide_index=True)
    st.caption(
        f"Projected Money Left at {planning_age} means the estimated portfolio balance remaining at the end of the plan. "
        "It uses the same numbers from the projection: savings, contributions, retirement spending, income, taxes, and investment return assumptions."
    )

    with st.expander("Show advanced numbers", expanded=False):
        advanced = comp[[
            "Retirement Age",
            "Blueprint Score",
            "Label",
            "Ending Portfolio",
            "Max Withdrawal Rate",
            "Avg Income Coverage",
            "Estimated Federal Tax",
        ]].copy()
        advanced["Ending Portfolio"] = advanced["Ending Portfolio"].map(money)
        advanced["Max Withdrawal Rate"] = advanced["Max Withdrawal Rate"].map(pct)
        advanced["Avg Income Coverage"] = advanced["Avg Income Coverage"].map(pct)
        advanced["Estimated Federal Tax"] = advanced["Estimated Federal Tax"].map(money)
        advanced = advanced.rename(columns={
            "Retirement Age": "Retire at Age",
            "Label": "Detailed Label",
        })
        st.dataframe(advanced, use_container_width=True, hide_index=True)
        st.caption(
            "Advanced numbers are useful for deeper analysis, but the simple comparison above is the user-friendly summary."
        )

def build_retirement_age_optimizer_results(start_age=None, end_age=None, safety_target=None):
    """
    Uses the app's real projection engine to test multiple retirement ages and
    identify the earliest possible, recommended, and safest retirement ages.
    """
    if not can_run:
        return None

    current_age = int(st.session_state.current_age or 0)
    planning_age = int(st.session_state.end_age or 90)

    if current_age <= 0 or planning_age <= current_age:
        return None

    if start_age is None:
        start_age = current_age + 1
    if end_age is None:
        end_age = min(70, planning_age - 1)
    if safety_target is None:
        safety_target = max(250000, annual_household_spending() * 2)

    start_age = max(int(start_age), current_age)
    end_age = min(int(end_age), planning_age - 1)

    rows = []
    for test_age in range(start_age, end_age + 1):
        snapshot = snapshot_session_state_for_projection()
        try:
            st.session_state.retire_age = int(test_age)
            test_df = run_projection()
            if test_df is None or test_df.empty:
                continue

            score, label, reasons = calculate_rtv_score(test_df)
            ending_portfolio = float(test_df["End Total"].iloc[-1])
            max_withdrawal_rate = float(test_df["Withdrawal Rate"].max())
            avg_income_coverage = float(test_df["Income Coverage Ratio"].mean())
            total_unmet_need = float(test_df["Unmet Need"].sum()) if "Unmet Need" in test_df.columns else 0.0
            estimated_tax = float(test_df.get("Estimated Federal Tax", pd.Series(dtype=float)).sum()) if "Estimated Federal Tax" in test_df.columns else 0.0

            failed = bool(total_unmet_need > 0 or ending_portfolio <= 0)
            plan_status = "Works" if not failed else "Needs Work"

            healthcare_gap_years = max(0, 65 - int(test_age))
            ss_gap_years = max(0, int(st.session_state.user_ss_age or 62) - int(test_age))

            rows.append({
                "Retirement Age": int(test_age),
                "Plan Status": plan_status,
                "Blueprint Score": int(score),
                "Readiness Label": label,
                "Ending Portfolio": ending_portfolio,
                "Safety Cushion": ending_portfolio - float(safety_target),
                "Max Withdrawal Rate": max_withdrawal_rate,
                "Avg Income Coverage": avg_income_coverage,
                "Estimated Federal Tax": estimated_tax,
                "Unmet Need": total_unmet_need,
                "Healthcare Gap Years": healthcare_gap_years,
                "Years Until Social Security": ss_gap_years,
                "Recommendation Notes": "; ".join(reasons[:3]) if reasons else "No major risk flags found.",
            })
        finally:
            restore_session_state_after_projection(snapshot)

    if not rows:
        return None

    results = pd.DataFrame(rows)
    viable = results[
        (results["Plan Status"] == "Works")
        & (results["Ending Portfolio"] > 0)
        & (results["Unmet Need"] <= 0)
    ].copy()

    if viable.empty:
        return {
            "results": results,
            "earliest": None,
            "recommended": None,
            "safest": None,
            "safety_target": float(safety_target),
        }

    earliest = viable.sort_values(["Retirement Age"], ascending=True).iloc[0]

    recommended_candidates = viable[
        (viable["Blueprint Score"] >= 80)
        & (viable["Ending Portfolio"] >= float(safety_target))
    ].copy()

    if recommended_candidates.empty:
        recommended_candidates = viable[
            (viable["Blueprint Score"] >= 60)
            & (viable["Ending Portfolio"] >= 0)
        ].copy()

    if recommended_candidates.empty:
        recommended_candidates = viable.copy()

    # Prefer a high score and cushion, but slightly favor earlier retirement when the plan is already strong.
    recommended_candidates["Recommendation Rank"] = (
        recommended_candidates["Blueprint Score"] * 2
        + (recommended_candidates["Safety Cushion"] / max(float(safety_target), 1)).clip(-2, 5) * 10
        - (recommended_candidates["Retirement Age"] - current_age) * 1.5
    )

    recommended = recommended_candidates.sort_values(
        ["Recommendation Rank", "Blueprint Score", "Ending Portfolio"],
        ascending=False
    ).iloc[0]

    safest = viable.sort_values(
        ["Ending Portfolio", "Blueprint Score"],
        ascending=False
    ).iloc[0]

    return {
        "results": results,
        "earliest": earliest,
        "recommended": recommended,
        "safest": safest,
        "safety_target": float(safety_target),
    }


def render_retirement_age_optimizer_page():
    render_page_shell(
        "Smart Retirement Age Optimizer",
        "Compare retirement ages and see which age gives the best balance of retiring sooner, portfolio safety, and long-term cushion.",
        "🎯"
    )
    page_help(
        "Smart Retirement Age Optimizer",
        "This educational tool runs the current blueprint several times using different retirement ages. It does not tell the user when to retire. It helps compare which tested age appears strongest based on the numbers entered."
    )

    if not can_run:
        st.info("Complete the required inputs first, then return here to calculate a retirement age recommendation.")
        return

    premium_badge("Premium Feature Preview")

    st.markdown("### What this tool is for")
    st.info(
        "This tool answers one simple question: **Based on the numbers entered, which retirement age looks strongest?** "
        "It compares several retirement ages side by side and looks at whether the money lasts, how much cushion is left, "
        "how much pressure withdrawals put on the portfolio, and how many years the user must bridge before Medicare or Social Security."
    )

    with st.expander("How to read the recommendation", expanded=True):
        st.markdown(
            """
            | **Result** | **What it means** |
            |---|---|
            | **Earliest Possible** | The first tested age where the plan appears to work through the planning age |
            | **Current Target Age** | The age with the best balance of retiring sooner, Blueprint Score, safety cushion, and risk |
            | **Safest Age** | The age that leaves the highest projected ending balance |
            | **Recommended Score** | The Blueprint Score for the tested retirement age |

            **Important:** The recommended age is not automatically the earliest age or the safest age.  
            It is the age that appears to offer the best overall balance based on the current inputs.
            """
        )

    st.warning(
        "Educational estimate only. This does not tell someone when they should retire and is not financial, tax, legal, investment, insurance, or retirement advice."
    )

    current_age = int(st.session_state.current_age or 0)
    planning_age = int(st.session_state.end_age or 90)
    current_retire_age = int(st.session_state.retire_age or max(current_age + 1, 62))

    st.markdown("### Ages to compare")
    st.caption("Choose the retirement ages you want the app to test. Most people test a range like 58 through 70.")

    c1, c2, c3 = st.columns(3)
    start_age = c1.number_input(
        "First age to test",
        min_value=current_age,
        max_value=max(current_age, min(75, planning_age - 1)),
        value=max(current_age, min(current_retire_age, planning_age - 1)),
        step=1,
        help="The earliest retirement age you want the optimizer to test.",
        key="optimizer_start_age",
    )
    end_age = c2.number_input(
        "Last age to test",
        min_value=int(start_age),
        max_value=max(int(start_age), min(75, planning_age - 1)),
        value=max(int(start_age), min(70, planning_age - 1)),
        step=1,
        help="The latest retirement age you want the optimizer to test. Many users test through age 70.",
        key="optimizer_end_age",
    )
    safety_target = c3.number_input(
        "Minimum cushion wanted",
        min_value=0,
        value=int(max(250000, annual_household_spending() * 2)),
        step=25000,
        help="The optimizer favors retirement ages that leave at least this much projected money at the end of the plan.",
        key="optimizer_safety_target",
    )

    st.caption(
        "Minimum cushion wanted is the amount of projected money the user would like to still have at the end of the plan. "
        "A higher cushion makes the recommendation more conservative."
    )

    if st.button("Calculate My Can I Retire at This Age?", type="primary", use_container_width=True):
        with st.spinner("Testing retirement ages with your current blueprint..."):
            st.session_state.retirement_age_optimizer = build_retirement_age_optimizer_results(
                start_age=int(start_age),
                end_age=int(end_age),
                safety_target=float(safety_target),
            )

    if "retirement_age_optimizer" not in st.session_state:
        st.info("Click the button above to generate your retirement age recommendation.")
        return

    opt = st.session_state.retirement_age_optimizer
    if not opt or opt.get("results") is None or opt["results"].empty:
        st.warning("The optimizer could not calculate results with the current inputs.")
        return

    results = opt["results"].copy()

    if opt["recommended"] is None:
        st.error("None of the tested retirement ages fully worked under the current assumptions.")
        st.write("Try testing later ages, reducing spending, increasing savings, adding income, or adjusting Social Security timing.")
    else:
        earliest = opt["earliest"]
        recommended = opt["recommended"]
        safest = opt["safest"]

        st.success(
            f"Current Target Age: **{int(recommended['Retirement Age'])}** — "
            "best overall balance from the ages tested."
        )

        st.markdown("### Recommendation summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Earliest Possible", int(earliest["Retirement Age"]), "First tested age that works")
        m1.caption("Useful if the user wants to retire as soon as the plan appears workable.")

        m2.metric("Current Target Age", int(recommended["Retirement Age"]), "Best balance")
        m2.caption("Balances retiring sooner with score, cushion, and risk.")

        m3.metric("Safest Age", int(safest["Retirement Age"]), "Highest ending balance")
        m3.caption("Most conservative of the tested ages.")

        m4.metric("Recommended Score", f"{int(recommended['Blueprint Score'])}/100", recommended["Readiness Label"])
        m4.caption("Blueprint Score at the recommended age.")

        st.markdown("### Why this age was recommended")
        st.caption(
            "This table explains the main drivers behind the recommendation. The optimizer is looking for an age that works, "
            "has a strong score, leaves a cushion, and does not put too much withdrawal pressure on the portfolio."
        )

        why_rows = [
            ["Portfolio survival", recommended["Plan Status"], f"Does the money last through age {planning_age}? Projected money left is {money(recommended['Ending Portfolio'])}."],
            ["Safety cushion", money(recommended["Safety Cushion"]), f"Projected money above the selected minimum cushion of {money(opt['safety_target'])}."],
            ["Withdrawal pressure", pct(recommended["Max Withdrawal Rate"]), "The highest withdrawal rate during retirement. Lower usually means more flexibility."],
            ["Income coverage", pct(recommended["Avg Income Coverage"]), "How much spending is covered by income sources like Social Security, pension, or other income instead of portfolio withdrawals."],
            ["Healthcare gap", f"{int(recommended['Healthcare Gap Years'])} years", "Years before Medicare eligibility at age 65. More gap years can increase risk."],
            ["Social Security gap", f"{int(recommended['Years Until Social Security'])} years", "Years before Social Security starts. More gap years mean the portfolio must carry more of the load."],
        ]
        st.dataframe(pd.DataFrame(why_rows, columns=["Factor", "Result", "What it means"]), use_container_width=True, hide_index=True)

        st.markdown("### Plain-English takeaway")
        if int(earliest["Retirement Age"]) < int(recommended["Retirement Age"]):
            st.info(
                f"The plan may work as early as **age {int(earliest['Retirement Age'])}**, "
                f"but **age {int(recommended['Retirement Age'])}** looks stronger because it provides a better balance of score, cushion, and risk."
            )
        else:
            st.info(
                f"**Age {int(recommended['Retirement Age'])}** appears to be the earliest tested age that also provides a reasonable safety margin."
            )

        if int(safest["Retirement Age"]) > int(recommended["Retirement Age"]):
            st.write(
                f"Age **{int(safest['Retirement Age'])}** is the safest tested age because it leaves the highest projected ending portfolio. "
                f"The optimizer did not automatically choose it because age **{int(recommended['Retirement Age'])}** already appears strong and allows retirement sooner."
            )

    st.subheader("Retirement Age Comparison")
    st.caption(
        "Use this table to compare each tested age. It shows whether the plan works, the Blueprint Score, projected money left, "
        "withdrawal pressure, and key gap years before Medicare or Social Security."
    )

    display = results.copy()
    for col in ["Ending Portfolio", "Safety Cushion", "Estimated Federal Tax", "Unmet Need"]:
        if col in display.columns:
            display[col] = display[col].map(money)
    for col in ["Max Withdrawal Rate", "Avg Income Coverage"]:
        if col in display.columns:
            display[col] = display[col].map(pct)

    display_columns = [
        "Retirement Age",
        "Plan Status",
        "Blueprint Score",
        "Readiness Label",
        "Ending Portfolio",
        "Safety Cushion",
        "Max Withdrawal Rate",
        "Avg Income Coverage",
        "Healthcare Gap Years",
        "Years Until Social Security",
        "Unmet Need",
    ]
    st.dataframe(display[display_columns], use_container_width=True, hide_index=True)

    with st.expander("What each column means", expanded=False):
        st.markdown(
            """
            | **Column** | **Meaning** |
            |---|---|
            | **Retirement Age** | The age being tested |
            | **Plan Status** | Whether the portfolio appears to last through the planning age |
            | **Blueprint Score** | Overall retirement readiness score for that tested age |
            | **Ending Portfolio** | Projected money left at the end of the plan |
            | **Safety Cushion** | Projected money left above the minimum cushion selected above |
            | **Max Withdrawal Rate** | The highest annual portfolio withdrawal rate in the plan |
            | **Avg Income Coverage** | Percent of spending covered by income sources instead of withdrawals |
            | **Healthcare Gap Years** | Years before Medicare starts |
            | **Years Until Social Security** | Years before Social Security starts |
            | **Unmet Need** | Spending the plan could not cover, if any |
            """
        )

    csv = results.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Retirement Age Comparison CSV",
        csv,
        "retirement_age_optimizer.csv",
        "text/csv",
        use_container_width=True,
    )

    st.warning("Educational planning estimate only. Not financial, tax, legal, investment, insurance, or retirement advice.")

def set_default(key, value):
    if key not in st.session_state:
        st.session_state[key] = value


# -----------------------------
# Defaults
# -----------------------------
defaults = {
    "current_age": 0,
    "retire_age": 0,
    "end_age": 90,
    "traditional": 0,
    "roth": 0,
    "taxable": 0,
    "cash": 0,
    "annual_contribution": 0,
    "has_spouse": False,
    "spouse_age": 0,
    "spouse_retire_age": 0,
    "spouse_plan_age": 90,
    "spouse_annual_contribution": 0,
    "healthcare": 0,
    "spouse_healthcare": 0,
    "user_ss_age": 62,
    "user_ss": 0,
    "spouse_ss_age": 62,
    "spouse_ss": 0,
    "survivor_ss_strategy": "Higher benefit continues",
    "survivor_spending": 0,
    "budget_mode": "Flat monthly number",
    "flat_monthly_spending": 0,
    "growth_return": 0.07,
    "safe_return": 0.045,
    "inflation": 0.03,
    "annual_conversion": 0,
    "bucket1_years": 3.0,
    "income_mode": "Simple income",
    "simple_income": 0,
    "simple_income_start": 0,
    "simple_income_end": 0,
    "simple_income_inflation": False,
    "simple_income_reliability": "Guaranteed",
    "home_value": 0,
    "mortgage_balance": 0,
    "monthly_mortgage": 0,
    "annual_property_taxes_home": 0,
    "mortgage_payoff_age": 0,
    "retirement_housing_plan": "Unsure",
    "tax_year": 2026,
    "filing_status": "married_joint",
    "rmd_start_age": None,
    "user_plan": "free",
    "premium_preview_enabled": True,
    "bucket2_years": 5.0,
    "enable_spending_change": False,
    "spending_change_age": 0,
    "spending_change_monthly": 0,
}
for k, v in defaults.items():
    set_default(k, v)

budget_keys = [
    ("mortgage_rent", "Mortgage / Rent"),
    ("property_tax", "Property taxes"),
    ("home_insurance", "Home insurance"),
    ("hoa", "HOA / condo fees"),
    ("electric", "Electric"),
    ("gas_utility", "Gas / heating"),
    ("water_sewer", "Water / sewer"),
    ("trash", "Trash"),
    ("internet", "Internet"),
    ("cell_phone", "Cell phones"),
    ("subscriptions", "Streaming / subscriptions"),
    ("groceries", "Groceries"),
    ("restaurants", "Restaurants / coffee"),
    ("household_items", "Household items"),
    ("car_payment", "Car payments"),
    ("car_insurance", "Car insurance"),
    ("gasoline", "Gasoline"),
    ("car_maintenance", "Car maintenance"),
    ("travel", "Vacations / travel"),
    ("hobbies", "Hobbies"),
    ("golf_entertainment", "Golf / entertainment"),
    ("clothing", "Clothing"),
    ("gifts_family", "Gifts / family support"),
    ("pets", "Pets"),
    ("personal_care", "Personal care"),
    ("medical_oop", "Medical out-of-pocket, not premiums"),
    ("misc_buffer", "Miscellaneous buffer"),
]
for k, _ in budget_keys:
    set_default(k, 0)

if "income_sources_df" not in st.session_state:
    st.session_state.income_sources_df = pd.DataFrame([
        {
            "Name": "Pension / side gig / rental",
            "Annual Amount": 0,
            "Start Age": 0,
            "End Age": 0,
            "Inflation Adjusted": False,
            "Taxable": True,
            "Owner": "Joint",
            "Reliability": "Guaranteed",
            "Continues After First Death": True,
        }
    ])


# -----------------------------
# Saved scenario helpers
# -----------------------------
def get_scenario_data():
    data = {}

    keys_to_save = [
        "current_age", "retire_age", "end_age",
        "traditional", "roth", "taxable", "cash",
        "annual_contribution", "has_spouse", "spouse_age",
        "spouse_retire_age", "spouse_plan_age",
        "spouse_annual_contribution", "healthcare", "spouse_healthcare",
        "user_ss_age", "user_ss", "spouse_ss_age", "spouse_ss",
        "survivor_ss_strategy", "survivor_spending",
        "budget_mode", "flat_monthly_spending",
        "growth_return", "safe_return", "inflation",
        "annual_conversion", "bucket1_years", "bucket2_years",
        "income_mode", "simple_income", "simple_income_start",
        "simple_income_end", "simple_income_inflation",
        "simple_income_reliability",
        "home_value", "mortgage_balance", "monthly_mortgage",
        "annual_property_taxes_home", "mortgage_payoff_age",
        "retirement_housing_plan",
        "rmd_start_age",
        "enable_spending_change", "spending_change_age", "spending_change_monthly",
    ]

    for key in keys_to_save:
        data[key] = st.session_state.get(key)

    for key, _ in budget_keys:
        data[key] = st.session_state.get(key, 0)

    if "income_sources_df" in st.session_state and st.session_state.income_sources_df is not None:
        data["income_sources_df"] = st.session_state.income_sources_df.to_dict("records")
    else:
        data["income_sources_df"] = []

    return data


def apply_scenario_data(data):
    for key, value in data.items():
        if key == "income_sources_df":
            st.session_state.income_sources_df = pd.DataFrame(value)
        else:
            st.session_state[key] = value


def save_scenario(user, scenario_name, scenario_data):
    supabase.table("retirement_scenarios").insert({
        "user_id": user.id,
        "scenario_name": scenario_name,
        "scenario_data": scenario_data
    }).execute()


def load_scenarios(user):
    response = (
        supabase.table("retirement_scenarios")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


def detailed_monthly_budget_total():
    return sum(float(st.session_state.get(k, 0) or 0) for k, _ in budget_keys)


def annual_household_spending():
    if st.session_state.budget_mode == "Flat monthly number":
        return float(st.session_state.flat_monthly_spending or 0) * 12
    return detailed_monthly_budget_total() * 12


def annual_spending_for_age(age):
    base = annual_household_spending()
    if bool(st.session_state.get("enable_spending_change", False)):
        change_age = int(st.session_state.get("spending_change_age", 0) or 0)
        change_monthly = float(st.session_state.get("spending_change_monthly", 0) or 0)
        if change_age > 0 and change_monthly > 0 and age >= change_age:
            return change_monthly * 12
    return base


def home_equity():
    return max(float(st.session_state.home_value or 0) - float(st.session_state.mortgage_balance or 0), 0)


def annual_mortgage_payment_for_age(age):
    monthly = float(st.session_state.monthly_mortgage or 0)
    payoff_age = int(st.session_state.mortgage_payoff_age or 0)
    if monthly <= 0:
        return 0
    if payoff_age <= 0:
        return monthly * 12
    if age < payoff_age:
        return monthly * 12
    return 0


def housing_flexibility_label():
    equity = home_equity()
    plan = st.session_state.retirement_housing_plan
    if equity >= 500000:
        return "High Flexibility"
    if equity >= 250000:
        return "Moderate Flexibility"
    if plan in ["Downsize", "Relocate", "Snowbird"]:
        return "Strategy Opportunity"
    return "Limited / Unknown"


def required_missing():
    missing = []

    if st.session_state.current_age == 0:
        missing.append("current age")
    if st.session_state.retire_age == 0:
        missing.append("retirement age")
    if st.session_state.end_age == 0:
        missing.append("plan-through age")
    if annual_household_spending() == 0:
        missing.append("household spending")

    # Spouse fields are only required when the user chooses to include a spouse/partner.
    if st.session_state.has_spouse:
        if st.session_state.spouse_age == 0:
            missing.append("spouse age")
        if st.session_state.spouse_retire_age == 0:
            missing.append("spouse retirement age")

    return missing


def inflate(amount, start_age, age):
    if age <= start_age:
        return amount
    return amount * ((1 + float(st.session_state.inflation)) ** (age - start_age))


def simple_income_for_age(age):
    amount = float(st.session_state.simple_income or 0)
    start = int(st.session_state.simple_income_start or 0)
    end = int(st.session_state.simple_income_end or 0)
    if amount <= 0 or start <= 0 or age < start:
        return {"guaranteed": 0, "variable": 0, "taxable": 0, "total": 0}
    if end > 0 and age > end:
        return {"guaranteed": 0, "variable": 0, "taxable": 0, "total": 0}
    val = inflate(amount, start, age) if st.session_state.simple_income_inflation else amount
    if st.session_state.simple_income_reliability == "Guaranteed":
        return {"guaranteed": val, "variable": 0, "taxable": val, "total": val}
    return {"guaranteed": 0, "variable": val, "taxable": val, "total": val}


def advanced_income_for_age(age, spouse_alive):
    df = st.session_state.income_sources_df
    guaranteed = variable = taxable = total = 0.0
    if df is None or df.empty:
        return {"guaranteed": 0, "variable": 0, "taxable": 0, "total": 0}

    for _, row in df.iterrows():
        try:
            amount = float(row.get("Annual Amount", 0) or 0)
            start = int(row.get("Start Age", 0) or 0)
            end = int(row.get("End Age", 0) or 0)
        except Exception:
            continue
        if amount <= 0 or start <= 0 or age < start:
            continue
        if end > 0 and age > end:
            continue

        owner = row.get("Owner", "Joint")
        continues = bool(row.get("Continues After First Death", True))
        if st.session_state.has_spouse and not spouse_alive and owner in ["Spouse", "Joint"] and not continues:
            continue

        val = inflate(amount, start, age) if bool(row.get("Inflation Adjusted", False)) else amount
        total += val
        if bool(row.get("Taxable", True)):
            taxable += val
        if row.get("Reliability", "Guaranteed") == "Guaranteed":
            guaranteed += val
        else:
            variable += val

    return {"guaranteed": guaranteed, "variable": variable, "taxable": taxable, "total": total}


def other_income_for_age(age, spouse_alive):
    if st.session_state.income_mode == "Simple income":
        return simple_income_for_age(age)
    return advanced_income_for_age(age, spouse_alive)


def calculate_rtv_score(df):
    """
    RTV = Retirement Timing Viability.

    This version prioritizes actual projected plan success:
    - Does the plan run out of money?
    - Is there any unmet spending need?
    - How large is the ending cushion?
    - Are withdrawals aggressive relative to survivability?

    A plan ending with a very large balance should score strongly even if
    outside income coverage is low or early withdrawals are elevated.
    """
    if df.empty:
        return 0, "Incomplete", []

    ending = float(df["End Total"].iloc[-1])
    start_total = float(df["Start Total"].iloc[0])
    max_wr = float(df["Withdrawal Rate"].max())
    avg_wr = float(df["Withdrawal Rate"].mean())
    income_coverage = float(df["Income Coverage Ratio"].mean())
    unmet_need = float(df["Unmet Need"].sum())

    score = 100
    reasons = []

    # Hard penalties only when the plan actually fails.
    if unmet_need > 0:
        score -= 45
        reasons.append("The plan has unmet spending needs in at least one year.")

    if ending <= 0:
        score -= 45
        reasons.append("The portfolio is depleted before the plan ends.")

    # Ending cushion is the most important success signal.
    if ending > 0 and unmet_need <= 0:
        if ending >= start_total * 2:
            score += 5
            reasons.append("Projected ending portfolio is very strong.")
        elif ending >= start_total:
            reasons.append("Projected ending portfolio remains above the starting balance.")
        elif ending >= 500000:
            score -= 3
            reasons.append("Projected ending portfolio remains healthy.")
        elif ending >= 250000:
            score -= 8
            reasons.append("Projected ending portfolio cushion is moderate.")
        else:
            score -= 18
            reasons.append("Projected ending portfolio cushion is low.")

    # Withdrawal rate matters, but should not dominate if the plan survives with a large cushion.
    if max_wr > 0.09:
        score -= 12
        reasons.append("Maximum withdrawal rate is high in at least one year.")
    elif max_wr > 0.07:
        score -= 8
        reasons.append("Maximum withdrawal rate is elevated.")
    elif max_wr > 0.05:
        score -= 4
        reasons.append("Maximum withdrawal rate is moderately elevated.")

    if avg_wr > 0.06:
        score -= 8
        reasons.append("Average withdrawal pressure is high across the plan.")
    elif avg_wr > 0.045:
        score -= 4
        reasons.append("Average withdrawal pressure is moderate.")

    # Income coverage is a confidence factor, not a deal-breaker.
    if income_coverage < 0.25:
        score -= 4
        reasons.append("Outside income covers a smaller share of spending, so the plan relies more on portfolio withdrawals.")
    elif income_coverage >= 0.60:
        score += 3
        reasons.append("Outside income coverage improves plan stability.")

    score = max(0, min(100, round(score)))

    if score >= 90:
        label = "Very Strong"
    elif score >= 80:
        label = "Strong"
    elif score >= 70:
        label = "Likely Viable"
    elif score >= 60:
        label = "Needs Optimization"
    else:
        label = "High Risk"

    return score, label, reasons

def run_projection():
    if st.session_state.current_age <= 0 or st.session_state.retire_age <= 0 or st.session_state.end_age <= 0:
        return pd.DataFrame()

    rows = []
    trad = float(st.session_state.traditional)
    roth = float(st.session_state.roth)
    taxable = float(st.session_state.taxable)
    bucket1 = float(st.session_state.cash)
    base_spending = annual_household_spending()

    for age in range(int(st.session_state.current_age), int(st.session_state.end_age) + 1):
        year_offset = age - int(st.session_state.current_age)
        spouse_age = int(st.session_state.spouse_age) + year_offset if st.session_state.has_spouse else 0
        spouse_alive = bool(st.session_state.has_spouse and spouse_age <= int(st.session_state.spouse_plan_age))
        start_total = trad + roth + taxable + bucket1
        start_trad_for_rmd = trad

        if age < int(st.session_state.retire_age):
            trad += float(st.session_state.annual_contribution) * 0.8
            roth += float(st.session_state.annual_contribution) * 0.2
        if spouse_alive and spouse_age < int(st.session_state.spouse_retire_age):
            trad += float(st.session_state.spouse_annual_contribution) * 0.8
            roth += float(st.session_state.spouse_annual_contribution) * 0.2

        trad *= (1 + float(st.session_state.growth_return))
        roth *= (1 + float(st.session_state.growth_return))
        taxable *= (1 + float(st.session_state.growth_return))
        bucket1 *= (1 + float(st.session_state.safe_return))

        household_retired = age >= int(st.session_state.retire_age) and (not spouse_alive or spouse_age >= int(st.session_state.spouse_retire_age))

        # Do not auto-transfer pre-tax money into Bucket 1.
        # Bucket 1 in this projection represents actual cash/safe assets entered by the user.
        # The 2-bucket module shows suggested targets separately without silently reclassifying
        # traditional assets or using a hardcoded after-tax haircut.

        conversion = 0
        if age >= int(st.session_state.retire_age) and float(st.session_state.annual_conversion) > 0:
            conversion = min(trad, float(st.session_state.annual_conversion))
            trad -= conversion
            roth += conversion

        user_ss = apply_cola_to_social_security(
            social_security_for_age(age, int(st.session_state.user_ss_age), float(st.session_state.user_ss)),
            age,
        )
        spouse_ss = apply_cola_to_social_security(
            social_security_for_age(spouse_age, int(st.session_state.spouse_ss_age), float(st.session_state.spouse_ss)),
            age,
        ) if spouse_alive else 0
        if st.session_state.has_spouse and not spouse_alive:
            if st.session_state.survivor_ss_strategy == "Higher benefit continues":
                spouse_survivor_ss = apply_cola_to_social_security(
                    estimate_social_security_by_claim_age(float(st.session_state.spouse_ss), int(st.session_state.spouse_ss_age)),
                    age,
                )
                ss_income = max(user_ss, spouse_survivor_ss)
            else:
                ss_income = user_ss
        else:
            ss_income = user_ss + spouse_ss

        inc = other_income_for_age(age, spouse_alive)
        other_income = inc["total"]
        guaranteed_income = ss_income + inc["guaranteed"]
        variable_income = inc["variable"]

        spending = 0
        if household_retired:
            inflation_factor = inflation_factor_from_today(age)
            if st.session_state.has_spouse and not spouse_alive and float(st.session_state.survivor_spending) > 0:
                spending = float(st.session_state.survivor_spending) * inflation_factor
            else:
                spending = annual_spending_for_age(age) * inflation_factor

        healthcare = 0
        healthcare_inflation_factor = inflation_factor_from_today(age)
        if age >= int(st.session_state.retire_age):
            healthcare += float(st.session_state.healthcare) * healthcare_inflation_factor
        if spouse_alive and spouse_age >= int(st.session_state.spouse_retire_age):
            healthcare += float(st.session_state.spouse_healthcare) * healthcare_inflation_factor

        mortgage_payment = annual_mortgage_payment_for_age(age) if household_retired else 0
        total_spending = spending + healthcare + mortgage_payment
        non_portfolio_income = ss_income + other_income

        ordinary_income_before_withdrawals = float(inc.get("taxable", 0)) + conversion
        base_tax_estimate = estimate_federal_tax(ordinary_income_before_withdrawals, social_security_income=ss_income)
        base_federal_tax = base_tax_estimate["federal_tax"]
        income_gap = max(total_spending + base_federal_tax - non_portfolio_income, 0)
        withdrawal_needed = income_gap

        used_b1 = used_taxable = used_trad = used_roth = 0.0
        federal_tax_from_trad = 0.0
        take = min(bucket1, withdrawal_needed); bucket1 -= take; withdrawal_needed -= take; used_b1 += take
        take = min(taxable, withdrawal_needed); taxable -= take; withdrawal_needed -= take; used_taxable += take
        if withdrawal_needed > 0:
            take, net_from_trad = gross_traditional_needed_for_net(withdrawal_needed, ordinary_income_before_withdrawals, trad, social_security_income=ss_income)
            federal_tax_from_trad = incremental_federal_tax(ordinary_income_before_withdrawals, take, social_security_income=ss_income)
            trad -= take
            withdrawal_needed -= net_from_trad
            used_trad += take
        take = min(roth, max(withdrawal_needed, 0)); roth -= take; withdrawal_needed -= take; used_roth += take

        rmd_required = calculate_required_minimum_distribution(age, start_trad_for_rmd)
        forced_rmd = 0.0
        federal_tax_from_forced_rmd = 0.0
        taxable_reinvestment = 0.0
        if household_retired and rmd_required > used_trad and trad > 0:
            forced_rmd = min(trad, rmd_required - used_trad)
            federal_tax_from_forced_rmd = incremental_federal_tax(
                ordinary_income_before_withdrawals + used_trad,
                forced_rmd,
                social_security_income=ss_income
            )
            trad -= forced_rmd
            used_trad += forced_rmd
            taxable_reinvestment = max(forced_rmd - federal_tax_from_forced_rmd, 0)
            taxable += taxable_reinvestment

        estimated_federal_tax = base_federal_tax + federal_tax_from_trad + federal_tax_from_forced_rmd
        final_tax_estimate = estimate_federal_tax(ordinary_income_before_withdrawals + used_trad, social_security_income=ss_income)
        actual_withdrawal = used_b1 + used_taxable + used_trad + used_roth
        end_total = trad + roth + taxable + bucket1
        leftover = max(non_portfolio_income + actual_withdrawal - total_spending - estimated_federal_tax, 0)

        rows.append({
            "Age": age,
            "Spouse Age": spouse_age if st.session_state.has_spouse else "",
            "Spouse Alive": spouse_alive if st.session_state.has_spouse else "",
            "Household Retired": household_retired,
            "Start Total": start_total,
            "End Total": end_total,
            "Traditional": trad,
            "Roth": roth,
            "Taxable": taxable,
            "Bucket 1": bucket1,
            "Lifestyle Spending": spending,
            "Healthcare": healthcare,
            "Mortgage Payment": mortgage_payment,
            "Total Spending": total_spending,
            "Social Security": ss_income,
            "Other Guaranteed Income": inc["guaranteed"],
            "Other Variable Income": variable_income,
            "Total Other Income": other_income,
            "Total Non-Portfolio Income": non_portfolio_income,
            "Guaranteed Income": guaranteed_income,
            "Income Gap": income_gap,
            "Estimated Federal Tax": estimated_federal_tax,
            "Provisional Income": final_tax_estimate["provisional_income"],
            "Taxable Social Security": final_tax_estimate["taxable_social_security"],
            "Taxable Ordinary Income": final_tax_estimate["gross_ordinary_income"],
            "Federal Taxable Income": final_tax_estimate["taxable_income"],
            "Effective Federal Tax Rate": estimated_federal_tax / max(final_tax_estimate["gross_ordinary_income"], 1),
            "Portfolio Withdrawal": actual_withdrawal,
            # Backward-compatible alias used throughout the UI for the amount needed from savings.
            "Portfolio Need": actual_withdrawal,
            "Left Over After Spending": leftover,
            "Roth Conversion": conversion,
            "RMD Required": rmd_required,
            "Forced RMD": forced_rmd,
            "RMD Reinvested to Taxable": taxable_reinvestment,
            "Unmet Need": max(withdrawal_needed, 0),
            "Withdrawal Rate": actual_withdrawal / max(start_total, 1),
            "Income Coverage Ratio": non_portfolio_income / max(total_spending, 1),
            "Guaranteed Income Coverage Ratio": guaranteed_income / max(total_spending, 1),
        })

        if end_total <= 0:
            break

    return pd.DataFrame(rows)



def snapshot_session_state_for_projection():
    keys = list(defaults.keys()) + [key for key, _ in budget_keys]
    snap = {}
    for key in keys:
        snap[key] = st.session_state.get(key)

    if "income_sources_df" in st.session_state and st.session_state.income_sources_df is not None:
        snap["income_sources_df"] = st.session_state.income_sources_df.copy()
    else:
        snap["income_sources_df"] = None

    return snap


def restore_session_state_after_projection(snapshot):
    for key, value in snapshot.items():
        st.session_state[key] = value


def run_projection_for_saved_scenario(data):
    snapshot = snapshot_session_state_for_projection()

    try:
        apply_scenario_data(data)
        temp_df = run_projection()

        if temp_df.empty:
            return temp_df, 0, "Incomplete", []

        score, label, reasons = calculate_rtv_score(temp_df)
        return temp_df, score, label, reasons

    finally:
        restore_session_state_after_projection(snapshot)



def test_rtv_with_changes(**changes):
    """
    Temporarily apply changes to session_state, run the real projection,
    calculate RTV, then restore original values.
    """
    snapshot = snapshot_session_state_for_projection()

    try:
        for key, value in changes.items():
            st.session_state[key] = value

        test_df = run_projection()
        if test_df.empty:
            return {
                "score": 0,
                "label": "Incomplete",
                "ending": 0,
                "max_wr": 0,
                "income_coverage": 0,
                "unmet_need": 0,
            }

        score, label, reasons = calculate_rtv_score(test_df)

        return {
            "score": score,
            "label": label,
            "ending": float(test_df["End Total"].iloc[-1]),
            "max_wr": float(test_df["Withdrawal Rate"].max()),
            "income_coverage": float(test_df["Income Coverage Ratio"].mean()),
            "unmet_need": float(test_df["Unmet Need"].sum()),
        }

    finally:
        restore_session_state_after_projection(snapshot)


def build_rtv_improvement_recommendations(base_df, base_score):
    """
    Creates practical RTV improvement options using the actual projection engine.
    """
    actions = []

    current_retire_age = int(st.session_state.retire_age)
    current_end_age = int(st.session_state.end_age)
    current_monthly = float(annual_household_spending() / 12)
    current_contrib = float(st.session_state.annual_contribution or 0)
    current_ss_age = int(st.session_state.user_ss_age)

    tests = []

    if current_monthly > 0:
        tests.append(("Reduce spending by $500/month", {"flat_monthly_spending": max(current_monthly - 500, 0)}))
        tests.append(("Reduce spending by $1,000/month", {"flat_monthly_spending": max(current_monthly - 1000, 0)}))
        tests.append(("Reduce spending by 10%", {"flat_monthly_spending": max(current_monthly * 0.90, 0)}))

    if current_retire_age < 75:
        tests.append(("Delay retirement 1 year", {"retire_age": current_retire_age + 1}))
        tests.append(("Delay retirement 2 years", {"retire_age": current_retire_age + 2}))

    if current_end_age > current_retire_age + 15:
        tests.append(("Plan to age 85 instead", {"end_age": 85}))
        tests.append(("Plan to age 90 instead", {"end_age": 90}))

    if current_contrib >= 0:
        tests.append(("Add $10,000/year contributions", {"annual_contribution": current_contrib + 10000}))
        tests.append(("Add $20,000/year contributions", {"annual_contribution": current_contrib + 20000}))

    if current_ss_age < 70:
        tests.append(("Delay your Social Security to 67", {"user_ss_age": max(67, current_ss_age)}))
        tests.append(("Delay your Social Security to 70", {"user_ss_age": 70}))

    for name, changes in tests:
        result = test_rtv_with_changes(**changes)
        delta = result["score"] - base_score

        actions.append({
            "Action": name,
            "Blueprint Impact": delta,
            "New Blueprint Score": result["score"],
            "Status": result["label"],
            "Ending Portfolio": result["ending"],
            "Max Withdrawal Rate": result["max_wr"],
            "Income Coverage": result["income_coverage"],
            "Unmet Need": result["unmet_need"],
        })

    actions = sorted(actions, key=lambda x: x["Blueprint Impact"], reverse=True)
    return actions


def build_spend_more_tests(base_score):
    """
    Tests whether user can spend more and still keep a strong RTV score.
    """
    current_monthly = float(annual_household_spending() / 12)
    if current_monthly <= 0:
        return []

    tests = [
        ("Spend $500/month more", current_monthly + 500),
        ("Spend $1,000/month more", current_monthly + 1000),
        ("Spend 10% more", current_monthly * 1.10),
        ("Spend 20% more", current_monthly * 1.20),
    ]

    rows = []
    for name, new_monthly in tests:
        result = test_rtv_with_changes(flat_monthly_spending=new_monthly)
        rows.append({
            "Scenario": name,
            "New Monthly Spending": new_monthly,
            "Blueprint Impact": result["score"] - base_score,
            "New Blueprint Score": result["score"],
            "Status": result["label"],
            "Ending Portfolio": result["ending"],
            "Max Withdrawal Rate": result["max_wr"],
        })

    return rows




def safe_get(obj, key, default=None):
    try:
        if isinstance(obj, dict):
            value = obj.get(key, default)
        else:
            value = getattr(obj, key, default)
        if value is None:
            return default
        return value
    except Exception:
        return default

def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default

def safe_int(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default



def get_display_timezone():
    # Streamlit Cloud usually stores created_at in UTC. Browser timezone requires
    # a JS component, so for now we default to Eastern Time for the current target/testing group.
    # Later we can replace this with automatic browser timezone detection.
    return st.session_state.get("display_timezone", "America/Detroit")

def format_saved_datetime(value, timezone_name=None):
    try:
        if not value:
            return ""
        tz_name = timezone_name or get_display_timezone()
        dt = pd.to_datetime(value)

        # If timestamp has no timezone, treat it as UTC because Supabase/Streamlit saved times are usually UTC.
        if getattr(dt, "tzinfo", None) is None:
            dt = dt.tz_localize("UTC")

        dt = dt.tz_convert(tz_name)
        return dt.strftime("%b %d, %Y • %-I:%M %p")
    except Exception:
        try:
            dt = pd.to_datetime(value)
            return dt.strftime("%b %d, %Y • %I:%M %p")
        except Exception:
            return str(value)


def compact_money_label(x):
    try:
        x = float(x)
        if abs(x) >= 1_000_000:
            return f"${x/1_000_000:.1f}M"
        if abs(x) >= 1_000:
            return f"${x/1_000:.0f}K"
        return f"${x:,.0f}"
    except Exception:
        return "$0"


def style_axis_money(ax):
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: compact_money_label(x)))
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def add_last_value_label(ax, x, y, label=None):
    if len(x) == 0 or len(y) == 0:
        return
    label = label or compact_money_label(y.iloc[-1] if hasattr(y, "iloc") else y[-1])
    ax.annotate(
        label,
        xy=(x.iloc[-1] if hasattr(x, "iloc") else x[-1], y.iloc[-1] if hasattr(y, "iloc") else y[-1]),
        xytext=(8, 0),
        textcoords="offset points",
        va="center",
        fontsize=9,
        fontweight="bold",
    )


def plot_portfolio_area_chart(df):
    fig, ax = plt.subplots(figsize=(12, 5.8))

    ages = df["Age"]
    stack_cols = ["Traditional", "Roth", "Taxable", "Bucket 1"]
    labels = ["Traditional", "Roth", "Taxable", "Bucket 1"]

    ax.stackplot(ages, [df[c] for c in stack_cols], labels=labels, alpha=0.82)
    ax.plot(ages, df["End Total"], linewidth=3, label="Total Portfolio")

    start_val = df["End Total"].iloc[0]
    end_val = df["End Total"].iloc[-1]

    ax.annotate(
        f"Start {compact_money_label(start_val)}",
        xy=(ages.iloc[0], start_val),
        xytext=(12, 12),
        textcoords="offset points",
        fontsize=9,
        fontweight="bold",
    )

    ax.annotate(
        f"End {compact_money_label(end_val)}",
        xy=(ages.iloc[-1], end_val),
        xytext=(-90, 14),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold",
    )

    ax.set_title("Portfolio Balance by Account Type", fontsize=15, fontweight="bold", loc="left")
    ax.set_xlabel("Age")
    ax.set_ylabel("Portfolio Balance")
    style_axis_money(ax)
    ax.legend(loc="upper left", ncol=3, frameon=True)
    fig.tight_layout()
    return fig


def plot_spending_income_bar_chart(df):
    fig, ax = plt.subplots(figsize=(12, 5.8))

    ages = df["Age"]
    width = 0.38

    ax.bar(ages - width / 2, df["Total Spending"], width=width, label="Total Spending")
    ax.bar(ages + width / 2, df["Total Non-Portfolio Income"], width=width, label="Non-Portfolio Income")
    ax.plot(ages, df["Portfolio Withdrawal"], linewidth=3, marker="o", markersize=4, label="Portfolio Withdrawal")

    # Label every few years to avoid clutter.
    step = max(1, len(df) // 8)
    for i in range(0, len(df), step):
        ax.text(
            ages.iloc[i],
            df["Total Spending"].iloc[i],
            compact_money_label(df["Total Spending"].iloc[i]),
            ha="center",
            va="bottom",
            fontsize=8,
        )

    add_last_value_label(ax, ages, df["Portfolio Withdrawal"], f"Withdrawal {compact_money_label(df['Portfolio Withdrawal'].iloc[-1])}")

    ax.set_title("Spending vs. Income vs. Portfolio Withdrawal", fontsize=15, fontweight="bold", loc="left")
    ax.set_xlabel("Age")
    ax.set_ylabel("Annual Amount")
    style_axis_money(ax)
    ax.legend(loc="upper left", ncol=3, frameon=True)
    fig.tight_layout()
    return fig


def plot_income_gap_chart(df):
    fig, ax = plt.subplots(figsize=(12, 5.8))

    ages = df["Age"]
    ax.bar(ages, df["Income Gap"], label="Income Gap")
    ax.plot(ages, df["Total Spending"], linewidth=3, label="Total Spending")
    ax.plot(ages, df["Guaranteed Income"], linewidth=3, label="Guaranteed Income")

    max_gap = df["Income Gap"].max()
    if max_gap > 0:
        max_gap_age = df.loc[df["Income Gap"].idxmax(), "Age"]
        ax.annotate(
            f"Largest Gap {compact_money_label(max_gap)}",
            xy=(max_gap_age, max_gap),
            xytext=(10, 18),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
            arrowprops=dict(arrowstyle="->", alpha=0.5),
        )

    add_last_value_label(ax, ages, df["Total Spending"], f"Spending {compact_money_label(df['Total Spending'].iloc[-1])}")
    add_last_value_label(ax, ages, df["Guaranteed Income"], f"Guaranteed {compact_money_label(df['Guaranteed Income'].iloc[-1])}")

    ax.set_title("Income Gap and Guaranteed Income Coverage", fontsize=15, fontweight="bold", loc="left")
    ax.set_xlabel("Age")
    ax.set_ylabel("Annual Amount")
    style_axis_money(ax)
    ax.legend(loc="upper left", ncol=3, frameon=True)
    fig.tight_layout()
    return fig


def plot_withdrawal_rate_chart(df):
    fig, ax = plt.subplots(figsize=(12, 4.8))

    ages = df["Age"]
    wr = df["Withdrawal Rate"] * 100

    ax.bar(ages, wr, label="Withdrawal Rate %")
    ax.axhline(4, linestyle="--", linewidth=2, label="4% Reference")
    ax.axhline(6, linestyle="--", linewidth=2, label="6% Watch Zone")

    max_wr = wr.max()
    max_age = df.loc[wr.idxmax(), "Age"]
    ax.annotate(
        f"Max {max_wr:.1f}%",
        xy=(max_age, max_wr),
        xytext=(10, 14),
        textcoords="offset points",
        fontsize=9,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", alpha=0.5),
    )

    ax.set_title("Withdrawal Rate Pressure by Age", fontsize=15, fontweight="bold", loc="left")
    ax.set_xlabel("Age")
    ax.set_ylabel("Withdrawal Rate")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{x:.0f}%"))
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper right", frameon=True)
    fig.tight_layout()
    return fig



def run_projection_with_return_sequence(return_sequence):
    """
    Monte Carlo version of run_projection.
    Uses the same core logic, but replaces the fixed growth return with
    a year-by-year random return sequence.
    """
    if st.session_state.current_age <= 0 or st.session_state.retire_age <= 0 or st.session_state.end_age <= 0:
        return pd.DataFrame()

    rows = []
    trad = float(st.session_state.traditional)
    roth = float(st.session_state.roth)
    taxable = float(st.session_state.taxable)
    bucket1 = float(st.session_state.cash)
    base_spending = annual_household_spending()

    ages = list(range(int(st.session_state.current_age), int(st.session_state.end_age) + 1))

    for i, age in enumerate(ages):
        growth_return = float(return_sequence[i]) if i < len(return_sequence) else float(st.session_state.growth_return)

        year_offset = age - int(st.session_state.current_age)
        spouse_age = int(st.session_state.spouse_age) + year_offset if st.session_state.has_spouse else 0
        spouse_alive = bool(st.session_state.has_spouse and spouse_age <= int(st.session_state.spouse_plan_age))
        start_total = trad + roth + taxable + bucket1
        start_trad_for_rmd = trad

        if age < int(st.session_state.retire_age):
            trad += float(st.session_state.annual_contribution) * 0.8
            roth += float(st.session_state.annual_contribution) * 0.2

        if spouse_alive and spouse_age < int(st.session_state.spouse_retire_age):
            trad += float(st.session_state.spouse_annual_contribution) * 0.8
            roth += float(st.session_state.spouse_annual_contribution) * 0.2

        trad *= (1 + growth_return)
        roth *= (1 + growth_return)
        taxable *= (1 + growth_return)
        bucket1 *= (1 + float(st.session_state.safe_return))

        household_retired = age >= int(st.session_state.retire_age) and (not spouse_alive or spouse_age >= int(st.session_state.spouse_retire_age))

        # Do not auto-transfer pre-tax money into Bucket 1.
        # Bucket 1 in this projection represents actual cash/safe assets entered by the user.
        # The 2-bucket module shows suggested targets separately without silently reclassifying
        # traditional assets or using a hardcoded after-tax haircut.

        conversion = 0
        if age >= int(st.session_state.retire_age) and float(st.session_state.annual_conversion) > 0:
            conversion = min(trad, float(st.session_state.annual_conversion))
            trad -= conversion
            roth += conversion

        user_ss = apply_cola_to_social_security(
            social_security_for_age(age, int(st.session_state.user_ss_age), float(st.session_state.user_ss)),
            age,
        )
        spouse_ss = apply_cola_to_social_security(
            social_security_for_age(spouse_age, int(st.session_state.spouse_ss_age), float(st.session_state.spouse_ss)),
            age,
        ) if spouse_alive else 0

        if st.session_state.has_spouse and not spouse_alive:
            if st.session_state.survivor_ss_strategy == "Higher benefit continues":
                spouse_survivor_ss = apply_cola_to_social_security(
                    estimate_social_security_by_claim_age(float(st.session_state.spouse_ss), int(st.session_state.spouse_ss_age)),
                    age,
                )
                ss_income = max(user_ss, spouse_survivor_ss)
            else:
                ss_income = user_ss
        else:
            ss_income = user_ss + spouse_ss

        inc = other_income_for_age(age, spouse_alive)
        other_income = inc["total"]
        guaranteed_income = ss_income + inc["guaranteed"]

        spending = 0
        if household_retired:
            inflation_factor = inflation_factor_from_today(age)
            if st.session_state.has_spouse and not spouse_alive and float(st.session_state.survivor_spending) > 0:
                spending = float(st.session_state.survivor_spending) * inflation_factor
            else:
                spending = annual_spending_for_age(age) * inflation_factor

        healthcare = 0
        healthcare_inflation_factor = inflation_factor_from_today(age)
        if age >= int(st.session_state.retire_age):
            healthcare += float(st.session_state.healthcare) * healthcare_inflation_factor
        if spouse_alive and spouse_age >= int(st.session_state.spouse_retire_age):
            healthcare += float(st.session_state.spouse_healthcare) * healthcare_inflation_factor

        mortgage_payment = annual_mortgage_payment_for_age(age) if household_retired else 0
        total_spending = spending + healthcare + mortgage_payment
        non_portfolio_income = ss_income + other_income

        ordinary_income_before_withdrawals = float(inc.get("taxable", 0)) + conversion
        base_tax_estimate = estimate_federal_tax(ordinary_income_before_withdrawals, social_security_income=ss_income)
        base_federal_tax = base_tax_estimate["federal_tax"]
        income_gap = max(total_spending + base_federal_tax - non_portfolio_income, 0)
        withdrawal_needed = income_gap

        used_b1 = used_taxable = used_trad = used_roth = 0.0
        federal_tax_from_trad = 0.0

        take = min(bucket1, withdrawal_needed)
        bucket1 -= take
        withdrawal_needed -= take
        used_b1 += take

        take = min(taxable, withdrawal_needed)
        taxable -= take
        withdrawal_needed -= take
        used_taxable += take

        if withdrawal_needed > 0:
            take, net_from_trad = gross_traditional_needed_for_net(withdrawal_needed, ordinary_income_before_withdrawals, trad, social_security_income=ss_income)
            federal_tax_from_trad = incremental_federal_tax(ordinary_income_before_withdrawals, take, social_security_income=ss_income)
            trad -= take
            withdrawal_needed -= net_from_trad
            used_trad += take

        take = min(roth, max(withdrawal_needed, 0))
        roth -= take
        withdrawal_needed -= take
        used_roth += take

        rmd_required = calculate_required_minimum_distribution(age, start_trad_for_rmd)
        forced_rmd = 0.0
        federal_tax_from_forced_rmd = 0.0
        taxable_reinvestment = 0.0
        if household_retired and rmd_required > used_trad and trad > 0:
            forced_rmd = min(trad, rmd_required - used_trad)
            federal_tax_from_forced_rmd = incremental_federal_tax(
                ordinary_income_before_withdrawals + used_trad,
                forced_rmd,
                social_security_income=ss_income
            )
            trad -= forced_rmd
            used_trad += forced_rmd
            taxable_reinvestment = max(forced_rmd - federal_tax_from_forced_rmd, 0)
            taxable += taxable_reinvestment

        estimated_federal_tax = base_federal_tax + federal_tax_from_trad + federal_tax_from_forced_rmd
        final_tax_estimate = estimate_federal_tax(ordinary_income_before_withdrawals + used_trad, social_security_income=ss_income)
        actual_withdrawal = used_b1 + used_taxable + used_trad + used_roth
        end_total = trad + roth + taxable + bucket1

        rows.append({
            "Age": age,
            "Start Total": start_total,
            "End Total": end_total,
            "Total Spending": total_spending,
            "Total Non-Portfolio Income": non_portfolio_income,
            "Guaranteed Income": guaranteed_income,
            "Income Gap": income_gap,
            "Estimated Federal Tax": estimated_federal_tax,
            "Provisional Income": final_tax_estimate["provisional_income"],
            "Taxable Social Security": final_tax_estimate["taxable_social_security"],
            "Taxable Ordinary Income": final_tax_estimate["gross_ordinary_income"],
            "Federal Taxable Income": final_tax_estimate["taxable_income"],
            "Effective Federal Tax Rate": estimated_federal_tax / max(final_tax_estimate["gross_ordinary_income"], 1),
            "Portfolio Withdrawal": actual_withdrawal,
            # Backward-compatible alias used throughout the UI for the amount needed from savings.
            "Portfolio Need": actual_withdrawal,
            "RMD Required": rmd_required,
            "Forced RMD": forced_rmd,
            "RMD Reinvested to Taxable": taxable_reinvestment,
            "Unmet Need": max(withdrawal_needed, 0),
            "Withdrawal Rate": actual_withdrawal / max(start_total, 1),
            "Income Coverage Ratio": non_portfolio_income / max(total_spending, 1),
            "Guaranteed Income Coverage Ratio": guaranteed_income / max(total_spending, 1),
            "Annual Return": growth_return,
        })

        if end_total <= 0 and withdrawal_needed > 0:
            break

    return pd.DataFrame(rows)


def run_monte_carlo_simulation(num_simulations, mean_return, volatility, seed=42):
    """
    Runs Monte Carlo simulations and returns summary + full result table.
    """
    rng = np.random.default_rng(seed)
    years = int(st.session_state.end_age) - int(st.session_state.current_age) + 1

    results = []
    paths = []

    for sim in range(num_simulations):
        returns = rng.normal(loc=mean_return, scale=volatility, size=years)
        returns = np.clip(returns, -0.45, 0.45)

        sim_df = run_projection_with_return_sequence(returns)

        if sim_df.empty:
            ending = 0
            success = False
            depletion_age = None
            max_wr = 0
        else:
            ending = float(sim_df["End Total"].iloc[-1])
            unmet = float(sim_df["Unmet Need"].sum())
            reached_end = int(sim_df["Age"].iloc[-1]) >= int(st.session_state.end_age)
            success = reached_end and ending > 0 and unmet <= 0

            depletion_age = None
            failed_rows = sim_df[(sim_df["End Total"] <= 0) | (sim_df["Unmet Need"] > 0)]
            if not failed_rows.empty:
                depletion_age = int(failed_rows["Age"].iloc[0])

            max_wr = float(sim_df["Withdrawal Rate"].max())

            paths.append(
                sim_df[["Age", "End Total"]]
                .assign(Simulation=sim)
            )

        results.append({
            "Simulation": sim + 1,
            "Success": success,
            "Ending Portfolio": ending,
            "Depletion Age": depletion_age,
            "Max Withdrawal Rate": max_wr,
            "Average Return": float(np.mean(returns)),
            "Worst Year Return": float(np.min(returns)),
        })

    results_df = pd.DataFrame(results)

    if paths:
        paths_df = pd.concat(paths, ignore_index=True)
    else:
        paths_df = pd.DataFrame(columns=["Age", "End Total", "Simulation"])

    success_rate = float(results_df["Success"].mean()) if not results_df.empty else 0
    median_ending = float(results_df["Ending Portfolio"].median()) if not results_df.empty else 0
    p10_ending = float(results_df["Ending Portfolio"].quantile(0.10)) if not results_df.empty else 0
    p90_ending = float(results_df["Ending Portfolio"].quantile(0.90)) if not results_df.empty else 0

    return {
        "success_rate": success_rate,
        "median_ending": median_ending,
        "p10_ending": p10_ending,
        "p90_ending": p90_ending,
        "results_df": results_df,
        "paths_df": paths_df,
    }


def plot_monte_carlo_paths(paths_df, results_df):
    fig, ax = plt.subplots(figsize=(12, 5.8))

    if paths_df.empty:
        ax.text(0.5, 0.5, "No simulation paths available", ha="center", va="center")
        return fig

    # Plot a limited sample for readability.
    sample_sims = paths_df["Simulation"].drop_duplicates().head(80)

    for sim in sample_sims:
        path = paths_df[paths_df["Simulation"] == sim]
        ax.plot(path["Age"], path["End Total"], linewidth=0.8, alpha=0.18)

    percentile_df = (
        paths_df.groupby("Age")["End Total"]
        .quantile([0.10, 0.50, 0.90])
        .unstack()
        .reset_index()
    )

    ax.plot(percentile_df["Age"], percentile_df[0.50], linewidth=3, label="Median Path")
    ax.plot(percentile_df["Age"], percentile_df[0.10], linewidth=2, linestyle="--", label="10th Percentile")
    ax.plot(percentile_df["Age"], percentile_df[0.90], linewidth=2, linestyle="--", label="90th Percentile")

    ax.axhline(0, linewidth=1)
    ax.set_title("Monte Carlo Portfolio Paths", fontsize=15, fontweight="bold", loc="left")
    ax.set_xlabel("Age")
    ax.set_ylabel("Portfolio Balance")
    style_axis_money(ax)
    ax.legend(loc="upper left", frameon=True)
    fig.tight_layout()
    return fig


def plot_monte_carlo_ending_distribution(results_df):
    fig, ax = plt.subplots(figsize=(12, 5.2))

    endings = results_df["Ending Portfolio"] if not results_df.empty else pd.Series(dtype=float)

    if endings.empty:
        ax.text(0.5, 0.5, "No simulation results available", ha="center", va="center")
        return fig

    ax.hist(endings, bins=30, alpha=0.85)
    ax.axvline(endings.median(), linewidth=3, label=f"Median {compact_money_label(endings.median())}")
    ax.axvline(endings.quantile(0.10), linewidth=2, linestyle="--", label=f"10th % {compact_money_label(endings.quantile(0.10))}")
    ax.axvline(endings.quantile(0.90), linewidth=2, linestyle="--", label=f"90th % {compact_money_label(endings.quantile(0.90))}")

    ax.set_title("Ending Portfolio Distribution", fontsize=15, fontweight="bold", loc="left")
    ax.set_xlabel("Ending Portfolio")
    ax.set_ylabel("Number of Simulations")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: compact_money_label(x)))
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper right", frameon=True)
    fig.tight_layout()
    return fig



def run_stress_test_scenario(
    scenario_name,
    forced_returns=None,
    inflation_override=None,
    spending_multiplier=1.0,
):
    years = int(st.session_state.end_age) - int(st.session_state.current_age) + 1
    base_return = float(st.session_state.growth_return)

    if forced_returns is None:
        forced_returns = [base_return] * years
    else:
        forced_returns = list(forced_returns)
        if len(forced_returns) < years:
            forced_returns.extend([base_return] * (years - len(forced_returns)))

    original_inflation = float(st.session_state.inflation)
    original_flat_spending = st.session_state.flat_monthly_spending
    original_budget_values = {key: st.session_state.get(key, 0) for key, _ in budget_keys}

    try:
        if inflation_override is not None:
            st.session_state.inflation = inflation_override

        if spending_multiplier != 1.0:
            if st.session_state.budget_mode == "Flat monthly number":
                st.session_state.flat_monthly_spending = original_flat_spending * spending_multiplier
            else:
                for key, _ in budget_keys:
                    st.session_state[key] = float(original_budget_values.get(key, 0) or 0) * spending_multiplier

        sim_df = run_projection_with_return_sequence(forced_returns)

    finally:
        st.session_state.inflation = original_inflation
        st.session_state.flat_monthly_spending = original_flat_spending
        for key, value in original_budget_values.items():
            st.session_state[key] = value

    if sim_df.empty:
        return {
            "Scenario": scenario_name,
            "Blueprint Score": 0,
            "Blueprint Label": "Incomplete",
            "Result": "Failed",
            "Lasts Until Age": int(st.session_state.current_age),
            "Years Covered": 0,
            "Ending Portfolio": 0,
            "Max Withdrawal Rate": 0,
            "Income Coverage": 0,
        }

    rtv_score, rtv_label, _ = calculate_rtv_score(sim_df)

    ending = float(sim_df["End Total"].iloc[-1])
    max_wr = float(sim_df["Withdrawal Rate"].max())
    income_coverage = float(sim_df["Income Coverage Ratio"].mean())

    failed_rows = sim_df[(sim_df["End Total"] <= 0) | (sim_df["Unmet Need"] > 0)]

    if not failed_rows.empty:
        lasts_until_age = int(failed_rows["Age"].iloc[0])
    else:
        lasts_until_age = int(sim_df["Age"].iloc[-1])

    years_covered = max(lasts_until_age - int(st.session_state.current_age), 0)

    failed = (
        sim_df["Unmet Need"].sum() > 0
        or ending <= 0
        or int(sim_df["Age"].iloc[-1]) < int(st.session_state.end_age)
    )

    return {
        "Scenario": scenario_name,
        "Blueprint Score": rtv_score,
        "Blueprint Label": rtv_label,
        "Result": "Failed" if failed else "Survived",
        "Lasts Until Age": lasts_until_age,
        "Years Covered": years_covered,
        "Ending Portfolio": ending,
        "Max Withdrawal Rate": max_wr,
        "Income Coverage": income_coverage,
    }

def plot_stress_test_chart(stress_df):
    fig, ax = plt.subplots(figsize=(12, 5.5))

    bars = ax.bar(stress_df["Scenario"], stress_df["Blueprint Score"])

    for bar, score in zip(bars, stress_df["Blueprint Score"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            score + 1,
            f"{score}",
            ha="center",
            fontsize=10,
            fontweight="bold",
        )

    ax.axhline(75, linestyle="--", linewidth=2, label="Likely Viable")
    ax.axhline(90, linestyle="--", linewidth=2, label="Very Strong")

    ax.set_ylim(0, 105)
    ax.set_ylabel("Blueprint Score")
    ax.set_title("Stress Test Blueprint Scores", fontsize=15, fontweight="bold", loc="left")
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend()

    fig.tight_layout()
    return fig



def fig_to_reportlab_image(fig, width=6.8 * inch, height=3.6 * inch):
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format="png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    img_buffer.seek(0)
    return Image(img_buffer, width=width, height=height)


def make_pdf_table(rows, col_widths=None, header=True, font_size=None):
    """
    Build PDF tables with wrapped text so columns do not overlap.
    ReportLab Table cells do not reliably wrap plain strings, so every
    cell is converted to a Paragraph with a small, readable style.
    """
    table_body_style = ParagraphStyle(
        "PDFTableBody",
        fontName="Helvetica",
        fontSize=font_size or 7.6,
        leading=(font_size or 7.6) + 1.8,
        textColor=colors.HexColor("#111827"),
        wordWrap="LTR",
        splitLongWords=True,
        spaceAfter=0,
    )
    table_header_style = ParagraphStyle(
        "PDFTableHeader",
        fontName="Helvetica-Bold",
        fontSize=(font_size or 7.6) + 0.3,
        leading=(font_size or 7.6) + 2.1,
        textColor=colors.white,
        wordWrap="LTR",
        splitLongWords=True,
        spaceAfter=0,
    )

    def cell_to_para(value, is_header=False):
        value = "" if value is None else str(value)
        value = xml_escape(value).replace("\n", "<br/>")
        return Paragraph(value, table_header_style if is_header else table_body_style)

    wrapped_rows = []
    for r_idx, row in enumerate(rows):
        wrapped_rows.append([cell_to_para(cell, header and r_idx == 0) for cell in row])

    table = Table(wrapped_rows, colWidths=col_widths, hAlign="LEFT", repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]

    if header:
        style.extend([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#111827")),
        ])

    table.setStyle(TableStyle(style))
    return table


def build_action_plan_rows(df, rtv_score):
    actions = build_rtv_improvement_recommendations(df, rtv_score)
    top = [a for a in actions if a["Blueprint Impact"] > 0][:7]

    rows = [["Possible Recommendation", "Why It May Help", "Blueprint Impact", "New Blueprint Score"]]

    if not top:
        rows.append([
            "Maintain current plan and monitor annually",
            "The current plan already appears strong under the current assumptions.",
            "0",
            str(rtv_score),
        ])
    else:
        for a in top:
            action = a["Action"]

            if "Reduce spending" in action:
                why = "Lowers portfolio withdrawals and reduces sequence-of-return pressure."
            elif "Delay retirement" in action:
                why = "Adds more saving years and shortens the withdrawal period."
            elif "contributions" in action:
                why = "Builds a larger portfolio before retirement begins."
            elif "Social Security" in action:
                why = "May increase guaranteed income and reduce portfolio withdrawals later."
            elif "Plan to age" in action:
                why = "Shortens the modeled planning horizon, but reduces longevity protection."
            else:
                why = "Improves one or more plan assumptions in the projection."

            rows.append([
                action,
                why,
                f"+{a['Blueprint Impact']}" if a["Blueprint Impact"] > 0 else str(a["Blueprint Impact"]),
                str(a["New Blueprint Score"]),
            ])

    return rows


def build_report_best_retirement_age_guidance():
    """
    Builds a concise retirement-age recommendation for the PDF report using the
    same optimizer logic already used inside the app.
    """
    try:
        current_age = int(st.session_state.get("current_age", 0) or 0)
        planning_age = int(st.session_state.get("end_age", 90) or 90)
        if current_age <= 0 or planning_age <= current_age + 1:
            return None

        test_start = max(current_age + 1, min(int(st.session_state.get("retire_age", current_age + 1) or current_age + 1) - 3, planning_age - 1))
        test_end = min(75, planning_age - 1, max(int(st.session_state.get("retire_age", current_age + 1) or current_age + 1) + 7, current_age + 10))
        if test_end < test_start:
            test_start = current_age + 1
            test_end = min(75, planning_age - 1)

        opt = build_retirement_age_optimizer_results(
            start_age=test_start,
            end_age=test_end,
            safety_target=max(250000, annual_household_spending() * 2),
        )
        if not opt or opt.get("recommended") is None:
            return opt
        return opt
    except Exception:
        return None


def build_best_age_explanation(opt):
    """Plain-English explanation for why the report selected the recommended age."""
    if not opt or opt.get("recommended") is None:
        return "The report could not calculate a best retirement age because the projection did not have enough complete inputs or no tested age appeared to work."

    rec = opt["recommended"]
    earliest = opt.get("earliest")
    safest = opt.get("safest")
    rec_age = int(rec["Retirement Age"])
    parts = [
        f"Age {rec_age} looks like the best tested retirement age because it balances retiring sooner with a {int(rec['Blueprint Score'])}/100 Blueprint Score, projected ending portfolio of {money(rec['Ending Portfolio'])}, and a maximum withdrawal rate of {pct(rec['Max Withdrawal Rate'])}.",
    ]

    if earliest is not None and int(earliest["Retirement Age"]) < rec_age:
        parts.append(
            f"Age {int(earliest['Retirement Age'])} appears to be the earliest tested age that works, but age {rec_age} provides more cushion and/or less withdrawal pressure."
        )

    if safest is not None and int(safest["Retirement Age"]) > rec_age:
        parts.append(
            f"Age {int(safest['Retirement Age'])} is the safest tested age by ending balance, but the report favors age {rec_age} because it may allow retirement sooner while still keeping a reasonable margin."
        )

    if int(rec.get("Healthcare Gap Years", 0)) > 0:
        parts.append(
            f"This age still has about {int(rec['Healthcare Gap Years'])} year(s) before Medicare, so healthcare and ACA planning remain important."
        )

    if int(rec.get("Years Until Social Security", 0)) > 0:
        parts.append(
            f"The portfolio may need to bridge about {int(rec['Years Until Social Security'])} year(s) before Social Security starts."
        )

    return " ".join(parts)


def build_best_age_pdf_rows(opt):
    rows = [["Age Result", "Age", "Blueprint Score", "Ending Portfolio", "Why it matters"]]
    if not opt or opt.get("recommended") is None:
        rows.append(["Best tested age", "N/A", "N/A", "N/A", "Not enough complete inputs or no tested age appeared to work."])
        return rows

    for label, key, why in [
        ("Earliest age that works", "earliest", "First tested age where the plan appears to last through the planning age."),
        ("Best age to retire", "recommended", "Best balance of score, cushion, withdrawal pressure, healthcare gap, Social Security gap, and retiring sooner."),
        ("Safest tested age", "safest", "Tested age with the highest projected ending portfolio."),
    ]:
        row = opt.get(key)
        if row is None:
            rows.append([label, "N/A", "N/A", "N/A", "No tested age met this condition."])
        else:
            rows.append([
                label,
                str(int(row["Retirement Age"])),
                f"{int(row['Blueprint Score'])}/100",
                money(row["Ending Portfolio"]),
                why,
            ])
    return rows


def build_score_improvement_detail_rows(df, rtv_score, limit=6):
    """More detailed score-improvement table for the PDF report."""
    rows = [["Recommendation", "Why it improves the score", "Score Impact", "New Score", "Projected Ending Portfolio"]]
    try:
        actions = build_rtv_improvement_recommendations(df, rtv_score)
    except Exception:
        actions = []

    top = [a for a in actions if a.get("Blueprint Impact", 0) > 0][:limit]
    if not top:
        rows.append([
            "Keep monitoring the plan",
            "The current score is already strong or no simple test created a higher score. Stress-test inflation, healthcare, taxes, and market returns annually.",
            "+0",
            f"{rtv_score}/100",
            money(float(df["End Total"].iloc[-1])) if df is not None and not df.empty else "N/A",
        ])
        return rows

    for a in top:
        action = a.get("Action", "Review assumption")
        if "Reduce spending" in action:
            why = "Reduces annual portfolio withdrawals and lowers sequence-of-return risk."
        elif "Delay retirement" in action:
            why = "Adds saving years, shortens the drawdown period, and gives the portfolio more time to compound."
        elif "contributions" in action:
            why = "Builds the retirement base before withdrawals begin."
        elif "Social Security" in action:
            why = "Can increase reliable income later and reduce pressure on investments."
        elif "Plan to age" in action:
            why = "Improves the modeled result, but should be used carefully because longevity risk still matters."
        else:
            why = "Improves one or more assumptions used by the projection model."

        impact = int(a.get("Blueprint Impact", 0))
        rows.append([
            action,
            why,
            f"+{impact}" if impact > 0 else str(impact),
            f"{int(a.get('New Blueprint Score', rtv_score))}/100",
            money(a.get("Ending Portfolio", 0)),
        ])
    return rows


def build_general_recommendation_paragraphs(df, rtv_score):
    ending = float(df["End Total"].iloc[-1])
    starting = float(df["Start Total"].iloc[0])
    max_wr = float(df["Withdrawal Rate"].max())
    avg_wr = float(df["Withdrawal Rate"].mean())
    income_coverage = float(df["Income Coverage Ratio"].mean())
    unmet_need = float(df["Unmet Need"].sum())

    recs = []

    if unmet_need > 0:
        recs.append("Address unmet spending needs first. This may require reducing spending, retiring later, increasing income, or increasing savings before retirement.")

    if max_wr > 0.07:
        recs.append("Review early-retirement spending. The plan shows a high maximum withdrawal rate, which can increase sequence-of-return risk.")
    elif max_wr > 0.05:
        recs.append("Monitor withdrawal pressure. A larger Bucket 1 or slightly lower spending could improve resilience.")
    else:
        recs.append("Withdrawal pressure appears reasonable under the current assumptions.")

    if income_coverage < 0.35:
        recs.append("Consider ways to increase dependable income, such as Social Security timing, part-time work, pension optimization, or other reliable income sources.")
    elif income_coverage >= 0.60:
        recs.append("Income coverage is a strength. Non-portfolio income is helping reduce reliance on investment withdrawals.")

    if ending > starting:
        recs.append("The ending portfolio is higher than the starting portfolio. This may suggest room for additional lifestyle spending, gifting, Roth conversion planning, or legacy planning.")
    elif ending > 500000:
        recs.append("The plan leaves a meaningful ending cushion, but should still be stress-tested for inflation, healthcare, and market timing.")
    else:
        recs.append("The ending cushion is limited. Protecting spending flexibility and reducing downside risk should be priorities.")

    if float(st.session_state.traditional or 0) > max(float(st.session_state.roth or 0) * 3, 250000):
        recs.append("Traditional retirement balances are much larger than Roth balances. Roth conversion planning may help manage future tax risk, especially before RMDs.")

    if int(st.session_state.retire_age or 0) < 65:
        recs.append("Because retirement is before Medicare age, healthcare costs and ACA subsidy planning should be reviewed carefully.")

    recs.append("Revisit the plan at least annually or after major life changes such as job changes, market changes, Social Security decisions, healthcare changes, or relocation.")

    return recs

def build_pdf_report(df):
    """
    Builds a polished PDF retirement report and returns bytes.
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#111827"),
        spaceAfter=10,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=14,
    )

    h1 = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#111827"),
        spaceBefore=14,
        spaceAfter=8,
    )

    h2 = ParagraphStyle(
        "SmallHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=8,
        spaceAfter=6,
    )

    body = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#374151"),
        spaceAfter=7,
    )

    small = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#6b7280"),
    )

    story = []

    rtv_score, rtv_label, rtv_reasons = calculate_rtv_score(df)
    ending = float(df["End Total"].iloc[-1])
    starting = float(df["Start Total"].iloc[0])
    max_wr = float(df["Withdrawal Rate"].max())
    avg_income_coverage = float(df["Income Coverage Ratio"].mean())
    total_spending = float(df["Total Spending"].sum())
    total_withdrawals = float(df["Portfolio Withdrawal"].sum())

    # Cover
    story.append(Paragraph("Your Personalized Retirement Blueprint", title_style))
    story.append(Paragraph(
        "A premium-style planning report based on the current assumptions entered in Retirement Blueprint 101.",
        subtitle_style
    ))

    plan_type = "Couple / household plan" if st.session_state.has_spouse else "Individual plan"

    score_color = "#16a34a" if rtv_score >= 80 else ("#f59e0b" if rtv_score >= 60 else "#dc2626")

    summary_rows = [
        [
            Paragraph(f"<b><font color='{score_color}'>{rtv_score}/100</font></b><br/>Blueprint Score", body),
            Paragraph(f"<b>{rtv_label}</b><br/>Blueprint Label", body),
            Paragraph(f"<b>{money(ending)}</b><br/>End of Plan Portfolio", body),
            Paragraph(f"<b>{pct(max_wr)}</b><br/>Max Withdrawal Rate", body),
        ],
        [
            Paragraph(f"<b>{plan_type}</b><br/>Plan Type", body),
            Paragraph(f"<b>{st.session_state.current_age}</b><br/>Current Age", body),
            Paragraph(f"<b>{st.session_state.retire_age}</b><br/>Retirement Age", body),
            Paragraph(f"<b>{st.session_state.end_age}</b><br/>Plan Through Age", body),
        ],
    ]

    card_table = Table(summary_rows, colWidths=[1.7 * inch] * 4)
    card_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#dbeafe")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(card_table)
    story.append(Spacer(1, 0.14 * inch))

    story.append(Paragraph("Executive Summary", h1))

    summary_text = (
        f"The current projection starts with {money(starting)} and ends with {money(ending)} "
        f"at age {int(st.session_state.end_age)}. The RTV score is {rtv_score}/100 ({rtv_label}). "
        f"The plan's highest projected withdrawal rate is {pct(max_wr)}, and average non-portfolio income "
        f"coverage is {pct(avg_income_coverage)}. The projection includes federal tax bracket estimates, "
        f"taxable Social Security logic, and {get_tax_settings()['label']} filing status for {get_tax_year()}."
    )
    story.append(Paragraph(summary_text, body))

    best_age_opt = build_report_best_retirement_age_guidance()
    if best_age_opt and best_age_opt.get("recommended") is not None:
        recommended_age = int(best_age_opt["recommended"]["Retirement Age"])
        story.append(Paragraph("Best Age to Retire Estimate", h2))
        story.append(Paragraph(build_best_age_explanation(best_age_opt), body))
        story.append(make_pdf_table(build_best_age_pdf_rows(best_age_opt), col_widths=[1.4*inch, 0.55*inch, 0.9*inch, 1.2*inch, 2.45*inch], font_size=7.1))
    else:
        story.append(Paragraph("Best Age to Retire Estimate", h2))
        story.append(Paragraph("The report could not calculate a best retirement age yet. Complete the core inputs, then rerun the report to compare retirement ages.", body))

    if rtv_reasons:
        story.append(Paragraph("Main score drivers:", h2))
        for reason in rtv_reasons[:5]:
            story.append(Paragraph(f"- {reason}", body))

    story.append(Paragraph("<b>Educational purposes only:</b> This report is for general education and planning discussion only. It is not financial, tax, legal, insurance, or investment advice. Users should verify assumptions and consult qualified professionals before making retirement, tax, insurance, or investment decisions.", small))
    story.append(PageBreak())

    # Assumptions
    story.append(Paragraph("Plan Assumptions", h1))

    assumptions_rows = [
        ["Input", "Value"],
        ["Current Age", str(st.session_state.current_age)],
        ["Retirement Age", str(st.session_state.retire_age)],
        ["Plan Through Age", str(st.session_state.end_age)],
        ["Plan Type", plan_type],
        ["Traditional / Pre-tax", money(st.session_state.traditional)],
        ["Roth", money(st.session_state.roth)],
        ["Taxable", money(st.session_state.taxable)],
        ["Bucket 1 / Cash", money(st.session_state.cash)],
        ["Annual Contributions", money(st.session_state.annual_contribution)],
        ["Annual Spending Before Healthcare", money(annual_household_spending())],
        ["Annual Healthcare", money(st.session_state.healthcare)],
        ["Social Security Start Age", str(st.session_state.user_ss_age)],
        ["Annual Social Security", money(st.session_state.user_ss)],
        ["Federal Tax Year", str(get_tax_year())],
        ["Federal Filing Status", get_tax_settings()["label"]],
        ["Federal Standard Deduction", money(get_tax_settings()["standard_deduction"])],
        ["Growth Return", pct(st.session_state.growth_return)],
        ["Safe Return", pct(st.session_state.safe_return)],
        ["Inflation", pct(st.session_state.inflation)],
        ["Annual Roth Conversion", money(st.session_state.annual_conversion)],
        ["Bucket 1 Target Years", str(st.session_state.bucket1_years)],
    ]

    if st.session_state.has_spouse:
        assumptions_rows.extend([
            ["Spouse Age", str(st.session_state.spouse_age)],
            ["Spouse Retirement Age", str(st.session_state.spouse_retire_age)],
            ["Spouse Annual Social Security", money(st.session_state.spouse_ss)],
            ["Spouse Annual Healthcare", money(st.session_state.spouse_healthcare)],
        ])

    story.append(make_pdf_table(assumptions_rows, col_widths=[3.1 * inch, 3.1 * inch]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Federal Tax Estimate", h2))
    total_federal_tax = float(df.get("Estimated Federal Tax", pd.Series(dtype=float)).sum()) if "Estimated Federal Tax" in df.columns else 0
    total_taxable_ss = float(df.get("Taxable Social Security", pd.Series(dtype=float)).sum()) if "Taxable Social Security" in df.columns else 0
    tax_rows = [
        ["Tax Assumption", "Value"],
        ["Tax Year", str(get_tax_year())],
        ["Filing Status", get_tax_settings()["label"]],
        ["Standard Deduction", money(get_tax_settings()["standard_deduction"])],
        ["Projected Federal Tax Across Plan", money(total_federal_tax)],
        ["Projected Taxable Social Security Across Plan", money(total_taxable_ss)],
    ]
    story.append(make_pdf_table(tax_rows, col_widths=[3.1 * inch, 3.1 * inch]))
    story.append(Paragraph(tax_assumption_note(), small))

    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Premium 2-Bucket Strategy", h2))
    bucket_rows = [["Bucket", "Purpose", "Suggested Amount", "Target", "Risk"]]
    for _, b in build_three_bucket_strategy(df).iterrows():
        bucket_rows.append([b["Bucket"], b["Purpose"], money(b["Suggested Amount"]), str(b["Target Years"]), b["Risk Level"]])
    story.append(make_pdf_table(bucket_rows, col_widths=[0.9*inch, 2.0*inch, 1.3*inch, 0.9*inch, 1.1*inch], font_size=7.2))

    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Premium Scenario Comparison", h2))
    scenario_rows = [["Retire Age", "Score", "Ending Portfolio", "Max WR", "Est. Federal Tax"]]
    current_age = int(st.session_state.retire_age or st.session_state.current_age or 0)
    for age in sorted(set([max(int(st.session_state.current_age or 0), current_age-2), current_age, current_age+1, current_age+2, current_age+5])):
        if age <= int(st.session_state.end_age or 90):
            r = run_projection_with_temp_retire_age(age)
            if r:
                scenario_rows.append([str(r["Retirement Age"]), f"{r['Blueprint Score']}/100", money(r["Ending Portfolio"]), pct(r["Max Withdrawal Rate"]), money(r["Estimated Federal Tax"])])
    if len(scenario_rows) > 1:
        story.append(make_pdf_table(scenario_rows, col_widths=[1.0*inch, 1.0*inch, 1.5*inch, 1.0*inch, 1.6*inch], font_size=7.4))
    story.append(PageBreak())

    # Charts
    story.append(Paragraph("Dashboard Charts", h1))
    story.append(Paragraph("Portfolio balance by account type", h2))
    story.append(fig_to_reportlab_image(plot_portfolio_area_chart(df)))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("Spending, income, and portfolio withdrawals", h2))
    story.append(fig_to_reportlab_image(plot_spending_income_bar_chart(df)))
    story.append(PageBreak())

    story.append(Paragraph("Income gap and withdrawal pressure", h1))
    story.append(Paragraph("Income gap", h2))
    story.append(fig_to_reportlab_image(plot_income_gap_chart(df)))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Withdrawal rate pressure", h2))
    story.append(fig_to_reportlab_image(plot_withdrawal_rate_chart(df)))
    story.append(PageBreak())

    # Recommendations
    story.append(Paragraph("Possible Recommendations", h1))
    story.append(Paragraph(
        "The ideas below are educational planning suggestions generated from the projection assumptions. "
        "They are not personalized financial advice. They are intended to help the user identify what to review, test, or discuss with a qualified professional.",
        body
    ))

    story.append(Paragraph("Planning Observations", h2))
    for rec in build_general_recommendation_paragraphs(df, rtv_score):
        story.append(Paragraph(f"- {rec}", body))

    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Blueprint Improvement Ideas", h2))
    action_rows = build_action_plan_rows(df, rtv_score)
    story.append(make_pdf_table(action_rows, col_widths=[2.15 * inch, 2.55 * inch, 0.95 * inch, 0.95 * inch]))

    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Ways to Improve Your Blueprint Score", h2))
    story.append(Paragraph(
        "These are the highest-impact levers the app tested against the current blueprint. The goal is not to force every change, but to show which assumptions most improve retirement readiness.",
        body
    ))
    story.append(make_pdf_table(build_score_improvement_detail_rows(df, rtv_score), col_widths=[1.55*inch, 2.15*inch, 0.75*inch, 0.75*inch, 1.35*inch], font_size=7.0))

    if 'best_age_opt' not in locals():
        best_age_opt = build_report_best_retirement_age_guidance()
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Best Age to Retire and Why", h2))
    story.append(Paragraph(build_best_age_explanation(best_age_opt), body))

    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Can the user spend more?", h2))

    spend_more_rows = build_spend_more_tests(rtv_score)
    spend_rows = [["Scenario", "New Monthly Spending", "New Blueprint Score", "Ending Portfolio"]]
    for row in spend_more_rows:
        spend_rows.append([
            row["Scenario"],
            money(row["New Monthly Spending"]),
            str(row["New Blueprint Score"]),
            money(row["Ending Portfolio"]),
        ])
    story.append(make_pdf_table(spend_rows, col_widths=[2.0 * inch, 1.55 * inch, 1.05 * inch, 1.9 * inch]))
    story.append(PageBreak())

    # Monte Carlo
    story.append(Paragraph("Monte Carlo Summary", h1))
    if "mc_result" in st.session_state:
        mc = st.session_state.mc_result
        mc_rows = [
            ["Metric", "Value"],
            ["Probability of Success", pct(mc["success_rate"])],
            ["Median Ending Portfolio", money(mc["median_ending"])],
            ["10th Percentile Ending", money(mc["p10_ending"])],
            ["90th Percentile Ending", money(mc["p90_ending"])],
        ]
        story.append(make_pdf_table(mc_rows, col_widths=[3.1 * inch, 3.1 * inch]))
        story.append(Spacer(1, 0.15 * inch))
        story.append(fig_to_reportlab_image(plot_monte_carlo_paths(mc["paths_df"], mc["results_df"])))
    else:
        story.append(Paragraph("Monte Carlo has not been run yet. Run the Monte Carlo page before exporting if you want this section populated.", body))

    story.append(PageBreak())

    # Stress Tests
    story.append(Paragraph("Stress Test Summary", h1))
    if "stress_results_df" in st.session_state:
        stress_df = st.session_state.stress_results_df.copy()
        stress_rows = [["Scenario", "RTV", "Result", "Lasts Until", "Ending Portfolio"]]

        for _, row in stress_df.iterrows():
            stress_rows.append([
                str(row.get("Scenario", "")),
                str(row.get("Blueprint Score", "")),
                str(row.get("Result", "")),
                str(row.get("Lasts Until Age", "")),
                money(row.get("Ending Portfolio", 0)),
            ])

        story.append(make_pdf_table(stress_rows, col_widths=[2.1 * inch, 0.7 * inch, 1.0 * inch, 1.2 * inch, 1.7 * inch]))
        story.append(Spacer(1, 0.15 * inch))
        story.append(fig_to_reportlab_image(plot_stress_test_chart(stress_df)))
    else:
        story.append(Paragraph("Stress tests have not been run yet. Run the Stress Tests page before exporting if you want this section populated.", body))

    story.append(PageBreak())

    # Saved retirement places
    story.append(Paragraph("Retirement Location Shortlist", h1))
    saved_places = st.session_state.get("saved_retirement_places", [])
    if saved_places:
        saved_df = pd.DataFrame(saved_places)
        loc_rows = [["Place", "State", "Fit", "Est. Tax", "Why It Fits", "Watch-Out"]]
        for _, row in saved_df.head(8).iterrows():
            loc_rows.append([
                str(row.get("Place", "")),
                str(row.get("State", "")),
                str(int(row.get("Recommended Fit Score", 0))) if pd.notna(row.get("Recommended Fit Score", 0)) else "",
                money(row.get("Estimated Annual State/Local Tax", 0)),
                str(row.get("Why It Fits", "")),
                str(row.get("Watch Outs", "")),
            ])
        story.append(make_pdf_table(loc_rows, col_widths=[0.85 * inch, 0.75 * inch, 0.45 * inch, 0.75 * inch, 2.05 * inch, 1.75 * inch]))
        story.append(Paragraph("Location scores are educational planning estimates based on simplified state/local tax, affordability, healthcare, lifestyle, climate, and recreation assumptions.", small))
    else:
        story.append(Paragraph("No retirement locations have been saved yet. Use the Places to Retire page to save favorite states or cities before exporting the report.", body))

    story.append(PageBreak())

    # Projection snapshot
    story.append(Paragraph("Projection Snapshot", h1))
    projection_cols = [
        "Age", "End Total", "Total Spending", "Social Security",
        "Total Other Income", "Portfolio Withdrawal", "Withdrawal Rate"
    ]
    available_cols = [c for c in projection_cols if c in df.columns]
    snap = df[available_cols].copy()

    # Show every 5 years plus first/last
    snap = snap[(snap["Age"] % 5 == 0) | (snap["Age"] == df["Age"].iloc[0]) | (snap["Age"] == df["Age"].iloc[-1])]

    rows = [available_cols]
    for _, row in snap.iterrows():
        out_row = []
        for col in available_cols:
            if col == "Age":
                out_row.append(str(int(row[col])))
            elif col == "Withdrawal Rate":
                out_row.append(pct(row[col]))
            else:
                out_row.append(money(row[col]))
        rows.append(out_row)

    story.append(make_pdf_table(rows, col_widths=[0.55 * inch, 1.15 * inch, 1.1 * inch, 1.05 * inch, 1.15 * inch, 1.15 * inch, 0.85 * inch]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#6b7280"))
        canvas.drawString(0.55 * inch, 0.32 * inch, "Retirement Blueprint 101 - Educational Planning Report")
        canvas.drawRightString(7.95 * inch, 0.32 * inch, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)

    buffer.seek(0)
    return buffer.getvalue()



def build_saved_scenario_ai_context(name, summary, recommendations):
    return f"""
Saved scenario name: {name}

Key numbers:
- RTV score: {summary.get('score')}/100
- RTV label: {summary.get('label')}
- Current age: {summary.get('current_age')}
- Retirement age: {summary.get('retire_age')}
- Plan-through age: {summary.get('end_age')}
- Years to retirement: {summary.get('years_to_retire')}
- Total assets: {summary.get('total_assets')}
- Traditional/pre-tax assets: {summary.get('traditional')}
- Roth assets: {summary.get('roth')}
- Taxable assets: {summary.get('taxable')}
- Cash/Bucket 1: {summary.get('cash')}
- Monthly spending: {summary.get('monthly_spending')}
- Annual spending: {summary.get('annual_spending')}
- Annual income: {summary.get('annual_income')}
- Income coverage ratio: {summary.get('income_coverage')}
- Max withdrawal rate: {summary.get('rough_wr')}
- Growth return assumption: {summary.get('growth_return')}
- Safe return assumption: {summary.get('safe_return')}
- Inflation assumption: {summary.get('inflation')}
- Bucket 1 years: {summary.get('bucket1_years')}
- Annual Roth conversion: {summary.get('annual_conversion')}

Rule-based recommendations already identified:
{chr(10).join("- " + r for r in recommendations)}
"""


def generate_ai_recommendation_for_saved_scenario(name, summary, recommendations):
    """
    Uses OpenAI to generate a plain-English educational recommendation
    for one saved scenario.
    """
    try:
        from openai import OpenAI
        api_key = st.secrets.get("OPENAI_API_KEY", "")

        if not api_key:
            return "OpenAI API key is not configured. Add OPENAI_API_KEY in Streamlit Secrets to enable AI recommendations."

        client = OpenAI(api_key=api_key)

        prompt = f"""
You are an educational retirement planning assistant inside a retirement calculator.
You are not a financial advisor, CPA, attorney, insurance agent, or investment advisor.

Generate a concise, helpful recommendation for this saved retirement scenario.

Tone:
- Clear
- Friendly
- Practical
- No fearmongering
- No promises
- No personalized financial advice
- Educational only

Format:
1. Short overall read
2. Top 3 opportunities to improve the plan
3. Top 3 risks to review
4. One practical next step

Important:
- Explain using the scenario numbers.
- Do not invent missing information.
- Do not say the user should buy a specific product.
- Mention that this is educational only.

Scenario context:
{build_saved_scenario_ai_context(name, summary, recommendations)}
"""

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            max_output_tokens=700,
        )

        return response.output_text

    except Exception as e:
        return f"AI recommendation failed: {e}"



def get_phase1_retirement_places_data():
    """
    Phase 1 static scoring model.
    Scores are directional educational estimates on a 0-100 scale.
    They are intended for comparison, not tax advice.
    """
    return pd.DataFrame([
        {
            "State": "Florida",
            "Example Places": "Sarasota; The Villages; Naples; St. Augustine",
            "Tax Score": 96,
            "Cost Score": 68,
            "Healthcare Score": 82,
            "Lifestyle Score": 92,
            "Climate Score": 90,
            "Overall Score": 86,
            "Why It Ranks Well": "No state income tax; strong retiree infrastructure; warm weather; many coastal and golf communities.",
            "Watch Outs": "Higher homeowners insurance in some areas; hurricane risk; popular areas can be expensive.",
            "Best Fit": "Warm-weather retirees, golfers, beach lifestyle, no-income-tax preference",
        },
        {
            "State": "Tennessee",
            "Example Places": "Knoxville; Chattanooga; Franklin; Tellico Village",
            "Tax Score": 94,
            "Cost Score": 82,
            "Healthcare Score": 76,
            "Lifestyle Score": 78,
            "Climate Score": 74,
            "Overall Score": 83,
            "Why It Ranks Well": "No state income tax; relatively affordable; mild climate; good mix of mountains, lakes, and cities.",
            "Watch Outs": "Some popular areas have rising housing costs; summers can be hot and humid.",
            "Best Fit": "Low-tax living, mountain/lake lifestyle, moderate cost of living",
        },
        {
            "State": "South Carolina",
            "Example Places": "Hilton Head; Greenville; Charleston suburbs; Myrtle Beach",
            "Tax Score": 84,
            "Cost Score": 77,
            "Healthcare Score": 76,
            "Lifestyle Score": 90,
            "Climate Score": 84,
            "Overall Score": 82,
            "Why It Ranks Well": "Retirement-friendly tax treatment; strong golf/beach lifestyle; lower cost than many coastal states.",
            "Watch Outs": "Coastal insurance and hurricane exposure; Charleston/Hilton Head can be pricey.",
            "Best Fit": "Golfers, coastal retirees, snowbirds, warm-weather lifestyle",
        },
        {
            "State": "Arizona",
            "Example Places": "Scottsdale; Tucson; Mesa; Prescott",
            "Tax Score": 80,
            "Cost Score": 73,
            "Healthcare Score": 80,
            "Lifestyle Score": 86,
            "Climate Score": 82,
            "Overall Score": 80,
            "Why It Ranks Well": "Popular retiree destination; dry climate; strong healthcare access around Phoenix and Tucson.",
            "Watch Outs": "Extreme summer heat; water concerns; some markets have become expensive.",
            "Best Fit": "Dry-climate retirees, golfers, desert lifestyle, active adult communities",
        },
        {
            "State": "North Carolina",
            "Example Places": "Asheville; Raleigh suburbs; Wilmington; Pinehurst",
            "Tax Score": 76,
            "Cost Score": 75,
            "Healthcare Score": 82,
            "Lifestyle Score": 86,
            "Climate Score": 78,
            "Overall Score": 79,
            "Why It Ranks Well": "Strong healthcare corridors; mountains and beaches; moderate climate; good quality of life.",
            "Watch Outs": "State income tax applies; popular areas can be expensive.",
            "Best Fit": "Balanced lifestyle, healthcare access, mountains/beaches, golf",
        },
        {
            "State": "Texas",
            "Example Places": "San Antonio; Georgetown; Frisco; McAllen",
            "Tax Score": 94,
            "Cost Score": 73,
            "Healthcare Score": 79,
            "Lifestyle Score": 76,
            "Climate Score": 70,
            "Overall Score": 79,
            "Why It Ranks Well": "No state income tax; many affordable cities; strong healthcare in major metros.",
            "Watch Outs": "Property taxes can be high; hot summers; large driving distances.",
            "Best Fit": "No-income-tax preference, large metro healthcare, affordable city options",
        },
        {
            "State": "Georgia",
            "Example Places": "Savannah; Athens; Peachtree City; Blue Ridge",
            "Tax Score": 79,
            "Cost Score": 78,
            "Healthcare Score": 76,
            "Lifestyle Score": 80,
            "Climate Score": 80,
            "Overall Score": 78,
            "Why It Ranks Well": "Moderate cost; warm climate; good access to Atlanta healthcare; varied city/coastal/mountain options.",
            "Watch Outs": "Atlanta traffic; summer humidity; tax details vary by income type.",
            "Best Fit": "Warm climate, southern lifestyle, moderate affordability",
        },
        {
            "State": "Nevada",
            "Example Places": "Henderson; Reno; Mesquite; Summerlin",
            "Tax Score": 95,
            "Cost Score": 69,
            "Healthcare Score": 72,
            "Lifestyle Score": 78,
            "Climate Score": 78,
            "Overall Score": 77,
            "Why It Ranks Well": "No state income tax; dry climate; good retiree communities near Las Vegas and Reno.",
            "Watch Outs": "Healthcare access varies outside major metros; heat in southern Nevada; housing costs rose in popular areas.",
            "Best Fit": "No-income-tax preference, dry climate, entertainment access",
        },
        {
            "State": "Michigan",
            "Example Places": "Traverse City; Grand Rapids; Ann Arbor; Plymouth/Canton",
            "Tax Score": 67,
            "Cost Score": 74,
            "Healthcare Score": 84,
            "Lifestyle Score": 70,
            "Climate Score": 55,
            "Overall Score": 70,
            "Why It Ranks Well": "Strong healthcare in major metros; relatively affordable housing in many areas; excellent summer lifestyle.",
            "Watch Outs": "Cold winters; state tax planning matters; snowbird strategy may be attractive.",
            "Best Fit": "People keeping family ties, lower housing than coastal states, summer lifestyle",
        },
        {
            "State": "California",
            "Example Places": "San Diego; Palm Springs; San Luis Obispo; Sacramento suburbs",
            "Tax Score": 42,
            "Cost Score": 35,
            "Healthcare Score": 90,
            "Lifestyle Score": 95,
            "Climate Score": 92,
            "Overall Score": 68,
            "Why It Ranks Well": "Excellent climate and healthcare; strong lifestyle options; beaches, mountains, and culture.",
            "Watch Outs": "High cost of living; high taxes; housing affordability challenges.",
            "Best Fit": "High-budget retirees prioritizing climate, healthcare, and lifestyle",
        },
    ])


def score_badge(score):
    if score >= 85:
        return "Excellent"
    if score >= 75:
        return "Strong"
    if score >= 65:
        return "Moderate"
    return "High Cost / Specialized Fit"


def filter_places_data(df, priority):
    if priority == "Lowest taxes":
        return df.sort_values(["Tax Score", "Overall Score"], ascending=False)
    if priority == "Lowest cost":
        return df.sort_values(["Cost Score", "Overall Score"], ascending=False)
    if priority == "Healthcare access":
        return df.sort_values(["Healthcare Score", "Overall Score"], ascending=False)
    if priority == "Lifestyle / weather":
        return df.sort_values(["Lifestyle Score", "Climate Score", "Overall Score"], ascending=False)
    return df.sort_values("Overall Score", ascending=False)


def plot_best_states_scores(df):
    fig, ax = plt.subplots(figsize=(12, 5.5))
    show = df.head(10).sort_values("Overall Score")
    ax.barh(show["State"], show["Overall Score"])
    for i, v in enumerate(show["Overall Score"]):
        ax.text(v + 1, i, f"{int(v)}", va="center", fontweight="bold")
    ax.set_xlim(0, 105)
    ax.set_xlabel("Overall Retirement Fit Score")
    ax.set_title("Top Retirement States - Phase 1 Score", fontsize=15, fontweight="bold", loc="left")
    ax.grid(axis="x", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig



def estimate_state_income_tax_simple(state, taxable_income, social_security_income=0, retirement_income=0):
    """
    Simplified educational state income tax estimate.
    This is intentionally directional, not tax advice.
    """
    taxable_income = max(float(taxable_income or 0), 0)
    social_security_income = max(float(social_security_income or 0), 0)
    retirement_income = max(float(retirement_income or 0), 0)

    no_income_tax_states = ["Florida", "Tennessee", "Texas", "Nevada"]
    if state in no_income_tax_states:
        return 0

    if state == "Arizona":
        return taxable_income * 0.025

    if state == "North Carolina":
        return taxable_income * 0.0425

    if state == "Michigan":
        # Directional estimate: Michigan has retirement-income rules/exemptions that vary by birth year.
        adjusted = max(taxable_income - min(retirement_income, 40000), 0)
        return adjusted * 0.0425

    if state == "South Carolina":
        # Directional estimate: retirement deductions can be meaningful, especially for older retirees.
        adjusted = max(taxable_income - min(retirement_income, 30000), 0)
        return adjusted * 0.064

    if state == "Georgia":
        # Directional estimate: retirement exclusion can reduce taxable retirement income.
        adjusted = max(taxable_income - min(retirement_income, 65000), 0)
        return adjusted * 0.0549

    if state == "California":
        # Simplified progressive-style estimate.
        brackets = [
            (10000, 0.01),
            (25000, 0.02),
            (50000, 0.04),
            (75000, 0.06),
            (150000, 0.08),
            (float("inf"), 0.093),
        ]
        remaining = taxable_income
        last = 0
        tax = 0
        for limit, rate in brackets:
            amount = min(remaining, limit - last)
            if amount <= 0:
                break
            tax += amount * rate
            remaining -= amount
            last = limit
        return tax

    return taxable_income * 0.05


def get_state_property_tax_rate_simple(state):
    rates = {
        "Florida": 0.0082,
        "Tennessee": 0.0056,
        "South Carolina": 0.0057,
        "Arizona": 0.0063,
        "North Carolina": 0.0075,
        "Texas": 0.0160,
        "Georgia": 0.0083,
        "Nevada": 0.0053,
        "Michigan": 0.0138,
        "California": 0.0075,
    }
    return rates.get(state, 0.009)


def get_state_sales_tax_rate_simple(state):
    rates = {
        "Florida": 0.070,
        "Tennessee": 0.095,
        "South Carolina": 0.074,
        "Arizona": 0.084,
        "North Carolina": 0.070,
        "Texas": 0.082,
        "Georgia": 0.074,
        "Nevada": 0.082,
        "Michigan": 0.060,
        "California": 0.087,
    }
    return rates.get(state, 0.07)


def estimate_total_state_tax_burden(state, ss_income, pretax_withdrawals, pension_other_income, taxable_income, annual_spending, home_value):
    """
    Estimates annual state-level tax burden:
    - simplified state income tax
    - estimated property tax
    - estimated sales tax on taxable spending
    """
    retirement_income = float(pretax_withdrawals or 0) + float(pension_other_income or 0)
    income_tax_base = float(pretax_withdrawals or 0) + float(pension_other_income or 0) + float(taxable_income or 0)

    # Most states here do not tax Social Security in this simplified model.
    # Phase 3 can add detailed SS taxation by state and filing status.
    income_tax = estimate_state_income_tax_simple(
        state,
        income_tax_base,
        social_security_income=ss_income,
        retirement_income=retirement_income
    )

    property_tax = float(home_value or 0) * get_state_property_tax_rate_simple(state)

    # Sales tax estimate: assume 45% of spending is taxable consumption.
    taxable_sales_spending = float(annual_spending or 0) * 0.45
    sales_tax = taxable_sales_spending * get_state_sales_tax_rate_simple(state)

    total_tax = income_tax + property_tax + sales_tax

    return {
        "Estimated Income Tax": income_tax,
        "Estimated Property Tax": property_tax,
        "Estimated Sales Tax": sales_tax,
        "Estimated Total State/Local Tax": total_tax,
        "Effective State/Local Tax Rate": total_tax / max(
            float(ss_income or 0) + float(pretax_withdrawals or 0) + float(pension_other_income or 0) + float(taxable_income or 0),
            1
        ),
    }


def build_personalized_places_table(places_df, ss_income, pretax_withdrawals, pension_other_income, taxable_income, annual_spending, home_value):
    rows = []

    for _, row in places_df.iterrows():
        state = row["State"]

        tax = estimate_total_state_tax_burden(
            state,
            ss_income=ss_income,
            pretax_withdrawals=pretax_withdrawals,
            pension_other_income=pension_other_income,
            taxable_income=taxable_income,
            annual_spending=annual_spending,
            home_value=home_value,
        )

        # Lower estimated annual tax burden gets a higher personalized tax score.
        total_tax = tax["Estimated Total State/Local Tax"]
        tax_drag_score = max(0, min(100, 100 - (total_tax / 750)))

        personalized_score = (
            tax_drag_score * 0.35
            + float(row["Cost Score"]) * 0.20
            + float(row["Healthcare Score"]) * 0.20
            + float(row["Lifestyle Score"]) * 0.15
            + float(row["Climate Score"]) * 0.10
        )

        rows.append({
            "State": state,
            "Example Places": row["Example Places"],
            "Personalized Score": round(personalized_score),
            "Estimated Annual Tax": total_tax,
            "Income Tax": tax["Estimated Income Tax"],
            "Property Tax": tax["Estimated Property Tax"],
            "Sales Tax": tax["Estimated Sales Tax"],
            "Effective Tax Rate": tax["Effective State/Local Tax Rate"],
            "Cost Score": row["Cost Score"],
            "Healthcare Score": row["Healthcare Score"],
            "Lifestyle Score": row["Lifestyle Score"],
            "Climate Score": row["Climate Score"],
            "Best Fit": row["Best Fit"],
            "Watch Outs": row["Watch Outs"],
        })

    return pd.DataFrame(rows).sort_values("Personalized Score", ascending=False).reset_index(drop=True)


def plot_personalized_tax_burden(personal_df):
    fig, ax = plt.subplots(figsize=(12, 5.5))
    show = personal_df.head(10).sort_values("Estimated Annual Tax", ascending=True)
    bars = ax.barh(show["State"], show["Estimated Annual Tax"])

    for i, v in enumerate(show["Estimated Annual Tax"]):
        ax.text(v + max(show["Estimated Annual Tax"].max() * 0.01, 250), i, money(v), va="center", fontweight="bold")

    ax.set_xlabel("Estimated Annual State/Local Tax")
    ax.set_title("Estimated Annual Tax by State", fontsize=15, fontweight="bold", loc="left")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: compact_money_label(x)))
    ax.grid(axis="x", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig



def get_phase3_city_places_data():
    """
    Phase 3 static city/place-level retirement fit model.
    Scores are directional educational estimates on a 0-100 scale.
    """
    return pd.DataFrame([
        {
            "State": "Florida",
            "Place": "Sarasota",
            "Type": "Coastal / Arts / Beach",
            "Overall City Score": 88,
            "Affordability": 62,
            "Healthcare": 86,
            "Lifestyle": 95,
            "Golf / Recreation": 90,
            "Climate": 90,
            "Why Retire Here": "Beach lifestyle, arts, restaurants, golf, strong retiree infrastructure.",
            "Watch Outs": "Housing and insurance can be expensive; hurricane exposure.",
        },
        {
            "State": "Florida",
            "Place": "The Villages",
            "Type": "Active Adult / Golf Cart Community",
            "Overall City Score": 86,
            "Affordability": 72,
            "Healthcare": 78,
            "Lifestyle": 92,
            "Golf / Recreation": 96,
            "Climate": 88,
            "Why Retire Here": "Highly social active-adult lifestyle, golf carts, clubs, recreation, and no state income tax.",
            "Watch Outs": "May feel too retirement-specific for some; summer heat and insurance considerations.",
        },
        {
            "State": "Florida",
            "Place": "St. Augustine",
            "Type": "Coastal / Historic",
            "Overall City Score": 82,
            "Affordability": 68,
            "Healthcare": 75,
            "Lifestyle": 90,
            "Golf / Recreation": 82,
            "Climate": 86,
            "Why Retire Here": "Historic coastal feel, beaches nearby, walkable areas, and strong lifestyle appeal.",
            "Watch Outs": "Tourism, coastal insurance, and some housing-cost pressure.",
        },
        {
            "State": "South Carolina",
            "Place": "Hilton Head",
            "Type": "Coastal / Golf",
            "Overall City Score": 87,
            "Affordability": 58,
            "Healthcare": 76,
            "Lifestyle": 96,
            "Golf / Recreation": 97,
            "Climate": 84,
            "Why Retire Here": "Premier golf, beaches, bike paths, restaurants, and resort-style retirement lifestyle.",
            "Watch Outs": "Higher housing cost; coastal insurance and storm exposure.",
        },
        {
            "State": "South Carolina",
            "Place": "Greenville",
            "Type": "Small City / Mountains Nearby",
            "Overall City Score": 83,
            "Affordability": 77,
            "Healthcare": 78,
            "Lifestyle": 84,
            "Golf / Recreation": 78,
            "Climate": 78,
            "Why Retire Here": "Vibrant downtown, lower cost than coastal areas, mountain access, and good quality of life.",
            "Watch Outs": "Not coastal; growth has increased housing demand.",
        },
        {
            "State": "South Carolina",
            "Place": "Myrtle Beach",
            "Type": "Coastal / Golf / Value",
            "Overall City Score": 80,
            "Affordability": 75,
            "Healthcare": 72,
            "Lifestyle": 86,
            "Golf / Recreation": 94,
            "Climate": 84,
            "Why Retire Here": "Affordable coastal golf lifestyle with many courses and entertainment options.",
            "Watch Outs": "Tourism, seasonal traffic, and coastal storm risk.",
        },
        {
            "State": "Tennessee",
            "Place": "Knoxville",
            "Type": "University City / Mountains",
            "Overall City Score": 84,
            "Affordability": 82,
            "Healthcare": 78,
            "Lifestyle": 80,
            "Golf / Recreation": 76,
            "Climate": 74,
            "Why Retire Here": "No state income tax, access to Smoky Mountains, college-town energy, and moderate cost.",
            "Watch Outs": "Humidity and rising demand in popular neighborhoods.",
        },
        {
            "State": "Tennessee",
            "Place": "Chattanooga",
            "Type": "River City / Outdoors",
            "Overall City Score": 82,
            "Affordability": 80,
            "Healthcare": 75,
            "Lifestyle": 82,
            "Golf / Recreation": 74,
            "Climate": 74,
            "Why Retire Here": "Scenic river/mountain setting, outdoor activities, and no state income tax.",
            "Watch Outs": "Healthcare depth is not the same as larger metros.",
        },
        {
            "State": "Arizona",
            "Place": "Scottsdale",
            "Type": "Desert / Golf / Luxury",
            "Overall City Score": 85,
            "Affordability": 50,
            "Healthcare": 84,
            "Lifestyle": 94,
            "Golf / Recreation": 98,
            "Climate": 78,
            "Why Retire Here": "World-class golf, healthcare access, dining, resorts, and active adult communities.",
            "Watch Outs": "Expensive housing and extreme summer heat.",
        },
        {
            "State": "Arizona",
            "Place": "Tucson",
            "Type": "Desert / University / Value",
            "Overall City Score": 81,
            "Affordability": 74,
            "Healthcare": 80,
            "Lifestyle": 80,
            "Golf / Recreation": 84,
            "Climate": 78,
            "Why Retire Here": "More affordable than Scottsdale, strong outdoor lifestyle, dry climate, and healthcare access.",
            "Watch Outs": "Summer heat and desert climate may not fit everyone.",
        },
        {
            "State": "North Carolina",
            "Place": "Pinehurst",
            "Type": "Golf / Village",
            "Overall City Score": 84,
            "Affordability": 72,
            "Healthcare": 76,
            "Lifestyle": 86,
            "Golf / Recreation": 98,
            "Climate": 78,
            "Why Retire Here": "One of the strongest golf-retirement fits in the country with a village feel.",
            "Watch Outs": "Smaller-town setting; not coastal or major metro.",
        },
        {
            "State": "North Carolina",
            "Place": "Wilmington",
            "Type": "Coastal / Small City",
            "Overall City Score": 82,
            "Affordability": 68,
            "Healthcare": 78,
            "Lifestyle": 90,
            "Golf / Recreation": 82,
            "Climate": 80,
            "Why Retire Here": "Coastal lifestyle, beaches, restaurants, and good regional healthcare.",
            "Watch Outs": "Hurricane exposure and rising housing costs.",
        },
        {
            "State": "Texas",
            "Place": "Georgetown",
            "Type": "Active Adult / Austin Area",
            "Overall City Score": 81,
            "Affordability": 70,
            "Healthcare": 78,
            "Lifestyle": 82,
            "Golf / Recreation": 82,
            "Climate": 70,
            "Why Retire Here": "Active-adult communities, no state income tax, and access to Austin-area healthcare.",
            "Watch Outs": "Property taxes and hot summers.",
        },
        {
            "State": "Nevada",
            "Place": "Henderson",
            "Type": "Desert / Las Vegas Area",
            "Overall City Score": 80,
            "Affordability": 66,
            "Healthcare": 76,
            "Lifestyle": 82,
            "Golf / Recreation": 84,
            "Climate": 76,
            "Why Retire Here": "No state income tax, entertainment access, golf, and airport convenience.",
            "Watch Outs": "Summer heat and healthcare varies by provider access.",
        },
        {
            "State": "Michigan",
            "Place": "Traverse City",
            "Type": "Lake / Summer Lifestyle",
            "Overall City Score": 76,
            "Affordability": 58,
            "Healthcare": 72,
            "Lifestyle": 88,
            "Golf / Recreation": 82,
            "Climate": 55,
            "Why Retire Here": "Beautiful lake lifestyle, wineries, golf, and excellent summers.",
            "Watch Outs": "Cold winters and housing can be expensive for Michigan.",
        },
        {
            "State": "Michigan",
            "Place": "Grand Rapids",
            "Type": "Mid-size City / Healthcare",
            "Overall City Score": 74,
            "Affordability": 73,
            "Healthcare": 84,
            "Lifestyle": 74,
            "Golf / Recreation": 72,
            "Climate": 54,
            "Why Retire Here": "Strong healthcare, reasonable cost, airport, restaurants, and West Michigan lifestyle.",
            "Watch Outs": "Winter weather and state tax planning.",
        },
    ])


def filter_city_places(city_df, selected_states, lifestyle_priority):
    df = city_df.copy()

    if selected_states:
        df = df[df["State"].isin(selected_states)]

    # Keep a fallback after the state filter. Some combinations, such as
    # Michigan + Coastal/Warm or Michigan + Active Adult, may have no exact
    # starter-city match in our current dataset. We should show the best
    # available matches instead of returning an empty frame and crashing.
    state_filtered_df = df.copy()

    if lifestyle_priority == "Golf / recreation":
        df = df.sort_values(["Golf / Recreation", "Overall City Score"], ascending=False)
    elif lifestyle_priority == "Healthcare":
        df = df.sort_values(["Healthcare", "Overall City Score"], ascending=False)
    elif lifestyle_priority == "Lower cost":
        df = df.sort_values(["Affordability", "Overall City Score"], ascending=False)
    elif lifestyle_priority == "Coastal / warm lifestyle":
        filtered = df[df["Type"].str.contains("Coastal|Beach|Desert", case=False, regex=True, na=False)]
        df = filtered if not filtered.empty else state_filtered_df
        df = df.sort_values(["Lifestyle", "Climate", "Overall City Score"], ascending=False)
    elif lifestyle_priority == "Active adult community":
        filtered = df[df["Type"].str.contains("Active Adult|Golf Cart", case=False, regex=True, na=False)]
        df = filtered if not filtered.empty else state_filtered_df
        df = df.sort_values(["Lifestyle", "Golf / Recreation", "Overall City Score"], ascending=False)
    else:
        df = df.sort_values("Overall City Score", ascending=False)

    if df.empty:
        df = city_df.sort_values("Overall City Score", ascending=False)

    return df.reset_index(drop=True)


def plot_city_scores(city_df):
    fig, ax = plt.subplots(figsize=(12, 5.5))
    show = city_df.head(10).sort_values("Overall City Score")
    labels = show["Place"] + ", " + show["State"]
    ax.barh(labels, show["Overall City Score"])
    for i, v in enumerate(show["Overall City Score"]):
        ax.text(v + 1, i, f"{int(v)}", va="center", fontweight="bold")
    ax.set_xlim(0, 105)
    ax.set_xlabel("City Retirement Fit Score")
    ax.set_title("Top Places to Retire - Phase 3 City Scores", fontsize=15, fontweight="bold", loc="left")
    ax.grid(axis="x", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig



def build_state_comparison_table(places_df, personal_df, selected_states):
    rows = []

    for state in selected_states:
        base = places_df[places_df["State"] == state]
        personal = personal_df[personal_df["State"] == state]

        if base.empty or personal.empty:
            continue

        b = base.iloc[0]
        p = personal.iloc[0]

        rows.append({
            "State": state,
            "Overall Score": b["Overall Score"],
            "Personalized Score": p["Personalized Score"],
            "Estimated Annual Tax": p["Estimated Annual Tax"],
            "Income Tax": p["Income Tax"],
            "Property Tax": p["Property Tax"],
            "Sales Tax": p["Sales Tax"],
            "Effective Tax Rate": p["Effective Tax Rate"],
            "Cost Score": b["Cost Score"],
            "Healthcare Score": b["Healthcare Score"],
            "Lifestyle Score": b["Lifestyle Score"],
            "Climate Score": b["Climate Score"],
            "Example Places": b["Example Places"],
            "Best Fit": b["Best Fit"],
            "Watch Outs": b["Watch Outs"],
        })

    return pd.DataFrame(rows)


def plot_state_comparison_scores(compare_df):
    fig, ax = plt.subplots(figsize=(12, 5.5))

    x = range(len(compare_df))
    width = 0.35

    ax.bar([i - width / 2 for i in x], compare_df["Overall Score"], width=width, label="Base Score")
    ax.bar([i + width / 2 for i in x], compare_df["Personalized Score"], width=width, label="Personalized Score")

    ax.set_xticks(list(x))
    ax.set_xticklabels(compare_df["State"])
    ax.set_ylim(0, 105)

    for i, row in compare_df.iterrows():
        ax.text(i - width / 2, row["Overall Score"] + 1, str(int(row["Overall Score"])), ha="center", fontweight="bold")
        ax.text(i + width / 2, row["Personalized Score"] + 1, str(int(row["Personalized Score"])), ha="center", fontweight="bold")

    ax.set_ylabel("Score")
    ax.set_title("Base vs Personalized Retirement Fit", fontsize=15, fontweight="bold", loc="left")
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_state_tax_stack(compare_df):
    fig, ax = plt.subplots(figsize=(12, 5.5))

    states = compare_df["State"]
    income_tax = compare_df["Income Tax"]
    property_tax = compare_df["Property Tax"]
    sales_tax = compare_df["Sales Tax"]

    ax.bar(states, income_tax, label="Income Tax")
    ax.bar(states, property_tax, bottom=income_tax, label="Property Tax")
    ax.bar(states, sales_tax, bottom=income_tax + property_tax, label="Sales Tax")

    totals = compare_df["Estimated Annual Tax"]
    for i, total in enumerate(totals):
        ax.text(i, total + max(totals.max() * 0.02, 250), money(total), ha="center", fontweight="bold")

    ax.set_ylabel("Estimated Annual Tax")
    ax.set_title("Estimated Tax Burden Breakdown", fontsize=15, fontweight="bold", loc="left")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: compact_money_label(x)))
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend()
    fig.tight_layout()
    return fig


def build_compare_narrative(compare_df):
    if compare_df.empty:
        return []

    best_score = compare_df.sort_values("Personalized Score", ascending=False).iloc[0]
    lowest_tax = compare_df.sort_values("Estimated Annual Tax").iloc[0]
    best_healthcare = compare_df.sort_values("Healthcare Score", ascending=False).iloc[0]
    best_lifestyle = compare_df.sort_values("Lifestyle Score", ascending=False).iloc[0]
    best_cost = compare_df.sort_values("Cost Score", ascending=False).iloc[0]

    notes = [
        f"Best overall personalized fit: **{best_score['State']}** with a personalized score of **{int(best_score['Personalized Score'])}/100**.",
        f"Lowest estimated annual tax burden: **{lowest_tax['State']}** at about **{money(lowest_tax['Estimated Annual Tax'])}** per year.",
        f"Best healthcare score: **{best_healthcare['State']}** with a healthcare score of **{int(best_healthcare['Healthcare Score'])}/100**.",
        f"Best lifestyle score: **{best_lifestyle['State']}** with a lifestyle score of **{int(best_lifestyle['Lifestyle Score'])}/100**.",
        f"Best cost score: **{best_cost['State']}** with a cost score of **{int(best_cost['Cost Score'])}/100**.",
    ]

    return notes



def calculate_location_fit_profile(
    tax_weight,
    cost_weight,
    healthcare_weight,
    lifestyle_weight,
    climate_weight,
    golf_weight,
):
    total = tax_weight + cost_weight + healthcare_weight + lifestyle_weight + climate_weight + golf_weight
    if total <= 0:
        total = 1

    return {
        "tax": tax_weight / total,
        "cost": cost_weight / total,
        "healthcare": healthcare_weight / total,
        "lifestyle": lifestyle_weight / total,
        "climate": climate_weight / total,
        "golf": golf_weight / total,
    }


def build_retirement_location_recommendation_engine(
    city_df,
    personal_df,
    weights,
    preferred_states=None,
    avoid_states=None,
    wants_snowbird=False,
):
    preferred_states = preferred_states or []
    avoid_states = avoid_states or []

    rows = []

    for _, city in city_df.iterrows():
        state = city["State"]

        if avoid_states and state in avoid_states:
            continue

        p = personal_df[personal_df["State"] == state]
        if p.empty:
            continue
        p = p.iloc[0]

        preference_bonus = 0
        if preferred_states and state in preferred_states:
            preference_bonus += 5

        snowbird_bonus = 0
        if wants_snowbird and city["Climate"] >= 80:
            snowbird_bonus += 4

        score = (
            (100 - min(float(p["Estimated Annual Tax"]) / 750, 100)) * weights["tax"]
            + float(city["Affordability"]) * weights["cost"]
            + float(city["Healthcare"]) * weights["healthcare"]
            + float(city["Lifestyle"]) * weights["lifestyle"]
            + float(city["Climate"]) * weights["climate"]
            + float(city["Golf / Recreation"]) * weights["golf"]
            + preference_bonus
            + snowbird_bonus
        )

        rows.append({
            "Place": city["Place"],
            "State": state,
            "Type": city["Type"],
            "Recommended Fit Score": round(min(score, 100)),
            "Estimated Annual State/Local Tax": p["Estimated Annual Tax"],
            "Healthcare": city["Healthcare"],
            "Affordability": city["Affordability"],
            "Lifestyle": city["Lifestyle"],
            "Climate": city["Climate"],
            "Golf / Recreation": city["Golf / Recreation"],
            "Why It Fits": city["Why Retire Here"],
            "Watch Outs": city["Watch Outs"],
        })

    cols = [
        "Place",
        "State",
        "Type",
        "Recommended Fit Score",
        "Estimated Annual State/Local Tax",
        "Healthcare",
        "Affordability",
        "Lifestyle",
        "Climate",
        "Golf / Recreation",
        "Why It Fits",
        "Watch Outs",
    ]

    if not rows:
        return pd.DataFrame(columns=cols)

    return pd.DataFrame(rows, columns=cols).sort_values("Recommended Fit Score", ascending=False).reset_index(drop=True)


def build_snowbird_recommendations(location_df, current_home_state="Michigan"):
    warm_states = ["Florida", "South Carolina", "Arizona", "Texas", "Nevada", "Georgia"]
    snowbird_df = location_df[location_df["State"].isin(warm_states)].copy()

    if snowbird_df.empty:
        return pd.DataFrame()

    snowbird_df["Snowbird Fit Score"] = (
        snowbird_df["Climate"] * 0.30
        + snowbird_df["Lifestyle"] * 0.25
        + snowbird_df["Golf / Recreation"] * 0.25
        + snowbird_df["Healthcare"] * 0.10
        + snowbird_df["Affordability"] * 0.10
    ).round()

    snowbird_df["Snowbird Strategy"] = (
        "Keep primary home in " + current_home_state
        + " and spend winter months here before buying."
    )

    return snowbird_df.sort_values("Snowbird Fit Score", ascending=False).reset_index(drop=True)


def plot_location_engine_scores(location_df):
    fig, ax = plt.subplots(figsize=(12, 5.5))

    show = location_df.head(10).sort_values("Recommended Fit Score")
    labels = show["Place"] + ", " + show["State"]

    ax.barh(labels, show["Recommended Fit Score"])

    for i, v in enumerate(show["Recommended Fit Score"]):
        ax.text(v + 1, i, f"{int(v)}", va="center", fontweight="bold")

    ax.set_xlim(0, 105)
    ax.set_xlabel("Personalized Location Fit Score")
    ax.set_title("Personalized Retirement Location Recommendations", fontsize=15, fontweight="bold", loc="left")
    ax.grid(axis="x", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig


def build_location_recommendation_summary(location_df):
    if location_df.empty:
        return []

    top = location_df.iloc[0]
    lowest_tax = location_df.sort_values("Estimated Annual State/Local Tax").iloc[0]
    best_healthcare = location_df.sort_values("Healthcare", ascending=False).iloc[0]
    best_golf = location_df.sort_values("Golf / Recreation", ascending=False).iloc[0]
    best_value = location_df.sort_values("Affordability", ascending=False).iloc[0]

    return [
        f"Best overall personalized match: **{top['Place']}, {top['State']}** with a fit score of **{int(top['Recommended Fit Score'])}/100**.",
        f"Lowest estimated tax option among recommendations: **{lowest_tax['Place']}, {lowest_tax['State']}** at about **{money(lowest_tax['Estimated Annual State/Local Tax'])}** per year.",
        f"Best healthcare score: **{best_healthcare['Place']}, {best_healthcare['State']}**.",
        f"Best golf/recreation score: **{best_golf['Place']}, {best_golf['State']}**.",
        f"Best affordability score: **{best_value['Place']}, {best_value['State']}**.",
    ]



def run_projection_with_temp_monthly_spending(test_monthly_spending):
    original_budget_mode = st.session_state.budget_mode
    original_flat_monthly_spending = st.session_state.flat_monthly_spending
    original_enable_spending_change = st.session_state.enable_spending_change

    try:
        st.session_state.budget_mode = "Flat monthly number"
        st.session_state.flat_monthly_spending = float(test_monthly_spending)
        st.session_state.enable_spending_change = False

        test_df = run_projection()
        if test_df is None or test_df.empty:
            return None, 0, "Incomplete"

        score_result = calculate_rtv_score(test_df)
        test_score = score_result[0]
        test_label = score_result[1]

        return test_df, test_score, test_label

    finally:
        st.session_state.budget_mode = original_budget_mode
        st.session_state.flat_monthly_spending = original_flat_monthly_spending
        st.session_state.enable_spending_change = original_enable_spending_change


def find_monthly_spending_for_target_score(target_score=80):
    current_monthly = annual_household_spending() / 12

    if current_monthly <= 0:
        return None

    # First check current result.
    current_test_df, current_score, current_label = run_projection_with_temp_monthly_spending(current_monthly)

    if current_test_df is None:
        return None

    # If current score is below target, search lower spending.
    if current_score < target_score:
        low = 0
        high = current_monthly
        best_monthly = None
        best_score = 0
        best_label = "Incomplete"

        for _ in range(24):
            mid = (low + high) / 2
            test_df, test_score, test_label = run_projection_with_temp_monthly_spending(mid)

            if test_df is None:
                high = mid
                continue

            if test_score >= target_score:
                best_monthly = mid
                best_score = test_score
                best_label = test_label
                low = mid
            else:
                high = mid

        return {
            "mode": "lower",
            "target_score": target_score,
            "current_monthly": current_monthly,
            "current_score": current_score,
            "current_label": current_label,
            "suggested_monthly": best_monthly,
            "suggested_score": best_score,
            "suggested_label": best_label,
            "monthly_difference": (best_monthly - current_monthly) if best_monthly is not None else None,
        }

    # If current score is healthy, search higher spending until target is almost lost.
    low = current_monthly
    high = current_monthly * 2.0

    # Expand high limit if plan is very strong.
    for _ in range(5):
        test_df, test_score, test_label = run_projection_with_temp_monthly_spending(high)
        if test_df is not None and test_score >= target_score:
            low = high
            high *= 1.5
        else:
            break

    best_monthly = current_monthly
    best_score = current_score
    best_label = current_label

    for _ in range(24):
        mid = (low + high) / 2
        test_df, test_score, test_label = run_projection_with_temp_monthly_spending(mid)

        if test_df is not None and test_score >= target_score:
            best_monthly = mid
            best_score = test_score
            best_label = test_label
            low = mid
        else:
            high = mid

    return {
        "mode": "higher",
        "target_score": target_score,
        "current_monthly": current_monthly,
        "current_score": current_score,
        "current_label": current_label,
        "suggested_monthly": best_monthly,
        "suggested_score": best_score,
        "suggested_label": best_label,
        "monthly_difference": best_monthly - current_monthly,
    }


def render_suggested_spending_target_tool():
    """Render the Action Plan spending target tool as a featured planning lab."""
    st.markdown("""
    <style>
    .rb-spend-lab {
        border: 1px solid rgba(59,130,246,.22);
        border-radius: 28px;
        padding: 28px 28px 24px 28px;
        margin: 8px 0 26px 0;
        background:
            radial-gradient(circle at top right, rgba(20,184,166,.16), transparent 34%),
            linear-gradient(135deg, #F8FBFF 0%, #EEF6FF 52%, #F0FDF4 100%);
        box-shadow: 0 18px 45px rgba(15, 23, 42, .08);
    }
    .rb-spend-lab-top {
        display: flex;
        justify-content: space-between;
        gap: 18px;
        align-items: flex-start;
        margin-bottom: 18px;
    }
    .rb-spend-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #DBEAFE;
        color: #1D4ED8;
        border-radius: 999px;
        padding: 7px 12px;
        font-size: .76rem;
        font-weight: 900;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .rb-spend-title {
        font-size: 2.1rem;
        line-height: 1.05;
        font-weight: 950;
        color: #0F172A;
        margin: 0 0 8px 0;
    }
    .rb-spend-subtitle {
        color: #475569;
        font-size: 1.02rem;
        line-height: 1.55;
        max-width: 850px;
    }
    .rb-spend-side {
        min-width: 215px;
        border-radius: 22px;
        background: rgba(255,255,255,.74);
        border: 1px solid rgba(148,163,184,.24);
        padding: 16px;
        box-shadow: 0 10px 24px rgba(15,23,42,.06);
    }
    .rb-spend-side-label {
        color: #64748B;
        font-weight: 850;
        font-size: .82rem;
        text-transform: uppercase;
        letter-spacing: .05em;
    }
    .rb-spend-side-value {
        color: #0F172A;
        font-size: 1.75rem;
        font-weight: 950;
        margin-top: 4px;
    }
    .rb-spend-steps {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin-top: 20px;
    }
    .rb-spend-step {
        border-radius: 18px;
        background: rgba(255,255,255,.72);
        border: 1px solid rgba(148,163,184,.22);
        padding: 14px 15px;
    }
    .rb-spend-step-num {
        display: inline-flex;
        width: 26px;
        height: 26px;
        border-radius: 999px;
        align-items: center;
        justify-content: center;
        background: #0F62FE;
        color: white;
        font-weight: 950;
        font-size: .86rem;
        margin-right: 8px;
    }
    .rb-spend-step-title {
        font-weight: 900;
        color: #0F172A;
    }
    .rb-spend-step-note {
        color: #64748B;
        margin-top: 6px;
        font-size: .92rem;
        line-height: 1.4;
    }
    .rb-spend-control-box {
        border: 1px solid rgba(226,232,240,.95);
        border-radius: 24px;
        padding: 22px 24px 18px 24px;
        margin: 18px 0 22px 0;
        background: #FFFFFF;
        box-shadow: 0 10px 30px rgba(15,23,42,.055);
    }
    .rb-spend-control-title {
        font-size: 1.05rem;
        font-weight: 950;
        color: #0F172A;
        margin-bottom: 4px;
    }
    .rb-spend-control-note {
        color: #64748B;
        margin-bottom: 12px;
    }
    .rb-spend-result-hero {
        border-radius: 26px;
        padding: 24px 26px;
        margin: 18px 0 18px 0;
        background: linear-gradient(135deg, #ECFDF5 0%, #EFF6FF 100%);
        border: 1px solid rgba(34,197,94,.28);
        box-shadow: 0 16px 38px rgba(15,23,42,.075);
    }
    .rb-spend-result-eyebrow {
        color: #15803D;
        font-size: .78rem;
        letter-spacing: .08em;
        text-transform: uppercase;
        font-weight: 950;
        margin-bottom: 8px;
    }
    .rb-spend-result-title {
        color: #0F172A;
        font-size: 1.65rem;
        line-height: 1.15;
        font-weight: 950;
        margin-bottom: 8px;
    }
    .rb-spend-result-note {
        color: #475569;
        font-size: 1rem;
        line-height: 1.5;
    }
    .rb-spend-card-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 16px;
        margin: 14px 0 20px 0;
    }
    .rb-spend-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 22px;
        padding: 20px;
        box-shadow: 0 10px 26px rgba(15,23,42,.06);
        min-height: 165px;
    }
    .rb-spend-card-label {
        color: #475569;
        font-weight: 900;
        font-size: .96rem;
        min-height: 42px;
    }
    .rb-spend-card-value {
        color: #0F172A;
        font-size: 2rem;
        line-height: 1.05;
        font-weight: 950;
        margin-top: 12px;
    }
    .rb-spend-card-note {
        color: #64748B;
        margin-top: 12px;
        font-size: .92rem;
        line-height: 1.35;
    }
    @media (max-width: 900px) {
        .rb-spend-lab-top { flex-direction: column; }
        .rb-spend-side { width: 100%; }
        .rb-spend-steps { grid-template-columns: 1fr; }
        .rb-spend-card-grid { grid-template-columns: 1fr; }
        .rb-spend-title { font-size: 1.65rem; }
    }
    </style>
    <div class="rb-spend-lab">
      <div class="rb-spend-lab-top">
        <div>
          <div class="rb-spend-badge">✨ Featured What‑If Tool</div>
          <div class="rb-spend-title">Find the spending number that makes the plan work</div>
          <div class="rb-spend-subtitle">
            This is one of the most useful parts of the Action Plan: instead of only saying whether retirement looks strong or risky,
            it backs into a monthly spending target that can help the user reach the Blueprint Score they want.
          </div>
        </div>
        <div class="rb-spend-side">
          <div class="rb-spend-side-label">Best for</div>
          <div class="rb-spend-side-value">Decision clarity</div>
          <div class="rb-spend-step-note">Great for testing “Can I spend this much?” before changing retirement age, savings, or income.</div>
        </div>
      </div>
      <div class="rb-spend-steps">
        <div class="rb-spend-step">
          <div><span class="rb-spend-step-num">1</span><span class="rb-spend-step-title">Choose a target score</span></div>
          <div class="rb-spend-step-note">Pick the confidence level the user wants to aim for.</div>
        </div>
        <div class="rb-spend-step">
          <div><span class="rb-spend-step-num">2</span><span class="rb-spend-step-title">Run the spending test</span></div>
          <div class="rb-spend-step-note">The app tests spending levels against the current projection assumptions.</div>
        </div>
        <div class="rb-spend-step">
          <div><span class="rb-spend-step-num">3</span><span class="rb-spend-step-title">Use the action number</span></div>
          <div class="rb-spend-step-note">See whether the plan needs a cut, has room, or needs another lever.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="rb-spend-control-box">
      <div class="rb-spend-control-title">Set your target Blueprint Score</div>
      <div class="rb-spend-control-note">Move the slider, then run the test to calculate the suggested monthly spending target.</div>
    </div>
    """, unsafe_allow_html=True)

    target_score = st.slider(
        "Target Blueprint Score",
        min_value=50,
        max_value=100,
        value=int(st.session_state.get("action_target_blueprint_score", 80) or 80),
        step=1,
        key="action_target_blueprint_score",
        help="A higher target usually means the plan needs more cushion, lower spending, more income, or more assets.",
    )

    run_col, note_col = st.columns([1, 2.4])
    with run_col:
        run_test = st.button("Calculate My Spending Target", type="primary", key="find_action_suggested_spending", use_container_width=True)
    with note_col:
        st.caption("This feature uses your saved inputs and the current Blueprint Score model. It is an educational estimate, not financial advice.")

    if run_test:
        with st.spinner("Testing spending levels against your Blueprint Score..."):
            st.session_state.action_spending_target_result = find_monthly_spending_for_target_score(target_score)

    result = st.session_state.get("action_spending_target_result")

    if not result:
        st.markdown("""
        <div class="rb-next-box">
          <div class="rb-next-heading">Why this is powerful</div>
          <div class="rb-muted">
            Most retirement tools only show a score. This turns the score into a specific monthly spending target,
            so the user knows what to test next instead of guessing.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    current_monthly = float(result.get("current_monthly") or 0)
    suggested_monthly = result.get("suggested_monthly")
    current_score = int(result.get("current_score") or 0)
    suggested_score = int(result.get("suggested_score") or current_score or 0)
    monthly_difference = result.get("monthly_difference")

    if suggested_monthly is None or monthly_difference is None:
        st.warning(
            "I could not find a monthly spending amount that reaches that score with the current assumptions. "
            "Try a lower target score, later retirement age, more savings, or more guaranteed income."
        )
        return

    suggested_monthly = float(suggested_monthly)
    monthly_difference = float(monthly_difference)

    if suggested_score >= 80:
        score_badge = "↗ Strong"
        score_badge_style = "background:#DCFCE7;color:#166534;"
    elif suggested_score >= 65:
        score_badge = "⚠ Watch"
        score_badge_style = "background:#FEF3C7;color:#92400E;"
    else:
        score_badge = "⚠ Needs Work"
        score_badge_style = "background:#FEE2E2;color:#991B1B;"

    difference_label = f"{money(abs(monthly_difference))}"
    if monthly_difference < 0:
        difference_note = "Monthly reduction needed"
        difference_prefix = "-"
        result_headline = f"To target {target_score}+, aim for about {money(suggested_monthly)} per month."
        result_note = f"That means reducing current monthly spending by about {money(abs(monthly_difference))}, based on the current projection model."
    elif monthly_difference > 0:
        difference_note = "Estimated extra monthly room"
        difference_prefix = "+"
        result_headline = f"Your plan may support about {money(suggested_monthly)} per month at this target."
        result_note = f"That is about {money(abs(monthly_difference))} more than current monthly spending while still targeting a Blueprint Score of {target_score}+."
    else:
        difference_note = "No monthly change needed"
        difference_prefix = ""
        result_headline = f"Your current spending is right on target for a {target_score}+ score."
        result_note = "No monthly spending adjustment is suggested under the current assumptions."

    st.markdown(f"""
    <div class="rb-spend-result-hero">
      <div class="rb-spend-result-eyebrow">Suggested spending answer</div>
      <div class="rb-spend-result-title">{result_headline}</div>
      <div class="rb-spend-result-note">{result_note}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="rb-spend-card-grid">
      <div class="rb-spend-card">
        <div class="rb-spend-card-label">Current Monthly Spending</div>
        <div class="rb-spend-card-value">{money(current_monthly)}</div>
        <div class="rb-spend-card-note">Based on your current spending inputs.</div>
      </div>
      <div class="rb-spend-card">
        <div class="rb-spend-card-label">Suggested Monthly Spending</div>
        <div class="rb-spend-card-value">{money(suggested_monthly)}</div>
        <div class="rb-spend-card-note">Estimated spending level for the target score.</div>
      </div>
      <div class="rb-spend-card">
        <div class="rb-spend-card-label">Monthly Difference</div>
        <div class="rb-spend-card-value">{difference_prefix}{difference_label}</div>
        <div class="rb-spend-card-note">{difference_note}</div>
      </div>
      <div class="rb-spend-card">
        <div class="rb-spend-card-label">Estimated Blueprint Score</div>
        <div class="rb-spend-card-value">{suggested_score}/100</div>
        <div class="rb-spend-card-note"><span style="display:inline-block;padding:6px 11px;border-radius:999px;font-weight:900;{score_badge_style}">{score_badge}</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("Spending Change Recommendations")
    if monthly_difference < 0:
        st.info(
            "Consider reducing flexible spending, delaying large purchases, or adding a later-life spending change if travel, mortgage, or early-retirement expenses decline."
        )
    else:
        st.info(
            "Your current spending appears workable under this target. Consider documenting when spending may drop later in retirement, such as after travel slows or a mortgage is paid off."
        )

    st.divider()

    st.subheader("Home & Housing Recommendations")
    home_value = float(st.session_state.get("home_value", 0) or 0)
    mortgage_balance = float(st.session_state.get("mortgage_balance", 0) or 0)
    home_equity = max(home_value - mortgage_balance, 0)
    if home_equity > 0:
        st.info(
            f"Moderate housing flexibility: estimated home equity of {money(home_equity)} could become an important retirement planning lever."
        )
    else:
        st.info(
            "Moderate housing flexibility: home equity, downsizing, relocating, or mortgage payoff timing could become important retirement planning levers."
        )

    st.divider()


# -----------------------------
# App navigation
# -----------------------------
PAGE_NAMES = [
    "Home",
    "Guided Questions",
    "Budget Builder",
    "Income Builder",
    "Spouse Questions",
    "Review Answers",
    "Retirement Dashboard",
    "Recommendations",
    "Projection Table",
    "Saved Scenarios",
    "Best Places to Retire",
    "Monte Carlo",
    "Stress Tests",
    "PDF Report",
    "AI Retirement Coach",
    "Retirement Age Optimizer",
    "Resources",
    "Help / Instructions",
]

PAGE_ICONS = {
    "Home": "🏠",
    "Guided Questions": "🧭",
    "Budget Builder": "💳",
    "Income Builder": "💼",
    "Spouse Questions": "👥",
    "Review Answers": "📝",
    "Retirement Dashboard": "📊",
    "Recommendations": "💡",
    "Projection Table": "📈",
    "Saved Scenarios": "💾",
    "Best Places to Retire": "📍",
    "Monte Carlo": "🎲",
    "Stress Tests": "🛡️",
    "PDF Report": "📄",
    "AI Retirement Coach": "🤖",
    "Retirement Age Optimizer": "🎯",
    "Resources": "📚",
    "Help / Instructions": "❓",
}

NAV_LABELS = {
    "Home": "Home",
    "Guided Questions": "Start My Blueprint",
    "Budget Builder": "Spending Plan",
    "Income Builder": "Income Plan",
    "Spouse Questions": "Household Plan",
    "Review Answers": "Review Inputs",
    "Retirement Dashboard": "Retirement Dashboard",
    "Recommendations": "Action Plan",
    "Projection Table": "Projection",
    "Saved Scenarios": "Saved Blueprints",
    "Best Places to Retire": "Places to Retire",
    "Monte Carlo": "Confidence Test",
    "Stress Tests": "Stress Tests",
    "PDF Report": "Blueprint Report",
    "AI Retirement Coach": "Blueprint Coach",
    "Retirement Age Optimizer": "Age Optimizer",
    "Resources": "Resources",
    "Help / Instructions": "Help",
}


# TEMPORARY TESTING OVERRIDE:
# Unlock all premium features for every user while testing.
# Before launch, remove this and connect is_premium_user to the paid subscription status.
st.session_state["is_premium_user"] = True

if "active_page" not in st.session_state or st.session_state.active_page not in PAGE_NAMES:
    st.session_state.active_page = "Home"

def auto_close_sidebar():
    """Auto-collapse the Streamlit sidebar after a sidebar navigation click.

    Streamlit has changed the sidebar button label across versions
    (Close sidebar, Collapse sidebar, Hide sidebar, etc.), so this uses
    several selectors and retries briefly after the page reruns.
    """
    components.html(
        """
        <script>
        (function() {
            function findCloseSidebarButton(doc) {
                const selectors = [
                    '[data-testid="stSidebarCollapseButton"] button',
                    '[data-testid="stSidebarCollapseButton"]',
                    'button[aria-label*="Close" i]',
                    'button[title*="Close" i]',
                    'button[aria-label*="Collapse" i]',
                    'button[title*="Collapse" i]',
                    'button[aria-label*="Hide" i]',
                    'button[title*="Hide" i]'
                ];

                for (const selector of selectors) {
                    const el = doc.querySelector(selector);
                    if (el) return el;
                }

                const buttons = Array.from(doc.querySelectorAll('button'));
                return buttons.find(btn => {
                    const text = (btn.innerText || btn.textContent || '').toLowerCase();
                    const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                    const title = (btn.getAttribute('title') || '').toLowerCase();
                    const combined = text + ' ' + label + ' ' + title;
                    return (
                        combined.includes('close sidebar') ||
                        combined.includes('collapse sidebar') ||
                        combined.includes('hide sidebar') ||
                        combined.includes('chevron_left') ||
                        combined.includes('keyboard_arrow_left')
                    );
                });
            }

            let tries = 0;
            const timer = setInterval(function() {
                tries += 1;
                const doc = window.parent.document;
                const btn = findCloseSidebarButton(doc);

                if (btn) {
                    btn.click();
                    clearInterval(timer);
                }

                if (tries >= 20) {
                    clearInterval(timer);
                }
            }, 150);
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def go_to_page(page_name: str):
    # Use a plain session_state value, not a widget key. This avoids the
    # StreamlitAPIException caused by trying to modify a radio widget after render.
    st.session_state.active_page = page_name
    st.session_state.close_sidebar_after_nav = True
    st.rerun()

def render_navigation():
    with st.sidebar:
        st.markdown("""
        <div style="padding:14px 6px 18px 6px;">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:18px;">
            <div style="width:46px;height:46px;border-radius:16px;background:linear-gradient(135deg,#2563EB,#14B8A6);display:flex;align-items:center;justify-content:center;color:white;font-weight:900;font-size:22px;">↗</div>
            <div>
              <div style="font-size:1.15rem;font-weight:900;color:#0F172A;line-height:1.1;">Retirement</div>
              <div style="font-size:1.15rem;font-weight:900;color:#0F172A;line-height:1.1;">Blueprint 101</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("PLAN SECTIONS")

        ordered_pages = [
            "Home",
            "Guided Questions",
            "Budget Builder",
            "Income Builder",
            "Review Answers",
            "Retirement Dashboard",
            "Recommendations",
            "Projection Table",
            "Saved Scenarios",
            "Retirement Age Optimizer",
            "Best Places to Retire",
            "PDF Report",
            "AI Retirement Coach",
            "Resources",
                    "Help / Instructions",
        ]

        for page_name in ordered_pages:
            is_active = st.session_state.active_page == page_name
            icon = PAGE_ICONS.get(page_name, "")
            display_name = NAV_LABELS.get(page_name, page_name)
            label = f"{icon} {display_name}"
            if st.button(
                label,
                key=f"sidebar_nav_{page_name}",
                use_container_width=True,
                disabled=is_active,
            ):
                go_to_page(page_name)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="border:1px solid #DBEAFE;border-radius:18px;padding:16px;background:linear-gradient(180deg,#F8FBFF,#EEF6FF);">
          <div style="font-size:1.25rem;margin-bottom:6px;">👑</div>
          <div style="font-weight:900;color:#0F172A;margin-bottom:6px;">Go Premium</div>
          <div style="color:#64748B;font-size:.9rem;line-height:1.4;">Unlock advanced tools and personalized retirement strategies.</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("View Premium", key="sidebar_view_premium", use_container_width=True):
            go_to_page("Retirement Dashboard")

render_navigation()
active_page = st.session_state.active_page

if st.session_state.get("close_sidebar_after_nav", False):
    auto_close_sidebar()
    st.session_state.close_sidebar_after_nav = False

# Safe projection object used by premium insight cards across pages.
# Keep this before any page rendering so Start My Blueprint / Home can use df safely.
can_run = len(required_missing()) == 0
try:
    df = run_projection() if can_run else pd.DataFrame()
except Exception as _projection_error:
    df = pd.DataFrame()
    can_run = False



def render_dashboard_roadmap():
    st.markdown("""
    <div class="rb-roadmap">
      <div class="rb-roadmap-title">Your Roadmap to a Confident Retirement</div>
      <div class="rb-roadmap-sub">A simple path from entering your numbers to building a full retirement plan.</div>
      <div class="rb-step-line"></div>
      <div class="rb-roadmap-grid">
        <div class="rb-step done">
          <div class="rb-step-num">1</div>
          <div class="rb-step-title">Enter Your Numbers</div>
          <div class="rb-step-copy">Start your blueprint</div>
        </div>
        <div class="rb-step done">
          <div class="rb-step-num">2</div>
          <div class="rb-step-title">Get Your Score</div>
          <div class="rb-step-copy">See where you stand</div>
        </div>
        <div class="rb-step">
          <div class="rb-step-num">3</div>
          <div class="rb-step-title">See When You Can Retire</div>
          <div class="rb-step-copy">Find your best retirement age</div>
        </div>
        <div class="rb-step">
          <div class="rb-step-num">4</div>
          <div class="rb-step-title">Compare Better Options</div>
          <div class="rb-step-copy">Explore scenarios and strategies</div>
        </div>
        <div class="rb-step">
          <div class="rb-step-num">5</div>
          <div class="rb-step-title">Take Action</div>
          <div class="rb-step-copy">Build your action plan</div>
        </div>
        <div class="rb-step">
          <div class="rb-step-num">6</div>
          <div class="rb-step-title">Create Your Plan</div>
          <div class="rb-step-copy">Get your full blueprint report</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def _dashboard_primary_next_step(df, rtv_score):
    try:
        rows = build_action_plan_rows(df, rtv_score)
        if rows and len(rows) > 1:
            top = rows[1]
            return {
                "action": top[0],
                "why": top[1],
                "impact": top[2],
                "new_score": top[3]
            }
    except Exception:
        pass
    return {
        "action": "Review your Action Plan",
        "why": "Use the action plan to see the highest-impact ways to strengthen your retirement readiness.",
        "impact": "+0",
        "new_score": str(int(rtv_score)) if rtv_score is not None else "0",
    }

def render_dashboard_combo_overview(df, rtv_score, rtv_label):
    planning_age = int(st.session_state.get("end_age", 90) or 90)
    ending = float(df["End Total"].iloc[-1] or 0)
    income_cov = float(df["Income Coverage Ratio"].mean() or 0)
    chosen_age = int(st.session_state.get("retire_age", 0) or 0)
    next_step = _dashboard_primary_next_step(df, rtv_score)

    st.markdown('<div class="rb-section-title">At-a-glance plan snapshot</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="rb-modern-card">
          <h4>Blueprint Score</h4>
          <div class="rb-modern-value">{int(rtv_score)}/100</div>
          <div class="rb-pill">{rtv_label}</div>
          <div style="height:10px"></div>
          <div class="rb-modern-muted">Your overall retirement readiness based on the current inputs.</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="rb-modern-card">
          <h4>Current Target Age</h4>
          <div class="rb-modern-value">{chosen_age}</div>
          <div class="rb-pill">Current plan setting</div>
          <div style="height:10px"></div>
          <div class="rb-modern-muted">Use Age Optimizer to compare earlier and later retirement ages side by side.</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="rb-modern-card">
          <h4>Money Left at {planning_age}</h4>
          <div class="rb-modern-value green">{money(ending)}</div>
          <div class="rb-pill">Projected</div>
          <div style="height:10px"></div>
          <div class="rb-modern-muted">Estimated portfolio balance remaining at the end of the plan.</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="rb-modern-card">
          <h4>Income Coverage</h4>
          <div class="rb-modern-value">{pct(income_cov)}</div>
          <div class="rb-pill">On track</div>
          <div style="height:10px"></div>
          <div class="rb-modern-muted">Percent of retirement spending covered by non-portfolio income.</div>
        </div>
        """, unsafe_allow_html=True)

    left, right = st.columns([1, 1.65])
    with left:
        st.markdown(f"""
        <div class="rb-next-step">
          <div class="rb-next-step-title">Next Best Step</div>
          <div style="color:#0F172A;font-size:1.05rem;font-weight:700;margin-bottom:8px;">{next_step['action']}</div>
          <div class="rb-modern-muted" style="margin-bottom:14px;">{next_step['why']}</div>
          <div class="rb-pill">Estimated Blueprint impact: {next_step['impact']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("See Action Plan", key="dashboard_combo_action_plan", use_container_width=True):
            go_to_page("Recommendations")
    with right:
        st.markdown('<div class="rb-modern-card"><h4>Projected Portfolio Value</h4><div class="rb-modern-muted" style="margin-top:4px;">See how the current plan may evolve over time.</div></div>', unsafe_allow_html=True)
        st.pyplot(plot_portfolio_area_chart(df), use_container_width=True)



def compact_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0.0

    sign = "-" if value < 0 else ""
    value = abs(value)

    if value >= 1_000_000:
        shown = value / 1_000_000
        if shown >= 10:
            return f"{sign}${shown:,.0f}M"
        return f"{sign}${shown:,.1f}M"
    if value >= 1_000:
        shown = value / 1_000
        if shown >= 100:
            return f"{sign}${shown:,.0f}K"
        return f"{sign}${shown:,.1f}K"
    return f"{sign}${value:,.0f}"


def render_tax_aware_withdrawal_plan(projection_df=None):
    """Premium-style educational withdrawal-order section.

    This does not give individualized tax advice. It gives a plain-English
    planning sequence based on the account balances entered in the app.
    """
    traditional = float(st.session_state.get("traditional", 0) or 0)
    roth = float(st.session_state.get("roth", 0) or 0)
    taxable = float(st.session_state.get("taxable", 0) or 0)
    cash = float(st.session_state.get("cash", 0) or 0)
    total_assets = traditional + roth + taxable + cash

    monthly_spending = float(st.session_state.get("monthly_spending", 0) or 0)
    annual_spending = monthly_spending * 12
    annual_income = (
        float(st.session_state.get("pension", 0) or 0)
        + float(st.session_state.get("other_income", 0) or 0)
        + float(st.session_state.get("ss", 0) or 0)
    )
    estimated_gap = max(0.0, annual_spending - annual_income)

    if projection_df is not None and not projection_df.empty and "Portfolio Need" in projection_df.columns:
        try:
            retired_rows = projection_df[projection_df.get("Household Retired", False) == True]
            if not retired_rows.empty:
                estimated_gap = float(retired_rows["Portfolio Need"].iloc[0] or estimated_gap)
        except Exception:
            pass

    st.markdown("""
    <div class="rb-insight-card">
      <div class="rb-insight-kicker">Premium Tool</div>
      <div class="rb-insight-title">Tax-Aware Withdrawal Plan</div>
      <div class="rb-insight-copy">
        A plain-English starting point for which accounts may make sense to draw from first.
        The goal is to fund spending while managing taxes, preserving flexibility, and keeping Roth money powerful later.
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Taxable Brokerage", money(taxable))
    with c2:
        st.metric("Traditional / Pre-Tax", money(traditional))
    with c3:
        st.metric("Roth", money(roth))
    with c4:
        st.metric("Estimated Annual Gap", money(estimated_gap))

    order_rows = []
    step = 1
    if cash > 0:
        order_rows.append({
            "Step": step,
            "Account": "Cash / Bucket 1",
            "Use For": "Near-term spending buffer",
            "Why": "Can reduce the need to sell investments during bad market years.",
            "Watchout": "Too much cash can drag down long-term growth.",
        })
        step += 1
    if taxable > 0:
        order_rows.append({
            "Step": step,
            "Account": "Taxable brokerage",
            "Use For": "Early flexible withdrawals",
            "Why": "Often gives flexibility and may receive capital-gains treatment instead of ordinary income treatment.",
            "Watchout": "Selling appreciated holdings can create taxable gains.",
        })
        step += 1
    if traditional > 0:
        order_rows.append({
            "Step": step,
            "Account": "Traditional 401(k) / IRA",
            "Use For": "Bracket-aware withdrawals or Roth conversions",
            "Why": "Strategic withdrawals before RMD age may reduce future tax pressure.",
            "Watchout": "Withdrawals are generally taxed as ordinary income and may affect Medicare/IRMAA later.",
        })
        step += 1
    if roth > 0:
        order_rows.append({
            "Step": step,
            "Account": "Roth IRA / Roth 401(k)",
            "Use For": "Later-life flexibility and tax-free reserve",
            "Why": "Preserving Roth can help with future tax control, survivor planning, and legacy flexibility.",
            "Watchout": "Using Roth too early can give up years of tax-free growth.",
        })

    if not order_rows:
        st.warning("Add account balances first, then this section will build a suggested withdrawal order.")
        return

    st.subheader("Suggested withdrawal order")
    st.dataframe(pd.DataFrame(order_rows), use_container_width=True, hide_index=True)

    st.subheader("What this means for your blueprint")
    notes = []
    if taxable <= 0 and traditional > 0:
        notes.append("You have little or no taxable brokerage entered, so early retirement withdrawals may lean more heavily on pre-tax money unless cash/Bucket 1 is available.")
    if traditional > roth * 3 and traditional > 250000:
        notes.append("Your pre-tax balance is much larger than Roth. That can create future RMD and survivor-tax pressure, so Roth conversions may be worth testing.")
    if roth > 0:
        notes.append("You have Roth money available. A common strategy is to preserve it for later years unless it is needed to avoid a high tax year.")
    if cash < estimated_gap and estimated_gap > 0:
        notes.append("Your cash/Bucket 1 balance may cover less than one year of estimated portfolio withdrawals. A larger safety bucket may reduce sequence-of-returns risk.")
    if not notes:
        notes.append("Your account mix gives the app enough flexibility to test withdrawal sequencing, Roth conversions, and Bucket 1 planning.")

    for note in notes:
        st.info(note)

    st.markdown("""
    <div class="rb-next-box">
      <div class="rb-next-heading">Educational rule of thumb</div>
      <div class="rb-muted">
        Many retirees start with taxable/cash for flexibility, use traditional accounts strategically to manage brackets and future RMDs,
        and preserve Roth assets for later tax-free flexibility. The best order can change based on Social Security timing,
        healthcare subsidies, RMDs, pension income, and filing status.
      </div>
    </div>
    """, unsafe_allow_html=True)

    nav_cols = st.columns(3)
    with nav_cols[0]:
        if st.button("Test Roth Conversions", use_container_width=True, key="tax_plan_test_roth"):
            go_to_page("Guided Questions")
    with nav_cols[1]:
        if st.button("Review Projection Table", use_container_width=True, key="tax_plan_projection"):
            st.session_state.projection_focus = ""
            st.rerun()
    with nav_cols[2]:
        if st.button("Create Blueprint Report", use_container_width=True, key="tax_plan_report"):
            go_to_page("PDF Report")

    st.caption("Educational planning estimate only. Confirm tax decisions with a qualified CPA, tax professional, or fiduciary financial planner.")


def render_guided_progress(current_step: int):
    steps = [
        (1, "Start Blueprint", "Enter core numbers"),
        (2, "Spending Plan", "Estimate spending"),
        (3, "Income Plan", "Add income sources"),
        (4, "Retirement Dashboard", "Review results"),
        (5, "Improve / Upgrade", "Test better options"),
    ]

    html = ['<div class="rb-progress-wrap">']
    html.append('<div class="rb-progress-title">YOUR RETIREMENT BLUEPRINT PATH</div>')
    html.append('<div class="rb-progress-grid">')

    for num, label, copy in steps:
        status = "done" if num < current_step else ("active" if num == current_step else "")
        html.append(
            f'<div class="rb-progress-step {status}">'
            f'<div class="rb-progress-num">{num}</div>'
            f'<div class="rb-progress-label">{label}</div>'
            f'<div class="rb-progress-copy">{copy}</div>'
            f'</div>'
        )

    html.append('</div></div>')
    st.markdown("".join(html), unsafe_allow_html=True)


if active_page == PAGE_NAMES[0]:
    render_guided_progress(1)
    missing_items_home = required_missing()

    safe_df_home = pd.DataFrame()
    safe_can_run_home = False

    try:
        if len(missing_items_home) == 0:
            safe_df_home = run_projection()
            safe_can_run_home = isinstance(safe_df_home, pd.DataFrame) and not safe_df_home.empty
    except Exception as e:
        safe_df_home = pd.DataFrame()
        safe_can_run_home = False
        st.warning(f"Projection cannot run yet: {e}")

    if safe_can_run_home:
        try:
            score_result_home = calculate_rtv_score(safe_df_home)
            rtv_score_home = score_result_home[0]
            rtv_label_home = score_result_home[1]
        except Exception:
            rtv_score_home = 0
            rtv_label_home = "Incomplete"

        rtv_value_home = f"{rtv_score_home}/100"
        rtv_note_home = f"{rtv_label_home} readiness score based on your current inputs."
        planning_age_home = int(st.session_state.get("end_age", 90) or 90)
        money_left_home = compact_money(safe_df_home["End Total"].iloc[-1])

        unmet_need_home = float(safe_df_home["Unmet Need"].sum() or 0)
        end_total_home = float(safe_df_home["End Total"].iloc[-1] or 0)
        if unmet_need_home > 0 or end_total_home <= 0:
            retire_status_home = "Not Yet"
            retire_status_note_home = "The current target age may need changes."
        elif rtv_score_home >= 80:
            retire_status_home = "Looks Good"
            retire_status_note_home = "Your target retirement age appears realistic."
        else:
            retire_status_home = "Maybe"
            retire_status_note_home = "The plan may work, but needs review."

        avg_gap_home = float(safe_df_home["Portfolio Need"].mean() if "Portfolio Need" in safe_df_home.columns else 0)
        if avg_gap_home <= 0 and "Total Spending" in safe_df_home.columns and "Total Non-Portfolio Income" in safe_df_home.columns:
            avg_gap_home = float((safe_df_home["Total Spending"] - safe_df_home["Total Non-Portfolio Income"]).clip(lower=0).mean())
        monthly_gap_raw_home = max(avg_gap_home, 0) / 12
        monthly_gap_home = compact_money(monthly_gap_raw_home)

        target_retire_age_home = int(st.session_state.get("retire_age", 0) or 0)
        ss_start_age_home = int(st.session_state.get("user_ss_age", 62) or 62)
        healthcare_gap_years_home = max(0, min(65, planning_age_home) - target_retire_age_home) if target_retire_age_home else 0
        ss_gap_years_home = max(0, ss_start_age_home - target_retire_age_home) if target_retire_age_home else 0
        annual_spending_home = annual_household_spending() + float(st.session_state.get("healthcare", 0) or 0)
        total_income_first_year_home = 0
        try:
            if "Total Non-Portfolio Income" in safe_df_home.columns:
                total_income_first_year_home = float(safe_df_home["Total Non-Portfolio Income"].iloc[0] or 0)
        except Exception:
            total_income_first_year_home = 0

        dashboard_reason_bits = []
        dashboard_idea_bits = []

        if rtv_score_home < 60:
            dashboard_status_plain = "This plan needs work before it looks retirement-ready."
            dashboard_reason_bits.append(f"<b>Blueprint Score:</b> Your score is <b>{rtv_score_home}/100</b>. {dashboard_status_plain}")
            dashboard_idea_bits.append("Try a later retirement age.")
            dashboard_idea_bits.append("Try lowering monthly spending.")
            dashboard_idea_bits.append("Add income sources if available.")
        elif rtv_score_home < 80:
            dashboard_status_plain = "This plan may be possible, but the cushion is thin."
            dashboard_reason_bits.append(f"<b>Blueprint Score:</b> Your score is <b>{rtv_score_home}/100</b>. {dashboard_status_plain}")
            dashboard_idea_bits.append("Build more cushion before retirement.")
            dashboard_idea_bits.append("Stress test bad market years.")
            dashboard_idea_bits.append("Compare Social Security timing.")
        else:
            dashboard_status_plain = "This plan looks stronger under the current assumptions."
            dashboard_reason_bits.append(f"<b>Blueprint Score:</b> Your score is <b>{rtv_score_home}/100</b>. {dashboard_status_plain} You should still stress-test it.")
            dashboard_idea_bits.append("Save this version as your baseline.")
            dashboard_idea_bits.append("Run stress tests to see how it handles bad years.")
            dashboard_idea_bits.append("Compare one or two alternate retirement ages.")

        if ss_gap_years_home > 0:
            dashboard_reason_bits.append(f"<b>Social Security gap:</b> There are about <b>{ss_gap_years_home} year(s)</b> between the tested retirement age and when Social Security starts. During that gap, savings may need to carry more of the spending.")
            dashboard_idea_bits.append("Use the Action Plan to test whether delaying retirement or changing Social Security timing improves the score.")
        else:
            dashboard_reason_bits.append("<b>Social Security timing:</b> Social Security appears to start at or before the tested retirement age, which can reduce pressure on savings.")

        if healthcare_gap_years_home > 0:
            dashboard_reason_bits.append(f"<b>Healthcare bridge:</b> There are about <b>{healthcare_gap_years_home} year(s)</b> before Medicare age 65. Healthcare costs during this bridge period can reduce the plan cushion.")
            dashboard_idea_bits.append("Check whether healthcare costs before Medicare are realistic.")
        else:
            dashboard_reason_bits.append("<b>Healthcare bridge:</b> The plan does not show a major pre-Medicare healthcare bridge based on the current ages.")

        if monthly_gap_raw_home > 0:
            dashboard_reason_bits.append(f"<b>Monthly gap from savings:</b> After estimated income is counted, about <b>{compact_money(monthly_gap_raw_home)}</b> per month still needs to come from savings.")
            if monthly_gap_raw_home >= 8000:
                dashboard_idea_bits.append("The savings gap is large, so spending, income, and retirement age are the biggest levers.")
            elif monthly_gap_raw_home >= 3000:
                dashboard_idea_bits.append("The savings gap is manageable to test, but still deserves attention.")
        else:
            dashboard_reason_bits.append("<b>Monthly gap from savings:</b> Estimated income appears to cover the monthly spending need in the early years.")

        if end_total_home <= 0 or unmet_need_home > 0:
            dashboard_reason_bits.append("<b>Money left:</b> The projection shows a shortfall or portfolio depletion. The biggest levers are usually retiring later, reducing spending, increasing income, or saving more before retirement.")
            dashboard_idea_bits.append("Go to the Action Plan to see which lever may add the most points.")
        else:
            dashboard_reason_bits.append(f"<b>Money left:</b> The projection estimates about <b>{compact_money(end_total_home)}</b> left at the end of the plan. This is a cushion estimate, not a guarantee.")
            if end_total_home < 250000:
                dashboard_idea_bits.append("The ending cushion is thin, so stress testing matters.")
            else:
                dashboard_idea_bits.append("The ending balance is a cushion estimate. Use stress tests before relying on it.")

        dashboard_reason_html = "<br/><br/>".join(dashboard_reason_bits)

        # Deduplicate action ideas while preserving order.
        cleaned_ideas = []
        seen_ideas = set()
        for idea in dashboard_idea_bits:
            if idea not in seen_ideas:
                cleaned_ideas.append(idea)
                seen_ideas.add(idea)

        dashboard_ideas_html = "".join([f"<li>{idea}</li>" for idea in cleaned_ideas[:5]])

        status_title = "Your plan is ready to review."
        status_note = "Use the Retirement Dashboard, Action Plan, Confidence Test, Stress Tests, and Blueprint Report for deeper analysis."
        required_panel = ""
    else:
        rtv_value_home = "Incomplete"
        rtv_note_home = "Complete your plan to see your Blueprint Score."
        planning_age_home = int(st.session_state.get("end_age", 90) or 90)
        money_left_home = "$0"
        retire_status_home = "Not Ready"
        retire_status_note_home = "Enter your core numbers to test your retirement age."
        monthly_gap_home = "$0"
        monthly_gap_raw_home = 0
        dashboard_reason_html = "Complete your Start Blueprint, Spending Plan, and Income Plan first. Then this dashboard will explain what is helping or hurting the retirement estimate."
        status_title = "You are not signed in." if not user else "Your plan needs a little more information."
        status_note = "You can still use the planner, but saved blueprints require an account." if not user else "Complete the required fields below to unlock projections and recommendations."
        required_panel = ", ".join(missing_items_home) if missing_items_home else "Review Start My Blueprint and Spending Plan."

    if safe_can_run_home:
        st.markdown("""
        <div class="rb-page-section-label">Retirement Dashboard</div>
        <div class="rb-muted" style="margin-bottom: 12px;">Your retirement results based on the information entered so far.</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="rb-card-grid">
          <div class="rb-card">
            <div class="rb-card-top"><div class="rb-card-label">Blueprint Score</div><div class="rb-icon">☆</div></div>
            <div class="rb-card-value">{rtv_value_home}</div>
            <div class="rb-card-note">{rtv_note_home}</div>
          </div>
          <div class="rb-card">
            <div class="rb-card-top"><div class="rb-card-label">Can I Retire at This Age?</div><div class="rb-icon">✓</div></div>
            <div class="rb-card-value">{retire_status_home}</div>
            <div class="rb-card-note">{retire_status_note_home}</div>
          </div>
          <div class="rb-card">
            <div class="rb-card-top"><div class="rb-card-label">Money Left at Age {planning_age_home}</div><div class="rb-icon">$</div></div>
            <div class="rb-card-value money-compact">{money_left_home}</div>
            <div class="rb-card-note">Estimated money remaining at the end of the plan.</div>
          </div>
          <div class="rb-card">
            <div class="rb-card-top"><div class="rb-card-label">Monthly Gap From Savings</div><div class="rb-icon">↗</div></div>
            <div class="rb-card-value">{monthly_gap_home}</div>
            <div class="rb-card-note">Estimated monthly spending that needs to come from savings.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="rb-save-callout">
          <div>
            <div class="rb-save-kicker">Baseline Blueprint</div>
            <div class="rb-save-title">Your blueprint is ready. Save this version before testing changes.</div>
            <div class="rb-save-copy">
              Saving gives you a starting point before you adjust retirement age, spending, Social Security timing, or income.
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        save_cols = st.columns([1, 1])
        with save_cols[0]:
            if st.button("Save This Blueprint", type="primary", use_container_width=True, key="dashboard_save_baseline_blueprint"):
                go_to_page("Saved Scenarios")
        with save_cols[1]:
            if st.button("Next: View Action Plan", use_container_width=True, key="dashboard_view_action_after_save_prompt"):
                go_to_page("Recommendations")
    else:
        st.markdown("""
        <div class="rb-insight-card" style="padding: 26px 28px; margin-bottom: 22px;">
          <div style="display:grid; grid-template-columns: minmax(0, 1.2fr) minmax(320px, .8fr); gap: 28px; align-items:center;">
            <div>
              <div class="rb-insight-kicker">Retirement Blueprint 101</div>
              <div style="font-size: clamp(2.0rem, 4vw, 4.2rem); line-height: 1.02; font-weight: 950; color:#0f172a; letter-spacing:-.05em; margin: 6px 0 14px;">
                Find out if your retirement plan can actually work.
              </div>
              <div class="rb-insight-copy" style="max-width: 920px; font-size: 1.05rem;">
                No finance degree needed. Enter your age, savings, spending, Social Security, and income.
                The app turns those numbers into a simple retirement blueprint: when you may be able to retire,
                how long your money may last, and what to improve first.
              </div>
              <div style="display:flex; flex-wrap:wrap; gap:10px; margin-top:18px;">
                <span style="background:#dcfce7; color:#166534; border:1px solid #bbf7d0; border-radius:999px; padding:8px 12px; font-weight:800;">Simple answers</span>
                <span style="background:#e0f2fe; color:#075985; border:1px solid #bae6fd; border-radius:999px; padding:8px 12px; font-weight:800;">What-if testing</span>
                <span style="background:#eef2ff; color:#3730a3; border:1px solid #c7d2fe; border-radius:999px; padding:8px 12px; font-weight:800;">Action plan included</span>
              </div>
            </div>
            <div style="background:#ffffff; border:1px solid #dbeafe; border-radius:24px; padding:18px; box-shadow:0 22px 50px rgba(15,23,42,.10); transform: rotate(1deg);">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div style="font-weight:950; color:#0f172a; font-size:1.15rem;">Example Blueprint</div>
                <div style="font-size:.78rem; font-weight:900; color:#2563eb; background:#eff6ff; border-radius:999px; padding:5px 9px;">PREVIEW</div>
              </div>
              <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                <div style="background:#f8fafc; border:1px solid #e5e7eb; border-radius:16px; padding:13px;">
                  <div style="color:#64748b; font-size:.78rem; font-weight:800;">Blueprint Score</div>
                  <div style="font-size:2rem; font-weight:950; color:#0f172a;">76/100</div>
                  <div style="color:#166534; font-weight:900; font-size:.78rem;">Likely viable</div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e5e7eb; border-radius:16px; padding:13px;">
                  <div style="color:#64748b; font-size:.78rem; font-weight:800;">Retire at 60?</div>
                  <div style="font-size:2rem; font-weight:950; color:#0f172a;">Maybe</div>
                  <div style="color:#b45309; font-weight:900; font-size:.78rem;">Needs review</div>
                </div>
              </div>
              <div style="margin-top:12px; background:linear-gradient(135deg,#eff6ff,#ecfdf5); border:1px solid #bfdbfe; border-radius:18px; padding:14px;">
                <div style="font-weight:950; color:#0f172a; margin-bottom:8px;">Plain-English Summary</div>
                <div style="color:#475569; line-height:1.45; font-size:.95rem;">
                  Your plan may work, but the biggest pressure is how much must come from savings each month.
                </div>
              </div>
              <div style="margin-top:12px; display:grid; gap:8px;">
                <div style="display:flex; gap:8px; align-items:flex-start;"><span>✅</span><span style="color:#334155;">See your retirement score</span></div>
                <div style="display:flex; gap:8px; align-items:flex-start;"><span>📉</span><span style="color:#334155;">Spot risk before you retire</span></div>
                <div style="display:flex; gap:8px; align-items:flex-start;"><span>🧭</span><span style="color:#334155;">Get your next best step</span></div>
              </div>
            </div>
          </div>
        </div>

        <div style="display:grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap:16px; margin-bottom: 22px;">
          <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:20px; padding:20px; box-shadow:0 12px 28px rgba(15,23,42,.06);">
            <div style="font-size:2.4rem; font-weight:950; color:#2563eb; line-height:1;">67%</div>
            <div style="font-weight:900; color:#0f172a; margin-top:8px;">worry more about running out of money than death</div>
            <div class="rb-muted" style="margin-top:8px;">That fear is exactly what this app is built to help people test in plain English.</div>
            <div style="font-size:.78rem; color:#64748b; margin-top:10px;">Source: Allianz Life 2026 Annual Retirement Study</div>
          </div>
          <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:20px; padding:20px; box-shadow:0 12px 28px rgba(15,23,42,.06);">
            <div style="font-size:2.4rem; font-weight:950; color:#16a34a; line-height:1;">3</div>
            <div style="font-weight:900; color:#0f172a; margin-top:8px;">big questions answered</div>
            <div class="rb-muted" style="margin-top:8px;">Can I retire? Will my money last? What should I change first?</div>
          </div>
          <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:20px; padding:20px; box-shadow:0 12px 28px rgba(15,23,42,.06);">
            <div style="font-size:2.4rem; font-weight:950; color:#0f172a; line-height:1;">1</div>
            <div style="font-weight:900; color:#0f172a; margin-top:8px;">personal blueprint</div>
            <div class="rb-muted" style="margin-top:8px;">A simple plan you can save, compare, improve, and turn into a report.</div>
          </div>
        </div>

        <div style="background:#f8fafc; border:1px solid #e5e7eb; border-radius:22px; padding:20px; margin-bottom: 22px;">
          <div style="font-weight:950; color:#0f172a; font-size:1.25rem; margin-bottom:12px;">What you will get</div>
          <div style="display:grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap:12px;">
            <div style="background:#ffffff; border-radius:16px; padding:14px; border:1px solid #e5e7eb;"><b>Retirement score</b><br/><span class="rb-muted">A simple signal showing where your plan stands.</span></div>
            <div style="background:#ffffff; border-radius:16px; padding:14px; border:1px solid #e5e7eb;"><b>Money timeline</b><br/><span class="rb-muted">See key ages, income timing, and projected balances.</span></div>
            <div style="background:#ffffff; border-radius:16px; padding:14px; border:1px solid #e5e7eb;"><b>Action plan</b><br/><span class="rb-muted">Find the changes that may improve confidence fastest.</span></div>
            <div style="background:#ffffff; border-radius:16px; padding:14px; border:1px solid #e5e7eb;"><b>Scenario testing</b><br/><span class="rb-muted">Compare retiring earlier, later, or spending differently.</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    if not required_panel:
        st.success("Your blueprint has enough information to review the dashboard, action plan, confidence test, stress tests, and reports.")
        render_premium_insight("What your blueprint is telling you", df if can_run else None, "general")

    st.markdown("### Start Here: Your Retirement Blueprint Process")
    st.caption("Follow these steps in order. The sidebar stays available when you are ready to jump around, but this gives new users the clearest path.")

    process_left, process_right = st.columns([1.35, 1])

    with process_left:
        st.markdown("""
        <div class="rb-panel">
          <div class="rb-panel-title"><span>🚀</span><span>Quick Start Roadmap</span></div>
          <div class="rb-qs-step"><span class="rb-qs-step-num">1</span><span class="rb-qs-step-text"><b>Start My Blueprint</b><br/>Enter your age, savings, retirement age, Social Security, returns, and household setup.</span></div>
          <div class="rb-qs-step"><span class="rb-qs-step-num">2</span><span class="rb-qs-step-text"><b>Build Your Spending Plan</b><br/>Estimate how much you want to spend each year in retirement.</span></div>
          <div class="rb-qs-step"><span class="rb-qs-step-num">3</span><span class="rb-qs-step-text"><b>Add Income Sources</b><br/>Include pension, rental income, part-time work, or other retirement income.</span></div>
          <div class="rb-qs-step"><span class="rb-qs-step-num">4</span><span class="rb-qs-step-text"><b>Review Your Dashboard</b><br/>See your Blueprint Score, projected money left, withdrawal pressure, and income coverage.</span></div>
          <div class="rb-qs-step"><span class="rb-qs-step-num">5</span><span class="rb-qs-step-text"><b>Compare and Improve</b><br/>Use the Action Plan, Age Optimizer, scenarios, and bucket strategy to improve the plan.</span></div>
          <div class="rb-qs-step"><span class="rb-qs-step-num">6</span><span class="rb-qs-step-text"><b>Save or Export</b><br/>Save blueprints, compare options, and export a full Blueprint Report.</span></div>
        </div>
        """, unsafe_allow_html=True)

    with process_right:
        st.markdown("""
        <div class="rb-panel">
          <div class="rb-panel-title"><span>✅</span><span>Next Best Step</span></div>
          <div class="rb-next-box">
            <div class="rb-next-heading">Start with your blueprint inputs</div>
            <div class="rb-muted">Begin with the core numbers, then review your inputs before reading the dashboard.</div>
          </div>
          <div class="rb-tips">
            <div class="rb-tips-title">💡 Helpful Tips</div>
            <ul>
              <li>Use estimates at first. You can refine them later.</li>
              <li>Move left-to-right through the sidebar for the easiest flow.</li>
              <li>Save multiple blueprints to compare different retirement choices.</li>
            </ul>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    if st.button("Start My Blueprint", type="primary", use_container_width=True, key="home_big_start_before_premium"):
        go_to_page("Guided Questions")

    st.markdown("### Premium Retirement Tools")
    st.caption("Once the basics are entered, these tools help compare retirement ages, reduce risk, plan withdrawals, and create a fuller retirement blueprint.")
    render_premium_lock_cards()

    st.caption("Educational planning tool only. Not financial, tax, legal, insurance, or investment advice.")


if active_page == PAGE_NAMES[1]:
    render_page_shell("Start My Blueprint", "Set the core numbers that drive your retirement blueprint: ages, savings, contributions, Social Security, returns, and your bucket strategy.", "🧭")
    render_guided_progress(1)
    page_help(
        "Guided Retirement Questions",
        "This page collects the core numbers for your retirement blueprint: ages, savings, contributions, Social Security, expected returns, inflation, Roth conversions, and premium 2-bucket strategy. These inputs drive the Retirement Dashboard, Blueprint Score, Action Plan, and Projection."
    )

    blueprint_mode = st.radio(
        "Choose blueprint type",
        ["Quick Blueprint", "Detailed Blueprint"],
        index=0 if st.session_state.get("blueprint_mode", "Quick Blueprint") == "Quick Blueprint" else 1,
        key="blueprint_mode",
        horizontal=True,
        help="Switch between the simple starter version and the full detailed planning form."
    )

    if blueprint_mode == "Quick Blueprint":
        st.subheader("Quick Blueprint")
        st.caption("Simple starter version for free trial users. Enter the basics first, then use the detailed section below when you want a more precise plan.")

        with st.expander("Open Quick Blueprint starter", expanded=True):
            q1, q2, q3 = st.columns(3)
            quick_current_age = q1.number_input("Current age", 0, 100, st.session_state.current_age, help=FIELD_HELP["current_age"])
            quick_retire_age = q2.number_input("Target retirement age", 0, 100, st.session_state.retire_age, help=FIELD_HELP["retire_age"])
            quick_end_age = q3.number_input("Plan through age", 0, 110, st.session_state.end_age, help=FIELD_HELP["end_age"])

            q1, q2, q3 = st.columns(3)
            quick_total_savings = q1.number_input(
                "Total retirement savings",
                min_value=0,
                value=int(float(st.session_state.traditional or 0) + float(st.session_state.roth or 0) + float(st.session_state.taxable or 0) + float(st.session_state.cash or 0)),
                step=10000,
                help="A simple total of retirement savings across 401k, IRA, Roth, taxable accounts, and cash."
            )
            quick_monthly_spending = q2.number_input(
                "Monthly retirement spending",
                min_value=0,
                value=int(float(st.session_state.get("monthly_spending", 0) or 0)),
                step=500,
                help="A simple estimate of how much you expect to spend each month in retirement."
            )
            quick_annual_contribution = q3.number_input(
                "Annual savings until retirement",
                min_value=0,
                value=int(st.session_state.annual_contribution),
                step=5000,
                help=FIELD_HELP["annual_contribution"]
            )

            q1, q2, q3 = st.columns(3)
            quick_ss_age = q1.number_input("Social Security start age", 62, 70, st.session_state.user_ss_age, help=FIELD_HELP["user_ss_age"])
            quick_ss = q2.number_input("Annual Social Security at 62", min_value=0, value=st.session_state.user_ss, step=1000, help=FIELD_HELP["user_ss"])
            quick_growth_return = q3.slider(
            "Expected average return",
            min_value=0.0,
            max_value=30.0,
            value=min(max(float(st.session_state.growth_return) * 100, 0.0), 30.0),
            step=0.25,
            format="%.2f%%",
            help=FIELD_HELP["growth_return"],
        ) / 100

            quick_save = st.button("Save Quick Blueprint", type="primary", use_container_width=True, key="save_quick_blueprint_button")

            if quick_save:
                quick_traditional = int(quick_total_savings * 0.80)
                quick_roth = int(quick_total_savings * 0.20)

                for k, v in {
                    "current_age": quick_current_age,
                    "retire_age": quick_retire_age,
                    "end_age": quick_end_age,
                    "traditional": quick_traditional,
                    "roth": quick_roth,
                    "taxable": 0,
                    "cash": 0,
                    "annual_contribution": quick_annual_contribution,
                    "user_ss_age": quick_ss_age,
                    "user_ss": quick_ss,
                    "growth_return": quick_growth_return,
                    "safe_return": 0.045,
                    "inflation": 0.03,
                    "bucket1_years": 3.0,

                    # CRITICAL MATH FIX:
                    # Quick Blueprint spending must feed the same fields used by run_projection().
                    "budget_mode": "Flat monthly number",
                    "flat_monthly_spending": quick_monthly_spending,

                    # Backward-compatible aliases used by the Basic Blueprint dashboard and older page logic.
                    "monthly_spending": quick_monthly_spending,
                    "spending_quick_monthly": quick_monthly_spending,
                    "basic_blueprint_monthly_spending": quick_monthly_spending,
                    "basic_blueprint_annual_spending": quick_monthly_spending * 12,
                    "monthly_expenses": quick_monthly_spending,
                    "annual_spending": quick_monthly_spending * 12,
                    "monthly_needs": quick_monthly_spending,
                    "retirement_monthly_spending": quick_monthly_spending,
                }.items():
                    st.session_state[k] = v

                st.session_state.quick_blueprint_saved = True
                st.success("Quick Blueprint saved. Your Basic Blueprint is ready.")

        if st.session_state.get("quick_blueprint_saved"):
            st.markdown("""
            <div class="rb-next-box">
              <div class="rb-next-heading">Basic Blueprint ready</div>
              <div class="rb-muted">
                Your starter blueprint uses the basics you entered: age, target retirement age, savings,
                monthly retirement spending, Social Security, annual savings, and expected return.
                Next, review the dashboard to see your first retirement snapshot.
              </div>
            </div>
            """, unsafe_allow_html=True)

            b1, b2 = st.columns(2)
            with b1:
                if st.button("View My Basic Blueprint", type="primary", use_container_width=True, key="quick_next_dashboard"):
                    st.session_state.quick_blueprint_saved = True
                    st.session_state.active_page = "Retirement Dashboard"
                    st.rerun()
            with b2:
                if st.button("Unlock Detailed Blueprint", use_container_width=True, key="quick_next_unlock"):
                    st.session_state.show_premium_prompt = True
                    st.rerun()

            st.caption("Detailed spending, account-level planning, tax settings, Roth conversions, home equity, and bucket strategy are part of Detailed Blueprint.")

        if st.session_state.get("show_premium_prompt"):
            st.info("Detailed Blueprint is a Premium feature. Free trial users can continue with Quick Blueprint, then unlock Premium for account-level planning, tax settings, Roth conversions, home equity, detailed spending, and bucket strategy.")

    if blueprint_mode == "Detailed Blueprint":
        st.subheader("Detailed Blueprint")
        st.caption("Premium planning section. Use this when you want the full planning model: account types, tax settings, home equity, Roth conversions, and bucket strategy.")

        is_premium_user = bool(st.session_state.get("is_premium_user", False))

        if not is_premium_user:
            st.markdown("""
            <div class="rb-insight-card">
              <div class="rb-insight-kicker">Premium Feature</div>
              <div class="rb-insight-title">Unlock Detailed Blueprint</div>
              <div class="rb-insight-copy">
                Detailed Blueprint adds detailed spending, account-level savings, tax settings, home equity, Roth conversions,
                household planning, and bucket strategy. Quick Blueprint remains available for the free trial.
              </div>
            </div>
            """, unsafe_allow_html=True)
            st.info("Free trial users can use Quick Blueprint above. Detailed Blueprint is reserved for Premium users.")
        else:
            # Live spouse/partner selector.
            # This stays OUTSIDE st.form so spouse fields appear/disappear immediately when clicked.
            st.subheader("Household")
            has_spouse_live = st.checkbox(
                "Include spouse or partner in this blueprint?",
                value=bool(st.session_state.get("has_spouse", False)),
                help="Turn this on if the retirement plan should include a spouse or partner. Leave it off for an individual plan.",
                key="spouse_live_selector",
            )
            st.session_state.has_spouse = has_spouse_live

            with st.form("guided_form"):
                st.subheader("Timeline")
                c1, c2, c3 = st.columns(3)
                current_age = c1.number_input("How old are you today?", 0, 100, st.session_state.current_age, help=FIELD_HELP["current_age"])
                retire_age = c2.number_input("What age do you want to retire?", 0, 100, st.session_state.retire_age, help=FIELD_HELP["retire_age"])
                end_age = c3.number_input("What age should the plan last until?", 0, 110, st.session_state.end_age, help=FIELD_HELP["end_age"])

                st.subheader("Savings")
                c1, c2, c3, c4 = st.columns(4)
                traditional = c1.number_input("Traditional 401k/IRA total", min_value=0, value=st.session_state.traditional, step=10000, help=FIELD_HELP["traditional"])
                roth = c2.number_input("Roth total", min_value=0, value=st.session_state.roth, step=10000, help=FIELD_HELP["roth"])
                taxable = c3.number_input("Taxable brokerage", min_value=0, value=st.session_state.taxable, step=10000, help=FIELD_HELP["taxable"])
                cash = c4.number_input("Bucket 1 / cash / safe money", min_value=0, value=st.session_state.cash, step=10000, help=FIELD_HELP["cash"])

                st.subheader("Contributions, healthcare, Social Security")
                c1, c2, c3, c4 = st.columns(4)
                annual_contribution = c1.number_input("Annual contributions until retirement", min_value=0, value=st.session_state.annual_contribution, step=5000, help=FIELD_HELP["annual_contribution"])
                healthcare = c2.number_input("Your annual healthcare in retirement", min_value=0, value=st.session_state.healthcare, step=1000, help=FIELD_HELP["healthcare"])
                user_ss_age = c3.number_input("Your Social Security start age", 62, 70, st.session_state.user_ss_age, help=FIELD_HELP["user_ss_age"])
                user_ss = c4.number_input("Your annual Social Security at 62", min_value=0, value=st.session_state.user_ss, step=1000, help=FIELD_HELP["user_ss"])

                st.subheader("Household")
                has_spouse = bool(st.session_state.get("has_spouse", False))

                if has_spouse:
                    st.info("Spouse / partner fields are included in this blueprint.")
                    c1, c2, c3 = st.columns(3)
                    spouse_age = c1.number_input("Spouse current age", min_value=0, max_value=110, value=st.session_state.spouse_age, help=FIELD_HELP["spouse_age"])
                    spouse_retire_age = c2.number_input("Spouse retirement age", min_value=0, max_value=110, value=st.session_state.spouse_retire_age, help=FIELD_HELP["spouse_retire_age"])
                    spouse_plan_age = c3.number_input("Spouse plan-through age", min_value=0, max_value=120, value=st.session_state.spouse_plan_age, help=FIELD_HELP["spouse_plan_age"])

                    c1, c2, c3, c4 = st.columns(4)
                    spouse_annual_contribution = c1.number_input("Spouse annual contributions", min_value=0, value=st.session_state.spouse_annual_contribution, step=5000, help=FIELD_HELP["spouse_annual_contribution"])
                    spouse_healthcare = c2.number_input("Spouse annual healthcare", min_value=0, value=st.session_state.spouse_healthcare, step=1000, help=FIELD_HELP["spouse_healthcare"])
                    spouse_ss_age = c3.number_input("Spouse Social Security age", 62, 70, st.session_state.spouse_ss_age, help=FIELD_HELP["spouse_ss_age"])
                    spouse_ss = c4.number_input("Spouse annual Social Security at 62", min_value=0, value=st.session_state.spouse_ss, step=1000, help=FIELD_HELP["spouse_ss"])

                    survivor_ss_strategy = st.selectbox(
                        "Survivor Social Security strategy",
                        ["Higher benefit continues", "User benefit only"],
                        index=0 if st.session_state.survivor_ss_strategy == "Higher benefit continues" else 1,
                        help="Usually, the surviving spouse keeps the higher Social Security benefit and loses the smaller one."
                    )
                else:
                    spouse_age = 0
                    spouse_retire_age = 0
                    spouse_plan_age = 90
                    spouse_annual_contribution = 0
                    spouse_healthcare = 0
                    spouse_ss_age = 62
                    spouse_ss = 0
                    survivor_ss_strategy = "Higher benefit continues"
                    st.caption("Individual plan selected. Spouse / partner fields are hidden and will not affect the projection.")

                st.subheader("Assumptions")
                c1, c2, c3 = st.columns(3)
                growth_return = c1.slider(
                "Growth return",
                min_value=0.0,
                max_value=30.0,
                value=min(max(float(st.session_state.growth_return) * 100, 0.0), 30.0),
                step=0.25,
                format="%.2f%%",
                help=FIELD_HELP["growth_return"],
            ) / 100
                safe_return = c2.slider(
                "Bucket 1 safe return",
                min_value=0.0,
                max_value=10.0,
                value=min(max(float(st.session_state.safe_return) * 100, 0.0), 10.0),
                step=0.25,
                format="%.2f%%",
                help=FIELD_HELP["safe_return"],
            ) / 100
                inflation = c3.slider(
                "Inflation",
                min_value=0.0,
                max_value=10.0,
                value=min(max(float(st.session_state.inflation) * 100, 0.0), 10.0),
                step=0.25,
                format="%.2f%%",
                help=FIELD_HELP["inflation"],
            ) / 100

                st.subheader("Strategy")
                c1, c2 = st.columns(2)
                annual_conversion = c1.number_input("Annual Roth conversion to test", min_value=0, value=int(st.session_state.annual_conversion), step=5000, help=FIELD_HELP["annual_conversion"])
                bucket1_years = c2.number_input("Bucket 1 safety years of spending", min_value=0.0, max_value=10.0, value=float(st.session_state.bucket1_years), step=0.5, help="How many years of near-term retirement spending to keep in the safer Safety Bucket.")
                bucket2_years = float(st.session_state.get("bucket2_years", 5.0))
                c2.caption("Bucket 2 is the remaining long-term Growth Bucket. No extra bucket setup needed.")

                st.subheader("Federal Tax Estimate")
                st.caption("Phase 2: estimates federal ordinary income tax using IRS brackets, filing status, standard deduction, traditional withdrawals, Roth conversions, and taxable Social Security.")
                t1, t2 = st.columns(2)
                tax_year_options = sorted(TAX_TABLES.keys())
                tax_year = t1.selectbox(
                    "Tax year",
                    tax_year_options,
                    index=tax_year_options.index(get_tax_year()) if get_tax_year() in tax_year_options else len(tax_year_options) - 1,
                    help=FIELD_HELP["tax_year"],
                )
                filing_keys = list(FILING_STATUS_OPTIONS.keys())
                filing_status_label = t2.selectbox(
                    "Federal filing status",
                    [FILING_STATUS_OPTIONS[k] for k in filing_keys],
                    index=filing_keys.index(get_filing_status()) if get_filing_status() in filing_keys else 1,
                    help=FIELD_HELP["filing_status"],
                )
                filing_status = filing_keys[[FILING_STATUS_OPTIONS[k] for k in filing_keys].index(filing_status_label)]
                tax_settings_preview = get_tax_settings(tax_year, filing_status)
                st.info(f"Using {tax_year} federal brackets, {tax_settings_preview['label']}, and a standard deduction of {money(tax_settings_preview['standard_deduction'])}. Taxable Social Security is now estimated using provisional income thresholds. State taxes come in a later phase.")

                if st.session_state.enable_spending_change and int(st.session_state.spending_change_age or 0) > 0:
                    st.subheader("Planned Spending Change")
                    s1, s2 = st.columns(2)
                    s1.metric("Spending Change Age", int(st.session_state.spending_change_age))
                    s2.metric("New Monthly Spending", money(st.session_state.spending_change_monthly))
                    st.info("The projection uses this new spending amount starting at the selected age, then continues applying inflation.")

                st.subheader("Home & Housing Strategy")
                st.caption("Optional, but useful. Your home can affect retirement flexibility, mortgage cash flow, downsizing options, taxes, and relocation decisions.")

                c1, c2, c3 = st.columns(3)
                home_value = c1.number_input("Current home value", min_value=0, value=int(st.session_state.home_value), step=10000, help="Estimated current market value of your primary home.")
                mortgage_balance = c2.number_input("Remaining mortgage balance", min_value=0, value=int(st.session_state.mortgage_balance), step=5000, help="How much you still owe on the home.")
                monthly_mortgage = c3.number_input("Monthly mortgage payment", min_value=0, value=int(st.session_state.monthly_mortgage), step=100, help="Principal and interest payment. If taxes and insurance are escrowed, you can include the full payment here.")

                c1, c2, c3 = st.columns(3)
                annual_property_taxes_home = c1.number_input("Annual property taxes", min_value=0, value=int(st.session_state.annual_property_taxes_home), step=500, help="Estimated yearly property tax bill for the home.")
                mortgage_payoff_age = c2.number_input("Mortgage payoff age", min_value=0, max_value=110, value=int(st.session_state.mortgage_payoff_age), step=1, help="Age when the mortgage is expected to be paid off. Use 0 if unknown.")
                retirement_housing_plan = c3.selectbox(
                    "Retirement housing plan",
                    ["Stay in Current Home", "Downsize", "Relocate", "Snowbird", "Unsure"],
                    index=["Stay in Current Home", "Downsize", "Relocate", "Snowbird", "Unsure"].index(st.session_state.retirement_housing_plan) if st.session_state.retirement_housing_plan in ["Stay in Current Home", "Downsize", "Relocate", "Snowbird", "Unsure"] else 4,
                    help="How you expect housing to change in retirement."
                )

                st.info(f"Estimated home equity: {money(max(home_value - mortgage_balance, 0))}")

                save = st.form_submit_button("Save main answers", type="primary", use_container_width=True)

            if save:
                for k, v in {
                    "current_age": current_age, "retire_age": retire_age, "end_age": end_age,
                    "traditional": traditional, "roth": roth, "taxable": taxable, "cash": cash,
                    "annual_contribution": annual_contribution, "healthcare": healthcare,
                    "user_ss_age": user_ss_age, "user_ss": user_ss,
                    "has_spouse": has_spouse,
                    "spouse_age": spouse_age,
                    "spouse_retire_age": spouse_retire_age,
                    "spouse_plan_age": spouse_plan_age,
                    "spouse_annual_contribution": spouse_annual_contribution,
                    "spouse_healthcare": spouse_healthcare,
                    "spouse_ss_age": spouse_ss_age,
                    "spouse_ss": spouse_ss,
                    "survivor_ss_strategy": survivor_ss_strategy,
                    "growth_return": growth_return, "safe_return": safe_return, "inflation": inflation,
                    "annual_conversion": annual_conversion, "bucket1_years": bucket1_years, "bucket2_years": bucket2_years,
                    "tax_year": tax_year, "filing_status": filing_status,
                    "home_value": home_value,
                    "mortgage_balance": mortgage_balance,
                    "monthly_mortgage": monthly_mortgage,
                    "annual_property_taxes_home": annual_property_taxes_home,
                    "mortgage_payoff_age": mortgage_payoff_age,
                    "retirement_housing_plan": retirement_housing_plan,
                }.items():
                    st.session_state[k] = v
                st.success("Main answers saved.")

            render_premium_insight("Premium bucket strategy", df if can_run else None, "bucket")
            render_three_bucket_strategy(df if can_run else None)
            st.subheader("Compare 1 Bucket vs 2 Bucket")
            render_bucket_strategy_comparison_panel(df if can_run else None)

    st.divider()
    if st.button("Next: Spending Plan", type="primary", use_container_width=True, key="next_from_guided_to_budget"):
        go_to_page("Budget Builder")


if active_page == PAGE_NAMES[2]:
    render_page_shell("Spending Plan", "Estimate your retirement lifestyle costs using either a quick monthly number or a more detailed category-by-category budget.", "💳")
    render_guided_progress(2)
    page_help(
        "Budget Builder",
        "This page estimates how much money you need each year in retirement. You can use a simple flat monthly amount or enter a detailed monthly budget. Healthcare is handled separately so the app can model it more clearly."
    )

    st.markdown("""
    <div class="rb-next-box">
      <div class="rb-next-heading">Step 2: Choose your spending style</div>
      <div class="rb-muted">
        Pick the simple option if you know roughly what you want to spend each month.
        Pick detailed budget if you want to build the number category by category.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # This selector must stay OUTSIDE the form so the page refreshes immediately
    # when the user switches between Flat monthly number and Detailed monthly budget.
    # Use radio styling so it matches the Income Plan selector instead of the red segmented tabs.
    budget_mode = st.radio(
        "How do you want to enter household spending?",
        ["Flat monthly number", "Detailed monthly budget"],
        index=0 if st.session_state.budget_mode == "Flat monthly number" else 1,
        key="budget_mode_selector",
        horizontal=True,
        help="Choose flat monthly spending for a quick estimate, or detailed monthly budget to enter category-by-category spending."
    )

    if not budget_mode:
        budget_mode = st.session_state.budget_mode

    st.session_state.budget_mode = budget_mode

    if budget_mode == "Flat monthly number":
        st.success("Simple mode selected. Enter one monthly spending number and move on.")
    else:
        st.info("Detailed mode selected. Enter the categories you know. Use zero for anything that does not apply.")

    with st.form("budget_form"):
        if budget_mode == "Flat monthly number":
            flat_monthly_spending = st.number_input(
                "Total household spending per month before healthcare",
                min_value=0,
                value=int(st.session_state.flat_monthly_spending),
                step=500,
                help=FIELD_HELP["flat_monthly_spending"]
            )
            detailed_values = {}
        else:
            st.info("Detailed monthly budget is selected. The spending categories below are opened so you can enter each item.")

            flat_monthly_spending = st.session_state.flat_monthly_spending
            detailed_values = {}

            groups = [
                ("Housing", budget_keys[0:4]),
                ("Utilities & communications", budget_keys[4:11]),
                ("Food & household", budget_keys[11:14]),
                ("Cars & transportation", budget_keys[14:18]),
                ("Lifestyle", budget_keys[18:21]),
                ("Other", budget_keys[21:]),
            ]

            for group_name, keys in groups:
                with st.expander(group_name, expanded=True):
                    cols = st.columns(min(4, len(keys)))
                    for i, (key, label) in enumerate(keys):
                        with cols[i % len(cols)]:
                            detailed_values[key] = st.number_input(
                                f"{label} per month",
                                min_value=0,
                                value=int(st.session_state.get(key, 0) or 0),
                                step=50,
                                help=f"Enter your estimated monthly amount for {label.lower()}."
                            )

        st.subheader("Planned Spending Change")
        enable_spending_change = st.checkbox(
            "Change my spending at a certain age",
            value=bool(st.session_state.enable_spending_change),
            help="Use this if spending will change later in retirement, such as spending more early and less later."
        )

        if enable_spending_change:
            c1, c2 = st.columns(2)
            spending_change_age = c1.number_input(
                "Age when spending changes",
                min_value=0,
                max_value=110,
                value=int(st.session_state.spending_change_age),
                step=1,
                help="Enter the age when your new monthly spending should begin."
            )
            spending_change_monthly = c2.number_input(
                "New monthly spending amount",
                min_value=0,
                value=int(st.session_state.spending_change_monthly),
                step=500,
                help="Enter the new monthly spending amount before healthcare."
            )
            if spending_change_age > 0 and spending_change_monthly > 0:
                st.info(f"Spending will change to {money(spending_change_monthly)} per month starting at age {spending_change_age}.")
        else:
            spending_change_age = st.session_state.spending_change_age
            spending_change_monthly = st.session_state.spending_change_monthly

        survivor_spending = st.number_input(
            "Annual household spending after first spouse death, optional",
            min_value=0,
            value=int(st.session_state.survivor_spending),
            step=5000,
            help=FIELD_HELP["survivor_spending"]
        )

        save_budget = st.form_submit_button("Save budget", type="primary", use_container_width=True)

    if save_budget:
        st.session_state.budget_mode = budget_mode
        st.session_state.flat_monthly_spending = flat_monthly_spending
        st.session_state.survivor_spending = survivor_spending
        st.session_state.enable_spending_change = enable_spending_change
        st.session_state.spending_change_age = spending_change_age
        st.session_state.spending_change_monthly = spending_change_monthly

        for k, v in detailed_values.items():
            st.session_state[k] = v

        st.success("Budget saved. Next, add your income sources.")

    monthly = (
        st.session_state.flat_monthly_spending
        if st.session_state.budget_mode == "Flat monthly number"
        else detailed_monthly_budget_total()
    )

    c1, c2 = st.columns(2)
    c1.metric("Monthly Spending Before Healthcare", money(monthly))
    c2.metric("Annual Spending Before Healthcare", money(monthly * 12))

    if st.session_state.enable_spending_change and int(st.session_state.spending_change_age or 0) > 0:
        c3, c4 = st.columns(2)
        c3.metric("Spending Changes At Age", int(st.session_state.spending_change_age))
        c4.metric("New Monthly Spending", money(st.session_state.spending_change_monthly))

    st.divider()
    next_cols = st.columns([1, 1])
    with next_cols[0]:
        if st.button("Back: Start My Blueprint", use_container_width=True, key="back_from_budget_to_guided"):
            go_to_page("Guided Questions")
    with next_cols[1]:
        if st.button("Next: Income Plan", type="primary", use_container_width=True, key="next_from_budget_to_income"):
            go_to_page("Income Builder")


if active_page == PAGE_NAMES[3]:
    render_page_shell("Income Plan", "Add pensions, rental income, side income, annuities, or any other cash flows that reduce pressure on your portfolio.", "💼")
    render_guided_progress(3)
    page_help(
        "Income Builder",
        "This page captures income besides portfolio withdrawals, such as pensions, rental income, part-time work, consulting, annuities, or business income. More reliable income usually reduces portfolio withdrawal pressure."
    )
    st.write("Add pension, rental income, annuity, side gig, consulting, business income, dividends, royalties, or other retirement income.")

    income_mode = st.radio(
        "How do you want to enter other income?",
        ["Simple income", "Advanced income builder"],
        index=0 if st.session_state.income_mode == "Simple income" else 1,
    )
    st.session_state.income_mode = income_mode

    if income_mode == "Simple income":
        with st.form("simple_income_form"):
            c1, c2, c3 = st.columns(3)
            simple_income = c1.number_input("Other annual income before taxes", min_value=0, value=st.session_state.simple_income, step=1000, help=FIELD_HELP["simple_income"])
            simple_income_start = c2.number_input("Start age", min_value=0, max_value=110, value=st.session_state.simple_income_start, help=FIELD_HELP["simple_income_start"])
            simple_income_end = c3.number_input("End age, use 0 if lifelong", min_value=0, max_value=120, value=st.session_state.simple_income_end, help=FIELD_HELP["simple_income_end"])
            c1, c2 = st.columns(2)
            simple_income_inflation = c1.checkbox("Inflation adjusted?", value=st.session_state.simple_income_inflation, help=FIELD_HELP["simple_income_inflation"])
            simple_income_reliability = c2.selectbox("Reliability", ["Guaranteed", "Variable"], index=0 if st.session_state.simple_income_reliability == "Guaranteed" else 1, help=FIELD_HELP["simple_income_reliability"])
            save_income = st.form_submit_button("Save simple income", type="primary", use_container_width=True)
        if save_income:
            st.session_state.simple_income = simple_income
            st.session_state.simple_income_start = simple_income_start
            st.session_state.simple_income_end = simple_income_end
            st.session_state.simple_income_inflation = simple_income_inflation
            st.session_state.simple_income_reliability = simple_income_reliability
            st.success("Income saved. Next, review your Retirement Dashboard.")
    else:
        edited = st.data_editor(
            st.session_state.income_sources_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Name": st.column_config.TextColumn("Income name"),
                "Annual Amount": st.column_config.NumberColumn("Annual amount", min_value=0, step=1000),
                "Start Age": st.column_config.NumberColumn("Start age", min_value=0, max_value=110, step=1),
                "End Age": st.column_config.NumberColumn("End age", min_value=0, max_value=120, step=1, help="Use 0 if lifelong"),
                "Inflation Adjusted": st.column_config.CheckboxColumn("Inflation adjusted?"),
                "Taxable": st.column_config.CheckboxColumn("Taxable?"),
                "Owner": st.column_config.SelectboxColumn("Owner", options=["User", "Spouse", "Joint"]),
                "Reliability": st.column_config.SelectboxColumn("Reliability", options=["Guaranteed", "Variable"]),
                "Continues After First Death": st.column_config.CheckboxColumn("Continues after first death?"),
            },
            key="income_editor",
        )
        if st.button("Save advanced income sources"):
            st.session_state.income_sources_df = edited
            st.success("Advanced income sources saved.")

    st.divider()
    next_cols = st.columns([1, 1])
    with next_cols[0]:
        if st.button("Back: Spending Plan", use_container_width=True, key="back_from_income_to_budget"):
            go_to_page("Budget Builder")
    with next_cols[1]:
        if st.button("Next: Review Inputs", type="primary", use_container_width=True, key="next_from_income_to_review"):
            go_to_page("Review Answers")


if active_page == PAGE_NAMES[4]:
    render_page_shell("Household Plan", "Household setup now lives inside Start My Blueprint.", "👥")
    st.info("Household planning is now included directly on the Start My Blueprint page. Use the spouse / partner checkbox there to include or hide household fields.")
    if st.button("Go to Start My Blueprint", use_container_width=True, key="go_guided_from_household_removed"):
        go_to_page("Guided Questions")

if active_page == PAGE_NAMES[5]:
    render_page_shell("Review Inputs", "See a clean summary of your current inputs before running deeper analysis or sharing the results.", "📝")
    render_guided_progress(4)
    page_help(
        "Review Answers",
        "This page summarizes your saved inputs before running the plan. Use it to catch missing or incorrect assumptions before trusting the results."
    )
    missing = required_missing()
    if missing:
        st.warning("Still missing: " + ", ".join(missing))
    else:
        st.success("Required answers are complete.")

    review = pd.DataFrame([
        ["Current age", st.session_state.current_age],
        ["Retirement age", st.session_state.retire_age],
        ["Plan-through age", st.session_state.end_age],
        ["Traditional", money(st.session_state.traditional)],
        ["Roth", money(st.session_state.roth)],
        ["Taxable", money(st.session_state.taxable)],
        ["Bucket 1 / Cash", money(st.session_state.cash)],
        ["Annual contributions", money(st.session_state.annual_contribution)],
        ["Budget mode", st.session_state.budget_mode],
        ["Annual spending before healthcare", money(annual_household_spending())],
        ["Spending change enabled", "Yes" if st.session_state.enable_spending_change else "No"],
        ["Spending change age", st.session_state.spending_change_age if st.session_state.enable_spending_change else "N/A"],
        ["New monthly spending", money(st.session_state.spending_change_monthly) if st.session_state.enable_spending_change else "N/A"],
        ["Income mode", st.session_state.income_mode],
        ["Simple other income", money(st.session_state.simple_income) if st.session_state.income_mode == "Simple income" else "Advanced table"],
        ["Plan type", "Couple / household plan" if st.session_state.has_spouse else "Individual plan"],
        ["Spouse age", st.session_state.spouse_age if st.session_state.has_spouse else "N/A"],
        ["Spouse retirement age", st.session_state.spouse_retire_age if st.session_state.has_spouse else "N/A"],
        ["Your SS", money(st.session_state.user_ss)],
        ["Spouse SS", money(st.session_state.spouse_ss) if st.session_state.has_spouse else "N/A"],
        ["Growth return", pct(st.session_state.growth_return)],
        ["Inflation", pct(st.session_state.inflation)],
        ["Home value", money(st.session_state.home_value)],
        ["Mortgage balance", money(st.session_state.mortgage_balance)],
        ["Estimated home equity", money(home_equity())],
        ["Monthly mortgage payment", money(st.session_state.monthly_mortgage)],
        ["Annual property taxes", money(st.session_state.annual_property_taxes_home)],
        ["Mortgage payoff age", st.session_state.mortgage_payoff_age if st.session_state.mortgage_payoff_age else "Unknown"],
        ["Housing plan", st.session_state.retirement_housing_plan],
    ], columns=["Input", "Answer"])
    st.dataframe(review, use_container_width=True)

# can_run and df are initialized safely before page rendering above.


def render_dashboard_close_to_mock(df, rtv_score, rtv_label, rtv_reasons):
    planning_age = int(st.session_state.get("end_age", 90) or 90)
    ending = float(df["End Total"].iloc[-1] or 0)
    income_cov = float(df["Income Coverage Ratio"].mean() or 0)
    max_wr = float(df["Withdrawal Rate"].max() or 0)
    chosen_age = int(st.session_state.get("retire_age", 0) or 0)

    unmet_need = float(df["Unmet Need"].sum() or 0)
    if unmet_need > 0 or ending <= 0:
        retire_status = "Not Yet"
        retire_status_note = "The current target age may need changes."
    elif rtv_score >= 80:
        retire_status = "Looks Good"
        retire_status_note = "Your target age appears realistic."
    else:
        retire_status = "Maybe"
        retire_status_note = "The plan may work, but needs review."

    avg_gap = float(df["Portfolio Need"].mean() if "Portfolio Need" in df.columns else 0)
    if avg_gap <= 0 and "Total Spending" in df.columns and "Total Non-Portfolio Income" in df.columns:
        avg_gap = float((df["Total Spending"] - df["Total Non-Portfolio Income"]).clip(lower=0).mean())
    monthly_gap = money(max(avg_gap, 0) / 12)

    # Money-left card explanation: show the age when money is projected to run out.
    runout_age = None
    try:
        if "End Total" in df.columns:
            runout_rows = df[df["End Total"] <= 0]
            if not runout_rows.empty:
                if "Age" in df.columns:
                    runout_age = int(runout_rows["Age"].iloc[0])
                else:
                    runout_age = planning_age
    except Exception:
        runout_age = None

    if runout_age is not None:
        money_left_pill = f"Runs out at {runout_age}"
        money_left_note = f"Projection reaches $0 around age {runout_age}."
        money_left_class = "rb-kpi-value"
    else:
        money_left_pill = "Projected"
        money_left_note = "Estimated balance at the end of the plan."
        money_left_class = "rb-kpi-value green"

    # Top KPI card row removed per design preference.

    # Next step and chart
    try:
        action_rows = build_action_plan_rows(df, rtv_score)
        if len(action_rows) > 1:
            top_action, top_why, impact, new_score = action_rows[1]
        else:
            top_action, top_why, impact, new_score = "Review your Action Plan", "See the highest-impact ways to improve your retirement outlook.", "+0", str(rtv_score)
    except Exception:
        top_action, top_why, impact, new_score = "Review your Action Plan", "See the highest-impact ways to improve your retirement outlook.", "+0", str(rtv_score)

    left, right = st.columns([1, 1.75])
    with left:
        st.markdown(f"""
        <div class="rb-next-panel-v2">
          <div class="rb-next-title-v2">Next Best Step</div>
          <div style="font-weight:900;color:#0F172A;font-size:1.02rem;margin-bottom:8px;">{top_action}</div>
          <div style="color:#64748B;line-height:1.45;margin-bottom:16px;">{top_why}</div>
          <div class="rb-kpi-pill">Potential score impact: {impact}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("See Action Plan", key="mock_see_action_plan", use_container_width=True):
            go_to_page("Recommendations")
        if st.button("Why this matters", key="mock_why_matters", use_container_width=True):
            st.session_state.show_mock_why = not st.session_state.get("show_mock_why", False)
        if st.session_state.get("show_mock_why"):
            st.info("This recommendation is based on the highest-impact lever the current blueprint found. It is educational and not financial advice.")
    with right:
        st.markdown("""
        <div class="rb-chart-card-v2">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
            <div>
              <div style="font-weight:900;color:#0F172A;font-size:1.05rem;">Projected Portfolio Value</div>
              <div style="color:#64748B;font-size:.9rem;">Year-by-year projected portfolio trend.</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.pyplot(plot_portfolio_area_chart(df), use_container_width=True)


def calculate_basic_blueprint_snapshot():
    current_age = int(st.session_state.get("current_age", 0) or 0)
    retire_age = int(st.session_state.get("retire_age", 0) or 0)
    end_age = int(st.session_state.get("end_age", 90) or 90)
    starting_savings = float(st.session_state.get("traditional", 0) or 0) + float(st.session_state.get("roth", 0) or 0) + float(st.session_state.get("taxable", 0) or 0) + float(st.session_state.get("cash", 0) or 0)
    annual_contribution = float(st.session_state.get("annual_contribution", 0) or 0)
    monthly_spending = float(st.session_state.get("basic_blueprint_monthly_spending", 0) or st.session_state.get("monthly_spending", 0) or 0)
    annual_spending = monthly_spending * 12
    ss_age = int(st.session_state.get("user_ss_age", 62) or 62)
    ss_annual = float(st.session_state.get("user_ss", 0) or 0)
    growth_return = float(st.session_state.get("growth_return", 0.07) or 0.07)
    inflation = float(st.session_state.get("inflation", 0.03) or 0.03)

    years_to_retire = max(retire_age - current_age, 0)
    balance_at_retirement = starting_savings
    for _ in range(years_to_retire):
        balance_at_retirement = balance_at_retirement * (1 + growth_return) + annual_contribution

    balance = balance_at_retirement
    first_year_spending = annual_spending * ((1 + inflation) ** max(retire_age - current_age, 0))
    first_year_ss = ss_annual * ((1 + inflation) ** max(retire_age - current_age, 0)) if retire_age >= ss_age else 0
    first_year_gap = max(first_year_spending - first_year_ss, 0)
    depletion_age = None
    for age in range(retire_age, end_age + 1):
        years_from_today = max(age - current_age, 0)
        spending = annual_spending * ((1 + inflation) ** years_from_today)
        income = ss_annual * ((1 + inflation) ** years_from_today) if age >= ss_age else 0
        gap = max(spending - income, 0)
        balance = balance * (1 + growth_return) - gap
        if balance <= 0 and depletion_age is None:
            depletion_age = age
            balance = 0
            break

    money_left = max(balance, 0)
    if current_age <= 0 or retire_age <= 0 or annual_spending <= 0:
        status = "Needs Inputs"
        status_note = "Enter age, retirement age, and spending to see your basic result."
        score = "Incomplete"
    elif depletion_age:
        status = "Not Yet"
        status_note = f"Basic estimate shows savings could run out around age {depletion_age}."
        score = "Needs Work"
    elif money_left > balance_at_retirement * 0.5:
        status = "Looks Good"
        status_note = "Basic estimate shows money lasting through the plan."
        score = "Strong"
    else:
        status = "Maybe"
        status_note = "Basic estimate works, but the cushion may need review."
        score = "Fair"

    return {
        "retire_age": retire_age, "end_age": end_age, "money_left": money_left,
        "monthly_gap": first_year_gap / 12, "status": status,
        "status_note": status_note, "score": score,
    }



def render_blueprint_dashboard_mockup_section(df, rtv_score, rtv_label):
    """Premium-looking dashboard summary inspired by the requested mockup."""

    # Local CSS for the premium dashboard mockup. This keeps the section styled even
    # when the dashboard is rendered before other page-specific CSS blocks.
    st.markdown("""
    <style>
/* Premium Blueprint Dashboard mockup section */
.rb-blueprint-mock-hero {
    display:flex;
    gap:14px;
    align-items:flex-start;
    border:1px solid #C7E3FF;
    border-radius:22px;
    background:linear-gradient(135deg,#F8FBFF 0%,#FFFFFF 62%,#ECFEFF 100%);
    padding:20px 22px;
    margin:8px 0 18px 0;
    box-shadow:0 12px 30px rgba(15,23,42,.055);
}
.rb-blueprint-mock-icon {
    width:48px;
    height:48px;
    border-radius:14px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#E0F2FE;
    font-size:1.45rem;
    flex:0 0 auto;
}
.rb-blueprint-mock-kicker-pill {
    display:inline-flex;
    align-items:center;
    border-radius:999px;
    padding:4px 10px;
    background:#DBEAFE;
    color:#1D4ED8;
    font-size:.76rem;
    font-weight:900;
    margin-bottom:8px;
}
.rb-blueprint-mock-title {
    color:#0F172A;
    font-size:1.45rem;
    font-weight:950;
    letter-spacing:-.03em;
    margin-bottom:4px;
}
.rb-blueprint-mock-sub {
    color:#64748B;
    line-height:1.45;
    max-width:850px;
}
.rb-score-banner {
    display:flex;
    gap:18px;
    align-items:center;
    border:1px solid #BBF7D0;
    border-radius:22px;
    background:linear-gradient(135deg,#ECFDF5 0%,#F0FDFA 100%);
    padding:22px 24px;
    margin:18px 0 20px 0;
    box-shadow:0 14px 30px rgba(16,185,129,.10);
}
.rb-score-badge {
    width:74px;
    height:74px;
    border-radius:18px;
    background:linear-gradient(135deg,#22C55E,#059669);
    color:#FFFFFF;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    box-shadow:0 14px 24px rgba(5,150,105,.25);
    flex:0 0 auto;
}
.rb-score-badge-num { font-size:1.8rem; font-weight:950; line-height:1; }
.rb-score-badge-label { font-size:.55rem; font-weight:900; letter-spacing:.05em; margin-top:4px; }
.rb-score-banner-pill {
    display:inline-flex;
    border-radius:999px;
    padding:4px 10px;
    background:#DCFCE7;
    color:#15803D;
    font-size:.75rem;
    font-weight:900;
    margin-bottom:7px;
}
.rb-score-banner-title {
    color:#0F172A;
    font-size:1.25rem;
    font-weight:950;
    letter-spacing:-.02em;
    margin-bottom:4px;
}
.rb-score-banner-copy { color:#475569; line-height:1.5; }
.rb-dashboard-section-kicker {
    color:#2563EB;
    font-size:.78rem;
    font-weight:950;
    text-transform:uppercase;
    letter-spacing:.08em;
    margin:20px 0 10px 3px;
}
.rb-health-timeline-grid {
    display:grid;
    grid-template-columns: 1.08fr .92fr;
    gap:18px;
    margin:18px 0 20px 0;
}
.rb-panel-card {
    background:#FFFFFF;
    border:1px solid #E5E7EB;
    border-radius:22px;
    padding:20px 22px;
    box-shadow:0 10px 26px rgba(15,23,42,.055);
}
.rb-panel-title {
    color:#0F172A;
    font-size:1.15rem;
    font-weight:950;
    margin-bottom:4px;
}
.rb-panel-sub { color:#64748B; font-size:.9rem; margin-bottom:16px; }
.rb-health-row {
    display:grid;
    grid-template-columns: 42px 1fr auto;
    gap:12px;
    align-items:center;
    padding:12px 0;
    border-top:1px solid #F1F5F9;
}
.rb-health-row:first-of-type { border-top:0; }
.rb-health-icon {
    width:34px;
    height:34px;
    border-radius:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#F8FAFC;
    font-size:1rem;
}
.rb-health-title { color:#0F172A; font-weight:900; }
.rb-health-copy { color:#64748B; font-size:.86rem; line-height:1.35; }
.rb-health-pill {
    border-radius:999px;
    padding:5px 10px;
    font-weight:900;
    font-size:.72rem;
    white-space:nowrap;
}
.rb-pill-green { background:#DCFCE7; color:#15803D; }
.rb-pill-yellow { background:#FEF3C7; color:#B45309; }
.rb-pill-red { background:#FEE2E2; color:#B91C1C; }
.rb-pill-blue { background:#DBEAFE; color:#1D4ED8; }
.rb-timeline-row {
    display:grid;
    grid-template-columns: 52px 1fr;
    gap:12px;
    padding:12px 0;
}
.rb-timeline-age { color:#2563EB; font-weight:950; }
.rb-timeline-title { color:#0F172A; font-weight:900; }
.rb-timeline-copy { color:#64748B; font-size:.86rem; line-height:1.35; }
@media (max-width: 900px) {
    .rb-score-banner { align-items:flex-start; }
    .rb-health-timeline-grid { grid-template-columns:1fr; }
}
    </style>
    """, unsafe_allow_html=True)
    current_age = int(st.session_state.get("current_age", 0) or 0)
    retire_age = int(st.session_state.get("retire_age", 0) or 0)
    end_age = int(st.session_state.get("end_age", 90) or 90)
    ss_age = int(st.session_state.get("user_ss_age", 62) or 62)
    rmd_age = int(get_rmd_start_age())
    monthly_spending = float(annual_household_spending() or 0) / 12
    ending_balance = float(df["End Total"].iloc[-1] or 0) if "End Total" in df.columns and not df.empty else 0.0
    unmet_need = float(df["Unmet Need"].sum() or 0) if "Unmet Need" in df.columns else 0.0
    income_coverage = float(df["Income Coverage Ratio"].mean() or 0) if "Income Coverage Ratio" in df.columns else 0.0
    max_withdrawal_rate = float(df["Withdrawal Rate"].max() or 0) if "Withdrawal Rate" in df.columns else 0.0

    avg_gap = 0.0
    if "Portfolio Need" in df.columns:
        avg_gap = float(df["Portfolio Need"].mean() or 0)
    elif "Total Spending" in df.columns and "Total Non-Portfolio Income" in df.columns:
        avg_gap = float((df["Total Spending"] - df["Total Non-Portfolio Income"]).clip(lower=0).mean() or 0)
    monthly_gap = max(avg_gap, 0) / 12

    if rtv_score >= 80 and unmet_need <= 0 and ending_balance > 0:
        score_pill = "✓ Strong"
        score_title = f"Yes — retiring at {retire_age} looks workable."
        score_copy = f"Your plan appears to last through age {end_age} with a solid cushion. A few small improvements could make it even more comfortable."
        status_short = "Yes"
        status_pill = "Based on your plan"
        longevity_value = f"To age {end_age}+"
        longevity_pill = "Lasts the whole plan"
    elif rtv_score >= 65 and unmet_need <= 0:
        score_pill = "⚠ Close"
        score_title = f"Retiring at {retire_age} may work, but review the cushion."
        score_copy = "Your plan has some positive signs, but the margin is thinner. Spending, Social Security timing, or retirement age may deserve another test."
        status_short = "Maybe"
        status_pill = "Needs review"
        longevity_value = f"To age {end_age}"
        longevity_pill = "Watch the cushion"
    else:
        score_pill = "⚠ Needs work"
        score_title = f"Retiring at {retire_age} needs more adjustment."
        score_copy = "The current blueprint may need lower spending, more income, more savings, or a later retirement age before it looks comfortable."
        status_short = "Not yet"
        status_pill = "Needs changes"
        longevity_value = "At risk"
        longevity_pill = "Runs short risk"

    if income_coverage >= 0.70:
        income_label, income_class = "Strong", "rb-pill-green"
    elif income_coverage >= 0.40:
        income_label, income_class = "Moderate", "rb-pill-yellow"
    else:
        income_label, income_class = "Low", "rb-pill-red"

    if max_withdrawal_rate <= 0.04:
        spending_label, spending_class = "Healthy", "rb-pill-green"
    elif max_withdrawal_rate <= 0.06:
        spending_label, spending_class = "Watch", "rb-pill-yellow"
    else:
        spending_label, spending_class = "High", "rb-pill-red"

    healthcare_gap_years = max(0, min(65, end_age) - retire_age) if retire_age else 0
    if healthcare_gap_years <= 0:
        healthcare_label, healthcare_class = "Covered", "rb-pill-green"
    elif healthcare_gap_years <= 5:
        healthcare_label, healthcare_class = "Worth a look", "rb-pill-yellow"
    else:
        healthcare_label, healthcare_class = "High gap", "rb-pill-red"

    tax_pressure = 0.0
    if "Estimated Federal Tax" in df.columns and "Total Spending" in df.columns:
        tax_pressure = float(df["Estimated Federal Tax"].sum() or 0) / max(float(df["Total Spending"].sum() or 0), 1)
    elif "Estimated Tax" in df.columns and "Total Spending" in df.columns:
        tax_pressure = float(df["Estimated Tax"].sum() or 0) / max(float(df["Total Spending"].sum() or 0), 1)
    if tax_pressure >= 0.18:
        tax_label, tax_class = "Review", "rb-pill-yellow"
    elif tax_pressure > 0:
        tax_label, tax_class = "Manageable", "rb-pill-green"
    else:
        tax_label, tax_class = "Simplified", "rb-pill-blue"

    if max_withdrawal_rate > 0.06 or rtv_score < 70:
        market_label, market_class = "High risk", "rb-pill-red"
    elif max_withdrawal_rate > 0.045:
        market_label, market_class = "Moderate", "rb-pill-yellow"
    else:
        market_label, market_class = "Lower", "rb-pill-green"

    summary_text = (
        f"You told us you want to retire at <b>{retire_age}</b> and spend about <b>{money(monthly_spending)}/month</b>. "
        f"After Social Security and other income, your savings may need to cover roughly <b>{money(monthly_gap)}/month</b>. "
        f"The good news: your projected balance at age <b>{end_age}</b> is about <b>{compact_money(ending_balance)}</b>. "
        "The main thing to check next is what happens if the market has a few bad years right after you retire."
    )

    st.markdown(f"""
    <div class="rb-blueprint-mock-hero">
      <div class="rb-blueprint-mock-icon">📊</div>
      <div>
        <div class="rb-blueprint-mock-kicker-pill">Planner Section</div>
        <div class="rb-blueprint-mock-title">Blueprint Dashboard</div>
        <div class="rb-blueprint-mock-sub">Review your blueprint outcome, year-by-year trends, and the key retirement metrics that show whether your plan is on track.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("💬 What this page means: Dashboard", expanded=False):
        st.write("This page turns the retirement math into plain English. It shows whether your plan appears workable, which numbers matter most, and what to review next.")

    st.caption("Tax estimates now include taxable Social Security when provisional income exceeds IRS thresholds. Roth and cash withdrawals are modeled as tax-free; taxable brokerage is still simplified until the capital-gains phase.")

    st.markdown(f"""
    <div class="rb-score-banner">
      <div class="rb-score-badge"><div class="rb-score-badge-num">{int(rtv_score)}</div><div class="rb-score-badge-label">OUT OF 100</div></div>
      <div>
        <div class="rb-score-banner-pill">{xml_escape(score_pill)}</div>
        <div class="rb-score-banner-title">{xml_escape(score_title)}</div>
        <div class="rb-score-banner-copy">{xml_escape(score_copy)}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="rb-dashboard-section-kicker">The 4 numbers that matter most</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="rb-card-grid">
      <div class="rb-card">
        <div class="rb-card-label">Can I retire at {retire_age}?</div>
        <div class="rb-card-value" style="color:#15803D;">{xml_escape(status_short)}</div>
        <div class="rb-kpi-pill">{xml_escape(status_pill)}</div>
        <div class="rb-card-note">Your savings and income vs. when you want to stop working.</div>
      </div>
      <div class="rb-card">
        <div class="rb-card-label">Will my money last?</div>
        <div class="rb-card-value" style="color:#15803D;">{xml_escape(longevity_value)}</div>
        <div class="rb-kpi-pill">{xml_escape(longevity_pill)}</div>
        <div class="rb-card-note">Whether your money outlasts your plan, or runs out early.</div>
      </div>
      <div class="rb-card">
        <div class="rb-card-label">Money Left at {end_age}</div>
        <div class="rb-card-value" style="color:#15803D;">{money(ending_balance)}</div>
        <div class="rb-kpi-pill">Projected</div>
        <div class="rb-card-note">Estimated balance at the end of the plan.</div>
      </div>
      <div class="rb-card">
        <div class="rb-card-label">Monthly Gap From Savings</div>
        <div class="rb-card-value">{money(monthly_gap)}</div>
        <div class="rb-kpi-pill">Savings need</div>
        <div class="rb-card-note">Estimated monthly amount that needs to come from savings.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="rb-dashboard-explain rb-dashboard-explain-top">
      <div class="rb-explain-title">💬 What this means, in plain English</div>
      <div class="rb-explain-copy">{summary_text}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="rb-health-timeline-grid">
      <div class="rb-panel-card">
        <div class="rb-panel-title">Your Retirement Health Check</div>
        <div class="rb-panel-sub">Quick checks on the parts of your plan that matter most.</div>
        <div class="rb-health-row"><div class="rb-health-icon">💰</div><div><div class="rb-health-title">Income coverage</div><div class="rb-health-copy">How much of your spending is covered by Social Security & pensions</div></div><div class="rb-health-pill {income_class}">{income_label}</div></div>
        <div class="rb-health-row"><div class="rb-health-icon">📉</div><div><div class="rb-health-title">Spending rate</div><div class="rb-health-copy">How fast you’re drawing down savings — lower is safer</div></div><div class="rb-health-pill {spending_class}">{spending_label}</div></div>
        <div class="rb-health-row"><div class="rb-health-icon">🏥</div><div><div class="rb-health-title">Healthcare gap</div><div class="rb-health-copy">Covering health costs before Medicare starts at 65</div></div><div class="rb-health-pill {healthcare_class}">{healthcare_label}</div></div>
        <div class="rb-health-row"><div class="rb-health-icon">🧾</div><div><div class="rb-health-title">Tax pressure</div><div class="rb-health-copy">How much of your withdrawals may go to taxes</div></div><div class="rb-health-pill {tax_class}">{tax_label}</div></div>
        <div class="rb-health-row"><div class="rb-health-icon">📊</div><div><div class="rb-health-title">Market timing risk</div><div class="rb-health-copy">Risk of a bad market right when you retire</div></div><div class="rb-health-pill {market_class}">{market_label}</div></div>
      </div>
      <div class="rb-panel-card">
        <div class="rb-panel-title">Your Money Timeline</div>
        <div class="rb-panel-sub">The key moments ahead in your plan.</div>
        <div class="rb-timeline-row"><div class="rb-timeline-age">Age {current_age}</div><div><div class="rb-timeline-title">Where you are now</div><div class="rb-timeline-copy">Still saving</div></div></div>
        <div class="rb-timeline-row"><div class="rb-timeline-age">{retire_age}</div><div><div class="rb-timeline-title">You retire</div><div class="rb-timeline-copy">Start drawing from savings; healthcare costs begin</div></div></div>
        <div class="rb-timeline-row"><div class="rb-timeline-age">{ss_age}</div><div><div class="rb-timeline-title">Social Security starts</div><div class="rb-timeline-copy">Your monthly gap shrinks as Social Security income begins</div></div></div>
        <div class="rb-timeline-row"><div class="rb-timeline-age">{rmd_age}</div><div><div class="rb-timeline-title">Required withdrawals begin</div><div class="rb-timeline-copy">The IRS requires minimum withdrawals from many pre-tax retirement accounts</div></div></div>
        <div class="rb-timeline-row"><div class="rb-timeline-age">{end_age}</div><div><div class="rb-timeline-title">End of plan</div><div class="rb-timeline-copy">~{compact_money(ending_balance)} projected to remain</div></div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_basic_blueprint_dashboard():
    snap = calculate_basic_blueprint_snapshot()
    st.markdown("""
    <div class="rb-insight-card">
      <div class="rb-insight-kicker">Basic Blueprint</div>
      <div class="rb-insight-title">Your starter retirement snapshot is ready</div>
      <div class="rb-insight-copy">
        This is a simplified estimate based on your Quick Blueprint inputs. Upgrade to Detailed Blueprint
        for account-level planning, taxes, Roth conversions, detailed spending, home equity, and bucket strategy.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="rb-card-grid">
      <div class="rb-card">
        <div class="rb-card-top"><div class="rb-card-label">Basic Blueprint Score</div><div class="rb-icon">☆</div></div>
        <div class="rb-card-value">{snap['score']}</div>
        <div class="rb-card-note">Starter score based on quick inputs.</div>
      </div>
      <div class="rb-card">
        <div class="rb-card-top"><div class="rb-card-label">Can I Retire at {snap['retire_age']}?</div><div class="rb-icon">✓</div></div>
        <div class="rb-card-value">{snap['status']}</div>
        <div class="rb-card-note">{snap['status_note']}</div>
      </div>
      <div class="rb-card">
        <div class="rb-card-top"><div class="rb-card-label">Money Left at Age {snap['end_age']}</div><div class="rb-icon">$</div></div>
        <div class="rb-card-value">{compact_money(snap['money_left'])}</div>
        <div class="rb-card-note">Basic estimate after retirement spending and Social Security.</div>
      </div>
      <div class="rb-card">
        <div class="rb-card-top"><div class="rb-card-label">Monthly Gap From Savings</div><div class="rb-icon">↗</div></div>
        <div class="rb-card-value">{compact_money(snap['monthly_gap'])}</div>
        <div class="rb-card-note">Estimated first-year monthly amount needed from savings.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Free-user value: give a small useful takeaway without unlocking the full optimization engine.
    if snap["status"] == "Looks Good":
        takeaway = "Your quick numbers suggest your target retirement age may be realistic, but the free version is still a simplified estimate."
        idea_1 = "Stress-test the plan by asking: what happens if returns are lower than expected?"
        idea_2 = "Check whether your spending estimate includes healthcare, taxes, travel, and home repairs."
    elif snap["status"] == "Maybe":
        takeaway = "Your quick numbers show the plan may work, but the cushion looks thinner and deserves a closer review."
        idea_1 = "Try lowering estimated monthly spending or delaying retirement by 1 year."
        idea_2 = "Review Social Security timing because delaying benefits may reduce pressure on savings."
    elif snap["status"] == "Not Yet":
        takeaway = "Your quick numbers suggest the current retirement age may be too aggressive without changing savings, spending, or timing."
        idea_1 = "Try delaying retirement by 1–2 years to give savings more time to grow."
        idea_2 = "Try reducing monthly retirement spending to lower the amount needed from savings."
    else:
        takeaway = "Your Basic Blueprint needs a few more starter inputs before it can give a useful retirement snapshot."
        idea_1 = "Enter your current age, retirement age, savings, and monthly spending."
        idea_2 = "Use reasonable estimates first. You can refine the details later."

    st.markdown(f"""
    <div class="rb-insight-card">
      <div class="rb-insight-kicker">Basic Blueprint Takeaway</div>
      <div class="rb-insight-title">What your quick numbers are telling you</div>
      <div class="rb-insight-copy">{takeaway}</div>
    </div>
    """, unsafe_allow_html=True)

    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"""
        <div class="rb-next-box">
          <div class="rb-next-heading">Thing to try #1</div>
          <div class="rb-muted">{idea_1}</div>
        </div>
        """, unsafe_allow_html=True)
    with t2:
        st.markdown(f"""
        <div class="rb-next-box">
          <div class="rb-next-heading">Thing to try #2</div>
          <div class="rb-muted">{idea_2}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="rb-next-box">
      <div class="rb-next-heading">Want a more accurate answer?</div>
      <div class="rb-muted">
        Premium can calculate the impact instead of making you guess. Detailed Blueprint adds account-by-account taxes,
        detailed spending categories, Roth conversion impact, home equity, bucket strategy, age optimization, and saved comparisons.
      </div>
    </div>
    """, unsafe_allow_html=True)

    is_premium_user = bool(st.session_state.get("is_premium_user", False))

    if is_premium_user:
        u1, u2, u3 = st.columns(3)
        with u1:
            if st.button("Open Detailed Blueprint", type="primary", use_container_width=True, key="basic_unlock_detailed"):
                go_to_page("Guided Questions")
        with u2:
            if st.button("Run Age Optimizer", use_container_width=True, key="basic_age_optimizer"):
                go_to_page("Retirement Age Optimizer")
        with u3:
            if st.button("Save This Blueprint", use_container_width=True, key="basic_save_blueprint"):
                go_to_page("Saved Scenarios")
    else:
        st.markdown("""
        <div class="rb-insight-card">
          <div class="rb-insight-kicker">Premium Preview</div>
          <div class="rb-insight-title">Unlock the full retirement planning tools</div>
          <div class="rb-insight-copy">
            Premium unlocks Detailed Blueprint, Age Optimizer, saved blueprint comparisons,
            tax-aware withdrawal planning, Roth conversion testing, and the full Blueprint Report.
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Upgrade to Get a Detailed Blueprint", type="primary", use_container_width=True, key="basic_upgrade_prompt"):
            st.session_state.show_premium_prompt = True
            st.info("Pricing is temporarily hidden while we finalize the app. Premium tools are still available in testing mode.")

    st.caption("Basic Blueprint is educational and simplified. It is not financial, tax, legal, insurance, or investment advice.")

    st.divider()
    nav_cols = st.columns([1, 1])
    with nav_cols[0]:
        if st.button("Back: Income Plan", use_container_width=True, key="review_inputs_back_income"):
            go_to_page("Income Builder")
    with nav_cols[1]:
        if st.button("Next: Retirement Dashboard", type="primary", use_container_width=True, key="review_inputs_to_retirement_dashboard"):
            go_to_page("Retirement Dashboard")
if active_page == PAGE_NAMES[6]:
    render_guided_progress(5)
    if st.session_state.get("dashboard_focus"):
        focus_label = st.session_state.get("dashboard_focus")
        st.info(f"Opened from Premium Retirement Tools: **{focus_label}**. Use the premium tool buttons below or open advanced dashboard details.")
        if st.button("Clear premium tool note", key="clear_dashboard_focus"):
            st.session_state.dashboard_focus = ""
            st.rerun()

    if not can_run:
        if st.session_state.get("quick_blueprint_saved"):
            st.markdown('<div class="rb-saas-title">Basic Retirement Dashboard</div><div class="rb-saas-sub">Your simplified retirement snapshot based on Quick Blueprint inputs.</div>', unsafe_allow_html=True)
            render_basic_blueprint_dashboard()
        else:
            st.markdown('<div class="rb-saas-title">Retirement Dashboard</div><div class="rb-saas-sub">Start with Quick Blueprint to unlock your starter retirement snapshot.</div>', unsafe_allow_html=True)
            st.info("Start with Quick Blueprint first.")
            if st.button("Go to Start My Blueprint", key="dashboard_go_start", use_container_width=True):
                go_to_page("Guided Questions")
    else:
        ending = df["End Total"].iloc[-1]
        depleted = df["Unmet Need"].sum() > 0 or ending <= 0 or df["Age"].iloc[-1] < st.session_state.end_age
        rtv_score, rtv_label, rtv_reasons = calculate_rtv_score(df)

        render_blueprint_dashboard_mockup_section(df, rtv_score, rtv_label)

        render_dashboard_close_to_mock(df, rtv_score, rtv_label, rtv_reasons)

        # Plain-English explanation directly under the Retirement Dashboard cards.
        retirement_dashboard_reason_bits = []
        retirement_dashboard_idea_bits = []

        dashboard_score_val = rtv_score if "rtv_score" in locals() else 0
        dashboard_end_total = float(df["End Total"].iloc[-1] or 0) if "End Total" in df.columns else 0
        dashboard_unmet_need = float(df["Unmet Need"].sum() or 0) if "Unmet Need" in df.columns else 0

        dashboard_target_age = int(st.session_state.get("retire_age", 0) or 0)
        dashboard_ss_age = int(st.session_state.get("user_ss_age", 62) or 62)
        dashboard_plan_age = int(st.session_state.get("end_age", 90) or 90)
        dashboard_ss_gap = max(0, dashboard_ss_age - dashboard_target_age) if dashboard_target_age else 0
        dashboard_healthcare_gap = max(0, min(65, dashboard_plan_age) - dashboard_target_age) if dashboard_target_age else 0

        dashboard_avg_gap = float(df["Portfolio Need"].mean() if "Portfolio Need" in df.columns else 0)
        if dashboard_avg_gap <= 0 and "Total Spending" in df.columns and "Total Non-Portfolio Income" in df.columns:
            dashboard_avg_gap = float((df["Total Spending"] - df["Total Non-Portfolio Income"]).clip(lower=0).mean())
        dashboard_monthly_gap = max(dashboard_avg_gap, 0) / 12

        if dashboard_score_val < 60:
            retirement_dashboard_reason_bits.append(f"<b>Blueprint Score:</b> Your score is <b>{dashboard_score_val}/100</b>. This plan needs work before it looks retirement-ready.")
            retirement_dashboard_idea_bits.extend(["Try a later retirement age.", "Try lowering monthly spending.", "Add income sources if available."])
        elif dashboard_score_val < 80:
            retirement_dashboard_reason_bits.append(f"<b>Blueprint Score:</b> Your score is <b>{dashboard_score_val}/100</b>. This plan may be possible, but the cushion is thin.")
            retirement_dashboard_idea_bits.extend(["Build more cushion before retirement.", "Stress test bad market years.", "Compare Social Security timing."])
        else:
            retirement_dashboard_reason_bits.append(f"<b>Blueprint Score:</b> Your score is <b>{dashboard_score_val}/100</b>. This plan looks stronger under the current assumptions, but it should still be stress-tested.")
            retirement_dashboard_idea_bits.extend(["Save this version as your baseline.", "Run stress tests to see how it handles bad years.", "Compare one or two alternate retirement ages."])

        if dashboard_ss_gap > 0:
            retirement_dashboard_reason_bits.append(f"<b>Social Security gap:</b> There are about <b>{dashboard_ss_gap} year(s)</b> between the tested retirement age and when Social Security starts. During that gap, savings may need to carry more of the spending.")
            retirement_dashboard_idea_bits.append("Use the Action Plan to test whether delaying retirement or changing Social Security timing improves the score.")
        else:
            retirement_dashboard_reason_bits.append("<b>Social Security timing:</b> Social Security appears to start at or before the tested retirement age, which can reduce pressure on savings.")

        if dashboard_healthcare_gap > 0:
            retirement_dashboard_reason_bits.append(f"<b>Healthcare bridge:</b> There are about <b>{dashboard_healthcare_gap} year(s)</b> before Medicare age 65. Healthcare costs during this bridge period can reduce the plan cushion.")
            retirement_dashboard_idea_bits.append("Check whether healthcare costs before Medicare are realistic.")
        else:
            retirement_dashboard_reason_bits.append("<b>Healthcare bridge:</b> The plan does not show a major pre-Medicare healthcare bridge based on the current ages.")

        if dashboard_monthly_gap > 0:
            retirement_dashboard_reason_bits.append(f"<b>Monthly gap from savings:</b> After estimated income is counted, about <b>{compact_money(dashboard_monthly_gap)}</b> per month still needs to come from savings.")
            if dashboard_monthly_gap >= 8000:
                retirement_dashboard_idea_bits.append("The savings gap is large, so spending, income, and retirement age are the biggest levers.")
            elif dashboard_monthly_gap >= 3000:
                retirement_dashboard_idea_bits.append("The savings gap is manageable to test, but still deserves attention.")
        else:
            retirement_dashboard_reason_bits.append("<b>Monthly gap from savings:</b> Estimated income appears to cover the monthly spending need in the early years.")

        if dashboard_end_total <= 0 or dashboard_unmet_need > 0:
            retirement_dashboard_reason_bits.append("<b>Money left:</b> The projection shows a shortfall or portfolio depletion. The biggest levers are usually retiring later, reducing spending, increasing income, or saving more before retirement.")
            retirement_dashboard_idea_bits.append("Go to the Action Plan to see which lever may add the most points.")
        else:
            retirement_dashboard_reason_bits.append(f"<b>Money left:</b> The projection estimates about <b>{compact_money(dashboard_end_total)}</b> left at the end of the plan. This is a cushion estimate, not a guarantee.")
            if dashboard_end_total < 250000:
                retirement_dashboard_idea_bits.append("The ending cushion is thin, so stress testing matters.")
            else:
                retirement_dashboard_idea_bits.append("The ending balance is a cushion estimate. Use stress tests before relying on it.")

        cleaned_dashboard_ideas = []
        seen_dashboard_ideas = set()
        for idea in retirement_dashboard_idea_bits:
            if idea not in seen_dashboard_ideas:
                cleaned_dashboard_ideas.append(idea)
                seen_dashboard_ideas.add(idea)

        retirement_dashboard_reason_html = "<br/><br/>".join(retirement_dashboard_reason_bits)
        retirement_dashboard_ideas_html = "".join([f"<li>{idea}</li>" for idea in cleaned_dashboard_ideas[:5]])

        st.markdown(f"""
        <div class="rb-dashboard-explain rb-dashboard-explain-top">
          <div class="rb-explain-kicker">Retirement Dashboard Explanation</div>
          <div class="rb-explain-title">Why these numbers look this way</div>
          <div class="rb-explain-copy">
            {retirement_dashboard_reason_html}
          </div>
          <div class="rb-explain-next">
            <div class="rb-explain-next-title">What to look at next</div>
            <ul>{retirement_dashboard_ideas_html}</ul>
          </div>
          <div class="rb-explain-note">
            <b>Important:</b> The age shown is your <b>current target age being tested</b>, not a recommendation that you should retire at that age.
            The Action Plan is the next step to see what changes may improve the score.
          </div>
        </div>
        """, unsafe_allow_html=True)

        dashboard_explain_cols = st.columns([1, 1])
        with dashboard_explain_cols[0]:
            if st.button("Next: See Ideas to Improve My Score", type="primary", use_container_width=True, key="retirement_dashboard_to_action_plan_top"):
                go_to_page("Recommendations")
        with dashboard_explain_cols[1]:
            if st.button("Save This Baseline First", use_container_width=True, key="retirement_dashboard_to_saved_blueprints_top"):
                go_to_page("Saved Scenarios")


        st.markdown('<div class="rb-dashboard-premium-spacer"></div>', unsafe_allow_html=True)
        # Premium mini cards
        st.markdown("""
        <div class="rb-premium-title-row">
          <div>
            <div class="rb-premium-title-main">Premium Retirement Tools</div>
            <div style="color:#64748B;font-size:.95rem;margin-top:3px;">Advanced tools to take your plan to the next level.</div>
          </div>
          <div class="rb-premium-see-all">See all tools -&gt;</div>
        </div>
        """, unsafe_allow_html=True)

        dashboard_tools = [
            ("🎯", "Smart Retirement Age Optimizer", "Find the best age to retire with confidence.", "Open Age Optimizer", "age"),
            ("🪣", "2-Bucket Strategy", "Create a safer spending and growth strategy.", "Open 2-Bucket Strategy", "bucket"),
            ("🔁", "Scenario Comparison", "Compare retirement scenarios side by side.", "Open Scenario Comparison", "scenario"),
            ("💸", "Tax-Aware Withdrawal Plan", "Withdraw smarter and reduce tax pressure.", "Open Tax-Aware Plan", "tax"),
            ("📄", "Full Blueprint Report", "Get your complete retirement report.", "Open Blueprint Report", "report"),
            ("🤖", "Blueprint Coach", "Get educational guidance and plain-English answers.", "Open Blueprint Coach", "coach"),
        ]
        for row_start in [0, 3]:
            cols = st.columns(3)
            for col, tool in zip(cols, dashboard_tools[row_start:row_start+3]):
                icon, title, copy, button_label, key = tool
                with col:
                    st.markdown(
                        "<div class='rb-premium-mini'>"
                        + f"<div class='rb-premium-mini-icon'>{icon}</div>"
                        + f"<div class='rb-premium-mini-title'>{title}</div>"
                        + f"<div class='rb-premium-mini-copy'>{copy}</div>"
                        + "<div class='rb-premium-mini-badge'>Premium</div>"
                        + "</div>",
                        unsafe_allow_html=True,
                    )
                    if key == "age":
                        if st.button(button_label, key="mock_open_age", use_container_width=True):
                            go_to_page("Retirement Age Optimizer")
                    elif key == "bucket":
                        if st.button(button_label, key="mock_open_bucket", use_container_width=True):
                            st.session_state.dashboard_focus = "2-Bucket Strategy"
                            go_to_page("Retirement Dashboard")
                    elif key == "scenario":
                        if st.button(button_label, key="mock_open_scenario", use_container_width=True):
                            st.session_state.dashboard_focus = "Scenario Comparison"
                            go_to_page("Retirement Dashboard")
                    elif key == "tax":
                        if st.button(button_label, key="mock_open_tax", use_container_width=True):
                            st.session_state.projection_focus = "Tax-Aware Withdrawal Plan"
                            go_to_page("Projection Table")
                    elif key == "report":
                        if st.button(button_label, key="mock_open_report", use_container_width=True):
                            go_to_page("PDF Report")
                    elif key == "coach":
                        if st.button(button_label, key="mock_open_coach", use_container_width=True):
                            go_to_page("AI Retirement Coach")

        st.caption("Educational planning tool only. Not financial, tax, legal, insurance, or investment advice.")




        with st.expander("Advanced Dashboard Details", expanded=False):
            summary_dashboard = {
                "traditional": float(st.session_state.traditional),
                "roth": float(st.session_state.roth),
                "taxable": float(st.session_state.taxable),
                "cash": float(st.session_state.cash),
                "total_assets": float(st.session_state.traditional) + float(st.session_state.roth) + float(st.session_state.taxable) + float(st.session_state.cash),
                "monthly_spending": annual_household_spending() / 12,
                "annual_spending": annual_household_spending(),
                "annual_income": float(df["Total Non-Portfolio Income"].mean()),
                "income_coverage": float(df["Income Coverage Ratio"].mean()),
                "rough_wr": float(df["Withdrawal Rate"].max()),
                "score": rtv_score,
                "retire_age": st.session_state.retire_age,
                "end_age": st.session_state.end_age,
                "growth_return": st.session_state.growth_return,
                "safe_return": st.session_state.safe_return,
                "inflation": st.session_state.inflation,
            }

            risk_scores = calculate_risk_scores(summary_dashboard)

            st.subheader("Risk signals")
            rc1, rc2, rc3, rc4, rc5 = st.columns(5)
            rc1.metric("Sequence Risk", f"{risk_scores['Sequence Risk']}/100")
            rc2.metric("Tax Risk", f"{risk_scores['Tax Risk']}/100")
            rc3.metric("Healthcare Risk", f"{risk_scores['Healthcare Risk']}/100")
            rc4.metric("Longevity Risk", f"{risk_scores['Longevity Risk']}/100")
            rc5.metric("Income Stability", f"{100-risk_scores['Income Stability Risk']}/100")

            st.subheader("Why did I get this Blueprint Score?")
            if rtv_reasons:
                for reason in rtv_reasons:
                    st.write(f"- {reason}")
            else:
                st.write("No major risk flags found.")

            render_premium_insight("Dashboard insight", df, "general")
            render_confidence_meters(df)

            st.subheader("Home & Housing Strategy")
            h1, h2, h3, h4 = st.columns(4)
            h1.metric("Home Value", money(st.session_state.home_value))
            h2.metric("Mortgage Balance", money(st.session_state.mortgage_balance))
            h3.metric("Home Equity", money(home_equity()), housing_flexibility_label())
            h4.metric("Housing Plan", st.session_state.retirement_housing_plan)

            st.subheader("Premium Scenario Comparison")
            render_scenario_comparison_panel()

            st.subheader("Premium 2-Bucket Strategy")
            render_three_bucket_strategy(df)

            st.subheader("Compare 1 Bucket vs 2 Bucket")
            render_bucket_strategy_comparison_panel(df)

            st.subheader("Roth Conversion Explorer")
            st.caption("Educational preview: test an annual Roth conversion amount in Start My Blueprint, then review the tax and balance impact in the Projection Table.")
            rcol1, rcol2 = st.columns(2)
            with rcol1:
                st.metric("Annual Roth Conversion Tested", money(float(st.session_state.get("annual_conversion", 0) or 0)))
            with rcol2:
                st.metric("Traditional / Roth Balance", f"{money(float(st.session_state.get('traditional', 0) or 0))} / {money(float(st.session_state.get('roth', 0) or 0))}")
            rr1, rr2 = st.columns(2)
            with rr1:
                if st.button("Edit Roth Conversion Amount", use_container_width=True, key="dashboard_edit_roth_conversion"):
                    go_to_page("Guided Questions")
            with rr2:
                if st.button("Review Tax Impact in Projection", use_container_width=True, key="dashboard_review_roth_projection"):
                    go_to_page("Projection Table")
            st.warning("Educational purposes only. Roth conversions can create taxes today and should be reviewed with a qualified tax or financial professional.")

            st.subheader("Spending, Income, and Portfolio Withdrawal")
            st.pyplot(plot_spending_income_bar_chart(df), use_container_width=True)

            st.subheader("Income Gap")
            st.pyplot(plot_income_gap_chart(df), use_container_width=True)

            st.subheader("Withdrawal Rate Pressure")
            st.pyplot(plot_withdrawal_rate_chart(df), use_container_width=True)

    st.divider()
    next_cols = st.columns([1, 1])
    with next_cols[0]:
        if st.button("Next: View Action Plan", type="primary", use_container_width=True, key="next_from_dashboard_to_action"):
            go_to_page("Recommendations")
    with next_cols[1]:
        if st.button("Review Projection", use_container_width=True, key="next_from_dashboard_to_projection"):
            go_to_page("Projection Table")

if active_page == PAGE_NAMES[7]:
    render_page_shell("Action Plan", "Plain-English next steps to help improve your retirement blueprint.", "💡")
    render_guided_progress(5)
    page_help(
        "Recommendations",
        "This page explains what your retirement numbers mean in plain English and gives you practical ideas to improve the plan."
    )

    if not can_run:
        st.markdown("""
        <div class="rb-insight-card">
          <div class="rb-insight-kicker">Action Plan</div>
          <div class="rb-insight-title">Complete your blueprint first</div>
          <div class="rb-insight-copy">
            Add your core numbers, spending plan, and income sources first. Then this page will explain
            what looks strong, what needs attention, and what to try next.
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Start My Blueprint", type="primary", use_container_width=True, key="action_go_start"):
            go_to_page("Guided Questions")
    else:
        depleted = df["Unmet Need"].sum() > 0 or df["End Total"].iloc[-1] <= 0 or df["Age"].iloc[-1] < st.session_state.end_age
        max_wr = float(df["Withdrawal Rate"].max() or 0)
        avg_wr = float(df["Withdrawal Rate"].mean() or 0)
        rtv_score, rtv_label, rtv_reasons = calculate_rtv_score(df)
        ending_portfolio = float(df["End Total"].iloc[-1] or 0)
        avg_income_coverage = float(df["Income Coverage Ratio"].mean() or 0)
        end_age_val = int(st.session_state.get("end_age", 90) or 90)
        retire_age_val = int(st.session_state.get("retire_age", 0) or 0)

        avg_gap = 0.0
        if "Portfolio Need" in df.columns:
            avg_gap = float(df["Portfolio Need"].mean() or 0)
        elif "Total Spending" in df.columns and "Total Non-Portfolio Income" in df.columns:
            avg_gap = float((df["Total Spending"] - df["Total Non-Portfolio Income"]).clip(lower=0).mean())
        monthly_gap = max(avg_gap, 0) / 12

        if depleted or rtv_score < 60:
            simple_result = "Needs Work"
            simple_result_note = "Your current plan may run short unless something changes."
            result_color = "#FEF2F2"
        elif rtv_score < 80:
            simple_result = "Close, But Review"
            simple_result_note = "Your plan may work, but it needs a stronger cushion."
            result_color = "#FFFBEB"
        else:
            simple_result = "Looks Good"
            simple_result_note = "Your current plan appears realistic under these assumptions."
            result_color = "#F0FDF4"

        if max_wr > 0.07:
            pressure_title = "Withdrawal pressure"
            pressure_plain = "Your savings may need to cover too much spending each year."
            first_focus = "Lower spending, retire later, or add income."
        elif avg_income_coverage < 0.30:
            pressure_title = "Income gap"
            pressure_plain = "A lot of retirement spending depends on your portfolio."
            first_focus = "Review Social Security timing, pension, part-time income, or other income."
        elif ending_portfolio < 250000:
            pressure_title = "Low ending cushion"
            pressure_plain = "The plan may survive, but there may not be much margin for surprises."
            first_focus = "Build more cushion before increasing spending."
        else:
            pressure_title = "Plan cushion"
            pressure_plain = "Your plan has a reasonable cushion based on the current projection."
            first_focus = "Stress test the plan and compare a few options."

        st.markdown(f"""
        <div class="rb-insight-card">
          <div class="rb-insight-kicker">Plain-English Summary</div>
          <div class="rb-insight-title">Here’s what your retirement blueprint is telling you</div>
          <div class="rb-insight-copy">
            Your plan status is <b>{simple_result}</b>. {simple_result_note}
            The biggest thing to watch right now is <b>{pressure_title.lower()}</b>: {pressure_plain}
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="rb-card-grid">
          <div class="rb-card">
            <div class="rb-card-top"><div class="rb-card-label">Blueprint Score</div><div class="rb-icon">☆</div></div>
            <div class="rb-card-value">{rtv_score}/100</div>
            <div class="rb-card-note">{rtv_label}. This is your overall readiness signal.</div>
          </div>
          <div class="rb-card">
            <div class="rb-card-top"><div class="rb-card-label">Can I Retire at {retire_age_val}?</div><div class="rb-icon">✓</div></div>
            <div class="rb-card-value">{simple_result}</div>
            <div class="rb-card-note">{simple_result_note}</div>
          </div>
          <div class="rb-card">
            <div class="rb-card-top"><div class="rb-card-label">Money Left at {end_age_val}</div><div class="rb-icon">$</div></div>
            <div class="rb-card-value">{compact_money(ending_portfolio)}</div>
            <div class="rb-card-note">Estimated money remaining at the end of the plan.</div>
          </div>
          <div class="rb-card">
            <div class="rb-card-top"><div class="rb-card-label">Monthly Gap From Savings</div><div class="rb-icon">↗</div></div>
            <div class="rb-card-value">{compact_money(monthly_gap)}</div>
            <div class="rb-card-note">Estimated monthly amount that needs to come from savings.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="rb-next-box">
          <div class="rb-next-heading">What this means</div>
          <div class="rb-muted">
            Think of this page like a retirement coach. It is not just showing numbers.
            It is telling you where the plan is strongest, where it is weakest, and what to test next.
            Right now, your first focus should be: <b>{first_focus}</b>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        render_suggested_spending_target_tool()

        actions = build_rtv_improvement_recommendations(df, rtv_score)
        positive_actions = [a for a in actions if a.get("Blueprint Impact", 0) > 0]

        if rtv_score < 60:
            st.error(
                "Your current blueprint is high risk. The goal now is not to fine-tune the plan — it is to test bigger changes that could improve the score."
            )

        st.subheader("Your Next Best Step")

        if positive_actions:
            best = positive_actions[0]
            best_action = best["Action"]
            best_impact = best["Blueprint Impact"]
            new_score = best["New Blueprint Score"]

            st.markdown(f"""
            <div class="rb-insight-card">
              <div class="rb-insight-kicker">Highest-Impact Action</div>
              <div class="rb-insight-title">{best_action}</div>
              <div class="rb-insight-copy">
                This tested change could improve your Blueprint Score by about <b>+{best_impact}</b>,
                moving it from <b>{rtv_score}</b> to about <b>{new_score}</b>.
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Fallback improvement guidance. A low score should never say the plan is testing well.
            if rtv_score < 60:
                fallback_title = "Your plan needs improvement before it looks retirement-ready"
                fallback_copy = (
                    "The score is low, so focus on the biggest levers: spending, retirement age, income, "
                    "and savings. The app could not find a single automatic test that fixed the plan, but these are the right next moves to try."
                )
                fallback_impact = "Potential score impact: +10 to +35 depending on your numbers"
            elif rtv_score < 80:
                fallback_title = "Your plan is close, but it needs more cushion"
                fallback_copy = (
                    "The plan may be possible, but the cushion is thin. Try small improvements before treating this as a confident retirement date."
                )
                fallback_impact = "Potential score impact: +5 to +20 depending on your numbers"
            else:
                fallback_title = "Your plan is testing well"
                fallback_copy = (
                    "The common improvement tests did not materially improve your score. Use stress tests, "
                    "scenario comparisons, and the report to confirm the plan still feels comfortable."
                )
                fallback_impact = "Potential score impact: smaller"

            st.markdown(f"""
            <div class="rb-insight-card">
              <div class="rb-insight-kicker">Highest-Impact Action</div>
              <div class="rb-insight-title">{fallback_title}</div>
              <div class="rb-insight-copy">
                {fallback_copy}
                <br/><br/><b>{fallback_impact}</b>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("Top Things to Try")

        try_rows = []

        # Always show score-improvement advice, especially when the score is low.
        if max_wr > 0.07 or rtv_score < 60:
            try_rows.append([
                "Lower spending",
                "Reduces how much has to come out of savings each year.",
                "Try lowering spending by $500–$1,000/month.",
                "+5 to +15"
            ])
            try_rows.append([
                "Retire later",
                "Gives savings more time to grow and reduces the number of years withdrawals are needed.",
                "Test retiring 1–2 years later.",
                "+10 to +25"
            ])

        if avg_income_coverage < 0.30 or rtv_score < 70:
            try_rows.append([
                "Add reliable income",
                "Less of the retirement bill has to come from savings.",
                "Add pension, part-time work, rental income, or other income.",
                "+5 to +20"
            ])
            try_rows.append([
                "Review Social Security timing",
                "Delaying Social Security can increase guaranteed income and lower pressure on savings.",
                "Compare age 62, full retirement age, and 70.",
                "+3 to +15"
            ])

        if ending_portfolio < 250000 or rtv_score < 80:
            try_rows.append([
                "Increase savings before retirement",
                "More starting money gives the plan a bigger cushion.",
                "Try increasing contributions or saving extra cash before retirement.",
                "+5 to +20"
            ])
            try_rows.append([
                "Build a safer spending bucket",
                "A cash/safe bucket can help cover spending during bad market years.",
                "Target 1–3 years of near-term spending in safer money.",
                "+3 to +10"
            ])

        # If the plan is already strong, keep the list focused on validation.
        if not try_rows:
            try_rows.append([
                "Stress test the plan",
                "A good plan should still survive some bad years.",
                "Run the confidence and stress tests.",
                "Risk reduction"
            ])
            try_rows.append([
                "Compare better options",
                "Small timing changes can improve confidence.",
                "Test retirement ages and Social Security timing.",
                "Optimization"
            ])

        # Remove duplicates while preserving order.
        deduped = []
        seen = set()
        for row in try_rows:
            if row[0] not in seen:
                deduped.append(row)
                seen.add(row[0])

        try_df = pd.DataFrame(
            deduped[:6],
            columns=["Thing to Try", "Why It Helps", "Simple Next Step", "Possible Score Impact"]
        )

        try_df = try_df[[
            "Possible Score Impact",
            "Thing to Try",
            "Simple Next Step",
            "Why It Helps",
        ]]

        st.dataframe(try_df, use_container_width=True, hide_index=True)

        st.subheader("Plain-English Explanation of the Numbers")

        explain_df = pd.DataFrame([
            ["Blueprint Score", f"{rtv_score}/100", "A simple readiness score. Higher means the plan has more cushion."],
            ["Money Left at End", compact_money(ending_portfolio), "Estimated money remaining at the final planning age."],
            ["Monthly Gap From Savings", money(monthly_gap), "The part of monthly spending not covered by Social Security, pension, or other income."],
            ["Withdrawal Pressure", pct(max_wr), "How hard your spending is pulling from your savings. Lower is usually safer."],
            ["Income Coverage", pct(avg_income_coverage), "How much of your spending is covered by income instead of savings."],
        ], columns=["Item", "Your Result", "What It Means"])
        st.dataframe(explain_df, use_container_width=True, hide_index=True)

        with st.expander("Show advanced numbers"):
            st.caption("These are helpful for deeper analysis, but the plain-English summary above is the main takeaway.")
            advanced_df = pd.DataFrame([{
                "Blueprint Score": f"{rtv_score}/100",
                "Label": rtv_label,
                "Ending Portfolio": money(ending_portfolio),
                "Max Withdrawal Rate": pct(max_wr),
                "Average Withdrawal Rate": pct(avg_wr),
                "Average Income Coverage": pct(avg_income_coverage),
                "Unmet Need": money(df["Unmet Need"].sum()),
            }])
            st.dataframe(advanced_df, use_container_width=True, hide_index=True)

            if rtv_reasons:
                st.markdown("**Why this score?**")
                for reason in rtv_reasons:
                    st.write(f"- {reason}")

        st.subheader("Premium Planning Tools")
        st.caption("Use these tools when you want to go from a general answer to a more precise retirement strategy.")

        tool_cols = st.columns(3)
        with tool_cols[0]:
            if st.button("Compare Retirement Ages", use_container_width=True, key="action_age_optimizer"):
                go_to_page("Retirement Age Optimizer")
        with tool_cols[1]:
            if st.button("Review Projection Table", use_container_width=True, key="action_projection"):
                go_to_page("Projection Table")
        with tool_cols[2]:
            if st.button("Create Blueprint Report", use_container_width=True, key="action_report"):
                go_to_page("PDF Report")

        st.caption("Educational planning tool only. Not financial, tax, legal, insurance, or investment advice.")

    st.divider()
    next_cols = st.columns([1, 1])
    with next_cols[0]:
        if st.button("Compare Retirement Ages", type="primary", use_container_width=True, key="next_from_action_to_age"):
            go_to_page("Retirement Age Optimizer")
    with next_cols[1]:
        if st.button("Create Blueprint Report", use_container_width=True, key="next_from_action_to_report"):
            go_to_page("PDF Report")


if active_page == PAGE_NAMES[8]:
    render_page_shell("Projection", "A clean year-by-year view of how your retirement blueprint may play out.", "📈")
    render_guided_progress(4)

    if st.session_state.get("projection_focus"):
        focus_label = st.session_state.get("projection_focus")
        if focus_label == "Tax-Aware Withdrawal Plan":
            if can_run:
                render_tax_aware_withdrawal_plan(df)
            else:
                render_tax_aware_withdrawal_plan(None)
            st.divider()
        else:
            st.info(f"Opened from Premium Retirement Tools: **{focus_label}**. Review the projection below for year-by-year balances, income, withdrawals, taxes, and Roth conversion impact.")
        if st.button("Clear premium tool view", key="clear_projection_focus"):
            st.session_state.projection_focus = ""
            st.rerun()

    page_help(
        "Projection Table",
        "This page shows the year-by-year math behind your plan in a cleaner format. Start with the summary cards, then open the full detailed table if you want the deeper numbers."
    )

    if not can_run:
        st.markdown("""
        <div class="rb-insight-card">
          <div class="rb-insight-kicker">Projection</div>
          <div class="rb-insight-title">Complete your blueprint first</div>
          <div class="rb-insight-copy">
            Add your core numbers, spending plan, and income sources first. Then this page will show your
            year-by-year balances, income, withdrawals, taxes, and projected money left.
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Start My Blueprint", type="primary", use_container_width=True, key="projection_go_start"):
            go_to_page("Guided Questions")
    else:
        start_total = float(df["Start Total"].iloc[0] or 0)
        ending_total = float(df["End Total"].iloc[-1] or 0)
        end_age = int(df["Age"].iloc[-1])

        # Projection summary card: show the estimated portfolio available at the
        # selected retirement age instead of total lifetime withdrawals.
        retire_age_for_card = int(st.session_state.get("retire_age", 0) or 0)
        retirement_rows_for_card = df[df["Age"] >= retire_age_for_card] if "Age" in df.columns else pd.DataFrame()
        if not retirement_rows_for_card.empty and "Start Total" in retirement_rows_for_card.columns:
            portfolio_at_retirement = float(retirement_rows_for_card["Start Total"].iloc[0] or 0)
            portfolio_at_retirement_age = int(retirement_rows_for_card["Age"].iloc[0])
        else:
            portfolio_at_retirement = start_total
            portfolio_at_retirement_age = retire_age_for_card

        total_tax = float(df["Estimated Federal Tax"].sum() if "Estimated Federal Tax" in df.columns else 0)

        st.markdown("""
        <div class="rb-insight-card">
          <div class="rb-insight-kicker">Projection Insight</div>
          <div class="rb-insight-title">The table below is the math behind your blueprint</div>
          <div class="rb-insight-copy">
            Use this page when you want to see how your money may change each year. The summary cards show the big picture.
            The detailed table is there if you want to inspect the year-by-year numbers.
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="rb-card-grid">
          <div class="rb-card">
            <div class="rb-card-top"><div class="rb-card-label">Starting Portfolio</div><div class="rb-icon">$</div></div>
            <div class="rb-card-value">{compact_money(start_total)}</div>
            <div class="rb-card-note">Portfolio balance at the beginning of this projection.</div>
          </div>
          <div class="rb-card">
            <div class="rb-card-top"><div class="rb-card-label">Money Left at Age {end_age}</div><div class="rb-icon">✓</div></div>
            <div class="rb-card-value">{compact_money(ending_total)}</div>
            <div class="rb-card-note">Estimated balance at the end of the plan.</div>
          </div>
          <div class="rb-card">
            <div class="rb-card-top"><div class="rb-card-label">Portfolio at Retirement</div><div class="rb-icon">↗</div></div>
            <div class="rb-card-value">{compact_money(portfolio_at_retirement)}</div>
            <div class="rb-card-note">Estimated portfolio available at age {portfolio_at_retirement_age} when retirement begins.</div>
          </div>
          <div class="rb-card">
            <div class="rb-card-top"><div class="rb-card-label">Estimated Federal Tax</div><div class="rb-icon">$</div></div>
            <div class="rb-card-value">{compact_money(total_tax)}</div>
            <div class="rb-card-note">Educational estimate using current app tax assumptions.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        simple_cols = [
            "Age",
            "Start Total",
            "End Total",
            "Total Spending",
            "Total Non-Portfolio Income",
            "Portfolio Need",
            "Estimated Federal Tax",
            "Withdrawal Rate",
            "Unmet Need",
        ]
        simple_cols = [c for c in simple_cols if c in df.columns]
        simple = df[simple_cols].copy()

        rename_simple = {
            "Start Total": "Start Balance",
            "End Total": "End Balance",
            "Total Spending": "Spending",
            "Total Non-Portfolio Income": "Income",
            "Portfolio Need": "From Savings",
            "Estimated Federal Tax": "Federal Tax",
            "Withdrawal Rate": "Withdrawal Rate",
            "Unmet Need": "Shortfall",
        }
        simple = simple.rename(columns=rename_simple)

        money_like = ["Start Balance", "End Balance", "Spending", "Income", "From Savings", "Federal Tax", "Shortfall"]
        for col in money_like:
            if col in simple.columns:
                simple[col] = simple[col].map(money)
        if "Withdrawal Rate" in simple.columns:
            simple["Withdrawal Rate"] = simple["Withdrawal Rate"].map(pct)

        st.subheader("Clean projection view")
        st.caption("Start here. This version focuses only on the numbers most people actually need to understand.")

        st.dataframe(
            simple,
            use_container_width=True,
            hide_index=True,
            height=420,
        )

        st.markdown("""
        <div class="rb-next-box">
          <div class="rb-next-heading">How to read this table</div>
          <div class="rb-muted">
            <b>Start Balance</b> is what you begin the year with. <b>End Balance</b> is what may be left after growth,
            income, spending, withdrawals, and taxes. <b>From Savings</b> is the amount your portfolio needs to cover.
            <b>Shortfall</b> means the plan could not fully cover spending in that year.
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Show full detailed projection table"):
            show = df.copy()

            if "Taxable" in show.columns:
                show = show.rename(columns={"Taxable": "Taxable Brokerage Balance"})

            percent_cols = [
                "Withdrawal Rate",
                "Income Coverage Ratio",
                "Guaranteed Income Coverage Ratio",
                "Effective Federal Tax Rate",
            ]
            non_money_cols = [
                "Age",
                "Spouse Age",
                "Spouse Alive",
                "Household Retired",
            ] + percent_cols

            money_cols = [c for c in show.columns if c not in non_money_cols]
            for c in money_cols:
                show[c] = show[c].map(money)

            for c in percent_cols:
                if c in show.columns:
                    show[c] = show[c].map(pct)

            st.caption("This detailed version includes more columns for deeper analysis.")
            st.dataframe(show, use_container_width=True, hide_index=True, height=460)

        st.download_button(
            "Download Projection CSV",
            df.to_csv(index=False).encode("utf-8"),
            "retirement_projection.csv",
            "text/csv",
            use_container_width=True,
        )

        st.caption("Tax estimates now include taxable Social Security when provisional income exceeds IRS thresholds. Roth and cash withdrawals are modeled as tax-free; taxable brokerage is still simplified until the capital-gains phase.")


if active_page == PAGE_NAMES[9]:
    def _saved_blueprint_display_rows(saved_items):
        rows = []
        for i, item in enumerate(saved_items or []):
            try:
                name = safe_get(item, "name", None) or safe_get(item, "title", None) or f"Blueprint {i + 1}"
                created = safe_get(item, "created_at", None) or safe_get(item, "created", None) or ""
                score = safe_get(item, "score", None)
                if score is None:
                    score = safe_get(item, "blueprint_score", None)
                retire_age = safe_get(item, "retire_age", None) or safe_get(item, "retirement_age", None)
                ending = (
                    safe_get(item, "ending_portfolio", None)
                    or safe_get(item, "money_left", None)
                    or safe_get(item, "end_total", None)
                    or safe_get(item, "ending_balance", None)
                )
                rows.append({
                    "Blueprint": name,
                    "Created": created,
                    "Score": "Not calculated" if score is None else f"{safe_int(score)}/100",
                    "Retirement Age": "—" if retire_age is None else safe_int(retire_age),
                    "Money Left": "—" if ending is None else compact_money(safe_float(ending)),
                    "Status": "Ready" if score is not None else "Needs review",
                })
            except Exception:
                rows.append({
                    "Blueprint": f"Blueprint {i + 1}",
                    "Created": "",
                    "Score": "Could not read",
                    "Retirement Age": "—",
                    "Money Left": "—",
                    "Status": "Needs review",
                })
        return pd.DataFrame(rows)


    st.markdown("""
    <style>
    /* Saved Scenarios page polish */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border-radius: 12px;
        padding: 8px 10px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.45rem;
        font-weight: 800;
        color: #111827;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.82rem;
        color: #374151;
        font-weight: 650;
    }

    .saved-page-title {
        font-size: 2.05rem;
        line-height: 1.1;
        font-weight: 850;
        color: #111827;
        margin-bottom: 0.25rem;
    }

    .saved-page-caption {
        font-size: 1rem;
        color: #4b5563;
        margin-bottom: 1.5rem;
    }

    .scenario-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        padding-bottom: 8px;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 14px;
    }

    .scenario-title-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }

    .scenario-title {
        font-size: 1.35rem;
        font-weight: 850;
        color: #111827;
    }

    .scenario-date {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 10px;
        border-radius: 999px;
        background: #F1F5F9;
        color: #475569;
        font-size: 0.82rem;
        font-weight: 750;
        white-space: nowrap;
    }

    .badge-current {
        display: inline-block;
        padding: 4px 11px;
        border-radius: 999px;
        background: #dbeafe;
        color: #1d4ed8;
        font-size: 0.78rem;
        font-weight: 800;
    }

    .badge-strong {
        display: inline-block;
        padding: 4px 11px;
        border-radius: 999px;
        background: #dcfce7;
        color: #15803d;
        font-size: 0.78rem;
        font-weight: 800;
    }

    .badge-work {
        display: inline-block;
        padding: 4px 11px;
        border-radius: 999px;
        background: #ffedd5;
        color: #ea580c;
        font-size: 0.78rem;
        font-weight: 800;
    }

    .badge-risk {
        display: inline-block;
        padding: 4px 11px;
        border-radius: 999px;
        background: #fee2e2;
        color: #dc2626;
        font-size: 0.78rem;
        font-weight: 800;
    }

    .section-title {
        font-weight: 850;
        font-size: 1rem;
        margin-bottom: 0.65rem;
        color: #111827;
    }

    .kv-row {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid #f1f5f9;
        padding: 6px 0;
        font-size: 0.93rem;
    }

    .kv-left {
        color: #475569;
    }

    .kv-right {
        color: #111827;
        font-weight: 750;
    }

    .score-big {
        font-size: 2.15rem;
        font-weight: 900;
        line-height: 1.0;
        color: #16a34a;
    }

    .score-big-warning {
        color: #f97316;
    }

    .score-big-risk {
        color: #dc2626;
    }

    .tiny-caption {
        color: #64748b;
        font-size: 0.8rem;
    }
    
/* ==========================================================
   Hide Streamlit's "Press Enter to submit form" text globally
   ========================================================== */
input::placeholder,
textarea::placeholder,
input:focus::placeholder,
textarea:focus::placeholder,
[data-baseweb="input"] input::placeholder,
[data-baseweb="input"] input:focus::placeholder,
[data-baseweb="textarea"] textarea::placeholder,
[data-baseweb="textarea"] textarea:focus::placeholder,
.stNumberInput input::placeholder,
.stNumberInput input:focus::placeholder,
.stTextInput input::placeholder,
.stTextInput input:focus::placeholder,
.stTextArea textarea::placeholder,
.stTextArea textarea:focus::placeholder,
input[placeholder="Press Enter to submit form"]::placeholder,
input[placeholder="Press Enter to submit form"]:focus::placeholder {
    color: transparent !important;
    opacity: 0 !important;
    -webkit-text-fill-color: transparent !important;
    font-size: 0 !important;
}

input[placeholder="Press Enter to submit form"],
input[placeholder="Press Enter to submit form"]:focus {
    caret-color: #0f172a !important;
}


/* Match Spending/Income two-option selectors to the blue pill style */
div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    gap: 0 !important;
    width: fit-content !important;
    padding: 8px !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 999px !important;
    background: #F8FAFC !important;
    box-shadow: 0 8px 22px rgba(15,23,42,.04) !important;
}
div[role="radiogroup"] label {
    border-radius: 999px !important;
    padding: 10px 18px !important;
    margin: 0 !important;
    min-width: 160px !important;
    justify-content: center !important;
}
div[role="radiogroup"] label[data-checked="true"],
div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(135deg, #2563EB, #22C7C7) !important;
    color: #FFFFFF !important;
    box-shadow: 0 10px 24px rgba(37,99,235,.25) !important;
}
div[role="radiogroup"] label:has(input:checked) p,
div[role="radiogroup"] label:has(input:checked) span,
div[role="radiogroup"] label[data-checked="true"] p,
div[role="radiogroup"] label[data-checked="true"] span {
    color: #FFFFFF !important;
    font-weight: 900 !important;
}
div[role="radiogroup"] input {
    display: none !important;
}


/* Keep large money values readable inside dashboard cards */
.rb-card-value,
.rb-kpi-value {
    white-space: nowrap !important;
    overflow-wrap: normal !important;
    word-break: normal !important;
}
.rb-card-value {
    font-size: clamp(1.65rem, 2.4vw, 2.25rem) !important;
}
.rb-kpi-value {
    font-size: clamp(1.65rem, 2.4vw, 2.35rem) !important;
}


/* Action Plan polish */
.rb-insight-card b,
.rb-next-box b {
    color: #0f172a;
    font-weight: 900;
}


/* Projection page polish */
div[data-testid="stDataFrame"] {
    border-radius: 16px !important;
    overflow: hidden !important;
}


/* Force dashboard money-left values to stay on one line */
.money-compact,
.rb-card-value,
.rb-kpi-value {
    white-space: nowrap !important;
    word-break: keep-all !important;
    overflow-wrap: normal !important;
    line-height: 1.05 !important;
}

.rb-card-value {
    font-size: clamp(1.55rem, 2.1vw, 2.05rem) !important;
}

.rb-kpi-value {
    font-size: clamp(1.55rem, 2.1vw, 2.15rem) !important;
}

/* Give KPI cards a little more breathing room for money values */
.rb-card,
.rb-kpi-card {
    min-width: 0 !important;
}


/* Compact top-right sign-in area */
.rb-account-mini {
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    background: #FFFFFF;
    padding: 10px 12px;
    box-shadow: 0 8px 20px rgba(15,23,42,.05);
    margin-bottom: 8px;
    text-align: center;
}
.rb-account-mini-label {
    color: #0F172A;
    font-weight: 900;
    font-size: .82rem;
}
.rb-account-mini-email {
    color: #2563EB;
    font-weight: 750;
    font-size: .72rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}


/* Full-width hero after removing top-right sign-in button */
.rb-hero {
    width: 100% !important;
}


/* Home empty-state mini steps */
.rb-mini-step {
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    background: #FFFFFF;
    padding: 14px;
    min-height: 84px;
    color: #64748B;
    box-shadow: 0 8px 22px rgba(15,23,42,.04);
    line-height: 1.35;
}
.rb-mini-step b {
    display: inline-flex;
    width: 26px;
    height: 26px;
    border-radius: 999px;
    align-items: center;
    justify-content: center;
    background: #2563EB;
    color: #FFFFFF;
    margin-bottom: 8px;
}


/* Dashboard save baseline callout */
.rb-save-callout {
    margin: 18px 0 12px 0;
    border: 1px solid #BFDBFE;
    border-left: 6px solid #2563EB;
    border-radius: 18px;
    background: linear-gradient(135deg, #EFF6FF 0%, #F8FAFC 55%, #ECFEFF 100%);
    padding: 18px 20px;
    box-shadow: 0 10px 26px rgba(37,99,235,.08);
}
.rb-save-kicker {
    color: #2563EB;
    font-size: .78rem;
    font-weight: 950;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: 6px;
}
.rb-save-title {
    color: #0F172A;
    font-size: 1.1rem;
    font-weight: 950;
    margin-bottom: 6px;
}
.rb-save-copy {
    color: #64748B;
    font-size: .95rem;
    line-height: 1.45;
}


/* Dashboard plain-English explanation polish */
.rb-next-box b {
    color: #0f172a;
    font-weight: 900;
}


/* Dashboard explanation polish */
.rb-next-box b {
    color: #0f172a;
    font-weight: 900;
}


/* Retirement Dashboard plain-English explanation */
.rb-dashboard-explain {
    border: 1px solid #BFDBFE !important;
    border-radius: 24px !important;
    background: linear-gradient(180deg, #F8FBFF 0%, #EFF6FF 100%) !important;
    padding: 22px 24px !important;
    box-shadow: 0 10px 24px rgba(59,130,246,.08) !important;
}
.rb-explain-kicker {
    color: #2563EB !important;
    font-size: .78rem !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    margin-bottom: 8px !important;
}
.rb-explain-title {
    color: #1E3A8A !important;
    font-size: 1.28rem !important;
    font-weight: 950 !important;
    margin-bottom: 14px !important;
}
.rb-explain-copy {
    color: #475569 !important;
    font-size: 1rem !important;
    line-height: 1.65 !important;
}
.rb-explain-copy b {
    color: #0F172A !important;
    font-weight: 900 !important;
}


/* Expanded Retirement Dashboard explanation */
.rb-explain-next {
    margin-top: 18px !important;
    border: 1px solid #DBEAFE !important;
    background: rgba(255,255,255,.65) !important;
    border-radius: 18px !important;
    padding: 14px 16px !important;
}
.rb-explain-next-title {
    color: #1D4ED8 !important;
    font-weight: 900 !important;
    margin-bottom: 6px !important;
}
.rb-explain-next ul {
    margin: 8px 0 0 20px !important;
    padding: 0 !important;
    color: #475569 !important;
}
.rb-explain-next li {
    margin-bottom: 7px !important;
    line-height: 1.45 !important;
}
.rb-explain-note {
    margin-top: 16px !important;
    color: #475569 !important;
    font-size: .96rem !important;
    line-height: 1.55 !important;
    border-top: 1px solid rgba(59,130,246,.15) !important;
    padding-top: 14px !important;
}
.rb-explain-note b {
    color: #0F172A !important;
    font-weight: 900 !important;
}


/* Dashboard explanation placed near score cards */
.rb-dashboard-explain {
    border: 1px solid #BFDBFE !important;
    border-radius: 24px !important;
    background: linear-gradient(180deg, #F8FBFF 0%, #EFF6FF 100%) !important;
    padding: 22px 24px !important;
    box-shadow: 0 10px 24px rgba(59,130,246,.08) !important;
}
.rb-explain-kicker {
    color: #2563EB !important;
    font-size: .78rem !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    margin-bottom: 8px !important;
}
.rb-explain-title {
    color: #1E3A8A !important;
    font-size: 1.28rem !important;
    font-weight: 950 !important;
    margin-bottom: 14px !important;
}
.rb-explain-copy {
    color: #475569 !important;
    font-size: 1rem !important;
    line-height: 1.65 !important;
}
.rb-explain-copy b {
    color: #0F172A !important;
    font-weight: 900 !important;
}
.rb-explain-next {
    margin-top: 18px !important;
    border: 1px solid #DBEAFE !important;
    background: rgba(255,255,255,.65) !important;
    border-radius: 18px !important;
    padding: 14px 16px !important;
}
.rb-explain-next-title {
    color: #1D4ED8 !important;
    font-weight: 900 !important;
    margin-bottom: 6px !important;
}
.rb-explain-next ul {
    margin: 8px 0 0 20px !important;
    padding: 0 !important;
    color: #475569 !important;
}
.rb-explain-next li {
    margin-bottom: 7px !important;
    line-height: 1.45 !important;
}
.rb-explain-note {
    margin-top: 16px !important;
    color: #475569 !important;
    font-size: .96rem !important;
    line-height: 1.55 !important;
    border-top: 1px solid rgba(59,130,246,.15) !important;
    padding-top: 14px !important;
}
.rb-explain-note b {
    color: #0F172A !important;
    font-weight: 900 !important;
}


/* Section label used when Home contains dashboard results */
.rb-page-section-label {
    margin-top: 18px;
    margin-bottom: 4px;
    color: #0F172A;
    font-weight: 950;
    font-size: 1.35rem;
}


/* Polished status message card */
.rb-status-card {
    display: flex;
    gap: 14px;
    align-items: flex-start;
    border-radius: 20px;
    padding: 18px 20px;
    margin: 18px 0 22px 0;
    box-shadow: 0 10px 26px rgba(15,23,42,.06);
}
.rb-status-card.ready {
    border: 1px solid #BFDBFE;
    background: linear-gradient(135deg, #EFF6FF 0%, #F8FAFC 55%, #ECFEFF 100%);
}
.rb-status-card.needs {
    border: 1px solid #FDE68A;
    background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 65%);
}
.rb-status-icon {
    flex: 0 0 auto;
    width: 38px;
    height: 38px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 950;
    color: #FFFFFF;
    background: #2563EB;
    box-shadow: 0 8px 16px rgba(37,99,235,.18);
}
.rb-status-card.needs .rb-status-icon {
    background: #F59E0B;
    box-shadow: 0 8px 16px rgba(245,158,11,.18);
}
.rb-status-title {
    color: #0F172A;
    font-weight: 950;
    font-size: 1.02rem;
    margin-bottom: 4px;
}
.rb-status-copy {
    color: #64748B;
    font-size: .95rem;
    line-height: 1.45;
}


/* Retirement Dashboard explanation under cards */
.rb-dashboard-explain-top {
    margin-top: 18px !important;
    margin-bottom: 22px !important;
    width: 100% !important;
}
.rb-dashboard-explain {
    border: 1px solid #BFDBFE !important;
    border-radius: 24px !important;
    background: linear-gradient(180deg, #F8FBFF 0%, #EFF6FF 100%) !important;
    padding: 22px 24px !important;
    box-shadow: 0 10px 24px rgba(59,130,246,.08) !important;
}
.rb-explain-kicker {
    color: #2563EB !important;
    font-size: .78rem !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    margin-bottom: 8px !important;
}
.rb-explain-title {
    color: #1E3A8A !important;
    font-size: 1.28rem !important;
    font-weight: 950 !important;
    margin-bottom: 14px !important;
}
.rb-explain-copy {
    color: #475569 !important;
    font-size: 1rem !important;
    line-height: 1.65 !important;
}
.rb-explain-copy b {
    color: #0F172A !important;
    font-weight: 900 !important;
}
.rb-explain-next {
    margin-top: 18px !important;
    border: 1px solid #DBEAFE !important;
    background: rgba(255,255,255,.65) !important;
    border-radius: 18px !important;
    padding: 14px 16px !important;
}
.rb-explain-next-title {
    color: #1D4ED8 !important;
    font-weight: 900 !important;
    margin-bottom: 6px !important;
}
.rb-explain-next ul {
    margin: 8px 0 0 20px !important;
    padding: 0 !important;
    color: #475569 !important;
}
.rb-explain-next li {
    margin-bottom: 7px !important;
    line-height: 1.45 !important;
}
.rb-explain-note {
    margin-top: 16px !important;
    color: #475569 !important;
    font-size: .96rem !important;
    line-height: 1.55 !important;
    border-top: 1px solid rgba(59,130,246,.15) !important;
    padding-top: 14px !important;
}
.rb-explain-note b {
    color: #0F172A !important;
    font-weight: 900 !important;
}


/* Equal-size Retirement Dashboard KPI cards */
.rb-card-grid {
    align-items: stretch !important;
}
.rb-card-grid .rb-card {
    height: 100% !important;
    min-height: 250px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
}
.rb-card-grid .rb-card .rb-card-note {
    margin-top: auto !important;
}

/* Light theme-matching explanation box under the cards */
.rb-dashboard-explain-top {
    margin-top: 18px !important;
    margin-bottom: 22px !important;
    width: 100% !important;
}
.rb-dashboard-explain {
    border: 1px solid #BFDBFE !important;
    border-radius: 24px !important;
    background: linear-gradient(180deg, #F8FBFF 0%, #EFF6FF 100%) !important;
    padding: 22px 24px !important;
    box-shadow: 0 10px 24px rgba(59,130,246,.08) !important;
}
.rb-explain-kicker {
    color: #2563EB !important;
    font-size: .78rem !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    margin-bottom: 8px !important;
}
.rb-explain-title {
    color: #1E3A8A !important;
    font-size: 1.28rem !important;
    font-weight: 950 !important;
    margin-bottom: 14px !important;
}
.rb-explain-copy {
    color: #475569 !important;
    font-size: 1rem !important;
    line-height: 1.65 !important;
}
.rb-explain-copy b {
    color: #0F172A !important;
    font-weight: 900 !important;
}
.rb-explain-next {
    margin-top: 18px !important;
    border: 1px solid #DBEAFE !important;
    background: rgba(255,255,255,.65) !important;
    border-radius: 18px !important;
    padding: 14px 16px !important;
}
.rb-explain-next-title {
    color: #1D4ED8 !important;
    font-weight: 900 !important;
    margin-bottom: 6px !important;
}
.rb-explain-next ul {
    margin: 8px 0 0 20px !important;
    padding: 0 !important;
    color: #475569 !important;
}
.rb-explain-next li {
    margin-bottom: 7px !important;
    line-height: 1.45 !important;
}
.rb-explain-note {
    margin-top: 16px !important;
    color: #475569 !important;
    font-size: .96rem !important;
    line-height: 1.55 !important;
    border-top: 1px solid rgba(59,130,246,.15) !important;
    padding-top: 14px !important;
}
.rb-explain-note b {
    color: #0F172A !important;
    font-weight: 900 !important;
}


/* Premium tools placed directly under Retirement Dashboard explanation */
.rb-dashboard-premium-spacer {
    height: 16px;
}


/* Six-step retirement blueprint path */
.rb-progress-grid, .rb-step-grid {
    grid-template-columns: repeat(6, minmax(0, 1fr)) !important;
}
@media (max-width: 900px) {
    .rb-progress-grid, .rb-step-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
}


/* Money-left card runout note */
.rb-kpi-card-v2 .rb-kpi-pill {
    white-space: nowrap;
}


/* Sidebar cleanup: avoid oversized hover-tooltip feel */
section[data-testid="stSidebar"] button {
    overflow: hidden !important;
}



/* Premium Blueprint Dashboard mockup section */
.rb-blueprint-mock-hero {
    display:flex;
    gap:14px;
    align-items:flex-start;
    border:1px solid #C7E3FF;
    border-radius:22px;
    background:linear-gradient(135deg,#F8FBFF 0%,#FFFFFF 62%,#ECFEFF 100%);
    padding:20px 22px;
    margin:8px 0 18px 0;
    box-shadow:0 12px 30px rgba(15,23,42,.055);
}
.rb-blueprint-mock-icon {
    width:48px;
    height:48px;
    border-radius:14px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#E0F2FE;
    font-size:1.45rem;
    flex:0 0 auto;
}
.rb-blueprint-mock-kicker-pill {
    display:inline-flex;
    align-items:center;
    border-radius:999px;
    padding:4px 10px;
    background:#DBEAFE;
    color:#1D4ED8;
    font-size:.76rem;
    font-weight:900;
    margin-bottom:8px;
}
.rb-blueprint-mock-title {
    color:#0F172A;
    font-size:1.45rem;
    font-weight:950;
    letter-spacing:-.03em;
    margin-bottom:4px;
}
.rb-blueprint-mock-sub {
    color:#64748B;
    line-height:1.45;
    max-width:850px;
}
.rb-score-banner {
    display:flex;
    gap:18px;
    align-items:center;
    border:1px solid #BBF7D0;
    border-radius:22px;
    background:linear-gradient(135deg,#ECFDF5 0%,#F0FDFA 100%);
    padding:22px 24px;
    margin:18px 0 20px 0;
    box-shadow:0 14px 30px rgba(16,185,129,.10);
}
.rb-score-badge {
    width:74px;
    height:74px;
    border-radius:18px;
    background:linear-gradient(135deg,#22C55E,#059669);
    color:#FFFFFF;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    box-shadow:0 14px 24px rgba(5,150,105,.25);
    flex:0 0 auto;
}
.rb-score-badge-num { font-size:1.8rem; font-weight:950; line-height:1; }
.rb-score-badge-label { font-size:.55rem; font-weight:900; letter-spacing:.05em; margin-top:4px; }
.rb-score-banner-pill {
    display:inline-flex;
    border-radius:999px;
    padding:4px 10px;
    background:#DCFCE7;
    color:#15803D;
    font-size:.75rem;
    font-weight:900;
    margin-bottom:7px;
}
.rb-score-banner-title {
    color:#0F172A;
    font-size:1.25rem;
    font-weight:950;
    letter-spacing:-.02em;
    margin-bottom:4px;
}
.rb-score-banner-copy { color:#475569; line-height:1.5; }
.rb-dashboard-section-kicker {
    color:#2563EB;
    font-size:.78rem;
    font-weight:950;
    text-transform:uppercase;
    letter-spacing:.08em;
    margin:20px 0 10px 3px;
}
.rb-health-timeline-grid {
    display:grid;
    grid-template-columns: 1.08fr .92fr;
    gap:18px;
    margin:18px 0 20px 0;
}
.rb-panel-card {
    background:#FFFFFF;
    border:1px solid #E5E7EB;
    border-radius:22px;
    padding:20px 22px;
    box-shadow:0 10px 26px rgba(15,23,42,.055);
}
.rb-panel-title {
    color:#0F172A;
    font-size:1.15rem;
    font-weight:950;
    margin-bottom:4px;
}
.rb-panel-sub { color:#64748B; font-size:.9rem; margin-bottom:16px; }
.rb-health-row {
    display:grid;
    grid-template-columns: 42px 1fr auto;
    gap:12px;
    align-items:center;
    padding:12px 0;
    border-top:1px solid #F1F5F9;
}
.rb-health-row:first-of-type { border-top:0; }
.rb-health-icon {
    width:34px;
    height:34px;
    border-radius:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#F8FAFC;
    font-size:1rem;
}
.rb-health-title { color:#0F172A; font-weight:900; }
.rb-health-copy { color:#64748B; font-size:.86rem; line-height:1.35; }
.rb-health-pill {
    border-radius:999px;
    padding:5px 10px;
    font-weight:900;
    font-size:.72rem;
    white-space:nowrap;
}
.rb-pill-green { background:#DCFCE7; color:#15803D; }
.rb-pill-yellow { background:#FEF3C7; color:#B45309; }
.rb-pill-red { background:#FEE2E2; color:#B91C1C; }
.rb-pill-blue { background:#DBEAFE; color:#1D4ED8; }
.rb-timeline-row {
    display:grid;
    grid-template-columns: 52px 1fr;
    gap:12px;
    padding:12px 0;
}
.rb-timeline-age { color:#2563EB; font-weight:950; }
.rb-timeline-title { color:#0F172A; font-weight:900; }
.rb-timeline-copy { color:#64748B; font-size:.86rem; line-height:1.35; }
@media (max-width: 900px) {
    .rb-score-banner { align-items:flex-start; }
    .rb-health-timeline-grid { grid-template-columns:1fr; }
}

</style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='saved-page-title'>Saved Scenarios</div>", unsafe_allow_html=True)
    st.markdown("<div class='saved-page-caption'>Save, load, compare, and generate AI recommendations for your retirement plans.</div>", unsafe_allow_html=True)

    if "compare_scenarios" not in st.session_state:
        st.session_state.compare_scenarios = {}

    if "saved_ai_recommendations" not in st.session_state:
        st.session_state.saved_ai_recommendations = {}

    def saved_scenario_annual_spending(data):
        """Calculate spending from saved scenario data using the same flat/detailed logic as the live app."""
        if data.get("budget_mode", "Flat monthly number") == "Detailed monthly budget":
            return sum(float(data.get(k, 0) or 0) for k, _ in budget_keys) * 12
        return float(data.get("flat_monthly_spending", 0) or 0) * 12

    def scenario_summary_from_data(data):
        traditional = float(data.get("traditional", 0) or 0)
        roth = float(data.get("roth", 0) or 0)
        taxable = float(data.get("taxable", 0) or 0)
        cash = float(data.get("cash", 0) or 0)
        total_assets = traditional + roth + taxable + cash

        annual_spending = saved_scenario_annual_spending(data)
        monthly_spending = annual_spending / 12

        user_ss = float(data.get("user_ss", 0) or 0)
        spouse_ss = float(data.get("spouse_ss", 0) or 0) if data.get("has_spouse", False) else 0
        simple_income = float(data.get("simple_income", 0) or 0)
        annual_income = user_ss + spouse_ss + simple_income

        income_coverage = annual_income / annual_spending if annual_spending > 0 else 0

        retire_age = int(data.get("retire_age", 0) or 0)
        current_age = int(data.get("current_age", 0) or 0)
        end_age = int(data.get("end_age", 90) or 90)
        years_to_retire = max(retire_age - current_age, 0)

        rough_wr = max(annual_spending - annual_income, 0) / total_assets if total_assets > 0 else 0

        # Use the real projection engine for saved scenario math.
        projection_df, score, label, rtv_reasons = run_projection_for_saved_scenario(data)

        if not projection_df.empty:
            annual_income = float(projection_df["Total Non-Portfolio Income"].mean())
            income_coverage = float(projection_df["Income Coverage Ratio"].mean())
            rough_wr = float(projection_df["Withdrawal Rate"].max())
            ending_portfolio = float(projection_df["End Total"].iloc[-1])
            unmet_need = float(projection_df["Unmet Need"].sum())
        else:
            ending_portfolio = 0
            unmet_need = 0

        if score >= 90:
            badge = "badge-strong"
            score_class = "score-big"
        elif score >= 80:
            badge = "badge-strong"
            score_class = "score-big"
        elif score >= 60:
            badge = "badge-work"
            score_class = "score-big score-big-warning"
        else:
            badge = "badge-risk"
            score_class = "score-big score-big-risk"

        return {
            "traditional": traditional,
            "roth": roth,
            "taxable": taxable,
            "cash": cash,
            "total_assets": total_assets,
            "monthly_spending": monthly_spending,
            "annual_spending": annual_spending,
            "user_ss": user_ss,
            "spouse_ss": spouse_ss,
            "simple_income": simple_income,
            "annual_income": annual_income,
            "income_coverage": income_coverage,
            "rough_wr": rough_wr,
            "ending_portfolio": ending_portfolio,
            "unmet_need": unmet_need,
            "rtv_reasons": rtv_reasons,
            "score": score,
            "label": label,
            "badge": badge,
            "score_class": score_class,
            "current_age": current_age,
            "retire_age": retire_age,
            "end_age": end_age,
            "years_to_retire": years_to_retire,
            "growth_return": float(data.get("growth_return", 0) or 0),
            "safe_return": float(data.get("safe_return", 0) or 0),
            "inflation": float(data.get("inflation", 0) or 0),
            "bucket1_years": float(data.get("bucket1_years", 0) or 0),
            "annual_conversion": float(data.get("annual_conversion", 0) or 0),
        }

    def make_template_data(template_name):
        data = get_scenario_data()

        if template_name == "Conservative":
            data["growth_return"] = 0.055
            data["safe_return"] = 0.035
            data["inflation"] = 0.035
            data["bucket1_years"] = 4.0
            if float(data.get("flat_monthly_spending", 0) or 0) > 0:
                data["flat_monthly_spending"] = round(float(data["flat_monthly_spending"]) * 1.05)
            data["annual_conversion"] = 0

        elif template_name == "Base":
            data["growth_return"] = 0.07
            data["safe_return"] = 0.045
            data["inflation"] = 0.03
            data["bucket1_years"] = 3.0

        elif template_name == "Aggressive":
            data["growth_return"] = 0.085
            data["safe_return"] = 0.045
            data["inflation"] = 0.03
            data["bucket1_years"] = 2.0
            if int(data.get("retire_age", 0) or 0) > 0:
                data["retire_age"] = max(int(data["retire_age"]) - 2, int(data.get("current_age", 0) or 0))

        return data

    def generate_recommendations_for_summary(summary):
        recs = []

        if summary["score"] >= 85:
            recs.append("This scenario looks strong. Focus on protecting the plan from taxes, healthcare surprises, and sequence-of-return risk.")
        elif summary["score"] >= 70:
            recs.append("This scenario may be viable, but it should be stress-tested before relying on it.")
        else:
            recs.append("This scenario needs work before it should be considered a confident retirement plan.")

        if summary["rough_wr"] > 0.06:
            recs.append("Withdrawal pressure looks high. Consider delaying retirement, lowering spending, increasing guaranteed income, or building more assets.")
        elif summary["rough_wr"] > 0.04:
            recs.append("Withdrawal pressure is moderate. A stronger cash bucket or lower early-retirement spending could improve confidence.")

        if summary["income_coverage"] < 0.40:
            recs.append("Outside income covers a relatively small share of spending. Social Security timing, part-time income, pension income, or annuity analysis may help.")
        elif summary["income_coverage"] >= 0.70:
            recs.append("Income coverage is strong. This reduces pressure on the portfolio.")

        if summary["cash"] < summary["annual_spending"] * 1.5 and summary["annual_spending"] > 0:
            recs.append("Bucket 1/cash may be light. Consider holding 2–4 years of spending needs in safer assets before retirement.")

        if summary["traditional"] > summary["roth"] * 3 and summary["traditional"] > 250000:
            recs.append("Traditional retirement assets are much larger than Roth. Roth conversion planning may reduce future tax risk.")

        return recs

    def build_pdf_report_bytes(name, data, summary, recommendations):
        """Create a polished, client-friendly PDF report for a saved retirement scenario."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.45 * inch,
            leftMargin=0.45 * inch,
            topMargin=0.45 * inch,
            bottomMargin=0.45 * inch,
            title=f"Retirement Blueprint 101 - {name}",
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="RBTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=8,
        ))
        styles.add(ParagraphStyle(
            name="RBSubtitle",
            parent=styles["BodyText"],
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#475569"),
            spaceAfter=10,
        ))
        styles.add(ParagraphStyle(
            name="RBSection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1D4ED8"),
            spaceBefore=12,
            spaceAfter=7,
        ))
        styles.add(ParagraphStyle(
            name="RBBody",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#334155"),
            spaceAfter=6,
        ))
        styles.add(ParagraphStyle(
            name="RBSmall",
            parent=styles["BodyText"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#64748B"),
        ))
        styles.add(ParagraphStyle(
            name="RBCardLabel",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9,
            textColor=colors.HexColor("#64748B"),
            alignment=1,
        ))
        styles.add(ParagraphStyle(
            name="RBCardValue",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=colors.HexColor("#0F172A"),
            alignment=1,
        ))
        styles.add(ParagraphStyle(
            name="RBWhiteTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.white,
            alignment=0,
        ))
        styles.add(ParagraphStyle(
            name="RBWhiteBody",
            parent=styles["BodyText"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#DBEAFE"),
            alignment=0,
        ))

        def esc(x):
            return xml_escape(str(x))

        def para(text, style="RBBody"):
            return Paragraph(esc(text), styles[style])

        def bullet(text):
            return Paragraph("• " + esc(text), styles["RBBody"])

        def status_color(score):
            if score >= 85:
                return colors.HexColor("#16A34A")
            if score >= 70:
                return colors.HexColor("#2563EB")
            if score >= 55:
                return colors.HexColor("#F59E0B")
            return colors.HexColor("#DC2626")

        projection_df, projection_score, projection_label, projection_reasons = run_projection_for_saved_scenario(data)
        if projection_df is None:
            projection_df = pd.DataFrame()

        score = int(summary.get("score", projection_score if projection_score is not None else 0) or 0)
        label = summary.get("label", projection_label or "Needs Review")
        score_fill = max(0, min(100, score))
        retire_age = int(summary.get("retire_age", 0) or 0)
        current_age = int(summary.get("current_age", 0) or 0)
        end_age = int(summary.get("end_age", 90) or 90)
        years_to_retire = max(retire_age - current_age, 0)
        annual_spending = float(summary.get("annual_spending", 0) or 0)
        annual_income = float(summary.get("annual_income", 0) or 0)
        annual_gap = max(annual_spending - annual_income, 0)
        income_coverage = float(summary.get("income_coverage", 0) or 0)
        max_wr = float(summary.get("rough_wr", 0) or 0)
        ending_portfolio = float(summary.get("ending_portfolio", 0) or 0)
        unmet_need = float(summary.get("unmet_need", 0) or 0)

        if not projection_df.empty:
            retired_rows = projection_df[projection_df["Age"] >= retire_age] if retire_age > 0 else projection_df
            portfolio_at_retirement = float(projection_df.loc[projection_df["Age"] >= retire_age, "Start Total"].iloc[0]) if retire_age > 0 and not projection_df.loc[projection_df["Age"] >= retire_age].empty else float(projection_df["Start Total"].iloc[0])
            total_withdrawals = float(projection_df["Portfolio Withdrawal"].sum()) if "Portfolio Withdrawal" in projection_df else 0
            total_federal_tax = float(projection_df["Estimated Federal Tax"].sum()) if "Estimated Federal Tax" in projection_df else 0
            first_shortfall_age = None
            if "Unmet Need" in projection_df and (projection_df["Unmet Need"] > 0).any():
                first_shortfall_age = int(projection_df.loc[projection_df["Unmet Need"] > 0, "Age"].iloc[0])
            rmd_total = float(projection_df["RMD Required"].sum()) if "RMD Required" in projection_df else 0
            conversion_total = float(projection_df["Roth Conversion"].sum()) if "Roth Conversion" in projection_df else 0
        else:
            portfolio_at_retirement = float(summary.get("total_assets", 0) or 0)
            total_withdrawals = 0
            total_federal_tax = 0
            first_shortfall_age = None
            rmd_total = 0
            conversion_total = 0

        if score >= 85:
            executive_summary = (
                "This retirement blueprint appears strong based on the current inputs. The main planning focus should shift from 'Can I retire?' "
                "to 'How do I make this more tax-efficient, resilient, and comfortable?'"
            )
        elif score >= 70:
            executive_summary = (
                "This blueprint appears workable, but it deserves stress testing. The plan may be sensitive to market returns, early-retirement spending, "
                "healthcare costs, or tax assumptions."
            )
        elif score >= 55:
            executive_summary = (
                "This blueprint is possible but not yet comfortable. A few targeted changes could materially improve the plan, especially around spending, "
                "retirement age, savings, guaranteed income, or cash-bucket protection."
            )
        else:
            executive_summary = (
                "This blueprint needs improvement before it should be treated as a confident retirement plan. The highest-impact levers are usually delaying retirement, "
                "lowering spending, increasing savings, and improving income coverage."
            )

        strengths = []
        risks = []
        next_steps = []

        if years_to_retire >= 5:
            strengths.append(f"You have about {years_to_retire} years before the target retirement age, giving the plan time to benefit from continued savings and compounding.")
        else:
            risks.append("The target retirement date is close, so the plan has less time to recover from market declines or unexpected expenses.")

        if income_coverage >= 0.70:
            strengths.append("Non-portfolio income covers a large share of spending, reducing pressure on investments.")
        elif income_coverage >= 0.40:
            strengths.append("Non-portfolio income covers a meaningful share of spending.")
        else:
            risks.append("Income coverage is low, meaning more of retirement spending depends on portfolio withdrawals.")

        if max_wr <= 0.04 and annual_spending > 0:
            strengths.append("The estimated maximum withdrawal rate is in a conservative range.")
        elif max_wr <= 0.06 and annual_spending > 0:
            risks.append("Withdrawal pressure is moderate. This can work, but it should be tested against poor early market returns.")
        elif annual_spending > 0:
            risks.append("Withdrawal pressure is high. The plan may be vulnerable if early retirement years include weak market returns.")

        if float(summary.get("cash", 0) or 0) >= annual_spending * 2 and annual_spending > 0:
            strengths.append("Bucket 1 / cash appears to provide at least two years of spending coverage.")
        elif annual_spending > 0:
            risks.append("Bucket 1 / cash may be light. Consider building a 2–4 year safer-spending reserve before retirement.")

        if float(summary.get("traditional", 0) or 0) > max(float(summary.get("roth", 0) or 0) * 3, 250000):
            risks.append("Traditional retirement assets are much larger than Roth assets, which can create future RMD and tax-management pressure.")
            next_steps.append("Run Roth conversion scenarios for the gap years between retirement and Social Security / RMDs.")

        if unmet_need > 0:
            risks.append(f"The projection shows an estimated unmet need of {money(unmet_need)} over the plan period.")
            next_steps.append("Test a lower-spending scenario and a later-retirement scenario to identify the smallest change that fixes the shortfall.")

        if first_shortfall_age:
            risks.append(f"The first projected shortfall appears around age {first_shortfall_age}.")

        next_steps.extend(recommendations[:5])
        if not next_steps:
            next_steps = [
                "Stress test the plan with lower returns, higher inflation, and higher healthcare costs.",
                "Review Social Security timing to compare lifetime income and survivor-benefit tradeoffs.",
                "Review tax-efficient withdrawal order across taxable, traditional, and Roth accounts.",
            ]

        # Cover / hero
        story = []
        hero = Table(
            [[
                Paragraph("Retirement Blueprint 101", styles["RBWhiteTitle"]),
                Paragraph(f"Blueprint Score<br/><font size='24'><b>{score}/100</b></font><br/>{esc(label)}", styles["RBWhiteBody"]),
            ], [
                Paragraph(esc(name), styles["RBWhiteBody"]),
                Paragraph("Educational retirement-readiness report", styles["RBWhiteBody"]),
            ]],
            colWidths=[5.0 * inch, 2.0 * inch],
            rowHeights=[0.70 * inch, 0.35 * inch],
        )
        hero.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1D4ED8")),
            ("BOX", (0, 0), (-1, -1), 1.0, colors.HexColor("#1D4ED8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#60A5FA")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(hero)
        story.append(Spacer(1, 0.18 * inch))

        story.append(Paragraph("Executive Summary", styles["RBSection"]))
        story.append(para(executive_summary))
        story.append(para(
            f"Based on the current assumptions, the model estimates {money(portfolio_at_retirement)} at the target retirement age of {retire_age}, "
            f"{money(ending_portfolio)} remaining at age {end_age}, and a maximum estimated withdrawal rate of {pct(max_wr)}. "
            f"Annual spending is modeled at {money(annual_spending)}, with {money(annual_income)} of average annual non-portfolio income."
        ))

        # Color score bar
        score_table = Table(
            [[Paragraph("Readiness Score", styles["RBCardLabel"]), Paragraph(f"{score}/100", styles["RBCardValue"]), Paragraph(label, styles["RBCardLabel"])]],
            colWidths=[2.0 * inch, 2.5 * inch, 2.5 * inch],
            rowHeights=[0.40 * inch],
        )
        score_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#BFDBFE")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TEXTCOLOR", (1, 0), (1, 0), status_color(score)),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 0.12 * inch))

        card_data = [
            [Paragraph("Current Age", styles["RBCardLabel"]), Paragraph("Retire Age", styles["RBCardLabel"]), Paragraph("Plan Until", styles["RBCardLabel"]), Paragraph("Assets Today", styles["RBCardLabel"])],
            [Paragraph(str(current_age), styles["RBCardValue"]), Paragraph(str(retire_age), styles["RBCardValue"]), Paragraph(str(end_age), styles["RBCardValue"]), Paragraph(money(summary.get("total_assets", 0)), styles["RBCardValue"])],
            [Paragraph("At Retirement", styles["RBCardLabel"]), Paragraph("Ending Portfolio", styles["RBCardLabel"]), Paragraph("Annual Gap", styles["RBCardLabel"]), Paragraph("Max Withdrawal", styles["RBCardLabel"])],
            [Paragraph(money(portfolio_at_retirement), styles["RBCardValue"]), Paragraph(money(ending_portfolio), styles["RBCardValue"]), Paragraph(money(annual_gap), styles["RBCardValue"]), Paragraph(pct(max_wr), styles["RBCardValue"])],
        ]
        cards = Table(card_data, colWidths=[1.75 * inch] * 4, rowHeights=[0.24 * inch, 0.42 * inch, 0.24 * inch, 0.42 * inch])
        cards.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.50, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(cards)

        story.append(Paragraph("What Is Helping the Plan", styles["RBSection"]))
        for item in (strengths or ["No major strengths were identified yet because the inputs are still incomplete."]):
            story.append(bullet(item))

        story.append(Paragraph("Main Risks / Watch Items", styles["RBSection"]))
        for item in (risks or ["No major red flags were identified from the current inputs. Keep stress-testing before making final retirement decisions."]):
            story.append(bullet(item))

        story.append(Paragraph("Recommended Next Moves", styles["RBSection"]))
        for item in next_steps[:8]:
            story.append(bullet(item))

        story.append(PageBreak())
        story.append(Paragraph("Detailed Snapshot", styles["RBSection"]))
        snapshot_rows = [
            ["Category", "Value", "Why it matters"],
            ["Traditional retirement assets", money(summary.get("traditional", 0)), "Taxable later; drives future RMD planning"],
            ["Roth assets", money(summary.get("roth", 0)), "Tax-free flexibility later"],
            ["Taxable brokerage", money(summary.get("taxable", 0)), "Useful bridge account before 59½ / Medicare"],
            ["Bucket 1 / cash", money(summary.get("cash", 0)), "Helps reduce sequence-of-return risk"],
            ["Monthly spending", money(summary.get("monthly_spending", 0)), "Largest driver of retirement readiness"],
            ["Annual spending", money(annual_spending), "Used to estimate withdrawal needs"],
            ["Annual income", money(annual_income), "Reduces portfolio withdrawals"],
            ["Income coverage", pct(income_coverage), "Share of spending covered by income"],
            ["Total projected withdrawals", money(total_withdrawals), "Total portfolio withdrawals over the plan"],
            ["Estimated federal tax", money(total_federal_tax), "Educational estimate only"],
        ]
        snapshot_table = Table(snapshot_rows, colWidths=[2.0 * inch, 1.45 * inch, 3.55 * inch], repeatRows=1)
        snapshot_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DBEAFE")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFFFFF")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.2),
            ("LEADING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(snapshot_table)

        story.append(Paragraph("Planning Assumptions", styles["RBSection"]))
        assumptions = [
            ["Assumption", "Current Setting"],
            ["Growth return", pct(summary.get("growth_return", 0))],
            ["Inflation", pct(summary.get("inflation", 0))],
            ["Safe / Bucket 1 return", pct(summary.get("safe_return", 0))],
            ["Bucket 1 years", f"{float(summary.get('bucket1_years', 0) or 0):.1f}"],
            ["Annual Roth conversion", money(summary.get("annual_conversion", 0))],
            ["RMDs estimated", "Yes, when applicable" if rmd_total > 0 else "No RMD shown in this projection"],
            ["Roth conversions modeled", money(conversion_total)],
        ]
        assumption_table = Table(assumptions, colWidths=[3.5 * inch, 3.5 * inch], repeatRows=1)
        assumption_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCFCE7")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(assumption_table)

        if not projection_df.empty:
            story.append(Paragraph("Projection Checkpoints", styles["RBSection"]))
            checkpoint_ages = sorted(set([current_age, retire_age, 62, 65, 67, 70, end_age]))
            checkpoint_rows = [["Age", "Start Balance", "End Balance", "Spending", "Income", "From Portfolio", "Est. Tax"]]
            for age in checkpoint_ages:
                match = projection_df[projection_df["Age"] == age]
                if match.empty:
                    continue
                r = match.iloc[0]
                checkpoint_rows.append([
                    str(int(r["Age"])),
                    money(r.get("Start Total", 0)),
                    money(r.get("End Total", 0)),
                    money(r.get("Total Spending", 0)),
                    money(r.get("Total Non-Portfolio Income", 0)),
                    money(r.get("Portfolio Withdrawal", 0)),
                    money(r.get("Estimated Federal Tax", 0)),
                ])
            if len(checkpoint_rows) > 1:
                checkpoint_table = Table(checkpoint_rows, colWidths=[0.55 * inch, 1.05 * inch, 1.05 * inch, 1.05 * inch, 1.05 * inch, 1.1 * inch, 1.05 * inch], repeatRows=1)
                checkpoint_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E0F2FE")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.append(checkpoint_table)

        story.append(Spacer(1, 0.15 * inch))
        story.append(para(
            "Important: This report is an educational estimate. It is not financial, tax, legal, investment, or insurance advice. "
            "Before making retirement decisions, validate assumptions with qualified financial, tax, and legal professionals.",
            "RBSmall",
        ))

        def add_page_number(canvas, doc_obj):
            canvas.saveState()
            canvas.setFillColor(colors.HexColor("#64748B"))
            canvas.setFont("Helvetica", 8)
            canvas.drawString(0.45 * inch, 0.28 * inch, "Retirement Blueprint 101")
            canvas.drawRightString(8.05 * inch, 0.28 * inch, f"Page {doc_obj.page}")
            canvas.restoreState()

        doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
        buffer.seek(0)
        return buffer.getvalue()

    def blank_scenario_data():
        data = {k: v for k, v in defaults.items()}
        for k, _ in budget_keys:
            data[k] = 0
        data["income_sources_df"] = []
        return data

    if not user:
        st.info("Log in to save and load retirement scenarios.")
    else:
        st.subheader("Save Current Scenario")

        save_col1, save_col2 = st.columns([5, 1.25])
        with save_col1:
            scenario_name = st.text_input("Scenario name", "My Retirement Plan", label_visibility="visible")
        with save_col2:
            st.write("")
            st.write("")
            save_clicked = st.button("💾 Save Scenario", use_container_width=True, type="primary")

        if save_clicked:
            try:
                scenario_data = get_scenario_data()
                save_scenario(user, scenario_name, scenario_data)
                st.success("Scenario saved.")
                st.rerun()
            except Exception as e:
                st.error(f"Scenario save failed: {e}")

        st.divider()

        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.subheader("Your Saved Scenarios")
        with col_b:
            if st.button("⟳ Refresh", use_container_width=True):
                st.rerun()

        try:
            scenarios = load_scenarios(user)
        except Exception as e:
            st.error(f"Could not load scenarios: {e}")
            scenarios = []

        if not scenarios:
            st.info("No saved scenarios yet.")
        else:
            # Scenario Comparison panel
            if st.session_state.compare_scenarios:
                st.markdown("### Scenario Comparison")
                st.caption("Compare your saved retirement plans side by side.")

                compare_items = []
                for sid, item in st.session_state.compare_scenarios.items():
                    data = item["data"]
                    s = scenario_summary_from_data(data)
                    compare_items.append({
                        "id": sid,
                        "name": item["name"],
                        "summary": s,
                    })

                best = max(
                    compare_items,
                    key=lambda x: (
                        x["summary"]["score"],
                        x["summary"]["income_coverage"],
                        x["summary"]["total_assets"],
                    )
                )

                st.success(
                    f"Best current option: **{best['name']}** "
                    f"with an RTV score of **{best['summary']['score']}** "
                    f"({best['summary']['label']})."
                )

                card_cols = st.columns(min(len(compare_items), 3))
                for i, item in enumerate(compare_items):
                    s = item["summary"]
                    with card_cols[i % len(card_cols)]:
                        with st.container(border=True):
                            st.subheader(item["name"])
                            st.metric("Blueprint Score", f"{s['score']}/100", s["label"])
                            st.progress(s["score"] / 100)
                            st.write(f"Retire Age: **{s['retire_age']}**")
                            st.write(f"Total Assets: **{money(s['total_assets'])}**")
                            st.write(f"Monthly Spending: **{money(s['monthly_spending'])}**")
                            st.write(f"Annual Income: **{money(s['annual_income'])}**")
                            st.write(f"Income Coverage: **{pct(s['income_coverage'])}**")
                            st.write(f"Max Withdrawal Rate: **{pct(s['rough_wr'])}**")

                compare_rows = []
                for item in compare_items:
                    s = item["summary"]
                    compare_rows.append({
                        "Scenario": item["name"],
                        "Blueprint Score": s["score"],
                        "Status": s["label"],
                        "Retire Age": s["retire_age"],
                        "Plan Until": s["end_age"],
                        "Total Assets": money(s["total_assets"]),
                        "Monthly Spending": money(s["monthly_spending"]),
                        "Annual Income": money(s["annual_income"]),
                        "Income Coverage": pct(s["income_coverage"]),
                        "Max Withdrawal Rate": pct(s["rough_wr"]),
                    })

                st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)

                if len(compare_items) >= 2:
                    sorted_items = sorted(compare_items, key=lambda x: x["summary"]["score"], reverse=True)
                    top = sorted_items[0]
                    bottom = sorted_items[-1]
                    score_gap = top["summary"]["score"] - bottom["summary"]["score"]

                    st.markdown("#### What Changed?")
                    headline, insights = explain_scenario_changes(top["summary"], bottom["summary"])
                    st.success(headline)
                    for insight in insights:
                        st.write(f"• {insight}")

                    st.info(
                        f"**{top['name']}** currently scores **{score_gap} points higher** than "
                        f"**{bottom['name']}**."
                    )

                clear_col, note_col = st.columns([1, 4])
                with clear_col:
                    if st.button("Clear Compare", use_container_width=True):
                        st.session_state.compare_scenarios = {}
                        st.rerun()
                with note_col:
                    st.caption("Tip: compare 2 or 3 plans for the cleanest readout.")

                st.divider()

            for idx, scenario in enumerate(scenarios):
                data = scenario["scenario_data"]
                summary = scenario_summary_from_data(data)
                sid = str(scenario["id"])
                is_selected = sid in st.session_state.compare_scenarios
                selected_text = "Selected" if is_selected else ""
                recommendations = generate_recommendations_for_summary(summary)
                saved_display_time = format_saved_datetime(scenario.get("created_at", ""))

                expander_label = f"{scenario['scenario_name']}  •  Saved {saved_display_time}  •  {summary['label']}"
                with st.expander(expander_label, expanded=(idx == 0)):
                    st.markdown(
                        f"""
                        <div class="scenario-card-header">
                            <div class="scenario-title-wrap">
                                <span class="scenario-title">{scenario['scenario_name']}</span>\n                                <span class="{summary['badge']}">{summary['label']}</span>
                                {"<span class='badge-current'>Current</span>" if idx == 0 else ""}
                                {f"<span class='badge-work'>{selected_text}</span>" if selected_text else ""}
                            
                            
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    m1, m2, m3, m4, m5, m6 = st.columns([1, 1, 1.15, 1.15, 1.15, 0.95])
                    m1.metric("🗓️ Retire Age", summary["retire_age"])
                    m2.metric("👥 Plan Until", summary["end_age"])
                    m3.metric("💵 Total Assets", money(summary["total_assets"]))
                    m4.metric("🛒 Monthly Spending", money(summary["monthly_spending"]))
                    m5.metric("💼 Income Annual", money(summary["annual_income"]))

                    with m6:
                        st.markdown("Blueprint Score")
                        st.markdown(
                            f"<div class='{summary['score_class']}'>{summary['score']}</div>"
                            f"<div class='tiny-caption'>{summary['label']}</div>",
                            unsafe_allow_html=True
                        )

                    st.divider()

                    left, middle, right = st.columns([1.25, 1.05, 1.15])

                    with left:
                        st.markdown("<div class='section-title'>Asset Breakdown</div>", unsafe_allow_html=True)

                        asset_rows = pd.DataFrame({
                            "Account": ["Traditional", "Roth", "Taxable", "Cash / Bucket 1"],
                            "Amount": [summary["traditional"], summary["roth"], summary["taxable"], summary["cash"]],
                        })
                        asset_rows = asset_rows[asset_rows["Amount"] > 0]

                        if not asset_rows.empty:
                            fig_saved, ax_saved = plt.subplots(figsize=(3.25, 3.25))
                            wedges, _ = ax_saved.pie(
                                asset_rows["Amount"],
                                startangle=90,
                                wedgeprops=dict(width=0.42)
                            )
                            ax_saved.axis("equal")
                            ax_saved.legend(
                                wedges,
                                asset_rows["Account"],
                                title="Accounts",
                                loc="center left",
                                bbox_to_anchor=(1.0, 0.5),
                                fontsize=8
                            )
                            st.pyplot(fig_saved, use_container_width=True)

                            st.caption("Account values by color")
                            for _, row in asset_rows.iterrows():
                                pct_val = row["Amount"] / summary["total_assets"] if summary["total_assets"] > 0 else 0
                                st.markdown(
                                    f"""
                                    <div class="kv-row">
                                        <span class="kv-left">{row['Account']}</span>
                                        <span class="kv-right">{money(row['Amount'])} ({pct(pct_val)})</span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                        else:
                            st.info("No asset balances saved yet.")

                    with middle:
                        st.markdown("<div class='section-title'>Key Assumptions</div>", unsafe_allow_html=True)
                        rows = [
                            ("↗ Growth Return", pct(summary["growth_return"])),
                            ("🔥 Inflation", pct(summary["inflation"])),
                            ("🛡️ Safe Return", pct(summary["safe_return"])),
                            ("🗓️ Bucket 1 Years", f"{summary['bucket1_years']:.1f}"),
                            ("↔ Roth Conversion", money(summary["annual_conversion"])),
                        ]

                        for label, value in rows:
                            st.markdown(
                                f"""
                                <div class="kv-row">
                                    <span class="kv-left">{label}</span>
                                    <span class="kv-right">{value}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    with right:
                        st.markdown("<div class='section-title'>Other Income Annual</div>", unsafe_allow_html=True)
                        st.markdown(
                            f"""
                            <div class="kv-row">
                                <span class="kv-left">Social Security</span>
                                <span class="kv-right">{money(summary['user_ss'] + summary['spouse_ss'])}</span>
                            </div>
                            <div class="kv-row">
                                <span class="kv-left">Other Income</span>
                                <span class="kv-right">{money(summary['simple_income'])}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.divider()
                        income_col, wr_col = st.columns(2)
                        income_col.metric("Income Coverage", pct(summary["income_coverage"]))
                        wr_col.metric("Max Withdrawal Rate", pct(summary["rough_wr"]))

                    with st.expander("AI Recommendations for This Scenario"):
                        st.caption("Educational only. These suggestions are not financial, tax, legal, insurance, or investment advice.")

                        st.markdown("**Quick rule-based suggestions**")
                        for rec in recommendations:
                            st.write(f"- {rec}")

                        st.divider()

                        ai_key = f"ai_recommendation_{sid}"

                        if st.button("Generate AI Recommendation", key=f"generate_ai_{sid}", use_container_width=True):
                            with st.spinner("Generating AI recommendation..."):
                                st.session_state.saved_ai_recommendations[ai_key] = generate_ai_recommendation_for_saved_scenario(
                                    scenario["scenario_name"],
                                    summary,
                                    recommendations
                                )

                        if ai_key in st.session_state.saved_ai_recommendations:
                            st.markdown("**AI-generated scenario review**")
                            st.markdown(st.session_state.saved_ai_recommendations[ai_key])

                            if st.button("Clear AI Recommendation", key=f"clear_ai_{sid}", use_container_width=True):
                                st.session_state.saved_ai_recommendations.pop(ai_key, None)
                                st.rerun()
                        else:
                            st.info("Click the button to generate a plain-English AI review for this saved scenario.")

                    b1, b2, b3, b4, b5 = st.columns([1, 1, 1, 1, 1])

                    with b1:
                        if st.button("↥ Load This Scenario", key=f"load_{sid}", use_container_width=True, type="primary"):
                            apply_scenario_data(data)
                            st.success("Scenario loaded.")
                            st.rerun()

                    with b2:
                        compare_label = "Remove Compare" if is_selected else "⚖ Compare"
                        if st.button(compare_label, key=f"compare_{sid}", use_container_width=True):
                            if is_selected:
                                st.session_state.compare_scenarios.pop(sid, None)
                            else:
                                st.session_state.compare_scenarios[sid] = {
                                    "name": scenario["scenario_name"],
                                    "data": data,
                                }
                            st.rerun()

                    with b3:
                        if st.button("⧉ Duplicate", key=f"duplicate_{sid}", use_container_width=True):
                            try:
                                copy_name = f"{scenario['scenario_name']} Copy"
                                save_scenario(user, copy_name, data)
                                st.success("Scenario duplicated.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Duplicate failed: {e}")

                    with b4:
                        pdf_bytes = build_pdf_report_bytes(
                            scenario["scenario_name"],
                            data,
                            summary,
                            recommendations
                        )
                        st.download_button(
                            "PDF Report",
                            data=pdf_bytes,
                            file_name=f"{scenario['scenario_name'].replace(' ', '_')}_report.pdf",
                            mime="application/pdf",
                            key=f"pdf_{sid}",
                            use_container_width=True
                        )

                    with b5:
                        confirm_key = f"confirm_delete_{sid}"

                        if st.session_state.get(confirm_key, False):
                            if st.button("Confirm Delete", key=f"confirm_delete_btn_{sid}", use_container_width=True):
                                try:
                                    supabase.table("retirement_scenarios").delete().eq("id", scenario["id"]).eq("user_id", user.id).execute()
                                    st.session_state.compare_scenarios.pop(sid, None)
                                    st.session_state[confirm_key] = False
                                    st.success("Scenario deleted.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Delete failed: {e}")

                            if st.button("Cancel", key=f"cancel_delete_btn_{sid}", use_container_width=True):
                                st.session_state[confirm_key] = False
                                st.rerun()
                        else:
                            if st.button("🗑 Delete", key=f"delete_{sid}", use_container_width=True):
                                st.session_state[confirm_key] = True
                                st.rerun()

            st.divider()

            t1, t2, t3, t4 = st.columns([1.2, 1, 1, 1])
            with t1:
                if st.button("＋ Create New Blank Scenario", use_container_width=True):
                    try:
                        save_scenario(user, "New Blank Scenario", blank_scenario_data())
                        st.success("Blank scenario created.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Blank scenario failed: {e}")

            with t2:
                if st.button("Conservative", use_container_width=True):
                    try:
                        save_scenario(user, "Conservative Plan", make_template_data("Conservative"))
                        st.success("Conservative scenario created.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Template failed: {e}")

            with t3:
                if st.button("Base", use_container_width=True):
                    try:
                        save_scenario(user, "Base Plan", make_template_data("Base"))
                        st.success("Base scenario created.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Template failed: {e}")

            with t4:
                if st.button("Aggressive", use_container_width=True):
                    try:
                        save_scenario(user, "Aggressive Plan", make_template_data("Aggressive"))
                        st.success("Aggressive scenario created.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Template failed: {e}")



if active_page == PAGE_NAMES[10]:
    render_page_shell(
        "Places to Retire",
        "Find retirement locations that fit your money, lifestyle, healthcare needs, climate preferences, and tax situation.",
        "📍"
    )
    page_help(
        "Places to Retire",
        "This page starts with a simple state-level ranking, then lets you personalize the results using taxes, cost, healthcare, lifestyle, climate, and city-level preferences."
    )

    st.markdown("""
    <div class="rb-insight-card">
      <div class="rb-insight-kicker">Location Planning</div>
      <div class="rb-insight-title">Where you retire can change how long your money lasts</div>
      <div class="rb-insight-copy">
        Taxes, housing costs, healthcare access, insurance, climate, and lifestyle can all change your retirement picture.
        Start with the best overall matches, then adjust the priorities to fit what matters most to you.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.warning(
        "Educational estimate only. State taxes, property taxes, insurance, healthcare access, and cost of living change over time. Verify details before making relocation or tax decisions."
    )

    places_df = get_phase1_retirement_places_data().copy()

    # Basic ranking controls
    st.subheader("Best Places to Retire Snapshot")
    st.caption("Start here. This gives a quick ranking before you personalize the results.")

    c1, c2 = st.columns([1, 2])
    with c1:
        priority = st.selectbox(
            "What do you want to optimize for?",
            [
                "Balanced overall",
                "Lowest taxes",
                "Lowest cost",
                "Healthcare access",
                "Lifestyle / weather",
            ],
            help="This changes the starting ranking. You can personalize the weights below."
        )
    with c2:
        st.markdown("""
        <div class="rb-next-box">
          <div class="rb-next-heading">How to use this page</div>
          <div class="rb-muted">
            First, look at the best overall match. Then compare the top states and adjust the personal priorities below.
            A high score does not mean a state is perfect. It means it may be worth a closer look.
          </div>
        </div>
        """, unsafe_allow_html=True)

    ranked_df = filter_places_data(places_df, priority).reset_index(drop=True)
    ranked_df.insert(0, "Rank", ranked_df.index + 1)
    ranked_df["Fit Label"] = ranked_df["Overall Score"].map(score_badge)

    top = ranked_df.iloc[0]
    top_low_tax = filter_places_data(places_df, "Lowest taxes").reset_index(drop=True).iloc[0]
    top_health = filter_places_data(places_df, "Healthcare access").reset_index(drop=True).iloc[0]
    top_lifestyle = filter_places_data(places_df, "Lifestyle / weather").reset_index(drop=True).iloc[0]

    st.markdown(f"""
    <div class="rb-card-grid">
      <div class="rb-card">
        <div class="rb-card-top"><div class="rb-card-label">Best Overall Match</div><div class="rb-icon">📍</div></div>
        <div class="rb-card-value">{top['State']}</div>
        <div class="rb-card-note">Score: {int(top['Overall Score'])}/100 — {top['Fit Label']}</div>
      </div>
      <div class="rb-card">
        <div class="rb-card-top"><div class="rb-card-label">Best Low-Tax Option</div><div class="rb-icon">$</div></div>
        <div class="rb-card-value">{top_low_tax['State']}</div>
        <div class="rb-card-note">Best starting point if taxes matter most.</div>
      </div>
      <div class="rb-card">
        <div class="rb-card-top"><div class="rb-card-label">Best Healthcare Access</div><div class="rb-icon">✓</div></div>
        <div class="rb-card-value">{top_health['State']}</div>
        <div class="rb-card-note">Strong starting point for healthcare access.</div>
      </div>
      <div class="rb-card">
        <div class="rb-card-top"><div class="rb-card-label">Best Lifestyle / Weather</div><div class="rb-icon">☀️</div></div>
        <div class="rb-card-value">{top_lifestyle['State']}</div>
        <div class="rb-card-note">Good fit for climate and retirement lifestyle.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Top state rankings")
    st.caption("These are broad state-level rankings. Use them as a shortlist, not a final answer.")

    display = ranked_df.head(10).copy()
    display["Best For"] = display["Best Fit"]
    display["Watch Out For"] = display["Watch Outs"]
    state_table = display[[
        "Rank",
        "State",
        "Overall Score",
        "Fit Label",
        "Best For",
        "Watch Out For",
        "Example Places",
    ]]
    st.dataframe(state_table, use_container_width=True, hide_index=True, height=390)

    with st.expander("What the scores mean", expanded=False):
        explain = pd.DataFrame([
            ["Taxes", "Affects how much retirement income you keep."],
            ["Cost of living", "Lower costs can make the same savings last longer."],
            ["Healthcare", "Access becomes more important as you age."],
            ["Lifestyle", "Retirement should fit how you actually want to live."],
            ["Climate", "Weather, snowbird plans, and seasonal comfort matter."],
        ], columns=["Factor", "Why It Matters"])
        st.dataframe(explain, use_container_width=True, hide_index=True)

    # Personalized ranking
    st.divider()
    st.subheader("Personalize the ranking")
    st.caption("Tell the app what matters most. This turns the broad state list into a more personal shortlist.")

    default_ss = float(st.session_state.user_ss or 0)
    if st.session_state.has_spouse:
        default_ss += float(st.session_state.spouse_ss or 0)

    default_spending = annual_household_spending() + float(st.session_state.healthcare or 0)
    if st.session_state.has_spouse:
        default_spending += float(st.session_state.spouse_healthcare or 0)

    default_other_income = float(st.session_state.simple_income or 0)
    estimated_portfolio_need = max(default_spending - default_ss - default_other_income, 0)

    with st.expander("Your money assumptions", expanded=True):
        i1, i2, i3 = st.columns(3)
        ss_income = i1.number_input(
            "Annual Social Security income",
            min_value=0,
            value=int(default_ss),
            step=1000,
            help="Estimated annual household Social Security income."
        )
        pretax_withdrawals = i2.number_input(
            "Annual pre-tax withdrawals",
            min_value=0,
            value=int(estimated_portfolio_need),
            step=1000,
            help="Estimated annual withdrawals from traditional 401(k)/IRA accounts."
        )
        pension_other_income = i3.number_input(
            "Annual pension / other taxable income",
            min_value=0,
            value=int(default_other_income),
            step=1000,
            help="Pension, rental income, annuity income, side income, or other taxable income."
        )

        i1, i2, i3 = st.columns(3)
        taxable_income = i1.number_input(
            "Annual taxable brokerage income",
            min_value=0,
            value=0,
            step=1000,
            help="Estimated dividends, interest, or realized capital gains from taxable accounts."
        )
        annual_spending_input = i2.number_input(
            "Annual household spending",
            min_value=0,
            value=int(default_spending),
            step=1000,
            help="Used to estimate sales tax exposure. The model assumes a portion of spending is taxable."
        )
        home_value = i3.number_input(
            "Estimated home value",
            min_value=0,
            value=400000,
            step=25000,
            help="Used to estimate property tax by state."
        )

    st.markdown("### What matters most to you?")
    w1, w2, w3, w4, w5 = st.columns(5)
    tax_weight = w1.slider("Taxes", 0, 10, 8)
    cost_weight = w2.slider("Cost", 0, 10, 7)
    healthcare_weight = w3.slider("Healthcare", 0, 10, 8)
    lifestyle_weight = w4.slider("Lifestyle", 0, 10, 7)
    climate_weight = w5.slider("Climate", 0, 10, 6)

    p1, p2, p3 = st.columns(3)
    preferred_states = p1.multiselect(
        "Preferred states, optional",
        sorted(places_df["State"].unique().tolist()),
        default=[],
        help="Adds a small boost to these states."
    )
    avoid_states = p2.multiselect(
        "States to avoid, optional",
        sorted(places_df["State"].unique().tolist()),
        default=[],
        help="Removes these states from the personalized ranking."
    )
    warm_weather_bonus = p3.checkbox(
        "Prefer warmer / snowbird-friendly weather",
        value=True,
        help="Adds a small boost to high climate-score states."
    )

    personalized_df = build_personalized_places_table(
        places_df,
        ss_income=ss_income,
        pretax_withdrawals=pretax_withdrawals,
        pension_other_income=pension_other_income,
        taxable_income=taxable_income,
        annual_spending=annual_spending_input,
        home_value=home_value,
    )

    total_weight = max(tax_weight + cost_weight + healthcare_weight + lifestyle_weight + climate_weight, 1)
    max_tax = max(float(personalized_df["Estimated Annual Tax"].max()), 1)
    min_tax = min(float(personalized_df["Estimated Annual Tax"].min()), max_tax)

    def _tax_drag_score(x):
        if max_tax == min_tax:
            return 100
        return max(0, min(100, 100 - ((float(x) - min_tax) / (max_tax - min_tax) * 100)))

    personalized_df["Personal Tax Score"] = personalized_df["Estimated Annual Tax"].apply(_tax_drag_score)
    personalized_df["Preference Fit Score"] = (
        personalized_df["Personal Tax Score"] * tax_weight
        + personalized_df["Cost Score"] * cost_weight
        + personalized_df["Healthcare Score"] * healthcare_weight
        + personalized_df["Lifestyle Score"] * lifestyle_weight
        + personalized_df["Climate Score"] * climate_weight
    ) / total_weight

    if warm_weather_bonus:
        personalized_df["Preference Fit Score"] += personalized_df["Climate Score"].apply(lambda x: 3 if x >= 80 else 0)

    if preferred_states:
        personalized_df.loc[personalized_df["State"].isin(preferred_states), "Preference Fit Score"] += 4

    if avoid_states:
        personalized_df = personalized_df[~personalized_df["State"].isin(avoid_states)]

    personalized_df["Preference Fit Score"] = personalized_df["Preference Fit Score"].clip(0, 100).round(0)
    personalized_df = personalized_df.sort_values("Preference Fit Score", ascending=False).reset_index(drop=True)
    personalized_df.insert(0, "Personal Rank", personalized_df.index + 1)

    if personalized_df.empty:
        st.warning("No states are left after your filters. Remove one or more avoided states.")
    else:
        best_personal = personalized_df.iloc[0]

        st.markdown(f"""
        <div class="rb-insight-card">
          <div class="rb-insight-kicker">Your Personalized Match</div>
          <div class="rb-insight-title">{best_personal['State']} looks like your strongest state-level fit</div>
          <div class="rb-insight-copy">
            Fit score: <b>{int(best_personal['Preference Fit Score'])}/100</b>.
            Estimated annual state/local tax: <b>{money(best_personal['Estimated Annual Tax'])}</b>.
            Use this as a shortlist starter, then compare cities and real housing/insurance costs.
          </div>
        </div>
        """, unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Top State", best_personal["State"])
        k2.metric("Fit Score", f"{int(best_personal['Preference Fit Score'])}/100")
        k3.metric("Est. Annual Tax", money(best_personal["Estimated Annual Tax"]))
        k4.metric("Effective Rate", pct(best_personal["Effective Tax Rate"]))

        personal_display = personalized_df.copy()
        for col in ["Estimated Annual Tax", "Income Tax", "Property Tax", "Sales Tax"]:
            personal_display[col] = personal_display[col].map(money)
        personal_display["Effective Tax Rate"] = personal_display["Effective Tax Rate"].map(pct)

        st.subheader("Personalized top states")
        st.dataframe(
            personal_display[
                [
                    "Personal Rank",
                    "State",
                    "Preference Fit Score",
                    "Estimated Annual Tax",
                    "Effective Tax Rate",
                    "Cost Score",
                    "Healthcare Score",
                    "Lifestyle Score",
                    "Climate Score",
                    "Example Places",
                    "Best Fit",
                ]
            ].head(12),
            use_container_width=True,
            hide_index=True,
            height=430
        )

        with st.expander("Show tax breakdown chart and deeper state comparison", expanded=False):
            st.pyplot(plot_personalized_tax_burden(personalized_df), use_container_width=True)

            compare_states = st.multiselect(
                "Choose states to compare",
                personalized_df["State"].tolist(),
                default=personalized_df["State"].head(3).tolist(),
                max_selections=5,
                key="optimized_compare_states"
            )

            if compare_states:
                phase3_compare_df = build_state_comparison_table(
                    places_df,
                    personalized_df.assign(**{"Personalized Score": personalized_df["Preference Fit Score"]}),
                    compare_states
                )

                if not phase3_compare_df.empty:
                    st.pyplot(plot_state_comparison_scores(phase3_compare_df), use_container_width=True)
                    st.pyplot(plot_state_tax_stack(phase3_compare_df), use_container_width=True)

                    phase3_display = phase3_compare_df.copy()
                    for col in ["Estimated Annual Tax", "Income Tax", "Property Tax", "Sales Tax"]:
                        phase3_display[col] = phase3_display[col].map(money)
                    phase3_display["Effective Tax Rate"] = phase3_display["Effective Tax Rate"].map(pct)

                    st.dataframe(
                        phase3_display[[
                            "State",
                            "Overall Score",
                            "Personalized Score",
                            "Estimated Annual Tax",
                            "Income Tax",
                            "Property Tax",
                            "Sales Tax",
                            "Effective Tax Rate",
                            "Cost Score",
                            "Healthcare Score",
                            "Lifestyle Score",
                            "Climate Score",
                            "Example Places",
                            "Watch Outs",
                        ]],
                        use_container_width=True,
                        hide_index=True
                    )

                    st.markdown("### Plain-English comparison notes")
                    for note in build_compare_narrative(phase3_compare_df):
                        st.markdown(f"- {note}")

        # City-level retirement location engine
        st.divider()
        st.subheader("City-level retirement matches")
        st.caption("State rankings are useful, but people retire in real places. This section compares starter cities and retirement areas.")

        city_df = get_phase3_city_places_data().copy()

        c1, c2, c3 = st.columns(3)
        with c1:
            city_state_filter = st.multiselect(
                "Filter cities by state",
                sorted(city_df["State"].unique().tolist()),
                default=[],
                key="optimized_city_state_filter",
                help="Leave blank to include all starter cities."
            )
        with c2:
            city_priority = st.selectbox(
                "City lifestyle priority",
                [
                    "Balanced",
                    "Golf / recreation",
                    "Healthcare",
                    "Lower cost",
                    "Coastal / warm lifestyle",
                    "Active adult community",
                ],
                key="optimized_city_priority"
            )
        with c3:
            golf_weight = st.slider(
                "Golf / recreation importance",
                min_value=0,
                max_value=10,
                value=7,
                key="optimized_golf_weight",
                help="Adds another preference factor for golf, outdoor recreation, and active lifestyle."
            )

        filtered_city_df = filter_city_places(city_df, city_state_filter, city_priority)

        location_weights = calculate_location_fit_profile(
            tax_weight=tax_weight,
            cost_weight=cost_weight,
            healthcare_weight=healthcare_weight,
            lifestyle_weight=lifestyle_weight,
            climate_weight=climate_weight,
            golf_weight=golf_weight,
        )

        personalized_for_compare = personalized_df.copy()
        personalized_for_compare["Personalized Score"] = personalized_for_compare["Preference Fit Score"]

        location_recommendations = build_retirement_location_recommendation_engine(
            filtered_city_df,
            personalized_for_compare,
            location_weights,
            preferred_states=preferred_states,
            avoid_states=avoid_states,
            wants_snowbird=warm_weather_bonus,
        )

        if location_recommendations.empty:
            st.warning("No city recommendations match the current filters. Widen the state filter or change the lifestyle priority.")
        else:
            top_place = location_recommendations.iloc[0]

            st.markdown(f"""
            <div class="rb-insight-card">
              <div class="rb-insight-kicker">Top City-Level Match</div>
              <div class="rb-insight-title">{top_place['Place']}, {top_place['State']}</div>
              <div class="rb-insight-copy">
                Fit score: <b>{int(top_place['Recommended Fit Score'])}/100</b>.
                Type: <b>{top_place['Type']}</b>.
                Estimated annual state/local tax: <b>{money(top_place['Estimated Annual State/Local Tax'])}</b>.
              </div>
            </div>
            """, unsafe_allow_html=True)

            location_display = location_recommendations.copy()
            location_display["Estimated Annual State/Local Tax"] = location_display["Estimated Annual State/Local Tax"].map(money)

            st.dataframe(
                location_display[[
                    "Place",
                    "State",
                    "Type",
                    "Recommended Fit Score",
                    "Estimated Annual State/Local Tax",
                    "Affordability",
                    "Healthcare",
                    "Lifestyle",
                    "Climate",
                    "Golf / Recreation",
                    "Why It Fits",
                    "Watch Outs",
                ]].head(12),
                use_container_width=True,
                hide_index=True,
                height=430
            )

            with st.expander("Show city chart and recommendation notes", expanded=False):
                st.pyplot(plot_location_engine_scores(location_recommendations), use_container_width=True)
                for note in build_location_recommendation_summary(location_recommendations):
                    st.markdown(f"- {note}")

            if warm_weather_bonus:
                snowbird_df = build_snowbird_recommendations(city_df, current_home_state="Michigan")
                if not snowbird_df.empty:
                    with st.expander("Snowbird shortlist", expanded=False):
                        snowbird_display = snowbird_df[[
                            "Place", "State", "Type", "Snowbird Fit Score", "Climate", "Lifestyle", "Golf / Recreation", "Snowbird Strategy", "Watch Outs"
                        ]].copy()
                        st.dataframe(snowbird_display, use_container_width=True, hide_index=True)

            # Save favorites
            st.divider()
            st.subheader("Save favorite retirement places")
            st.caption("Saved places stay in this session and are included in the Blueprint Report PDF.")

            if "saved_retirement_places" not in st.session_state:
                st.session_state.saved_retirement_places = []

            save_options = (location_recommendations["Place"] + ", " + location_recommendations["State"]).head(12).tolist()
            place_to_save = st.selectbox(
                "Choose a place to save",
                save_options,
                key="optimized_place_to_save"
            )

            s1, s2 = st.columns([1, 1])
            with s1:
                if st.button("Save Selected Place", type="primary", use_container_width=True, key="optimized_save_place_btn"):
                    place_name, state_name = place_to_save.split(", ", 1)
                    row = location_recommendations[
                        (location_recommendations["Place"] == place_name)
                        & (location_recommendations["State"] == state_name)
                    ].iloc[0].to_dict()

                    existing_keys = {f"{x.get('Place')}, {x.get('State')}" for x in st.session_state.saved_retirement_places}
                    if place_to_save not in existing_keys:
                        st.session_state.saved_retirement_places.append(row)
                        st.success(f"Saved {place_to_save}.")
                    else:
                        st.info(f"{place_to_save} is already saved.")

            with s2:
                if st.button("Clear Saved Places", use_container_width=True, key="optimized_clear_saved_places_btn"):
                    st.session_state.saved_retirement_places = []
                    st.success("Saved places cleared.")

            saved_places = st.session_state.get("saved_retirement_places", [])
            if saved_places:
                saved_df = pd.DataFrame(saved_places)
                saved_display = saved_df.copy()
                if "Estimated Annual State/Local Tax" in saved_display.columns:
                    saved_display["Estimated Annual State/Local Tax"] = saved_display["Estimated Annual State/Local Tax"].map(money)

                show_cols = [c for c in [
                    "Place", "State", "Type", "Recommended Fit Score", "Estimated Annual State/Local Tax",
                    "Healthcare", "Affordability", "Lifestyle", "Climate", "Golf / Recreation", "Why It Fits", "Watch Outs"
                ] if c in saved_display.columns]

                st.dataframe(saved_display[show_cols], use_container_width=True, hide_index=True)

                saved_csv = saved_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Saved Places CSV",
                    saved_csv,
                    "saved_retirement_places.csv",
                    "text/csv",
                    use_container_width=True,
                    key="optimized_saved_places_csv"
                )
                st.info("Saved places will appear in the next Blueprint Report PDF you generate.")
            else:
                st.info("No saved retirement places yet. Save a place from the city-level recommendations above.")

        csv = personalized_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Personalized Places CSV",
            csv,
            "personalized_places_to_retire.csv",
            "text/csv",
            use_container_width=True
        )

    st.caption("This page is educational and simplified. It does not replace professional tax, financial, legal, insurance, relocation, or real-estate advice.")



if active_page == PAGE_NAMES[11]:
    render_page_shell("Confidence Test", "Stress test your blueprint across many market paths to understand the probability of success and the range of possible outcomes.", "🎲")
    page_help(
        "Monte Carlo Simulator",
        "This page runs hundreds or thousands of randomized market-return paths to estimate how often the retirement plan survives. It helps show sequence-of-return risk and the range of possible ending portfolio balances."
    )

    st.caption("Tax estimates now include taxable Social Security when provisional income exceeds IRS thresholds. Roth and cash withdrawals are modeled as tax-free; taxable brokerage is still simplified until the capital-gains phase.")
    if not can_run:
        st.info("Complete required inputs first.")
    else:
        st.warning("Educational estimate only. Monte Carlo results depend heavily on the return, volatility, inflation, and spending assumptions you enter.")

        st.subheader("Simulation Settings")

        c1, c2, c3, c4 = st.columns(4)

        num_simulations = c1.number_input(
            "Number of simulations",
            min_value=100,
            max_value=2000,
            value=500,
            step=100,
            help="More simulations give a smoother estimate, but may run slower."
        )

        mean_return = c2.slider(
            "Average annual return",
            min_value=0.0,
            max_value=30.0,
            value=min(max(float(st.session_state.growth_return) * 100, 0.0), 30.0),
            step=0.25,
            format="%.2f%%",
            help="Expected average annual return for growth assets."
        ) / 100

        volatility = c3.slider(
            "Annual volatility",
            min_value=1.0,
            max_value=25.0,
            value=12.0,
            step=0.5,
            help="How much yearly returns vary. Higher volatility increases sequence risk."
        ) / 100

        seed = c4.number_input(
            "Random seed",
            min_value=1,
            max_value=99999,
            value=42,
            step=1,
            help="Keeps results repeatable. Change this to generate a different random set."
        )

        run_mc = st.button("Run Monte Carlo Simulation", type="primary", use_container_width=True)

        if run_mc:
            with st.spinner("Running Monte Carlo simulations..."):
                st.session_state.mc_result = run_monte_carlo_simulation(
                    int(num_simulations),
                    float(mean_return),
                    float(volatility),
                    int(seed)
                )

        if "mc_result" not in st.session_state:
            st.info("Click **Run Monte Carlo Simulation** to generate probability-of-success results.")
        else:
            mc = st.session_state.mc_result
            results_df = mc["results_df"]
            paths_df = mc["paths_df"]

            st.subheader("Monte Carlo Results")

            success_rate = mc["success_rate"]
            median_ending = mc["median_ending"]
            p10_ending = mc["p10_ending"]
            p90_ending = mc["p90_ending"]

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Probability of Success", pct(success_rate))
            m2.metric("Median Ending Portfolio", money(median_ending))
            m3.metric("10th Percentile Ending", money(p10_ending))
            m4.metric("90th Percentile Ending", money(p90_ending))

            st.progress(success_rate)

            if success_rate >= 0.90:
                st.success("Monte Carlo result: Strong probability of success under these assumptions.")
            elif success_rate >= 0.75:
                st.warning("Monte Carlo result: Moderate-to-good probability of success. Stress testing is still recommended.")
            elif success_rate >= 0.60:
                st.warning("Monte Carlo result: Borderline. Consider reducing spending, delaying retirement, or improving income coverage.")
            else:
                st.error("Monte Carlo result: High risk. The plan fails in many simulated market paths.")

            st.caption(
                "Success means the plan reaches the final planning age with money remaining and no unmet spending years."
            )

            st.subheader("Portfolio Path Range")
            st.pyplot(plot_monte_carlo_paths(paths_df, results_df), use_container_width=True)

            st.subheader("Ending Portfolio Distribution")
            st.pyplot(plot_monte_carlo_ending_distribution(results_df), use_container_width=True)

            st.subheader("Simulation Detail")

            detail = results_df.copy()
            detail["Success"] = detail["Success"].map(lambda x: "Success" if x else "Failed")
            detail["Ending Portfolio"] = detail["Ending Portfolio"].map(money)
            detail["Max Withdrawal Rate"] = detail["Max Withdrawal Rate"].map(pct)
            detail["Average Return"] = detail["Average Return"].map(pct)
            detail["Worst Year Return"] = detail["Worst Year Return"].map(pct)
            st.dataframe(detail.head(100), use_container_width=True, hide_index=True)

            csv = results_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Monte Carlo CSV",
                csv,
                "monte_carlo_results.csv",
                "text/csv",
                use_container_width=True
            )




if active_page == PAGE_NAMES[12]:
    render_page_shell("Stress Tests", "Try tougher scenarios like lower returns, higher spending, or inflation shocks to see where your plan bends or breaks.", "🛡️")

    st.caption("Tax estimates now include taxable Social Security when provisional income exceeds IRS thresholds. Roth and cash withdrawals are modeled as tax-free; taxable brokerage is still simplified until the capital-gains phase.")
    if not can_run:
        st.info("Complete required inputs first.")
    else:
        st.warning("Stress tests simulate difficult retirement conditions.")

        if st.button("Run Stress Tests", type="primary", use_container_width=True):
            if "stress_results_df" in st.session_state:
                del st.session_state.stress_results_df

            years = int(st.session_state.end_age) - int(st.session_state.current_age) + 1
            base_return = float(st.session_state.growth_return)

            stress_results = []

            stress_results.append(
                run_stress_test_scenario(
                    "Base Case",
                    forced_returns=[base_return] * years
                )
            )

            stress_results.append(
                run_stress_test_scenario(
                    "Bad First 3 Years",
                    forced_returns=[-0.20, -0.12, -0.08] + [base_return] * (years - 3)
                )
            )

            stress_results.append(
                run_stress_test_scenario(
                    "High Inflation",
                    inflation_override=0.06
                )
            )

            stress_results.append(
                run_stress_test_scenario(
                    "4% Returns",
                    forced_returns=[0.04] * years
                )
            )

            stress_results.append(
                run_stress_test_scenario(
                    "Healthcare Shock",
                    spending_multiplier=1.15
                )
            )

            stress_results.append(
                run_stress_test_scenario(
                    "Severe Recession",
                    forced_returns=[-0.30, -0.15, 0.00, 0.03] + [base_return] * (years - 4)
                )
            )

            st.session_state.stress_results_df = pd.DataFrame(stress_results)

        if "stress_results_df" in st.session_state:

            stress_df = st.session_state.stress_results_df.copy()

            # Safety: older cached stress-test results may not include these new columns.
            if "Lasts Until Age" not in stress_df.columns:
                stress_df["Lasts Until Age"] = int(st.session_state.end_age)
            if "Years Covered" not in stress_df.columns:
                stress_df["Years Covered"] = stress_df["Lasts Until Age"].astype(int) - int(st.session_state.current_age)

            st.subheader("Stress Test Summary")
            st.pyplot(plot_stress_test_chart(stress_df), use_container_width=True)

            display_df = stress_df.copy()

            display_df["Lasts Until Age"] = display_df["Lasts Until Age"].map(lambda x: int(x))
            display_df["Years Covered"] = display_df["Years Covered"].map(lambda x: max(int(x), 0))
            display_df["Ending Portfolio"] = display_df["Ending Portfolio"].map(money)
            display_df["Max Withdrawal Rate"] = display_df["Max Withdrawal Rate"].map(pct)
            display_df["Income Coverage"] = display_df["Income Coverage"].map(pct)

            st.caption("Lasts Until Age shows the first age where the plan fails, or the final plan age if it survives.")
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.markdown("""
### Stress Test Definitions

- **Base Case** → Uses your normal assumptions.
- **Bad First 3 Years** → Simulates retiring into a bear market.
- **High Inflation** → Uses 6% inflation.
- **4% Returns** → Assumes weaker long-term market returns.
- **Healthcare Shock** → Increases spending by 15%.
- **Severe Recession** → Simulates a major market crash and slow recovery.
""")



if active_page == PAGE_NAMES[13]:
    render_page_shell("Blueprint Report", "Create a shareable retirement blueprint you can save, print, or discuss with a spouse, advisor, or planner.", "📄")
    page_help(
        "PDF Report",
        "This page exports a visually polished retirement report with the plan summary, assumptions, dashboard charts, recommendations, Monte Carlo results, stress tests, and a projection snapshot."
    )

    st.caption("Tax estimates now include taxable Social Security when provisional income exceeds IRS thresholds. Roth and cash withdrawals are modeled as tax-free; taxable brokerage is still simplified until the capital-gains phase.")
    if not can_run:
        st.info("Complete required inputs first.")
    else:
        st.success("Ready to export a professional-looking premium retirement blueprint report.")
        render_premium_insight("Report insight", df, "general")
        st.warning("Educational purposes only. This report is not financial, tax, legal, insurance, or investment advice.")

        st.write("""
The PDF report includes:

- Blueprint Score and executive summary
- Key planning assumptions
- Portfolio, spending, income, and withdrawal charts
- Possible recommendations and planning observations
- Recommended actions to improve the score
- Spend-more analysis
- Premium scenario comparison
- Premium 2-bucket strategy summary
- Monte Carlo results, if already run
- Stress test results, if already run
- Projection snapshot
""")

        if "mc_result" not in st.session_state:
            st.warning("Monte Carlo has not been run yet. The PDF will include a placeholder for that section.")

        if "stress_results_df" not in st.session_state:
            st.warning("Stress tests have not been run yet. The PDF will include a placeholder for that section.")

        if st.button("Generate Blueprint Report", type="primary", use_container_width=True):
            with st.spinner("Creating report..."):
                st.session_state.pdf_report_bytes = build_pdf_report(df)

        if "pdf_report_bytes" in st.session_state:
            st.download_button(
                "Download Blueprint Report PDF",
                data=st.session_state.pdf_report_bytes,
                file_name="retirement_readiness_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )


if active_page == PAGE_NAMES[14]:
    render_page_shell("Blueprint Coach", "Ask follow-up questions, explore trade-offs, and get plain-English explanations of what your blueprint results mean.", "🤖")
    page_help(
        "AI Retirement Coach",
        "This chat explains the retirement numbers in plain English. It uses your current plan context, but it is educational only and not financial, tax, legal, insurance, or investment advice."
    )
    st.warning("Educational use only. This chat does not provide financial, tax, legal, insurance, or investment advice.")

    try:
        from openai import OpenAI
        api_key = st.secrets.get("OPENAI_API_KEY", "")
        if not api_key:
            st.info("Add your OpenAI API key in Streamlit Secrets to enable chat.")
            st.code('OPENAI_API_KEY = "your-api-key-here"', language="toml")
            st.stop()
        client = OpenAI(api_key=api_key)
    except Exception:
        st.error("OpenAI is not configured. Add OPENAI_API_KEY in Streamlit Secrets and openai in requirements.txt.")
        st.stop()

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if st.button("Clear chat"):
        st.session_state.chat_messages = []
        st.rerun()

    if can_run and not df.empty:
        rtv_score, rtv_label, rtv_reasons = calculate_rtv_score(df)

        plan_context = f"""
        Current age: {st.session_state.current_age}
        Retirement age: {st.session_state.retire_age}
        Plan-through age: {st.session_state.end_age}
        Traditional: {st.session_state.traditional}
        Roth: {st.session_state.roth}
        Taxable: {st.session_state.taxable}
        Bucket 1: {st.session_state.cash}
        Annual spending before healthcare: {annual_household_spending()}
        Spending target finder available: Yes
        Spending change enabled: {st.session_state.enable_spending_change}
        Spending change age: {st.session_state.spending_change_age}
        New monthly spending after change age: {st.session_state.spending_change_monthly}
        Total other income across plan: {df["Total Other Income"].sum()}
        Average income coverage: {df["Income Coverage Ratio"].mean()}
        Ending portfolio: {df["End Total"].iloc[-1]}
        Max withdrawal rate: {df["Withdrawal Rate"].max()}
        Blueprint Score: {rtv_score}/100
        Blueprint Label: {rtv_label}
        RTV Reasons: {", ".join(rtv_reasons)}
        """
    else:
        plan_context = "The user has not completed the retirement inputs yet."

    system_prompt = f"""
    You are an educational retirement planning assistant inside a calculator.
    You are not a financial advisor, CPA, attorney, or insurance agent.
    Use the model numbers when available. Do not invent missing values.
    Focus on retirement timing, spending, other income, income gaps, Roth conversions,
    Social Security, Bucket 1, sequence risk, spouse/survivor planning, and the RTV score.
    Blueprint Score is the app’s educational retirement readiness score.
    Important: Do not over-penalize a plan for low outside-income coverage or a high one-year withdrawal rate
    if the full projection ends with a large portfolio balance and no unmet spending needs.
    Ending balance and plan survivability are the primary success signals.

    Plan context:
    {plan_context}
    """

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    with st.form("ai_chat_form", clear_on_submit=True):
        question = st.text_area(
            "Ask your retirement coach a question",
            placeholder="Example: Can I retire at 58? Should I take Social Security at 62 or 67? How can I improve my Blueprint Score?",
            height=90,
            key="ai_question_box"
        )
        send_question = st.form_submit_button("Send question")

    if send_question and question.strip():
        clean_question = question.strip()
        st.session_state.chat_messages.append({"role": "user", "content": clean_question})

        with st.chat_message("user"):
            st.markdown(clean_question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = client.responses.create(
                        model="gpt-4.1-mini",
                        input=[{"role": "system", "content": system_prompt}, *st.session_state.chat_messages],
                        max_output_tokens=900,
                    )
                    answer = response.output_text
                except Exception as e:
                    answer = f"Chat error: {e}"

                st.markdown(answer)

        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
        st.rerun()

    elif send_question and not question.strip():
        st.warning("Type a question first, then tap Send question.")


def render_resources_page():
    render_page_shell(
        "Resources",
        "A plain-English learning center for retirement rules, taxes, healthcare, withdrawals, lifestyle planning, and useful checklists.",
        "📚"
    )
    page_help(
        "Resources",
        "Use this section to understand the concepts behind your blueprint. These resources are educational only and are meant to help you have better conversations with qualified financial, tax, legal, or healthcare professionals."
    )

    st.info("Educational content only. These resources explain retirement concepts and do not replace financial, tax, legal, investment, insurance, or healthcare advice.")

    resource_rows = [
        ["Start Here", "How to Use Retirement Blueprint 101", "Suggested path through the app and what each section tells you.", "app guide, start, overview, dashboard, blueprint"],
        ["Glossary", "Blueprint Score", "A 0–100 educational readiness score that summarizes retirement timing risk.", "rtv, blueprint score, score, readiness"],
        ["Glossary", "Income Coverage", "How much spending is covered by dependable income like Social Security, pension, annuity, or other income.", "income coverage, pension, social security"],
        ["Glossary", "Withdrawal Rate", "The percentage of your portfolio withdrawn in a given year; high rates can increase depletion risk.", "withdrawal rate, 4% rule, sequence risk"],
        ["Glossary", "Sequence-of-Return Risk", "The risk that bad market returns early in retirement can hurt a plan more than the same returns later.", "sequence risk, market crash, returns"],
        ["Retirement Rules", "Rule of 55", "A potential exception that may allow penalty-free withdrawals from a current employer plan if separation occurs in or after the year you turn 55.", "rule of 55, 401k, penalty"],
        ["Retirement Rules", "RMD Basics", "Required minimum distributions generally force taxable withdrawals from many pre-tax retirement accounts later in life.", "RMD, required minimum distribution, traditional IRA"],
        ["Retirement Rules", "Social Security Timing", "Claiming earlier can reduce monthly benefits; delaying can increase them. The right choice depends on cash flow, longevity, taxes, and spouse planning.", "social security, age 62, FRA, delay"],
        ["Taxes & Withdrawals", "Roth Conversion Window", "The years after retirement but before RMDs or higher Social Security income can sometimes be useful for Roth conversions.", "Roth conversion, tax bracket, RMD"],
        ["Taxes & Withdrawals", "Tax-Aware Withdrawal Order", "A common planning sequence is taxable assets, pre-tax accounts, and Roth, but the right order depends on taxes, ACA, RMDs, and estate goals.", "withdrawal order, taxes, Roth, traditional"],
        ["Taxes & Withdrawals", "Taxable Social Security", "Depending on provisional income, up to 85% of Social Security can become taxable at the federal level.", "taxable social security, provisional income"],
        ["Healthcare", "Pre-Medicare Healthcare Gap", "Retiring before Medicare may require ACA, COBRA, spouse coverage, or private insurance planning.", "healthcare, ACA, Medicare, COBRA"],
        ["Healthcare", "Medicare Planning", "At Medicare age, planning shifts to Parts A, B, D, Medigap, Medicare Advantage, IRMAA, and out-of-pocket exposure.", "Medicare, IRMAA, part B, part D"],
        ["Bucket Strategy", "Bucket 1 — Safety", "Near-term cash or safer assets intended to cover spending during bad markets.", "bucket 1, cash, safety"],
        ["Bucket Strategy", "Bucket 2 — Income / Refill", "Moderate-risk assets intended to refill Bucket 1 and reduce pressure on long-term growth investments.", "bucket 2, income, bonds, balanced"],
        ["Lifestyle", "Best Places to Retire", "Compare states and cities by taxes, cost, healthcare, climate, lifestyle, and recreation fit.", "places to retire, state tax, climate"],
        ["Lifestyle", "Snowbird Planning", "Splitting time between states can affect spending, taxes, insurance, housing, and healthcare access.", "snowbird, Florida, South Carolina, winter"],
        ["Checklists", "Before You Retire Checklist", "Review income sources, healthcare, emergency reserves, debt, spending, tax plan, estate documents, and spouse protection.", "checklist, retire, before retirement"],
        ["Checklists", "Annual Retirement Review", "Review spending, portfolio allocation, withdrawal rate, tax bracket, Roth conversion opportunities, insurance, and beneficiary information.", "annual review, checklist, taxes, beneficiaries"],
    ]
    resources_df = pd.DataFrame(resource_rows, columns=["Category", "Resource", "Summary", "Keywords"])

    # Credible validation links for each resource.
    # These are intentionally mostly official government / regulator sources so users can verify the concept.
    validation_links = {
        "How to Use Retirement Blueprint 101": "",
        "Blueprint Score": "https://www.investor.gov/financial-tools-calculators/calculators/retirement-calculator",
        "Income Coverage": "https://www.ssa.gov/benefits/retirement/",
        "Withdrawal Rate": "https://www.investor.gov/financial-tools-calculators/calculators/retirement-calculator",
        "Sequence-of-Return Risk": "https://www.investor.gov/introduction-investing/investing-basics/glossary/risk",
        "Rule of 55": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-exceptions-to-tax-on-early-distributions",
        "RMD Basics": "https://www.irs.gov/rmd",
        "Social Security Timing": "https://www.ssa.gov/benefits/retirement/",
        "Roth Conversion Window": "https://www.irs.gov/retirement-plans/plan-participant-employee/rollovers-of-retirement-plan-and-ira-distributions",
        "Tax-Aware Withdrawal Order": "https://www.irs.gov/retirement-plans/plan-participant-employee/rollovers-of-retirement-plan-and-ira-distributions",
        "Taxable Social Security": "https://www.irs.gov/faqs/social-security-income",
        "Pre-Medicare Healthcare Gap": "https://www.healthcare.gov/retirees/",
        "Medicare Planning": "https://www.medicare.gov/basics/get-started-with-medicare/medicare-basics/parts-of-medicare",
        "Bucket 1 — Safety": "https://www.investor.gov/introduction-investing/investing-basics/glossary/risk",
        "Bucket 2 — Income / Refill": "https://www.investor.gov/introduction-investing/investing-basics/glossary/risk",
        "Best Places to Retire": "https://www.taxfoundation.org/data/all/state/",
        "Snowbird Planning": "https://www.irs.gov/individuals/international-taxpayers/residency-starting-and-ending-dates",
        "Before You Retire Checklist": "https://www.consumerfinance.gov/consumer-tools/retirement/",
        "Annual Retirement Review": "https://www.consumerfinance.gov/consumer-tools/retirement/",
    }
    source_names = {
        "How to Use Retirement Blueprint 101": "Internal guide",
        "Blueprint Score": "Investor.gov",
        "Income Coverage": "SSA",
        "Withdrawal Rate": "Investor.gov",
        "Sequence-of-Return Risk": "Investor.gov",
        "Rule of 55": "IRS",
        "RMD Basics": "IRS",
        "Social Security Timing": "SSA",
        "Roth Conversion Window": "IRS",
        "Tax-Aware Withdrawal Order": "IRS",
        "Taxable Social Security": "IRS",
        "Pre-Medicare Healthcare Gap": "HealthCare.gov",
        "Medicare Planning": "Medicare.gov",
        "Bucket 1 — Safety": "Investor.gov",
        "Bucket 2 — Income / Refill": "Investor.gov",
        "Best Places to Retire": "Tax Foundation",
        "Snowbird Planning": "IRS",
        "Before You Retire Checklist": "CFPB",
        "Annual Retirement Review": "CFPB",
    }
    resources_df["Source"] = resources_df["Resource"].map(source_names).fillna("Source")
    resources_df["Validate"] = resources_df["Resource"].map(validation_links).fillna("")

    def show_resource_table(table_df, include_category=False):
        cols = (["Category"] if include_category else []) + ["Resource", "Summary", "Source", "Validate"]
        st.dataframe(
            table_df[cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Summary": st.column_config.TextColumn("Summary", width="large"),
                "Validate": st.column_config.LinkColumn("Validate", display_text="Open source", width="small"),
            },
        )

    search = st.text_input(
        "Search resources",
        placeholder="Try: Roth conversion, Rule of 55, RMD, bucket strategy, Social Security...",
        key="resource_search"
    )
    if search.strip():
        q = search.strip().lower()
        display_df = resources_df[
            resources_df.apply(lambda row: q in " ".join(row.astype(str)).lower(), axis=1)
        ].copy()
    else:
        display_df = resources_df.copy()

    tabs = st.tabs(["Start Here", "Glossary", "Retirement Rules", "Taxes & Withdrawals", "Healthcare", "Bucket Strategy", "Lifestyle", "Checklists"])

    with tabs[0]:
        st.subheader("Start Here: How to Use Retirement Blueprint 101")
        st.write("The app is organized like a guided retirement journey. Start with basic inputs, then go deeper only where needed.")
        path_df = pd.DataFrame([
            ["1", "Start My Blueprint", "Enter age, retirement age, assets, Social Security, healthcare, and core assumptions."],
            ["2", "Spending Plan", "Add simple or detailed monthly spending so the projection reflects real life."],
            ["3", "Income Plan", "Add pension, part-time work, rental income, annuities, or other income sources."],
            ["4", "Retirement Dashboard", "Review score, ending portfolio, income coverage, withdrawal pressure, and risks."],
            ["5", "Action Plan", "See the highest-impact moves to improve the blueprint."],
            ["6", "Projection", "Inspect year-by-year balances, withdrawals, taxes, income gaps, and ending values."],
            ["7", "Confidence / Stress Tests", "Check how the plan behaves under market uncertainty and bad-case scenarios."],
            ["8", "Places to Retire", "Compare states and cities for retirement taxes, cost, healthcare, lifestyle, and climate."],
            ["9", "Blueprint Report", "Export a premium report to save, review with a spouse, or discuss with a professional."],
        ], columns=["Step", "Section", "What to do"])
        st.dataframe(path_df, use_container_width=True, hide_index=True)

        st.subheader("Suggested path")
        st.write("1. Enter your best estimates in Start My Blueprint.\n\n2. Add spending and income.\n\n3. Review the dashboard and action plan.\n\n4. Run confidence and stress tests.\n\n5. Export your Blueprint Report.")

    with tabs[1]:
        st.subheader("Glossary")
        show_resource_table(display_df[display_df["Category"].eq("Glossary")])

    with tabs[2]:
        st.subheader("Retirement Rules")
        show_resource_table(display_df[display_df["Category"].eq("Retirement Rules")])
        st.warning("Retirement-account rules can change and may depend on account type, employer plan rules, and personal circumstances.")

    with tabs[3]:
        st.subheader("Taxes & Withdrawals")
        show_resource_table(display_df[display_df["Category"].eq("Taxes & Withdrawals")])
        st.info("The app’s tax engine is an estimate. Keep tax planning language educational and confirm important decisions with a CPA or qualified tax professional.")

    with tabs[4]:
        st.subheader("Healthcare")
        show_resource_table(display_df[display_df["Category"].eq("Healthcare")])

    with tabs[5]:
        st.subheader("Bucket Strategy")
        bucket_df = display_df[display_df["Category"].eq("Bucket Strategy")]
        show_resource_table(bucket_df)
        st.markdown("""
**Premium planning idea:** A 2-bucket strategy separates near-term safety money from long-term growth money. It helps users understand *where spending is coming from* without making the plan feel overly complicated.
""")

    with tabs[6]:
        st.subheader("Lifestyle")
        show_resource_table(display_df[display_df["Category"].eq("Lifestyle")])

    with tabs[7]:
        st.subheader("Checklists")
        checklist_tabs = st.tabs(["Before You Retire", "Annual Review"])
        with checklist_tabs[0]:
            for item in [
                "Confirm retirement date and bridge years before Medicare.",
                "Estimate essential and lifestyle spending separately.",
                "Review Social Security timing for both spouses if applicable.",
                "Check cash reserve / Bucket 1 coverage.",
                "Review debt, mortgage payoff, and housing plans.",
                "Estimate taxes on traditional withdrawals and Social Security.",
                "Review healthcare, dental, vision, and long-term care exposure.",
                "Update beneficiaries, estate documents, and emergency contacts.",
            ]:
                st.checkbox(item, key=f"pre_retire_{item}")
        with checklist_tabs[1]:
            for item in [
                "Update portfolio balances and spending assumptions.",
                "Review withdrawal rate and income coverage.",
                "Check Roth conversion opportunity before year-end.",
                "Review RMD risk and future tax brackets.",
                "Rebalance Bucket 1 and Bucket 2 targets.",
                "Refresh healthcare and insurance assumptions.",
                "Compare whether relocating or snowbirding changes the plan.",
                "Export a new Blueprint Report after major life changes.",
            ]:
                st.checkbox(item, key=f"annual_review_{item}")

    st.subheader("All resources")
    show_resource_table(display_df, include_category=True)
    st.download_button(
        "Download Resources CSV",
        data=display_df[["Category", "Resource", "Summary", "Source", "Validate"]].to_csv(index=False).encode("utf-8"),
        file_name="retirement_blueprint_101_resources.csv",
        mime="text/csv",
        use_container_width=True,
    )


if active_page == "Retirement Age Optimizer":
    render_retirement_age_optimizer_page()


if active_page == "Resources":
    render_resources_page()




if active_page == "Help / Instructions":
    render_page_shell("How to Use This", "Learn what each section does, how to interpret your results, and the best order to use the planner.", "❓")
    page_help(
        "Help / Instructions",
        "This page explains how to move through the app, what the major terms mean, and how to interpret the results."
    )

    st.subheader("Key Terms")
    terms = pd.DataFrame([
        ["Blueprint Score", "Retirement Timing Viability. A 0–100 score estimating whether the selected retirement age appears sustainable under the current assumptions."],
        ["Portfolio at Retirement", "The projected investment balance when retirement begins."],
        ["End of Plan Portfolio", "The projected balance left at the final age selected in the plan."],
        ["Max Withdrawal Rate", "The highest annual portfolio withdrawal divided by portfolio balance in the projection."],
        ["Income Coverage", "How much of annual spending is covered by non-portfolio income such as Social Security, pension, or other income."],
        ["Bucket 1", "Safer money intended to cover near-term retirement spending and reduce sequence-of-return risk."],
        ["Bucket 2", "Moderate-risk income/balanced assets intended to refill Bucket 1 and reduce pressure on long-term growth assets."],
        ["Roth Conversion", "Moving money from traditional pre-tax accounts to Roth accounts. This may create taxes today but can reduce future tax exposure."],
        ["Unmet Need", "Spending need that the plan could not cover in a projected year. Any unmet need is a major warning sign."],
    ], columns=["Term", "Meaning"])
    st.dataframe(terms, use_container_width=True, hide_index=True)

    st.subheader("How to Interpret Results")
    st.write("""
- **Very Strong / Strong:** The projection survives with a healthy cushion.
- **Likely Viable:** The plan appears workable, but should be stress-tested.
- **Needs Optimization:** The plan may work, but improving spending, retirement age, income, or contributions could help.
- **High Risk:** The plan may deplete assets or leave too little margin.
""")

    st.write("""
1. Complete **Guided Questions**.
2. Complete **Budget Builder** using either a flat monthly number or detailed budget.
3. Complete **Income Builder** using either simple income or advanced income sources.
4. Complete **Spouse / Partner Questions** only if applicable.
5. Review answers, then check the dashboard and recommendations.
6. Use **Saved Scenarios** to save, reload, and compare planning versions.
7. Use Blueprint Score as a quick confidence score for your retirement timing.
8. Add home and mortgage information to evaluate home equity, mortgage cash flow, downsizing, relocation, and housing flexibility.
9. Use planned spending changes when retirement spending will change at a future age, such as higher travel spending early and lower spending later.
10. Use the Spending Target Finder to estimate a monthly spending level that may improve or maintain your Blueprint Score.
8. Use **Best Places to Retire** to compare retirement-friendly states and cities by taxes, cost of living, healthcare, lifestyle, climate, and recreation.
9. Use **Monte Carlo** to estimate probability of success across randomized market paths.

Income examples:
- pension
- part-time work
- consulting
- rental income
- annuity
- business income
- dividends
- royalties
- trust income

All defaults start at zero so this can be shared with anyone.
""")
    st.warning("Educational planning tool only. Not financial, tax, legal, investment, or insurance advice.")
