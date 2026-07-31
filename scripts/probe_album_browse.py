from __future__ import annotations

from playwright.sync_api import sync_playwright


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--autoplay-policy=no-user-gesture-required"],
        )
        page = browser.new_page()
        page.goto("http://127.0.0.1:8765/", wait_until="domcontentloaded")
        page.wait_for_function(
            """() => {
              const el = document.getElementById('coverIndex');
              return el && /\\d+\\/\\d+/.test(el.textContent || '') && !el.textContent.startsWith('0/');
            }""",
            timeout=60000,
        )
        page.click("#settingsBtn")
        page.wait_for_timeout(250)
        page.click("#libraryBrowseAlbumBtn")
        page.wait_for_timeout(400)
        page.click("#settingsCloseBtn")
        page.wait_for_timeout(500)
        btn = page.locator("#singBtn").inner_text().strip().lower()
        print("primary", btn)
        assert btn.startswith("obrir"), btn
        page.click("#singBtn")
        page.wait_for_timeout(700)
        assert page.locator("#albumBackBtn").is_visible()
        detail_btn = page.locator("#singBtn").inner_text().strip().lower()
        print("detail", detail_btn, page.locator("#coverTitle").inner_text())
        assert detail_btn == "cantar" or detail_btn.startswith("sincron")
        page.click("#albumBackBtn")
        page.wait_for_timeout(500)
        print("back", page.locator("#singBtn").inner_text())
        browser.close()
    print("OK")


if __name__ == "__main__":
    main()
