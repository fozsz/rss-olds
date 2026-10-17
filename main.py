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

  # 4. 記事リンクの抽出
  news_links = soup.find_all("a", href=True)
  added_urls = set()

  for a in news_links:
    href = a["href"]

    # OLDSの記事ページリンクを判定
    if "olds.jp" in href and href not in added_urls:
      title = a.get_text(strip=True)

      # 不要なリンク文字やトップページへのリンクは除外
      if not title or title in ["続きを読む...", "続きを読む", "過去の記事 »"]:
        continue

      full_url = urljoin(target_url, href)
      if full_url in ["https://olds.jp/", "https://olds.jp/info/"]:
        continue

      added_urls.add(href)

      # 親要素から日付等のテキストがあれば取得
      parent_text = a.parent.get_text(strip=True) if a.parent else ""

      # RSSエントリーの追加
      fe = fg.add_entry()
      fe.title(title)
      fe.link(href=full_url)
      fe.guid(full_url, permalink=True)
      if parent_text and parent_text != title:
        fe.description(parent_text)

  # 5. olds.xml ファイルとして保存
  fg.rss_file("olds.xml")
  print("olds.xml の作成が完了しました。")


if __name__ == "__main__":
  main()
