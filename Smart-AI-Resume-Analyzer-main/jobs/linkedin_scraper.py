import time
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
}

LIST_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"


# 🔥 FIXED: latest jobs + sorting
def _fetch_listings(keywords, location, start):
    params = {
        "keywords": keywords,
        "location": location,
        "start": start,
        "f_TPR": "r86400",   # ✅ last 24 hours
        "sortBy": "DD"       # ✅ newest first
    }

    try:
        r = requests.get(LIST_URL, headers=HEADERS, params=params, timeout=15)
        if r.status_code == 200:
            return r.text
        else:
            print("Status Code:", r.status_code)
    except Exception as e:
        print("Error:", e)

    return ""


def _parse_cards(html):
    soup = BeautifulSoup(html, "lxml")
    rows = []

    for c in soup.find_all("div", class_="base-card"):
        try:
            title = c.find("h3", class_="base-search-card__title")
            company = c.find("h4", class_="base-search-card__subtitle")
            loc = c.find("span", class_="job-search-card__location")
            link = c.find("a", class_="base-card__full-link")

            if not (title and company and link):
                continue

            rows.append({
                "Job Title": title.get_text(strip=True),
                "Company Name": company.get_text(strip=True),
                "Location": loc.get_text(strip=True) if loc else "",
                "Website URL": link.get("href", "").split("?")[0],
            })
        except:
            continue

    return rows


def _fetch_description(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return "Description not available"

        soup = BeautifulSoup(r.text, "lxml")
        d = soup.find("div", class_="show-more-less-html__markup")

        if d:
            return d.get_text("\n", strip=True)

    except:
        pass

    return "Description not available"


def _scrape(keywords, location, count):
    rows = []
    start = 0

    while len(rows) < count and start < 75:
        html = _fetch_listings(keywords, location, start)
        if not html:
            break

        new_rows = _parse_cards(html)
        if not new_rows:
            break

        rows.extend(new_rows)
        start += 25
        time.sleep(1)

    if not rows:
        return pd.DataFrame()

    # 🔥 remove duplicates
    df = pd.DataFrame(rows).drop_duplicates(subset=["Website URL"])
    df = df.head(count)

    descriptions = []
    for url in df["Website URL"]:
        descriptions.append(_fetch_description(url))
        time.sleep(0.5)

    df["Job Description"] = descriptions
    return df


def render_linkedin_scraper():
    st.title("LinkedIn Job Scraper")

    with st.form("scraper"):
        title = st.text_input("Job Title")
        location = st.text_input("Location", value="India")
        count = st.number_input("Number of Jobs", 1, 25, 5)

        submit = st.form_submit_button("Search")

    if not submit:
        return

    if not title:
        st.warning("Enter job title")
        return

    with st.spinner("Fetching latest jobs..."):
        df = _scrape(title, location, int(count))

    if df.empty:
        st.error("No jobs found")
        return

    st.success(f"Found {len(df)} latest jobs")

    for _, row in df.iterrows():
        st.subheader(row["Job Title"])
        st.write(f"{row['Company Name']} - {row['Location']}")

        with st.expander("Description"):
            st.write(row["Job Description"])
            st.markdown(f"[Apply Here]({row['Website URL']})")

        st.markdown("---")
