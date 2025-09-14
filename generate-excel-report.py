import requests
import pandas as pd
import matplotlib.pyplot as plt
import chardet
import zipfile
from io import StringIO
from openpyxl import load_workbook
from openpyxl.drawing.image import Image

# --- Step 1: Download CSV from Matomo ---
url = "http://192.168.29.191:8080/index.php"
params = {
    "module": "API",
    "method": "Actions.getPageUrls",
    "idSite": "1",
    "period": "day",
    "date": "today",
    "format": "CSV",
    "token_auth": "a8f851e63acc4fae2e5824d517b8cca5"
}

response = requests.post(url, data=params)
raw_bytes = response.content
encoding = chardet.detect(raw_bytes)['encoding'] or 'utf-8'
csv_content = raw_bytes.decode(encoding)

# --- Step 2: Load and Filter CSV ---
df = pd.read_csv(StringIO(csv_content))
available_columns = df.columns.tolist()
desired_columns = [
    "label",
    "nb_hits",
    "sum_time_spent",
    "avg_time_generation",
    "avg_page_load_time",
    "entry_sum_visit_length"
]
filtered_df = df[[col for col in desired_columns if col in available_columns]]

# --- Step 3: Save to Excel ---
excel_path = "matomo_filtered_report.xlsx"
filtered_df.to_excel(excel_path, index=False, sheet_name="Filtered Data")

# --- Step 4: Generate Charts ---
# Pie Chart: Pageviews
fig1, ax1 = plt.subplots()
ax1.pie(filtered_df["nb_hits"], labels=filtered_df["label"], autopct="%1.1f%%")
ax1.set_title("Pageviews Distribution")
fig1.savefig("pageviews_pie.png")

# Bar Chart: Total Time Spent
fig2, ax2 = plt.subplots()
ax2.bar(filtered_df["label"], filtered_df["sum_time_spent"])
ax2.set_title("Total Time Spent by Visitors")
ax2.set_ylabel("Seconds")
ax2.tick_params(axis='x', rotation=45)
fig2.tight_layout()
fig2.savefig("time_spent_bar.png")

# --- Step 5: Embed Charts into Excel ---
if zipfile.is_zipfile(excel_path):
    workbook = load_workbook(excel_path)
    sheet = workbook["Filtered Data"]
    sheet.add_image(Image("pageviews_pie.png"), "H2")
    sheet.add_image(Image("time_spent_bar.png"), "H30")
    workbook.save(excel_path)
else:
    print("Excel file is not valid. Skipping chart embedding.")
