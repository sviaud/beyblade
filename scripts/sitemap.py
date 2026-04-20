"""Génération de sitemap.xml + robots.txt."""
from datetime import datetime, timezone
import html as html_mod

from seo_meta import SITE_URL


def render_sitemap(pages):
    """Construit un sitemap.xml standard.

    Args:
        pages: list[dict] — chaque dict : {'path': '/xxx/', 'lastmod': iso8601, 'priority': 0.8, 'changefreq': 'weekly'}
    """
    items = []
    for page in pages:
        path = page['path']
        loc = SITE_URL + path
        loc_esc = html_mod.escape(loc)
        lastmod = page.get('lastmod') or datetime.now(timezone.utc).strftime('%Y-%m-%d')
        priority = page.get('priority', 0.7)
        changefreq = page.get('changefreq', 'weekly')

        items.append(
            f'  <url>\n'
            f'    <loc>{loc_esc}</loc>\n'
            f'    <lastmod>{lastmod}</lastmod>\n'
            f'    <changefreq>{changefreq}</changefreq>\n'
            f'    <priority>{priority:.1f}</priority>\n'
            f'  </url>'
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(items)
        + '\n</urlset>\n'
    )


def render_robots():
    """robots.txt standard avec lien vers sitemap."""
    return (
        f"User-agent: *\n"
        f"Allow: /\n"
        f"Disallow: /404.html\n"
        f"\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )


if __name__ == '__main__':
    sample_pages = [
        {'path': '/', 'priority': 1.0, 'changefreq': 'daily'},
        {'path': '/dran-sword-3-60f/', 'priority': 0.8, 'changefreq': 'weekly'},
        {'path': '/comparatif-beyblade-x/', 'priority': 0.9, 'changefreq': 'weekly'},
    ]
    print(render_sitemap(sample_pages))
    print('---')
    print(render_robots())
