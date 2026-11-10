"""
Workforce Burnout & Absenteeism Dashboard
AI-generated version (different visual style)
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Burnout Analytics",
    page_icon="🔥",
    layout="wide"
)

# Completely different visual system
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    h1, h2, h3, .main-title {
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .stApp {
        background: #0f172a;
        color: #e2e8f0;
    }

    section[data-testid="stSidebar"] {
        background: #1e293b;
        border-right: 1px solid #334155;
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.3rem;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    /* KPI cards - different style */
    .kpi-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.3rem 1.1rem;
        position: relative;
        overflow: hidden;
    }
    .kpi-box::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: #8b5cf6;
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #94a3b8;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #f1f5f9;
        line-height: 1.1;
    }
    .kpi-value.alert {
        color: #f87171;
    }
    .kpi-hint {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.25rem;
    }

    /* Section headers */
    .section-label {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.35rem;
        font-weight: 600;
        color: #e2e8f0;
        margin: 2.2rem 0 1rem 0;
        padding-left: 12px;
        border-left: 4px solid #8b5cf6;
    }

    /* Finding / insight boxes */
    .insight {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        margin: 1.2rem 0;
        position: relative;
    }
    .insight::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: #06b6d4;
        border-radius: 10px 0 0 10px;
    }
    .insight-tag {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #06b6d4;
        margin-bottom: 0.35rem;
    }
    .insight-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 0.3rem;
    }
    .insight-body {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.55;
    }

    /* Recommendation cards */
    .rec {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        position: relative;
    }
    .rec::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: #a78bfa;
    }
    .rec-num {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        color: #a78bfa;
        font-size: 0.9rem;
        margin-bottom: 0.2rem;
    }
    .rec-title {
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.25rem;
    }
    .rec-text {
        color: #94a3b8;
        font-size: 0.9rem;
    }

    /* Override some Streamlit defaults for dark theme */
    .stDataFrame {
        background: #1e293b;
    }
    div[data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Filters")
    selected_depts = st.multiselect(
        "Departments",
        ["Sales", "R&D", "HR"],
        default=["Sales", "R&D", "HR"]
    )
    st.date_input("Period", value=(pd.to_datetime("2024-01-01"), pd.to_datetime("2024-12-31")))
    st.markdown("---")
    st.caption("AI-generated prototype • Static data")

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">Burnout & Absenteeism Monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Quick scan of overtime pressure, risk concentration and absence patterns</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# KPI row
# -----------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown("""
    <div class="kpi-box">
        <div class="kpi-label">Unplanned Absence</div>
        <div class="kpi-value">25.0%</div>
        <div class="kpi-hint">Sales (highest)</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown("""
    <div class="kpi-box">
        <div class="kpi-label">Weekly Overtime</div>
        <div class="kpi-value">3.40h</div>
        <div class="kpi-hint">Sales average</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown("""
    <div class="kpi-box">
        <div class="kpi-label">Critical Risk</div>
        <div class="kpi-value alert">9</div>
        <div class="kpi-hint">employees flagged</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown("""
    <div class="kpi-box">
        <div class="kpi-label">Highest Dept Gap</div>
        <div class="kpi-value">3.8pts</div>
        <div class="kpi-hint">Sales vs HR</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Section 1
# -----------------------------------------------------------------------------
st.markdown('<div class="section-label">Department Pressure</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    abs_df = pd.DataFrame({
        "Department": ["Sales", "R&D", "HR"],
        "Rate": [25.0, 24.7, 21.2]
    })
    abs_df = abs_df[abs_df["Department"].isin(selected_depts)]
    fig = px.bar(abs_df, x="Department", y="Rate", text="Rate",
                 color_discrete_sequence=["#8b5cf6"])
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        height=320,
        margin=dict(t=30, b=20, l=10, r=10),
        yaxis_title=None,
        xaxis_title=None,
        showlegend=False
    )
    fig.update_yaxes(gridcolor="#334155")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Unplanned absence rate (%)")

with c2:
    ot_df = pd.DataFrame({
        "Department": ["Sales", "R&D", "HR"],
        "Hours": [3.40, 3.00, 2.53]
    })
    ot_df = ot_df[ot_df["Department"].isin(selected_depts)]
    fig2 = px.bar(ot_df, x="Department", y="Hours", text="Hours",
                  color_discrete_sequence=["#06b6d4"])
    fig2.update_traces(texttemplate="%{text:.2f}h", textposition="outside")
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        height=320,
        margin=dict(t=30, b=20, l=10, r=10),
        yaxis_title=None,
        xaxis_title=None,
        showlegend=False
    )
    fig2.update_yaxes(gridcolor="#334155")
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Average weekly overtime (hours)")

st.markdown("""
<div class="insight">
    <div class="insight-tag">Insight</div>
    <div class="insight-title">Sales and R&D are under the most pressure</div>
    <div class="insight-body">
        Both departments combine high unplanned absence (~25%) with the highest overtime.
        They should be the first focus for any workload intervention.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Section 2
# -----------------------------------------------------------------------------
st.markdown('<div class="section-label">Critical Risk Group</div>', unsafe_allow_html=True)

st.write("Employees with avg hours > 48 or peak > 58 **and** annual leave under 10 days.")

risk_df = pd.DataFrame({
    "Name": ["Sarah M.", "James T.", "Elena R.", "Mohamed K.", "Lisa P.",
             "David L.", "Anna S.", "Karim B.", "Nadia F."],
    "Dept": ["Sales", "Sales", "R&D", "R&D", "Sales", "R&D", "HR", "Sales", "R&D"],
    "Avg h": [51.2, 49.8, 50.5, 48.9, 52.1, 49.3, 48.2, 50.8, 49.7],
    "Peak": [61, 59, 58, 57, 63, 60, 56, 62, 59],
    "Leave": [6, 4, 8, 7, 3, 9, 5, 2, 8]
})
if selected_depts:
    risk_df = risk_df[risk_df["Dept"].isin(selected_depts)]

st.dataframe(risk_df, use_container_width=True, hide_index=True)

st.markdown("""
<div class="insight">
    <div class="insight-tag">Insight</div>
    <div class="insight-title">Risk is concentrated in a small group</div>
    <div class="insight-body">
        Only 9 people sit in the critical zone. Acting on this short list is the highest-leverage action available right now.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Section 3
# -----------------------------------------------------------------------------
st.markdown('<div class="section-label">Absence Timing</div>', unsafe_allow_html=True)

w1, w2 = st.columns(2)

with w1:
    wd = pd.DataFrame({
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "Events": [142, 98, 87, 91, 135]
    })
    fig3 = px.bar(wd, x="Day", y="Events", color_discrete_sequence=["#a78bfa"])
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        height=300,
        margin=dict(t=20, b=20, l=10, r=10),
        yaxis_title=None,
        xaxis_title=None,
        showlegend=False
    )
    fig3.update_yaxes(gridcolor="#334155")
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("Unplanned absences peak on Monday and Friday")

with w2:
    reasons = pd.DataFrame({
        "Reason": ["Illness", "Personal", "Family", "Other"],
        "Share": [48, 22, 17, 13]
    })
    fig4 = px.pie(reasons, values="Share", names="Reason",
                  color_discrete_sequence=["#8b5cf6", "#06b6d4", "#a78bfa", "#64748b"],
                  hole=0.45)
    fig4.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        height=300,
        margin=dict(t=20, b=20, l=10, r=10)
    )
    st.plotly_chart(fig4, use_container_width=True)

# -----------------------------------------------------------------------------
# Recommendations
# -----------------------------------------------------------------------------
st.markdown('<div class="section-label">Suggested Actions</div>', unsafe_allow_html=True)

st.markdown("""
<div class="rec">
    <div class="rec-num">01</div>
    <div class="rec-title">Rebalance Sales & R&D first</div>
    <div class="rec-text">Highest combined load of absence + overtime. Temporary capacity or internal mobility can help within one quarter.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="rec">
    <div class="rec-num">02</div>
    <div class="rec-title">Protect the 9 critical employees</div>
    <div class="rec-text">Force recovery leave and run a short workload audit with their managers this month.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="rec">
    <div class="rec-num">03</div>
    <div class="rec-title">Test flexible options around weekends</div>
    <div class="rec-text">Monday/Friday spikes suggest recovery or discretionary patterns. A small pilot can test the effect.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Generated with AI • Numbers taken from the original prompt • Not connected to live data sources")
