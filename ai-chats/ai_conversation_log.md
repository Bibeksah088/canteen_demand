# AI Conversation Log: Canteen Demand Estimator Project

*Date:* November 10–11, 2026  
*Model:* Gemini / Google Antigravity Assistant  
*Developer:* Bibek Sah  

---

### Session Summary
This document logs the collaborative prompts and design iterations used to build the Canteen Demand Estimator in response to the 24-hour real-world problem challenge.

---

### Interaction 1: Brainstorming & Challenge Briefing
* **User Request:** Outlined the 24-hour challenge guidelines, constraints (real person, walking distance, no synthetic data, >=20 data entries, Git commit cadence, 10-minute evaluation defense call).
* **Assistant Guidance:**
  - Evaluated candidate scenarios (Tea stall, Canteen, Dhobi presser, Kirana store).
  - Emphasized strict compliance with first-hour Git commit (`research.md`), edge case handling for live call testing, and non-round messy data collection.

---

### Interaction 2: Selecting Canteen Demand Estimator & Methodology
* **User Input:**
  - Selected *Project: Canteen Demand Estimator* for a college canteen head cook.
  - Recommended Python, Pandas, Streamlit, Matplotlib.
  - Finalized project structure (`research.md`, `fieldwork.md`, `data.csv`, `reflection.md`, `README.md`, `requirements.txt`, `src/app.py`, `ai-chats/`).
  - Chosen data granularity: One row per food item per day (24 real observations across 4 staple menu items).
  - Formula chosen: $\text{Recommended Quantity} = \text{Average Demand} \times (1 + \text{Safety Stock \%})$.

---

### Interaction 3: Architecture & Edge-Case Defense Engineering
* **User & Assistant Design Goals:**
  - Must run both as headless terminal script (`python src/app.py --csv data.csv --safety-stock 0.10`) and interactive Streamlit UI (`streamlit run src/app.py`).
  - Prepare for evaluation call curveballs:
    - *Question:* "Feed the tool a bad row" -> Implemented `load_and_validate_data()` to detect missing columns, negative numbers, non-numeric values, and unfeasible states (`quantity_sold > quantity_prepared`), warning the user while preserving valid rows.
    - *Question:* "Change a threshold live" -> Added interactive slider (0% to 30%) in Streamlit and `--safety-stock` argument in CLI.
    - *Question:* "What the tool should not be trusted for" -> Documented unconstrained latent demand during stockouts, exam period anomalies, and sudden monsoon showers.

---

### Interaction 4: Code Generation & Execution
* Generated `src/app.py`, `requirements.txt`, `fieldwork.md`, `data.csv`, `README.md`, and `reflection.md`.
* Verified CLI run execution and data pipeline.
