import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- Config ---
start_date = datetime(2024, 9, 14)
end_date = datetime(2025, 9, 14)
pages = ["about", "contact", "home", "services", "blog", "faq", "pricing", "testimonials"]

# --- Generate Date Range ---
dates = pd.date_range(start=start_date, end=end_date, freq="D")

# --- Page Traffic Profiles ---
base_hits = {
    "home": 60,
    "contact": 45,
    "about": 35,
    "services": 25,
    "blog": 15,
    "faq": 10,
    "pricing": 8,
    "testimonials": 5
}

# --- Generate Mock Data ---
data = []
np.random.seed(42)  # For reproducibility

for date in dates:
    weekday = date.weekday()
    weekend_factor = 0.7 if weekday >= 5 else 1.0  # Reduce traffic on weekends

    for page in pages:
        # Simulate occasional spikes for blog and pricing
        spike = np.random.rand() < 0.05 if page in ["blog", "pricing"] else False
        multiplier = 3 if spike else 1

        hits = int(np.random.poisson(base_hits[page] * weekend_factor * multiplier))
        time_spent = np.random.normal(loc=hits * 9, scale=hits * 1.5)
        load_time = np.random.normal(loc=0.8, scale=0.2)
        bounce_rate = np.random.uniform(0.1, 0.7)
        exit_rate = np.random.uniform(0.1, 0.6)
        entrances = np.random.randint(0, hits + 1)
        bounces = int(hits * bounce_rate)

        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "label": page,
            "nb_hits": hits,
            "sum_time_spent": max(0, round(time_spent, 2)),
            "avg_page_load_time": round(max(0.1, load_time), 3),
            "bounce_rate": f"{round(bounce_rate * 100, 1)}%",
            "exit_rate": f"{round(exit_rate * 100, 1)}%",
            "entrances": entrances,
            "bounces": bounces
        })

# --- Create DataFrame ---
df = pd.DataFrame(data)

# --- Save to CSV ---
df.to_csv("mock_matomo_data.csv", index=False)

# --- Preview ---
print("✅ Mock data generated for", len(pages), "pages over", len(dates), "days.")
print(df.head(10))
df.to_csv("mock_matomo_data.csv", index=False)
