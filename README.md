# Canteen Demand Estimator 🍲

A simple, explainable daily batch planning tool built for a college canteen head cook to eliminate afternoon food waste and prevent early lunch stockouts.

* **Target Person:** Manoj Kumar (Head Cook & Canteen In-charge)
* **Location:** Main Campus Student Canteen (Ground Floor, North Block)
* **Date:** November 11, 2026
* **Evaluation Defense Video:** [Link to 3-minute screen recording](#) *(to be inserted before final hand-in)*

---

## 1. The Real-World Problem
Every day at 9:00 AM, Manoj Kumar decides how many portions of Chai, Samosas, Veg Thalis, and Fried Rice to prepare. Without data, he overcompensates out of anxiety of running out during the 1:00 PM rush, leading to 15%–25% spoilage of cooked staples by 4:00 PM. On other days, stockouts happen before 1:15 PM, forfeiting direct student revenue.

This tool takes Manoj's raw daily counts (`quantity_prepared`, `quantity_sold`, `leftover`) and calculates tomorrow's recommended batch size with an adjustable safety stock buffer:

$$\text{Recommended Quantity} = \text{round}\Big(\overline{\text{Daily Demand}} \times (1 + \text{Safety Stock \%})\Big)$$

---

## 2. Project Structure

```
canteen-demand-estimator/
├── research.md          # Step 1: Problem statement, 2 existing solutions, 2 read sources
├── fieldwork.md         # Step 2: 20-min visit, photos, 3 quotes, 1 surprise
├── data.csv             # Step 2: 24 authentic daily service observations
├── reflection.md        # Step 4: Half-page honest reflection (written without AI)
├── README.md            # Step 3: Setup instructions, outputs, limitations
├── requirements.txt     # Python dependencies (pandas, streamlit, matplotlib)
├── src/
│   └── app.py           # Core tool: CLI analysis + interactive Streamlit UI
└── ai-chats/            # Exported transcripts of AI collaboration
    └── ai_conversation_log.md
```

---

## 3. How to Run the Tool

### Prerequisites
* Python 3.10+ installed
* Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Option A: Command Line Interface (CLI Mode)
Run directly from terminal without opening a browser:
```bash
python src/app.py --csv data.csv --safety-stock 0.10
```

To test with a different safety stock threshold (e.g., 15% buffer during busy exam week):
```bash
python src/app.py --csv data.csv --safety-stock 0.15
```

### Option B: Interactive Streamlit UI
Launch the interactive web dashboard with sliders and comparison charts:
```bash
streamlit run src/app.py
```

---

## 4. Real Output from Collected Data (`data.csv`)

Running `python src/app.py --csv data.csv --safety-stock 0.10` produces:

```text
==================================================
  CANTEEN DEMAND ESTIMATOR - CLI REPORT
==================================================
Loading data from: data.csv
Safety stock buffer: 10.0%

--- RECOMMENDATIONS FOR TOMORROW'S PREPARATION ---
Item         | Obs  | Avg Prep | Avg Sold | Avg Left | Leftover % | Stockouts | Rec Prep
----------------------------------------------------------------------------------------
Chai         | 6    | 112.5    | 99.7     | 12.8     | 11.4       | 0         | 110     
Samosa       | 6    | 66.7     | 61.8     | 4.8      | 7.2        | 1         | 68      
Veg Thali    | 6    | 47.5     | 43.8     | 3.7      | 7.7        | 2         | 48      
Fried Rice   | 6    | 34.2     | 28.3     | 5.8      | 17.1       | 0         | 31

[i] Recommendation Formula: round(Avg Sold * (1 + Safety Stock %))
==================================================
```

### Key Real-World Insights:
1. **Fried Rice is Over-Prepared:** With a **17.1% leftover rate**, Manoj was routinely preparing 34 portions when average demand was only 28.3. The tool recommends reducing prep to **31 portions**, cutting waste by over 50%.
2. **Samosa & Thali Face Stockouts:** Veg Thali had **2 stockout days** where 100% of prepared food sold out early. The 10% safety buffer recommends bumping preparation from 45 to **48 portions** on high-demand days.

---

## 5. What the Tool Gets Wrong & Known Limitations
*(Prepared for the 10-minute live evaluator defense)*

1. **Weather & Rainy Days:** The tool currently assumes demand is steady across days. When heavy unseasonal rain hits campus, physical footfall drops by ~40%, meaning the recommended batch will still result in excess leftover.
2. **Exam & Vacation Outliers:** During semester exam weeks or college festivals, demand patterns invert (morning snacks spike, sit-down thali lunches crash). A standard moving average does not account for academic calendar anomalies.
3. **Cannot Be Trusted for Uncapped True Demand:** On days where stockouts occurred (`leftover = 0`), `quantity_sold` only reflects what was physically available, **not** total latent demand (how many students walked away empty-handed).
4. **Perishability Constraints:** Samosas are fried in discrete batches (e.g. trays of 12 or 15), while Chai is brewed in liters. The tool recommends integer portion counts, which kitchen staff must map to their physical cooking vessels.
