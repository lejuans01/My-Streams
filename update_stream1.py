import requests
import os
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
            
        # Add timestamp and proper M3U header
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        m3u_content = f"#EXTM3U\n# Last Updated: {timestamp}\n{content}"
        
        # Write the updated M3U file
        with open("strem1.m3u", "w", encoding='utf-8') as f:
            f.write(m3u_content)
            
        print("Successfully updated strem1.m3u playlist")
        return True
        
    except Exception as e:
        print(f"Error updating M3U playlist: {str(e)}")
        return False

if __name__ == "__main__":
    update_playlist()
