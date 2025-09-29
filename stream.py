import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright, Request


BASE_URL = "https://www.streameast.pk"
M3U8_FILE = "StreamEast.m3u8"


CATEGORY_LOGOS = {
    "StreamEast - PPV Events": "https://github.com/BuddyChewChew/My-Streams/blob/main/Logos/sports/ppv2.png?raw=true",
    "StreamEast - Soccer": "https://github.com/BuddyChewChew/My-Streams/blob/main/Logos/sports/football.png?raw=true",
    "StreamEast - F1": "https://github.com/BuddyChewChew/My-Streams/blob/main/Logos/sports/f1.png?raw=true",
    "StreamEast - Boxing": "https://github.com/BuddyChewChew/My-Streams/blob/main/Logos/sports/boxing.png?raw=true",
    "StreamEast - MMA": "https://github.com/BuddyChewChew/My-Streams/blob/main/Logos/sports/mma.png?raw=true",
    "StreamEast - WWE": "https://github.com/BuddyChewChew/My-Streams/blob/main/Logos/sports/wwe.png?raw=true",
    "StreamEast - Golf": "https://github.com/BuddyChewChew/My-Streams/blob/main/Logos/sports/golf.png?raw=true",
    "StreamEast - Am. Football": "https://github.com/BuddyChewChew/My-Streams/blob/main/Logos/sports/nfl.png?raw=true",
    "StreamEast - Baseball": "https://github.com/BuddyChewChew/My-Streams/blob/main/Logos/sports/baseball.png?raw=true",
    "StreamEast - Basketball Hub": "https://github.com/BuddyChewChew/My-Streams/blob/main/Logos/sports/nba.png?raw=true",
    "StreamEast - Hockey": "https://github.com/BuddyChewChew/My-Streams/blob/main/Logos/sports/hockey.png?raw=true",
    "StreamEast - WNBA": "https://github.com/BuddyChewChew/My-Streams/blob/main/Logos/sports/wnba.png?raw=true",
}


CATEGORY_TVG_IDS = {
    "StreamEast - PPV Events": "PPV.EVENTS.Dummy.us",
    "StreamEast - Soccer": "Soccer.Dummy.us",
    "StreamEast - F1": "Racing.Dummy.us",
    "StreamEast - Boxing": "Boxing.Dummy.us",
    "StreamEast - MMA": "UFC.Fight.Pass.Dummy.us",
    "StreamEast - WWE": "PPV.EVENTS.Dummy.us",
    "StreamEast - Golf": "Golf.Dummy.us",
    "StreamEast - Am. Football": "NFL.Dummy.us",
    "StreamEast - Baseball": "MLB.Baseball.Dummy.us",
    "StreamEast - Basketball Hub": "Basketball.Dummy.us",
    "StreamEast - Hockey": "NHL.Hockey.Dummy.us",
    "StreamEast - WNBA": "WNBA.dummy.us",
}


def categorize_stream(url, title=""):
    lowered = (url + " " + title).lower()
    if "wnba" in lowered: return "StreamEast - WNBA"
    if "nba" in lowered or "basketball" in lowered: return "StreamEast - Basketball Hub"
    if "nfl" in lowered or "football" in lowered: return "StreamEast - Am. Football"
    if "mlb" in lowered or "baseball" in lowered: return "StreamEast - Baseball"
    if "ufc" in lowered or "mma" in lowered: return "StreamEast - MMA"
    if "wwe" in lowered or "wrestling" in lowered: return "StreamEast - WWE"
    if "boxing" in lowered: return "StreamEast - Boxing"
    if "soccer" in lowered or "futbol" in lowered: return "StreamEast - Soccer"
    if "golf" in lowered: return "StreamEast - Golf"
    if "hockey" in lowered or "nhl" in lowered: return "StreamEast - Hockey"
    if "f1" in lowered or "nascar" in lowered or "motorsport" in lowered: return "StreamEast - F1"
    return "StreamEast - PPV Events"


async def safe_goto(page, url, tries=2, timeout=20000):
    for attempt in range(tries):
        try:
            await page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            html = await page.content()
            if any(x in html.lower() for x in ["cloudflare", "just a moment", "attention required"]):
                await asyncio.sleep(2)
                continue
            return True
        except Exception as e:
            print(f"⚠️ Error loading {url}: {e}")
            await asyncio.sleep(2)
    return False


async def get_event_links(page):
    print("🌐 Gathering links...")
    if not await safe_goto(page, BASE_URL):
        return []
    links = await page.evaluate("""() => Array.from(document.querySelectorAll('a'))
        .map(a => a.href)
        .filter(h => h.includes('/nba') || h.includes('/mlb') || h.includes('/ufc') ||
                     h.includes('/f1') || h.includes('/soccer') || h.includes('/wnba') ||
                     h.includes('/boxing') || h.includes('/wwe') || h.includes('/nfl'))""")
    return list(set(links))


async def scrape_stream_url(context, url):
    m3u8_links = set()
    event_name = "Unknown Event"
    page = await context.new_page()


    def capture_request(request: Request):
        if ".m3u8" in request.url.lower() and not m3u8_links:
            print(f"🎯 Found stream: {request.url}")
            m3u8_links.add(request.url)


    page.on("request", capture_request)


    try:
        if not await safe_goto(page, url): return event_name, []
        await asyncio.sleep(1)


        event_name = await page.evaluate("""
            () => {
                const selectors = ['h1', '.event-title', '.title', '.stream-title'];
                for (let sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) return el.textContent.trim();
                }
                return document.title.trim();
            }
        """)


        await page.mouse.click(500, 500)
        for _ in range(10):
            if m3u8_links:
                break
            await asyncio.sleep(0.5)


    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
    finally:
        await page.close()


    return event_name, list(m3u8_links)



async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 Firefox/139.0")


        main_page = await context.new_page()
        links = await get_event_links(main_page)
        await main_page.close()


        with open(M3U8_FILE, "w", encoding="utf-8") as f:
            f.write(f"# Updated at {datetime.utcnow().isoformat()}Z\n")
            f.write("#EXTM3U url-tvg=\"https://epgshare01.online/epgshare01/epg_ripper_DUMMY_CHANNELS.xml.gz\"\n")


            for idx, link in enumerate(links, 1):
                print(f"\n➡️ [{idx}/{len(links)}] {link}")
                name, streams = await scrape_stream_url(context, link)
                category = categorize_stream(link, name)
                logo = CATEGORY_LOGOS.get(category, "")
                tvg_id = CATEGORY_TVG_IDS.get(category, "")


                for s_url in streams:
                    f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{category}",{name}\n')
                    f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0\n')
                    f.write('#EXTVLCOPT:http-origin=https://streamscenter.online\n')
                    f.write('#EXTVLCOPT:http-referrer=https://streamscenter.online/\n')
                    f.write(f'{s_url}\n\n')
                await asyncio.sleep(0.5)


        print("✅ StreamEast.m3u8 saved.")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
