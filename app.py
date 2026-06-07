import streamlit as st
import pickle
import sqlite3
import math
import os
from html import escape
from pathlib import Path
from assessment import build_assessment, score_assessment
from learning import generate_weekly_plan, infer_learning_context
from product import LEVEL_PROFILES, analyze_text, build_report
from writing_coach import analyze_writing
from storage import (
    clear_profile_data,
    get_dashboard_stats,
    get_latest_assessment,
    get_profile,
    initialize_database,
    list_analyses,
    list_completed_tasks,
    save_analysis,
    save_assessment,
    set_task_completed,
    update_profile,
)

# 1. Sayfa Ayarları
st.set_page_config(
    page_title="Pro English AI | English Intelligence",
    page_icon="PE",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,600;1,600&display=swap');

    :root {
        --ink: #0d0f12;
        --panel: #15191e;
        --paper: #f5f0e8;
        --gold: #d2ad52;
        --teal: #3da08f;
        --muted: #a8a39a;
    }
    .stApp {
        background:
            radial-gradient(circle at 85% 8%, rgba(61,160,143,.13), transparent 25rem),
            radial-gradient(circle at 10% 30%, rgba(210,173,82,.09), transparent 28rem),
            var(--ink);
        color: var(--paper);
        font-family: 'DM Sans', sans-serif;
    }
    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 20% 0%, rgba(210,173,82,.13), transparent 15rem),
            linear-gradient(180deg, #15191e 0%, #101317 100%);
        border-right: 1px solid rgba(210,173,82,.18);
        box-shadow: 12px 0 35px rgba(0,0,0,.16);
    }
    [data-testid="stSidebar"] > div:first-child { padding: 1.25rem 1rem; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--muted); }
    [data-testid="stSidebar"] .stRadio > label {
        color: #817c73;
        font-size: .68rem;
        font-weight: 700;
        letter-spacing: .15em;
        text-transform: uppercase;
        margin: 1rem 0 .5rem;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: .55rem; }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
        background: rgba(245,240,232,.035);
        border: 1px solid rgba(245,240,232,.09);
        border-radius: .75rem;
        padding: .8rem .85rem;
        transition: all .18s ease;
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
        border-color: rgba(210,173,82,.42);
        background: rgba(210,173,82,.06);
        transform: translateX(3px);
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) {
        border-color: rgba(210,173,82,.7);
        background: linear-gradient(90deg, rgba(210,173,82,.15), rgba(210,173,82,.04));
        box-shadow: inset 3px 0 0 var(--gold);
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:first-child {
        display: none;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="collapsedControl"] {
        background: var(--panel);
        border: 1px solid rgba(210,173,82,.3);
        border-radius: 0 .7rem .7rem 0;
        color: var(--gold);
    }
    .block-container { max-width: 1180px; padding-top: 2.2rem; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; }
    .hero {
        padding: 2.2rem 0 1.5rem;
        text-align: center;
    }
    .eyebrow {
        color: var(--gold);
        font-size: .72rem;
        letter-spacing: .22em;
        font-weight: 600;
        margin-bottom: .8rem;
    }
    .hero h1 {
        font-size: clamp(2.5rem, 6vw, 5rem);
        line-height: 1.02;
        margin: 0;
        color: var(--paper);
    }
    .hero h1 em { color: var(--gold); }
    .hero p {
        color: var(--muted);
        max-width: 720px;
        margin: 1.1rem auto 1.6rem;
        font-size: 1.03rem;
        line-height: 1.7;
    }
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin: 1rem 0 1.7rem;
    }
    .hero-stat strong {
        display: block;
        color: var(--gold);
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
    }
    .hero-stat span { color: #827d74; font-size: .7rem; letter-spacing: .12em; }
    .level-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: .55rem;
        margin: 1rem 0 2rem;
    }
    .level-chip {
        padding: .75rem .45rem;
        border: 1px solid color-mix(in srgb, var(--level) 70%, transparent);
        border-radius: .7rem;
        background: color-mix(in srgb, var(--level) 9%, transparent);
        color: var(--level);
        text-align: center;
        font-size: .76rem;
        letter-spacing: .04em;
    }
    .level-chip b { display: block; font-size: 1rem; margin-bottom: .15rem; }
    .info-card, .result-card {
        background: linear-gradient(145deg, rgba(245,240,232,.065), rgba(245,240,232,.025));
        border: 1px solid rgba(210,173,82,.22);
        border-radius: 1rem;
        padding: 1.35rem 1.5rem;
        min-height: 100%;
        box-shadow: 0 18px 45px rgba(0,0,0,.18);
    }
    .info-card h3 { color: var(--gold); margin-top: 0; }
    .info-card p, .info-card li { color: var(--muted); line-height: 1.65; }
    .info-card li { margin-bottom: .45rem; }
    .sidebar-brand {
        border-bottom: 1px solid rgba(210,173,82,.16);
        padding: .35rem .15rem 1.15rem;
        margin-bottom: .4rem;
    }
    .sidebar-mark {
        width: 2.5rem;
        height: 2.5rem;
        display: grid;
        place-items: center;
        border-radius: .7rem;
        background: linear-gradient(145deg, #d2ad52, #8d6f2d);
        color: #111;
        font-family: 'Playfair Display', serif;
        font-size: 1.2rem;
        font-weight: 700;
        box-shadow: 0 8px 20px rgba(210,173,82,.18);
        margin-bottom: .8rem;
    }
    .sidebar-brand h2 {
        color: var(--paper);
        font-size: 1.25rem;
        line-height: 1.15;
        margin: 0 0 .35rem;
    }
    .sidebar-brand h2 em { color: var(--gold); }
    .sidebar-brand p { font-size: .72rem; letter-spacing: .11em; margin: 0; }
    .sidebar-status {
        margin-top: 1rem;
        padding: .9rem;
        border: 1px solid rgba(61,160,143,.22);
        background: rgba(61,160,143,.055);
        border-radius: .75rem;
    }
    .status-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #d8d4cc;
        font-size: .78rem;
        margin-bottom: .45rem;
    }
    .status-row:last-child { margin-bottom: 0; }
    .status-value { color: var(--teal); font-weight: 600; }
    .status-dot {
        width: .45rem;
        height: .45rem;
        display: inline-block;
        background: var(--teal);
        border-radius: 50%;
        box-shadow: 0 0 0 4px rgba(61,160,143,.1);
        margin-right: .45rem;
    }
    .sidebar-footer {
        color: #6e6a63;
        font-size: .67rem;
        line-height: 1.55;
        border-top: 1px solid rgba(245,240,232,.08);
        padding-top: .9rem;
        margin-top: 1.1rem;
    }
    .page-hero {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(210,173,82,.2);
        border-radius: 1.1rem;
        padding: 2rem 2.2rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(130deg, rgba(210,173,82,.09), rgba(61,160,143,.055));
    }
    .page-hero::after {
        content: "";
        position: absolute;
        width: 15rem;
        height: 15rem;
        right: -5rem;
        top: -7rem;
        border: 1px solid rgba(210,173,82,.12);
        border-radius: 50%;
        box-shadow: 0 0 0 2.5rem rgba(210,173,82,.025);
    }
    .page-hero h1 { color: var(--paper); margin: .3rem 0 .5rem; font-size: 2.6rem; }
    .page-hero p { color: var(--muted); max-width: 680px; line-height: 1.65; margin: 0; }
    .exam-meta {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: .65rem;
        margin: 1rem 0 1.4rem;
    }
    .exam-meta div {
        background: rgba(245,240,232,.035);
        border: 1px solid rgba(245,240,232,.09);
        border-radius: .75rem;
        padding: .8rem;
        text-align: center;
        color: var(--muted);
        font-size: .72rem;
    }
    .exam-meta b { display: block; color: var(--gold); font-size: 1rem; margin-bottom: .15rem; }
    .result-level {
        font-family: 'Playfair Display', serif;
        font-size: 4.2rem;
        line-height: 1;
        color: var(--gold);
    }
    .cefr-bar { display: flex; gap: .35rem; margin: 1.2rem 0 .45rem; }
    .cefr-segment {
        flex: 1;
        height: .42rem;
        border-radius: 2rem;
        opacity: .22;
    }
    .cefr-segment.active { opacity: 1; transform: scaleY(1.55); }
    .cefr-labels { display: flex; color: #77736c; font-size: .7rem; }
    .cefr-labels span { flex: 1; text-align: center; }
    .cefr-labels span.active { color: var(--gold); font-weight: 700; }
    div[data-testid="stTextArea"] textarea {
        background: rgba(245,240,232,.045);
        border: 1px solid rgba(245,240,232,.16);
        border-radius: .8rem;
        color: var(--paper);
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: var(--gold);
        box-shadow: 0 0 0 1px var(--gold);
    }
    .stButton > button, .stFormSubmitButton > button {
        background: linear-gradient(135deg, #d2ad52, #e8c97a);
        color: #111;
        border: 0;
        border-radius: .65rem;
        font-weight: 700;
        min-height: 3rem;
        transition: transform .18s, box-shadow .18s;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        color: #111;
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(210,173,82,.22);
    }
    div[data-testid="stMetric"] {
        background: rgba(245,240,232,.045);
        border: 1px solid rgba(245,240,232,.1);
        border-radius: .75rem;
        padding: .8rem;
    }
    div[data-baseweb="select"] > div {
        background: rgba(245,240,232,.045);
        border-color: rgba(245,240,232,.14);
        border-radius: .7rem;
        min-height: 3rem;
    }
    div[data-baseweb="select"] > div:hover { border-color: var(--gold); }
    div[data-testid="stForm"] {
        background: rgba(245,240,232,.025);
        border: 1px solid rgba(210,173,82,.16);
        border-radius: 1rem;
        padding: 1.25rem 1.4rem 1.5rem;
    }
    div[data-testid="stForm"] .stRadio {
        background: rgba(245,240,232,.025);
        border: 1px solid rgba(245,240,232,.08);
        border-radius: .8rem;
        padding: .75rem 1rem .8rem;
        margin: .35rem 0 1.05rem;
    }
    div[data-testid="stForm"] .stRadio > label {
        color: #77736c;
        font-size: .7rem;
        letter-spacing: .1em;
        text-transform: uppercase;
    }
    div[data-testid="stForm"] label[data-baseweb="radio"] {
        background: rgba(245,240,232,.02);
        border: 1px solid rgba(245,240,232,.08);
        border-radius: .55rem;
        padding: .55rem .7rem;
        margin-right: .35rem;
    }
    div[data-testid="stForm"] label[data-baseweb="radio"]:has(input:checked) {
        border-color: rgba(210,173,82,.6);
        background: rgba(210,173,82,.1);
    }
    div[data-testid="stAlert"] {
        border-radius: .75rem;
        border: 1px solid rgba(245,240,232,.1);
    }
    .answer-card {
        border-radius: .7rem;
        padding: .75rem .9rem;
        margin: .45rem 0;
        color: #d7d3ca;
        line-height: 1.5;
    }
    .answer-card.correct {
        background: rgba(61,160,143,.07);
        border: 1px solid rgba(61,160,143,.22);
    }
    .answer-card.wrong {
        background: rgba(201,92,84,.07);
        border: 1px solid rgba(201,92,84,.22);
    }
    .trust-strip {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: .6rem;
        margin: -.4rem 0 1.6rem;
    }
    .trust-item {
        display: flex;
        align-items: center;
        gap: .65rem;
        padding: .7rem .85rem;
        background: rgba(245,240,232,.025);
        border: 1px solid rgba(245,240,232,.075);
        border-radius: .7rem;
        color: #969188;
        font-size: .72rem;
    }
    .trust-icon {
        display: grid;
        place-items: center;
        width: 1.7rem;
        height: 1.7rem;
        border-radius: .45rem;
        background: rgba(61,160,143,.1);
        color: var(--teal);
        font-weight: 700;
    }
    .section-label {
        color: #77736c;
        font-size: .68rem;
        font-weight: 700;
        letter-spacing: .16em;
        text-transform: uppercase;
        margin-bottom: .45rem;
    }
    .analysis-shell {
        background: linear-gradient(145deg, rgba(245,240,232,.04), rgba(245,240,232,.018));
        border: 1px solid rgba(245,240,232,.09);
        border-radius: 1rem;
        padding: 1.25rem;
    }
    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1rem;
    }
    .reliability-badge {
        border: 1px solid rgba(61,160,143,.3);
        background: rgba(61,160,143,.08);
        color: #76c7b8;
        border-radius: 99px;
        padding: .38rem .65rem;
        font-size: .68rem;
        font-weight: 700;
        white-space: nowrap;
    }
    .profile-grid {
        display: grid;
        grid-template-columns: 1.1fr .9fr;
        gap: .75rem;
        margin-top: 1rem;
    }
    .profile-card {
        background: rgba(245,240,232,.028);
        border: 1px solid rgba(245,240,232,.08);
        border-radius: .8rem;
        padding: 1rem;
    }
    .profile-card h4 {
        color: var(--gold);
        margin: 0 0 .55rem;
        font-size: .82rem;
        letter-spacing: .04em;
    }
    .profile-card p, .profile-card li {
        color: #aaa59c;
        font-size: .78rem;
        line-height: 1.55;
    }
    .profile-card ul { margin: 0; padding-left: 1.1rem; }
    .quality-track {
        height: .42rem;
        background: rgba(245,240,232,.08);
        border-radius: 99px;
        overflow: hidden;
        margin: .55rem 0 .35rem;
    }
    .quality-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--teal), var(--gold));
        border-radius: inherit;
    }
    .history-card {
        display: grid;
        grid-template-columns: 4rem 1fr auto;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.1rem;
        margin-bottom: .65rem;
        background: rgba(245,240,232,.03);
        border: 1px solid rgba(245,240,232,.08);
        border-radius: .8rem;
    }
    .history-level {
        font-family: 'Playfair Display', serif;
        font-size: 1.55rem;
        color: var(--gold);
    }
    .history-copy { color: #aaa59c; font-size: .78rem; line-height: 1.45; }
    .history-meta { color: #77736c; font-size: .7rem; text-align: right; }
    .score-summary {
        display: grid;
        grid-template-columns: auto 1fr;
        align-items: center;
        gap: 1.2rem;
        padding: 1.2rem 1.3rem;
        margin: 1rem 0 1.3rem;
        background: linear-gradient(135deg, rgba(210,173,82,.1), rgba(61,160,143,.06));
        border: 1px solid rgba(210,173,82,.22);
        border-radius: .9rem;
    }
    .score-number {
        font-family: 'Playfair Display', serif;
        font-size: 2.3rem;
        color: var(--gold);
        line-height: 1;
    }
    .score-copy b { color: #e3ded5; }
    .score-copy p { color: #969188; font-size: .78rem; margin: .25rem 0 0; }
    .profile-chip {
        display: flex;
        align-items: center;
        gap: .65rem;
        margin: .85rem 0 .15rem;
        padding: .7rem .75rem;
        background: rgba(245,240,232,.035);
        border: 1px solid rgba(245,240,232,.08);
        border-radius: .7rem;
    }
    .profile-avatar {
        width: 2rem;
        height: 2rem;
        display: grid;
        place-items: center;
        border-radius: 50%;
        background: linear-gradient(145deg, rgba(210,173,82,.25), rgba(61,160,143,.18));
        color: var(--gold);
        font-weight: 700;
    }
    .profile-chip b { color: #ddd8cf; display: block; font-size: .8rem; }
    .profile-chip span { color: #77736c; display: block; font-size: .67rem; }
    .goal-card {
        padding: 1.1rem 1.2rem;
        margin: .8rem 0 1.2rem;
        background: linear-gradient(135deg, rgba(61,160,143,.08), rgba(210,173,82,.06));
        border: 1px solid rgba(61,160,143,.2);
        border-radius: .85rem;
    }
    .goal-head {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        color: #ddd8cf;
        font-size: .82rem;
        margin-bottom: .55rem;
    }
    .goal-head span { color: var(--teal); font-weight: 700; }
    .goal-track {
        height: .5rem;
        background: rgba(245,240,232,.08);
        border-radius: 99px;
        overflow: hidden;
    }
    .goal-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--teal), var(--gold));
        border-radius: inherit;
    }
    .goal-card p { color: #817c73; font-size: .7rem; margin: .5rem 0 0; }
    .assessment-toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding: .8rem 1rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(245,240,232,.08);
        background: rgba(245,240,232,.025);
        border-radius: .75rem;
        color: #969188;
        font-size: .74rem;
    }
    .assessment-toolbar b { color: var(--gold); }
    .question-meta {
        display: flex;
        gap: .45rem;
        margin-bottom: .4rem;
    }
    .question-tag {
        padding: .2rem .45rem;
        border-radius: 99px;
        border: 1px solid rgba(210,173,82,.2);
        color: #aaa59c;
        font-size: .62rem;
        letter-spacing: .06em;
        text-transform: uppercase;
    }
    .domain-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: .7rem;
        margin: 1rem 0;
    }
    .domain-card {
        padding: 1rem;
        text-align: center;
        background: rgba(245,240,232,.03);
        border: 1px solid rgba(245,240,232,.08);
        border-radius: .8rem;
    }
    .domain-card strong {
        display: block;
        color: var(--gold);
        font-family: 'Playfair Display', serif;
        font-size: 1.65rem;
    }
    .domain-card span { color: #858078; font-size: .68rem; text-transform: uppercase; }
    .level-performance {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: .45rem;
        margin: .8rem 0 1.1rem;
    }
    .level-performance div {
        padding: .65rem .35rem;
        text-align: center;
        border: 1px solid rgba(245,240,232,.08);
        border-radius: .6rem;
        color: #858078;
        font-size: .68rem;
    }
    .level-performance b { display: block; color: #d8d4cc; font-size: .9rem; }
    .explanation-card {
        padding: .75rem .9rem;
        margin: .35rem 0;
        background: rgba(245,240,232,.025);
        border-left: 2px solid rgba(210,173,82,.45);
        color: #9f9a91;
        font-size: .75rem;
        line-height: 1.5;
    }
    .plan-hero {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 1rem;
        align-items: center;
        padding: 1.2rem 1.35rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, rgba(61,160,143,.09), rgba(210,173,82,.07));
        border: 1px solid rgba(61,160,143,.22);
        border-radius: .9rem;
    }
    .plan-hero h3 { margin: 0 0 .35rem; color: #e2ddd4; }
    .plan-hero p { margin: 0; color: #918c83; font-size: .78rem; }
    .plan-score {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        color: var(--teal);
        white-space: nowrap;
    }
    .task-card {
        padding: 1rem 1.1rem;
        margin-bottom: .65rem;
        background: rgba(245,240,232,.03);
        border: 1px solid rgba(245,240,232,.08);
        border-radius: .8rem;
    }
    .task-card.done {
        background: rgba(61,160,143,.06);
        border-color: rgba(61,160,143,.2);
    }
    .task-meta {
        display: flex;
        gap: .45rem;
        margin-bottom: .45rem;
    }
    .task-meta span {
        padding: .2rem .45rem;
        border-radius: 99px;
        background: rgba(210,173,82,.07);
        color: #9c968d;
        font-size: .62rem;
    }
    .task-card h4 { margin: 0 0 .35rem; color: #ddd8cf; font-size: .92rem; }
    .task-card p { margin: 0; color: #918c83; font-size: .76rem; line-height: 1.55; }
    .coach-shell {
        margin: 1.25rem 0;
        padding: 1.35rem;
        background: linear-gradient(145deg, rgba(61,160,143,.065), rgba(245,240,232,.02));
        border: 1px solid rgba(61,160,143,.24);
        border-radius: 1rem;
    }
    .coach-head {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: .85rem;
    }
    .coach-head h3 { margin: 0 0 .3rem; color: #e4dfd6; }
    .coach-head p { margin: 0; color: #918c83; font-size: .78rem; }
    .coach-engine {
        padding: .32rem .6rem;
        border: 1px solid rgba(61,160,143,.26);
        border-radius: 99px;
        color: #76c7b8;
        background: rgba(61,160,143,.07);
        font-size: .65rem;
        white-space: nowrap;
    }
    .issue-card {
        padding: 1rem 1.05rem;
        margin: .55rem 0;
        border: 1px solid rgba(245,240,232,.09);
        border-left: 3px solid var(--gold);
        border-radius: .75rem;
        background: rgba(245,240,232,.025);
    }
    .issue-top {
        display: flex;
        justify-content: space-between;
        gap: .8rem;
        color: #77736c;
        font-size: .67rem;
        text-transform: uppercase;
        letter-spacing: .08em;
    }
    .issue-category { color: var(--gold); font-weight: 700; }
    .issue-change {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: .5rem;
        margin: .7rem 0 .5rem;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }
    .issue-before, .issue-after {
        padding: .3rem .5rem;
        border-radius: .4rem;
    }
    .issue-before {
        color: #ef9b94;
        background: rgba(201,92,84,.1);
        text-decoration: line-through;
    }
    .issue-after { color: #83cfbf; background: rgba(61,160,143,.1); }
    .issue-arrow { color: #6f6a62; }
    .issue-message { color: #aaa59c; font-size: .76rem; line-height: 1.55; }
    .rewrite-card {
        padding: 1rem 1.1rem;
        margin: .55rem 0;
        border: 1px solid rgba(245,240,232,.09);
        border-radius: .75rem;
        background: rgba(245,240,232,.025);
    }
    .rewrite-label {
        color: #77736c;
        font-size: .62rem;
        font-weight: 700;
        letter-spacing: .11em;
        text-transform: uppercase;
        margin-bottom: .3rem;
    }
    .rewrite-before { color: #be8a85; line-height: 1.55; }
    .rewrite-after { color: #91cbbf; line-height: 1.55; }
    .corrected-copy {
        padding: 1.1rem 1.2rem;
        border: 1px solid rgba(61,160,143,.18);
        border-radius: .8rem;
        background: rgba(61,160,143,.045);
        color: #d9d5cc;
        line-height: 1.75;
        white-space: pre-wrap;
    }
    hr { border-color: rgba(210,173,82,.15) !important; }
    @media (max-width: 760px) {
        .level-grid { grid-template-columns: repeat(3, 1fr); }
        .hero-stats { gap: 1.2rem; }
        .exam-meta { grid-template-columns: 1fr; }
        .trust-strip, .profile-grid { grid-template-columns: 1fr; }
        .domain-grid { grid-template-columns: 1fr; }
        .plan-hero { grid-template-columns: 1fr; }
        .level-performance { grid-template-columns: repeat(3, 1fr); }
        .history-card { grid-template-columns: 3rem 1fr; }
        .history-meta { display: none; }
        .page-hero { padding: 1.4rem; }
        .page-hero h1 { font-size: 2rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

LEVEL_INFO = {
    "A1": ("Beginner", "#c95c54"),
    "A2": ("Elementary", "#dc8b43"),
    "B1": ("Intermediate", "#52a66b"),
    "B2": ("Upper Intermediate", "#4c8fc7"),
    "C1": ("Advanced", "#9469b8"),
    "C2": ("Proficient", "#3da08f"),
}


def render_level_grid():
    chips = "".join(
        f'<div class="level-chip" style="--level:{color}"><b>{level}</b>{name}</div>'
        for level, (name, color) in LEVEL_INFO.items()
    )
    st.markdown(f'<div class="level-grid">{chips}</div>', unsafe_allow_html=True)


def render_cefr_scale(active_level):
    segments = "".join(
        f'<div class="cefr-segment {"active" if level == active_level else ""}" '
        f'style="background:{color}"></div>'
        for level, (_, color) in LEVEL_INFO.items()
    )
    labels = "".join(
        f'<span class="{"active" if level == active_level else ""}">{level}</span>'
        for level in LEVEL_INFO
    )
    st.markdown(
        f'<div class="cefr-bar">{segments}</div><div class="cefr-labels">{labels}</div>',
        unsafe_allow_html=True,
    )


# 2. Modeli Yükle
def render_writing_coach(coach):
    issues = coach.get("issues", [])
    counts = coach.get("counts", {})
    st.markdown(
        f"""
        <div class="coach-shell">
            <div class="coach-head">
                <div>
                    <div class="section-label">PRO ENGLISH AI WRITING COACH</div>
                    <h3>Hatalarınızı görün, cümlenizi geliştirin</h3>
                    <p>Yazım, dilbilgisi ve noktalama sorunları metindeki gerçek
                    konumlarıyla açıklanır.</p>
                </div>
                <span class="coach-engine">{escape(coach.get("engine", "Pro English AI"))}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(4)
    metric_columns[0].metric("Toplam Bulgu", len(issues))
    metric_columns[1].metric("Yazım", counts.get("Yazım", 0))
    metric_columns[2].metric("Dilbilgisi", counts.get("Dilbilgisi", 0))
    metric_columns[3].metric(
        "Diğer",
        len(issues) - counts.get("Yazım", 0) - counts.get("Dilbilgisi", 0),
    )

    errors_tab, corrected_tab, comparison_tab = st.tabs(
        ["Hata Haritası", "Düzeltilmiş Metin", "Cümle Karşılaştırması"]
    )
    with errors_tab:
        if not issues:
            st.success("Belirgin bir yazım veya dilbilgisi hatası bulunmadı.")
        for issue in issues[:20]:
            replacement = issue.get("replacement") or "Bağlama göre yeniden yazın"
            st.markdown(
                f"""
                <div class="issue-card">
                    <div class="issue-top">
                        <span class="issue-category">{escape(issue["category"])}</span>
                        <span>Satır {issue["line"]} · Sütun {issue["column"]}</span>
                    </div>
                    <div class="issue-change">
                        <span class="issue-before">{escape(issue["original"] or "∅")}</span>
                        <span class="issue-arrow">→</span>
                        <span class="issue-after">{escape(replacement)}</span>
                    </div>
                    <div class="issue-message">{escape(issue["message"])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        if len(issues) > 20:
            st.caption(f"İlk 20 bulgu gösteriliyor. Toplam {len(issues)} bulgu var.")

    with corrected_tab:
        corrected_text = coach.get("corrected_text", "")
        st.markdown(
            f'<div class="corrected-copy">{escape(corrected_text)}</div>',
            unsafe_allow_html=True,
        )
        st.download_button(
            "Düzeltilmiş Metni İndir",
            data=corrected_text,
            file_name="pro-english-ai-corrected-writing.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with comparison_tab:
        comparisons = coach.get("sentence_comparisons", [])
        if not comparisons:
            st.info("Cümle yapısında gösterilecek bir değişiklik bulunmadı.")
        for comparison in comparisons:
            st.markdown(
                f"""
                <div class="rewrite-card">
                    <div class="rewrite-label">Önce</div>
                    <div class="rewrite-before">{escape(comparison["before"])}</div>
                    <hr>
                    <div class="rewrite-label">Daha doğru kurulmuş sürüm</div>
                    <div class="rewrite-after">{escape(comparison["after"])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


@st.cache_resource
def load_assets():
    try:
        model_path = Path(__file__).resolve().parent / "model.pkl"
        with model_path.open("rb") as f:
            bundle = pickle.load(f)
        if not isinstance(bundle, dict) or "pipeline" not in bundle:
            raise ValueError("Eski model formatı")
        return bundle, None
    except (OSError, pickle.PickleError, ValueError, AttributeError, EOFError) as exc:
        return None, str(exc)

model_bundle, model_error = load_assets()

DEFAULT_PROFILE = {
    "display_name": "Learner",
    "target_level": "B2",
    "weekly_goal": 3,
    "save_history": 0,
}
storage_enabled = (
    os.getenv("PRO_ENGLISH_AI_STORAGE_MODE", "session").lower() == "local"
)

if storage_enabled:
    try:
        initialize_database()
        storage_error = None
        profile = get_profile() or DEFAULT_PROFILE.copy()
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
        storage_error = str(exc)
        profile = DEFAULT_PROFILE.copy()
else:
    storage_error = None
    if "session_profile" not in st.session_state:
        st.session_state.session_profile = DEFAULT_PROFILE.copy()
    profile = st.session_state.session_profile

if "analysis_history" not in st.session_state:
    try:
        st.session_state.analysis_history = (
            list_analyses(limit=50)
            if storage_enabled and not storage_error
            else []
        )
    except (OSError, ValueError, RuntimeError, sqlite3.Error):
        st.session_state.analysis_history = []
if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = (
        st.session_state.analysis_history[0]
        if st.session_state.analysis_history
        else None
    )
if "assessment_questions" not in st.session_state:
    st.session_state.assessment_questions = []
if "assessment_page" not in st.session_state:
    st.session_state.assessment_page = 0
if "assessment_result" not in st.session_state:
    st.session_state.assessment_result = None
if "session_completed_tasks" not in st.session_state:
    st.session_state.session_completed_tasks = set()

# --- YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-mark">PE</div>
            <h2>Pro English <em>AI</em></h2>
            <p>AI · CEFR · A1-C2</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    app_mode = st.radio(
        "Çalışma Alanı",
        [
            "AI Seviye Analizi",
            "Seviye Değerlendirmesi",
            "Öğrenme Planı",
            "Gelişim Merkezi",
        ],
    )
    report = model_bundle.get("report", {}) if model_bundle else {}
    model_status = "Hazır" if model_bundle else "Kapalı"
    data_mode = "Yerel SQLite" if storage_enabled else "Güvenli oturum"
    st.markdown(
        f"""
        <div class="sidebar-status">
            <div class="status-row">
                <span><i class="status-dot"></i>AI Modeli</span>
                <span class="status-value">{model_status}</span>
            </div>
            <div class="status-row">
                <span>CEFR kapsamı</span><span class="status-value">A1-C2</span>
            </div>
            <div class="status-row">
                <span>Bağımsız test</span>
                <span class="status-value">%{report.get("independent_test_accuracy", 0) * 100:.1f}</span>
            </div>
            <div class="status-row">
                <span>Veri modu</span><span class="status-value">{data_mode}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    safe_display_name = escape(profile["display_name"])
    initials = "".join(
        part[0].upper() for part in profile["display_name"].split()[:2] if part
    ) or "L"
    persistence_label = "Kalıcı profil" if profile["save_history"] else "Gizli oturum"
    st.markdown(
        f"""
        <div class="profile-chip">
            <div class="profile-avatar">{initials}</div>
            <div><b>{safe_display_name}</b>
            <span>Hedef {profile["target_level"]} · {persistence_label}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Profil ve hedefler"):
        with st.form("profile_settings"):
            profile_name = st.text_input(
                "Görünen ad",
                value=profile["display_name"],
                max_chars=40,
            )
            target_level = st.selectbox(
                "Hedef CEFR seviyesi",
                list(LEVEL_PROFILES),
                index=list(LEVEL_PROFILES).index(profile["target_level"]),
            )
            weekly_goal = st.number_input(
                "Haftalık analiz hedefi",
                min_value=1,
                max_value=14,
                value=int(profile["weekly_goal"]),
            )
            save_history_enabled = st.toggle(
                "Geçmişi bu cihazda sakla",
                value=bool(profile["save_history"]) if storage_enabled else False,
                disabled=not storage_enabled,
            )
            profile_submit = st.form_submit_button("Profili Güncelle")
        if profile_submit:
            if storage_enabled and not storage_error:
                update_profile(
                    profile_name,
                    target_level,
                    weekly_goal,
                    save_history_enabled,
                )
            else:
                st.session_state.session_profile = {
                    "display_name": profile_name.strip()[:40] or "Learner",
                    "target_level": target_level,
                    "weekly_goal": int(weekly_goal),
                    "save_history": 0,
                }
            st.rerun()
        if storage_enabled:
            st.caption(
                "Yerel profil bu bilgisayardaki SQLite veritabanında tutulur."
            )
        else:
            st.caption(
                "Genel demo modunda profil ve sonuçlar yalnızca bu tarayıcı "
                "oturumu boyunca tutulur."
            )
        if storage_error:
            st.warning("Yerel profil kullanılamıyor; oturum modunda devam ediliyor.")

# --- BÖLÜM 1: YAPAY ZEKA ANALİZİ ---
if app_mode == "AI Seviye Analizi":
    validation_preview = model_bundle.get("report", {}) if model_bundle else {}
    close_preview = validation_preview.get("within_one_level_accuracy", 0) * 100
    training_samples = validation_preview.get("training_samples", 0)
    st.markdown(
        f"""
        <section class="hero">
            <div class="eyebrow">YAPAY ZEKA DESTEKLİ · CEFR STANDARTLARI</div>
            <h1>Discover Your <em>True</em><br>English Level</h1>
            <p>Yazdığınız İngilizce metni kelime seçimi, karakter örüntüleri ve
            dilsel yapı bakımından analiz ederek CEFR seviyenizi belirler.</p>
            <div class="hero-stats">
                <div class="hero-stat"><strong>6</strong><span>CEFR SEVİYESİ</span></div>
                <div class="hero-stat"><strong>{training_samples:,}</strong><span>EĞİTİM ÖRNEĞİ</span></div>
                <div class="hero-stat"><strong>%{close_preview:.1f}</strong><span>±1 SEVİYE DOĞRULUK</span></div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    render_level_grid()
    st.markdown(
        """
        <div class="trust-strip">
            <div class="trust-item"><span class="trust-icon">P</span>Metinleriniz kalıcı olarak saklanmaz</div>
            <div class="trust-item"><span class="trust-icon">V</span>Bağımsız uzman veri setiyle doğrulandı</div>
            <div class="trust-item"><span class="trust-icon">R</span>Sonuçlar açıklanabilir metriklerle sunulur</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if model_bundle is None:
        st.error("⚠️ Model yüklenemedi. Terminalde `python train.py` çalıştırın.")
        if model_error:
            st.caption(f"Teknik ayrıntı: {model_error}")
        st.stop()

    model = model_bundle["pipeline"]
    levels = model_bundle["levels"]
    validation = model_bundle.get("report", {})

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="section-label">01 · Writing Sample</div>', unsafe_allow_html=True)
        st.subheader("Metninizi analiz edin")
        user_input = st.text_area(
            "İngilizce metni buraya yapıştırın:",
            height=250,
            placeholder=(
                "Write naturally about your work, studies, a recent experience, "
                "or an idea you care about. Aim for at least 50 words."
            ),
        )
        input_word_count = len(user_input.split())
        st.caption(
            f"{input_word_count} kelime · En güvenilir sonuç için 50-150 kelime önerilir."
        )
        analyze_btn = st.button(
            "Akıllı CEFR Analizini Başlat",
            use_container_width=True,
            type="primary",
        )

    with col2:
        if st.session_state.current_analysis is None:
            st.markdown(
                """
                <div class="info-card">
                    <div class="eyebrow">PRO ENGLISH AI ENGINE</div>
                    <h3>Bir seviyeden fazlasını öğrenin</h3>
                    <p>Pro English AI, metninizi çok katmanlı olarak analiz eder ve yalnızca
                    bir CEFR etiketi değil, gelişiminiz için net bir yön sunar.</p>
                    <ul>
                        <li>Tahmini CEFR seviyesi ve olası seviye aralığı</li>
                        <li>Kelime çeşitliliği ve cümle yapısı profili</li>
                        <li>Girdi kalitesi ve sonuç güvenilirliği</li>
                        <li>Bir sonraki seviyeye özel çalışma planı</li>
                    </ul>
                    <p><b>Privacy controls:</b> Kalıcı geçmiş tercihini siz yönetirsiniz.
                    Gizli oturumda metinler veritabanına yazılmaz.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if analyze_btn and not user_input.strip():
        st.warning("Analiz için İngilizce bir metin girin.")

    if analyze_btn and user_input.strip():
        try:
            with st.spinner("CEFR seviyesi ve yazım hataları birlikte inceleniyor..."):
                result = analyze_text(model, levels, user_input)
                result["writing_coach"] = analyze_writing(user_input)
            st.session_state.current_analysis = result
            st.session_state.analysis_history.insert(0, result)
            st.session_state.analysis_history = st.session_state.analysis_history[:50]
            if storage_enabled and profile["save_history"] and not storage_error:
                save_analysis(result)
        except (ValueError, TypeError, RuntimeError, sqlite3.Error) as exc:
            st.error("Analiz şu anda tamamlanamadı. Lütfen metni kontrol edip tekrar deneyin.")
            st.caption(f"Hata kodu: {type(exc).__name__}")

    result = st.session_state.current_analysis
    if result is not None:
        with col2:
            level_color = LEVEL_INFO[result["level"]][1]
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="result-header">
                        <div>
                            <div class="eyebrow">ANALYSIS COMPLETE · CEFR PROFILE</div>
                            <div class="result-level" style="color:{level_color}">{result["level"]}</div>
                            <h3>{result["level_name"]}</h3>
                        </div>
                        <span class="reliability-badge">%{result["reliability"]} güvenilirlik</span>
                    </div>
                    <p style="color:#a8a39a">{result["summary"]}</p>
                    <div class="quality-track">
                        <div class="quality-fill" style="width:{result["quality_score"]}%"></div>
                    </div>
                    <small style="color:#77736c">Girdi kalitesi: {result["quality_label"]}
                    · %{result["quality_score"]}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_cefr_scale(result["level"])

        metrics = result["metrics"]
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("CEFR Aralığı", result["likely_range"])
        m2.metric("Kelime", metrics["word_count"])
        m3.metric("Ort. Cümle", metrics["avg_sent_len"])
        m4.metric("Kelime Çeşitliliği", f"%{metrics['vocabulary_diversity']}")
        m5.metric("Karmaşık Kelime", f"%{metrics['complex_ratio']}")

        focus_items = "".join(f"<li>{item}</li>" for item in result["focus"])
        st.markdown(
            f"""
            <div class="profile-grid">
                <div class="profile-card">
                    <h4>ÖNCELİKLİ GELİŞİM ALANLARI</h4>
                    <ul>{focus_items}</ul>
                </div>
                <div class="profile-card">
                    <h4>SONRAKİ EN İYİ ADIM</h4>
                    <p>{result["next_step"]}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        writing_coach = result.get("writing_coach")
        if writing_coach:
            render_writing_coach(writing_coach)

        report_json = build_report(result, validation)
        download_col, note_col = st.columns([1, 2])
        with download_col:
            st.download_button(
                "Raporu JSON Olarak İndir",
                data=report_json,
                file_name=f"pro-english-ai-{result['level'].lower()}-report.json",
                mime="application/json",
                use_container_width=True,
            )
        with note_col:
            exact = validation.get("independent_test_accuracy", 0) * 100
            close = validation.get("within_one_level_accuracy", 0) * 100
            st.caption(
                f"Model şeffaflığı: bağımsız uzman testinde %{exact:.1f} kesin uyum, "
                f"%{close:.1f} en fazla bir seviye sapma. Sonuç resmi sertifika değildir."
            )

# --- BÖLÜM 2: KENDİNİ TEST ET (SINAV + YANLIŞ ANALİZİ) ---
elif app_mode == "Seviye Değerlendirmesi":
    st.markdown(
        """
        <section class="page-hero">
            <div class="eyebrow">MULTI-SKILL · CEFR ASSESSMENT</div>
            <h1>English Placement Suite</h1>
            <p>Tek bir seviyeyi onaylamak yerine A1-C2 aralığındaki gerçek konumunuzu
            dil bilgisi, kelime ve okuma becerileri üzerinden çok aşamalı olarak ölçün.</p>
        </section>
        <div class="exam-meta">
            <div><b>36 Soru</b>Tam yerleştirme testi</div>
            <div><b>3 Beceri</b>Grammar · Vocabulary · Reading</div>
            <div><b>A1-C2</b>Zorluk duyarlı puanlama</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.assessment_questions and st.session_state.assessment_result is None:
        setup_left, setup_right = st.columns([1.2, .8], gap="large")
        with setup_left:
            assessment_type = st.radio(
                "Değerlendirme türü",
                ["Kapsamlı Seviye Tespit", "Hedef Seviye Kontrolü"],
                horizontal=True,
            )
            check_level = None
            if assessment_type == "Hedef Seviye Kontrolü":
                check_level = st.selectbox(
                    "Kontrol edilecek seviye",
                    ["A1", "A2", "B1", "B2", "C1", "C2"],
                    index=2,
                )
            if assessment_type == "Kapsamlı Seviye Tespit":
                st.info(
                    "36 soru, 3 aşama ve tüm CEFR seviyeleri. İlk kez kullananlar için önerilir."
                )
            else:
                st.info(
                    "18 soru; seçilen seviyenin bir altı, kendisi ve bir üstünü karşılaştırır."
                )

            if st.button(
                "Değerlendirmeyi Başlat",
                type="primary",
                use_container_width=True,
            ):
                for key in list(st.session_state):
                    if key.startswith("assessment_answer_"):
                        del st.session_state[key]
                mode = (
                    "placement"
                    if assessment_type == "Kapsamlı Seviye Tespit"
                    else "level_check"
                )
                st.session_state.assessment_questions = build_assessment(
                    mode,
                    check_level,
                )
                st.session_state.assessment_page = 0
                st.session_state.assessment_result = None
                st.rerun()

        with setup_right:
            st.markdown(
                """
                <div class="info-card">
                    <div class="eyebrow">DEĞERLENDİRME STANDARDI</div>
                    <h3>Daha güvenilir bir ölçüm</h3>
                    <ul>
                        <li>Her seviyede eşit sayıda soru</li>
                        <li>Üç ayrı dil becerisi profili</li>
                        <li>Soru zorluğunu dikkate alan yetenek tahmini</li>
                        <li>Her yanıt için öğretici açıklama</li>
                        <li>Seviye ve alan bazlı ayrıntılı rapor</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

    elif st.session_state.assessment_questions and st.session_state.assessment_result is None:
        questions = st.session_state.assessment_questions
        page_size = 12 if len(questions) == 36 else 6
        total_pages = math.ceil(len(questions) / page_size)
        current_page = st.session_state.assessment_page
        start = current_page * page_size
        end = min(start + page_size, len(questions))
        current_questions = questions[start:end]

        st.markdown(
            f"""
            <div class="assessment-toolbar">
                <span><b>Aşama {current_page + 1}/{total_pages}</b> · Sorular {start + 1}-{end}</span>
                <span>{len(questions)} soruluk değerlendirme</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress((current_page + 1) / total_pages)

        for offset, question in enumerate(current_questions):
            question_number = start + offset + 1
            st.markdown(
                f"""
                <div class="question-meta">
                    <span class="question-tag">{question["level"]}</span>
                    <span class="question-tag">{question["domain"]}</span>
                    <span class="question-tag">Soru {question_number}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(f"**{question['prompt']}**")
            st.radio(
                "Yanıtınızı seçin",
                question["options"],
                index=None,
                key=f"assessment_answer_{question['id']}",
                label_visibility="collapsed",
            )
            st.divider()

        unanswered = [
            question
            for question in current_questions
            if st.session_state.get(f"assessment_answer_{question['id']}") is None
        ]
        back_col, next_col = st.columns([1, 2])
        with back_col:
            if current_page > 0 and st.button("Önceki Aşama", use_container_width=True):
                st.session_state.assessment_page -= 1
                st.rerun()
        with next_col:
            final_page = current_page == total_pages - 1
            action_label = "Değerlendirmeyi Tamamla" if final_page else "Sonraki Aşama"
            if st.button(
                action_label,
                type="primary",
                use_container_width=True,
                disabled=bool(unanswered),
            ):
                if final_page:
                    answers = [
                        st.session_state.get(f"assessment_answer_{question['id']}")
                        for question in questions
                    ]
                    result = score_assessment(questions, answers)
                    result["questions"] = questions
                    result["answers"] = answers
                    st.session_state.assessment_result = result
                    if storage_enabled and profile["save_history"] and not storage_error:
                        try:
                            save_assessment(
                                result["level"],
                                result["correct"],
                                result["total"],
                                details={
                                    "level": result["level"],
                                    "confidence": result["confidence"],
                                    "score_percent": result["score_percent"],
                                    "domain_scores": result["domain_scores"],
                                    "level_scores": result["level_scores"],
                                    "strongest_domain": result["strongest_domain"],
                                    "focus_domain": result["focus_domain"],
                                },
                            )
                        except sqlite3.Error:
                            st.warning("Değerlendirme sonucu yerel profile kaydedilemedi.")
                    st.rerun()
                else:
                    st.session_state.assessment_page += 1
                    st.rerun()
        if unanswered:
            st.caption(f"Devam etmek için bu aşamadaki {len(unanswered)} soruyu yanıtlayın.")

    else:
        result = st.session_state.assessment_result
        st.markdown(
            f"""
            <div class="score-summary">
                <div class="score-number">{result["level"]}</div>
                <div class="score-copy">
                    <b>Önerilen CEFR seviyesi · %{result["confidence"]} ölçüm güveni</b>
                    <p>{result["correct"]}/{result["total"]} doğru · Ham başarı
                    %{result["score_percent"]}. Güçlü alan: {result["strongest_domain"]};
                    öncelikli alan: {result["focus_domain"]}.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_cefr_scale(result["level"])

        domain_cards = "".join(
            f'<div class="domain-card"><strong>%{score}</strong><span>{domain}</span></div>'
            for domain, score in result["domain_scores"].items()
        )
        st.markdown(
            f'<div class="section-label">Beceri Profili</div>'
            f'<div class="domain-grid">{domain_cards}</div>',
            unsafe_allow_html=True,
        )

        level_cards = "".join(
            f"<div><b>%{score}</b>{level}</div>"
            for level, score in result["level_scores"].items()
        )
        st.markdown(
            f'<div class="section-label">Seviye Bazlı Performans</div>'
            f'<div class="level-performance">{level_cards}</div>',
            unsafe_allow_html=True,
        )

        with st.expander("Tüm soruların açıklamalı raporu"):
            for index, (question, answer) in enumerate(
                zip(result["questions"], result["answers"]),
                start=1,
            ):
                correct = answer == question["answer"]
                status = "Doğru" if correct else "Yanlış"
                css_class = "correct" if correct else "wrong"
                st.markdown(
                    f'<div class="answer-card {css_class}"><b>{index}. {status}</b> · '
                    f'Sizin yanıtınız: {escape(str(answer))}<br>'
                    f'Doğru yanıt: <b>{escape(question["answer"])}</b></div>'
                    f'<div class="explanation-card">{escape(question["explanation"])}</div>',
                    unsafe_allow_html=True,
                )

        if st.button("Yeni Değerlendirme Başlat", use_container_width=True):
            for key in list(st.session_state):
                if key.startswith("assessment_answer_"):
                    del st.session_state[key]
            st.session_state.assessment_questions = []
            st.session_state.assessment_page = 0
            st.session_state.assessment_result = None
            st.rerun()

elif app_mode == "Öğrenme Planı":
    history = st.session_state.analysis_history
    latest_assessment = None
    if st.session_state.assessment_result:
        latest_assessment = {"details": st.session_state.assessment_result}
    elif storage_enabled and not storage_error:
        try:
            latest_assessment = get_latest_assessment()
        except sqlite3.Error:
            latest_assessment = None

    context = infer_learning_context(profile, history, latest_assessment)
    plan = generate_weekly_plan(
        context["current_level"],
        context["target_level"],
        context["focus_domain"],
    )
    if storage_enabled and profile["save_history"] and not storage_error:
        try:
            completed_tasks = list_completed_tasks()
        except sqlite3.Error:
            completed_tasks = set()
    else:
        completed_tasks = st.session_state.session_completed_tasks

    completed_count = sum(task["id"] in completed_tasks for task in plan)
    total_minutes = sum(task["minutes"] for task in plan)
    completion_percent = round(completed_count / len(plan) * 100)

    st.markdown(
        """
        <section class="page-hero">
            <div class="eyebrow">PERSONALIZED LEARNING OS</div>
            <h1>Haftalık Öğrenme Planı</h1>
            <p>Analiz ve değerlendirme sonuçlarınızdan oluşturulan kısa, ölçülebilir
            ve tamamlanabilir görevlerle hedef CEFR seviyenize ilerleyin.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="plan-hero">
            <div>
                <h3>{context["current_level"]} seviyesinden {context["target_level"]} hedefine</h3>
                <p>Bu haftanın odağı: <b style="color:#d2ad52">{context["focus_domain"]}</b>
                · Toplam {total_minutes} dakika · {len(plan)} pratik görevi</p>
            </div>
            <div class="plan-score">%{completion_percent}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(completion_percent / 100)

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Tamamlanan", f"{completed_count}/{len(plan)}")
    p2.metric("Haftalık Süre", f"{total_minutes} dk")
    p3.metric("Öncelikli Alan", context["focus_domain"])
    p4.metric("Hedef Seviye", context["target_level"])

    if not history and not latest_assessment:
        st.info(
            "Plan başlangıç profiliyle oluşturuldu. AI analizi veya seviye "
            "değerlendirmesi tamamladığınızda görevler otomatik kişiselleşir."
        )

    st.markdown('<div class="section-label">Bu Haftanın Görevleri</div>', unsafe_allow_html=True)
    for task in plan:
        was_completed = task["id"] in completed_tasks
        check_col, content_col = st.columns([.08, .92])
        with check_col:
            checked = st.checkbox(
                "Tamamlandı",
                value=was_completed,
                key=f"learning_task_{task['id']}",
                label_visibility="collapsed",
            )
        with content_col:
            done_class = " done" if checked else ""
            st.markdown(
                f"""
                <div class="task-card{done_class}">
                    <div class="task-meta">
                        <span>{escape(task["domain"])}</span>
                        <span>{task["minutes"]} dakika</span>
                    </div>
                    <h4>{escape(task["title"])}</h4>
                    <p>{escape(task["description"])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if checked != was_completed:
            if storage_enabled and profile["save_history"] and not storage_error:
                try:
                    set_task_completed(task["id"], checked)
                except sqlite3.Error:
                    st.warning("Görev durumu yerel profile kaydedilemedi.")
            else:
                if checked:
                    st.session_state.session_completed_tasks.add(task["id"])
                else:
                    st.session_state.session_completed_tasks.discard(task["id"])
            st.rerun()

    st.caption(
        "Plan her takvim haftasında yenilenir. Kalıcı geçmiş kapalıysa görev "
        "tamamlama durumu yalnızca bu oturumda korunur."
    )

elif app_mode == "Gelişim Merkezi":
    history = st.session_state.analysis_history
    try:
        dashboard_stats = (
            get_dashboard_stats()
            if storage_enabled and not storage_error
            else {
                "analysis_total": len(history),
                "average_reliability": 0,
                "average_quality": 0,
                "assessment_total": 0,
                "average_assessment_score": 0,
                "weekly_analyses": len(history),
            }
        )
    except sqlite3.Error:
        dashboard_stats = {
            "analysis_total": len(history),
            "average_reliability": 0,
            "average_quality": 0,
            "assessment_total": 0,
            "average_assessment_score": 0,
            "weekly_analyses": len(history),
        }
    st.markdown(
        """
        <section class="page-hero">
            <div class="eyebrow">PERSONAL LEARNING INTELLIGENCE</div>
            <h1>Gelişim Merkezi</h1>
            <p>Bu oturumdaki analizlerinizi karşılaştırın, yazı profilinizdeki
            değişimi izleyin ve bir sonraki çalışma hedefinizi belirleyin.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    weekly_done = dashboard_stats["weekly_analyses"]
    weekly_goal = int(profile["weekly_goal"])
    goal_percent = min(round(weekly_done / weekly_goal * 100), 100)
    progress_source = (
        "bu bilgisayardaki yerel profil"
        if storage_enabled
        else "mevcut tarayıcı oturumu"
    )
    st.markdown(
        f"""
        <div class="goal-card">
            <div class="goal-head">
                <b>Haftalık analiz hedefi</b>
                <span>{weekly_done}/{weekly_goal}</span>
            </div>
            <div class="goal-track">
                <div class="goal-fill" style="width:{goal_percent}%"></div>
            </div>
            <p>Hedef CEFR seviyesi: <b style="color:#d2ad52">{profile["target_level"]}</b>
            · İlerleme {progress_source} üzerinden hesaplanır.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not history:
        st.markdown(
            """
            <div class="info-card">
                <div class="eyebrow">HENÜZ VERİ YOK</div>
                <h3>İlk gelişim kaydınızı oluşturun</h3>
                <p>AI Seviye Analizi alanında bir İngilizce metin analiz ettiğinizde
                sonuç burada görünür. Farklı tarihlerde ve konularda yazılar ekleyerek
                seviyenizi ve dil metriklerinizi karşılaştırabilirsiniz.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        latest = history[0]
        level_values = [item["level_index"] + 1 for item in reversed(history)]
        average_reliability = dashboard_stats["average_reliability"] or round(
            sum(item["reliability"] for item in history) / len(history)
        )
        target_index = list(LEVEL_PROFILES).index(profile["target_level"])
        levels_to_target = max(0, target_index - latest["level_index"])

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Son Seviye", latest["level"])
        c2.metric("Toplam Analiz", dashboard_stats["analysis_total"] or len(history))
        c3.metric("Ort. Güvenilirlik", f"%{average_reliability}")
        c4.metric("Hedefe Mesafe", f"{levels_to_target} seviye")
        c5.metric(
            "Sınav Ortalaması",
            (
                f"%{dashboard_stats['average_assessment_score']}"
                if dashboard_stats["assessment_total"]
                else "Henüz yok"
            ),
        )

        if len(history) > 1:
            st.markdown('<div class="section-label">Seviye Eğilimi</div>', unsafe_allow_html=True)
            st.line_chart(
                {"CEFR seviyesi": level_values},
                height=220,
                use_container_width=True,
            )

        st.markdown('<div class="section-label">Son Analizler</div>', unsafe_allow_html=True)
        for item in history:
            preview = item["text"].replace("\n", " ").strip()
            if len(preview) > 120:
                preview = preview[:117] + "..."
            preview = escape(preview)
            st.markdown(
                f"""
                <div class="history-card">
                    <div class="history-level">{item["level"]}</div>
                    <div class="history-copy">
                        <b style="color:#d8d4cc">{item["level_name"]}</b><br>
                        {preview}
                    </div>
                    <div class="history-meta">
                        %{item["reliability"]} güven<br>
                        {item["metrics"]["word_count"]} kelime
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("Veri ve gizlilik kontrolleri"):
            if storage_enabled:
                st.caption(
                    "Kalıcı profil verileri yalnızca bu bilgisayardaki "
                    "`app_data/pro_english_ai.db` dosyasında tutulur."
                )
                clear_label = "Tüm yerel analiz ve sınav geçmişimi sil"
                button_label = "Yerel Verileri Kalıcı Olarak Sil"
            else:
                st.caption(
                    "Genel demo modunda veriler yalnızca mevcut tarayıcı "
                    "oturumunda tutulur ve sunucu veritabanına yazılmaz."
                )
                clear_label = "Bu oturumdaki analiz geçmişimi temizle"
                button_label = "Oturum Verilerini Temizle"
            confirm_clear = st.checkbox(clear_label)
            if st.button(
                button_label,
                disabled=not confirm_clear,
                use_container_width=False,
            ):
                if storage_enabled and not storage_error:
                    clear_profile_data()
                st.session_state.analysis_history = []
                st.session_state.current_analysis = None
                st.rerun()

# Sayfa Alt Bilgisi
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-footer">
            <b style="color:#a8a39a">Pro English AI & Academy</b><br>
            Bayram ÖZTÜRK · Ozan KARAALİ<br>
            Mustafa Serhat EKER · Eray KATI
        </div>
        """,
        unsafe_allow_html=True,
    )
