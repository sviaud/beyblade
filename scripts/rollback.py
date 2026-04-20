#!/usr/bin/env python3
"""Rollback d'une run de mise à jour.

Usage: python3 scripts/rollback.py backups/YYYY-MM-DD-HHMMSS
Restaure le contenu, le titre et le status de tous les posts d'un backup.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wp_client import WPClient


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/rollback.py <backup_dir>")
        print("Example: python3 scripts/rollback.py backups/2026-04-09-155537")
        sys.exit(1)

    backup_dir = sys.argv[1]
    if not os.path.isabs(backup_dir):
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', backup_dir)

    posts_dir = os.path.join(backup_dir, 'posts')
    if not os.path.isdir(posts_dir):
        print(f"ERROR: {posts_dir} doesn't exist")
        sys.exit(1)

    client = WPClient.from_env(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.env'))

    files = sorted(os.listdir(posts_dir))
    json_files = [f for f in files if f.endswith('.json')]
    print(f"Rolling back {len(json_files)} posts from {backup_dir}")

    confirm = input("⚠️  This will overwrite current content on WordPress. Type 'ROLLBACK' to confirm: ")
    if confirm != 'ROLLBACK':
        print("Aborted.")
        sys.exit(0)

    success = 0
    failed = 0

    for fname in json_files:
        path = os.path.join(posts_dir, fname)
        with open(path, encoding='utf-8') as f:
            post = json.load(f)
        pid = post['id']
        title = post['title'].get('raw') or post['title'].get('rendered', '')
        try:
            client.update_post(pid, {
                'content': post['content']['raw'],
                'title': post['title']['raw'],
                'status': post['status'],
            })
            print(f"  ✅ [{pid}] {title[:60]}")
            success += 1
            time.sleep(1)
        except Exception as e:
            print(f"  ❌ [{pid}] {title[:60]} — {e}")
            failed += 1

    print(f"\nDone: {success} succeeded, {failed} failed")


if __name__ == '__main__':
    main()
