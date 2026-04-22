"""Écriture de fichiers HTML statiques dans /dist.

Remplace wp_client.py (qui faisait du POST API REST WordPress).
Style "static site generator" : on écrit des fichiers, on les commit,
Cloudflare Pages déploie automatiquement.
"""
import os
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / 'src'
DIST_DIR = PROJECT_ROOT / 'dist'


def clean_dist():
    """Vide /dist sans le supprimer (préserve les permissions)."""
    if DIST_DIR.exists():
        for item in DIST_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    else:
        DIST_DIR.mkdir(parents=True)


def _is_junk(path: Path) -> bool:
    """Filtre les fichiers à ne jamais copier dans /dist (macOS, éditeurs, etc.)."""
    name = path.name
    if name == '.DS_Store' or name.startswith('._'):
        return True
    if name.endswith(('~', '.swp', '.swo', '.bak')):
        return True
    if name == 'Thumbs.db' or name == 'desktop.ini':
        return True
    return False


def copy_static():
    """Copie src/static/* → dist/ (CSS, images, JS, fonts).

    Ignore les fichiers junk (.DS_Store, ._*, Thumbs.db, *~, *.swp, etc.).
    """
    static_src = SRC_DIR / 'static'
    if not static_src.exists():
        return 0
    count = 0
    for src in static_src.rglob('*'):
        if src.is_file() and not _is_junk(src):
            rel = src.relative_to(static_src)
            dst = DIST_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            count += 1
    return count


def copy_root_files():
    """Copie src/_redirects, src/_headers, src/llms.txt, etc. → dist/ (Cloudflare Pages)."""
    count = 0
    for name in ('_redirects', '_headers', 'robots.txt', 'llms.txt'):
        src = SRC_DIR / name
        if src.exists():
            shutil.copy2(src, DIST_DIR / name)
            count += 1
    return count


def write_page(slug, html, lang='fr'):
    """Écrit une page HTML à l'URL /{slug}/.

    Args:
        slug: str — chemin URL sans slash (ex: 'dran-sword-3-60f' ou '' pour la racine)
        html: str — HTML complet (avec <!doctype> ou pas — on l'ajoute si manquant)
        lang: str — code langue (mis dans <html lang="...">)
    """
    if not html.lstrip().lower().startswith('<!doctype'):
        # Wrap dans un doctype si manquant (sécurité)
        html = f'<!DOCTYPE html>\n<html lang="{lang}">\n{html}\n</html>'

    if slug in ('', '/', None):
        path = DIST_DIR / 'index.html'
    else:
        slug_clean = slug.strip('/')
        if slug_clean.endswith('.html'):
            # Fichier HTML direct (ex: 404.html) — pas de dossier
            path = DIST_DIR / slug_clean
        else:
            # URL propre /{slug}/ → /{slug}/index.html
            path = DIST_DIR / slug_clean / 'index.html'

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding='utf-8')
    return path


def write_xml(slug, xml_content):
    """Écrit un fichier XML (sitemap, RSS, etc.)."""
    if not slug.endswith('.xml'):
        slug += '.xml'
    path = DIST_DIR / slug
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(xml_content, encoding='utf-8')
    return path


def write_text(slug, content):
    """Écrit un fichier texte brut (robots.txt, manifest, etc.)."""
    path = DIST_DIR / slug
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    return path


def list_pages():
    """Retourne la liste de toutes les pages HTML générées dans /dist."""
    pages = []
    for html_file in DIST_DIR.rglob('index.html'):
        rel = html_file.relative_to(DIST_DIR).parent
        url = '/' if str(rel) == '.' else f'/{rel}/'
        pages.append({'url': url, 'path': html_file})
    return pages


if __name__ == '__main__':
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Source dir   : {SRC_DIR}")
    print(f"Dist dir     : {DIST_DIR}")
    print()
    print("--- Pages already in /dist ---")
    for p in list_pages():
        print(f"  {p['url']:40} {p['path']}")
