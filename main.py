# --- 必要なライブラリの読み込み ---
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import requests


def main():
  # 1. OLDSの更新情報ページ
  target_url = "https://olds.jp/info/"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  # 2. ページHTMLの取得
  response = requests.get(target_url, headers=headers)
  response.encoding = response.apparent_encoding
  soup = BeautifulSoup(response.text, "html.parser")

  # 3. RSSの土台作成
  fg = FeedGenerator()
  fg.title("OLDS 更新情報")
  fg.link(href=target_url, rel="alternate")
  fg.description("OLDS（https://olds.jp/info/）の自動生成RSSフィード")
  fg.language("ja")

  # 4. 記事カード（article要素）のみを順番にチェック
  articles = soup.find_all("article")
  added_urls = set()

  for article in articles:
    # 記事のタイトルリンクを探す（h1, h2, h3 などの見出しタグ内のリンク）
    title_tag = article.find(["h1", "h2", "h3", "h4"])
    link_tag = (
        title_tag.find("a")
        if title_tag
        else article.find("a", href=True)
    )

    if not link_tag or not link_tag.get("href"):
      continue

    href = link_tag["href"]
    full_url = urljoin(target_url, href)

    # 重複防止
    if full_url in added_urls:
      continue

    title = link_tag.get_text(strip=True)

    # 不要なシステム文字やトップページを除外
    if not title or title in [
        "続きを読む...",
        "続きを読む",
        "過去の記事 »",
    ]:
      continue

    added_urls.add(full_url)

    # 記事内の日付（timeタグ）があれば取得
    time_tag = article.find("time")
    date_str = time_tag.get_text(strip=True) if time_tag else ""

    # RSSエントリーの追加
    fe = fg.add_entry()
    # 日付があればタイトルの先頭につける（例: "2026/10/14 Webber Fast..."）
    fe.title(f"{date_str} {title}".strip() if date_str else title)
    fe.link(href=full_url)
    fe.guid(full_url, permalink=True)

  # 5. olds.xml ファイルとして保存
  fg.rss_file("olds.xml")
  print("olds.xml の作成が完了しました。")


if __name__ == "__main__":
  main()
