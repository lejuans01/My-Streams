import requests
import re
import concurrent.futures
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def fetch_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching content: {e}")
        return None

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def check_stream(url, timeout=5):
    """Check if a stream URL is accessible."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # For m3u8 and m3u playlists
        if url.endswith(('.m3u8', '.m3u')):
            response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
            if response.status_code == 200:
                return True, url
        # For direct video streams
        else:
            # Try a small range request to check if the stream is accessible
            headers['Range'] = 'bytes=0-1'
            response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
            if response.status_code in (200, 206):
                return True, url
            # If HEAD is not allowed, try GET with a small timeout
            response = requests.get(url, headers=headers, timeout=timeout, stream=True)
            if response.status_code == 200:
                response.close()
                return True, url
    except (requests.RequestException, Exception) as e:
        pass
    return False, url

def convert_to_m3u(content, output_file, max_workers=10):
    lines = content.split('\n')
    current_group = ""
    m3u_lines = ["#EXTM3U x-tvg-url=\"\""]
    entries = []
    
    # First, parse all entries
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.endswith(',#genre#'):
            current_group = line.split(',#genre#')[0].strip()
            entries.append(('group', current_group, None))
        elif ',' in line and is_valid_url(line.split(',')[-1]):
            parts = line.rsplit(',', 1)
            if len(parts) == 2 and is_valid_url(parts[1]):
                name, url = parts
                entries.append(('stream', name.strip(), url.strip(), current_group))
    
    # Process streams in parallel
    valid_streams = []
    stream_entries = [e for e in entries if e[0] == 'stream']
    
    print(f"Checking {len(stream_entries)} streams for availability...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_entry = {
            executor.submit(check_stream, entry[2]): entry 
            for entry in stream_entries
        }
        
        for future in concurrent.futures.as_completed(future_to_entry):
            entry = future_to_entry[future]
            try:
                is_valid, url = future.result()
                if is_valid:
                    valid_streams.append((entry[1], url, entry[3]))
                    print(f"✓ {entry[1]}")
                else:
                    print(f"✗ {entry[1]} (unreachable)")
            except Exception as e:
                print(f"✗ {entry[1]} (error: {str(e)})")
    
    # Build the final M3U file
    current_group = ""
    for entry in entries:
        if entry[0] == 'group':
            current_group = entry[1]
            m3u_lines.append(f"#EXTINF:-1 group-title=\"{current_group}\",{current_group}")
        else:
            # Only add stream if it's in the valid_streams list
            stream_match = next(
                (s for s in valid_streams if s[0] == entry[1] and s[2] == current_group and s[1] == entry[2]),
                None
            )
            if stream_match:
                m3u_lines.append(f"#EXTINF:-1 group-title=\"{current_group}\",{entry[1]}")
                m3u_lines.append(stream_match[1])
    
    print(f"\nFound {len(valid_streams)}/{len(stream_entries)} working streams")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u_lines))
    
    print(f"Successfully converted to {output_file}")

def main():
    url = "https://raw.githubusercontent.com/jack2713/my/refs/heads/main/my02.txt"
    output_file = "playlist.m3u"
    
    print(f"Fetching content from {url}...")
    content = fetch_content(url)
    
    if content:
        print("Converting to M3U format and checking stream availability...")
        start_time = time.time()
        convert_to_m3u(content, output_file)
        end_time = time.time()
        print(f"\nProcessing completed in {end_time - start_time:.2f} seconds")
    else:
        print("Failed to fetch content. Please check the URL and try again.")

if __name__ == "__main__":
    main()
