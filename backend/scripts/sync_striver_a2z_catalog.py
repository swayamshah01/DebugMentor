"""
Fetch the public Striver A2Z sheet catalog from takeUforward and write a local JSON manifest.

Run:
    cd backend
    python scripts/sync_striver_a2z_catalog.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import requests


SOURCE_URL = "https://takeuforward.org/dsa/strivers-a2z-sheet-learn-dsa-a-to-z"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "content" / "striver_a2z_catalog.json"


def extract_sheet_catalog(html: str) -> list[dict]:
    marker = 'subcategory_name\\":\\"'
    index = 0
    current_section = None
    rows: list[dict] = []

    while True:
        section_pos = html.find(marker, index)
        if section_pos == -1:
            break

        name_start = section_pos + len(marker)
        name_end = html.find('\\"', name_start)
        if name_end == -1:
            break

        current_section = html[name_start:name_end]
        problems_anchor = html.find('problems\\":[', name_end)
        if problems_anchor == -1:
            index = name_end
            continue

        next_section = html.find(marker, problems_anchor)
        chunk = html[problems_anchor: next_section if next_section != -1 else len(html)]

        for match in re.finditer(
            r'problem_id\\":\\"(?P<problem_id>[^"]+).*?problem_name\\":\\"(?P<problem_name>[^"]+).*?'
            r'article\\":\\"(?P<article>[^"]+).*?youtube\\":\\"(?P<youtube>[^"]*).*?'
            r'leetcode\\":\\"(?P<leetcode>[^"]*).*?difficulty\\":\\"(?P<difficulty>[^"]+)',
            chunk,
        ):
            rows.append({
                "sheet_section": current_section,
                "problem_id": match.group("problem_id"),
                "title": match.group("problem_name"),
                "article_url": match.group("article").replace("\\/", "/"),
                "youtube_url": match.group("youtube").replace("\\/", "/"),
                "leetcode_url": match.group("leetcode").replace("\\/", "/"),
                "difficulty": match.group("difficulty").lower(),
            })

        index = next_section if next_section != -1 else len(html)

    deduped: dict[tuple[str, str], dict] = {}
    for row in rows:
        key = (row["sheet_section"], row["title"])
        deduped[key] = row
    return list(deduped.values())


def main() -> None:
    response = requests.get(SOURCE_URL, timeout=30)
    response.raise_for_status()

    catalog = extract_sheet_catalog(response.text)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps({
        "source_url": SOURCE_URL,
        "problem_count": len(catalog),
        "problems": catalog,
    }, indent=2), encoding="utf-8")

    print(f"Wrote {len(catalog)} catalog entries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
