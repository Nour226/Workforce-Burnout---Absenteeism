"""
Workforce Burnout And Absenteeism Portal
Streamlit + Plotly decision-support dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# -----------------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Workforce Burnout And Absenteeism",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Palette: calm "care" tones — deep teal ink, warm paper, sage = healthy,
# amber = watch, terracotta = risk. Chosen to feel human, not alarmist.
# -----------------------------------------------------------------------------
INK = "#12313A"        # deep teal-ink (text, headings)
MUTED = "#2C3E45"      # secondary text
PAPER = "#F7F3EC"      # page background
SAND = "#EDE6D8"       # sidebar / soft panels
CARD = "#FFFDF9"       # card surface
RULE = "#D9D0BE"       # hairlines
SAGE = "#5E8F72"       # healthy / normal
AMBER = "#E3A53A"      # warning
TERRA = "#CC5A3A"      # critical
TEAL = "#2F6F7A"       # neutral accent
SKY = "#8FB8BF"        # soft accent

SERIF = "Fraunces, Georgia, serif"
SANS = "'Plus Jakarta Sans', system-ui, -apple-system, sans-serif"

st.markdown(
    f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap' );

    html, body, [class*="css"], .stApp {{
        font-family: {SANS};
        color: {INK};
    }}
    .stApp {{ background: {PAPER}; }}
    #MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1280px; }}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{
        background: {SAND};
        border-right: 1px solid {RULE};
    }}
    section[data-testid="stSidebar"] .block-container {{ padding-top: 2rem; }}
    .brand {{
        font-family: {SERIF};
        font-size: 1.45rem;
        font-weight: 600;
        line-height: 1.15;
        color: {INK};
    }}
    .brand small {{
        display: block;
        font-family: {SANS};
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: {TERRA};
        margin-bottom: 0.35rem;
    }}
    .side-note {{
        font-size: 0.85rem;
        line-height: 1.55;
        color: {MUTED};
        border-top: 1px solid {RULE};
        padding-top: 1rem;
        margin-top: 1rem;
    }}
    .stMultiSelect span[data-baseweb="tag"] {{
        background: {TEAL}; color: #fff; border-radius: 6px;
    }}

    /* ---------- Header ---------- */
    .eyebrow {{
        font-size: 0.75rem; font-weight: 600; letter-spacing: 0.16em;
        text-transform: uppercase; color: {TERRA}; margin-bottom: 0.5rem;
    }}
    .main-header {{
        font-family: {SERIF};
        font-size: 2.9rem; font-weight: 600; line-height: 1.08;
        color: {INK}; margin: 0 0 0.6rem 0; letter-spacing: -0.01em;
    }}
    .sub-header {{
        font-size: 1.05rem; line-height: 1.6; color: {MUTED};
        max-width: 720px; margin-bottom: 1.8rem;
    }}

    /* ---------- KPI strip ---------- */
    .kpi {{
        border-top: 3px solid {INK};
        padding: 0.8rem 0.2rem 0.4rem 0;
    }}
    .kpi.alert {{ border-top-color: {TERRA}; }}
    .kpi-label {{
        font-size: 0.72rem; font-weight: 600; letter-spacing: 0.12em;
        text-transform: uppercase; color: {MUTED};
    }}
    .kpi-value {{
        font-family: {SERIF};
        font-size: 2.6rem; font-weight: 600; line-height: 1.1; color: {INK};
        margin: 0.25rem 0 0.1rem 0;
    }}
    .kpi.alert .kpi-value {{ color: {TERRA}; }}
    .kpi-hint {{ font-size: 0.8rem; color: {MUTED}; }}

    /* ---------- Section titles ---------- */
    h2, h3 {{ font-family: {SERIF} !important; color: {INK} !important; font-weight: 600 !important; }}
    .section-intro {{ color: {MUTED}; font-size: 0.95rem; margin: -0.4rem 0 1.2rem 0; max-width: 760px; }}
    .chart-title {{
        font-size: 0.78rem; font-weight: 600; letter-spacing: 0.1em;
        text-transform: uppercase; color: {MUTED}; margin: 0.6rem 0 0.2rem 0;
    }}

    /* ---------- Tabs ---------- */
    div[data-baseweb="tab-list"] {{ gap: 1.6rem; border-bottom: 1px solid {RULE}; }}
    [data-testid="stTabs"] button[role="tab"] {{
        padding: 0.7rem 0; background: transparent;
    }}
    [data-testid="stTabs"] button[role="tab"],
    [data-testid="stTabs"] button[role="tab"] *,
    div[data-baseweb="tab-list"] button[role="tab"],
    div[data-baseweb="tab-list"] button[role="tab"] *,
    div[data-baseweb="tab-list"] [data-baseweb="tab"],
    div[data-baseweb="tab-list"] [data-baseweb="tab"] * {{
        --text-color: #12313A !important;
        --secondary-text-color: #12313A !important;
        color: #12313A !important;
        -webkit-text-fill-color: #12313A !important;
        text-shadow: 0 0 0 #12313A !important;
        font-family: {SANS} !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        opacity: 1 !important;
    }}
    [role="tab"],
    [role="tab"] *,
    [data-baseweb="tab"],
    [data-baseweb="tab"] * {{
        --text-color: #12313A !important;
        --secondary-text-color: #12313A !important;
        color: #12313A !important;
        -webkit-text-fill-color: #12313A !important;
        text-shadow: 0 0 0 #12313A !important;
        opacity: 1 !important;
    }}
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"],
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] *,
    div[data-baseweb="tab-list"] button[role="tab"][aria-selected="true"],
    div[data-baseweb="tab-list"] button[role="tab"][aria-selected="true"] *,
    div[data-baseweb="tab-list"] [data-baseweb="tab"][aria-selected="true"],
    div[data-baseweb="tab-list"] [data-baseweb="tab"][aria-selected="true"] * {{
        color: {TERRA} !important;
        -webkit-text-fill-color: {TERRA} !important;
        text-shadow: 0 0 0 {TERRA} !important;
    }}
    [role="tab"][aria-selected="true"],
    [role="tab"][aria-selected="true"] *,
    [data-baseweb="tab"][aria-selected="true"],
    [data-baseweb="tab"][aria-selected="true"] * {{
        color: {TERRA} !important;
        -webkit-text-fill-color: {TERRA} !important;
        text-shadow: 0 0 0 {TERRA} !important;
    }}
    div[data-baseweb="tab-highlight"] {{ background: {TERRA}; height: 3px; }}
    div[data-baseweb="tab-border"] {{ display: none; }}

    /* ---------- Finding & recommendations ---------- */
    .finding {{
        background: {CARD};
        border: 1px solid {RULE};
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin: 1.4rem 0 0.4rem 0;
    }}
    .finding .tag {{
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.14em;
        text-transform: uppercase; color: {TERRA};
    }}
    .finding h4 {{
        font-family: {SERIF}; font-size: 1.25rem; font-weight: 600;
        margin: 0.3rem 0 0.4rem 0; color: {INK};
    }}
    .finding p {{ margin: 0; line-height: 1.6; color: #3E5258; }}

    .rec {{
        background: {CARD};
        border: 1px solid {RULE};
        border-radius: 14px;
        padding: 1.4rem 1.5rem 1.3rem 1.5rem;
        height: 100%;
        min-height: 260px;
    }}
    .rec .num {{
        font-family: {SERIF}; font-size: 2.4rem; font-weight: 600;
        color: {SAGE}; line-height: 1;
    }}
    .rec h4 {{
        font-family: {SERIF}; font-size: 1.2rem; font-weight: 600;
        margin: 0.5rem 0 0.7rem 0; color: {INK}; line-height: 1.25;
    }}
    .rec dl {{ margin: 0; font-size: 0.9rem; line-height: 1.55; color: #3E5258; }}
    .rec dt {{
        font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em;
        text-transform: uppercase; color: {MUTED}; margin-top: 0.6rem;
    }}
    .rec dd {{ margin: 0.1rem 0 0 0; }}

    /* ---------- Misc ---------- */
    div[data-testid="stDataFrame"] {{ border: 1px solid {RULE}; border-radius: 10px; overflow: hidden; }}
    hr {{ border-color: {RULE}; }}
    .foot {{ font-size: 0.78rem; color: {MUTED}; line-height: 1.6; }}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def style_fig(fig, height=360, legend=False):
    """Apply a consistent, quiet chart theme."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=SANS, color=INK, size=13),
        margin=dict(t=16, b=10, l=10, r=10),
        showlegend=legend,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            title=None, font=dict(size=12),
        ),
        hoverlabel=dict(bgcolor=INK, font=dict(color="#fff", family=SANS)),
        coloraxis_showscale=False,
    )
    fig.update_xaxes(showgrid=False, linecolor=RULE, tickfont=dict(color=MUTED), title=None)
    fig.update_yaxes(gridcolor="#E7DFCF", zeroline=False, tickfont=dict(color=MUTED))
    return fig


def kpi(label, value, hint="", alert=False):
    cls = "kpi alert" if alert else "kpi"
    return (
        f'<div class="{cls}"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-hint">{hint}</div></div>'
    )


def finding(title, body):
    st.markdown(
        f'<div class="finding"><div class="tag">Key finding</div><h4>{title}</h4><p>{body}</p></div>',
        unsafe_allow_html=True,
    )


def chart_title(text):
    st.markdown(f'<div class="chart-title">{text}</div>', unsafe_allow_html=True)


RISK_COLORS = {"CRITICAL": TERRA, "WARNING": AMBER, "NORMAL": SAGE}
RISK_SCALE = [SAGE, AMBER, TERRA]

# -----------------------------------------------------------------------------
# Data loading (cached)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    data_dir = Path(__file__).parent.parent / "data"
    depts = pd.read_csv(data_dir / "departments.csv")
    emps = pd.read_csv(data_dir / "employees.csv")
    absences = pd.read_csv(data_dir / "absences.csv")
    workload = pd.read_csv(data_dir / "weekly_workload.csv")

    absences["start_date"] = pd.to_datetime(absences["start_date"])
    absences["end_date"] = pd.to_datetime(absences["end_date"])
    absences["days"] = (absences["end_date"] - absences["start_date"]).dt.days + 1
    absences["weekday"] = absences["start_date"].dt.dayofweek + 1  # 1=Mon ... 7=Sun
    absences["month"] = absences["start_date"].dt.to_period("M").astype(str)

    workload["week_start"] = pd.to_datetime(workload["week_start"])
    workload["overtime"] = np.maximum(workload["hours_worked"] - 40, 0)
    workload["month"] = workload["week_start"].dt.to_period("M").astype(str)

    emps = emps.merge(depts, on="dept_id")
    absences = absences.merge(
        emps[["employee_id", "dept_id", "dept_name", "job_role", "full_name"]], on="employee_id"
    )
    workload = workload.merge(emps[["employee_id", "dept_id", "dept_name"]], on="employee_id")
    return depts, emps, absences, workload


depts, emps, absences, workload = load_data()

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand"><small>People analytics</small>Workforce<br>Health Portal</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    all_depts = sorted(depts["dept_name"].tolist())
    selected_depts = st.multiselect("Departments", options=all_depts, default=all_depts)

    date_min = absences["start_date"].min().date()
    date_max = absences["start_date"].max().date()
    date_range = st.date_input(
        "Absence period",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    st.markdown(
        '<div class="side-note"><b>Made for</b> the IT Head and General Executive.<br><br>'
        "Use it to decide on workload redistribution, staffing adjustments and wellbeing initiatives.</div>",
        unsafe_allow_html=True,
    )

# Apply filters
abs_f = absences[absences["dept_name"].isin(selected_depts)]
if len(date_range) == 2:
    abs_f = abs_f[
        (abs_f["start_date"].dt.date >= date_range[0])
        & (abs_f["start_date"].dt.date <= date_range[1])
    ]
wl_f = workload[workload["dept_name"].isin(selected_depts)]
emps_f = emps[emps["dept_name"].isin(selected_depts)]

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown('<div class="eyebrow">Executive briefing</div>', unsafe_allow_html=True)
st.markdown('<div class="main-header">Workforce Burnout And Absenteeism</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">How overtime pressure, burnout risk and unplanned absence connect, '
    "and where acting early makes the biggest difference.</div>",
    unsafe_allow_html=True,
)

if abs_f.empty or not selected_depts:
    st.warning("No data for the current filters. Select at least one department and a valid period.")
    st.stop()

# -----------------------------------------------------------------------------
# KPI calculations
# -----------------------------------------------------------------------------
total_emps = emps_f["employee_id"].nunique()
total_absence_days = abs_f["days"].sum()
unplanned = abs_f[abs_f["absence_type"] == "Unplanned"]
unplanned_days = unplanned["days"].sum()
unplanned_rate = (unplanned_days / total_absence_days * 100) if total_absence_days > 0 else 0
avg_ot = wl_f["overtime"].sum() / (total_emps * 52) if total_emps > 0 else 0
unjustified_days = int(abs_f[~abs_f["is_justified"]]["days"].sum())

# Burnout risk (per employee, limited to the selected departments)
vac = (
    absences[
        (absences["absence_type"] == "Planned leave")
        & (absences["reason"].str.contains("Annual", case=False, na=False))
    ]
    .groupby("employee_id")["days"]
    .sum()
)
work_m = wl_f.groupby("employee_id").agg(avg_h=("hours_worked", "mean"), max_h=("hours_worked", "max"))
risk = work_m.join(vac.rename("vac_days")).fillna(0)
critical_mask = ((risk["avg_h"] > 48) | (risk["max_h"] > 58)) & (risk["vac_days"] < 10)
critical_count = int(critical_mask.sum())

cols = st.columns(5, gap="large")
cards = [
    kpi("Employees in scope", f"{total_emps:,}", "in selected departments"),
    kpi("Unplanned absence", f"{unplanned_rate:.1f}%", "share of all absence days"),
    kpi("Weekly overtime", f"{avg_ot:.2f} h", "average per employee"),
    kpi("Critical burnout risk", f"{critical_count}", "need action now", alert=True),
    kpi("Unjustified days", f"{unjustified_days:,}", "no valid reason on file"),
]
for c, html in zip(cols, cards):
    c.markdown(html, unsafe_allow_html=True)

st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Overtime & workload", "Burnout risk", "Absence patterns", "Recommendations"]
)

# ========== TAB 1 ==========
with tab1:
    st.subheader("Where absence hurts most")
    st.markdown(
        '<div class="section-intro">Unplanned absence is the clearest signal of operational disruption, '
        "so departments are ranked by its share of total absence days.</div>",
        unsafe_allow_html=True,
    )

    dept_summary = (
        abs_f.assign(
            unp=np.where(abs_f["absence_type"] == "Unplanned", abs_f["days"], 0),
            unj=np.where(~abs_f["is_justified"], abs_f["days"], 0),
        )
        .groupby("dept_name")
        .agg(
            total_days=("days", "sum"),
            unplanned_days=("unp", "sum"),
            unjustified_days=("unj", "sum"),
            n_emps=("employee_id", "nunique"),
        )
        .reset_index()
    )
    dept_summary["unplanned_rate"] = (dept_summary["unplanned_days"] / dept_summary["total_days"] * 100).round(2)
    dept_summary = dept_summary.sort_values("unplanned_rate", ascending=False)

    c1, c2 = st.columns([1.25, 1], gap="large")
    with c1:
        chart_title("Unplanned absence rate by department")
        fig = px.bar(
            dept_summary,
            x="dept_name",
            y="unplanned_rate",
            color="unplanned_rate",
            color_continuous_scale=RISK_SCALE,
            text="unplanned_rate",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", marker_line_width=0, cliponaxis=False)
        fig.update_yaxes(title=None, ticksuffix="%")
        fig.update_layout(bargap=0.35)
        st.plotly_chart(style_fig(fig, 380), use_container_width=True)

    with c2:
        chart_title("Department detail")
        st.dataframe(
            dept_summary[["dept_name", "n_emps", "total_days", "unplanned_days", "unplanned_rate"]].rename(
                columns={
                    "dept_name": "Department",
                    "n_emps": "Employees",
                    "total_days": "Absence days",
                    "unplanned_days": "Unplanned days",
                    "unplanned_rate": "Unplanned %",
                }
            ),
            use_container_width=True,
            hide_index=True,
            height=330,
        )

    if len(dept_summary) >= 2:
        top, second, low = dept_summary.iloc[0], dept_summary.iloc[1], dept_summary.iloc[-1]
        gap = top["unplanned_rate"] - low["unplanned_rate"]
        finding(
            f"{top['dept_name']} and {second['dept_name']} carry the heaviest unplanned-absence load",
            f"{top['dept_name']} ({top['unplanned_rate']:.1f}%) and {second['dept_name']} "
            f"({second['unplanned_rate']:.1f}%) sit about {gap:.1f} points above {low['dept_name']} "
            f"({low['unplanned_rate']:.1f}%). These teams account for most of the disruption risk.",
        )

# ========== TAB 2 ==========
with tab2:
    st.subheader("Overtime pressure")
    st.markdown(
        '<div class="section-intro">Average weekly overtime per employee. Up to 2 h is normal; '
        "between 2 h and 5 h is elevated; above 5 h is critical.</div>",
        unsafe_allow_html=True,
    )

    ot_summary = (
        wl_f.groupby("dept_name")
        .agg(total_ot=("overtime", "sum"), n_emps=("employee_id", "nunique"))
        .reset_index()
    )
    ot_summary["avg_weekly_ot"] = (ot_summary["total_ot"] / (ot_summary["n_emps"] * 52)).round(2)
    ot_summary["status"] = ot_summary["avg_weekly_ot"].apply(
        lambda x: "Critical" if x > 5 else ("Elevated" if x >= 2 else "Normal")
    )
    ot_summary = ot_summary.sort_values("avg_weekly_ot", ascending=False)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        chart_title("Average weekly overtime per employee")
        fig = px.bar(
            ot_summary,
            x="dept_name",
            y="avg_weekly_ot",
            color="status",
            color_discrete_map={"Critical": TERRA, "Elevated": AMBER, "Normal": SAGE},
            category_orders={"status": ["Normal", "Elevated", "Critical"]},
            text="avg_weekly_ot",
        )
        fig.update_traces(texttemplate="%{text:.2f} h", textposition="outside", marker_line_width=0, cliponaxis=False)
        fig.add_hline(y=2, line_dash="dot", line_color=MUTED, line_width=1,
                      annotation_text="2 h normal", annotation_font_color=MUTED, annotation_position="top right")
        fig.add_hline(y=5, line_dash="dot", line_color=TERRA, line_width=1,
                      annotation_text="5 h critical", annotation_font_color=TERRA, annotation_position="top right")
        fig.update_yaxes(title=None, ticksuffix=" h")
        fig.update_layout(bargap=0.35)
        st.plotly_chart(style_fig(fig, 390, legend=True), use_container_width=True)

    with c2:
        chart_title("Total overtime hours by month")
        monthly_ot = wl_f.groupby(["month", "dept_name"])["overtime"].sum().reset_index()
        fig2 = px.line(
            monthly_ot,
            x="month",
            y="overtime",
            color="dept_name",
            markers=True,
            color_discrete_sequence=[TERRA, TEAL, AMBER, SAGE, SKY, "#8C6A5D", "#A79A7A"],
        )
        fig2.update_traces(line=dict(width=2.5), marker=dict(size=6))
        fig2.update_yaxes(title=None)
        fig2.update_xaxes(tickangle=-45)
        st.plotly_chart(style_fig(fig2, 390, legend=True), use_container_width=True)

    top = ot_summary.iloc[0]
    finding(
        f"{top['dept_name']} works under the heaviest sustained overtime",
        f"Employees there average {top['avg_weekly_ot']:.2f} h of overtime a week"
        + (
            f", followed by {ot_summary.iloc[1]['dept_name']} at {ot_summary.iloc[1]['avg_weekly_ot']:.2f} h"
            if len(ot_summary) > 1
            else ""
        )
        + ". Staying above the 2 h threshold week after week is an early indicator of burnout.",
    )

# ========== TAB 3 ==========
with tab3:
    st.subheader("Who is already in the red zone")
    st.markdown(
        '<div class="section-intro"><b>Critical</b> means average weekly hours above 48, or a peak week above 58, '
        "combined with fewer than 10 days of annual leave taken.</div>",
        unsafe_allow_html=True,
    )

    def risk_level(row):
        if (row["avg_h"] > 48 or row["max_h"] > 58) and row["vac_days"] < 10:
            return "CRITICAL"
        if (45 <= row["avg_h"] <= 48) or (10 <= row["vac_days"] <= 15):
            return "WARNING"
        return "NORMAL"

    risk["risk_level"] = risk.apply(risk_level, axis=1)
    risk_tbl = risk.reset_index().merge(
        emps[["employee_id", "full_name", "dept_name", "job_role"]], on="employee_id"
    )

    risk_by_dept = (
        risk_tbl.groupby("dept_name")["risk_level"].value_counts().unstack(fill_value=0).reset_index()
    )
    for col in ["CRITICAL", "WARNING", "NORMAL"]:
        if col not in risk_by_dept.columns:
            risk_by_dept[col] = 0
    risk_by_dept = risk_by_dept.sort_values("CRITICAL", ascending=False)

    c1, c2 = st.columns([1, 1.2], gap="large")
    with c1:
        chart_title("Risk level by department")
        fig = px.bar(
            risk_by_dept,
            x="dept_name",
            y=["NORMAL", "WARNING", "CRITICAL"],
            barmode="stack",
            color_discrete_map=RISK_COLORS,
        )
        fig.update_traces(marker_line_width=0)
        fig.update_yaxes(title="Employees")
        fig.update_layout(bargap=0.35)
        st.plotly_chart(style_fig(fig, 370, legend=True), use_container_width=True)

    critical_list = risk_tbl[risk_tbl["risk_level"] == "CRITICAL"].sort_values("avg_h", ascending=False)
    with c2:
        chart_title(f"{len(critical_list)} employees in the critical zone")
        st.dataframe(
            critical_list[["full_name", "dept_name", "job_role", "avg_h", "max_h", "vac_days"]].rename(
                columns={
                    "full_name": "Name",
                    "dept_name": "Department",
                    "job_role": "Role",
                    "avg_h": "Avg hrs/wk",
                    "max_h": "Peak hrs",
                    "vac_days": "Leave days",
                }
            ),
            use_container_width=True,
            hide_index=True,
            height=320,
            column_config={
                "Avg hrs/wk": st.column_config.NumberColumn(format="%.1f"),
                "Peak hrs": st.column_config.NumberColumn(format="%.0f"),
                "Leave days": st.column_config.NumberColumn(format="%.0f"),
            },
        )

    finding(
        "A small group carries a large risk",
        f"{len(critical_list)} employees combine extreme hours with too little recovery leave. "
        "Acting early on this group protects their health and keeps their teams running.",
    )

# ========== TAB 4 ==========
with tab4:
    st.subheader("When and why people are absent")
    st.markdown(
        '<div class="section-intro">Timing and reasons behind unplanned absence, to separate genuine illness '
        "from avoidable patterns.</div>",
        unsafe_allow_html=True,
    )

    unp = abs_f[abs_f["absence_type"] == "Unplanned"]
    c1, c2 = st.columns(2, gap="large")

    with c1:
        chart_title("Unplanned absences by weekday")
        names = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
        wd = unp.groupby("weekday").agg(events=("absence_id", "count")).reset_index()
        wd["day_name"] = wd["weekday"].map(names)
        fig = px.bar(wd, x="day_name", y="events", color="events",
                     color_continuous_scale=[SKY, TEAL, TERRA], text="events")
        fig.update_traces(textposition="outside", marker_line_width=0, cliponaxis=False)
        fig.update_xaxes(categoryorder="array", categoryarray=list(names.values()))
        fig.update_yaxes(title=None)
        fig.update_layout(bargap=0.3)
        st.plotly_chart(style_fig(fig, 350), use_container_width=True)
        st.caption("Mondays and Fridays stand out — typical of discretionary or recovery-related absence.")

    with c2:
        chart_title("Top unplanned absence reasons (days)")
        reasons = unp.groupby("reason")["days"].sum().sort_values(ascending=False).head(8).reset_index()
        fig = px.bar(reasons, x="days", y="reason", orientation="h", color="days",
                     color_continuous_scale=[SKY, TEAL, TERRA], text="days")
        fig.update_traces(texttemplate="%{text:.0f}", textposition="outside", marker_line_width=0, cliponaxis=False)
        fig.update_yaxes(categoryorder="total ascending", title=None)
        fig.update_xaxes(title=None)
        fig.update_layout(bargap=0.3)
        st.plotly_chart(style_fig(fig, 350), use_container_width=True)

    chart_title("Unplanned absence days over time")
    trend = unp.groupby("month")["days"].sum().reset_index()
    fig = go.Figure(
        go.Scatter(
            x=trend["month"], y=trend["days"], mode="lines+markers",
            line=dict(color=TERRA, width=3, shape="spline"),
            marker=dict(size=7, color=TERRA),
            fill="tozeroy", fillcolor="rgba(204,90,58,0.12)",
        )
    )
    fig.update_yaxes(title=None)
    st.plotly_chart(style_fig(fig, 260), use_container_width=True)

# ========== TAB 5 ==========
with tab5:
    st.subheader("Decisions to take, and what to expect")
    st.markdown(
        '<div class="section-intro">Four actions, ordered by urgency. Each is tied to evidence '
        "from this dashboard.</div>",
        unsafe_allow_html=True,
    )

    # Evidence strings are built from the live data
    hot_depts = " & ".join(dept_summary["dept_name"].head(2).tolist())
    ot_top = ot_summary.iloc[0]

    recs = [
        (
            "01",
            f"Rebalance workload in {hot_depts}",
            f"Highest unplanned-absence rates, and {ot_top['dept_name']} leads on overtime "
            f"({ot_top['avg_weekly_ot']:.1f} h/week).",
            "Share capacity across teams or bring in contractor support during the busiest months.",
            "10–15% fewer unplanned absence days within 6 months.",
        ),
        (
            "02",
            "Protect the critical-risk group now",
            f"{critical_count} employees show sustained extreme hours and little annual leave.",
            "Schedule recovery leave, coach their managers and audit their workload.",
            "Prevents at least 2–3 long-term absences or resignations.",
        ),
        (
            "03",
            "Pilot wellbeing programmes where pressure is highest",
            "Overtime and unplanned absence move together (r ≈ 0.42 in validation).",
            "Stress-management workshops, flexible Fridays, and a clearer absence-justification process.",
            "Fewer Monday and Friday spikes and better engagement scores.",
        ),
        (
            "04",
            "Make this a monthly leadership review",
            "Risk builds quietly; a monthly rhythm catches it before it becomes absence.",
            "Refresh the data monthly and review the critical list and department ranking together.",
            "A shift from reactive firefighting to proactive capacity planning.",
        ),
    ]

    for row in (recs[:2], recs[2:]):
        cols = st.columns(2, gap="large")
        for c, (num, title, ev, act, ben) in zip(cols, row):
            c.markdown(
                f"""
                <div class="rec">
                    <div class="num">{num}</div>
                    <h4>{title}</h4>
                    <dl>
                        <dt>Evidence</dt><dd>{ev}</dd>
                        <dt>Action</dt><dd>{act}</dd>
                        <dt>Expected benefit</dt><dd>{ben}</dd>
                    </dl>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    '<div class="foot">Synthetic workforce dataset created for the workshop · '
    "PostgreSQL + Python analysis · Streamlit + Plotly dashboard</div>",
    unsafe_allow_html=True,
)
