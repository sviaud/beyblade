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


def build_metal_fusion_article(slug, product, template_filename):
    """Build une fiche Metal Fusion à partir d'un product dict + template HTML.

    Args:
        slug: ex 'rock-leone-145wb'
        product: dict avec name, reference, asin, type, year, review_score, faq, etc.
        template_filename: ex 'article_rock_leone.html'
    """
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )

    schemas = [
        product_schema(product, review_score=product['review_score'], review_max=10),
        article_schema(
            headline=product['headline'],
            description=product['description'],
            url_path=f'/{slug}/',
            image_url=product.get('image_url', f'{SITE_URL}/img/og-default.jpg'),
            date_published='2026-04-19T10:00:00+02:00',
            date_modified='2026-04-20T11:00:00+02:00',
            section='Beyblade Metal Fusion',
        ),
        breadcrumb_schema([
            ('Accueil', '/'),
            ('Beyblade Metal Fusion', '/comparatif-beyblade-metal-fusion/'),
            (product['name'], f'/{slug}/'),
        ]),
        faq_schema(product['faq']),
    ]

    head = render_head(
        title=product['title'],
        description=product['description'],
        canonical_path=f'/{slug}/',
        og_type='article',
        og_image=product.get('image_url', '/img/og-default.jpg'),
        article_published='2026-04-19T10:00:00+02:00',
        article_modified='2026-04-20T11:00:00+02:00',
        article_section='Beyblade Metal Fusion',
        extra_css=['/css/page-article.css'],
        extra_jsonld=schemas,
    )

    body_inner = (SRC_TEMPLATES / template_filename).read_text()
    return write_page(slug, f'<head>\n{head}\n</head>\n<body>\n{body_inner}\n</body>')


def build_article_rock_leone():
    """Génère /rock-leone-145wb/ — fiche Metal Fusion + activation backlink legacy."""
    product = {
        'name': 'Rock Leone 145WB',
        'reference': 'BB-30',
        'gamme': 'beyblade-metal-fusion',
        'type': 'defense',
        'year': 2010,
        'asin': 'B00NQFBOT2',
        'review_score': 8.1,
        'title': 'Rock Leone 145WB : test complet Metal Fusion (note 8.1/10)',
        'headline': 'Rock Leone 145WB : test complet Metal Fusion',
        'description': "Test complet de la Rock Leone 145WB (BB-30), la défenseuse iconique de Kyoya Tategami. Caractéristiques, performance, alternatives, FAQ — note 8.1/10.",
        'image_url': '',  # SVG placeholder, pas de photo réelle
        'faq': [
            ('La Rock Leone est-elle compatible avec un stadium Beyblade X ?',
             "Non. La Rock Leone est une toupie Metal Fusion qui utilise le système 5 pièces métalliques. Le stadium Xtreme de Beyblade X (rampe inclinée) n'est pas adapté à sa Performance Tip Wide Ball — utilisez un stadium Metal Fusion classique (Hasbro Hyperblade ou Takara Tomy BeyStadium)."),
            ('Quelle est la différence entre la version Hasbro et la version Takara Tomy ?',
             "La version Takara Tomy (japonaise originale) a une finition mat plus sobre et est devenue rare. La version Hasbro (européenne, vendue dès 2011) a une finition vert vif plus brillante et reste accessible sur Amazon FR. Mécaniquement, les deux sont identiques."),
            ('Peut-on encore l\'utiliser en tournoi compétitif aujourd\'hui ?',
             "Oui, mais uniquement dans des tournois Metal Fusion legacy (rares en 2026). Les tournois officiels actuels utilisent Beyblade X ou Burst. La Rock Leone reste valable pour les sessions casual entre fans de l'ère Metal Fight."),
            ('Quel combo personnalisé recommandez-vous ?',
             "Le combo stock Rock 145WB est déjà excellent en défense. Pour les confirmé·e·s, essayez Rock 230D (Spin Track 230 + Defense tip) qui pousse la stabilité encore plus loin, ou Earth 145WB qui combine endurance et défense."),
            ('Où acheter la Rock Leone en France en 2026 ?',
             "Amazon FR reste la source la plus fiable. Vous pouvez aussi chercher sur des sites spécialisés type BeyStation ou GoToupie. Évitez les marketplaces non vérifiées : nombreuses contrefaçons circulent (Fusion Wheel en plastique au lieu de métal)."),
        ],
    }
    return build_metal_fusion_article('rock-leone-145wb', product, 'article_rock_leone.html')


def build_article_meteo_l_drago():
    """Génère /meteo-l-drago-lw105lrf/ — fiche Metal Fusion attaque gauche."""
    product = {
        'name': 'Meteo L-Drago LW105LRF',
        'reference': 'BB-88',
        'gamme': 'beyblade-metal-fusion',
        'type': 'attaque',
        'year': 2011,
        'asin': 'B00N41NRLG',
        'review_score': 7.5,
        'title': 'Meteo L-Drago LW105LRF : test complet Metal Fusion (note 7.5/10)',
        'headline': 'Meteo L-Drago LW105LRF : test complet Metal Fusion',
        'description': "Test complet de la Meteo L-Drago LW105LRF (BB-88), l'attaquante à rotation gauche de Ryuga. Performance, Spin Steal, alternatives, FAQ — note 7.5/10.",
        'image_url': '',
        'faq': [
            ('La Meteo L-Drago est-elle compatible avec un stadium Beyblade X ?',
             "Non. C'est une toupie Metal Fusion. Le stadium Xtreme de Beyblade X n'est pas adapté à sa Performance Tip LRF en caoutchouc. Utilisez un stadium Metal Fusion classique."),
            ('Pourquoi la rotation gauche fait-elle une telle différence ?',
             "99% des toupies Beyblade tournent vers la droite. La Meteo L-Drago tourne vers la gauche, ce qui lui permet de voler l'énergie cinétique de l'adversaire (mécanique appelée Spin Steal). Une défenseuse droite normalement insortable peut être éjectée en 5-10 secondes."),
            ('Le lanceur gauche est-il indispensable ?',
             "Oui. Un lanceur droit standard ne fait pas tourner la Meteo L-Drago dans le bon sens. Le pack BB-88 inclut le lanceur L-Drago (gauche). Pour les remplacements : cherchez Beyblade Left Spin Launcher sur Amazon FR."),
            ('Combien de lancers la pointe LRF supporte-t-elle ?',
             "En usage normal sur stadium plastique : environ 50-80 lancers avant que la pointe rubber ne perde de sa souplesse. Sur stadium béton ou tournoi intensif : 30-40 lancers."),
            ('Où acheter la Meteo L-Drago en France en 2026 ?',
             "Amazon FR reste la source la plus fiable. Sites spécialisés type BeyStation ou GoToupie sinon. Évitez les marketplaces non vérifiées."),
        ],
    }
    return build_metal_fusion_article('meteo-l-drago-lw105lrf', product, 'article_meteo_l_drago.html')


def build_article_galaxy_pegasus():
    """Génère /galaxy-pegasus-w105r2f/ — fiche Metal Fusion attaque iconique."""
    product = {
        'name': 'Galaxy Pegasus W105R²F',
        'reference': 'BB-70',
        'gamme': 'beyblade-metal-fusion',
        'type': 'attaque',
        'year': 2010,
        'asin': 'B004PZCYXC',
        'review_score': 7.7,
        'title': 'Galaxy Pegasus W105R²F : test complet Metal Fusion (note 7.7/10)',
        'headline': 'Galaxy Pegasus W105R²F : test complet Metal Fusion',
        'description': "Test complet de la Galaxy Pegasus W105R²F (BB-70), l'attaquante iconique de Ginga Hagane. Évolution de la Storm Pegasus, performance, FAQ — note 7.7/10.",
        'image_url': '',
        'faq': [
            ('La Galaxy Pegasus est-elle compatible avec un stadium Beyblade X ?',
             "Non. C'est une toupie Metal Fusion. Le stadium Xtreme de Beyblade X n'est pas adapté à sa Performance Tip R²F. Utilisez un stadium Metal Fusion classique."),
            ('Quelle est la différence avec la Storm Pegasus 105RF ?',
             "La Storm Pegasus 105RF (BB-28, 2010) est la toupie originale, moins puissante mais culte. La Galaxy Pegasus W105R²F (BB-70, fin 2010) est son évolution avec Fusion Wheel plus puissante et Spin Track Wing 105 qui ajoute de la stabilité latérale."),
            ('Quelle est la différence entre la version Hasbro et Takara Tomy ?',
             "La version Takara Tomy a une finition métallique brillante et est devenue rare (35-50 €). La version Hasbro reste accessible sur Amazon FR (15-25 €). Mécaniquement identiques."),
            ('Quel combo personnalisé recommandez-vous ?',
             "Le combo stock Galaxy W105R²F est déjà excellent. Pour les confirmé·e·s : Galaxy 100RF (plus agressif) ou Galaxy 145D (Defense tip pour mode défense surprise)."),
            ('Où acheter la Galaxy Pegasus en France en 2026 ?',
             "Amazon FR (lien direct depuis cette page). Sites spécialisés type BeyStation ou GoToupie pour les éditions Takara Tomy. Évitez les marketplaces non vérifiées."),
        ],
    }
    return build_metal_fusion_article('galaxy-pegasus-w105r2f', product, 'article_galaxy_pegasus.html')


def build_comparatif_metal_fusion():
    """Génère /comparatif-beyblade-metal-fusion/ — page hub gamme MF."""
    from seo_meta import (
        render_head, breadcrumb_schema, faq_schema, SITE_URL,
    )

    # ItemList schema pour les 3 toupies testées (rich snippet)
    itemlist = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': 'Comparatif Beyblade Metal Fusion 2026',
        'itemListOrder': 'https://schema.org/ItemListOrderDescending',
        'numberOfItems': 3,
        'itemListElement': [
            {
                '@type': 'ListItem', 'position': 1,
                'item': {
                    '@type': 'Product',
                    'name': 'Rock Leone 145WB',
                    'category': 'Beyblade Metal Fusion',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 8.1, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/rock-leone-145wb/',
                },
            },
            {
                '@type': 'ListItem', 'position': 2,
                'item': {
                    '@type': 'Product',
                    'name': 'Galaxy Pegasus W105R²F',
                    'category': 'Beyblade Metal Fusion',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 7.7, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/galaxy-pegasus-w105r2f/',
                },
            },
            {
                '@type': 'ListItem', 'position': 3,
                'item': {
                    '@type': 'Product',
                    'name': 'Meteo L-Drago LW105LRF',
                    'category': 'Beyblade Metal Fusion',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 7.5, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/meteo-l-drago-lw105lrf/',
                },
            },
        ],
    }

    faq = faq_schema([
        ('Quelle Metal Fusion choisir pour débuter en collection ?',
         "Notre recommandation : Galaxy Pegasus W105R²F (BB-70). Toupie iconique de Ginga (héros de l'anime), polyvalente, prix correct sur Amazon FR (15-25 €), facile à compléter avec d'autres pièces Metal Fusion compatibles."),
        ('Quelle est la différence Metal Fusion vs Metal Masters vs Metal Fury ?',
         "Trois sous-générations : Metal Fusion (2010, BB-1 à BB-100), Metal Masters (2011-2012, BB-101 à BB-130), Metal Fury / 4D (2012-2013, BB-131+). Toutes les pièces sont interchangeables — seul le marketing change."),
        ('Les Metal Fusion sont-elles compatibles avec Beyblade Burst ou X ?',
         "Non. Chaque gamme a son système : Metal Fusion = 5 pièces métalliques, Burst = Layer/Disc/Driver, X = Blade/Ratchet/Bit. Stadiums et lanceurs sont aussi spécifiques."),
        ('Où acheter des Metal Fusion authentiques en 2026 ?',
         "Amazon FR pour les versions Hasbro encore en production (Rock Leone, Galaxy Pegasus, Storm Pegasus). Pour les versions Takara Tomy originales : BeyStation, GoToupie ou eBay (vigilance contre les contrefaçons en plastique)."),
        ('Comment reconnaître une Metal Fusion authentique d\'une contrefaçon ?',
         "3 vérifications : (1) la Fusion Wheel doit être en métal (test aimant ou poids ~25-30g). (2) Le sticker du Face Bolt est imprimé proprement. (3) La boîte officielle a un code-barres EAN Hasbro France ou Takara Tomy Japan."),
        ('Y a-t-il des tournois Metal Fusion en 2026 ?',
         "Plus de tournois officiels Hasbro depuis 2014. La communauté worldbeyblade.org organise encore des tournois legacy en ligne et en présentiel (USA, Europe). En France, quelques meet-ups via beybladeforum.forumgratuit.org."),
    ])

    breadcrumb = breadcrumb_schema([
        ('Accueil', '/'),
        ('Comparatifs', '/comparatifs/'),
        ('Beyblade Metal Fusion', '/comparatif-beyblade-metal-fusion/'),
    ])

    head = render_head(
        title='Comparatif Beyblade Metal Fusion 2026 : 8 toupies BB-XX testées',
        description="Comparatif complet des 8 toupies Beyblade Metal Fusion (2010-2013) : Rock Leone, Galaxy Pegasus, Meteo L-Drago et plus. Notes vérifiables, méthode publique, alternatives Amazon.",
        canonical_path='/comparatif-beyblade-metal-fusion/',
        og_type='website',
        extra_css=['/css/page-comparatif.css'],
        extra_jsonld=[itemlist, faq, breadcrumb],
    )

    body_inner = (SRC_TEMPLATES / 'page_comparatif_metal_fusion.html').read_text()
    return write_page('comparatif-beyblade-metal-fusion', f'<head>\n{head}\n</head>\n<body>\n{body_inner}\n</body>')


def build_comparatif_beyblade_x():
    """Génère /comparatif-beyblade-x/ — page hub gamme Beyblade X."""
    from seo_meta import (
        render_head, breadcrumb_schema, faq_schema, SITE_URL,
    )

    itemlist = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': 'Comparatif Beyblade X 2026',
        'itemListOrder': 'https://schema.org/ItemListOrderDescending',
        'numberOfItems': 3,
        'itemListElement': [
            {
                '@type': 'ListItem', 'position': 1,
                'item': {
                    '@type': 'Product',
                    'name': 'Phoenix Wing 9-60GF',
                    'category': 'Beyblade X',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 8.8, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/phoenix-wing-9-60gf/',
                },
            },
            {
                '@type': 'ListItem', 'position': 2,
                'item': {
                    '@type': 'Product',
                    'name': 'Dran Sword 3-60F',
                    'category': 'Beyblade X',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 8.5, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/dran-sword-3-60f/',
                },
            },
            {
                '@type': 'ListItem', 'position': 3,
                'item': {
                    '@type': 'Product',
                    'name': 'Knight Shield 3-80N',
                    'category': 'Beyblade X',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 8.2, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/knight-shield-3-80n/',
                },
            },
        ],
    }

    faq = faq_schema([
        ('Quelle Beyblade X choisir pour débuter ?',
         "Notre recommandation : Knight Shield 3-80N (BX-04). Défense entry-level, pardonnante aux erreurs de lancer, prix abordable (15-20 € sur Amazon FR). Si vous préférez attaquer dès le départ : la Dran Sword 3-60F (BX-01, 8.5/10), inaugurale de la gamme et bien équilibrée pour apprendre."),
        ('Quelle est la différence entre BX et UX (Unique-X) ?',
         "BX (Beyblade X standard) = blade plastique avec inserts métalliques légers, sortie 2023-2024. UX (Unique-X) = blade en alliage métallique premium, sortie 2024+, plus lourde et plus puissante. Les UX sont la sous-ligne compétition (ex: Dran Buster UX-01 vs Dran Sword BX-01). Pièces interchangeables avec BX."),
        ('Les Beyblade X sont-elles compatibles avec Beyblade Burst ou Metal Fusion ?',
         "Non. Chaque gamme a son système propre : Beyblade X = Blade/Ratchet/Bit + stadium Xtreme, Burst = Layer/Disc/Driver + stadium plat, Metal Fusion = 5 pièces métalliques + BeyStadium classique."),
        ('Faut-il acheter le stadium Xtreme officiel ?',
         "Indispensable. Le stadium Xtreme (BX-10, 39,99 € sur Amazon FR) avec sa rampe inclinée à 35° est le cœur du gameplay Beyblade X. Sur un stadium plat, les Bits glissent et les combats perdent leur intérêt. Pour 3 joueurs : Wide Xtreme Stadium (BX-32). Existe aussi en version motorisée Double Xtreme."),
        ('Comment reconnaître une Beyblade X authentique d\'une contrefaçon ?',
         "3 vérifications : (1) le Bit doit être correctement clipsable sur le Ratchet sans jeu. (2) Le Blade a un poids cohérent (~13-15g pour BX, ~18-22g pour UX). (3) La boîte officielle a un code-barres EAN Hasbro France ou Takara Tomy Japan."),
        ('Y a-t-il des tournois Beyblade X en 2026 ?',
         "Oui — la gamme X est l'active competitive scene. Hasbro organise les Beyblade X World Championship annuels. La communauté worldbeyblade.org liste les tournois locaux. En France, plusieurs magasins King Jouet et JouéClub organisent des sessions casual le samedi."),
    ])

    breadcrumb = breadcrumb_schema([
        ('Accueil', '/'),
        ('Comparatifs', '/comparatifs/'),
        ('Beyblade X', '/comparatif-beyblade-x/'),
    ])

    head = render_head(
        title='Comparatif Beyblade X 2026 : 18 toupies BX-XX et UX testées',
        description="Comparatif complet des toupies Beyblade X (gamme 2024+) avec notes vérifiables. Découvrez quelle toupie X choisir : Dran Sword, Phoenix Wing, Knight Shield, Wizard Arrow et plus.",
        canonical_path='/comparatif-beyblade-x/',
        og_type='website',
        extra_css=['/css/page-comparatif.css'],
        extra_jsonld=[itemlist, faq, breadcrumb],
    )

    body_inner = (SRC_TEMPLATES / 'page_comparatif_beyblade_x.html').read_text()
    return write_page('comparatif-beyblade-x', f'<head>\n{head}\n</head>\n<body>\n{body_inner}\n</body>')


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

    print('🦁 Building article : Rock Leone 145WB...')
    p = build_article_rock_leone()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🐉 Building article : Meteo L-Drago LW105LRF...')
    p = build_article_meteo_l_drago()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🦄 Building article : Galaxy Pegasus W105R²F...')
    p = build_article_galaxy_pegasus()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('📊 Building comparatif : Beyblade Metal Fusion...')
    p = build_comparatif_metal_fusion()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('📊 Building comparatif : Beyblade X...')
    p = build_comparatif_beyblade_x()
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
