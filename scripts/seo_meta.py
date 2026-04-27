"""Génération des balises SEO et JSON-LD structuré.

Remplace l'équivalent Yoast SEO. Couvre :
- Title tag, meta description
- Canonical URL
- Open Graph (og:title, og:image, og:type, etc.)
- Twitter Cards
- JSON-LD : Product, Review, Article, BreadcrumbList, FAQPage, Organization, WebSite
- Robots meta (index/noindex)
"""
import html as html_mod
import json
import re


SITE_URL = 'https://toupiebeyblade.fr'
SITE_NAME = 'toupiebeyblade.fr'
SITE_TAGLINE = 'Le guide ultime des toupies Beyblade'
SITE_LOCALE = 'fr_FR'
TWITTER_HANDLE = '@toupiebeyblade'  # à créer si besoin
DEFAULT_OG_IMAGE = '/img/og-default.jpg'  # à créer (1200x630)

# Google Analytics 4
GA4_MEASUREMENT_ID = 'G-0521NL3J30'

GA4_SNIPPET = f'''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA4_MEASUREMENT_ID}');
</script>'''


# ============================================================
#   META TAGS
# ============================================================

def render_head(
    *,
    title,
    description,
    canonical_path,
    og_type='website',
    og_image=None,
    article_published=None,
    article_modified=None,
    article_section=None,
    robots='index, follow',
    extra_jsonld=None,
    extra_css=None,
    preload_images=None,
):
    """Construit l'intégralité du <head> SEO d'une page.

    Args:
        title: str — title tag (max ~60 chars)
        description: str — meta description (max ~155 chars)
        canonical_path: str — path absolu (ex: '/dran-sword-3-60f/')
        og_type: 'website' | 'article'
        og_image: str|None — path absolu de l'image OG (ou None pour défaut)
        article_published, article_modified: ISO date strings (pour og:type=article)
        article_section: catégorie de l'article
        robots: meta robots
        extra_jsonld: list[dict] — schemas JSON-LD additionnels à inclure
    """
    title_esc = html_mod.escape(title)
    desc_esc = html_mod.escape(description)
    canonical = SITE_URL + canonical_path
    og_img_url = SITE_URL + (og_image or DEFAULT_OG_IMAGE)

    parts = [
        # Google Analytics 4 — premier élément après <head> pour tracking immédiat
        GA4_SNIPPET,
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{title_esc}</title>',
        f'<meta name="description" content="{desc_esc}">',
        f'<link rel="canonical" href="{canonical}">',
        f'<meta name="robots" content="{robots}">',

        # Open Graph
        f'<meta property="og:title" content="{title_esc}">',
        f'<meta property="og:description" content="{desc_esc}">',
        f'<meta property="og:url" content="{canonical}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:image" content="{og_img_url}">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:locale" content="{SITE_LOCALE}">',

        # Twitter Cards
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title_esc}">',
        f'<meta name="twitter:description" content="{desc_esc}">',
        f'<meta name="twitter:image" content="{og_img_url}">',
    ]

    if og_type == 'article':
        if article_published:
            parts.append(f'<meta property="article:published_time" content="{article_published}">')
        if article_modified:
            parts.append(f'<meta property="article:modified_time" content="{article_modified}">')
        if article_section:
            parts.append(f'<meta property="article:section" content="{html_mod.escape(article_section)}">')

    # Préconnexion fonts (gain perf LCP)
    parts.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
    parts.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')

    # Préload images critiques (above-the-fold) — gain LCP majeur
    for img_url in (preload_images or []):
        parts.append(f'<link rel="preload" as="image" href="{img_url}" fetchpriority="high">')

    # CSS
    parts.append('<link rel="stylesheet" href="/css/shared.css">')
    parts.append('<link rel="stylesheet" href="/css/beyblade.css">')
    for css_path in (extra_css or []):
        parts.append(f'<link rel="stylesheet" href="{css_path}">')

    # Favicon (placeholder — à créer)
    parts.append('<link rel="icon" type="image/svg+xml" href="/img/favicon.svg">')

    # JSON-LD schemas
    schemas = [website_schema(), organization_schema()]
    if extra_jsonld:
        schemas.extend(extra_jsonld)
    for schema in schemas:
        parts.append(
            f'<script type="application/ld+json">'
            f'{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}'
            f'</script>'
        )

    return '\n'.join(parts)


# ============================================================
#   JSON-LD SCHEMAS
# ============================================================

def website_schema():
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': f'{SITE_URL}/#website',
        'url': SITE_URL,
        'name': SITE_NAME,
        'description': SITE_TAGLINE,
        'inLanguage': 'fr-FR',
        'potentialAction': {
            '@type': 'SearchAction',
            'target': {
                '@type': 'EntryPoint',
                'urlTemplate': f'{SITE_URL}/?q={{search_term_string}}',
            },
            'query-input': 'required name=search_term_string',
        },
    }


def organization_schema():
    return {
        '@context': 'https://schema.org',
        '@type': 'Organization',
        '@id': f'{SITE_URL}/#organization',
        'name': SITE_NAME,
        'url': SITE_URL,
        'logo': f'{SITE_URL}/img/logo.svg',
    }


def breadcrumb_schema(items):
    """Args: items = [(name, path), ...] — path absolu /xxx/."""
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': i + 1,
                'name': name,
                'item': SITE_URL + path,
            }
            for i, (name, path) in enumerate(items)
        ],
    }


def product_schema(product, review_score=None, review_max=10):
    """Schema Product (+ Review nested si score).

    product: dict avec name, reference, gamme, year, type, asin, etc.
    """
    schema = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        'name': product['name'],
        'description': product.get('description', f"Toupie Beyblade {product.get('gamme', '')} — {product['name']}"),
        'sku': product.get('reference', ''),
        'brand': {
            '@type': 'Brand',
            'name': 'Hasbro / Takara Tomy',
        },
        'category': _gamme_label(product.get('gamme')),
    }
    if product.get('image_url'):
        schema['image'] = product['image_url']
    # Note (2026-04) : on n'émet PAS d'`offers` car notre politique éditoriale
    # ne fige pas de prix, et un `Offer` sans `price` est invalide pour Google
    # Product Snippet → cause un warning critique en GSC.
    # La conformité Google nécessite : name + (offers OR review OR aggregateRating).
    # On a déjà aggregateRating + review ci-dessous, donc on est conforme sans offers.
    if review_score is not None:
        schema['aggregateRating'] = {
            '@type': 'AggregateRating',
            'ratingValue': round(review_score, 1),
            'bestRating': review_max,
            'worstRating': 0,
            'ratingCount': 1,
            'reviewCount': 1,
        }
        schema['review'] = {
            '@type': 'Review',
            'reviewRating': {
                '@type': 'Rating',
                'ratingValue': round(review_score, 1),
                'bestRating': review_max,
                'worstRating': 0,
            },
            'author': {
                '@type': 'Organization',
                'name': SITE_NAME,
            },
        }
    return schema


def article_schema(*, headline, description, url_path, image_url=None,
                   date_published=None, date_modified=None, section=None):
    schema = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': headline,
        'description': description,
        'url': SITE_URL + url_path,
        # mainEntityOfPage : forme URL string (plus simple, évite le warning Google
        # "Champ name manquant" sur le WebPage nested qui n'a que @id).
        'mainEntityOfPage': SITE_URL + url_path,
        'inLanguage': 'fr-FR',
        'publisher': {
            '@id': f'{SITE_URL}/#organization',
        },
    }
    if image_url:
        schema['image'] = image_url if image_url.startswith('http') else SITE_URL + image_url
    if date_published:
        schema['datePublished'] = date_published
    if date_modified:
        schema['dateModified'] = date_modified
    if section:
        schema['articleSection'] = section
    return schema


def faq_schema(qa_pairs):
    """Args: qa_pairs = [(question, answer_html), ...]"""
    return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {
                '@type': 'Question',
                'name': q,
                'acceptedAnswer': {
                    '@type': 'Answer',
                    'text': _strip_html(a),
                },
            }
            for q, a in qa_pairs
        ],
    }


# ============================================================
#   HELPERS
# ============================================================

def _gamme_label(gamme):
    return {
        'beyblade-x':            'Beyblade X',
        'beyblade-burst':        'Beyblade Burst',
        'beyblade-metal-fusion': 'Beyblade Metal Fusion',
    }.get(gamme, 'Beyblade')


def _strip_html(text):
    """Supprime les balises HTML pour le contenu JSON-LD."""
    if not text:
        return ''
    return re.sub(r'<[^>]+>', '', text).strip()


def truncate_description(text, max_chars=155):
    """Tronque proprement à max_chars (sur un mot complet, ajoute …)."""
    text = _strip_html(text).strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rsplit(' ', 1)[0]
    return cut + '…'


# ============================================================
#   DEBUG
# ============================================================
if __name__ == '__main__':
    sample = {
        'name': 'Dranzer Spiral 3-60P',
        'reference': 'BX-42',
        'gamme': 'beyblade-x',
        'year': 2026,
        'type': 'attaque',
        'asin': 'B0CXXXXXXX',
        'image_url': 'https://toupiebeyblade.fr/img/dran-sword.webp',
    }
    head = render_head(
        title='Dranzer Spiral 3-60P : test complet · toupiebeyblade.fr',
        description='Test détaillé de la Dranzer Spiral 3-60P, attaquante Beyblade X 2026. Performances en stadium Xtreme, alternatives, FAQ.',
        canonical_path='/dran-sword-3-60p/',
        og_type='article',
        article_published='2026-04-19T10:00:00+02:00',
        article_section='Beyblade X',
        extra_jsonld=[
            product_schema(sample, review_score=9.2),
            breadcrumb_schema([
                ('Accueil', '/'),
                ('Beyblade X', '/beyblade-x/'),
                ('Dranzer Spiral', '/dran-sword-3-60p/'),
            ]),
        ],
    )
    print(head[:1500])
