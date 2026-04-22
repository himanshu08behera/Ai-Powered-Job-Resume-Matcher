

import time
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

LIST_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"


def _fetch_listings(keywords, location, start):
    params = {"keywords": keywords, "location": location, "start": start}
    try:
        r = requests.get(LIST_URL, headers=HEADERS, params=params, timeout=15)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return ""


def _parse_cards(html):
    soup = BeautifulSoup(html, "lxml")
    rows = []
    for c in soup.find_all("div", class_="base-card"):
        title = c.find("h3", class_="base-search-card__title")
        company = c.find("h4", class_="base-search-card__subtitle")
        loc = c.find("span", class_="job-search-card__location")
        link = c.find("a", class_="base-card__full-link") or c.find("a")
        if not (title and company and link):
            continue
        rows.append({
            "Job Title": title.get_text(strip=True),
            "Company Name": company.get_text(strip=True),
            "Location": loc.get_text(strip=True) if loc else "",
            "Website URL": link.get("href", "").split("?")[0],
        })
    return rows


def _fetch_description(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return "Description not available"
        soup = BeautifulSoup(r.text, "lxml")
        d = soup.find("div", class_="show-more-less-html__markup") or soup.find("div", class_="description__text")
        if d:
            t = d.get_text("\n", strip=True)
            if t:
                return t
    except Exception:
        pass
    return "Description not available"


def _scrape(keywords, location, count):
    rows, start = [], 0
    bar = st.progress(0)
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
    rows = rows[:count]
    if not rows:
        bar.empty()
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    descs = []
    for i, u in enumerate(df["Website URL"].tolist()):
        bar.progress(int((i + 1) / len(df) * 100))
        descs.append(_fetch_description(u))
        time.sleep(0.8)
    df["Job Description"] = descs
    bar.empty()
    return df


def render_linkedin_scraper():
    st.markdown("### LinkedIn Job Scraper")
    st.caption("Find real-time job listings directly from LinkedIn")

    with st.form("linkedin_scrape"):
        c1, c2, c3 = st.columns([5, 3, 2])
        with c1:
            title = st.text_input("Job Title", placeholder="e.g. Data Scientist")
        with c2:
            location = st.text_input("Job Location", value="India")
        with c3:
            count = st.number_input("Number of Jobs", 1, 25, 5, 1)
        submit = st.form_submit_button("Search LinkedIn Jobs", type="primary", use_container_width=True)

    if not submit:
        return
    if not title.strip():
        st.warning("Please enter a job title.")
        return
    if not location.strip():
        st.warning("Please enter a job location.")
        return

    with st.spinner("Searching LinkedIn..."):
        df = _scrape(title.strip(), location.strip(), int(count))

    if df.empty:
        st.warning("No jobs found. Try different search terms.")
        return

    st.success("Found " + str(len(df)) + " jobs on LinkedIn")
    for i in range(len(df)):
        row = df.iloc[i]
        st.markdown("#### " + str(row["Job Title"]))
        st.markdown("**" + str(row["Company Name"]) + "** - " + str(row["Location"]))
        with st.expander("View Job Description"):
            st.markdown(str(row["Job Description"]))
            st.markdown("[Apply on LinkedIn](" + str(row["Website URL"]) + ")")
        st.markdown("---")
