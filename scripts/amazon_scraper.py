"""Scraper minimal pour récupérer les URLs d'images d'une page produit Amazon FR.

Plan B en attendant l'éligibilité PA-API. Extrait les image IDs depuis le HTML
public de https://www.amazon.fr/dp/{ASIN} et reconstruit les URLs HD.

Usage :
    from amazon_scraper import fetch_product_images
    urls = fetch_product_images('B0C2HP6XCM', size='SL1500')
    # → ['https://m.media-amazon.com/images/I/61abc123._AC_SL1500_.jpg', ...]

Notes :
- Rate limiting 1.5 sec entre requêtes (politeness, pas pour anti-bot)
- User-Agent honnête (Mozilla, pas masqué en bot)
- Pattern de parsing : `colorImages` (le plus fiable) + fallback regex `data-old-hires`
- Si Amazon retourne du captcha (rare en GET simple), on lève une exception explicite
"""
from __future__ import annotations

import gzip
import io
import json
import re
import time
import urllib.request
import urllib.error


USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)
ACCEPT_LANGUAGE = 'fr-FR,fr;q=0.9,en-US;q=0.5,en;q=0.3'

# Amazon image IDs : alphanumeric + parfois dash/plus, 8-15 chars
# Source #1 (best, mais souvent absent du HTML SSR) : "hiRes":"https://..."
RE_HIRES = re.compile(r'"hiRes":"(https?://[^"]+\.jpg)"')
RE_LARGE = re.compile(r'"large":"(https?://[^"]+\.jpg)"')

# Source #2 (la mine d'or) : data-a-dynamic-image contient TOUS les thumbnails
# du carrousel d'images. Format : {"url1": [w,h], "url2": [w,h], ...} HTML-escapé.
RE_DYNAMIC_IMAGE = re.compile(r'data-a-dynamic-image=["\']([^"\']+)["\']')

# Source #3 : data-old-hires attribute on <img>
RE_DATA_OLD_HIRES = re.compile(r'data-old-hires=["\'](https?://[^"\']+\.jpg)["\']')

# Pattern d'extraction d'image ID depuis n'importe quelle URL Amazon
RE_ANY_AMZ_IMAGE = re.compile(
    r'https?://m\.media-amazon\.com/images/I/([A-Za-z0-9+%\-]{8,15})(\._[A-Z0-9_]+_)?\.jpg'
)

# Bot detection signatures
RE_CAPTCHA = re.compile(r'(Robot Check|Pour des raisons.{0,10}sécurité|api-services-support)', re.I)


def _http_get(url: str, timeout: int = 15) -> str:
    """GET request with realistic browser headers, gzip-aware, returns decoded HTML."""
    req = urllib.request.Request(url, method='GET')
    req.add_header('User-Agent', USER_AGENT)
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    req.add_header('Accept-Language', ACCEPT_LANGUAGE)
    req.add_header('Accept-Encoding', 'gzip, deflate')
    req.add_header('DNT', '1')
    req.add_header('Connection', 'close')
    req.add_header('Upgrade-Insecure-Requests', '1')

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            if resp.headers.get('Content-Encoding') == 'gzip':
                data = gzip.decompress(data)
            # Amazon sert UTF-8 par défaut sur amazon.fr
            return data.decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:200]
        raise RuntimeError(f"HTTP {e.code} on {url}: {body}") from e


def _extract_unique_image_ids(html: str) -> list[str]:
    """Parse all unique Amazon image IDs from the HTML (preserve order of first appearance).

    Stratégie : on agrège plusieurs sources et on dédoublonne en gardant l'ordre.
    L'ordre de priorité (= la première apparition) reflète l'ordre du carrousel sur
    la page produit (main image, puis thumbnails 2..n).
    """
    seen = []
    seen_set = set()

    def _add(iid: str):
        if iid and iid not in seen_set:
            seen.append(iid)
            seen_set.add(iid)

    # Source #1 : "hiRes" URLs (main image en HD)
    for url in RE_HIRES.findall(html):
        m = RE_ANY_AMZ_IMAGE.search(url)
        if m:
            _add(m.group(1))

    # Source #2 (la mine d'or pour le carrousel) : data-a-dynamic-image attributes
    # contient TOUS les thumbnails du gallery (3-8 images en général).
    # Le format est HTML-escapé : data-a-dynamic-image="{&quot;url1&quot;:[115,115], ...}"
    for raw in RE_DYNAMIC_IMAGE.findall(html):
        # Décoder les entités HTML
        decoded = (raw.replace('&quot;', '"')
                       .replace('&amp;', '&')
                       .replace('&#x2f;', '/'))
        # Extraire toutes les URLs media-amazon de ce dict
        for m in RE_ANY_AMZ_IMAGE.finditer(decoded):
            _add(m.group(1))

    # Source #3 : data-old-hires attribute on <img> tags
    for url in RE_DATA_OLD_HIRES.findall(html):
        m = RE_ANY_AMZ_IMAGE.search(url)
        if m:
            _add(m.group(1))

    # Source #4 : "large" URLs from imageGalleryData
    for url in RE_LARGE.findall(html):
        m = RE_ANY_AMZ_IMAGE.search(url)
        if m:
            _add(m.group(1))

    return seen


def fetch_product_images(asin: str, size: str = 'SL1500', max_images: int = 8) -> list[str]:
    """Récupère jusqu'à `max_images` URLs HD pour un ASIN amazon.fr.

    Args:
        asin: ASIN Amazon (ex 'B0C2HP6XCM')
        size: format de taille Amazon. Choix usuels:
              - 'SL500'    : ~500px largeur
              - 'SL1000'   : ~1000px
              - 'SL1500'   : ~1500px (recommandé pour détourage haute qualité)
              - ''         : original (souvent 1500-2000px)
        max_images: max d'images à retourner

    Returns:
        Liste d'URLs jpg HD, dans l'ordre d'apparition sur la page.
        Première image = main product image.
    """
    url = f'https://www.amazon.fr/dp/{asin}'
    html = _http_get(url)

    # Quick captcha check
    if RE_CAPTCHA.search(html[:5000]):
        raise RuntimeError(f"Amazon a servi un captcha pour ASIN {asin} — réessayer plus tard ou changer d'IP")

    image_ids = _extract_unique_image_ids(html)
    if not image_ids:
        # Sauvegarder le HTML pour debug si on n'a rien trouvé
        raise RuntimeError(f"Aucun image ID trouvé dans la page de {asin} (page peut-être vide ou format inattendu)")

    # Reconstruire les URLs avec la taille demandée
    suffix = f'._AC_{size}_' if size else ''
    urls = [
        f'https://m.media-amazon.com/images/I/{iid}{suffix}.jpg'
        for iid in image_ids[:max_images]
    ]
    return urls


def fetch_product_images_batch(asins: list[str], delay_sec: float = 1.5, **kwargs) -> dict[str, list[str] | str]:
    """Batch fetch with rate limiting. Returns {asin: [urls]} or {asin: error_message}."""
    results = {}
    for i, asin in enumerate(asins):
        if i > 0:
            time.sleep(delay_sec)
        try:
            urls = fetch_product_images(asin, **kwargs)
            results[asin] = urls
            print(f'  [{i+1}/{len(asins)}] {asin}: {len(urls)} images')
        except Exception as e:
            results[asin] = f'ERROR: {e}'
            print(f'  [{i+1}/{len(asins)}] {asin}: FAILED → {e}')
    return results


# ============ CLI ============

if __name__ == '__main__':
    import sys
    asins = sys.argv[1:] or ['B0C2HP6XCM']
    print(f'Fetching {len(asins)} ASIN(s) from amazon.fr...\n')
    if len(asins) == 1:
        try:
            urls = fetch_product_images(asins[0])
            print(f'\n{asins[0]}: {len(urls)} images found')
            for i, u in enumerate(urls):
                print(f'  {i+1}. {u}')
        except Exception as e:
            print(f'FAILED: {e}', file=sys.stderr)
            sys.exit(1)
    else:
        results = fetch_product_images_batch(asins)
        print(json.dumps(results, indent=2, ensure_ascii=False))
