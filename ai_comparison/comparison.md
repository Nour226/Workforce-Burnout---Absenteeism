# AI-Generated Dashboard vs Our Custom Solution

## AI Tool Used
**Claude 3.5 Sonnet** (Anthropic) – November 2025

## Exact Prompt
See `prompt_used.txt` in this folder.

## What the AI Produced
Claude returned a well-structured **specification** (not executable code) containing:

- 5 recommended sections with suggested chart types (KPI cards, stacked bars, heatmaps, line trends)
- Color semantics (green/amber/red)
- Explicit “Finding → Recommendation” mapping
- Filter recommendations (department, period)

The AI correctly identified the three priority decisions and proposed a clean executive narrative.

## Critical Comparison

| Dimension                  | AI Specification                          | Our Streamlit Dashboard                          | Winner / Comment |
|---------------------------|-------------------------------------------|--------------------------------------------------|------------------|
| **Executable & reproducible** | Specification only                       | Fully working app (`dashboard/app.py`) + requirements | **Ours** – ready to demo |
| **Data fidelity**         | Used the numbers we supplied             | Live calculation from the actual CSVs / Postgres | **Ours** – no hard-coded values |
| **Interactivity**         | Described filters                        | Real multiselect + date range that recompute everything | **Ours** |
| **Visual polish**         | Good conceptual design                   | Professional CSS + Plotly interactive charts     | Tie / Ours slightly ahead in practice |
| **Decision linkage**      | Strong “Finding → Action” language       | Same, plus a dedicated Recommendations tab       | Tie |
| **Speed of creation**     | ~2 minutes                               | Several hours of design + coding + validation    | **AI** |
| **Maintainability**       | Needs a developer to implement           | Source code is the documentation                 | **Ours** |
| **Auditability**          | Black-box narrative                      | Every KPI has a matching SQL file in `/sql`      | **Ours** |

## Key Take-away for the Jury
AI tools are excellent **accelerators for the analytical story and visual hierarchy**.  
They do **not** replace the need for:

1. Validated SQL against the real schema  
2. An executable, filterable dashboard that decision-makers can actually use  
3. Full reproducibility package (data + scripts + README)

Our solution therefore combines the best of both worlds: AI-inspired narrative structure + production-ready engineering.

## Recommendation
Use generative AI for the first draft of the executive story and slide outline, then implement and harden the actual dashboard and SQL layer ourselves. This hybrid approach is the most efficient for future projects.
