# Echoes of Joseon: Temporal-Structural Visual Analytics of Historical Figures in the Annals of the Joseon Dynasty

[![Live Demo](https://img.shields.io/badge/Live_Demo-GitHub_Pages-d4af37?style=for-the-badge)](https://lim0386.github.io/echoes-of-joseon/)
[![Data Source](https://img.shields.io/badge/Source-NIKH_Official_XML-3b82f6?style=for-the-badge)](https://sillok.history.go.kr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

Interactive visual analytics system and reproducible empirical dataset accompanying the manuscript:  
**"Echoes of Joseon: Exploring Temporal-Structural Dynamics of Historical Figures in the Annals of the Joseon Dynasty"**

---

## 🔗 Interactive Web Demonstration
- **Live Web Application:** https://lim0386.github.io/echoes-of-joseon/
- **Local Execution:** Simply open `index.html` in any modern web browser (Chrome, Edge, Firefox, Safari) — no backend server or external dependencies required.

### Key Visual Analytics Features
1. **Phase 1 — 27-Reign Temporal Switchboard (1392–1910):** Compare raw mention totals ($F_a$) against reign-duration-normalized mention density ($F_a / T_k$) across all 27 monarchs from King Taejo to King Sunjong, and filter cohort activity by clicking any reign bar.
2. **Phase 2 — Radial Cohort Topology ($N = 60$):** Explore the 60-figure stratified purposive analytical cohort arranged radially, with dynamic sorting by Total Mentions ($F_a$), Peak Density ($I_p^*$), Activity Ratio ($\alpha$), or Historical Field.
3. **Phase 3 — Longitudinal Barcode & 6-Axis Metric Rose:** Inspect any individual figure's 27-reign longitudinal mention barcode, 6-dimensional normalized profile vector $V_c = (F_p^*, I_p^*, I_a^*, F_a^*, A_a^*, \alpha)$, and MECE archetype classification, with one-click vector export (`Export SVG` for 300+ DPI publication figures).

---

## 📂 Repository Structure

```text
echoes-of-joseon/
├── index.html                           # Standalone interactive visualization system (HTML/CSS/JS)
├── README.md                            # Project documentation & methodology summary
├── data/
│   ├── echoes_data.json                 # Complete structured JSON dataset powering the web app (N=60)
│   ├── rev_cohort60_metrics.csv         # Full 6D normalized metrics & MECE classifications (N=60)
│   ├── rev_reign_normalized.csv         # Reign-by-reign raw & Tk-normalized mention densities (27 reigns)
│   ├── rev_top60.csv                    # Top 60 Korean historical entities extracted from the XML corpus
│   ├── rev_4cases.csv                   # Longitudinal breakdown for the 4 archetype case studies
│   └── audit_100_samples_verified.csv   # 100-sample manual precision/recall verification audit log
└── scripts/
    ├── extract_sillok.py                # XML parser linking <index type="이름" ref="M_..."> tags to NIKH metadata
    ├── step1_summary.py                 # Cohort filtering & authority metadata cross-referencing
    ├── step2_archetypes.py              # 6D metric normalization, MECE classification & sensitivity analysis
    └── audit_sample.py                  # Random stratified sampler for precision/recall validation