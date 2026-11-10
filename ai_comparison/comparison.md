# AI-Generated Dashboard vs Our Custom Solution

## AI Tool Used
**Claude 3.5 Sonnet** (Anthropic) – November 2025

## Exact Prompt
See `prompt_used.txt` in this folder.

## What the AI Produced
A functional Streamlit + Plotly dashboard (`ai_generated_dashboard.py`) with a completely different visual identity:

- Dark theme (slate + purple/cyan accents)
- Different typography (Space Grotesk + IBM Plex Sans)
- Vertical accent bars on cards and insight boxes
- KPI cards, department charts, critical risk table, absence patterns, and recommendations

Typical AI limitations remain:
- Most numbers are hardcoded from the prompt
- Date filter is present but does not drive the data
- Critical employee list uses invented names
- Recommendations are sensible but lack quantified expected benefits
- No SQL layer or full data lineage
- Design is modern but still generic compared to a purpose-built executive interface

## Critical Comparison

**Executable & reproducible**  
AI version: Working app  
Our version: Fully working app + requirements  
→ Winner: Ours (slight edge)

**Data fidelity**  
AI version: Hardcoded values from the prompt  
Our version: Live calculation from real CSVs / Postgres  
→ Winner: Ours

**Interactivity**  
AI version: Department filter works; date filter is decorative  
Our version: Real multiselect + date range that recomputes all KPIs  
→ Winner: Ours

**Visual identity**  
AI version: Dark theme, different fonts, accent bars  
Our version: Light professional system designed for executives  
→ Different by design

**Decision linkage**  
AI version: Clear insights + actions  
Our version: Stronger Evidence → Action → Expected benefit structure  
→ Winner: Ours

**Speed of creation**  
AI version: Minutes  
Our version: Several hours  
→ Winner: AI

**Maintainability**  
AI version: Hardcoded numbers  
Our version: Data-driven and modular  
→ Winner: Ours

**Auditability**  
AI version: No link to underlying queries  
Our version: Every KPI backed by SQL  
→ Winner: Ours

**Executive readiness**  
AI version: Good modern prototype  
Our version: Ready for IT Head & General Executive  
→ Winner: Ours

## Key Take-away for the Jury
AI can rapidly produce a modern-looking dashboard with a coherent visual language and solid analytical structure.  
It remains limited on data connectivity, full interactivity, quantified recommendations, and long-term maintainability.

Our solution keeps the analytical clarity while adding production-grade data fidelity, real interactivity, and an executive-ready design system.

## Recommendation
Use generative AI for fast visual and narrative prototyping.  
Always follow with proper data engineering, validation, and design refinement before presenting to decision-makers.
