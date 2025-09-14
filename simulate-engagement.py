from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, random, tempfile

BASE_URL = "http://192.168.29.191:8082"
PAGES = [
    "/home/index.html", "/about/index.html", "/contact/index.html",
    "/blog/index.html", "/services/index.html", "/pricing/index.html",
    "/faq/index.html", "/testimonials/index.html"
]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Linux; Android 10)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
]

NUM_USERS = 20

for i in range(NUM_USERS):
    print(f"Simulating user #{i+1}")
    temp_profile = tempfile.mkdtemp()
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"--user-data-dir={temp_profile}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    driver = webdriver.Chrome(options=options)

    visited_pages = random.sample(PAGES, k=random.randint(2, 5))
    for page in visited_pages:
        full_url = BASE_URL + page
        print(f"→ Visiting {full_url}")
        driver.get(full_url)
        time.sleep(random.randint(2, 6))  # Simulate time-on-page

    driver.quit()
    time.sleep(random.randint(1, 4))  # Delay between users
