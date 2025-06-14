import json
import os
import subprocess
import tempfile
import requests
from bs4 import BeautifulSoup

def get_goodreads_books(user_id):
    """Scrape Goodreads data for the given user_id and return books as a list of dicts. Returns an empty list if user_id is empty or scraping fails."""
    if not user_id:
        return []
    output_dir = tempfile.mkdtemp(prefix="goodreads_")
    try:
        # Run the goodreads-user-scraper CLI tool
        result = subprocess.run([
            "goodreads-user-scraper",
            "--user_id", str(user_id),
            "--output_dir", output_dir
        ], capture_output=True, text=True, timeout=900)
        if result.returncode != 0:
            print("[WARNING] Goodreads scraper failed:", result.stderr)
            return []
        books_path = os.path.join(output_dir, "books.json")
        if os.path.exists(books_path):
            with open(books_path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"[WARNING] Error scraping Goodreads: {e}")
    # Always return an empty list on error, but do not raise
    return []

def scrape_goodreads_books(user_id, shelf="read"):
    """
    Scrape all books from the user's Goodreads shelf (default: 'read') and return a list of books.
    Each book is a dict with 'title', 'author', 'book_url', 'rating', and 'review'.
    Handles pagination to fetch all books.
    Compatible with Goodreads HTML as of 2025.
    """
    books = []
    page = 1
    per_page = 100
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    while True:
        base_url = f"https://www.goodreads.com/review/list/{user_id}?shelf={shelf}&per_page={per_page}&page={page}"
        try:
            resp = requests.get(base_url, headers=headers, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table", {"id": "books"})
            if not table:
                print(f"[WARNING] Could not find books table on Goodreads shelf page (page {page}). Printing HTML snippet for debugging:")
                print(resp.text[:1000])
                break
            rows = table.find_all("tr", {"id": lambda x: x and x.startswith("review_")})
            if not rows:
                break
            for row in rows:
                # Title
                title = None
                book_url = None
                title_cell = row.find("td", {"class": "field title"})
                if title_cell:
                    value_div = title_cell.find("div", {"class": "value"})
                    if value_div:
                        link = value_div.find("a")
                        if link:
                            title = link.get_text(strip=True)
                            if link.has_attr("href"):
                                book_url = "https://www.goodreads.com" + link["href"]
                # Author
                author = None
                author_cell = row.find("td", {"class": "field author"})
                if author_cell:
                    value_div = author_cell.find("div", {"class": "value"})
                    if value_div:
                        author_link = value_div.find("a")
                        if author_link:
                            author = author_link.get_text(strip=True)
                # Rating
                rating = None
                stars_div = row.find("div", {"class": "stars"})
                if stars_div and stars_div.has_attr("data-rating"):
                    try:
                        rating = int(stars_div["data-rating"])
                    except Exception:
                        rating = None
                # Review
                review = None
                review_cell = row.find("td", {"class": "field review"})
                if review_cell:
                    value_div = review_cell.find("div", {"class": "value"})
                    if value_div:
                        review_text = value_div.get_text(strip=True)
                        if review_text:
                            review = review_text
                if title and author:
                    books.append({
                        "title": title,
                        "author": author,
                        "book_url": book_url,
                        "rating": rating,
                        "review": review
                    })
            # If less than per_page books found, this is the last page
            if len(rows) < per_page:
                break
            page += 1
        except Exception as e:
            print(f"[WARNING] Error scraping Goodreads shelf page {page}: {e}")
            break
    return books
