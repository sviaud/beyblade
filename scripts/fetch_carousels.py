"""Orchestrateur : scrape Amazon → télécharge → détoure → enregistre comme carrousel.

Pour chaque toupie testée du catalogue ayant un ASIN valide :
1. Récupère 3-8 URLs d'images HD via amazon_scraper.fetch_product_images()
2. Télécharge chaque image
3. Détoure (algorithme PIL existant : seuil luminance + alpha graduel + crop bbox + resize 600px)
4. Enregistre comme `src/static/img/{base}-N.webp` (N=1,2,3...) où base = slug sans suffixe ref
5. Affiche un rapport : pour chaque slug, la liste des fichiers générés à intégrer

Usage :
    python3 scripts/fetch_carousels.py            # tous les ASIN valides du catalogue
    python3 scripts/fetch_carousels.py B0C52C4L3T # un ASIN spécifique (par ASIN)
    python3 scripts/fetch_carousels.py hells-scythe-4-60t  # ou par slug
"""
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'data'))

from amazon_scraper import fetch_product_images
from PIL import Image
from io import BytesIO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = PROJECT_ROOT / 'src' / 'static' / 'img'
IMG_DIR.mkdir(parents=True, exist_ok=True)

UA = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)


def download_image(url: str, timeout: int = 15) -> bytes:
    req = urllib.request.Request(url, method='GET')
    req.add_header('User-Agent', UA)
    req.add_header('Referer', 'https://www.amazon.fr/')
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def detoure_to_webp(raw_bytes: bytes, out_path: Path, threshold: int = 240, padding: float = 0.05) -> int:
    """Detoure (white background → transparent), crop bbox, resize 600x600, save as WebP. Returns file size in KB."""
    im = Image.open(BytesIO(raw_bytes)).convert('RGBA')
    px = im.load()
    W, H = im.size
    for y in range(H):
        for x in range(W):
            r, g, b, _ = px[x, y]
            lum = 0.2126*r + 0.7152*g + 0.0722*b
            if lum >= threshold and abs(r-g) < 20 and abs(g-b) < 20:
                if lum >= 252:
                    px[x, y] = (r, g, b, 0)
                else:
                    a = int(255 * (252 - lum) / (252 - threshold))
                    px[x, y] = (r, g, b, max(0, min(255, a)))
    bbox = im.getbbox()
    if bbox is None:
        # Toute l'image est transparente — on saute
        return 0
    im = im.crop(bbox)
    cw, ch = im.size
    side = int(max(cw, ch) * (1 + 2*padding))
    canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - cw) // 2, (side - ch) // 2), im)
    canvas = canvas.resize((600, 600), Image.LANCZOS)
    canvas.save(out_path, 'WEBP', quality=88, method=6)
    return out_path.stat().st_size // 1024


def slug_to_base(slug: str) -> str:
    """Convertit 'cobalt-dragoon-2-60c' → 'cobalt-dragoon' (enleve suffixe ref toupie)."""
    # Le suffixe ref est généralement le dernier segment de type X-XXX ou XX-XX
    # Ex: cobalt-dragoon-2-60c → cobalt-dragoon
    #     hells-scythe-4-60t → hells-scythe
    #     phoenix-wing-9-60gf → phoenix-wing
    #     l-drago-destroy-fs → l-drago-destroy (le 'fs' est un suffix court)
    # On coupe au -dernier segment alphanum-court (≤4 chars)
    parts = slug.split('-')
    # Heuristic : on retire les segments depuis la fin tant qu'ils ressemblent à une ref
    # (chiffres, ou court mix alphanum)
    while len(parts) > 1:
        last = parts[-1]
        if any(c.isdigit() for c in last) and len(last) <= 4:
            parts.pop()
        else:
            break
    return '-'.join(parts) if parts else slug


def process_entry(entry: dict, delay_after: float = 1.5) -> dict:
    """Pour une entrée du catalogue, télécharge + détoure tous les images dispo. Retourne {slug, files: [...], errors: [...]}."""
    slug = entry['slug']
    asin = entry['asin']
    base = slug_to_base(slug)

    result = {'slug': slug, 'asin': asin, 'base': base, 'files': [], 'errors': []}
    print(f'\n→ {slug} (ASIN {asin}, base "{base}")')

    try:
        urls = fetch_product_images(asin, size='SL1500', max_images=8)
    except Exception as e:
        result['errors'].append(f'scrape: {e}')
        print(f'  ✘ scrape failed: {e}')
        return result

    print(f'  Found {len(urls)} image URLs from amazon.fr')

    for i, url in enumerate(urls, start=1):
        out_name = f'{base}-{i}.webp'
        out_path = IMG_DIR / out_name
        try:
            raw = download_image(url)
            kb = detoure_to_webp(raw, out_path)
            if kb > 0:
                result['files'].append(out_name)
                print(f'  ✓ {out_name} ({kb} KB) ← {url.split("/")[-1]}')
            else:
                print(f'  ⚠ {out_name}: image vide après détourage (skipped)')
        except Exception as e:
            result['errors'].append(f'image {i}: {e}')
            print(f'  ✘ {out_name} FAILED: {e}')
        time.sleep(0.4)  # gentle pacing for amazon CDN

    time.sleep(delay_after)  # gentle pacing between products
    return result


def main():
    from catalogue import CATALOGUE

    # Filter args
    args = sys.argv[1:]
    if args:
        # On peut passer soit des ASINs soit des slugs
        targets = []
        for a in args:
            for e in CATALOGUE:
                if e.get('slug') and (e.get('asin') == a or e['slug'] == a):
                    targets.append(e)
                    break
            else:
                print(f'⚠ {a}: pas trouvé dans CATALOGUE (ignored)')
    else:
        # All tested entries with an ASIN
        targets = [e for e in CATALOGUE if e.get('slug') and e.get('asin')]

    print(f'Processing {len(targets)} toupie(s)...')

    results = []
    for e in targets:
        r = process_entry(e)
        results.append(r)

    # Final report
    print('\n' + '=' * 70)
    print('REPORT — ajoute ces images au catalogue.py :')
    print('=' * 70)
    for r in results:
        if r['files']:
            print(f"\n# {r['slug']}")
            print(f"'image': '{r['files'][0]}',")
            print(f"'images': {r['files']!r},")
        if r['errors']:
            print(f"# ⚠ {r['slug']}: errors = {r['errors']}")

    # Stats
    total_imgs = sum(len(r['files']) for r in results)
    failed = sum(1 for r in results if not r['files'])
    print(f"\nTotal: {total_imgs} images générées sur {len(results)} toupies "
          f"({failed} échecs).")


if __name__ == '__main__':
    main()
