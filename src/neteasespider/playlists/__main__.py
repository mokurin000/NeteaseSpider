import json
from time import sleep
from os import makedirs

from playwright.sync_api import sync_playwright, Playwright, Page, Locator
from neteasespider import PLAYLIST_PATH, CATEGORY


BASE_URL = f"https://music.163.com/#/discover/playlist/?cat={CATEGORY}"


def scrap(page: Page, category: str, page_num: int):
    limit = 35
    offset = (page_num - 1) * limit
    url = f"{BASE_URL}&limit={limit}&offset={offset}"
    page.goto(url, wait_until="networkidle")
    real_page = page.frame_locator("#g_iframe")
    a_locs: list[Locator] = real_page.locator("a.msk").all()
    sleep(3)
    print("Found", len(a_locs), "lists")
    data = []
    for loc in a_locs:
        href = loc.get_attribute("href")
        data.append(href.split("=")[-1])

    makedirs(PLAYLIST_PATH, exist_ok=True)
    with open(
        f"{PLAYLIST_PATH}/{category}_{page_num:03}.json", mode="w+", encoding="utf-8"
    ) as free:
        json.dump(data, free, ensure_ascii=False, indent=4)


def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(f"{BASE_URL}")
    for page_num in range(1, 47 + 1):
        scrap(page, "playlist", page_num)
        sleep(2)
    browser.close()


def main():
    with sync_playwright() as playwright:
        run(playwright)


if __name__ == "__main__":
    main()
