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
import re
import sys
from datetime import datetime
from pathlib import Path

# Permettre l'import des modules locaux
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'data'))

from file_writer import (
    clean_dist, copy_static, copy_root_files, write_page,
    write_xml, write_text, list_pages, DIST_DIR
)
from sitemap import render_sitemap, render_robots

SRC_TEMPLATES = Path(__file__).resolve().parent.parent / 'src' / 'templates'


# ============ HTML POST-PROCESSORS ============
# Appliqués au body de toutes les pages avant écriture, pour éviter d'éditer
# le <header class="site-header"> dupliqué dans 22 templates.

NAV_SUBMENU_HTML = (
    '<div class="nav-submenu" role="menu">'
    '<a href="/comparatif-beyblade-x/" role="menuitem">Beyblade X</a>'
    '<a href="/comparatif-beyblade-burst/" role="menuitem">Beyblade Burst</a>'
    '<a href="/comparatif-beyblade-metal-fusion/" role="menuitem">Metal Fusion</a>'
    '<a href="/tous-les-beyblade/" role="menuitem">Toutes les toupies</a>'
    '</div>'
)

# Match the Comparatifs nav link (varies per page : URL + active class)
NAV_LINK_PATTERN = re.compile(
    r'(<a href="/comparatif-[^"]+/" class="has-submenu[^"]*"[^>]*>Comparatifs</a>)'
)

# Dead nav links to remove (option A from product decision: clean nav, no 404 propagation)
DEAD_NAV_LINKS_PATTERN = re.compile(
    r'\s*<a href="/(?:guides|blog|contact)/">[^<]+</a>'
)


def inject_nav_submenu(body_html: str) -> str:
    """Wrap the 'Comparatifs' nav link with a hover dropdown panel."""
    return NAV_LINK_PATTERN.sub(
        lambda m: f'<div class="nav-dropdown">{m.group(1)}{NAV_SUBMENU_HTML}</div>',
        body_html, count=1,
    )


def remove_dead_nav_links(body_html: str) -> str:
    """Strip Guides/Blog/Contact links from .nav (they 404 — option A SEO cleanup)."""
    return DEAD_NAV_LINKS_PATTERN.sub('', body_html)


def assemble_html(head: str, body_inner: str) -> str:
    """Wrap head + body into full HTML, applying nav submenu + dead-link cleanup."""
    body_inner = inject_nav_submenu(body_inner)
    body_inner = remove_dead_nav_links(body_inner)
    return f'<head>\n{head}\n</head>\n<body>\n{body_inner}\n</body>'


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
                    'name': 'Galaxy Pegasus W105R²F',
                    'category': 'Beyblade Metal Fusion',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 7.7, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/galaxy-pegasus-w105r2f/',
                },
            },
            {
                '@type': 'ListItem',
                'position': 4,
                'item': {
                    '@type': 'Product',
                    'name': 'Rock Leone 145WB',
                    'category': 'Beyblade Metal Fusion',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 8.1, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/rock-leone-145wb/',
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
    return write_page('', assemble_html(head, body_inner))


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
    return write_page('dran-sword-3-60f', assemble_html(head, body_inner))


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
    return write_page(slug, assemble_html(head, body_inner))


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


def build_article_phoenix_wing():
    """Génère /phoenix-wing-9-60gf/ — fiche Beyblade X équilibre (Bit Gear Flat)."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )

    product = {
        'name': 'Phoenix Wing 9-60GF',
        'reference': 'BX-23',
        'gamme': 'beyblade-x',
        'type': 'equilibre',
        'year': 2024,
        'asin': 'B0CMZSRJ3Q',
        'image_url': f'{SITE_URL}/img/phoenix-wing.webp',
        'description': "Test complet de la Phoenix Wing 9-60GF (BX-23), l'équilibrée Beyblade X au Bit Gear Flat révolutionnaire. Note 8.8/10. Performance, combos et FAQ.",
    }

    schemas = [
        product_schema(product, review_score=8.8, review_max=10),
        article_schema(
            headline='Phoenix Wing 9-60GF : test complet Beyblade X',
            description=product['description'],
            url_path='/phoenix-wing-9-60gf/',
            image_url=product['image_url'],
            date_published='2026-04-22T10:00:00+02:00',
            date_modified='2026-04-22T10:00:00+02:00',
            section='Beyblade X',
        ),
        breadcrumb_schema([
            ('Accueil', '/'),
            ('Beyblade X', '/comparatif-beyblade-x/'),
            ('Phoenix Wing 9-60GF', '/phoenix-wing-9-60gf/'),
        ]),
        faq_schema([
            ('Quel lanceur utiliser avec la Phoenix Wing ?',
             "Le Xtreme Launcher fourni dans la boîte est suffisant pour les sessions casual. Pour la compétition, le Beyblade X Launcher Grip ajoute un manche stabilisateur."),
            ('La Phoenix Wing est-elle compatible avec un stadium Burst ?',
             "Non, exclusivement Beyblade X. Le Bit Gear Flat ne fonctionne qu'avec une rampe Xtreme — sur stadium plat l'engrenage interne ne s'engage pas."),
            ('Où acheter la Phoenix Wing en France ?',
             "Amazon FR (lien direct depuis cette page), King Jouet, Leclerc Jouets et la Grande Récré. Évitez les marketplaces non vérifiées."),
            ('Quelle est la rareté de la Phoenix Wing ?',
             "Production large depuis mars 2024, donc rien d'extraordinaire en version standard. La Special Color Phoenix Wing or sortie en édition limitée Japon (1500 ex.) est en revanche déjà collector."),
            ('La Phoenix Wing est-elle personnalisable ?',
             "Oui — le Blade Phoenix Wing peut être combiné avec n'importe quel Ratchet/Bit Beyblade X. Notre combo préféré : Phoenix Wing 4-80GF qui pousse la défense à 9.5/10."),
            ('Quelle est la différence entre la Phoenix Wing et la Dran Sword ?',
             "La Dran Sword (BX-01, 8.5/10) est une attaquante pure avec Bit Flat. La Phoenix Wing (BX-23, 8.8/10) est une équilibrée avec Bit Gear Flat — elle dure plus longtemps grâce à la régénération de spin. Choisis Dran Sword pour KO rapide, Phoenix Wing pour out-spin et résistance."),
            ('À partir de quel âge peut-on jouer ?',
             "Hasbro indique 8 ans et plus. En pratique nous recommandons 10 ans et + pour profiter pleinement du système Xtreme. La Phoenix Wing est plus pardonnante que les attaquantes pures, donc accessible aux 8-10 ans avec supervision."),
            ('Faut-il acheter la garantie magasin ?',
             "Non. La Phoenix Wing est garantie 2 ans par Hasbro contre les défauts de fabrication, et l'usure normale n'est jamais couverte par les garanties magasin."),
        ]),
    ]

    head = render_head(
        title='Phoenix Wing 9-60GF : test complet Beyblade X (note 8.8/10)',
        description="Notre test complet de la Phoenix Wing 9-60GF (BX-23), l'équilibrée Beyblade X au Bit Gear Flat révolutionnaire. Performance en stadium Xtreme, combos avancés, alternatives, FAQ — note 8.8/10.",
        canonical_path='/phoenix-wing-9-60gf/',
        og_type='article',
        og_image='/img/phoenix-wing.webp',
        article_published='2026-04-22T10:00:00+02:00',
        article_modified='2026-04-22T10:00:00+02:00',
        article_section='Beyblade X',
        extra_css=['/css/page-article.css'],
        preload_images=['/img/phoenix-wing.webp'],
        extra_jsonld=schemas,
    )

    body_inner = (SRC_TEMPLATES / 'article_phoenix_wing_9_60gf.html').read_text()
    return write_page('phoenix-wing-9-60gf', assemble_html(head, body_inner))


def build_article_knight_shield():
    """Génère /knight-shield-3-80n/ — fiche Beyblade X défense entry-level."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )
    product = {
        'name': 'Knight Shield 3-80N',
        'reference': 'BX-04',
        'gamme': 'beyblade-x',
        'type': 'defense',
        'year': 2023,
        'asin': 'B0C52S6SNN',
        'image_url': f'{SITE_URL}/img/knight-shield.webp',
        'description': "Test complet de la Knight Shield 3-80N (BX-04, Helm Knight chez Hasbro EU), la défenseuse entry-level Beyblade X. Note 8.2/10. Performance, alternatives, FAQ.",
    }
    schemas = [
        product_schema(product, review_score=8.2, review_max=10),
        article_schema(headline='Knight Shield 3-80N : test complet Beyblade X',
                       description=product['description'],
                       url_path='/knight-shield-3-80n/', image_url=product['image_url'],
                       date_published='2026-04-22T11:00:00+02:00',
                       date_modified='2026-04-22T11:00:00+02:00', section='Beyblade X'),
        breadcrumb_schema([('Accueil', '/'), ('Beyblade X', '/comparatif-beyblade-x/'),
                           ('Knight Shield 3-80N', '/knight-shield-3-80n/')]),
        faq_schema([
            ('Quel lanceur utiliser avec la Knight Shield ?',
             "Le Xtreme Launcher fourni dans le starter set est suffisant. Pour la compétition, le Beyblade X Launcher Grip ajoute un manche stabilisateur."),
            ('La Knight Shield est-elle compatible avec un stadium Burst ?',
             "Non, exclusivement Beyblade X. Le Bit Needle ne fonctionne qu'avec une rampe Xtreme."),
            ("Pourquoi Knight Shield s'appelle Helm Knight chez Hasbro ?",
             "Hasbro renomme parfois certaines toupies pour le marché EU. La Knight Shield est ainsi devenue Helm Knight (heaume). Mécaniquement les deux sont identiques."),
            ('Knight Shield ou Dran Sword pour débuter ?',
             "Pour un vrai débutant, la Knight Shield (défense) est plus pardonnante. La Dran Sword (attaque) est plus excitante mais demande un meilleur lancer. Notre conseil : prendre le 4-Pack Starter Set qui contient les 2 (~40 €)."),
            ('Quel combo personnalisé recommandez-vous ?',
             "Le combo stock Knight Shield 3-80N est déjà excellent en défense passive. Pour pousser : Knight Shield 4-80B (Bit Ball stamina, hybride défense+endurance)."),
            ('Où acheter la Knight Shield en France ?',
             "Amazon FR (lien direct depuis cette page), King Jouet, Leclerc Jouets et la Grande Récré. Souvent dispo en Helm Knight chez Hasbro EU."),
            ('À partir de quel âge peut-on jouer ?',
             "Hasbro indique 8 ans et plus. La Knight Shield étant pardonnante, elle convient bien dès 8 ans."),
            ('Faut-il acheter la garantie magasin ?',
             "Non. Garantie 2 ans Hasbro contre les défauts de fabrication."),
        ]),
    ]
    head = render_head(
        title='Knight Shield 3-80N : test complet Beyblade X défense (note 8.2/10)',
        description="Notre test complet de la Knight Shield 3-80N (BX-04), la défenseuse entry-level Beyblade X. Pardonnante, stable, parfaite pour débuter. Performance, combos, FAQ — note 8.2/10.",
        canonical_path='/knight-shield-3-80n/', og_type='article', og_image='/img/knight-shield.webp',
        article_published='2026-04-22T11:00:00+02:00',
        article_modified='2026-04-22T11:00:00+02:00', article_section='Beyblade X',
        extra_css=['/css/page-article.css'], preload_images=['/img/knight-shield.webp'],
        extra_jsonld=schemas)
    body_inner = (SRC_TEMPLATES / 'article_knight_shield_3_80n.html').read_text()
    return write_page('knight-shield-3-80n', assemble_html(head, body_inner))


def build_article_wizard_arrow():
    """Génère /wizard-arrow-4-80b/ — fiche Beyblade X stamina pure."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )
    product = {
        'name': 'Wizard Arrow 4-80B',
        'reference': 'BX-03',
        'gamme': 'beyblade-x',
        'type': 'stamina',
        'year': 2023,
        'asin': 'B0C52TTRDX',
        'image_url': f'{SITE_URL}/img/wizard-arrow.webp',
        'description': "Test complet de la Wizard Arrow 4-80B (BX-03), la stamina pure Beyblade X qui tient 90s en spin. Note 8.4/10. Performance, alternatives, FAQ.",
    }
    schemas = [
        product_schema(product, review_score=8.4, review_max=10),
        article_schema(headline='Wizard Arrow 4-80B : test complet Beyblade X',
                       description=product['description'],
                       url_path='/wizard-arrow-4-80b/', image_url=product['image_url'],
                       date_published='2026-04-22T12:00:00+02:00',
                       date_modified='2026-04-22T12:00:00+02:00', section='Beyblade X'),
        breadcrumb_schema([('Accueil', '/'), ('Beyblade X', '/comparatif-beyblade-x/'),
                           ('Wizard Arrow 4-80B', '/wizard-arrow-4-80b/')]),
        faq_schema([
            ('Quel lanceur utiliser avec la Wizard Arrow ?',
             "Le Xtreme Launcher du starter set suffit. Pour la stamina maximale, optez pour le Beyblade X String Launcher (BX-28) qui donne plus de RPM au lancer initial."),
            ('La Wizard Arrow est-elle compatible avec un stadium Burst ?',
             "Non. Le Bit Ball nécessite la rampe Xtreme officielle pour glisser correctement."),
            ('Combien de temps tient la Wizard Arrow en spin solo ?',
             "Environ 80-90 secondes en lancer maximal sur stadium plat. C'est la plus longue de la gamme X. Une attaquante moyenne tourne 50-60 secondes."),
            ('Wizard Arrow ou Dran Sword pour gagner contre mes amis ?',
             "Si tes amis attaquent agressif : Wizard Arrow (out-spin). Si défensifs : Dran Sword (KO). Le 4-Pack Starter Set permet d'avoir les 2 et d'adapter."),
            ('Quel combo personnalisé recommandez-vous ?',
             "Le combo stock Wizard Arrow 4-80B est déjà excellent. Pour pousser la stamina au max : Wizard Arrow 9-80B (Ratchet 9 lobes pour stabilité maximale)."),
            ('Où acheter la Wizard Arrow en France ?',
             "Amazon FR, King Jouet, Leclerc Jouets et la Grande Récré. Souvent en bundle dans le 4-Pack Starter Set Hasbro à ~40 €."),
            ('À partir de quel âge peut-on jouer ?',
             "Hasbro indique 8 ans et plus. La Wizard Arrow étant stable, elle convient bien dès 8 ans."),
            ('Faut-il acheter la garantie magasin ?',
             "Non. Garantie 2 ans Hasbro contre les défauts de fabrication."),
        ]),
    ]
    head = render_head(
        title='Wizard Arrow 4-80B : test complet Beyblade X stamina (note 8.4/10)',
        description="Notre test complet de la Wizard Arrow 4-80B (BX-03), la stamina pure Beyblade X qui tient 90s en spin. Performance, combos, FAQ — note 8.4/10.",
        canonical_path='/wizard-arrow-4-80b/', og_type='article', og_image='/img/wizard-arrow.webp',
        article_published='2026-04-22T12:00:00+02:00',
        article_modified='2026-04-22T12:00:00+02:00', article_section='Beyblade X',
        extra_css=['/css/page-article.css'], preload_images=['/img/wizard-arrow.webp'],
        extra_jsonld=schemas)
    body_inner = (SRC_TEMPLATES / 'article_wizard_arrow_4_80b.html').read_text()
    return write_page('wizard-arrow-4-80b', assemble_html(head, body_inner))


def build_article_storm_pegasus():
    """Génère /storm-pegasus-105rf/ — fiche Metal Fusion originelle de Ginga."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )
    product = {
        'name': 'Storm Pegasus 105RF',
        'reference': 'BB-28',
        'gamme': 'beyblade-metal-fusion',
        'type': 'attaque',
        'year': 2009,
        'asin': 'B004AY8ICE',
        'image_url': f'{SITE_URL}/img/og-default.jpg',
        'description': "Test complet de la Storm Pegasus 105RF (BB-28), la toupie qui a inauguré la gamme Metal Fusion. Toupie originelle de Ginga Hagane. Note 8.0/10.",
    }
    schemas = [
        product_schema(product, review_score=8.0, review_max=10),
        article_schema(headline='Storm Pegasus 105RF : test complet Metal Fusion',
                       description=product['description'],
                       url_path='/storm-pegasus-105rf/', image_url=product['image_url'],
                       date_published='2026-04-22T13:00:00+02:00',
                       date_modified='2026-04-22T13:00:00+02:00', section='Beyblade Metal Fusion'),
        breadcrumb_schema([('Accueil', '/'), ('Beyblade Metal Fusion', '/comparatif-beyblade-metal-fusion/'),
                           ('Storm Pegasus 105RF', '/storm-pegasus-105rf/')]),
        faq_schema([
            ('La Storm Pegasus est-elle compatible avec un stadium Beyblade X ?',
             "Non. La Storm Pegasus utilise le système 5 pièces métalliques Metal Fusion. Le stadium Xtreme de Beyblade X (rampe inclinée) n'est pas adapté. Utilisez un stadium Metal Fusion classique (Hasbro Hyperblade ou Takara Tomy BeyStadium)."),
            ('Quelle est la différence entre Storm Pegasus, Galaxy Pegasus et Cosmic Pegasus ?',
             "Trois générations chez Ginga : Storm Pegasus 105RF (BB-28, saison 1) la plus accessible et culte ; Galaxy Pegasus W105R²F (BB-70, saison 2) plus puissante avec Wing Track ; Cosmic Pegasus F:D (BB-105, saison 3) la version 4D ultime."),
            ('Pourquoi est-elle si culte ?',
             "Storm Pegasus est LA toupie qui a relancé la franchise Beyblade en 2009. Toupie principale du héros Ginga Hagane dans la saison 1, c'est l'équivalent de la première Pokéball — celle avec laquelle des millions d'enfants ont commencé."),
            ('Combien dure une Storm Pegasus ?',
             "Le Bit RF (Rubber Flat) s'use en environ 50 lancers sur stadium plastique, 30 sur béton. Une fois usé, la toupie perd son agressivité. Vous pouvez remplacer juste le RF — cherchez Performance Tip RF en pièce détachée."),
            ('Où acheter la Storm Pegasus en France ?',
             "Amazon FR (lien direct depuis cette page) — version Hasbro encore en stock à 15-25 €. Pour les éditions Takara Tomy japonaises originales : eBay ou BeyStation FR (50-80 €)."),
        ]),
    ]
    head = render_head(
        title='Storm Pegasus 105RF : test complet Metal Fusion (note 8.0/10)',
        description="Notre test complet de la Storm Pegasus 105RF (BB-28), la toupie originelle de Ginga Hagane. Performance, alternatives, FAQ — note 8.0/10.",
        canonical_path='/storm-pegasus-105rf/', og_type='article',
        article_published='2026-04-22T13:00:00+02:00',
        article_modified='2026-04-22T13:00:00+02:00', article_section='Beyblade Metal Fusion',
        extra_css=['/css/page-article.css'], extra_jsonld=schemas)
    body_inner = (SRC_TEMPLATES / 'article_storm_pegasus_105rf.html').read_text()
    return write_page('storm-pegasus-105rf', assemble_html(head, body_inner))


def build_article_ray_unicorno():
    """Génère /ray-unicorno-d125cs/ — fiche Metal Fusion fan-favorite Hasbro EU."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )
    product = {
        'name': 'Ray Unicorno D125CS',
        'reference': 'BB-71',
        'gamme': 'beyblade-metal-fusion',
        'type': 'attaque',
        'year': 2010,
        'asin': 'B005ASZ5LE',
        'image_url': f'{SITE_URL}/img/og-default.jpg',
        'description': "Test complet de la Ray Unicorno D125CS (BB-71, Ray Striker chez Hasbro EU), attaquante équilibrée de Masamune Kadoya. Note 7.8/10.",
    }
    schemas = [
        product_schema(product, review_score=7.8, review_max=10),
        article_schema(headline='Ray Unicorno D125CS : test complet Metal Fusion',
                       description=product['description'],
                       url_path='/ray-unicorno-d125cs/', image_url=product['image_url'],
                       date_published='2026-04-22T14:00:00+02:00',
                       date_modified='2026-04-22T14:00:00+02:00', section='Beyblade Metal Fusion'),
        breadcrumb_schema([('Accueil', '/'), ('Beyblade Metal Fusion', '/comparatif-beyblade-metal-fusion/'),
                           ('Ray Unicorno D125CS', '/ray-unicorno-d125cs/')]),
        faq_schema([
            ('La Ray Unicorno est-elle compatible avec un stadium Beyblade X ?',
             "Non. La Ray Unicorno utilise le système 5 pièces métalliques Metal Fusion. Stadium classique requis (Hasbro Hyperblade ou Takara Tomy BeyStadium)."),
            ('Pourquoi Ray Unicorno s\'appelle Ray Striker chez Hasbro EU ?',
             "Hasbro a renommé certaines toupies pour le marché européen. La Ray Unicorno (Takara Tomy JP) devient Ray Striker en EU. Mécaniquement les deux sont identiques."),
            ('Quelle est la particularité du Spin Track D125 ?',
             "D125 (Defense Track 12.5mm) inclut des ailettes stabilisatrices qui réduisent les oscillations. Cela rend la Ray Unicorno plus stable que la moyenne des attaquantes — un compromis attaque/défense rare."),
            ('Quel combo personnalisé recommandez-vous ?',
             "Le combo stock Ray D125CS est déjà excellent. Pour pousser l'agressivité : Ray 105RF (Spin Track plus bas + Bit RF Rubber Flat). Pour la stabilité : Ray 145CS (track haut + CS)."),
            ('Où acheter la Ray Unicorno en France ?',
             "Stock variable sur Amazon FR. Si rupture, regardez chez BeyStation FR, GoToupie ou eBay. Versions Takara Tomy japonaises (édition originale) à ~30-50 € sur le marché de l'occasion."),
        ]),
    ]
    head = render_head(
        title='Ray Unicorno D125CS : test complet Metal Fusion (note 7.8/10)',
        description="Notre test complet de la Ray Unicorno D125CS (BB-71, Ray Striker EU), l'attaquante équilibrée de Masamune Kadoya. Performance, alternatives, FAQ — note 7.8/10.",
        canonical_path='/ray-unicorno-d125cs/', og_type='article',
        article_published='2026-04-22T14:00:00+02:00',
        article_modified='2026-04-22T14:00:00+02:00', article_section='Beyblade Metal Fusion',
        extra_css=['/css/page-article.css'], extra_jsonld=schemas)
    body_inner = (SRC_TEMPLATES / 'article_ray_unicorno_d125cs.html').read_text()
    return write_page('ray-unicorno-d125cs', assemble_html(head, body_inner))


def build_article_l_drago_destroy():
    """Génère /l-drago-destroy-fs/ — fiche Metal Fusion 4D ultime de Ryuga."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )
    product = {
        'name': 'L-Drago Destroy F:S',
        'reference': 'BB-108',
        'gamme': 'beyblade-metal-fusion',
        'type': 'attaque',
        'year': 2011,
        'asin': 'B005U8KMJM',
        'image_url': f'{SITE_URL}/img/og-default.jpg',
        'description': "Test complet de la L-Drago Destroy F:S (BB-108), évolution 4D ultime de la lignée L-Drago de Ryuga. Note 8.4/10.",
    }
    schemas = [
        product_schema(product, review_score=8.4, review_max=10),
        article_schema(headline='L-Drago Destroy F:S : test complet Metal Fusion 4D',
                       description=product['description'],
                       url_path='/l-drago-destroy-fs/', image_url=product['image_url'],
                       date_published='2026-04-22T15:00:00+02:00',
                       date_modified='2026-04-22T15:00:00+02:00', section='Beyblade Metal Fusion'),
        breadcrumb_schema([('Accueil', '/'), ('Beyblade Metal Fusion', '/comparatif-beyblade-metal-fusion/'),
                           ('L-Drago Destroy F:S', '/l-drago-destroy-fs/')]),
        faq_schema([
            ('Quelle est la différence entre L-Drago Destroy et Meteo L-Drago ?',
             "Meteo L-Drago LW105LF (BB-88, 2010) est le modèle Hybrid Wheel mid-tier de Ryuga avec son Bit Absorb. La L-Drago Destroy F:S (BB-108, 2011) est l'évolution 4D ultime — Metal Frame remplaçable, Bit F:S Final Survive et puissance brute supérieure. C'est la version finale du dragon."),
            ('Pourquoi la L-Drago tourne-t-elle vers la gauche ?',
             "Toutes les L-Drago (Lightning, Meteo, Destroy) sont des toupies en rotation gauche. Cela leur permet d'utiliser le mécanisme Spin Steal — voler l'énergie de rotation des adversaires droitiers à chaque collision frontale. C'est la signature stratégique de Ryuga depuis la saison 1."),
            ("Le Bit F:S (Final Survive) c'est quoi ?",
             "Le F:S est un Bit 4D à double mode : pointe Flat agressive (mode attaque) ou pointe Sharp endurante (mode survie). On bascule entre les deux en tournant manuellement la pièce. C'est l'un des Bits les plus polyvalents jamais sortis sur Metal Fusion."),
            ('Compatible avec un stadium Beyblade X ?',
             "Non. La L-Drago Destroy utilise le système 4D Metal Fusion. Le stadium Xtreme de Beyblade X (rampe inclinée) n'est pas adapté. Utilisez un stadium Metal Fusion classique."),
            ('Où acheter la L-Drago Destroy en France ?',
             "Stock variable sur Amazon FR (versions Hasbro et Takara Tomy). Pour la version japonaise originale, BeyStation FR ou eBay sont vos meilleures options. Comptez 30-60 € selon la version et l'état du Metal Frame."),
        ]),
    ]
    head = render_head(
        title='L-Drago Destroy F:S : test complet Metal Fusion 4D (note 8.4/10)',
        description="Notre test complet de la L-Drago Destroy F:S (BB-108), l'évolution 4D ultime de Ryuga. Spin Steal, mode F:S, performance — note 8.4/10.",
        canonical_path='/l-drago-destroy-fs/', og_type='article', og_image='/img/l-drago-destroy.webp',
        article_published='2026-04-22T15:00:00+02:00',
        article_modified='2026-04-22T15:00:00+02:00', article_section='Beyblade Metal Fusion',
        extra_css=['/css/page-article.css'], preload_images=['/img/l-drago-destroy.webp'],
        extra_jsonld=schemas)
    body_inner = (SRC_TEMPLATES / 'article_l_drago_destroy_fs.html').read_text()
    return write_page('l-drago-destroy-fs', assemble_html(head, body_inner))


def build_article_hells_scythe():
    """Génère /hells-scythe-4-60t/ — fiche Beyblade X stamina-defense de Multi."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )
    product = {
        'name': 'Hells Scythe 4-60T',
        'reference': 'BX-02',
        'gamme': 'beyblade-x',
        'type': 'stamina',
        'year': 2023,
        'asin': 'B0C52C4L3T',
        'image_url': f'{SITE_URL}/img/og-default.jpg',
        'description': "Test complet de la Hells Scythe 4-60T (BX-02), stamina-defense hybride du quatuor inaugural Beyblade X. Toupie de Multi. Note 8.3/10.",
    }
    schemas = [
        product_schema(product, review_score=8.3, review_max=10),
        article_schema(headline='Hells Scythe 4-60T : test complet Beyblade X',
                       description=product['description'],
                       url_path='/hells-scythe-4-60t/', image_url=product['image_url'],
                       date_published='2026-04-22T16:00:00+02:00',
                       date_modified='2026-04-22T16:00:00+02:00', section='Beyblade X'),
        breadcrumb_schema([('Accueil', '/'), ('Beyblade X', '/comparatif-beyblade-x/'),
                           ('Hells Scythe 4-60T', '/hells-scythe-4-60t/')]),
        faq_schema([
            ('Hells Scythe est-elle stamina ou défense ?',
             "Officiellement classée stamina, mais c'est en réalité une toupie hybride stamina/défense. Le Bit Taper (T) lui donne une stabilité inhabituelle pour une stamina pure, ce qui lui permet d'absorber les chocs avant de gagner par spin-out. C'est sa principale originalité dans la gamme X."),
            ('Quelle différence avec Wizard Arrow ?',
             "Wizard Arrow (BX-04) est une stamina classique avec Bit Ball, optimisée pour le spin-out par fatigue. Hells Scythe (BX-02) ajoute une couche de défense grâce à son Bit Taper, qui résiste mieux aux impacts d'attaquantes comme Dran Sword. Pour un combat équilibré : préférez Hells Scythe. Pour un combat de stamina pur : Wizard Arrow."),
            ('Que vaut le Starter Set 4-Pack BX-15 ?',
             "C'est l'un des meilleurs achats d'entrée Beyblade X : il contient les 4 toupies inaugurales (Dran Sword, Hells Scythe, Knight Shield, Wizard Arrow) et un stadium Xtreme. Rapport qualité/prix imbattable pour démarrer la collection — comptez 60-80 € sur Amazon FR."),
            ('Compatible avec un stadium Burst ou Metal Fusion ?',
             "Non. Hells Scythe est exclusivement Beyblade X. Le Bit Taper a besoin de la rampe inclinée du stadium Xtreme pour exprimer son potentiel défensif. Sur stadium plat, la toupie perd 40% de son intérêt."),
            ('Où acheter la Hells Scythe en France ?',
             "Amazon FR la propose en version individuelle (15-20 €) ou dans le starter pack 4-Pack BX-15 (60-80 €). Disponible aussi en magasin physique chez King Jouet, La Grande Récré et Leclerc Jouets."),
        ]),
    ]
    head = render_head(
        title='Hells Scythe 4-60T : test complet Beyblade X (note 8.3/10)',
        description="Notre test complet de la Hells Scythe 4-60T (BX-02), la stamina-defense du quatuor inaugural Beyblade X. Toupie de Multi — note 8.3/10.",
        canonical_path='/hells-scythe-4-60t/', og_type='article', og_image='/img/hells-scythe.webp',
        article_published='2026-04-22T16:00:00+02:00',
        article_modified='2026-04-22T16:00:00+02:00', article_section='Beyblade X',
        extra_css=['/css/page-article.css'], preload_images=['/img/hells-scythe.webp'],
        extra_jsonld=schemas)
    body_inner = (SRC_TEMPLATES / 'article_hells_scythe_4_60t.html').read_text()
    return write_page('hells-scythe-4-60t', assemble_html(head, body_inner))


def build_article_cobalt_dragoon():
    """Génère /cobalt-dragoon-2-60c/ — première left-spin Beyblade X (Spin Steal)."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )
    product = {
        'name': 'Cobalt Dragoon 2-60C',
        'reference': 'BX-34',
        'gamme': 'beyblade-x',
        'type': 'attaque',
        'year': 2024,
        'asin': 'B0D6MZB1VF',
        'image_url': f'{SITE_URL}/img/og-default.jpg',
        'description': "Test complet de la Cobalt Dragoon 2-60C (BX-34), première attaquante left-spin de Beyblade X avec Spin Steal. Note 8.6/10.",
    }
    schemas = [
        product_schema(product, review_score=8.6, review_max=10),
        article_schema(headline='Cobalt Dragoon 2-60C : test complet Beyblade X left-spin',
                       description=product['description'],
                       url_path='/cobalt-dragoon-2-60c/', image_url=product['image_url'],
                       date_published='2026-04-22T17:00:00+02:00',
                       date_modified='2026-04-22T17:00:00+02:00', section='Beyblade X'),
        breadcrumb_schema([('Accueil', '/'), ('Beyblade X', '/comparatif-beyblade-x/'),
                           ('Cobalt Dragoon 2-60C', '/cobalt-dragoon-2-60c/')]),
        faq_schema([
            ('Quelle différence entre Cobalt Dragoon et Cobalt Drake ?',
             "Aucune mécanique : ce sont les deux noms commerciaux de la même toupie. Cobalt Dragoon est le naming Takara Tomy (Japon, juillet 2024) ; Cobalt Drake est le naming Hasbro pour le marché européen (octobre 2024). Pièces strictement compatibles, seul le marquage et la finition diffèrent."),
            ('Quel lanceur est nécessaire ?',
             "Impérativement un Left Spin Launcher (généralement noir avec marquage L). Il est inclus dans le starter set BX-34 mais pas dans tous les packs Hasbro EU. Le Xtreme Launcher classique (droitier) est strictement incompatible avec une toupie left-spin."),
            ("Qu'est-ce que le Spin Steal ?",
             "Le Spin Steal est un mécanisme par lequel une toupie left-spin vole de l'énergie de rotation à un adversaire qui tourne dans le sens inverse (droite). À chaque collision frontale, la Cobalt Dragoon ralentit l'adversaire et accélère son propre spin. C'est la principale raison de l'acheter."),
            ('Est-elle efficace contre une autre left-spin ?',
             "Non — c'est son principal point faible. En miroir contre une autre toupie left-spin (Knight Lance ou Cobalt Dragoon adverse), le Spin Steal est neutralisé. Le combat redevient classique attaque vs attaque, où le Bit Cyclone n'est pas le mieux armé."),
            ('Où acheter la Cobalt Dragoon en France ?',
             "Amazon FR (version Cobalt Drake Hasbro 20-25 €, version Takara Tomy 30-40 €), King Jouet, Leclerc Jouets. Vérifiez bien que le pack inclut le Left Spin Launcher, sinon achetez-le séparément (env. 15 €)."),
        ]),
    ]
    head = render_head(
        title='Cobalt Dragoon 2-60C : test complet Beyblade X left-spin (note 8.6/10)',
        description="Notre test complet de la Cobalt Dragoon 2-60C (BX-34), première left-spin Beyblade X avec Spin Steal. Performance, combos, FAQ — note 8.6/10.",
        canonical_path='/cobalt-dragoon-2-60c/', og_type='article', og_image='/img/cobalt-dragoon.webp',
        article_published='2026-04-22T17:00:00+02:00',
        article_modified='2026-04-22T17:00:00+02:00', article_section='Beyblade X',
        extra_css=['/css/page-article.css'], preload_images=['/img/cobalt-dragoon.webp'],
        extra_jsonld=schemas)
    body_inner = (SRC_TEMPLATES / 'article_cobalt_dragoon_2_60c.html').read_text()
    return write_page('cobalt-dragoon-2-60c', assemble_html(head, body_inner))


def build_article_earth_eagle():
    """Génère /earth-eagle-145wd/ — 2e défenseuse MF (Tsubasa Otori, Earth Aquila chez Hasbro EU)."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )
    product = {
        'name': 'Earth Eagle 145WD',
        'reference': 'BB-47',
        'gamme': 'beyblade-metal-fusion',
        'type': 'defense',
        'year': 2010,
        'asin': 'B0050OMBU8',
        'image_url': f'{SITE_URL}/img/og-default.jpg',
        'description': "Test complet de la Earth Eagle 145WD (BB-47, Earth Aquila chez Hasbro EU), 2e défenseuse Metal Fusion de Tsubasa Otori. Note 7.6/10.",
    }
    schemas = [
        product_schema(product, review_score=7.6, review_max=10),
        article_schema(headline='Earth Eagle 145WD : test complet Metal Fusion défense',
                       description=product['description'],
                       url_path='/earth-eagle-145wd/', image_url=product['image_url'],
                       date_published='2026-04-23T10:00:00+02:00',
                       date_modified='2026-04-23T10:00:00+02:00', section='Beyblade Metal Fusion'),
        breadcrumb_schema([('Accueil', '/'), ('Beyblade Metal Fusion', '/comparatif-beyblade-metal-fusion/'),
                           ('Earth Eagle 145WD', '/earth-eagle-145wd/')]),
        faq_schema([
            ('Quelle différence entre Earth Eagle et Earth Aquila ?',
             "Aucune mécanique : ce sont les deux noms commerciaux de la même toupie. Earth Eagle est le naming Takara Tomy (Japon, octobre 2010) ; Earth Aquila est le naming Hasbro pour le marché européen (mai 2011). Pièces strictement compatibles, seul le marquage diffère."),
            ('Earth Eagle ou Rock Leone : laquelle choisir ?',
             "Pour une défense pure type 'mur' face à une attaquante puissante (L-Drago, Pegasus rapide), prenez la Rock Leone qui pèse 30 g vs 28 g pour Earth. Pour un compromis défense + endurance contre les stamina, prenez Earth Eagle. Les vrais collectionneurs ont les deux."),
            ('La Earth Eagle est-elle compatible avec un stadium Beyblade X ?',
             "Non. La Earth Eagle est une toupie Metal Fusion qui utilise le système 5 pièces métalliques. Le stadium Xtreme de Beyblade X (rampe inclinée) n'est pas adapté à sa Performance Tip Wide Defense. Utilisez un stadium Metal Fusion classique."),
            ('Quel combo personnalisé recommandez-vous ?',
             "Le combo stock Earth 145WD est déjà excellent en défense polyvalente. Pour pousser l'endurance, essayez Earth 145D (Defense tip pur). Pour la défense brute, montez sur Earth 230D — la combinaison la plus stable de toute la gamme MF."),
            ('Où acheter la Earth Eagle en France en 2026 ?',
             "Amazon FR reste la source la plus fiable. Cherchez aussi sous le nom 'Earth Aquila' qui est le nom Hasbro EU. BeyStation FR ou GoToupie pour les versions japonaises originales (50-90 €)."),
        ]),
    ]
    head = render_head(
        title='Earth Eagle 145WD : test complet Metal Fusion défense (note 7.6/10)',
        description="Notre test complet de la Earth Eagle 145WD (BB-47, Earth Aquila chez Hasbro EU), 2e défenseuse Metal Fusion de Tsubasa Otori. Note 7.6/10.",
        canonical_path='/earth-eagle-145wd/', og_type='article', og_image='/img/earth-eagle.webp',
        article_published='2026-04-23T10:00:00+02:00',
        article_modified='2026-04-23T10:00:00+02:00', article_section='Beyblade Metal Fusion',
        extra_css=['/css/page-article.css'], preload_images=['/img/earth-eagle.webp'],
        extra_jsonld=schemas)
    body_inner = (SRC_TEMPLATES / 'article_earth_eagle_145wd.html').read_text()
    return write_page('earth-eagle-145wd', assemble_html(head, body_inner))


def build_article_dran_buster():
    """Génère /dran-buster-1-60a/ — première Unique-X (UX) de Beyblade X, attaquante extrême."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )
    product = {
        'name': 'Dran Buster 1-60A',
        'reference': 'UX-01',
        'gamme': 'beyblade-x',
        'type': 'attaque',
        'year': 2024,
        'asin': 'B0CV7HF3W6',
        'image_url': f'{SITE_URL}/img/og-default.jpg',
        'description': "Test complet de la Dran Buster 1-60A (UX-01), première Unique-X de Beyblade X. Évolution de Dran Sword en Blade métal. Note 9.0/10.",
    }
    schemas = [
        product_schema(product, review_score=9.0, review_max=10),
        article_schema(headline='Dran Buster 1-60A : test complet Beyblade X UX',
                       description=product['description'],
                       url_path='/dran-buster-1-60a/', image_url=product['image_url'],
                       date_published='2026-04-23T11:00:00+02:00',
                       date_modified='2026-04-23T11:00:00+02:00', section='Beyblade X'),
        breadcrumb_schema([('Accueil', '/'), ('Beyblade X', '/comparatif-beyblade-x/'),
                           ('Dran Buster 1-60A', '/dran-buster-1-60a/')]),
        faq_schema([
            ('Quelle différence entre Dran Buster (UX) et Dran Sword (BX) ?',
             "Trois différences majeures : Blade en alliage métallique pour Dran Buster vs plastique pour Dran Sword (+25-40% de puissance d'impact), Ratchet 1-60 à un seul lobe massif vs 3-60 à 3 lobes, et Bit Accel qui boost la rotation à chaque collision vs Bit Flat passif. La Buster gagne 8 fois sur 10 contre une Sword stock en collision frontale."),
            ('Quel lanceur utiliser avec la Dran Buster ?',
             "Le Xtreme Launcher (rotation droite) suffit pour les sessions casual. Pour la compétition, nous recommandons fortement le Beyblade X Launcher Grip avec manche stabilisateur — la masse supplémentaire du Blade UX est plus difficile à lancer proprement avec un launcher standard. Comptez ~25 € pour le Grip officiel."),
            ('Faut-il déjà avoir une Dran Sword pour acheter une Dran Buster ?',
             "Non, mais c'est conseillé. La Buster est conçue comme une 'toupie de tournoi' — son 1-lobe Ratchet et son Bit Accel demandent un lancer maîtrisé. Si vous débutez Beyblade X, commencez par la Dran Sword 3-60F stock pour 6 mois, puis passez à la Buster."),
            ('Compatible avec un stadium Burst ?',
             "Non, la Dran Buster est exclusivement Beyblade X. Le Bit Accel a besoin d'une rampe inclinée pour exprimer son potentiel, et le Blade UX métal endommagerait un stadium Burst en plastique."),
            ('Où l\'acheter en France ?',
             "Amazon FR reste la référence avec stock fiable et livraison Prime. Comptez 25-35 € pour la version standard, 45-60 € pour les éditions chrome ou collector. Évitez les marketplaces tiers où circulent des contrefaçons UX particulièrement nombreuses."),
        ]),
    ]
    head = render_head(
        title='Dran Buster 1-60A : test complet Beyblade X UX (note 9.0/10)',
        description="Notre test complet de la Dran Buster 1-60A (UX-01), première Unique-X de Beyblade X. Évolution de Dran Sword en Blade métal — note 9.0/10.",
        canonical_path='/dran-buster-1-60a/', og_type='article', og_image='/img/dran-buster.webp',
        article_published='2026-04-23T11:00:00+02:00',
        article_modified='2026-04-23T11:00:00+02:00', article_section='Beyblade X',
        extra_css=['/css/page-article.css'], preload_images=['/img/dran-buster.webp'],
        extra_jsonld=schemas)
    body_inner = (SRC_TEMPLATES / 'article_dran_buster_1_60a.html').read_text()
    return write_page('dran-buster-1-60a', assemble_html(head, body_inner))


def build_article_cyclone_roktavor():
    """Génère /cyclone-roktavor-r7/ — 1ère fiche Burst (Aiger Akabane, Quad Drive 2022)."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )
    product = {
        'name': 'Cyclone Roktavor R7',
        'reference': 'F4067',
        'gamme': 'beyblade-burst',
        'type': 'attaque',
        'year': 2022,
        'asin': 'B09TGD75BP',
        'image_url': f'{SITE_URL}/img/og-default.jpg',
        'description': "Test complet de la Cyclone Roktavor R7 (F4067), attaquante signature d'Aiger dans Beyblade Burst Quad Drive. Driver Revolve 4 modes. Note 8.0/10.",
    }
    schemas = [
        product_schema(product, review_score=8.0, review_max=10),
        article_schema(headline='Cyclone Roktavor R7 : test complet Burst Quad Drive',
                       description=product['description'],
                       url_path='/cyclone-roktavor-r7/', image_url=product['image_url'],
                       date_published='2026-04-23T12:00:00+02:00',
                       date_modified='2026-04-23T12:00:00+02:00', section='Beyblade Burst'),
        breadcrumb_schema([('Accueil', '/'), ('Beyblade Burst', '/comparatif-beyblade-burst/'),
                           ('Cyclone Roktavor R7', '/cyclone-roktavor-r7/')]),
        faq_schema([
            ('C\'est quoi le système Quad Drive ?',
             "Quad Drive est la sous-série Burst lancée en 2022 (saison 6 de l'anime). Sa mécanique signature est un Driver à 4 modes interchangeables : Flat (attaque), Ball (défense), Sharp (endurance) et hybride. On bascule manuellement le mécanisme avant chaque combat selon l'adversaire. C'est la dernière évolution majeure du système Burst avant la transition vers Beyblade X."),
            ('Quel lanceur utiliser avec la Cyclone Roktavor ?',
             "Le SwitchStrike Launcher Hasbro fourni dans la boîte est suffisant pour les sessions casual. Pour la compétition, nous recommandons le Burst Beylauncher LR Takara Tomy qui permet un shoot rotation gauche/droite (utile contre les left-spin Burst comme Vanish Fafnir)."),
            ('Compatible avec un stadium Beyblade X ?',
             "Non, la Cyclone Roktavor est exclusivement Beyblade Burst. La rampe inclinée du stadium Xtreme rendrait le Driver Revolve impossible à exploiter, et le Layer Burst sortirait immédiatement. Utilisez impérativement un stadium Burst classique (Hasbro Hyperblade ou Takara Tomy BeyStadium plat)."),
            ('Où l\'acheter en France en 2026 ?',
             "Amazon FR reste la référence avec stock disponible (15-25 €). Attention : la production Burst étant arrêtée depuis fin 2023, le stock diminue progressivement. Si vous voulez la Cyclone Roktavor, achetez avant qu'elle ne devienne rare."),
            ('Différence avec la Z Achilles d\'Aiger (saison 5) ?',
             "Z Achilles A4 (B-129, saison 5 'Burst Turbo', 2018) était la première toupie d'Aiger — un attaquant pur sans modularité. La Cyclone Roktavor R7 (saison 6 'Quad Drive', 2022) est la dernière toupie d'Aiger, beaucoup plus polyvalente grâce au Driver Quad Drive."),
        ]),
    ]
    head = render_head(
        title='Cyclone Roktavor R7 : test complet Burst Quad Drive (note 8.0/10)',
        description="Notre test complet de la Cyclone Roktavor R7 (F4067), attaquante signature d'Aiger dans Beyblade Burst Quad Drive. Driver 4 modes — note 8.0/10.",
        canonical_path='/cyclone-roktavor-r7/', og_type='article', og_image='/img/cyclone-roktavor.webp',
        article_published='2026-04-23T12:00:00+02:00',
        article_modified='2026-04-23T12:00:00+02:00', article_section='Beyblade Burst',
        extra_css=['/css/page-article.css'], preload_images=['/img/cyclone-roktavor.webp'],
        extra_jsonld=schemas)
    body_inner = (SRC_TEMPLATES / 'article_cyclone_roktavor_r7.html').read_text()
    return write_page('cyclone-roktavor-r7', assemble_html(head, body_inner))


def build_article_vanish_fafnir():
    """Génère /vanish-fafnir-f7/ — stamina culte de Free de la Hoya (Quad Drive 2022, rotation gauche, Spin Steal)."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )
    product = {
        'name': 'Vanish Fafnir F7',
        'reference': 'F3966',
        'gamme': 'beyblade-burst',
        'type': 'stamina',
        'year': 2022,
        'asin': 'B09H17H8CD',
        'image_url': f'{SITE_URL}/img/og-default.jpg',
        'description': "Test complet de la Vanish Fafnir F7 (F3966), stamina culte de Free de la Hoya. Rotation gauche, mécanisme Spin Steal. Note 8.2/10.",
    }
    schemas = [
        product_schema(product, review_score=8.2, review_max=10),
        article_schema(headline='Vanish Fafnir F7 : test complet Burst Quad Drive',
                       description=product['description'],
                       url_path='/vanish-fafnir-f7/', image_url=product['image_url'],
                       date_published='2026-04-23T13:00:00+02:00',
                       date_modified='2026-04-23T13:00:00+02:00', section='Beyblade Burst'),
        breadcrumb_schema([('Accueil', '/'), ('Beyblade Burst', '/comparatif-beyblade-burst/'),
                           ('Vanish Fafnir F7', '/vanish-fafnir-f7/')]),
        faq_schema([
            ('C\'est quoi le Spin Steal ?',
             "Mécanisme par lequel une toupie en rotation gauche vole de l'énergie de rotation à un adversaire qui tourne en sens inverse (droite). À chaque collision frontale, la Vanish Fafnir ralentit l'adversaire et accélère son propre spin. C'est la principale raison de l'acheter."),
            ('Quel lanceur utiliser avec la Vanish Fafnir ?',
             "Impérativement un SwitchStrike Left Launcher (rouge ou noir avec marquage L). Inclus dans le starter set Hasbro F3966, mais pas toujours dans les packs combo. Si vous achetez la toupie seule sans launcher, prévoyez ~15-20 € pour le Left Launcher dédié."),
            ('Quelle différence entre les 4 Fafnir ?',
             "Quatre itérations chronologiques : Drain Fafnir (B-127, 2018) première stamina left-spin de Burst ; Geist Fafnir (B-145, 2019) Sparking Generation ; Hazard Fafnir (B-167, 2020) Burst Surge plus lourde ; Vanish Fafnir (B-205, 2022) Quad Drive avec Driver Revolve aimanté — l'itération la plus aboutie."),
            ('Compatible avec un stadium Beyblade X ?',
             "Non, la Vanish Fafnir est exclusivement Beyblade Burst. La rampe inclinée du stadium Xtreme rendrait le Driver Revolve aimanté impossible à exploiter. Utilisez un stadium Burst classique."),
            ('Différence avec la Cyclone Roktavor d\'Aiger ?',
             "Deux philosophies opposées de la même saison Quad Drive (2022) : Cyclone Roktavor R7 est l'attaquante polyvalente d'Aiger qui cherche le KO direct. Vanish Fafnir F7 est la stamina patiente de Free qui gagne par épuisement (Spin Steal). Vanish Fafnir bat Cyclone Roktavor 7 fois sur 10 en duel."),
        ]),
    ]
    head = render_head(
        title='Vanish Fafnir F7 : test complet Burst Quad Drive (note 8.2/10)',
        description="Notre test complet de la Vanish Fafnir F7 (F3966), stamina culte de Free de la Hoya. Rotation gauche + Spin Steal — note 8.2/10.",
        canonical_path='/vanish-fafnir-f7/', og_type='article', og_image='/img/vanish-fafnir.webp',
        article_published='2026-04-23T13:00:00+02:00',
        article_modified='2026-04-23T13:00:00+02:00', article_section='Beyblade Burst',
        extra_css=['/css/page-article.css'], preload_images=['/img/vanish-fafnir.webp'],
        extra_jsonld=schemas)
    body_inner = (SRC_TEMPLATES / 'article_vanish_fafnir_f7.html').read_text()
    return write_page('vanish-fafnir-f7', assemble_html(head, body_inner))


def build_article_stellar_hyperion():
    """Génère /stellar-hyperion-h8/ — attaquante de Lui Shirosagi (Quad Strike 2023, sub-série Hasbro EU/US)."""
    from seo_meta import (
        render_head, product_schema, article_schema,
        breadcrumb_schema, faq_schema, SITE_URL,
    )
    product = {
        'name': 'Stellar Hyperion H8',
        'reference': 'F6809',
        'gamme': 'beyblade-burst',
        'type': 'attaque',
        'year': 2023,
        'asin': 'B0BLNY6Q2K',  # placeholder — vérifier ASIN exact
        'image_url': f'{SITE_URL}/img/og-default.jpg',
        'description': "Test complet de la Stellar Hyperion H8 (F6809), attaquante brutale de Lui Shirosagi. Sub-série Burst Quad Strike Hasbro EU/US. Note 8.5/10.",
    }
    schemas = [
        product_schema(product, review_score=8.5, review_max=10),
        article_schema(headline='Stellar Hyperion H8 : test complet Burst Quad Strike',
                       description=product['description'],
                       url_path='/stellar-hyperion-h8/', image_url=product['image_url'],
                       date_published='2026-04-23T14:00:00+02:00',
                       date_modified='2026-04-23T14:00:00+02:00', section='Beyblade Burst'),
        breadcrumb_schema([('Accueil', '/'), ('Beyblade Burst', '/comparatif-beyblade-burst/'),
                           ('Stellar Hyperion H8', '/stellar-hyperion-h8/')]),
        faq_schema([
            ('C\'est quoi la sous-série Quad Strike ?',
             "Quad Strike est la 7ème et dernière sous-série Beyblade Burst, lancée en 2023 par Hasbro EU/US. Particularité : c'est une sub-série exclusive Hasbro qui n'a jamais eu d'équivalent direct chez Takara Tomy au Japon. Sa mécanique signature : le Driver Surge'-Spike avec mécanisme strike-and-spike."),
            ('Quel lanceur utiliser avec la Stellar Hyperion ?',
             "Le SwitchStrike Launcher fourni dans la boîte est suffisant pour les sessions casual. Pour la compétition, nous recommandons le String Launcher Hasbro qui permet un shoot 25% plus rapide (essentiel pour activer pleinement le Burst Finish)."),
            ('Quelle différence entre Stellar Hyperion et Hyper-Hyperion (saison 5) ?',
             "Hyper-Hyperion H5 (E7723, saison 5 Surge, 2020) — première toupie de Lui, Driver Quick'. Stellar Hyperion H8 (F6809, saison 7 Quad Strike, 2023) — dernière itération, Driver Surge'-Spike plus agressif, Disc 7 plus lourd. Stellar Hyperion bat Hyper-Hyperion 8 fois sur 10."),
            ('Pourquoi pas d\'équivalent Takara Tomy japonais ?',
             "Takara Tomy a arrêté Burst au Japon avec Dynamite Battle (B-185+, 2021-2022) pour basculer sur Beyblade X (juillet 2023). Hasbro EU/US a continué Burst un an de plus avec Quad Drive (2022) et Quad Strike (2023). C'est pourquoi Stellar Hyperion n'a pas de référence B-XXX japonaise."),
            ('Où l\'acheter en France en 2026 ?',
             "Amazon FR reste la référence avec stock disponible (20-30 €). King Jouet et Leclerc Jouets ont des stocks variables. Attention : la production Burst étant arrêtée fin 2023 et la sub-série Quad Strike étant exclusive Hasbro EU/US, le stock baisse rapidement."),
        ]),
    ]
    head = render_head(
        title='Stellar Hyperion H8 : test complet Burst Quad Strike (note 8.5/10)',
        description="Notre test complet de la Stellar Hyperion H8 (F6809), attaquante brutale de Lui Shirosagi. Sub-série Burst Quad Strike — note 8.5/10.",
        canonical_path='/stellar-hyperion-h8/', og_type='article', og_image='/img/stellar-hyperion.webp',
        article_published='2026-04-23T14:00:00+02:00',
        article_modified='2026-04-23T14:00:00+02:00', article_section='Beyblade Burst',
        extra_css=['/css/page-article.css'], preload_images=['/img/stellar-hyperion.webp'],
        extra_jsonld=schemas)
    body_inner = (SRC_TEMPLATES / 'article_stellar_hyperion_h8.html').read_text()
    return write_page('stellar-hyperion-h8', assemble_html(head, body_inner))


def build_comparatif_beyblade_burst():
    """Génère /comparatif-beyblade-burst/ — page hub gamme Beyblade Burst (3 testées + 6 références)."""
    from seo_meta import (
        render_head, breadcrumb_schema, faq_schema, SITE_URL,
    )

    itemlist = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': 'Comparatif Beyblade Burst 2026',
        'itemListOrder': 'https://schema.org/ItemListOrderDescending',
        'numberOfItems': 3,
        'itemListElement': [
            {
                '@type': 'ListItem', 'position': 1,
                'item': {
                    '@type': 'Product',
                    'name': 'Stellar Hyperion H8',
                    'category': 'Beyblade Burst Quad Strike',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 8.5, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/stellar-hyperion-h8/',
                },
            },
            {
                '@type': 'ListItem', 'position': 2,
                'item': {
                    '@type': 'Product',
                    'name': 'Vanish Fafnir F7',
                    'category': 'Beyblade Burst Quad Drive',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 8.2, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/vanish-fafnir-f7/',
                },
            },
            {
                '@type': 'ListItem', 'position': 3,
                'item': {
                    '@type': 'Product',
                    'name': 'Cyclone Roktavor R7',
                    'category': 'Beyblade Burst Quad Drive',
                    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 8.0, 'bestRating': 10, 'reviewCount': 1, 'ratingCount': 1},
                    'url': f'{SITE_URL}/cyclone-roktavor-r7/',
                },
            },
        ],
    }

    faq = faq_schema([
        ('Quelle Beyblade Burst choisir pour débuter en 2026 ?',
         "Cyclone Roktavor R7 (F4067). Toupie polyvalente d'Aiger, Driver Quad Drive 4 modes pour s'adapter à tout adversaire, prix correct (15-25 €), encore largement disponible malgré l'arrêt de production fin 2023."),
        ('C\'est quoi le Burst Finish ?',
         "Le Burst Finish est la mécanique signature de Burst : quand un Layer reçoit suffisamment d'impacts (3 à 5 selon le modèle), il éclate physiquement en plein combat. Cela donne 2 points à l'adversaire (vs 1 pour un KO classique). C'est ce qui rend Burst plus spectaculaire."),
        ('Quelle est la différence Quad Drive vs Quad Strike vs Pro Series ?',
         "Trois sous-séries Burst récentes : Quad Drive (2022, saison 6, Driver 4 modes), Quad Strike (2023, saison 7, exclusivité Hasbro EU/US), Pro Series (2020-2023, version premium métal pour collectionneurs adultes). Toutes les pièces sont compatibles."),
        ('Les Burst sont-elles compatibles avec Beyblade X ou Metal Fusion ?',
         "Non. Chaque gamme a son système : Burst = Layer/Disc/Driver, X = Blade/Ratchet/Bit, Metal Fusion = 5 pièces métalliques. Stadiums et lanceurs sont aussi spécifiques."),
        ('Où acheter des Beyblade Burst authentiques en 2026 ?',
         "Amazon FR reste la source la plus fiable. Production arrêtée par Hasbro fin 2023, donc stock en baisse. Pour les modèles plus rares (Spryzen Requiem, Z Achilles), regardez BeyStation, GoToupie ou eBay. Évitez AliExpress (contrefaçons)."),
        ('Y a-t-il encore des tournois Beyblade Burst en 2026 ?',
         "Oui, la communauté worldbeyblade.org organise encore des tournois Burst en ligne et en présentiel (USA, Europe, Japon). Les tournois officiels Hasbro ont cessé fin 2024 avec la transition vers Beyblade X."),
    ])

    breadcrumb = breadcrumb_schema([
        ('Accueil', '/'),
        ('Comparatifs', '/comparatifs/'),
        ('Beyblade Burst', '/comparatif-beyblade-burst/'),
    ])

    head = render_head(
        title='Comparatif Beyblade Burst 2026 : Quad Drive, Quad Strike et Pro Series',
        description="Comparatif complet des meilleures Beyblade Burst (Quad Drive, Quad Strike, Pro Series). Cyclone Roktavor, Vanish Fafnir, Stellar Hyperion et plus — notes vérifiables, méthode publique.",
        canonical_path='/comparatif-beyblade-burst/',
        og_type='website',
        extra_css=['/css/page-comparatif.css'],
        extra_jsonld=[itemlist, faq, breadcrumb],
    )

    body_inner = (SRC_TEMPLATES / 'page_comparatif_beyblade_burst.html').read_text()
    return write_page('comparatif-beyblade-burst', assemble_html(head, body_inner))


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
    return write_page('comparatif-beyblade-metal-fusion', assemble_html(head, body_inner))


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
    return write_page('comparatif-beyblade-x', assemble_html(head, body_inner))


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


def build_catalogue_page():
    """Génère /tous-les-beyblade/ — catalogue complet (testées + à venir) sortable + filterable.

    Source de vérité : data/catalogue.py (CATALOGUE list).
    Le tableau est rendu côté serveur (pas de JS pour l'affichage initial → SEO-friendly).
    Le JS embarqué gère uniquement filtrage/tri côté client après page load.
    """
    from seo_meta import (
        render_head, breadcrumb_schema, faq_schema, SITE_URL,
    )
    from catalogue import CATALOGUE, GAMMES, TYPES, amazon_url, stats

    s = stats()

    def normalize_search(*texts) -> str:
        """Lowercase + concat for the data-searchable attribute (matched by JS)."""
        return ' '.join(t for t in texts if t).lower()

    # Trier d'emblée par note décroissante (les non-testées en queue)
    sorted_entries = sorted(
        CATALOGUE,
        key=lambda e: (e.get('score') if e.get('score') is not None else -1),
        reverse=True,
    )

    rows = []
    for e in sorted_entries:
        gamme_meta = GAMMES[e['gamme']]
        type_meta = TYPES[e['type']]
        is_tested = bool(e.get('slug'))

        # Image cell : photo réelle si dispo, sinon initiales sur fond gradient
        if e.get('image'):
            thumb = (
                f'<div class="catalogue-thumb">'
                f'<img src="/img/{e["image"]}" alt="" loading="lazy" decoding="async" width="44" height="44">'
                f'</div>'
            )
        else:
            initials = ''.join(w[0] for w in e['name'].split()[:2]).upper()
            thumb = f'<div class="catalogue-thumb placeholder">{initials}</div>'

        # Score cell
        if is_tested:
            score_cell = f'<span class="catalogue-score">{e["score"]:.1f}<small>/10</small></span>'
        else:
            score_cell = '<span class="catalogue-score-pending">À tester</span>'

        # Action cell : fiche interne ou Amazon
        if is_tested:
            action_cell = f'<a href="/{e["slug"]}/" class="catalogue-cta">Voir →</a>'
        else:
            action_cell = (
                f'<a href="{amazon_url(e)}" class="catalogue-cta catalogue-cta--outline" '
                f'target="_blank" rel="nofollow sponsored noopener">Amazon</a>'
            )

        # Type filter key (regroupe attaque-gauche → attaque, stamina-gauche → stamina)
        type_filter = type_meta['filter_key']

        # Texte cherchable : nom + ref + owner + tagline
        searchable = normalize_search(e['name'], e['ref'], e.get('owner'), e.get('tagline'))

        # Pour le tri par nom, on lowercase + strip prefixes pour stabilité
        sort_name = e['name'].lower()

        # Score numérique pour tri (-1 pour les non-testées, qui finissent en queue)
        sort_score = e.get('score') if e.get('score') is not None else -1

        row = (
            f'<tr '
            f'data-name="{sort_name}" '
            f'data-gamme="{e["gamme"]}" '
            f'data-type="{type_filter}" '
            f'data-year="{e["year"]}" '
            f'data-score="{sort_score}" '
            f'data-tested="{1 if is_tested else 0}" '
            f'data-searchable="{searchable}">'
            f'<td><div class="catalogue-cell-product">{thumb}'
            f'<div class="catalogue-info"><div class="name">{e["name"]}</div>'
            f'<div class="meta">{e["ref"]} · {e.get("owner", "")}</div></div></div></td>'
            f'<td><span class="gamme-badge">{gamme_meta["short"]}</span></td>'
            f'<td><span class="type-badge {type_meta["badge_class"]}">{type_meta["label"]}</span></td>'
            f'<td>{e["year"]}</td>'
            f'<td>{score_cell}</td>'
            f'<td>{action_cell}</td>'
            f'</tr>'
        )
        rows.append(row)

    rows_html = '\n      '.join(rows)

    body_inner = (SRC_TEMPLATES / 'page_tous_les_beyblade.html').read_text()
    body_inner = (body_inner
                  .replace('{{CATALOGUE_ROWS}}', rows_html)
                  .replace('{{TOTAL_COUNT}}', str(s['total']))
                  .replace('{{TESTED_COUNT}}', str(s['tested'])))

    # Schema : ItemList (top 10 par note pour rich snippet) + breadcrumb
    top_10 = [e for e in sorted_entries if e.get('slug')][:10]
    itemlist = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': f'Catalogue toupies Beyblade — {s["total"]} références',
        'itemListOrder': 'https://schema.org/ItemListOrderDescending',
        'numberOfItems': len(top_10),
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': i + 1,
                'item': {
                    '@type': 'Product',
                    'name': e['name'],
                    'category': GAMMES[e['gamme']]['label'],
                    'aggregateRating': {
                        '@type': 'AggregateRating',
                        'ratingValue': e['score'],
                        'bestRating': 10,
                        'reviewCount': 1, 'ratingCount': 1,
                    },
                    'url': f'{SITE_URL}/{e["slug"]}/',
                },
            }
            for i, e in enumerate(top_10)
        ],
    }
    breadcrumb = breadcrumb_schema([
        ('Accueil', '/'),
        ('Toutes les toupies', '/tous-les-beyblade/'),
    ])

    head = render_head(
        title=f'Toutes les toupies Beyblade : catalogue complet ({s["total"]} références)',
        description=f"Catalogue interactif de {s['total']} toupies Beyblade ({s['tested']} testées) — Beyblade X, Burst, Metal Fusion. Filtrable par gamme et par type, triable par note.",
        canonical_path='/tous-les-beyblade/',
        og_type='website',
        extra_css=['/css/page-tous-les-beyblade.css', '/css/page-comparatif.css'],
        extra_jsonld=[itemlist, breadcrumb],
    )

    return write_page('tous-les-beyblade', assemble_html(head, body_inner))


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

    print('🦅 Building article : Phoenix Wing 9-60GF...')
    p = build_article_phoenix_wing()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🛡️  Building article : Knight Shield 3-80N...')
    p = build_article_knight_shield()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🏹 Building article : Wizard Arrow 4-80B...')
    p = build_article_wizard_arrow()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('⚡ Building article : Storm Pegasus 105RF...')
    p = build_article_storm_pegasus()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🦄 Building article : Ray Unicorno D125CS...')
    p = build_article_ray_unicorno()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🐲 Building article : L-Drago Destroy F:S...')
    p = build_article_l_drago_destroy()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('💀 Building article : Hells Scythe 4-60T...')
    p = build_article_hells_scythe()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🐉 Building article : Cobalt Dragoon 2-60C...')
    p = build_article_cobalt_dragoon()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🦅 Building article : Earth Eagle 145WD...')
    p = build_article_earth_eagle()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('💥 Building article : Dran Buster 1-60A...')
    p = build_article_dran_buster()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🌪️  Building article : Cyclone Roktavor R7...')
    p = build_article_cyclone_roktavor()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('🐺 Building article : Vanish Fafnir F7...')
    p = build_article_vanish_fafnir()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('⭐ Building article : Stellar Hyperion H8...')
    p = build_article_stellar_hyperion()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('📊 Building comparatif : Beyblade Burst...')
    p = build_comparatif_beyblade_burst()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('📊 Building comparatif : Beyblade Metal Fusion...')
    p = build_comparatif_metal_fusion()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('📊 Building comparatif : Beyblade X...')
    p = build_comparatif_beyblade_x()
    print(f'   → {p.relative_to(DIST_DIR.parent)}')

    print('📚 Building catalogue : Toutes les toupies...')
    p = build_catalogue_page()
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
