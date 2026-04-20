#!/usr/bin/env python3
"""Mode batch : traite tous les articles hors pilotes, applique en DRAFT.

Usage: python3 scripts/03_batch.py [--dry-run] [--skip-pilots]
"""
import datetime
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wp_client import WPClient
from product_data import ProductDatabase
from amazon_link import build_search_url, build_cta_html
from content_generator import generate_article_html
from image_handler import extract_first_image
from rating_box import build_review_block


PILOT_IDS = {9, 8566}
AMAZON_TAG = "pistol-21"
SKIP_DEFAULT = True  # Par défaut on skip les pilotes (déjà traités)


def make_backup_dir():
    ts = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H%M%S')
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backups', ts)
    os.makedirs(os.path.join(root, 'posts'), exist_ok=True)
    return root, ts


def backup_post(backup_dir, post):
    path = os.path.join(backup_dir, 'posts', f"{post['id']}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(post, f, ensure_ascii=False, indent=2)


def validate_new_content(html_content, min_words=750):
    text = re.sub(r'<[^>]+>', ' ', html_content)
    word_count = len(text.split())
    checks = {
        'word_count': word_count,
        'word_count_ok': word_count >= min_words,
        'has_h2': '<h2>' in html_content,
        'has_table': '<table>' in html_content,
        'has_amazon_link': bool(re.search(r'amazon\.fr/s\?k=.*?tag=' + AMAZON_TAG, html_content)),
        'has_faq': 'FAQ' in html_content,
    }
    checks['all_ok'] = all(v for k, v in checks.items() if k not in ('word_count',))
    return checks


def build_faqs(product):
    name = product['name']
    default_faqs = ProductDatabase.default_faq(name, product.get('age_min', 8), product.get('portee_m'))
    overrides = product.get('faq_overrides', [])
    override_themes = set()
    for f in overrides:
        q_lower = f['q'].lower()
        if 'enfant' in q_lower or 'ans' in q_lower:
            override_themes.add('enfant')
        if 'acheter' in q_lower or 'prix' in q_lower or 'trouver' in q_lower or 'o\u00f9' in q_lower:
            override_themes.add('acheter')
        if 'port\u00e9e' in q_lower or 'distance' in q_lower:
            override_themes.add('portee')
        if 'munition' in q_lower or 'fl\u00e9chette' in q_lower or 'compatible' in q_lower:
            override_themes.add('munitions')

    filtered_defaults = []
    for f in default_faqs:
        q_lower = f['q'].lower()
        skip = False
        if 'enfant' in q_lower and 'enfant' in override_themes:
            skip = True
        if 'acheter' in q_lower and 'acheter' in override_themes:
            skip = True
        if 'port\u00e9e' in q_lower and 'portee' in override_themes:
            skip = True
        if 'munition' in q_lower and 'munitions' in override_themes:
            skip = True
        if not skip:
            filtered_defaults.append(f)

    return (overrides + filtered_defaults)[:8]


def main():
    dry_run = '--dry-run' in sys.argv
    base_dir = os.path.dirname(os.path.abspath(__file__))
    client = WPClient.from_env(os.path.join(base_dir, '..', 'config.env'))
    db = ProductDatabase(os.path.join(base_dir, '..', 'data', 'nerf-products.json'))

    audit_path = os.path.join(base_dir, '..', 'data', 'posts-to-update.json')
    with open(audit_path) as f:
        audit = json.load(f)

    ids_to_process = [a['id'] for a in audit['posts'] if a['id'] not in PILOT_IDS]
    print(f"Total articles to process: {len(ids_to_process)}")
    print(f"Pilots skipped: {sorted(PILOT_IDS)}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE (PUBLISH)'}")

    backup_dir, run_id = make_backup_dir()
    print(f"Backup dir: {backup_dir}")

    log_entries = []
    manifest = {'run_id': run_id, 'mode': 'batch', 'posts': []}

    success_count = 0
    fail_count = 0
    skip_count = 0
    processed = 0

    for pid in ids_to_process:
        processed += 1
        print(f"\n[{processed}/{len(ids_to_process)}] POST {pid}", end='')

        try:
            post = client.get_post(pid)
        except Exception as e:
            print(f"  ❌ Fetch failed: {e}")
            fail_count += 1
            log_entries.append({'id': pid, 'status': 'fetch_failed', 'error': str(e)})
            continue

        backup_post(backup_dir, post)
        manifest['posts'].append({'id': pid, 'title': post['title'].get('raw', '')})

        if not db.has(pid):
            print(f"  ⚠️ No product data, skipping")
            skip_count += 1
            log_entries.append({'id': pid, 'status': 'no_data'})
            continue

        product = db.get(pid)
        name = product['name']
        print(f"  {name[:60]}", end='')

        amazon_url = build_search_url(name, AMAZON_TAG)
        amazon_cta = build_cta_html(name, AMAZON_TAG)

        image = extract_first_image(post['content'].get('raw', ''))
        fallback_img = image  # single image dict {'src':...} or None
        review_block = build_review_block(product, [], amazon_url, fallback_image=fallback_img)

        faqs = build_faqs(product)
        new_html = generate_article_html(
            product=product,
            image_html='',
            amazon_cta=amazon_cta,
            faqs=faqs,
            review_block=review_block,
        )

        checks = validate_new_content(new_html)
        if not checks['all_ok']:
            print(f"  ❌ Validation failed (wc={checks['word_count']})")
            fail_count += 1
            log_entries.append({'id': pid, 'status': 'validation_failed', 'checks': checks})
            continue

        old_wc = len(re.sub(r'<[^>]+>', ' ', post['content'].get('raw', '')).split())

        if dry_run:
            print(f"  [DRY] wc={checks['word_count']} (was {old_wc})")
        else:
            try:
                # Mise à jour + passage en publish
                client.update_post(pid, {
                    'content': new_html,
                    'status': 'publish',
                })
                print(f"  ✅ publish wc={checks['word_count']} (was {old_wc})")
                success_count += 1
                log_entries.append({
                    'id': pid,
                    'title': name,
                    'status': 'success',
                    'old_word_count': old_wc,
                    'new_word_count': checks['word_count'],
                    'amazon_link': amazon_url,
                    'image_processed': bool(image),
                    'faq_count': len(faqs),
                    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
                })
            except Exception as e:
                print(f"  ❌ Update failed: {e}")
                fail_count += 1
                log_entries.append({'id': pid, 'status': 'update_failed', 'error': str(e)})
                continue

        # Rate limiting
        time.sleep(1)
        if processed % 10 == 0:
            print("  [pause 5s]")
            time.sleep(5)

    # Manifest + log
    with open(os.path.join(backup_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    log_path = os.path.join(base_dir, '..', 'updates-log.json')
    existing = {'runs': []}
    if os.path.exists(log_path):
        with open(log_path) as f:
            existing = json.load(f)
    existing['runs'].append({
        'run_id': run_id,
        'mode': 'batch',
        'summary': {
            'total': len(ids_to_process),
            'success': success_count,
            'failed': fail_count,
            'skipped': skip_count,
        },
        'entries': log_entries,
    })
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"\n\n=== BATCH COMPLETE ===")
    print(f"  Total processed: {processed}")
    print(f"  ✅ Success: {success_count}")
    print(f"  ❌ Failed:  {fail_count}")
    print(f"  ⚠️  Skipped: {skip_count}")
    print(f"  Backup: {backup_dir}")


if __name__ == '__main__':
    main()
