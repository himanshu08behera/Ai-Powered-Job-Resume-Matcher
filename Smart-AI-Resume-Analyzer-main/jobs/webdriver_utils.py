"""Utility functions for webdriver setup and management.
Works on Streamlit Cloud (chromium + chromium-driver via packages.txt),
local Linux, macOS, and Windows.
"""
import os
import platform
import shutil
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Optional fallback: webdriver-manager
try:
    from webdriver_manager.chrome import ChromeDriverManager
    try:
        # New path (webdriver-manager >= 4.0)
        from webdriver_manager.core.os_manager import ChromeType
    except ImportError:
        # Old path (webdriver-manager < 4.0)
        from webdriver_manager.core.utils import ChromeType
    webdriver_manager_available = True
except Exception:
    webdriver_manager_available = False


def _find_first_existing(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def _find_chrome_binary():
    """Locate Chrome/Chromium executable across platforms."""
    system = platform.system()
    if system == "Windows":
        return _find_first_existing([
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ])
    # Linux / macOS
    return _find_first_existing([
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("google-chrome"),
    ])


def _find_chromedriver_binary():
    """Locate a system-installed chromedriver."""
    return _find_first_existing([
        "/usr/bin/chromedriver",
        "/usr/lib/chromium/chromedriver",
        "/usr/lib/chromium-browser/chromedriver",
        shutil.which("chromedriver"),
    ])


def _build_options(chrome_binary=None):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    if chrome_binary:
        options.binary_location = chrome_binary
    return options


def setup_webdriver():
    """
    Configure and return a Chrome webdriver. Tries multiple strategies.
    Returns None if nothing works.
    """
    chrome_binary = _find_chrome_binary()
    if not chrome_binary:
        st.error(
            "Chrome/Chromium not found. On Streamlit Cloud add 'chromium' to "
            "packages.txt. Locally, install Chrome or Chromium."
        )
        return None

    # --- Strategy 1: system chromium + system chromedriver (Streamlit Cloud path) ---
    driver_path = _find_chromedriver_binary()
    if driver_path:
        try:
            options = _build_options(chrome_binary)
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as e:
            st.warning(f"System chromedriver failed ({e}); trying fallbacks...")

    # --- Strategy 2: webdriver-manager download matching driver for chromium ---
    if webdriver_manager_available:
        try:
            options = _build_options(chrome_binary)
            service = Service(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
            )
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception:
            pass
        # Retry for regular Google Chrome
        try:
            options = _build_options(chrome_binary)
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception:
            pass

    # --- Strategy 3: chromedriver-autoinstaller ---
    try:
        import chromedriver_autoinstaller
        chromedriver_autoinstaller.install()
        options = _build_options(chrome_binary)
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception:
        pass

    # --- Strategy 4: let Selenium Manager handle everything (Selenium 4.10+) ---
    try:
        options = _build_options(chrome_binary)
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        st.error(
            "Failed to initialize Chrome webdriver after all fallbacks. "
            f"Last error: {e}"
        )
        return None