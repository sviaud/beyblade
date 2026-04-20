#!/usr/bin/env python3
"""Crée de nouveaux articles à partir d'images déjà uploadées sur WP.

Usage: python3 scripts/05_new_articles.py <products_json> [--dry-run]

Le fichier products_json contient un dict {slug: {product, wp_images: [{id, url}]}}
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
from rating_box import build_review_block

AMAZON_TAG = "pistol-21"
ELITE_CATEGORY_ID = 46


def build_faqs(product):
    from product_data import ProductDatabase
    name = product['name']
    default_faqs = ProductDatabase.default_faq(name, product.get('age_min', 8), product.get('portee_m'))
    overrides = product.get('faq_overrides', [])
    override_themes = set()
    for f in overrides:
        q = f['q'].lower()
        if 'enfant' in q or 'ans' in q: override_themes.add('enfant')
        if 'acheter' in q or 'prix' in q or 'où' in q: override_themes.add('acheter')
        if 'portée' in q or 'distance' in q: override_themes.add('portee')
        if 'munition' in q or 'fléchette' in q or 'compatible' in q: override_themes.add('munitions')
    filtered = [f for f in default_faqs if not any(k in f['q'].lower() for k in override_themes)]
    return (overrides + filtered)[:8]


def create_article(client, product, wp_images, category_id, dry_run=False):
    """Crée un article WP complet avec carrousel."""
    name = product['name']
    amazon_url = build_search_url(name, AMAZON_TAG)
    amazon_cta = build_cta_html(name, AMAZON_TAG)

    carousel_images = [{'src': img['url'], 'alt': f'{name} — photo {i+1}'} for i, img in enumerate(wp_images)]
    review_block = build_review_block(product, carousel_images, amazon_url)
    faqs = build_faqs(product)

    article_html = generate_article_html(
        product=product,
        image_html='',
        amazon_cta=amazon_cta,
        faqs=faqs,
        review_block=review_block,
    )

    word_count = len(re.sub(r'<[^>]+>', ' ', article_html).split())

    if dry_run:
        print(f'  [DRY] {name}: {word_count} words, {len(wp_images)} images')
        return None

    post_data = {
        'title': name,
        'content': article_html,
        'status': 'publish',
        'categories': [category_id],
    }

    result = client.post('/wp/v2/posts', post_data)
    post_id = result['id']
    post_url = result['link']

    # Apply The7 meta (sidebar, hide thumbnail, header style)
    the7_meta = {
        "_dt_sidebar_position": "right",
        "_dt_sidebar_widgetarea_id": "sidebar_1",
        "_dt_footer_show": "1",
        "_dt_footer_widgetarea_id": "sidebar_2",
        "_dt_header_title": "enabled",
        "_dt_header_background": "normal",
        "_dt_post_options_hide_thumbnail": "1",
        "_dt_post_options_related_mode": "same",
        "_dt_post_options_preview": "normal",
        "_dt_fancy_header_title_aligment": "center",
        "_dt_fancy_header_title": name,
        "_dt_fancy_header_title_color": "#ffffff",
        "_dt_fancy_header_bg_color": "#4c4c4c",
        "_dt_fancy_header_bg_repeat": "no-repeat",
        "_dt_fancy_header_bg_position_x": "center",
        "_dt_fancy_header_bg_position_y": "center",
        "_dt_fancy_header_bg_fullscreen": "1",
        "_dt_fancy_header_height": "80",
        "_dt_fancy_header_title_mode": "custom",
        "_dt_fancy_header_title_color_mode": "color",
        "_dt_fancy_header_bg_image": "a:1:{i:0;i:1277;}",
        "_dt_sidebar_hide_on_mobile": "0",
    }
    try:
        client.post(f'/pistoletnerf/v1/postmeta/{post_id}', the7_meta)
    except Exception as e:
        print(f'  ⚠️ The7 meta failed: {e}')

    # Set featured image (for widgets/search, hidden on page by _dt_post_options_hide_thumbnail)
    if wp_images:
        try:
            client.update_post(post_id, {'featured_media': wp_images[0]['id']})
        except Exception:
            pass

    print(f'  ✅ {name}: ID={post_id} wc={word_count} imgs={len(wp_images)}')
    print(f'     {post_url}')

    return {'id': post_id, 'url': post_url, 'word_count': word_count}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/05_new_articles.py <products_json> [--dry-run]")
        sys.exit(1)

    products_file = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    base_dir = os.path.dirname(os.path.abspath(__file__))
    client = WPClient.from_env(os.path.join(base_dir, '..', 'config.env'))

    with open(products_file) as f:
        products = json.load(f)

    # Also update the main products database
    db_path = os.path.join(base_dir, '..', 'data', 'nerf-products.json')
    with open(db_path) as f:
        all_products = json.load(f)

    print(f"Processing {len(products)} products {'[DRY RUN]' if dry_run else '[LIVE]'}")

    for slug, data in products.items():
        product = data['product']
        wp_images = data.get('wp_images', [])
        category_id = data.get('category_id', ELITE_CATEGORY_ID)

        result = create_article(client, product, wp_images, category_id, dry_run)

        if result and not dry_run:
            # Add to products database
            all_products[str(result['id'])] = product
            time.sleep(1)

    if not dry_run:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        print(f'\n✅ Products database updated')


if __name__ == '__main__':
    main()
