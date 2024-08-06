# app.py
from playwright.sync_api import sync_playwright

def test_playwright(url: str):
    try:
        with sync_playwright() as p:
            browser = p.webkit.launch()
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            browser.close()
            return f"Playwright ran successfully using WebKit. First 1000 characters of content:\n{content[:1000]}"
    except Exception as e:
        return f"Error running Playwright: {str(e)}"

if __name__ == "__main__":
    url = "https://google.com"  # Change to any URL you want to test
    result = test_playwright(url)
    print(result)
