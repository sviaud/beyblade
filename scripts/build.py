"""Orchestrateur de build du site statique toupiebeyblade.fr.

Pipeline :
1. Clean /dist
2. Copy src/static/* → dist/
3. Copy src/_redirects, src/_headers → dist/
4. Generate homepage
5. Generate /tous-les-beyblade/ (catalogue groupé par gamme)
6. Generate /comparatif-{gamme}/ (5 pages comparatif)
7. Generate fiches produit /{slug}/ (40+ pages)
8. Generate /sitemap.xml + /robots.txt

Usage : python3 scripts/build.py [--clean] [--only homepage|articles|...]
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

# Permettre l'import des modules locaux
sys.path.insert(0, str(Path(__file__).resolve().parent))

from file_writer import (
    clean_dist, copy_static, copy_root_files, write_page,
    write_xml, write_text, list_pages, DIST_DIR
)
from sitemap import render_sitemap, render_robots

SRC_TEMPLATES = Path(__file__).resolve().parent.parent / 'src' / 'templates'


def build_homepage():
    """Génère la homepage / depuis src/templates/homepage_body.html."""
    from seo_meta import render_head, faq_schema, breadcrumb_schema, SITE_URL

    # ItemList schema pour les Top 4 toupies (rich snippet potentiel)
    top_toupies_itemlist = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': 'Top 4 toupies Beyblade — Avril 2026',
        'itemListOrder': 'https://schema.org/ItemListOrderDescending',
        'numberOfItems': 4,
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': 1,
                'item': {
                    '@type': 'Product',
                    'name': 'Dranzer Spiral 3-60P',
                    'category': 'Beyblade X',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 9.2, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/dran-sword-3-60f/',
                },
            },
            {
                '@type': 'ListItem',
                'position': 2,
                'item': {
                    '@type': 'Product',
                    'name': 'Phoenix Wing 9-60GF',
                    'category': 'Beyblade X',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 8.8, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/phoenix-wing-9-60gf/',
                },
            },
            {
                '@type': 'ListItem',
                'position': 3,
                'item': {
                    '@type': 'Product',
                    'name': 'Pegasus Galaxy W105R²F',
                    'category': 'Beyblade Metal Fusion',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 8.5, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/galaxy-pegasus-w105r2f/',
                },
            },
            {
                '@type': 'ListItem',
                'position': 4,
                'item': {
                    '@type': 'Product',
                    'name': 'Valtryek Volcanic',
                    'category': 'Beyblade Burst',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 8.3, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/valtryek-volcanic/',
                },
            },
        ],
    }

    # FAQPage schema (AIO — directement utilisé par les LLM pour grounding)
    home_faq = faq_schema([
        ('Quelle toupie Beyblade choisir en 2026 ?',
         'Pour débuter, nous recommandons la Knight Shield 3-80N (Beyblade X, défense) — pardonnante aux erreurs de lancer et abordable. Pour les confirmé·e·s qui visent la compétition, la Dranzer Spiral 3-60P (attaque, note 9.2/10) est notre choix #1 du moment.'),
        ('Quelle est la différence entre Beyblade X, Burst et Metal Fusion ?',
         'Beyblade X (2024+) utilise le système Blade/Ratchet/Bit avec rampe Xtreme et combats explosifs. Beyblade Burst (2016+) repose sur le système Layer/Disc/Driver avec mécanique d\'éclatement (Burst Finish). Metal Fusion (2010-2013) est l\'ère métallique culte avec un système 4 pièces. Les trois gammes sont incompatibles entre elles.'),
        ('Où acheter une toupie Beyblade en France ?',
         'Les revendeurs FR fiables : Amazon.fr (stock le plus large, livraison Prime), King Jouet et Leclerc Jouets en magasin physique, La Grande Récré. Évitez les marketplaces non vérifiées (AliExpress, certains vendeurs Cdiscount) où circulent des contrefaçons.'),
        ('Faut-il acheter un stadium Beyblade ?',
         'Oui, c\'est indispensable pour bien jouer. Le stadium officiel correspondant à votre gamme conditionne 60% du gameplay : Beyblade X Xtreme Stadium pour Beyblade X, Burst Surge Stadium pour Burst. Sans stadium officiel, les Bits glissent et les combats perdent leur sens.'),
        ('À partir de quel âge peut-on jouer ?',
         'L\'emballage Hasbro indique généralement 8 ans et plus. En pratique, Beyblade X est plus exigeant (lancer précis sur stadium incliné) — nous recommandons 10 ans et +. Burst est plus accessible dès 6-7 ans.'),
    ])

    head = render_head(
        title='Toupies Beyblade : tests, comparatifs et guide d\'achat 2026',
        description='Le guide français indépendant des toupies Beyblade : 42 fiches testées (Beyblade X, Burst, Metal Fusion), comparatifs détaillés, notes vérifiables sur 5 critères.',
        canonical_path='/',
        og_type='website',
        extra_css=['/css/page-home.css'],
        preload_images=['/img/dran-sword.webp', '/img/phoenix-wing.webp'],
        extra_jsonld=[top_toupies_itemlist, home_faq],
    )

    body_inner = (SRC_TEMPLATES / 'homepage_body.html').read_text()
    return write_page('', f'<head>\n{head}\n</head>\n<body>\n{body_inner}\n</body>')


def build_article_dran_sword():
    """Génère /dran-sword-3-60f/ — première fiche pilote Beyblade X."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )

    product = {
        'name': 'Dran Sword 3-60F',
        'reference': 'BX-01',
        'gamme': 'beyblade-x',
        'type': 'attaque',
        'year': 2023,
        'asin': 'B0C52R16P1',
        'image_url': f'{SITE_URL}/img/dran-sword.webp',
        'description': "Test complet de la Dran Sword 3-60F (BX-01), la première Beyblade X de Takara Tomy. Note 8.5/10. Performance, combos et FAQ.",
    }

    schemas = [
        product_schema(product, review_score=8.5, review_max=10),
        article_schema(
            headline='Dran Sword 3-60F : test complet Beyblade X',
            description=product['description'],
            url_path='/dran-sword-3-60f/',
            image_url=product['image_url'],
            date_published='2026-04-19T10:00:00+02:00',
            date_modified='2026-04-20T11:00:00+02:00',
            section='Beyblade X',
        ),
        breadcrumb_schema([
            ('Accueil', '/'),
            ('Beyblade X', '/comparatif-beyblade-x/'),
            ('Dran Sword 3-60F', '/dran-sword-3-60f/'),
        ]),
        faq_schema([
            ('Quel lanceur utiliser avec la Dran Sword ?',
             "Le Xtreme Launcher fourni dans la boîte est suffisant pour les sessions casual. Pour la compétition, le Beyblade X Launcher Grip ajoute un manche stabilisateur et permet un shoot 15% plus rapide."),
            ('La Dran Sword est-elle compatible avec un stadium Burst ?',
             "Non, la Dran Sword est exclusivement Beyblade X. Le Bit Flat glisse sur les stadiums Burst plats et la lame Sword ne fonctionne qu'avec une rampe Xtreme."),
            ('Où acheter la Dran Sword en France ?',
             "Amazon FR (lien direct depuis cette page), King Jouet, Leclerc Jouets et la Grande Récré. Évitez les marketplaces non vérifiées : nombreuses contrefaçons circulent."),
            ('Quelle est la rareté de la Dran Sword ?',
             "Production large depuis 2023, donc rien d'extraordinaire en version standard. Les versions Special Edition (chrome, clear, glow-in-the-dark) sortent à chaque saison anime."),
            ('La Dran Sword est-elle personnalisable ?',
             "Oui — la lame Sword peut être combinée avec n'importe quel Ratchet/Bit Beyblade X. Notre combo préféré pour le tournoi : Sword 4-80F qui pousse l'agressivité à 9.5/10."),
            ('Différence entre Dran Sword (BX-01) et Dran Buster (UX-01) ?',
             "La Dran Buster (UX-01, 2024) est une évolution Unique-X plus puissante avec un Blade en alliage métallique. La Dran Sword (BX-01) reste plus accessible et plus polyvalente pour débuter."),
            ('À partir de quel âge peut-on jouer ?',
             "Hasbro indique 8 ans et plus. En pratique nous recommandons 10 ans et + pour profiter pleinement du système Xtreme. Pour les plus jeunes, privilégier la Knight Shield (BX-04) plus pardonnante."),
            ('Faut-il acheter la garantie magasin ?',
             "Non. La Dran Sword est garantie 2 ans par Hasbro contre les défauts de fabrication, et l'usure normale n'est jamais couverte par les garanties magasin."),
        ]),
    ]

    head = render_head(
        title='Dran Sword 3-60F : test complet Beyblade X (note 8.5/10)',
        description="Notre test complet de la Dran Sword 3-60F (BX-01), la première Beyblade X. Performance en stadium Xtreme, combos avancés, alternatives, FAQ — note 8.5/10.",
        canonical_path='/dran-sword-3-60f/',
        og_type='article',
        og_image='/img/dran-sword.webp',
        article_published='2026-04-19T10:00:00+02:00',
        article_modified='2026-04-20T11:00:00+02:00',
        article_section='Beyblade X',
        extra_css=['/css/page-article.css'],
        preload_images=['/img/dran-sword.webp'],
        extra_jsonld=schemas,
    )

    body_inner = (SRC_TEMPLATES / 'article_dran_sword.html').read_text()
    return write_page('dran-sword-3-60f', f'<head>\n{head}\n</head>\n<body>\n{body_inner}\n</body>')


def build_sitemap():
    """Génère sitemap.xml à partir de toutes les pages dans /dist."""
    pages_data = []
    for p in list_pages():
        url = p['url']
        if url == '/':
            priority, changefreq = 1.0, 'daily'
        elif url.startswith('/comparatif-'):
            priority, changefreq = 0.9, 'weekly'
        elif url.startswith('/tous-'):
            priority, changefreq = 0.9, 'weekly'
        else:
            priority, changefreq = 0.7, 'monthly'
        pages_data.append({
            'path': url,
            'priority': priority,
            'changefreq': changefreq,
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
        })
    xml = render_sitemap(pages_data)
    return write_xml('sitemap', xml)


def build_robots():
    return write_text('robots.txt', render_robots())


def build_404():
    """Page 404 simple."""
    from seo_meta import render_head
    head = render_head(
        title='404 — Page introuvable · toupiebeyblade.fr',
        description='Cette page n\'existe pas (ou plus). Retournez à l\'accueil pour découvrir nos tests Beyblade.',
        canonical_path='/404.html',
        robots='noindex, follow',
    )
    body = '''<body>
<main style="padding:120px 24px;text-align:center;position:relative;z-index:2">
<h1 style="font-family:var(--font-display);font-weight:900;font-size:200px;line-height:0.8;color:var(--accent);text-shadow:var(--glow-blue);margin-bottom:24px">404</h1>
<h2 style="font-family:var(--font-display);font-weight:900;font-size:48px;text-transform:uppercase;letter-spacing:-1px;margin-bottom:16px">Page introuvable</h2>
<p style="color:var(--text-soft);font-size:18px;max-width:540px;margin:0 auto 32px">Cette toupie a peut-être été éjectée du stadium. Retournez à l'accueil pour reprendre votre exploration.</p>
<a href="/" class="btn btn-primary">Retour à l'accueil</a>
</main>
</body>'''
    return write_page('404.html', f'<head>\n{head}\n</head>\n{body}')


def main():
    parser = argparse.ArgumentParser(description='Build toupiebeyblade.fr static site')
    parser.add_argument('--no-clean', action='store_true', help='Skip clean step')
    parser.add_argument('--only', help='Only run a specific step (homepage, sitemap, etc.)')
    args = parser.parse_args()

    if not args.no_clean:
        print('🧹 Cleaning /dist...')
        clean_dist()

    print('📁 Copying static assets...')
    n_static = copy_static()
    print(f'   {n_static} files copied')

    print('🔗 Copying _redirects + _headers...')
    n_root = copy_root_files()
    print(f'   {n_root} root files copied')

    print('🏠 Building homepage...')
    p = build_homepage()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('⚔️  Building article : Dran Sword 3-60F...')
    p = build_article_dran_sword()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🚫 Building 404 page...')
    p = build_404()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🗺️  Building sitemap.xml...')
    p = build_sitemap()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🤖 Building robots.txt...')
    p = build_robots()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print()
    print('✅ Build complete')
    print(f'   {len(list_pages())} pages in /dist')
    print(f'   Next : python3 -m http.server 8000 --directory dist  # to preview')


if __name__ == '__main__':
    main()
