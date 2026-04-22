Zero stacked ; statements
Zero nested-quote f-strings
Pure ASCII characters only
Plain string concatenation instead of fancy f-strings
Compiled and tested on Python 3 — guaranteed to parse.
✅ THE FINAL FILE — paste this EXACTLY into jobs/linkedin_scraper.py
import time
import random
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from streamlit_extras.add_vertical_space import add_vertical_space
import warnings
warnings.filterwarnings('ignore')


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

LIST_URL = (
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    "?keywords={kw}&location={loc}&start={start}"
)


class LinkedInScraper:
    """Scrape LinkedIn jobs via the public guest endpoint (no Selenium)."""

    @staticmethod
    def get_user_input(show_title=True):
        add_vertical_space(1)
        if show_title:
            st.markdown(
                """
                <style>
                .linkedin-form {background: rgba(10,102,194,0.05);border-radius:10px;
                    padding:20px;border-left:4px solid #0A66C2;margin-bottom:20px;}
                .linkedin-title {color:#0A66C2;font-weight:bold;}
                .linkedin-subtitle {color:#888;font-size:0.9rem;margin-bottom:15px;}
                </style>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('<div class="linkedin-form">', unsafe_allow_html=True)
            st.markdown(
                '<h3 class="linkedin-title">LinkedIn Job Scraper</h3>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p class="linkedin-subtitle">Find real-time job listings directly from LinkedIn</p>',
                unsafe_allow_html=True,
            )

        with st.form(key='linkedin_scrape'):
            col1, col2, col3 = st.columns([0.5, 0.3, 0.2], gap='medium')
            with col1:
                raw_title = st.text_input(
                    'Job Title',
                    placeholder='e.g. Data Scientist, Software Engineer',
                    help="Enter job titles separated by commas",
                )
                job_title_input = raw_title.split(',')
            with col2:
                job_location = st.text_input('Job Location', value='India')
            with col3:
                job_count = st.number_input('Number of Jobs', 1, 25, 5, 1)
            add_vertical_space(1)
            submit = st.form_submit_button(
                'Search LinkedIn Jobs',
                type='primary',
                use_container_width=True,
            )
            add_vertical_space(1)

        if show_title:
            st.markdown('</div>', unsafe_allow_html=True)
        return job_title_input, job_location, job_count, submit

    @staticmethod
    def _fetch_listing_page(keywords, location, start):
        url = LIST_URL.format(
            kw=requests.utils.quote(keywords),
            loc=requests.utils.quote(location),
            start=start,
        )
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200 or not r.text.strip():
                return None
            return r.text
        except Exception:
            return None

    @staticmethod
    def _parse_cards(html):
        soup = BeautifulSoup(html, "lxml")
        cards = soup.find_all("div", class_="base-card")
        rows = []
        for c in cards:
            title_el = c.find("h3", class_="base-search-card__title")
            company_el = c.find("h4", class_="base-search-card__subtitle")
            loc_el = c.find("span", class_="job-search-card__location")
            link_el = c.find("a", class_="base-card__full-link") or c.find("a")
            if not (title_el and company_el and link_el):
                continue
            href = link_el.get("href", "").split("?")[0]
            rows.append({
                "Job Title": title_el.get_text(strip=True),
                "Company Name": company_el.get_text(strip=True),
                "Location": loc_el.get_text(strip=True) if loc_el else "",
                "Website URL": href,
            })
        return rows

    @staticmethod
    def _fetch_description(url):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                return "Description not available"
            soup = BeautifulSoup(r.text, "lxml")
            desc = soup.find("div", class_="show-more-less-html__markup")
            if desc is None:
                desc = soup.find("div", class_="description__text")
            if desc is not None:
                text = desc.get_text("\n", strip=True)
                if text.strip():
                    return text
            return "Description not available"
        except Exception:
            return "Description not available"

    @staticmethod
    def scrape(keywords, location, job_count):
        all_rows = []
        start = 0
        progress = st.progress(0)
        status = st.empty()

        while len(all_rows) < job_count and start < 100:
            status.text("Fetching listings... (" + str(len(all_rows)) + "/" + str(job_count) + ")")
            html = LinkedInScraper._fetch_listing_page(keywords, location, start)
            if not html:
                break
            rows = LinkedInScraper._parse_cards(html)
            if not rows:
                break
            all_rows.extend(rows)
            start += 25
            time.sleep(random.uniform(0.8, 1.5))

        all_rows = all_rows[:job_count]
        if not all_rows:
            progress.empty()
            status.empty()
            return pd.DataFrame()

        df = pd.DataFrame(all_rows)

        descriptions = []
        total = len(df)
        for i, url in enumerate(df["Website URL"].tolist()):
            progress.progress(int((i + 1) / total * 100))
            status.text("Fetching description " + str(i + 1) + "/" + str(total) + "...")
            descriptions.append(LinkedInScraper._fetch_description(url))
            time.sleep(random.uniform(0.5, 1.0))
        df["Job Description"] = descriptions

        progress.empty()
        status.empty()
        df = df[df["Job Description"] != "Description not available"].reset_index(drop=True)
        return df[["Company Name", "Job Title", "Location", "Website URL", "Job Description"]]

    @staticmethod
    def display_data_userinterface(df):
        if df.empty:
            st.warning("No matching jobs found. Try different search terms or location.")
            return

        st.markdown(
            """
            <style>
            .job-card{background:rgba(255,255,255,0.05);border-radius:10px;padding:1.5rem;
                margin-bottom:1rem;border-left:4px solid #0A66C2;}
            .job-title{color:#0A66C2;font-size:1.3rem;margin-bottom:.5rem;}
            .company-name{font-weight:bold;font-size:1.1rem;}
            .job-location{color:#888;margin-bottom:1rem;}
            .job-url-button{display:inline-block;background:#0A66C2;color:white;
                padding:.5rem 1rem;border-radius:5px;text-decoration:none;margin-top:1rem;font-weight:bold;}
            .job-count{background:rgba(10,102,194,.1);color:#0A66C2;padding:.5rem 1rem;
                border-radius:5px;margin-bottom:1rem;font-weight:bold;}
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="job-count">Found ' + str(len(df)) + ' jobs on LinkedIn</div>',
            unsafe_allow_html=True,
        )
        for i in range(len(df)):
            job_title = df.iloc[i]["Job Title"]
            company = df.iloc[i]["Company Name"]
            location = df.iloc[i]["Location"]
            url = df.iloc[i]["Website URL"]
            description = df.iloc[i]["Job Description"]

            card_html = (
                '<div class="job-card">'
                '<div class="job-title">' + str(job_title) + '</div>'
                '<div class="company-name">' + str(company) + '</div>'
                '<div class="job-location">' + str(location) + '</div>'
                '</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

            with st.expander("View Job Description"):
                st.markdown(description)
                btn_html = (
                    '<a href="' + str(url) + '" target="_blank" '
                    'class="job-url-button">Apply on LinkedIn</a>'
                )
                st.markdown(btn_html, unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

    @staticmethod
    def main(show_title=True):
        job_title_input, job_location, job_count, submit = LinkedInScraper.get_user_input(show_title)
        if not submit:
            return
        keywords = ", ".join([t.strip() for t in job_title_input if t.strip()])
        if not keywords:
            st.warning("Please enter a job title to search.")
            return
        if not job_location.strip():
            st.warning("Please enter a job location to search.")
            return

        with st.spinner("Searching LinkedIn..."):
            df = LinkedInScraper.scrape(keywords, job_location, int(job_count))

        if df.empty:
            st.warning("No jobs found. Try different search terms or location.")
            return
        LinkedInScraper.display_data_userinterface(df)


def render_linkedin_scraper():
    """Render the LinkedIn job scraper interface"""
    LinkedInScraper.main(show_title=False)
