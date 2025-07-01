import requests
import json

# Configuration
BASE_URL = "https://phcms.hlth.prd.aws.chewy.cloud/wp-json/wp/v2/posts"
PARAMS = {
    "acf_format": "standard",
    "per_page": 100,
    "page": 1
}
HEADERS = {}

def fetch_total_pages():
    """Get the total number of pages available."""
    response = requests.get(BASE_URL, params=PARAMS)
    response.raise_for_status()
    total_pages = int(response.headers.get("X-Wp-TotalPages") or response.headers.get("X-WP-TotalPages"))
    return total_pages

def fetch_all_posts():
    """Fetch all paginated posts and return as a list."""
    all_posts = []
    total_pages = fetch_total_pages()

    for page in range(1, total_pages + 1):
        print(f"Fetching page {page}/{total_pages}")
        PARAMS["page"] = page
        response = requests.get(BASE_URL, params=PARAMS)
        response.raise_for_status()
        all_posts.extend(response.json())

    return all_posts

def save_to_file(data, filename="data/all_wp_posts.json"):
    """Save the aggregated post data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    posts = fetch_all_posts()
    save_to_file(posts)
    print(f"Saved {len(posts)} posts to data/all_wp_posts.json")

if __name__ == "__main__":
    main()
