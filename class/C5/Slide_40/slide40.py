"""
Slide 40 - Chapter 5: Đánh giá độ tương đồng giữa các bài báo VnExpress.

Mỗi lần chạy:
  1. Đọc RSS 3 chuyên mục, lấy 2 bài mới nhất mỗi chuyên mục (dữ liệu realtime).
  2. Crawl nội dung, lưu News11.txt, News12.txt, ..., News32.txt.
  3. Tiền xử lý (lowercase, bỏ ký tự đặc biệt, tách từ pyvi, bỏ stopwords).
  4. Vector hoá TF-IDF (hoặc BOW), tính ma trận Cosine.
  5. In các cặp tin tức theo độ tương đồng giảm dần.

Chạy: python slide40.py [--method tfidf|bow]
"""

import argparse
import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from itertools import combinations

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pyvi import ViTokenizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STOPWORDS_FILE = os.path.join(BASE_DIR, "vietnamese-stopwords.txt")

RSS_FEEDS = {
    1: ("Thể thao", "https://vnexpress.net/rss/the-thao.rss"),
    2: ("Sức khỏe", "https://vnexpress.net/rss/suc-khoe.rss"),
    3: ("Kinh doanh", "https://vnexpress.net/rss/kinh-doanh.rss"),
}
ARTICLES_PER_FEED = 2
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"}


# ---------------------------------------------------------------- Crawl
def get(url, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return resp.text
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise
            print(f"   ! Lỗi {e}, thử lại...")
            time.sleep(2)


def fetch_rss(url):
    """Trả về danh sách bài (title, link, pubDate) sắp xếp mới nhất trước."""
    root = ET.fromstring(get(url).encode("utf-8"))
    items = []
    for item in root.iter("item"):
        items.append({
            "title": item.findtext("title", "").strip(),
            "link": item.findtext("link", "").strip(),
            "pub_date": parsedate_to_datetime(item.findtext("pubDate").strip()),
        })
    return sorted(items, key=lambda x: x["pub_date"], reverse=True)


def crawl_article(url):
    """Lấy tiêu đề + sapo + thân bài. Trả về None nếu không phải bài văn bản."""
    soup = BeautifulSoup(get(url), "html.parser")
    body = soup.select_one("article.fck_detail")
    if body is None:
        return None
    # Bỏ đoạn căn phải (tên tác giả) và chú thích ảnh
    paragraphs = [p.get_text(" ", strip=True) for p in body.select("p.Normal")
                  if "text-align:right" not in (p.get("style") or "").replace(" ", "")]
    paragraphs = [p for p in paragraphs if p]
    if not paragraphs:
        return None
    title = soup.select_one("h1.title-detail")
    desc = soup.select_one("p.description")
    parts = [title.get_text(strip=True) if title else "",
             desc.get_text(" ", strip=True) if desc else ""] + paragraphs
    return "\n".join(x for x in parts if x)


def crawl_all():
    os.makedirs(DATA_DIR, exist_ok=True)
    docs = []
    for i, (cat, rss_url) in RSS_FEEDS.items():
        print(f"\n[News{i}] {cat}: {rss_url}")
        j = 0
        for item in fetch_rss(rss_url):
            if j == ARTICLES_PER_FEED:
                break
            text = crawl_article(item["link"])
            if text is None:  # bài video / ảnh, lấy bài kế tiếp
                print(f"   - Bỏ qua (không có nội dung văn bản): {item['title']}")
                continue
            j += 1
            name = f"News{i}{j}"
            with open(os.path.join(DATA_DIR, name + ".txt"), "w", encoding="utf-8") as f:
                f.write(text)
            print(f"   + {name}.txt | {item['pub_date']:%d/%m/%Y %H:%M} | {item['title']}")
            docs.append({"name": name, "category": cat, "title": item["title"], "text": text})
    return docs


# ------------------------------------------------------- Tiền xử lý
def load_stopwords():
    with open(STOPWORDS_FILE, encoding="utf-8") as f:
        # pyvi nối từ ghép bằng "_" nên chuẩn hoá stopwords theo cùng dạng
        return {line.strip().lower().replace(" ", "_") for line in f if line.strip()}


def preprocess(text, stopwords):
    text = text.lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^\w\s]|\d|_", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokens = ViTokenizer.tokenize(text).split()
    return " ".join(t for t in tokens if t not in stopwords and len(t) > 1)


# --------------------------------------------------- Độ tương đồng
def similarity(docs, method):
    stopwords = load_stopwords()
    corpus = [preprocess(d["text"], stopwords) for d in docs]
    vectorizer = TfidfVectorizer() if method == "tfidf" else CountVectorizer()
    vectors = vectorizer.fit_transform(corpus)
    names = [d["name"] for d in docs]
    return pd.DataFrame(cosine_similarity(vectors), index=names, columns=names)


def rank_pairs(docs, sim):
    rows = []
    for a, b in combinations(range(len(docs)), 2):
        da, db = docs[a], docs[b]
        rows.append({
            "Cặp": f"{da['name']} - {db['name']}",
            "Cosine": sim.iloc[a, b],
            "Quan hệ": "Cùng chuyên mục" if da["category"] == db["category"] else "Khác chuyên mục",
        })
    df = pd.DataFrame(rows).sort_values("Cosine", ascending=False).reset_index(drop=True)
    df.index += 1
    return df


def main(method="tfidf"):
    print(f"=== Crawl dữ liệu realtime lúc {datetime.now():%d/%m/%Y %H:%M:%S} ===")
    docs = crawl_all()

    pd.set_option("display.width", 200)
    sim = similarity(docs, method)
    print(f"\n=== Ma trận độ tương đồng Cosine ({method.upper()}) ===")
    print(sim.round(6))

    print("\n=== Các cặp tin tức theo độ tương đồng giảm dần ===")
    print(rank_pairs(docs, sim).to_string(formatters={"Cosine": "{:.6f}".format}))

    print("\n=== Danh sách bài ===")
    for d in docs:
        print(f"{d['name']} [{d['category']}]: {d['title']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=["tfidf", "bow"], default="tfidf")
    main(parser.parse_args().method)
