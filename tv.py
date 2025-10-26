import asyncio
import urllib.parse
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError

M3U8_FILE = "TheTVApp.m3u8"
BASE_URL = "https://thetvapp.to"
CHANNEL_LIST_URL = f"{BASE_URL}/tv"

# Increased default timeout to 60 seconds (60000ms) for navigation
DEFAULT_NAV_TIMEOUT = 60000 

SECTIONS_TO_APPEND = {
    "/nba": "NBA",
    "/mlb": "MLB",
    "/wnba": "WNBA",
    "/nfl": "NFL",
    "/ncaaf": "NCAAF",
    "/ncaab": "NCAAB",
    "/soccer": "Soccer",
    "/ppv": "PPV",
    "/events": "Events"
}

SPORTS_METADATA = {
    "MLB": {"tvg-id": "MLB.Baseball.Dummy.us", "logo": "http://drewlive24.duckdns.org:9000/Logos/Baseball-2.png"},
    "PPV": {"tvg-id": "PPV.EVENTS.Dummy.us", "logo": "http://drewlive24.duckdns.org:9000/Logos/PPV.png"},
    "NFL": {"tvg-id": "NFL.Dummy.us", "logo": "http://drewlive24.duckdns.org:9000/Logos/NFL.png"},
    "NCAAF": {"tvg-id": "NCAA.Football.Dummy.us", "logo": "http://drewlive24.duckdns.org:9000/Logos/CFB.png"},
}

def extract_real_m3u8(url: str):
    """
    Attempts to extract the real M3U8 URL from a redirect or a direct URL.
    """
    if "ping.gif" in url and "mu=" in url:
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        mu = qs.get("mu", [None])[0]
        if mu:
            return urllib.parse.unquote(mu)
    if ".m3u8" in url:
        return url
    return None

async def scrape_tv_urls():
    """Scrapes the main TV channel streams."""
    urls = []
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("🔄 Loading /tv channel list...")
        # *** FIX: Increased Timeout for initial navigation ***
        await page.goto(CHANNEL_LIST_URL, timeout=DEFAULT_NAV_TIMEOUT) 
        
        links = await page.locator("ol.list-group a").all()
        hrefs_and_titles = [(await link.get_attribute("href"), await link.text_content())
                            for link in links if await link.get_attribute("href")]
        await page.close()

        for href, title_raw in hrefs_and_titles:
            full_url = BASE_URL + href
            title = " - ".join(line.strip() for line in title_raw.splitlines() if line.strip())
            print(f"🎯 Scraping TV page: {full_url}")

            for quality in ["SD", "HD"]:
                stream_url = None
                new_page = await context.new_page()

                async def handle_response(response):
                    nonlocal stream_url
                    real = extract_real_m3u8(response.url)
                    if real and not stream_url:
                        stream_url = real

                new_page.on("response", handle_response)
                # *** FIX: Increased Timeout for channel page navigation ***
                try:
                    await new_page.goto(full_url, timeout=DEFAULT_NAV_TIMEOUT)
                except TimeoutError:
                    print(f"⚠️ Navigation timeout for {full_url}. Skipping stream check.")
                    await new_page.close()
                    continue

                try:
                    # Click timeout remains 60s, which is good for slow loading streams
                    await new_page.get_by_text(f"Load {quality} Stream", exact=True).click(timeout=60000)
                except TimeoutError as e:
                    # This catches timeouts specifically on the click, not the navigation
                    print(f"    Click timeout for {quality} stream on {title}: {e.name}")
                except Exception:
                    # Catch all other exceptions (e.g., element not found/disabled)
                    pass

                await asyncio.sleep(4)
                await new_page.close()

                if stream_url:
                    urls.append((stream_url, "TV", f"{title} {quality}"))
                    print(f"✅ {quality}: {stream_url}")
                else:
                    print(f"❌ {quality} not found")

        await browser.close()
    return urls

async def scrape_section_urls(context, section_path, group_name):
    """Scrapes streams for a specific sports section (e.g., /nba)."""
    urls = []
    page = await context.new_page()
    section_url = BASE_URL + section_path
    print(f"\n📁 Loading section: {section_url}")
    
    # *** FIX: Increased Timeout for section page navigation ***
    try:
        await page.goto(section_url, timeout=DEFAULT_NAV_TIMEOUT)
    except TimeoutError:
        print(f"⚠️ Navigation timeout for section {section_url}. Skipping section.")
        await page.close()
        return []
        
    links = await page.locator("ol.list-group a").all()
    hrefs_and_titles = []

    for link in links:
        href = await link.get_attribute("href")
        title_raw = await link.text_content()
        if href and title_raw:
            title = " - ".join(line.strip() for line in title_raw.splitlines() if line.strip())
            hrefs_and_titles.append((href, title))
    await page.close()

    for href, title in hrefs_and_titles:
        full_url = BASE_URL + href
        print(f"🎯 Scraping {group_name}: {title}")

        for quality in ["SD", "HD"]:
            stream_url = None
            new_page = await context.new_page()

            async def handle_response(response):
                nonlocal stream_url
                real = extract_real_m3u8(response.url)
                if real and not stream_url:
                    stream_url = real

            new_page.on("response", handle_response)
            
            # *** FIX: Increased Timeout for stream page navigation ***
            try:
                await new_page.goto(full_url, timeout=DEFAULT_NAV_TIMEOUT)
            except TimeoutError:
                print(f"⚠️ Navigation timeout for {full_url}. Skipping stream check.")
                await new_page.close()
                continue

            try:
                await new_page.get_by_text(f"Load {quality} Stream", exact=True).click(timeout=60000)
                await asyncio.sleep(4)
            except TimeoutError as e:
                print(f"    Click timeout for {quality} stream on {title}: {e.name}")
            except Exception:
                pass
            
            await new_page.close()

            if stream_url:
                urls.append((stream_url, group_name, f"{title} {quality}"))
                print(f"✅ {quality}: {stream_url}")
            else:
                print(f"❌ {quality} not found")
    return urls

async def scrape_all_sports_sections():
    """Launches Playwright and iterates over all sports sections to scrape URLs."""
    all_urls = []
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()

        for section_path, group_name in SECTIONS_TO_APPEND.items():
            urls = await scrape_section_urls(context, section_path, group_name)
            all_urls.extend(urls)

        await browser.close()
    return all_urls

def clean_m3u_header(lines):
    """Updates the M3U header with a current timestamp and EPG URL."""
    lines = [line for line in lines if not line.strip().startswith("#EXTM3U")]
    timestamp = int(datetime.utcnow().timestamp())
    lines.insert(0, f'#EXTM3U url-tvg="https://tvpass.org/epg.xml" # Updated: {timestamp}')
    return lines

def replace_tv_urls(lines, tv_urls):
    """Replaces existing /tv URLs in the M3U8 file with newly scraped ones."""
    updated = []
    tv_idx = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check if the line is a URL and we still have new URLs to insert
        if line.strip().startswith("http") and tv_idx < len(tv_urls):
            stream_url, group, title = tv_urls[tv_idx]
            
            # Update the EXTINF line immediately preceding the URL
            if i > 0 and lines[i - 1].startswith("#EXTINF"):
                extinf = lines[i - 1]
                # Replace the display title at the end of the EXTINF line
                if "," in extinf:
                    parts = extinf.split(",")
                    parts[-1] = title
                    extinf = ",".join(parts)
                updated[-1] = extinf # Replace the old EXTINF line
                
            updated.append(stream_url) # Append the new URL
            tv_idx += 1
        else:
            updated.append(line)
        i += 1
    return updated

def refresh_sports_sections(lines, new_sports_urls):
    """Removes old sports sections and appends the new ones."""
    cleaned_lines = []
    i = 0
    sports_groups = set(SECTIONS_TO_APPEND.values())
    
    # First, filter out existing sports section lines
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF"):
            # Check if this EXTINF belongs to one of the sports sections we are refreshing
            group = line.split('group-title="')[1].split('"')[0] if 'group-title="' in line else ""
            if group.replace("TheTVApp - ", "") in sports_groups:
                # Skip the current EXTINF line and the following URL line
                i += 2  
                continue
        cleaned_lines.append(line)
        i += 1
    
    # Second, append the newly scraped sports streams
    for url, group, title in new_sports_urls:
        meta = SPORTS_METADATA.get(group, {})
        tvg_id = meta.get("tvg-id", "")
        logo = meta.get("logo", "")
        
        # Replace commas in display title with dash for clean M3U8
        display_title = title.replace(",", " -")
        
        # Construct the EXTINF line
        if tvg_id or logo:
            ext = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{title}" tvg-logo="{logo}" group-title="TheTVApp - {group}",{display_title}'
        else:
            ext = f'#EXTINF:-1 tvg-name="{title}" group-title="TheTVApp - {group}",{display_title}'
            
        cleaned_lines.append(ext)
        cleaned_lines.append(url)

    return cleaned_lines

async def main():
    """Main execution function to scrape and write the M3U8 file."""
    if not Path(M3U8_FILE).exists():
        print(f"❌ File not found: {M3U8_FILE}. Ensure you have a template M3U8 file.")
        return

    try:
        with open(M3U8_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except Exception as e:
        print(f"Error reading {M3U8_FILE}: {e}")
        return

    lines = clean_m3u_header(lines)

    print("🔧 Replacing /tv stream URLs...")
    tv_new_urls = await scrape_tv_urls()
    if tv_new_urls:
        lines = replace_tv_urls(lines, tv_new_urls)

    print("\n📦 Refreshing all sports sections...")
    sports_new_urls = await scrape_all_sports_sections()
    if sports_new_urls:
        lines = refresh_sports_sections(lines, sports_new_urls)

    try:
        with open(M3U8_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception as e:
        print(f"Error writing to {M3U8_FILE}: {e}")
        return

    print(f"\n✅ {M3U8_FILE} fully refreshed and working.")

if __name__ == "__main__":
    asyncio.run(main())
