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
# Palette: one blue family for charts and accents.
# Red / amber are reserved ONLY for risk status (critical / warning).
# -----------------------------------------------------------------------------
INK = "#0E2747"        # deep navy (text, headings)
MUTED = "#52657F"      # secondary text
PAPER = "#F5F9FE"      # page background
SAND = "#E9F1FB"       # sidebar / soft panels
CARD = "#FFFFFF"       # card surface
RULE = "#D5E2F2"       # hairlines
GRID = "#E3ECF7"       # chart grid
BLUE = "#1F5FA8"       # primary accent
BLUE_DEEP = "#12407A"  # strong accent
AZURE = "#3B82D6"      # mid blue
SKY = "#9CC3F0"        # soft blue
AMBER = "#E3A53A"      # status: warning only
TERRA = "#D0533A"      # status: critical only

BLUE_SCALE = [SKY, AZURE, BLUE_DEEP]
BLUE_SEQ = [BLUE, AZURE, INK, SKY, "#2A9DB8", "#5B7DB1", "#A9C6E8"]

# One font family for the entire app (CSS, cards, and Plotly charts)
FONT = "'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif"

st.markdown(
    f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap');

  html {{ color-scheme: light; }}

  /* ---------- One font everywhere (icons are left alone) ---------- */
  html, body, .stApp, .stApp p, .stApp li, .stApp span, .stApp div, .stApp label,
  .stApp button, .stApp input, .stApp textarea, .stApp select,
  .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
  .stApp td, .stApp th, .stApp small, .stApp dt, .stApp dd,
  [data-testid="stMarkdownContainer"] *, [data-testid="stCaptionContainer"] *,
  [data-baseweb="select"] *, [data-baseweb="popover"] *, [data-baseweb="input"] * {{
      font-family: {FONT};
  }}
  [data-testid="stIconMaterial"], .material-icons, .material-symbols-rounded {{
      font-family: 'Material Symbols Rounded', 'Material Icons' !important;
  }}

  .stApp {{ background: {PAPER}; color: {INK}; }}
  #MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
  .block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1280px; }}

  /* ---------- Sidebar ---------- */
  section[data-testid="stSidebar"] {{
      background: {SAND};
      border-right: 1px solid {RULE};
  }}
  section[data-testid="stSidebar"] .block-container {{ padding-top: 2rem; }}
  .brand {{
      font-size: 1.4rem; font-weight: 700; line-height: 1.2; color: {INK};
  }}
  .brand small {{
      display: block; font-size: 0.72rem; font-weight: 600;
      letter-spacing: 0.12em; text-transform: uppercase;
      color: {BLUE}; margin-bottom: 0.35rem;
  }}

  /* Sidebar widgets: light blue look regardless of Streamlit theme */
  [data-baseweb="tag"], [data-testid="stMultiSelectTag"] {{
      background-color: {BLUE} !important; color: #fff !important; border-radius: 6px !important;
  }}
  [data-baseweb="tag"] * {{ color: #fff !important; fill: #fff !important; }}
  div[data-baseweb="select"] > div,
  div[data-baseweb="input"],
  div[data-baseweb="base-input"] {{
      background-color: {CARD} !important; color: {INK} !important;
      border: 1px solid {RULE} !important; border-radius: 10px !important;
  }}
  div[data-baseweb="input"] input, div[data-baseweb="base-input"] input {{
      color: {INK} !important; -webkit-text-fill-color: {INK} !important; background: transparent !important;
  }}
  div[data-baseweb="select"] svg, div[data-baseweb="input"] svg {{ color: {MUTED} !important; fill: {MUTED} !important; }}
  [data-baseweb="tag"] svg {{ color: #fff !important; fill: #fff !important; }}
  [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{
      color: {INK} !important; font-weight: 600 !important; opacity: 1 !important;
  }}

  /* ---------- Header ---------- */
  .eyebrow {{
      font-size: 0.75rem; font-weight: 600; letter-spacing: 0.14em;
      text-transform: uppercase; color: {BLUE}; margin-bottom: 0.5rem;
  }}
  .main-header {{
      font-size: 2.8rem; font-weight: 800; line-height: 1.1;
      color: {INK}; margin: 0 0 0.6rem 0; letter-spacing: -0.02em;
  }}
  .sub-header {{
      font-size: 1.05rem; line-height: 1.65; color: {MUTED};
      max-width: 720px; margin-bottom: 1.8rem;
  }}

  /* ---------- KPI strip ---------- */
  .kpi {{
      position: relative; overflow: hidden;
      background: {CARD};
      border: 1px solid {RULE};
      border-radius: 18px;
      padding: 1.1rem 1.2rem 1.15rem 1.2rem;
      min-height: 168px;
      box-shadow: 0 1px 2px rgba(14, 39, 71, 0.04), 0 6px 18px rgba(31, 95, 168, 0.06);
      transition: transform .18s ease, box-shadow .18s ease;
  }}
  .kpi:hover {{
      transform: translateY(-3px);
      box-shadow: 0 2px 4px rgba(14, 39, 71, 0.05), 0 12px 26px rgba(31, 95, 168, 0.12);
  }}
  .kpi-icon {{
      width: 2.5rem; height: 2.5rem; border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      background: {SAND}; color: {BLUE}; margin-bottom: 0.9rem;
  }}
  .kpi-icon svg {{
      width: 1.3rem; height: 1.3rem; fill: none; stroke: currentColor;
      stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round;
  }}
  .kpi-label {{
      font-size: 0.82rem; font-weight: 600; color: {MUTED};
  }}
  .kpi-value {{
      font-size: 2.25rem; font-weight: 800; line-height: 1.1; color: {INK};
      margin: 0.15rem 0 0.2rem 0; letter-spacing: -0.03em;
  }}
  .kpi-hint {{ font-size: 0.8rem; color: {MUTED}; }}

  /* critical card: warm tint so it stands apart from the blue ones */
  .kpi.alert {{
      background: linear-gradient(160deg, #FFF6F3 0%, #FDE9E3 100%);
      border-color: #F2CABF;
  }}
  .kpi.alert .kpi-icon {{ background: #FAD9D0; color: {TERRA}; }}
  .kpi.alert .kpi-value {{ color: {TERRA}; }}

  /* ---------- Section titles (neutral navy, numbered pill) ---------- */
  .section-title {{
      display: flex; align-items: center; gap: 0.8rem;
      font-size: 2rem; font-weight: 800; line-height: 1.15;
      letter-spacing: -0.02em; color: {INK};
      margin: 2.6rem 0 0.6rem 0;
      padding-top: 1.4rem; border-top: 1px solid {RULE};
  }}
  .section-num {{
      display: inline-flex; align-items: center; justify-content: center;
      min-width: 2.4rem; height: 2.4rem; padding: 0 0.6rem;
      border-radius: 999px; background: {INK}; color: #fff;
      font-size: 0.95rem; font-weight: 600; letter-spacing: 0;
  }}
  .stApp h2, .stApp h3 {{ color: {INK} !important; font-weight: 700 !important; letter-spacing: -0.01em; }}
  .section-intro {{ color: {MUTED}; font-size: 0.97rem; line-height: 1.6; margin: -0.2rem 0 1.2rem 0; max-width: 760px; }}
  .chart-title {{
      font-size: 0.78rem; font-weight: 600; letter-spacing: 0.08em;
      text-transform: uppercase; color: {MUTED}; margin: 0.6rem 0 0.2rem 0;
  }}

  /* ---------- Key finding ---------- */
  .finding {{
      background: {CARD};
      border: 1px solid {RULE};
      border-radius: 12px;
      padding: 1.2rem 1.4rem;
      margin: 1.4rem 0 0.4rem 0;
  }}
  .finding .tag {{
      font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em;
      text-transform: uppercase; color: {BLUE};
  }}
  .finding h4 {{
      font-size: 1.2rem; font-weight: 600; line-height: 1.3;
      margin: 0.3rem 0 0.4rem 0; color: {INK};
  }}
  .finding p {{ margin: 0; font-size: 0.97rem; line-height: 1.65; color: {MUTED}; }}

  /* ---------- Recommendation cards ---------- */
  /* Recommendations: one clean table-style panel instead of four boxes */
  .rec-table, .rec-table * {{ font-family: 'DM Sans', {FONT} !important; }}
  .rec-table {{
      background: {CARD};
      border: 1px solid {RULE};
      border-radius: 16px;
      overflow: hidden;
  }}
  .rec-grid {{
      display: grid;
      grid-template-columns: 3.2rem 1.15fr 1.2fr 1.3fr 1.1fr;
      column-gap: 1.6rem;
      align-items: start;
      padding: 1.25rem 1.6rem;
  }}
  .rec-header {{
      background: {SAND};
      padding-top: 0.75rem; padding-bottom: 0.75rem;
      font-size: 0.78rem; font-weight: 600; letter-spacing: 0.06em;
      text-transform: uppercase; color: {MUTED};
      align-items: center;
  }}
  .rec-item {{ border-top: 1px solid {RULE}; }}
  .rec-table .rec-no {{
      font-family: {FONT} !important;
      font-size: 1.5rem; font-weight: 800; line-height: 1;
      color: {INK}; letter-spacing: -0.02em;
      font-variant-numeric: tabular-nums;
  }}
  .rec-title {{
      font-size: 1.02rem; font-weight: 700; line-height: 1.3; color: {INK};
  }}
  .rec-cell {{ font-size: 0.9rem; line-height: 1.55; color: #33465F; }}
  .rec-cell.benefit {{ color: {BLUE_DEEP}; font-weight: 600; }}
  .rec-cell::before {{
      content: attr(data-label); display: none;
      font-size: 0.74rem; font-weight: 600; letter-spacing: 0.06em;
      text-transform: uppercase; color: {MUTED}; margin-bottom: 0.2rem;
  }}
  @media (max-width: 900px) {{
      .rec-header {{ display: none; }}
      .rec-grid {{ grid-template-columns: 2.6rem 1fr; row-gap: 0.7rem; }}
      .rec-no {{ grid-row: span 4; }}
      .rec-cell::before {{ display: block; }}
  }}

  /* ---------- Misc ---------- */
  div[data-testid="stDataFrame"] {{ border: 1px solid {RULE}; border-radius: 10px; overflow: hidden; }}
  [data-testid="stCaptionContainer"] {{ color: {MUTED}; }}
  hr {{ border-color: {RULE}; }}
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
        font=dict(family=FONT, color=INK, size=13),
        margin=dict(t=16, b=10, l=10, r=10),
        showlegend=legend,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            title=None, font=dict(size=12, family=FONT),
        ),
        hoverlabel=dict(bgcolor=INK, font=dict(color="#fff", family=FONT)),
        coloraxis_showscale=False,
    )
    fig.update_xaxes(showgrid=False, linecolor=RULE, tickfont=dict(color=MUTED, family=FONT), title=None)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED, family=FONT))
    return fig


KPI_ICONS = {
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>'
             '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>'
                '<path d="M10 14l4 4M14 14l-4 4"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "alert": '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
             '<path d="M12 9v4M12 17h.01"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>'
            '<path d="M10 13l4 4M14 13l-4 4"/>',
}


def kpi(label, value, hint="", alert=False, icon="users"):
    cls = "kpi alert" if alert else "kpi"
    svg = f'<svg viewBox="0 0 24 24" aria-hidden="true">{KPI_ICONS[icon]}</svg>'
    return (
        f'<div class="{cls}"><div class="kpi-icon">{svg}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-hint">{hint}</div></div>'
    )


def section_title(num, text):
    st.markdown(
        f'<div class="section-title"><span class="section-num">{num}</span>{text}</div>',
        unsafe_allow_html=True,
    )


def finding(title, body):
    st.markdown(
        f'<div class="finding"><div class="tag">Key finding</div><h4>{title}</h4><p>{body}</p></div>',
        unsafe_allow_html=True,
    )


def chart_title(text):
    st.markdown(f'<div class="chart-title">{text}</div>', unsafe_allow_html=True)


def rec_table(recs):
    # Built without indentation or blank lines: Markdown would treat them as a code block.
    html = (
        '<div class="rec-table">'
        '<div class="rec-grid rec-header"><div></div><div>Decision</div>'
        "<div>Evidence</div><div>Action</div><div>Expected benefit</div></div>"
    )
    for num, title, ev, act, ben in recs:
        html += (
            '<div class="rec-grid rec-item">'
            f'<div class="rec-no">{num}</div>'
            f'<div class="rec-title">{title}</div>'
            f'<div class="rec-cell" data-label="Evidence">{ev}</div>'
            f'<div class="rec-cell" data-label="Action">{act}</div>'
            f'<div class="rec-cell benefit" data-label="Expected benefit">{ben}</div>'
            "</div>"
        )
    return html + "</div>"


RISK_COLORS = {"CRITICAL": TERRA, "WARNING": AMBER, "NORMAL": BLUE}

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

cols = st.columns(5, gap="medium")
cards = [
    kpi("Employees in scope", f"{total_emps:,}", "in selected departments", icon="users"),
    kpi("Unplanned absence", f"{unplanned_rate:.1f}%", "share of all absence days", icon="calendar"),
    kpi("Weekly overtime", f"{avg_ot:.2f} h", "average per employee", icon="clock"),
    kpi("Critical burnout risk", f"{critical_count}", "need action now", alert=True, icon="alert"),
    kpi("Unjustified days", f"{unjustified_days:,}", "no valid reason on file", icon="file"),
]
for c, html in zip(cols, cards):
    c.markdown(html, unsafe_allow_html=True)

st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sections (all on ONE scrolling page)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = (st.container() for _ in range(5))

# ========== SECTION 1 ==========
with tab1:
    section_title("01", "Overview")
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
            color_continuous_scale=BLUE_SCALE,
            text="unplanned_rate",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", marker_line_width=0, cliponaxis=False)
        fig.update_yaxes(title=None, ticksuffix="%")
        fig.update_layout(bargap=0.35)
        st.plotly_chart(style_fig(fig, 380), width="stretch")

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
            width="stretch",
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

# ========== SECTION 2 ==========
with tab2:
    section_title("02", "Overtime &amp; workload")
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
            color_discrete_map={"Critical": TERRA, "Elevated": AMBER, "Normal": BLUE},
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
        st.plotly_chart(style_fig(fig, 390, legend=True), width="stretch")

    with c2:
        chart_title("Total overtime hours by month")
        monthly_ot = wl_f.groupby(["month", "dept_name"])["overtime"].sum().reset_index()
        fig2 = px.line(
            monthly_ot,
            x="month",
            y="overtime",
            color="dept_name",
            markers=True,
            color_discrete_sequence=BLUE_SEQ,
        )
        fig2.update_traces(line=dict(width=2.5), marker=dict(size=6))
        fig2.update_yaxes(title=None)
        fig2.update_xaxes(tickangle=-45)
        st.plotly_chart(style_fig(fig2, 390, legend=True), width="stretch")

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

# ========== SECTION 3 ==========
with tab3:
    section_title("03", "Burnout risk")
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
        st.plotly_chart(style_fig(fig, 370, legend=True), width="stretch")

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
            width="stretch",
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

# ========== SECTION 4 ==========
with tab4:
    section_title("04", "Absence patterns")
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
                     color_continuous_scale=BLUE_SCALE, text="events")
        fig.update_traces(textposition="outside", marker_line_width=0, cliponaxis=False)
        fig.update_xaxes(categoryorder="array", categoryarray=list(names.values()))
        fig.update_yaxes(title=None)
        fig.update_layout(bargap=0.3)
        st.plotly_chart(style_fig(fig, 350), width="stretch")
        st.caption("Mondays and Fridays stand out — typical of discretionary or recovery-related absence.")

    with c2:
        chart_title("Top unplanned absence reasons (days)")
        reasons = unp.groupby("reason")["days"].sum().sort_values(ascending=False).head(8).reset_index()
        fig = px.bar(reasons, x="days", y="reason", orientation="h", color="days",
                     color_continuous_scale=BLUE_SCALE, text="days")
        fig.update_traces(texttemplate="%{text:.0f}", textposition="outside", marker_line_width=0, cliponaxis=False)
        fig.update_yaxes(categoryorder="total ascending", title=None)
        fig.update_xaxes(title=None)
        fig.update_layout(bargap=0.3)
        st.plotly_chart(style_fig(fig, 350), width="stretch")

    chart_title("Unplanned absence days over time")
    trend = unp.groupby("month")["days"].sum().reset_index()
    fig = go.Figure(
        go.Scatter(
            x=trend["month"], y=trend["days"], mode="lines+markers",
            line=dict(color=BLUE, width=3, shape="spline"),
            marker=dict(size=7, color=BLUE),
            fill="tozeroy", fillcolor="rgba(31,95,168,0.12)",
        )
    )
    fig.update_yaxes(title=None)
    st.plotly_chart(style_fig(fig, 260), width="stretch")

    # ---- Unplanned absence reasons for EACH department ----
    st.subheader("Absence reasons in each department")
    st.markdown(
        '<div class="section-intro">What drives unplanned absence in every department: '
        "share of each department's unplanned absence days, by reason.</div>",
        unsafe_allow_html=True,
    )
    rd = unp.groupby(["dept_name", "reason"])["days"].sum().reset_index()
    rd["pct"] = (rd["days"] / rd.groupby("dept_name")["days"].transform("sum") * 100).round(1)

    r1, r2 = st.columns([1, 1], gap="medium")
    with r1:
        chart_title("Share of unplanned absence days by reason, per department")
        figr = px.bar(
            rd, x="dept_name", y="pct", color="reason", barmode="group", text="pct",
            color_discrete_sequence=BLUE_SEQ,
        )
        figr.update_traces(texttemplate="%{text:.1f}%", textposition="outside", marker_line_width=0, cliponaxis=False)
        figr.update_yaxes(title=None, ticksuffix="%")
        figr.update_layout(bargap=0.25)
        st.plotly_chart(style_fig(figr, 400, legend=True), width="stretch")
    with r2:
        chart_title("Unplanned absence days (count)")
        piv = rd.pivot(index="reason", columns="dept_name", values="days").fillna(0).astype(int)
        piv["Total"] = piv.sum(axis=1)
        st.dataframe(piv.sort_values("Total", ascending=False).reset_index().rename(columns={"reason": "Reason"}),
                     width="stretch", hide_index=True)
        top_r = rd.loc[rd.groupby("dept_name")["pct"].idxmax()]
        for _, r in top_r.iterrows():
            st.caption(f"**{r['dept_name']}**: main reason is {r['reason']} ({r['pct']:.1f}%)")

# ========== SECTION 5 ==========
with tab5:
    section_title("05", "Recommendations")
    st.subheader("Decisions to take, and what to expect")
    st.markdown(
        '<div class="section-intro">Four actions, ordered by urgency. Each is tied to evidence '
        "from this dashboard.</div>",
        unsafe_allow_html=True,
    )

    # Evidence strings are built from the live data
    hot_depts = " &amp; ".join(dept_summary["dept_name"].head(2).tolist())
    ot_top = ot_summary.iloc[0]

    # Live correlation between average overtime and unplanned absence days per employee
    ot_emp = wl_f.groupby("employee_id")["overtime"].mean().rename("ot")
    unp_emp = unp.groupby("employee_id")["days"].sum().rename("unp")
    corr_df = pd.concat([ot_emp, unp_emp], axis=1).fillna({"unp": 0}).dropna()
    corr_val = corr_df["ot"].corr(corr_df["unp"]) if len(corr_df) > 2 else np.nan
    corr_text = (
        f"Overtime and unplanned absence move together (r ≈ {corr_val:.2f} across employees)."
        if pd.notna(corr_val)
        else "Overtime and unplanned absence tend to move together."
    )

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
            corr_text,
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

    st.markdown(rec_table(recs), unsafe_allow_html=True)