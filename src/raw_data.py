import requests
import json
from markdownify import markdownify as md
import datetime
import time

from src.config import RAW_DATA_DIR, RAW_DATA_FILE

DEV_TO_API = "https://dev.to/api/articles"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

def convert_to_markdown(html_content):
    if not html_content:
        return ""
    markdown_content = md(html=html_content, heading_style='ATX')
    return markdown_content

def fetch_single_post(id):
    if not id:
        print('Error: Invalid article ID')
        return None
    
    url = f"{DEV_TO_API}/{id}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f'Error: Received status code {response.status_code} for article {id}')
            return None
        
        article = response.json()
        
        if not article or not isinstance(article, dict):
            print(f'Error: Invalid article data for article {id}')
            return None
        
        html_content = article.get('body_html', '')
        if not html_content:
            print(f'Warning: No HTML content for article {id}')
        
        markdown = convert_to_markdown(html_content)

        # Remove '\n'
        markdown = "\n".join([line for line in markdown.splitlines() if line.strip()])

        doc = {
            "id": id,
            "metadata": {
                "source": "dev.to",
                "type_of": article.get('type_of', 'article'),
                "title": article.get('title', 'Untitled'),
                "description": article.get('description', ''),
                "author": {
                    "name": article.get('user', {}).get('name', 'Unknown') if article.get('user') else 'Unknown',
                    "username": article.get('user', {}).get('username', 'unknown') if article.get('user') else 'unknown'
                },
                "url": article.get('url', ''),
                "published_time": article.get('published_timestamp', ''),
                "reading_time": article.get('reading_time_minutes', 0),
                "language": article.get('language', ''),
                "tags": article.get('tags', []) if isinstance(article.get('tags'), list) else [],
                "reactions": article.get('public_reactions_count', 0),
            },
            "content": {
                "html": html_content,
                "markdown": markdown
            },
            "crawled_at": datetime.datetime.now().isoformat()
        }
        return doc

    except requests.exceptions.RequestException as e:
        print(f'Error: Request failed for article {id}: {e}')
        return None
    except json.JSONDecodeError as e:
        print(f'Error: Failed to parse JSON response for article {id}: {e}')
        return None
    except Exception as e:
        print(f'Unexpected error fetching article {id}: {e}')
        return None

def fetch_data(tag="dataengineering", limit=20):
    if not tag or not isinstance(tag, str):
        print('Error: Invalid tag parameter')
        return
    
    if not isinstance(limit, int) or limit <= 0:
        print('Error: Invalid limit parameter')
        return
    
    params = {
        "tag": tag,
        #"state": "rising",
        "per_page": min(limit, 1000)  # API limit
    }

    try:
        response = requests.get(DEV_TO_API, params=params, timeout=10)
        existing_ids = set()
        current_data = []

        if RAW_DATA_FILE.exists():
            with open(RAW_DATA_FILE, 'r', encoding='utf-8') as file:
                try:
                    current_data = json.load(file)
                    for item in current_data:
                        existing_ids.add(item['id'])
                except json.JSONDecodeError:
                    pass

        if response.status_code != 200:
            print(f'Error: Received status code {response.status_code}')
            return
        
        articles = response.json()
        
        if not articles or not isinstance(articles, list):
            print('Error: No articles found or invalid response format')
            return

        print(f'Found {len(articles)} articles')
        json_list = []
        
        for i, article in enumerate(articles):
            if not article or not isinstance(article, dict):
                print(f'Warning: Skipping invalid article at position {i + 1}')
                continue
            article_id = article.get('id')

            if not article_id:
                print(f'Warning: Skipping article without ID at position {i + 1}')
                continue
            
            print(f'Fetching data of article number {i + 1} (ID: {article_id})...')
            
            if article_id in existing_ids:
                print(f'Article {article_id} already existed, skip')
                continue
            
            json_post = fetch_single_post(article_id)
            if json_post:
                json_list.append(json_post)
            else:
                print(f'Warning: Failed to fetch article {article_id}')
            
            time.sleep(0.5)

        if not json_list:
            print('Warning: No articles were successfully fetched')
            return

        print(f'Fetching done, writing {len(json_list)} articles to json...')
        
        with open(RAW_DATA_FILE, 'w', encoding='utf-8') as file:
            json.dump(json_list, file, ensure_ascii=False, indent=2)
        print(f'Successfully wrote data to {RAW_DATA_FILE}')

    except requests.exceptions.RequestException as e:
        print(f'Request error: {e}')
    except json.JSONDecodeError as e:
        print(f'Error: Failed to parse JSON response: {e}')
    except IOError as e:
        print(f'Error: Failed to write to file {RAW_DATA_FILE}: {e}')
    except Exception as e:
        print(f'Unexpected error: {e}')

if __name__ == "__main__":
    fetch_data(tag="ai")
