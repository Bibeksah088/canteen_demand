# Project Reflection: Canteen Demand Estimator

*Author: Bibek Sah*  
*Project: Canteen Demand Estimator*  
*Evaluation Date: November 11, 2026*  

---

### What I Got Wrong at the Start
When I first picked this problem, I viewed it through a classic data science lens: I assumed the canteen had predictable inventory cycles, that portions were measured consistently, and that overproduction was purely a math problem. 

Talking to Manoj Kumar in person quickly shattered that assumption. In reality, food isn't tracked in neat grams or plates—it's cooked in *degchis* and estimated by the visual density of the morning crowd at the tea counter. More importantly, I completely misunderstood his motivation. I thought he was trying to save money on raw ingredients; in truth, his primary fear was the emotional stress and conflict of facing hungry, angry college seniors when the counter runs dry at 1:15 PM. Overcooking was an intentional psychological shield against confrontation. Once I understood that, I realized any model proposing an aggressive cut to prep sizes would be immediately ignored.

### What I Would Cut If I Had Another Day
If I were to rebuild this, I would cut out the complex multi-chart visualizations and secondary metrics from the dashboard. Manoj is not going to look at standard deviation graphs or distribution curves on a screen in the middle of frying samosas with grease on his hands. 

Instead of an analytical dashboard, a simple one-click WhatsApp message or a printable single-sheet daily slip showing just: *"Cook 48 Thalis, Fry 65 Samosas today"* with a checkbox would provide 10x more utility. Simplicity and kitchen-speed matter far more than visual polish.

### Where AI Helped and Where It Wasted Time
* **Where AI Helped:**  
  AI was fantastic for rapid scaffolding. It helped formulate the statistical formula, created the CLI argument parser, generated robust edge-case validation (such as detecting when `quantity_sold > quantity_prepared` or handling corrupted input lines), and formatted clean Markdown tables and docstrings in minutes.

* **Where AI Wasted Time:**  
  AI repeatedly attempted to over-engineer the forecasting model. Early on, it suggested adding multi-variable ARIMA models, external weather API integrations, and ingredient-level Bill of Materials (BOM) tracking. In an unorganized college canteen without automated weighing scales, none of that data exists. I had to repeatedly push back to strip the complexity down to a basic, transparent moving average with a manual safety stock buffer that Manoj could understand and verify in 5 seconds.
