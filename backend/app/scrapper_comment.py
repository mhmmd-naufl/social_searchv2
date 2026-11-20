"""Ambil komentar dari halaman video lalu analisis sentimennya."""

import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)

from .analysis.analysis_comment import analyze_comments_from_data, lexicon

# Beberapa kandidat selector karena TikTok sering mengubah data-e2e.
COMMENT_SELECTORS = [
    'span[data-e2e="comment-level-1"]',
    'div[data-e2e="comment-level-1"]',
    '[data-e2e="comment-item"]',
    'p[data-e2e="comment-text"]',
]


def random_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))


def wait_for_page_load(driver):
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(2)


def find_comment_selectors(driver):
    for selector in COMMENT_SELECTORS:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            print(f"Ditemukan {len(elements)} elemen dengan selector: {selector}")
            return selector
    return None


def _scroll_comment_container(driver, selector):
    """Scroll kontainer komentar (atau halaman) untuk memuat komentar lain."""
    try:
        return driver.execute_script(
            """
            const root = document.querySelector(arguments[0]);
            if (!root) { window.scrollTo(0, document.body.scrollHeight); return false; }
            let node = root.parentElement;
            while (node) {
                const style = window.getComputedStyle(node);
                const scrollable =
                    style.overflowY === 'auto' || style.overflowY === 'scroll';
                if (scrollable && node.scrollHeight > node.clientHeight + 10) {
                    node.scrollTop = node.scrollHeight;
                    return true;
                }
                node = node.parentElement;
            }
            window.scrollTo(0, document.body.scrollHeight);
            return false;
            """,
            selector,
        )
    except Exception as exc:
        print(f"Gagal scroll kontainer komentar: {exc}")
        return False


def collect_comments(driver, max_scroll=5):
    selector = find_comment_selectors(driver)
    if not selector:
        time.sleep(5)
        selector = find_comment_selectors(driver)
    if not selector:
        print("Selector komentar tidak ditemukan.")
        driver.save_screenshot("debug_screenshot.png")
        return []

    comments = []
    seen = set()

    for attempt in range(max_scroll + 1):
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        for element in elements:
            try:
                text = element.text.strip()
                if text and text not in seen:
                    seen.add(text)
                    comments.append(text)
            except (NoSuchElementException, StaleElementReferenceException):
                continue

        print(f"Scroll komentar {attempt + 1}/{max_scroll + 1}: {len(comments)} komentar")
        if attempt == max_scroll:
            break

        _scroll_comment_container(driver, selector)
        random_delay(1, 2)

    print(f"Total komentar diambil: {len(comments)}")
    return comments


def cek(driver, video_data):
    try:
        url = video_data["video_link"]
        driver.get(url)
        random_delay(2, 4)
        print(f"Mengunjungi URL: {url}")
        wait_for_page_load(driver)

        comments = collect_comments(driver)
        return analyze_comments_from_data(comments, lexicon)
    except Exception as e:
        print(f"Terjadi error: {e}")
        driver.save_screenshot("error_screenshot.png")
        return []
