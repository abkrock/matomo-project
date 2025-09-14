import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import configparser
from datetime import datetime
import os

# --- Load config ---
config = configparser.ConfigParser()
config.read("report_config.properties")

report_title = config.get("DEFAULT", "report_title", fallback="Matomo Report")
report_fields = config.get("DEFAULT", "report_fields", fallback="label,nb_hits").split(",")
alias_raw = config.get("DEFAULT", "field_aliases", fallback="")
alias_map = {k.strip(): v.strip() for k, v in (pair.split(":") for pair in alias_raw.split(",") if ":" in pair)}

# --- Load mocked data ---
df = pd.read_csv("mock_matomo_data.csv", parse_dates=["date"])

# --- Filter for thisMonth and lastMonth ---
today = pd.Timestamp.today()
this_start = today.replace(day=1)
last_start = (this_start - pd.Timedelta(days=1)).replace(day=1)
last_end = this_start - pd.Timedelta(days=1)

df_this = df[(df["date"] >= this_start) & (df["date"] <= today)].copy()
df_last = df[(df["date"] >= last_start) & (df["date"] <= last_end)].copy()

# --- Aggregate to get top 10 distinct pages ---
page_totals = df_this.groupby("label")["nb_hits"].sum().sort_values(ascending=False)
top_pages = page_totals.head(10).index.tolist()

df_this_top = df_this[df_this["label"].isin(top_pages)]
df_last_top = df_last[df_last["label"].isin(top_pages)]

# --- Chart 1: Pie (Pageviews) ---
pie_data = df_this_top.groupby("label")["nb_hits"].sum()
fig1, ax1 = plt.subplots()
ax1.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%")
ax1.set_title("Pageviews Distribution")
fig1.savefig("chart_pie.png")

# --- Chart 2: Bar (Time Spent) ---
bar_data = df_this_top.groupby("label")["sum_time_spent"].sum()
fig2, ax2 = plt.subplots()
ax2.bar(bar_data.index, bar_data.values)
ax2.set_title("Total Time Spent by Visitors")
ax2.set_ylabel("Seconds")
ax2.tick_params(axis='x', rotation=45)
fig2.tight_layout()
fig2.savefig("chart_bar.png")

# --- Chart 3: Avg Time Spent (Bar Chart + % Change) ---
avg_this = df_this_top.groupby("label")["sum_time_spent"].mean()
avg_last = df_last_top.groupby("label")["sum_time_spent"].mean()
pct_change_avg = ((avg_this - avg_last) / avg_last * 100).round(1)

fig3, ax3 = plt.subplots()
colors = ["green" if pct_change_avg.get(label, 0) > 0 else "red" for label in avg_this.index]
bars = ax3.bar(avg_this.index, avg_this.values, color=colors)

# Annotate % change above each bar
for bar, label in zip(bars, avg_this.index):
    change = pct_change_avg.get(label, 0)
    sign = "+" if change > 0 else ""
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
             f"{sign}{change}%", ha='center', fontsize=9,
             color="darkgreen" if change > 0 else "crimson")

ax3.set_title("Avg Time Spent (Monthly) with % Change")
ax3.set_ylabel("Seconds")
ax3.tick_params(axis='x', rotation=45)
fig3.tight_layout()
fig3.savefig("chart_avg_time.png")

# --- Chart 4: Max Visitor Count (Bar Chart + % Change) ---
max_this = df_this_top.groupby("label")["nb_hits"].max()
max_last = df_last_top.groupby("label")["nb_hits"].max()
pct_change_max = ((max_this - max_last) / max_last * 100).round(1)

fig4, ax4 = plt.subplots()
colors = ["green" if pct_change_max.get(label, 0) > 0 else "red" for label in max_this.index]
bars = ax4.bar(max_this.index, max_this.values, color=colors)

# Annotate % change above each bar
for bar, label in zip(bars, max_this.index):
    change = pct_change_max.get(label, 0)
    sign = "+" if change > 0 else ""
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
             f"{sign}{change}%", ha='center', fontsize=9,
             color="darkgreen" if change > 0 else "crimson")

ax4.set_title("Max Visitor Count (Monthly) with % Change")
ax4.set_ylabel("Pageviews")
ax4.tick_params(axis='x', rotation=45)
fig4.tight_layout()
fig4.savefig("chart_max_visitors.png")

# Annotate % change above each point
for i, label in enumerate(max_this.index):
    change = pct_change_max.get(label, 0)
    sign = "+" if change > 0 else ""
    color = "green" if change > 0 else "red"
    ax4.text(i, max_this[label] + 5, f"{sign}{change}%", fontsize=9, ha='center', color=color)

ax4.set_title("Max Visitor Count (Monthly) with % Change")
ax4.set_ylabel("Pageviews")
ax4.tick_params(axis='x', rotation=45)
fig4.tight_layout()
fig4.savefig("chart_max_visitors.png")

# --- Build HTML Table with Aliases ---
#table_df = df_this_top[report_fields].copy()
#table_df.rename(columns=alias_map, inplace=True)
#html_table = table_df.to_html(index=False, border=0)

# --- Aggregate monthly summary for top pages ---
summary_df = df_this_top.groupby("label").agg({
    "nb_hits": "sum",
    "sum_time_spent": "sum",
    "avg_page_load_time": "mean"
}).reset_index()

# --- Select only requested fields ---
summary_df = summary_df[report_fields]

# --- Apply aliases ---
summary_df.rename(columns=alias_map, inplace=True)

# --- Convert to HTML table ---
html_table = summary_df.to_html(index=False, border=0)

# --- Create HTML Report ---
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{report_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h2 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 40px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        img {{ max-width: 100%; margin-bottom: 40px; }}
        .flex-row {{ display: flex; gap: 40px; }}
        .flex-col {{ flex: 1; text-align: center; }}
    </style>
</head>
<body>
    <h2>{report_title}</h2>
    <p>Generated on {timestamp}</p>
    {html_table}
    <h3>Pageviews vs Time Spent</h3>
    <div class="flex-row">
        <div class="flex-col">
            <img src="chart_pie.png" alt="Pie Chart">
            <p><strong>Pageviews Distribution</strong></p>
        </div>
        <div class="flex-col">
            <img src="chart_bar.png" alt="Bar Chart">
            <p><strong>Total Time Spent</strong></p>
        </div>
    </div>
    <h3>Monthly Comparison Charts</h3>
    <div class="flex-row">
    <div class="flex-col">
        <img src="chart_avg_time.png" alt="Avg Time Chart">
        <p><strong>Avg Time Spent Comparison</strong></p>
    </div>
    <div class="flex-col">
        <img src="chart_max_visitors.png" alt="Max Visitors Chart">
        <p><strong>Max Visitor Count Comparison</strong></p>
    </div>
</div>
</body>
</html>
"""

with open("matomo_dynamic_report.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Report generated: matomo_dynamic_report.html")

# --- Optional: Matomo API call (commented out) ---
"""
def fetch_matomo_data(period, date):
    import requests
    from io import StringIO
    import chardet

    params = {
        "module": "API",
        "method": "Actions.getPageUrls",
        "idSite": "1",
        "period": period,
        "date": date,
        "format": "CSV",
        "token_auth": "your_matomo_token"
    }
    response = requests.post("https://your-matomo-domain/matomo/index.php", data=params)
    encoding = chardet.detect(response.content)['encoding'] or 'utf-8'
    return pd.read_csv(StringIO(response.content.decode(encoding)))
"""
