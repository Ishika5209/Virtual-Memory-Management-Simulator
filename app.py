import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from fragmentation import fragmentation
from segmentation import segmentation
from optimal import optimal
from lru import lru
from paging import fifo_paging

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Virtual Memory Simulator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #050a14 !important;
    color: #e2e8f0;
    font-family: 'Syne', sans-serif;
}

[data-testid="stSidebar"] {
    background: #080f1e !important;
    border-right: 1px solid #1e2d47;
}

[data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem; }

/* ── Hero Banner ── */
.hero {
    background: linear-gradient(135deg, #0f2240 0%, #0d1b35 50%, #091527 100%);
    border: 1px solid #1e3a5f;
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(99,179,237,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #63b3ed, #76e4f7, #b794f4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.6rem;
}
.hero-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: #4a6fa5;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ── Section Headers ── */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #63b3ed;
    margin: 2rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1e3a5f, transparent);
}

/* ── Metric Cards ── */
.metric-row { display: flex; gap: 1rem; margin: 1.2rem 0; flex-wrap: wrap; }
.metric-card {
    background: #0d1b2e;
    border: 1px solid #1e3558;
    border-radius: 14px;
    padding: 1.2rem 1.6rem;
    flex: 1;
    min-width: 130px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.metric-card.blue::before  { background: linear-gradient(90deg, #63b3ed, #76e4f7); }
.metric-card.purple::before{ background: linear-gradient(90deg, #b794f4, #d6bcfa); }
.metric-card.green::before { background: linear-gradient(90deg, #68d391, #9ae6b4); }
.metric-card.orange::before{ background: linear-gradient(90deg, #f6ad55, #fbd38d); }
.metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a6fa5;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #e2e8f0;
    line-height: 1;
}
.metric-sub {
    font-size: 0.72rem;
    color: #4a6fa5;
    margin-top: 0.2rem;
}

/* ── Step Table ── */
.step-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.step-table th {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a6fa5;
    padding: 0.6rem 1rem;
    text-align: left;
    border-bottom: 1px solid #1e3558;
}
.step-table td {
    padding: 0.55rem 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    border-bottom: 1px solid #0d1b2e;
    color: #a0b8d8;
}
.step-table tr:hover td { background: #0d1b2e; color: #e2e8f0; }
.fault-yes { color: #fc8181 !important; font-weight: 700; }
.fault-no  { color: #68d391 !important; }
.frame-pill {
    display: inline-block;
    background: #1a2f4e;
    border: 1px solid #2d4a6e;
    border-radius: 6px;
    padding: 2px 8px;
    margin: 1px;
    font-size: 0.75rem;
    color: #76e4f7;
}

/* ── Info Box ── */
.info-box {
    background: #0a1628;
    border: 1px solid #1e3558;
    border-left: 3px solid #63b3ed;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    margin: 1rem 0;
    font-size: 0.85rem;
    color: #7fa8c9;
    line-height: 1.6;
}

/* ── Seg/Frag result card ── */
.result-card {
    background: #0a1628;
    border: 1px solid #1e3558;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin: 0.5rem 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    color: #a0b8d8;
}
.result-card.success { border-left: 3px solid #68d391; }
.result-card.error   { border-left: 3px solid #fc8181; }
.result-card.warning { border-left: 3px solid #f6ad55; }

/* ── Sidebar labels ── */
.sidebar-section {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #2d4a6e;
    margin: 1.5rem 0 0.5rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #1e2d47;
}

/* ── Streamlit overrides ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background-color: #0a1628 !important;
    border: 1px solid #1e3558 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #63b3ed !important;
    box-shadow: 0 0 0 2px rgba(99,179,237,0.15) !important;
}

label, .stSelectbox label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #4a6fa5 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #1a3a6e, #0f2240) !important;
    color: #63b3ed !important;
    border: 1px solid #2d5a9e !important;
    border-radius: 10px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    height: 42px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2d5a9e, #1a3a6e) !important;
    border-color: #63b3ed !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(99,179,237,0.2) !important;
}

/* Tab styling */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1e3558;
    gap: 0;
}
[data-baseweb="tab"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #4a6fa5 !important;
    background: transparent !important;
    border: none !important;
    padding: 0.7rem 1.5rem !important;
}
[aria-selected="true"] {
    color: #63b3ed !important;
    border-bottom: 2px solid #63b3ed !important;
}
[data-testid="stDivider"] { border-color: #1e3558 !important; }

/* Plotly chart background fix */
.js-plotly-plot { border-radius: 12px; overflow: hidden; }

.block-container { padding: 1.5rem 2rem 3rem 2rem !important; max-width: 1400px; }
</style>
""", unsafe_allow_html=True)


# ─── Helper: render history table ───────────────────────────────────────────────
def render_history_table(pages, history, frames):
    rows_html = ""
    prev = []
    for i, state in enumerate(history):
        page = pages[i]
        is_fault = page not in prev
        fault_html = '<span class="fault-yes">✗ FAULT</span>' if is_fault else '<span class="fault-no">✓ HIT</span>'
        frames_html = "".join(f'<span class="frame-pill">{p}</span>' for p in state)
        # pad empty frames
        for _ in range(frames - len(state)):
            frames_html += '<span class="frame-pill" style="opacity:0.2">—</span>'
        rows_html += f"""
        <tr>
            <td style="color:#4a6fa5">{i+1}</td>
            <td style="color:#76e4f7;font-weight:700">{page}</td>
            <td>{frames_html}</td>
            <td>{fault_html}</td>
        </tr>"""
        prev = state.copy()

    return f"""
    <table class="step-table">
        <thead><tr>
            <th>Step</th><th>Page Req.</th><th>Memory Frames</th><th>Status</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table>"""


# ─── Helper: plotly bar chart ────────────────────────────────────────────────────
def make_comparison_chart(labels, values, colors):
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0)', width=0),
            cornerradius=8
        ),
        text=values,
        textposition='outside',
        textfont=dict(family='Space Mono', size=14, color='#e2e8f0'),
        width=0.45
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Space Mono', color='#4a6fa5'),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color='#7fa8c9')),
        yaxis=dict(showgrid=True, gridcolor='#0d1b2e', tickfont=dict(size=10, color='#4a6fa5'), title='Page Faults'),
        margin=dict(t=40, b=20, l=40, r=20),
        height=320,
        showlegend=False,
    )
    return fig


# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 1.5rem;">
        <div style="font-size:2.2rem">🧠</div>
        <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.1rem;color:#63b3ed;">VMemSim</div>
        <div style="font-family:'Space Mono',monospace;font-size:0.6rem;color:#2d4a6e;letter-spacing:2px;">VIRTUAL MEMORY SIMULATOR</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Paging Inputs</div>', unsafe_allow_html=True)
    pages_input = st.text_input("Page Reference String", "7,0,1,2,0,3,0,4", key="pages_input")
    frames = st.number_input("Number of Frames", min_value=1, max_value=10, value=3, key="frames_input")

    st.markdown('<div class="sidebar-section">Segmentation</div>', unsafe_allow_html=True)
    seg_num = st.number_input("Segment Number", min_value=0, max_value=2, value=0)
    seg_offset = st.number_input("Offset", min_value=0, value=100)

    st.markdown('<div class="sidebar-section">Fragmentation</div>', unsafe_allow_html=True)
    memory_input = st.text_input("Memory Blocks", "100,500,200,300,600")
    process_input = st.text_input("Process Sizes", "212,417,112,426")

    st.markdown("""
    <div style="margin-top:2rem;padding:1rem;background:#060e1c;border-radius:10px;border:1px solid #1e2d47;">
        <div style="font-family:'Space Mono',monospace;font-size:0.6rem;letter-spacing:2px;color:#2d4a6e;margin-bottom:0.5rem;">ABOUT</div>
        <div style="font-size:0.75rem;color:#4a6fa5;line-height:1.6;">
            Simulates page replacement (FIFO, LRU, Optimal), memory segmentation, and fragmentation allocation.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Parse inputs ────────────────────────────────────────────────────────────────
try:
    pages = list(map(int, pages_input.split(",")))
except:
    pages = [7, 0, 1, 2, 0, 3, 0, 4]

try:
    memory_blocks = list(map(int, memory_input.split(",")))
    process_sizes = list(map(int, process_input.split(",")))
except:
    memory_blocks = [100, 500, 200, 300, 600]
    process_sizes = [212, 417, 112, 426]

segment_table = [(1000, 400), (2000, 300), (3000, 500)]


# ─── HERO ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">Virtual Memory Simulator</div>
    <div class="hero-sub">⬡ Paging &nbsp;·&nbsp; Segmentation &nbsp;·&nbsp; Fragmentation</div>
</div>
""", unsafe_allow_html=True)


# ─── TABS ────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📄 &nbsp;Paging Algorithms", "🧩 &nbsp;Segmentation", "🧱 &nbsp;Fragmentation"])


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 1 — PAGING
# ══════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Select Algorithm</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    fifo_btn    = col1.button("⟳ &nbsp;FIFO",    use_container_width=True)
    lru_btn     = col2.button("⊙ &nbsp;LRU",     use_container_width=True)
    optimal_btn = col3.button("★ &nbsp;Optimal", use_container_width=True)
    compare_btn = col4.button("≡ &nbsp;Compare All", use_container_width=True)

    st.markdown('<div class="info-box">Configure your <b>Page Reference String</b> and <b>Number of Frames</b> in the sidebar, then click an algorithm above.</div>', unsafe_allow_html=True)

    # ── FIFO ──
    if fifo_btn:
        faults, history = fifo_paging(pages, frames)
        hits = len(pages) - faults
        hit_rate = round(hits / len(pages) * 100, 1)

        st.markdown('<div class="section-header">FIFO — Results</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card blue">
                <div class="metric-label">Page Faults</div>
                <div class="metric-value">{faults}</div>
                <div class="metric-sub">out of {len(pages)} references</div>
            </div>
            <div class="metric-card green">
                <div class="metric-label">Page Hits</div>
                <div class="metric-value">{hits}</div>
                <div class="metric-sub">successful lookups</div>
            </div>
            <div class="metric-card purple">
                <div class="metric-label">Hit Rate</div>
                <div class="metric-value">{hit_rate}%</div>
                <div class="metric-sub">efficiency score</div>
            </div>
            <div class="metric-card orange">
                <div class="metric-label">Frames</div>
                <div class="metric-value">{frames}</div>
                <div class="metric-sub">memory slots</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Step-by-Step Memory Trace</div>', unsafe_allow_html=True)
        st.markdown(render_history_table(pages, history, frames), unsafe_allow_html=True)

    # ── LRU ──
    if lru_btn:
        faults, history = lru(pages, frames)
        hits = len(pages) - faults
        hit_rate = round(hits / len(pages) * 100, 1)

        st.markdown('<div class="section-header">LRU — Results</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card blue">
                <div class="metric-label">Page Faults</div>
                <div class="metric-value">{faults}</div>
                <div class="metric-sub">out of {len(pages)} references</div>
            </div>
            <div class="metric-card green">
                <div class="metric-label">Page Hits</div>
                <div class="metric-value">{hits}</div>
                <div class="metric-sub">successful lookups</div>
            </div>
            <div class="metric-card purple">
                <div class="metric-label">Hit Rate</div>
                <div class="metric-value">{hit_rate}%</div>
                <div class="metric-sub">efficiency score</div>
            </div>
            <div class="metric-card orange">
                <div class="metric-label">Frames</div>
                <div class="metric-value">{frames}</div>
                <div class="metric-sub">memory slots</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Step-by-Step Memory Trace</div>', unsafe_allow_html=True)
        st.markdown(render_history_table(pages, history, frames), unsafe_allow_html=True)

    # ── OPTIMAL ──
    if optimal_btn:
        faults, history = optimal(pages, frames)
        hits = len(pages) - faults
        hit_rate = round(hits / len(pages) * 100, 1)

        st.markdown('<div class="section-header">Optimal — Results</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card blue">
                <div class="metric-label">Page Faults</div>
                <div class="metric-value">{faults}</div>
                <div class="metric-sub">out of {len(pages)} references</div>
            </div>
            <div class="metric-card green">
                <div class="metric-label">Page Hits</div>
                <div class="metric-value">{hits}</div>
                <div class="metric-sub">successful lookups</div>
            </div>
            <div class="metric-card purple">
                <div class="metric-label">Hit Rate</div>
                <div class="metric-value">{hit_rate}%</div>
                <div class="metric-sub">efficiency score</div>
            </div>
            <div class="metric-card orange">
                <div class="metric-label">Frames</div>
                <div class="metric-value">{frames}</div>
                <div class="metric-sub">memory slots</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Step-by-Step Memory Trace</div>', unsafe_allow_html=True)
        st.markdown(render_history_table(pages, history, frames), unsafe_allow_html=True)

    # ── COMPARE ──
    if compare_btn:
        fifo_f, _    = fifo_paging(pages, frames)
        lru_f, _     = lru(pages, frames)
        optimal_f, _ = optimal(pages, frames)

        best = min(fifo_f, lru_f, optimal_f)
        worst = max(fifo_f, lru_f, optimal_f)

        st.markdown('<div class="section-header">Algorithm Comparison</div>', unsafe_allow_html=True)

        col_a, col_b = st.columns([3, 2])

        with col_a:
            fig = make_comparison_chart(
                ["FIFO", "LRU", "Optimal"],
                [fifo_f, lru_f, optimal_f],
                ["#63b3ed", "#b794f4", "#68d391"]
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col_b:
            st.markdown(f"""
            <div style="padding:0.5rem 0;">
            <div class="metric-card blue" style="margin-bottom:0.8rem">
                <div class="metric-label">FIFO Faults</div>
                <div class="metric-value" style="font-size:1.8rem">{fifo_f}</div>
            </div>
            <div class="metric-card purple" style="margin-bottom:0.8rem">
                <div class="metric-label">LRU Faults</div>
                <div class="metric-value" style="font-size:1.8rem">{lru_f}</div>
            </div>
            <div class="metric-card green">
                <div class="metric-label">Optimal Faults</div>
                <div class="metric-value" style="font-size:1.8rem">{optimal_f}</div>
            </div>
            </div>
            """, unsafe_allow_html=True)

        # Winner callout
        winner = ["FIFO", "LRU", "Optimal"][[fifo_f, lru_f, optimal_f].index(best)]
        st.markdown(f"""
        <div class="info-box" style="border-left-color:#68d391;margin-top:1rem;">
            🏆 &nbsp;<b>{winner}</b> performs best with <b>{best} page faults</b> on this reference string.
            {"&nbsp; All algorithms tie!" if fifo_f == lru_f == optimal_f else ""}
        </div>
        """, unsafe_allow_html=True)

        # Side-by-side trace table
        st.markdown('<div class="section-header">Side-by-Side Trace</div>', unsafe_allow_html=True)
        _, fifo_hist    = fifo_paging(pages, frames)
        _, lru_hist     = lru(pages, frames)
        _, optimal_hist = optimal(pages, frames)

        rows = []
        for i in range(len(pages)):
            rows.append({
                "Step": i + 1,
                "Page": pages[i],
                "FIFO Frames": str(fifo_hist[i]),
                "LRU Frames": str(lru_hist[i]),
                "Optimal Frames": str(optimal_hist[i]),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 2 — SEGMENTATION
# ══════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Segment Table</div>', unsafe_allow_html=True)

    # Render segment table
    seg_rows = ""
    for idx, (base, limit) in enumerate(segment_table):
        seg_rows += f"""<tr>
            <td style="color:#76e4f7">{idx}</td>
            <td>{base}</td>
            <td>{limit}</td>
            <td style="color:#4a6fa5">{base} – {base + limit - 1}</td>
        </tr>"""

    st.markdown(f"""
    <table class="step-table">
        <thead><tr>
            <th>Segment</th><th>Base Address</th><th>Limit</th><th>Address Range</th>
        </tr></thead>
        <tbody>{seg_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Address Translation</div>', unsafe_allow_html=True)

    if st.button("⟶ &nbsp;Calculate Physical Address", use_container_width=False):
        result = segmentation(segment_table, seg_num, seg_offset)

        if result == "Segmentation Fault":
            st.markdown(f"""
            <div class="result-card error">
                ✗ &nbsp;<b>Segmentation Fault</b><br>
                <span style="color:#4a6fa5">Segment {seg_num} · Offset {seg_offset} exceeds limit {segment_table[seg_num][1]}</span>
            </div>
            """, unsafe_allow_html=True)
        elif result == "Invalid Segment":
            st.markdown(f"""
            <div class="result-card error">
                ✗ &nbsp;<b>Invalid Segment</b><br>
                <span style="color:#4a6fa5">Segment number {seg_num} does not exist in the table.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            base, limit = segment_table[seg_num]
            st.markdown(f"""
            <div class="result-card success">
                ✓ &nbsp;<b>Physical Address: {result}</b>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-card blue">
                    <div class="metric-label">Base Address</div>
                    <div class="metric-value" style="font-size:1.6rem">{base}</div>
                </div>
                <div class="metric-card orange">
                    <div class="metric-label">+ Offset</div>
                    <div class="metric-value" style="font-size:1.6rem">{seg_offset}</div>
                </div>
                <div class="metric-card green">
                    <div class="metric-label">= Physical Addr</div>
                    <div class="metric-value" style="font-size:1.6rem">{result}</div>
                </div>
                <div class="metric-card purple">
                    <div class="metric-label">Limit</div>
                    <div class="metric-value" style="font-size:1.6rem">{limit}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 3 — FRAGMENTATION
# ══════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">First-Fit Memory Allocation</div>', unsafe_allow_html=True)

    if st.button("▶ &nbsp;Run Fragmentation Simulation", use_container_width=False):
        allocation, total_frag = fragmentation(memory_blocks.copy(), process_sizes)

        allocated_count = sum(1 for _, b, _ in allocation if b is not None)
        failed_count    = len(allocation) - allocated_count
        efficiency      = round(sum(p for p, b, _ in allocation if b is not None) /
                                sum(memory_blocks) * 100, 1) if sum(memory_blocks) else 0

        st.markdown('<div class="section-header">Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card green">
                <div class="metric-label">Allocated</div>
                <div class="metric-value">{allocated_count}</div>
                <div class="metric-sub">processes placed</div>
            </div>
            <div class="metric-card blue">
                <div class="metric-label">Failed</div>
                <div class="metric-value">{failed_count}</div>
                <div class="metric-sub">not allocated</div>
            </div>
            <div class="metric-card orange">
                <div class="metric-label">Total Fragmentation</div>
                <div class="metric-value" style="font-size:1.5rem">{total_frag}</div>
                <div class="metric-sub">wasted bytes</div>
            </div>
            <div class="metric-card purple">
                <div class="metric-label">Memory Used</div>
                <div class="metric-value">{efficiency}%</div>
                <div class="metric-sub">utilization</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Allocation Details</div>', unsafe_allow_html=True)

        for process, block, frag in allocation:
            if block is None:
                st.markdown(f"""
                <div class="result-card error">
                    ✗ &nbsp;Process <b>{process}</b> — <span style="color:#fc8181">Not Allocated</span>
                    &nbsp;<span style="color:#4a6fa5;font-size:0.75rem">(no block large enough)</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-card success">
                    ✓ &nbsp;Process <b>{process}</b> → Block <b>{block}</b>
                    &nbsp;·&nbsp; Internal Fragmentation: <b style="color:{'#f6ad55' if frag > 0 else '#68d391'}">{frag} bytes</b>
                </div>
                """, unsafe_allow_html=True)

        # Visual bar chart of blocks vs processes
        st.markdown('<div class="section-header">Memory Block Utilization</div>', unsafe_allow_html=True)

        block_labels = [f"Block {i}\n({b})" for i, b in enumerate(memory_blocks)]
        used = []
        for b in memory_blocks:
            matched = next((p for p, blk, _ in allocation if blk == b), None)
            used.append(matched if matched else 0)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name="Process Size",
            x=block_labels, y=used,
            marker=dict(color="#68d391", cornerradius=6),
            text=[f"{u}" if u else "" for u in used],
            textposition="inside"
        ))
        fig2.add_trace(go.Bar(
            name="Fragmentation / Free",
            x=block_labels,
            y=[b - u for b, u in zip(memory_blocks, used)],
            marker=dict(color="#1e3558", cornerradius=6),
        ))
        fig2.update_layout(
            barmode='stack',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Space Mono', color='#4a6fa5', size=10),
            xaxis=dict(showgrid=False, tickfont=dict(color='#7fa8c9')),
            yaxis=dict(showgrid=True, gridcolor='#0d1b2e', tickfont=dict(color='#4a6fa5'), title='Bytes'),
            legend=dict(font=dict(color='#7fa8c9', size=10), bgcolor='rgba(0,0,0,0)'),
            margin=dict(t=20, b=20, l=40, r=20),
            height=280,
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})