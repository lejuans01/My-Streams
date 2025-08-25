import requests
import os
import re
from datetime import datetime

def update_playlist():
    # Get M3U URL from environment variable
    m3u_url = os.getenv('M3U_SOURCE_URL')
    if not m3u_url:
        raise ValueError("M3U_SOURCE_URL environment variable not set")
    
    try:
        # Fetch the M3U content
        response = requests.get(m3u_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Get the content and remove the original #EXTM3U header if it exists
        content = response.text
        if content.startswith("#EXTM3U"):
            content = content[content.find('\n') + 1:]
            
        # Add M3U header with EPG URL
        m3u_content = "#EXTM3U x-tvg-url=\"https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz\"\n"
        
        # Process each channel to improve matching
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            if lines[i].startswith('#EXTINF'):
                # Extract channel name
                name_match = re.search(r'group-title=".*?",(.*?)$', lines[i])
                if name_match:
                    channel_name = name_match.group(1).strip()
                    # Add tvg-name attribute for better EPG matching
                    if 'tvg-name=' not in lines[i]:
                        # Clean up channel name for better matching
                        clean_name = re.sub(r'[^a-zA-Z0-9]', '', channel_name.split('(')[0].strip().lower())
                        lines[i] = lines[i].replace('#EXTINF', f'#EXTINF tvg-name="{clean_name}"', 1)
                i += 1  # Move to URL line
            i += 1
            
        # Rebuild content with processed lines
        m3u_content += '\n'.join(lines)
        
        # Write the updated M3U file
        output_filename = "stream1.m3u"
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
        
        print(f"Writing to: {output_path}")
        with open(output_path, "w", encoding='utf-8') as f:
            f.write(m3u_content)
            
        # Verify file was written
        if os.path.exists(output_path):
            print(f"Successfully updated {output_filename} playlist")
            print(f"File size: {os.path.getsize(output_path)} bytes")
        else:
            print(f"Error: Failed to create {output_filename}")
            
        return True
        
    except Exception as e:
        print(f"Error updating M3U playlist: {str(e)}")
        return False

if __name__ == "__main__":
    update_playlist()
