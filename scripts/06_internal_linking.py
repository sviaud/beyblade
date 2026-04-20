#!/usr/bin/env python3
"""Maillage interne : enrichit les alternatives pour chaque article.

Pour chaque article de la base, trouve 2-3 autres articles de la même gamme
avec des notes proches, et les ajoute dans product['alternatives'] avec le
WP post ID correct pour créer des liens internes.
"""
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
from rating_box import build_review_block, compute_ratings
from image_handler import extract_first_image


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    client = WPClient.from_env(os.path.join(base, '..', 'config.env'))
    db_path = os.path.join(base, '..', 'data', 'nerf-products.json')

    with open(db_path) as f:
        products = json.load(f)

    # Group by gamme
    by_gamme = {}
    for pid, product in products.items():
        gamme = product.get('gamme', '')
        if not gamme:
            continue
        by_gamme.setdefault(gamme, []).append({'id': pid, 'product': product, 'score': compute_ratings(product)['global']})

    print(f'Gammes: {list(by_gamme.keys())}')
    for g, items in by_gamme.items():
        print(f'  {g}: {len(items)} articles')

    # Build alternatives for each article
    enriched = 0
    for pid, product in products.items():
        gamme = product.get('gamme', '')
        if not gamme or gamme not in by_gamme:
            continue
        my_score = compute_ratings(product)['global']
        # Find 3 others with closest scores
        siblings = [s for s in by_gamme[gamme] if s['id'] != pid]
        if not siblings:
            continue
        siblings.sort(key=lambda s: abs(s['score'] - my_score))
        top3 = siblings[:3]

        alternatives = []
        for sib in top3:
            sib_name = sib['product']['name']
            # Build a differentiation hint based on score
            if sib['score'] > my_score + 0.3:
                diff = f"Meilleure note globale ({sib['score']:.1f}/10)"
            elif sib['score'] < my_score - 0.3:
                diff = f"Alternative plus accessible ({sib['score']:.1f}/10)"
            else:
                diff = f"Note similaire ({sib['score']:.1f}/10), un autre choix à envisager"
            alternatives.append({
                'name': sib_name,
                'post_id': int(sib['id']),
                'diff': diff
            })

        product['alternatives'] = alternatives
        enriched += 1

    # Save
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f'\n✅ {enriched} articles enriched with alternatives')


if __name__ == '__main__':
    main()
