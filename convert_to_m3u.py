import requests
import re
from urllib.parse import urlparse

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

def convert_to_m3u(content, output_file):
    lines = content.split('\n')
    current_group = ""
    m3u_lines = ["#EXTM3U x-tvg-url="""]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for group headers (lines ending with ,#genre#)
        if line.endswith(',#genre#'):
            current_group = line.split(',#genre#')[0].strip()
            m3u_lines.append(f"#EXTINF:-1 group-title=\"{current_group}\",{current_group}")
        # Check for channel entries (format: name,url)
        elif ',' in line and is_valid_url(line.split(',')[-1]):
            parts = line.rsplit(',', 1)
            if len(parts) == 2 and is_valid_url(parts[1]):
                name, url = parts
                m3u_lines.append(f"#EXTINF:-1 group-title=\"{current_group}\",{name}")
                m3u_lines.append(url)
    
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
        print("Converting to M3U format...")
        convert_to_m3u(content, output_file)
    else:
        print("Failed to fetch content. Please check the URL and try again.")

if __name__ == "__main__":
    main()
