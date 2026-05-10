import time
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


def decide_yes_no(page_text):
    text = page_text.lower()

    yes_score = sum(1 for word in YES_WORDS if word in text)
    no_score = sum(1 for word in NO_WORDS if word in text)

    print(f"YES score: {yes_score} | NO score: {no_score}")

    if yes_score >= no_score:
        return "Yes"
    else:
        return "No"


def click_answer(page, answer):
    selectors = [
        f"label:has-text('{answer}')",
        f"button:has-text('{answer}')",
        f"text={answer}",
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
        "button:has-text('Next')",
        "input[value='Next']",
        "text=Next",
        "button:has-text('Submit')",
        "input[value='Submit']",
        "text=Submit"
    ]

    for selector in selectors:
        try:
            page.locator(selector).first.click(timeout=3000)
            print("Clicked Next/Submit")
            return True
        except:
            pass

    return False


def survey_done(page):
    text = page.inner_text("body").lower()

    done_phrases = [
        "thank you",
        "your response has been recorded",
        "survey complete",
        "submitted"
    ]

    return any(phrase in text for phrase in done_phrases)


def main():
    survey_url = input("Paste Qualtrics survey URL: ").strip()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(survey_url)

        input("Press Enter once the first article/question is loaded...")

        question_number = 1

        while True:
            time.sleep(2)

            if survey_done(page):
                print("Survey looks complete.")
                break

            print(f"\n--- Question/Page {question_number} ---")

            page_text = page.inner_text("body")
            answer = decide_yes_no(page_text)
            print(f"Chosen answer: {answer}")

            if not click_answer(page, answer):
                print("Could not click Yes/No. Saving screenshot.")
                page.screenshot(path=f"survey_debug_{question_number}.png")
                break

            time.sleep(1)

            if not click_next(page):
                print("Could not click Next/Submit. Saving screenshot.")
                page.screenshot(path=f"survey_debug_{question_number}.png")
                break

            question_number += 1

        input("Press Enter to close browser...")
        browser.close()


if __name__ == "__main__":
    main()