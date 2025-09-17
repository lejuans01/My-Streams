import asyncio
import urllib.parse
from pathlib import Path
from playwright.async_api import async_playwright

M3U8_FILE = "TheTVApp.m3u8"
BASE_URL = "https://thetvapp.to"
CHANNEL_LIST_URL = f"{BASE_URL}/tv"

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

def extract_real_m3u8(url: str):
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
    urls = []
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"🔄 Loading /tv channel list...")
        await page.goto(CHANNEL_LIST_URL, timeout=60000)  # 60 seconds)
        links = await page.locator("ol.list-group a").all()
        hrefs = [await link.get_attribute("href") for link in links if await link.get_attribute("href")]
        await page.close()

        for href in hrefs:
            full_url = BASE_URL + href
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
                await new_page.goto(full_url)
                try:
                    await new_page.get_by_text(f"Load {quality} Stream", exact=True).click(timeout=5000)
                except:
                    pass
                await asyncio.sleep(4)
                await new_page.close()

                if stream_url:
                    print(f"✅ {quality}: {stream_url}")
                    urls.append(stream_url)
                else:
                    print(f"❌ {quality} not found")

        await browser.close()
    return urls

async def scrape_section_urls(context, section_path, group_name):
    urls = []
    page = await context.new_page()
    section_url = BASE_URL + section_path
    print(f"\n📁 Loading section: {section_url}")
    await page.goto(section_url, timeout=60000)
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
            await new_page.goto(full_url, timeout=60000)

            try:
                await new_page.get_by_text(f"Load {quality} Stream", exact=True).click(timeout=5000)
            except:
                pass

            await asyncio.sleep(4)
            await new_page.close()

            if stream_url:
                print(f"✅ {quality}: {stream_url}")
                urls.append((stream_url, group_name, title))
            else:
                print(f"❌ {quality} not found")

    return urls

async def scrape_all_append_sections():
    all_urls = []
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()

        for section_path, group_name in SECTIONS_TO_APPEND.items():
            urls = await scrape_section_urls(context, section_path, group_name)
            all_urls.extend(urls)

        await browser.close()
    return all_urls

def replace_urls_in_tv_section(lines, tv_urls):
    result = []
    url_idx = 0
    for line in lines:
        if line.strip().startswith("http") and url_idx < len(tv_urls):
            result.append(tv_urls[url_idx])
            url_idx += 1
        else:
            result.append(line)
    return result

def is_sporting_event(group, title):
    """Check if a channel is a sporting event that might expire."""
    sports_groups = ["NBA", "MLB", "NFL", "NCAAF", "NCAAB", "WNBA", "Soccer", "PPV", "Events"]
    
    # Debug: Print the group and title being checked
    is_sport_group = group in sports_groups
    print(f"\n🔍 Checking if event is a sport: Group='{group}', Title='{title}'")
    print(f"   - Is in sports groups: {is_sport_group}")
    
    if not is_sport_group:
        return False
    
    # Check if title contains a date (common for sports events)
    import re
    date_patterns = [
        (r'\((\d{4}-\d{2}-\d{2})\)', '%Y-%m-%d'),  # (2023-09-16)
        (r'(\d{1,2})/(\d{1,2})/(\d{2,4})', None),     # 9/16/23 or 09/16/2023
        (r'(\d{1,2})-(\d{1,2})-(\d{2,4})', None)      # 9-16-23 or 09-16-2023
    ]
    
    for pattern, date_format in date_patterns:
        match = re.search(pattern, title)
        if match:
            print(f"   - Found date pattern: {pattern} in title")
            return True
    
    print(f"   - No date pattern found in title")
    return False

def is_event_over(event_title):
    """Check if an event has already occurred based on its title."""
    import re
    from datetime import datetime, timedelta
    
    print(f"\n📅 Checking if event is over: '{event_title}'")
    
    # Look for date patterns in the title
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', event_title) or \
                 re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', event_title)
    
    if date_match:
        try:
            if len(date_match.groups()) == 1:  # YYYY-MM-DD format
                event_date = datetime.strptime(date_match.group(1), '%Y-%m-%d').date()
                print(f"   - Found YYYY-MM-DD date: {event_date}")
            else:  # MM/DD/YY or MM-DD-YYYY format
                month, day, year = date_match.groups()
                year = int(year) if len(year) == 4 else int(f'20{year}' if int(year) < 50 else f'19{year}')
                event_date = datetime(year, int(month), int(day)).date()
                print(f"   - Found MM/DD/YYYY date: {event_date}")
            
            today = datetime.now().date()
            is_over = event_date < (today - timedelta(days=1))
            
            print(f"   - Today's date: {today}")
            print(f"   - Is event over? {is_over} (event date: {event_date})")
            
            return is_over
            
        except (ValueError, IndexError) as e:
            print(f"   - Error parsing date: {e}")
            return False
    
    print("   - No recognizable date found in title")
    return False

def append_new_streams(lines, new_urls_with_groups):
    lines = [line for line in lines if line.strip() != "#EXTM3U"]
    existing = {}
    i = 0
    
    # First pass: identify all existing entries and mark sports events for removal
    to_remove = set()
    while i < len(lines):
        if lines[i].startswith("#EXTINF:-1"):
            group = None
            title = lines[i].split(",")[-1].strip()
            if 'group-title="' in lines[i]:
                group = lines[i].split('group-title="')[1].split('"')[0]
            
            if group and title and is_sporting_event(group, title) and is_event_over(title):
                print(f"🗑️ Removing expired event: {title}")
                # Mark both the #EXTINF line and the URL line for removal
                to_remove.add(i)
                if i + 1 < len(lines) and not lines[i+1].startswith('#'):
                    to_remove.add(i + 1)
            
            if group:
                existing[(group, title)] = i + 1  # Store index of URL line
        i += 1
    
    # Remove expired events
    if to_remove:
        lines = [line for i, line in enumerate(lines) if i not in to_remove]
        # Rebuild existing dict with updated indices
        existing = {}
        for i, line in enumerate(lines):
            if line.startswith("#EXTINF:-1"):
                group = None
                title = line.split(",")[-1].strip()
                if 'group-title="' in line:
                    group = line.split('group-title="')[1].split('"')[0]
                if group and i + 1 < len(lines):
                    existing[(group, title)] = i + 1
    
    # Add/update new streams
    for url, group, title in new_urls_with_groups:
        key = (group, title)
        if key in existing:
            if lines[existing[key]] != url:
                lines[existing[key]] = url
        else:
            if group == "MLB":
                lines.append(f'#EXTINF:-1 tvg-id="MLB.Baseball.Dummy.us" tvg-name="{title}" tvg-logo="http://drewlive24.duckdns.org:9000/Logos/Baseball-2.png" group-title="MLB",{title}')
            else:
                lines.append(f'#EXTINF:-1 group-title="{group}",{title}')
            lines.append(url)
    
    # Ensure we have a valid M3U file
    lines = [line for line in lines if line.strip()]
    lines.insert(0, "#EXTM3U")
    return lines

async def main():
    if not Path(M3U8_FILE).exists():
        print(f"❌ File not found: {M3U8_FILE}")
        return

    print("📂 Loading existing M3U file...")
    with open(M3U8_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    print(f"   - Loaded {len(lines)} lines from {M3U8_FILE}")

    print("\n🔧 Replacing only /tv stream URLs...")
    tv_new_urls = await scrape_tv_urls()
    if not tv_new_urls:
        print("❌ No TV URLs scraped.")
        return
    print(f"   - Found {len(tv_new_urls)} TV URLs")

    updated_lines = replace_urls_in_tv_section(lines, tv_new_urls)

    print("\n📦 Scraping all other sections (NBA, NFL, Events, etc)...")
    append_new_urls = await scrape_all_append_sections()
    print(f"   - Found {len(append_new_urls)} new streams to add/update")
    
    if append_new_urls:
        print("\n🧹 Processing sports events cleanup...")
        updated_lines = append_new_streams(updated_lines, append_new_urls)

    # Count how many lines we're writing back
    print(f"\n📊 Stats:")
    print(f"   - Original lines: {len(lines)}")
    print(f"   - Updated lines: {len(updated_lines)}")
    print(f"   - Lines removed: {len(lines) - len(updated_lines) + len(tv_new_urls) * 2}")

    # Write the updated content back to the file
    with open(M3U8_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(updated_lines))

    print(f"\n✅ {M3U8_FILE} updated: Clean top, no dups, proper logo/ID for MLB.")

if __name__ == "__main__":
    asyncio.run(main())
