"""Construction de liens d'affiliation Amazon.fr — version Beyblade.

Adaptation depuis pistoletnerf-refonte :
- Tag Amazon : beyblade0a-21 (au lieu de pistol-21)
- HTML CTA : palette dark + accent bleu électrique #0099ff
- Pas d'affichage de prix (décision validée — voir memory beyblade_blog_editorial)
- Support des liens directs ASIN en plus des liens de recherche
"""
import html
import re
import urllib.parse


def sanitize_product_name(name):
    """Nettoie un nom produit (HTML entities, espaces multiples, tirets unicode)."""
    decoded = html.unescape(name)
    decoded = decoded.replace('\u2013', '-').replace('\u2014', '-')
    decoded = re.sub(r'\s+', ' ', decoded).strip()
    return decoded


def build_search_url(product_name, tag):
    """Construit une URL de recherche Amazon.fr avec tag d'affiliation."""
    clean = sanitize_product_name(product_name)
    encoded = urllib.parse.quote_plus(clean)
    return f"https://www.amazon.fr/s?k={encoded}&tag={tag}"


def build_asin_url(asin, tag):
    """Construit une URL produit directe à partir d'un ASIN connu."""
    return f"https://www.amazon.fr/dp/{asin}?tag={tag}"


def build_url(product, tag):
    """Helper : retourne ASIN URL si dispo, sinon search URL."""
    if product.get('asin'):
        return build_asin_url(product['asin'], tag)
    return build_search_url(product['name'], tag)


def build_cta_html(product_name, tag, asin=None):
    """Bloc CTA final Amazon — version dark mode, sans prix.

    Style aligné sur la maquette mockups/02-article-produit.html `final-cta`.
    """
    url = build_asin_url(asin, tag) if asin else build_search_url(product_name, tag)
    clean_name = html.escape(sanitize_product_name(product_name))
    url_esc = html.escape(url)

    return f'''<div class="bb-final-cta">
<div class="bb-final-eyebrow">/ Trouver cette toupie</div>
<h3>Convaincu&nbsp;? Trouvez<br>la {clean_name}</h3>
<p>Disponible chez les revendeurs FR. Notre lien Amazon vous redirige vers la fiche officielle (livraison Prime, retour 30 jours, garantie constructeur).</p>
<a href="{url_esc}" target="_blank" rel="nofollow sponsored noopener" class="bb-cta">▶ Voir sur Amazon</a>
<div class="bb-disclaimer">Lien d'affiliation · Achat sans surcoût pour vous</div>
</div>'''
