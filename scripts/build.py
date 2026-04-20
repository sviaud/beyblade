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


def build_homepage():
    """Génère / (placeholder pour V1 — sera étoffé avec catalogue.md)."""
    from seo_meta import render_head
    head = render_head(
        title='Toupiebeyblade.fr — Le guide ultime des toupies Beyblade',
        description='Tests détaillés, comparatifs, guides d\'achat sur les toupies Beyblade X, Burst et Metal Fusion. 40+ fiches produit avec notes vérifiables.',
        canonical_path='/',
        og_type='website',
    )
    body = '''<body>
<header class="site-header">
<div class="header-inner">
<a href="/" class="logo">
<div class="logo-mark">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
<polygon points="12,2 15,9 22,9 16.5,14 18.5,21 12,17 5.5,21 7.5,14 2,9 9,9"/>
</svg>
</div>
<div>
<div class="logo-text">Toupie<span class="accent">Beyblade</span></div>
<span class="logo-tag">Le guide ultime · 2026</span>
</div>
</a>
<nav class="nav">
<a href="/" class="active">Accueil</a>
<a href="/tous-les-beyblade/">Toutes les toupies</a>
<a href="/comparatif-beyblade-x/" class="has-submenu">Comparatifs</a>
<a href="/guides/">Guides</a>
<a href="/blog/">Blog</a>
<a href="/contact/">Contact</a>
</nav>
</div>
</header>
<main style="padding:80px 24px;text-align:center;max-width:900px;margin:0 auto;position:relative;z-index:2">
<h1 style="font-family:var(--font-display);font-weight:900;font-size:clamp(48px,8vw,96px);line-height:0.9;letter-spacing:-2px;text-transform:uppercase;margin-bottom:16px">Toupiebeyblade.fr<br><span style="color:var(--accent)">Bientôt en ligne</span></h1>
<p style="font-size:19px;color:var(--text-soft);max-width:600px;margin:24px auto">Le guide ultime des toupies Beyblade — fiches produit, comparatifs, guides d'achat. Lancement courant 2026.</p>
</main>
</body>'''
    return write_page('', f'<head>\n{head}\n</head>\n{body}')


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
