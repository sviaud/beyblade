#!/usr/bin/env python3
"""Mode pilote : traite 2 articles, applique en production, vérifie.

Usage: python3 scripts/02_pilot.py [--dry-run]
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


PILOT_IDS = [9, 8566]
AMAZON_TAG = "pistol-21"


def make_backup_dir():
    ts = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H%M%S')
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backups', ts)
    os.makedirs(os.path.join(root, 'posts'), exist_ok=True)
    return root, ts


def backup_post(backup_dir, post):
    path = os.path.join(backup_dir, 'posts', f"{post['id']}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(post, f, ensure_ascii=False, indent=2)


def validate_new_content(html_content, min_words=800):
    text = re.sub(r'<[^>]+>', ' ', html_content)
    word_count = len(text.split())
    checks = {
        'word_count': word_count,
        'word_count_ok': word_count >= min_words,
        'has_h2': '<h2>' in html_content,
        'has_table': '<table>' in html_content,
        'has_amazon_link': bool(re.search(r'amazon\.fr/s\?k=.*?tag=pistol-21', html_content)),
        'has_faq': 'FAQ' in html_content,
    }
    checks['all_ok'] = all(v for k, v in checks.items() if k not in ('word_count',))
    return checks


def main():
    dry_run = '--dry-run' in sys.argv
    base_dir = os.path.dirname(os.path.abspath(__file__))
    client = WPClient.from_env(os.path.join(base_dir, '..', 'config.env'))
    db = ProductDatabase(os.path.join(base_dir, '..', 'data', 'nerf-products.json'))

    backup_dir, run_id = make_backup_dir()
    print(f"Backup dir: {backup_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")

    log_entries = []
    manifest = {'run_id': run_id, 'mode': 'pilot', 'posts': []}

    for pid in PILOT_IDS:
        print(f"\n=== Processing post {pid} ===")
        post = client.get_post(pid)
        backup_post(backup_dir, post)
        manifest['posts'].append({'id': pid, 'title': post['title']['raw']})

        if not db.has(pid):
            print(f"  ⚠️  No product data, skipping")
            continue

        product = db.get(pid)
        name = product['name']
        print(f"  Product: {name}")

        amazon_url = build_search_url(name, AMAZON_TAG)
        amazon_cta = build_cta_html(name, AMAZON_TAG)

        image = extract_first_image(post['content']['raw'])
        review_block = build_review_block(product, [], amazon_url, fallback_image=image)
        print(f"  Image: {'found' if image else 'NONE'}")

        default_faqs = ProductDatabase.default_faq(name, product.get('age_min', 8), product.get('portee_m'))
        overrides = product.get('faq_overrides', [])
        # Dédoublonnage thématique : si une override évoque "enfant" ou "acheter", on ignore la default correspondante
        override_themes = set()
        for f in overrides:
            q_lower = f['q'].lower()
            if 'enfant' in q_lower or 'ans' in q_lower:
                override_themes.add('enfant')
            if 'acheter' in q_lower or 'prix' in q_lower or 'trouver' in q_lower:
                override_themes.add('acheter')
            if 'portée' in q_lower or 'distance' in q_lower:
                override_themes.add('portee')
            if 'munition' in q_lower or 'fléchette' in q_lower:
                override_themes.add('munitions')

        filtered_defaults = []
        for f in default_faqs:
            q_lower = f['q'].lower()
            skip = False
            if 'enfant' in q_lower and 'enfant' in override_themes:
                skip = True
            if 'acheter' in q_lower and 'acheter' in override_themes:
                skip = True
            if 'portée' in q_lower and 'portee' in override_themes:
                skip = True
            if 'munition' in q_lower and 'munitions' in override_themes:
                skip = True
            if not skip:
                filtered_defaults.append(f)

        faqs = (overrides + filtered_defaults)[:8]

        new_html = generate_article_html(
            product=product,
            image_html='',
            amazon_cta=amazon_cta,
            faqs=faqs,
            review_block=review_block,
        )

        checks = validate_new_content(new_html)
        print(f"  Word count: {checks['word_count']}")
        print(f"  Checks: word_count_ok={checks['word_count_ok']} h2={checks['has_h2']} table={checks['has_table']} amazon={checks['has_amazon_link']} faq={checks['has_faq']}")

        if not checks['all_ok']:
            print(f"  ❌ Validation failed — skipping")
            log_entries.append({'id': pid, 'status': 'validation_failed', 'checks': checks})
            continue

        old_wc = len(re.sub(r'<[^>]+>', ' ', post['content']['raw']).split())

        if dry_run:
            print(f"  [DRY RUN] Would update post {pid}")
            preview_path = os.path.join(backup_dir, f'{pid}_preview.html')
            with open(preview_path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            print(f"  Preview: {preview_path}")
            status = 'dry_run'
        else:
            print(f"  Updating post {pid}...")
            client.update_post(pid, {'content': new_html})
            time.sleep(2)
            check = client.get_post(pid)
            if AMAZON_TAG in check['content'].get('raw', ''):
                print(f"  ✅ Update verified")
                status = 'success'
            else:
                print(f"  ⚠️  Update applied but verification failed")
                status = 'verification_failed'

        log_entries.append({
            'id': pid,
            'title': name,
            'status': status,
            'old_word_count': old_wc,
            'new_word_count': checks['word_count'],
            'amazon_link': amazon_url,
            'image_processed': bool(image),
            'faq_count': len(faqs),
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
        })

        time.sleep(1)

    with open(os.path.join(backup_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    log_path = os.path.join(base_dir, '..', 'updates-log.json')
    existing = {'runs': []}
    if os.path.exists(log_path):
        with open(log_path) as f:
            existing = json.load(f)
    existing['runs'].append({'run_id': run_id, 'mode': 'pilot', 'entries': log_entries})
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Pilot complete")
    print(f"   Log: {log_path}")
    print(f"   Backup: {backup_dir}")


if __name__ == '__main__':
    main()
