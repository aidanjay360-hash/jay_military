import sys
import re
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

YES_WORDS = [
    "study", "research", "scientists", "experts", "officials",
    "according to", "evidence", "data", "report", "confirmed",
    "court", "police", "government", "university"
]

NO_WORDS = [
    "shocking", "you won't believe", "miracle", "secret",
    "exposed", "conspiracy", "hoax", "fake", "rumor",
    "allegedly", "anonymous source", "click here"
]


def get_article_text(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = " ".join(soup.get_text(" ").split())
    return text[:8000]


def decide_yes_no(text):
    text_lower = text.lower()

    yes_score = sum(1 for word in YES_WORDS if word in text_lower)
    no_score = sum(1 for word in NO_WORDS if word in text_lower)

    print(f"YES score: {yes_score}")
    print(f"NO score: {no_score}")

    return "Yes" if yes_score >= no_score else "No"


def click_answer(page, answer):
    selectors = [
        f"text={answer}",
        f"label:has-text('{answer}')",
        f"button:has-text('{answer}')",
        f"input[value='{answer}']"
    ]

    for selector in selectors:
        try:
            page.locator(selector).first.click(timeout=3000)
            print(f"Clicked {answer}")
            return True
        except:
            pass

    return False


def click_next(page):
    selectors = [
        "text=Next",
        "button:has-text('Next')",
        "input[value='Next']",
        "text=Submit",
        "button:has-text('Submit')"
    ]

    for selector in selectors:
        try:
            page.locator(selector).first.click(timeout=3000)
            print("Clicked Next/Submit")
            return True
        except:
            pass

    return False


def main():
    if len(sys.argv) < 2:
        print('Usage: python qualtrics_automator_no_ai.py "ARTICLE_URL"')
        sys.exit(1)

    article_url = sys.argv[1]

    print("Reading article...")
    article_text = get_article_text(article_url)

    answer = decide_yes_no(article_text)
    print(f"Chosen answer: {answer}")

    survey_url = input("Paste the Qualtrics survey URL: ").strip()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(survey_url)

        input("Press Enter once the survey page is loaded...")

        if not click_answer(page, answer):
            print("Could not click Yes/No. Saving screenshot.")
            page.screenshot(path="survey_debug.png")
            return

        if not click_next(page):
            print("Could not click Next. Saving screenshot.")
            page.screenshot(path="survey_debug.png")
            return

        print("Done.")
        input("Press Enter to close browser...")
        browser.close()


if __name__ == "__main__":
    main()