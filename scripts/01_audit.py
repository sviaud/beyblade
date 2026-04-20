#!/usr/bin/env python3
"""Audit de tous les posts WordPress.

Produit data/posts-to-update.json avec la liste des articles à traiter.
"""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wp_client import WPClient


SHORTCODE_PATTERN = re.compile(r'\[amazon[^\]]*\]')
EDITORIAL_IDS = {1517, 1514, 1482}  # articles à ne pas toucher


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    client = WPClient.from_env(os.path.join(base, '..', 'config.env'))
    print("Fetching all posts...")
    posts = client.get_all_posts(per_page=100, context='edit')
    print(f"Fetched {len(posts)} posts")

    to_update = []
    skipped = []

    for p in posts:
        pid = p['id']
        title_raw = p['title'].get('raw') or p['title'].get('rendered', '')
        content_raw = p['content'].get('raw', '')

        if pid in EDITORIAL_IDS:
            skipped.append({'id': pid, 'title': title_raw, 'reason': 'editorial'})
            continue

        shortcodes = SHORTCODE_PATTERN.findall(content_raw)
        to_update.append({
            'id': pid,
            'title': title_raw,
            'slug': p['slug'],
            'link': p.get('link', ''),
            'categories': p['categories'],
            'featured_media': p.get('featured_media', 0),
            'word_count_before': len(re.sub(r'<[^>]+>', ' ', content_raw).split()),
            'has_shortcode': bool(shortcodes),
            'shortcodes': shortcodes,
        })

    output = {
        'generated_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'total_posts': len(posts),
        'to_update': len(to_update),
        'skipped': skipped,
        'posts': to_update,
    }

    out_path = os.path.join(base, '..', 'data', 'posts-to-update.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Audit complete")
    print(f"  To update: {len(to_update)}")
    print(f"  Skipped (editorial): {len(skipped)}")
    print(f"  Saved to: {out_path}")


if __name__ == '__main__':
    main()
