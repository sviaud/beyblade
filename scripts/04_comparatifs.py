#!/usr/bin/env python3
"""Met à jour toutes les pages de comparatif avec un tableau moderne.

Usage: python3 scripts/04_comparatifs.py [--dry-run] [--only PAGE_ID]
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
from amazon_link import build_search_url
from image_handler import extract_first_image
from comparison_table import build_comparison_page
from rating_box import compute_ratings


AMAZON_TAG = "pistol-21"

# Mapping page_id → (category_id, display_gamme_name)
COMPARISON_PAGES = {
    1100: {'category_id': 79, 'gamme': 'N-Strike Elite Mega'},
    1012: {'category_id': 64, 'gamme': 'Rebelle'},
    639:  {'category_id': 46, 'gamme': 'Elite'},
    426:  {'category_id': 26, 'gamme': 'Super Soaker'},
    281:  {'category_id': 19, 'gamme': 'Vortex'},
    247:  {'category_id': 12, 'gamme': 'Dart Tag'},
    82:   {'category_id':  7, 'gamme': 'Accessoires'},
    37:   {'category_id':  3, 'gamme': 'N-Strike'},
}

GAMME_CONTEXTS = {
    'N-Strike': "La gamme N-Strike est la collection historique de Nerf, lancée au milieu des années 2000. Elle a posé les bases de l'univers des blasters modernes avec des modèles modulaires et une grande variété de configurations. Les modèles N-Strike utilisent les fléchettes classiques orange et sont reconnus pour leur robustesse et leur accessibilité budgétaire.",
    'Elite': "La gamme Elite représente la génération moderne des blasters Nerf, avec des performances significativement améliorées par rapport à la N-Strike originale. Les modèles Elite utilisent des fléchettes bleues optimisées offrant une portée jusqu'à 22-27 mètres et une précision accrue. C'est aujourd'hui la gamme de référence pour les joueurs sérieux.",
    'N-Strike Elite Mega': "La gamme Mega propose des blasters tirant des fléchettes surdimensionnées (Mega Darts) qui produisent un sifflement caractéristique en vol. Plus imposants visuellement, ces blasters allient portée, précision et effet sonore impressionnant.",
    'Dart Tag': "La gamme Dart Tag, conçue pour la compétition et les tournois organisés, propose des blasters utilisant des fléchettes spéciales à tête velcro. Ces munitions se fixent sur les vestes Dart Tag officielles pour comptabiliser facilement les touches.",
    'Vortex': "La gamme Vortex marque une rupture technologique dans l'univers Nerf : au lieu de fléchettes, elle utilise des disques aérodynamiques appelés XLR Discs, qui offrent une portée remarquable grâce à leur forme permettant un vol stabilisé sur de longues distances.",
    'Rebelle': "La gamme Rebelle a été conçue spécifiquement pour les joueuses, avec un design coloré et élégant, sans compromettre les performances. Les modèles Rebelle proposent des fonctionnalités créatives comme les arcs, les arbalètes et les blasters compacts.",
    'Super Soaker': "Super Soaker est la gamme dédiée aux batailles d'eau, rachetée par Hasbro et intégrée à l'univers Nerf. Ces blasters à eau utilisent divers mécanismes pour propulser de l'eau à grande distance, offrant une alternative estivale aux fléchettes.",
    'Accessoires': "Les accessoires Nerf regroupent tous les compléments indispensables pour une expérience optimale : recharges de fléchettes, chargeurs additionnels, sacs et gilets tactiques, cibles, bandoulières et autres éléments de personnalisation.",
}


def extract_image_from_post(post, client):
    """Récupère l'URL de la featured image ou de la première image inline."""
    fm = post.get('featured_media', 0)
    if fm:
        try:
            media = client.get_media(fm)
            src = media.get('source_url') or media.get('guid', {}).get('rendered', '')
            if src:
                return src
        except Exception:
            pass
    img = extract_first_image(post['content'].get('raw', ''))
    return img.get('src') if img else None


def fetch_category_posts(client, category_id):
    """Récupère tous les posts d'une catégorie."""
    posts = client.get('/wp/v2/posts', params={
        'per_page': 100,
        'context': 'edit',
        'categories': category_id,
    })
    return posts


def backup_page(backup_dir, page):
    path = os.path.join(backup_dir, 'pages', f"{page['id']}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(page, f, ensure_ascii=False, indent=2)


def main():
    dry_run = '--dry-run' in sys.argv
    only_id = None
    if '--only' in sys.argv:
        idx = sys.argv.index('--only')
        only_id = int(sys.argv[idx + 1])

    base_dir = os.path.dirname(os.path.abspath(__file__))
    client = WPClient.from_env(os.path.join(base_dir, '..', 'config.env'))
    db = ProductDatabase(os.path.join(base_dir, '..', 'data', 'nerf-products.json'))

    ts = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H%M%S')
    backup_dir = os.path.join(base_dir, '..', 'backups', ts)
    os.makedirs(os.path.join(backup_dir, 'pages'), exist_ok=True)

    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Backup: {backup_dir}")

    pages_to_process = COMPARISON_PAGES
    if only_id:
        pages_to_process = {only_id: COMPARISON_PAGES[only_id]}
        print(f"Processing only page {only_id}")

    success = 0
    failed = 0

    for page_id, config in pages_to_process.items():
        cat_id = config['category_id']
        gamme = config['gamme']
        print(f"\n=== PAGE {page_id} ({gamme}, cat={cat_id}) ===")

        # Backup the page
        page = client.get(f'/wp/v2/pages/{page_id}', params={'context': 'edit'})
        backup_page(backup_dir, page)
        print(f"  Title: {page['title'].get('raw', '')}")

        # Fetch all posts in the category
        posts = fetch_category_posts(client, cat_id)
        print(f"  Found {len(posts)} posts in category")

        entries = []
        for post in posts:
            pid = post['id']
            if not db.has(pid):
                continue
            product = db.get(pid)
            image_src = extract_image_from_post(post, client)
            permalink = post.get('link', '')
            amazon_url = build_search_url(product['name'], AMAZON_TAG)
            entries.append({
                'product': product,
                'image_src': image_src,
                'permalink': permalink,
                'amazon_url': amazon_url,
                'post_id': pid,
            })

        # Trier par score global desc
        entries.sort(key=lambda e: compute_ratings(e['product'])['global'], reverse=True)
        print(f"  Entries prepared: {len(entries)}")

        gamme_ctx = GAMME_CONTEXTS.get(gamme, '')
        new_html = build_comparison_page(gamme, gamme_ctx, entries)

        word_count = len(re.sub(r'<[^>]+>', ' ', new_html).split())
        print(f"  Generated word count: {word_count}")

        if dry_run:
            preview_path = os.path.join(backup_dir, f'page_{page_id}_preview.html')
            with open(preview_path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            print(f"  [DRY] Preview: {preview_path}")
        else:
            try:
                client.post(f'/wp/v2/pages/{page_id}', {'content': new_html})
                print(f"  ✅ Page updated")
                success += 1
                time.sleep(1)
            except Exception as e:
                print(f"  ❌ Update failed: {e}")
                failed += 1

    print(f"\n=== DONE ===")
    print(f"  Success: {success}")
    print(f"  Failed:  {failed}")
    print(f"  Backup:  {backup_dir}")


if __name__ == '__main__':
    main()
