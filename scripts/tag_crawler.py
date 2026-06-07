import argparse
from pathlib import Path
import sys

import requests
from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config import TAG_LIST_FILE, TAGS_DATA_DIR

# Configuration
URL = "https://dev.to/tags"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TAGS_DATA_DIR.mkdir(parents=True, exist_ok=True)


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch available tags from Dev.to.")
    parser.add_argument(
        "--output",
        type=Path,
        default=TAG_LIST_FILE,
        help="Path to write the tag list.",
    )
    return parser.parse_args()


def crawl_tags(output_file=TAG_LIST_FILE):
    print(f"Connecting to {URL}...")
    
    try:
        response = requests.get(URL, headers=HEADERS)
        response.raise_for_status()
    except Exception as e:
        print(f"Connection error: {e}")
        return

    print("Parsing HTML content...")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    found_tags = set() # Use a set to avoid duplicates

    # Logic: Find all <a> tags where href starts with '/t/' and text starts with '#'
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link['href']
        text = link.get_text().strip()
        
        if href.startswith('/t/') and text.startswith('#'):
            # Remove the '#' character and extra whitespace
            clean_tag = text.replace('#', '').strip()
            
            # Basic validation to ensure it is not empty
            if clean_tag:
                found_tags.add(clean_tag)

    # Sort tags alphabetically
    sorted_tags = sorted(list(found_tags))
    
    # Save to file
    if sorted_tags:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for tag in sorted_tags:
                f.write(f"{tag}\n")
        
        print(f"Success! Saved {len(sorted_tags)} tags to '{output_file}'.")
    else:
        print("No tags found. The website structure might have changed.")

if __name__ == "__main__":
    args = parse_args()
    crawl_tags(output_file=args.output)
