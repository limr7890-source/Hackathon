import streamlit as st
import datetime
import json
import csv
import os
import time
import pandas as pd
import streamlit.components.v1 as components

# ייבוא פונקציית הדירקטוריון מקובץ ה-dashboard.py שלך
try:
    from dashboard import render_analytics_dashboard
except ImportError:
    st.error("Error: Could not import dashboard.py. Please ensure it is in the same folder.")
    st.stop()

# הגדרת דף ראשוני - מתבצעת פעם אחת בלבד עבור האפליקציה כולה
st.set_page_config(page_title="TagAlign AI", layout="wide", initial_sidebar_state="expanded")

# ─── HEARTBEAT SHUTDOWN MECHANISM ───────────────────────────────────────────
import threading
if 'last_heartbeat' not in st.session_state:
    st.session_state['last_heartbeat'] = time.time()
if 'shutdown_watcher_started' not in st.session_state:
    st.session_state['shutdown_watcher_started'] = False

query_params = st.query_params

if "heartbeat" in query_params:
    st.session_state['last_heartbeat'] = time.time()
    st.stop()  

def _shutdown_watcher():
    while True:
        time.sleep(2)
        age = time.time() - st.session_state.get('last_heartbeat', time.time())
        if age > 8:
            os._exit(0)

if not st.session_state['shutdown_watcher_started']:
    t = threading.Thread(target=_shutdown_watcher, daemon=True)
    t.start()
    st.session_state['shutdown_watcher_started'] = True

components.html("""
<script>
setInterval(function() {
    fetch(window.location.href.split('?')[0] + '?heartbeat=1', { method: 'GET' });
}, 3000);
</script>
""", height=0, width=0)

# ─── OUTPUT FILE PATH ────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_JSON_PATH = os.path.join(OUTPUT_DIR, "tagalign_input.json")
OUTPUT_CSV_PATH  = os.path.join(OUTPUT_DIR, "tagalign_input.csv")

def save_for_crew(hashtags, urls, region, start_date, end_date, max_posts):
    payload = {
        "exported_at": datetime.datetime.now().isoformat(),
        "config": {"region": region, "start_date": str(start_date), "end_date": str(end_date), "max_posts": max_posts},
        "hashtags": hashtags,
        "seed_urls": urls,
    }
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    max_len = max(len(hashtags), len(urls))
    
    with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Target_Hashtags", "Approved_Seed_URL", "Region", "Start_Date", "End_Date", "Max_Posts"])
        
        for i in range(max_len):
            tag = hashtags[i] if i < len(hashtags) else ""
            url = urls[i] if i < len(urls) else ""
            w.writerow([tag, url, region, str(start_date), str(end_date), max_posts])

# ─── SESSION STATE DEFAULTS ──────────────────────────────────────────────────
if 'app_mode' not in st.session_state:
    st.session_state['app_mode'] = 'HOME'  # ברירת מחדל קבועה למסך הבית
if 'hashtags_list' not in st.session_state:
    st.session_state['hashtags_list'] = ["#JustDoIt"]
if 'urls_list' not in st.session_state:
    st.session_state['urls_list'] = ["https://x.com/nike/status/123456789"]

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #dbeafe 100%);
    background-size: 300% 300% !important;
    animation: darkTechGradient 12s ease infinite !important;
}
@keyframes darkTechGradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
[data-testid="stSidebar"] {
    background: rgba(251, 146, 60, 0.15) !important;
    backdrop-filter: blur(15px);
    border-right: 1px solid #fb923c;
}
.hero-title {
    font-family: 'Inter', sans-serif; font-weight: 800; font-size: 64px;
    letter-spacing: -2.5px;
    background: linear-gradient(135deg, #ea580c 0%, #fb923c 50%, #fdba74 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-top: 50px; margin-bottom: 5px;
}
.hero-subtitle {
    font-family: 'Inter', sans-serif; font-weight: 700; color: #ea580c !important;
    font-size: 14px; margin-bottom: 50px; text-transform: uppercase; letter-spacing: 2.5px;
}
.floating-title { color: #78350f !important; font-family: 'Inter', sans-serif; font-weight: 800; font-size: 34px; margin-bottom: 15px; }
.floating-desc { color: #78350f !important; font-family: 'Inter', sans-serif; font-weight: 600; font-size: 18px; line-height: 1.6 !important; }
.highlight-purple { color: #ea580c !important; font-weight: 800; }
.highlight-pink { color: #c2410c !important; font-weight: 800; }

.cube-section-title {
    font-family: 'Inter', sans-serif; font-weight: 700; font-size: 13px;
    text-transform: uppercase; letter-spacing: 2px; color: #ea580c !important;
    margin-bottom: 12px; display: block;
}
.cube-item {
    background: rgba(255,255,255,0.8); border: 1.5px solid rgba(251, 146, 60, 0.5);
    border-radius: 12px; padding: 10px 12px; display: flex; align-items: center;
    justify-content: space-between; gap: 8px; min-height: 48px; margin-bottom: 8px;
}
.cube-item-text { font-family: 'Inter', sans-serif; font-weight: 600; font-size: 13px; color: #78350f !important; word-break: break-all; flex: 1; }
.cube-item-required { font-family: 'Inter', sans-serif; font-size: 10px; color: #ea580c !important; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; }

div.stButton > button:first-child {
    background: linear-gradient(135deg, #fb923c 0%, #fdba74 100%) !important;
    color: #ffffff !important; border-radius: 14px; border: none; padding: 16px 52px;
    font-family: 'Inter', sans-serif; font-weight: 800; font-size: 18px;
    box-shadow: 0 8px 0px #ea580c, 0 15px 25px rgba(251, 146, 60, 0.3);
    transition: all 0.15s ease;
}
div.stButton > button:first-child:hover { transform: translateY(2px); box-shadow: 0 6px 0px #ea580c; }

.menu-item { padding: 12px 0; font-family: 'Inter', sans-serif; font-weight: 700; color: #94a3b8; font-size: 14.5px; }

h3 {
    color: #c2410c !important;
    font-family: 'Inter', sans-serif;
    font-weight: 900 !important;
    font-size: 20px !important;
}

.stTabs [data-baseweb="tab-list"] button {
    color: #c2410c !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #ea580c !important;
    font-weight: 800 !important;
}

.floating-chart-3d {
    position: absolute; top: 25%; right: 6%; display: flex; align-items: flex-end; gap: 8px;
    background: rgba(251, 146, 60, 0.2); backdrop-filter: blur(8px); border: 1px solid #fb923c;
    padding: 24px; border-radius: 20px; animation: floatObject1 6s ease-in-out infinite; z-index: 1;
}
.chart-bar { width: 16px; border-radius: 4px; background: linear-gradient(to top, #fb923c, #fdba74); }
.bar-1{height:45px}.bar-2{height:85px}.bar-3{height:60px}.bar-4{height:110px}
.floating-trend-line {
    position: absolute; bottom: 15%; right: 24%; width: 140px; height: 70px;
    background: rgba(251, 146, 60, 0.2); border: 1px solid #fb923c; border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    animation: floatObject2 8s ease-in-out infinite; z-index: 1;
}
.factory-bubble {
    position: absolute; background: rgba(251, 146, 60, 0.3); border-radius: 50%;
    border: 1px solid #fb923c; display: flex; flex-direction: column;
    justify-content: center; align-items: center; z-index: 1; pointer-events: none; opacity: 0;
}
.trend-tag{font-weight:800;font-size:12px;color:#ffffff !important}
.trend-stat{font-size:11px;font-weight:800;color:#fdba74 !important}

@keyframes verticalRightPipeline {
    0%{transform:translateY(110vh) scale(0.5);opacity:0}
    15%{opacity:1}
    85%{transform:translateY(5vh) scale(1.1);opacity:1}
    92%{opacity:0}
    100%{transform:translateY(-5vh) scale(0);opacity:0}
}
.b-1{width:125px;height:125px;right:6%;animation:verticalRightPipeline 12s linear infinite}
.b-2{width:140px;height:140px;right:18%;animation:verticalRightPipeline 15s linear infinite}
@keyframes floatObject1{0%,100%{transform:translateY(0px) rotate(3deg)}50%{transform:translateY(-18px) rotate(-2deg)}}
@keyframes floatObject2{0%,100%{transform:translateY(0px) rotate(-4deg)}50%{transform:translateY(22px) rotate(4deg)}}

/* ⭐ עיצוב שדות קלט יציב ונקי בגוון OFF-WHITE ⭐ */

/* 1. תיבת הבחירה (Geographic Region) */
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: #fcfbfa !important;
    color: #78350f !important;
    border: 1.5px solid rgba(251, 146, 60, 0.4) !important;
    border-radius: 10px !important;
    outline: none !important;
}

/* 2. שדות הטקסט (Hashtags / URLs) וניקוי צלליות פנימיות */
div[data-testid="stTextInput"] div[data-baseweb="base-input"],
div[data-testid="stTextInput"] input {
    background-color: #fcfbfa !important;
    color: #78350f !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}
div[data-testid="stTextInput"] [data-baseweb="base-input"] {
    border: 1.5px solid rgba(251, 146, 60, 0.4) !important;
    border-radius: 10px !important;
    background-color: #fcfbfa !important;
}

/* 3. שדות הזנת תאריכים (From / To) */
div[data-testid="stDateInput"] div[data-baseweb="input"],
div[data-testid="stDateInput"] [data-baseweb="base-input"] {
    background-color: #fcfbfa !important;
    border: 1.5px solid rgba(251, 146, 60, 0.4) !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    outline: none !important;
}
div[data-testid="stDateInput"] input {
    background-color: transparent !important;
    color: #78350f !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

/* 4. התאמות פונטים, פלייסהולדרים וחצים */
div[data-testid="stTextInput"] input::placeholder {
    color: #94a3b8 !important;
}
div[data-testid="stSelectbox"] svg {
    fill: #78350f !important;
}
[data-testid="stWidgetLabel"] p {
    color: #ea580c !important;
    font-weight: 700 !important;
}

div[data-testid="stTextInput"] [data-baseweb="base-input"]:focus-within,
div[data-testid="stDateInput"] [data-baseweb="base-input"]:focus-within {
    border-color: #ea580c !important;
    box-shadow: none !important;
}

/* 📏 הקטנה וסימטריה של כפתור ה-"＋ Add" */
div[data-testid="stColumn"] button[key*="add_"] {
    padding: 10px 20px !important;
    min-height: 42px !important;
    font-size: 14px !important;
    border-radius: 10px !important;
    margin-top: 0px !important;
}
</style>
""", unsafe_allow_html=True)


# ─── CUBE LIST RENDERER ──────────────────────────────────────────────────────
def render_cube_list(items, key_prefix, min_one=True):
    to_remove = None
    for i, item in enumerate(items):
        label = item if len(item) <= 30 else item[:28] + "…"
        is_first = (i == 0)
        col_txt, col_btn = st.columns([5, 1])
        with col_txt:
            badge = '<span class="cube-item-required">required</span>' if is_first else ""
            st.markdown(
                f'<div class="cube-item">'
                f'<span class="cube-item-text">{label}</span>{badge}'
                f'</div>',
                unsafe_allow_html=True
            )
        with col_btn:
            can_remove = not (min_one and i == 0)
            if can_remove:
                if st.button("−", key=f"{key_prefix}_rm_{i}", help="Remove"):
                    to_remove = i
            else:
                st.markdown("<div style='height:42px'></div>", unsafe_allow_html=True)
    if to_remove is not None:
        items.pop(to_remove)
        st.rerun()


# ─── NAVIGATION SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='color:#fff;font-weight:800;letter-spacing:-1px'>🔮 Navigation</h2>", unsafe_allow_html=True)
    st.divider()
    
    if st.button(" Home Overview", use_container_width=True, key="nav_home"):
        st.session_state['app_mode'] = 'HOME'
        st.rerun()
        
    if st.button(" Campaign Config", use_container_width=True, key="nav_config"):
        st.session_state['app_mode'] = 'CONFIG'
        st.rerun()
        
    if st.button(" Real-Time Analytics", use_container_width=True, key="nav_dashboard"):
        if 'analysis_config' in st.session_state:
            st.session_state['app_mode'] = 'DASHBOARD'
            st.rerun()
        else:
            st.warning("Please configure analysis first.")


# ─── 1. HOME MODE ────────────────────────────────────────────────────────────
if st.session_state['app_mode'] == 'HOME':
    st.markdown("""
        <div class="floating-chart-3d">
            <div class="chart-bar bar-1"></div><div class="chart-bar bar-2"></div>
            <div class="chart-bar bar-3"></div><div class="chart-bar bar-4"></div>
        </div>
        <div class="floating-trend-line">
            <svg width="100" height="40" viewBox="0 0 100 40" fill="none">
                <path d="M5 35 L30 25 L55 28 L75 10 L95 5" stroke="#fb923c" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="95" cy="5" r="5" fill="#fdba74" stroke="#fff" stroke-width="2"/>
            </svg>
        </div>
        <div class="factory-bubble b-1"><div class="trend-tag">⚽ #WorldCup</div><div class="trend-stat">94.2%</div></div>
        <div class="factory-bubble b-2"><div class="trend-tag">🤖 #GPT5</div><div class="trend-stat">88.7%</div></div>
    """, unsafe_allow_html=True)

    col_content, _ = st.columns([2.5, 1])
    with col_content:
        st.markdown('<h1 class="hero-title">TagAlign AI</h1>', unsafe_allow_html=True)
        st.markdown('<p class="hero-subtitle">Semantic Content Alignment Infrastructure</p>', unsafe_allow_html=True)
        st.markdown("""
            <div style="margin-bottom:50px">
                <div class="floating-title">From Creative Idea Into Real Analytics</div>
                <div class="floating-desc">
                    By extracting <span class="highlight-purple">semantic footprints</span> from your approved
                    influencer baseline seeds, our engine cross-references live social streams via
                    <span class="highlight-pink">Bright Data</span> to measure real-world campaign execution.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Proceed to Data Analysis", key="hero_proceed"):
            st.session_state['app_mode'] = 'CONFIG'
            st.rerun()


# ─── 2. CONFIGURATION MODE ───────────────────────────────────────────────────
elif st.session_state['app_mode'] == 'CONFIG':
    st.markdown("<h2 style='color:#78350f; font-family:Inter,sans-serif;'>Configure Analysis Infrastructure</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#78320f;font-family:Inter,sans-serif;font-size:14px'>Set up tracking parameters and seed content below.</p>", unsafe_allow_html=True)
    st.divider()

    col_config, col_dynamic = st.columns([1, 1.5], gap="large")

    with col_config:
        st.markdown('### Feed Parameters')
        st.markdown("<p style='color:#ea580c; font-family:Inter,sans-serif; font-weight:700; font-size:14px; margin-bottom: 0px; padding-bottom: 0px;'>Geographic Region</p>", unsafe_allow_html=True)
        region = st.selectbox("", ["Worldwide","United States","Europe","Israel","Asia"], label_visibility="collapsed", key="field_region")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<p style='color:#ea580c; font-family:Inter,sans-serif; font-weight:700; font-size:14px; margin-bottom: 0px; padding-bottom: 0px;'>From</p>", unsafe_allow_html=True)
            start_date = st.date_input("", datetime.date.today() - datetime.timedelta(days=2), label_visibility="collapsed", key="field_start")
        with c2:
            st.markdown("<p style='color:#ea580c; font-family:Inter,sans-serif; font-weight:700; font-size:14px; margin-bottom: 0px; padding-bottom: 0px;'>To</p>", unsafe_allow_html=True)
            end_date = st.date_input("", datetime.date.today(), label_visibility="collapsed", key="field_end")
        
        st.markdown("<p style='color:#ea580c; font-family:Inter,sans-serif; font-weight:700; font-size:14px; margin-bottom: 5px; padding-bottom: 0px;'>Max Posts</p>", unsafe_allow_html=True)
        max_posts = st.slider("", 500, 10000, 2000, step=500, label_visibility="collapsed", key="field_slider")

    with col_dynamic:
        st.markdown("<h3 style='color:#c2410c !important; font-family:Inter,sans-serif; font-weight:900; font-size:20px; margin-bottom: 5px;'>Input Seeds</h3>", unsafe_allow_html=True)
        tab_tags, tab_urls = st.tabs(["# Hashtags", "🔗 Seed URLs"])

        with tab_tags:
            st.markdown(f'<span class="cube-section-title">{len(st.session_state["hashtags_list"])} hashtag(s)</span>', unsafe_allow_html=True)
            render_cube_list(st.session_state['hashtags_list'], "ht")
            
            a1, b1 = st.columns([4, 1])
            with a1:
                new_tag = st.text_input("Add hashtag", placeholder="#YourHashtag", key="new_tag_field", label_visibility="collapsed")
            with b1:
                if st.button("＋ Add", key="add_tag_action"):
                    val = new_tag.strip()
                    if val:
                        if not val.startswith("#"):
                            val = "#" + val
                        if val not in st.session_state['hashtags_list']:
                            st.session_state['hashtags_list'].append(val)
                            st.rerun()

        with tab_urls:
            st.markdown(f'<span class="cube-section-title">{len(st.session_state["urls_list"])} URL(s)</span>', unsafe_allow_html=True)
            render_cube_list(st.session_state['urls_list'], "url")
            
            a2, b2 = st.columns([4, 1])
            with a2:
                new_url = st.text_input("Add URL", placeholder="https://x.com/...", key="new_url_field", label_visibility="collapsed")
            with b2:
                if st.button("＋ Add", key="add_url_action"):
                    val = new_url.strip()
                    if val and val not in st.session_state['urls_list']:
                        st.session_state['urls_list'].append(val)
                        st.rerun()

    st.divider()

    if st.button("🚀 Run Semantic Analysis", use_container_width=True, key="action_run"):
        if not st.session_state['hashtags_list'] or not st.session_state['urls_list']:
            st.error("❌ Need at least one hashtag and one URL.")
        else:
            save_for_crew(
                st.session_state['hashtags_list'],
                st.session_state['urls_list'],
                region, start_date, end_date, max_posts
            )
            st.session_state['analysis_config'] = {
                "region": region,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "max_posts": max_posts,
                "hashtags": list(st.session_state['hashtags_list']),
                "seed_urls": list(st.session_state['urls_list']),
            }
            st.session_state['app_mode'] = 'DASHBOARD'
            st.rerun()


# ─── 3. DASHBOARD MODE ───────────────────────────────────────────────────────
elif st.session_state['app_mode'] == 'DASHBOARD':
    # הפעלה נקייה של הדאשבורד מתוך הקובץ החיצוני
    render_analytics_dashboard()