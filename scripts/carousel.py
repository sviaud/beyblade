"""Génération d'un carrousel d'images WordPress en HTML pur.

Chaque image est cliquable et ouvre le lien d'affiliation Amazon dans un nouvel onglet.
Le carrousel utilise du CSS scroll-snap (pas de JS requis) pour être compatible
avec tous les navigateurs modernes + mobile.
"""
import html as html_mod


def build_carousel(images, amazon_url, product_name):
    """Construit un carrousel HTML pur (CSS scroll-snap).

    Args:
        images: list of {'src': url, 'alt': text} — images déjà uploadées sur WP
        amazon_url: lien d'affiliation Amazon
        product_name: nom du produit pour les alt texts
    Returns:
        HTML string du carrousel
    """
    if not images:
        return ''

    name_escaped = html_mod.escape(product_name)
    url_escaped = html_mod.escape(amazon_url)

    slides = []
    for idx, img in enumerate(images):
        src = html_mod.escape(img['src'])
        alt = html_mod.escape(img.get('alt', f'{product_name} — photo {idx + 1}'))
        slides.append(
            f'<div style="flex:0 0 100%;scroll-snap-align:start;min-width:100%;text-align:center;padding:10px;box-sizing:border-box;">'
            f'<a href="{url_escaped}" target="_blank" rel="nofollow sponsored noopener">'
            f'<img src="{src}" alt="{alt}" style="max-height:400px;max-width:100%;object-fit:contain;border-radius:8px;" loading="lazy" />'
            f'</a>'
            f'</div>'
        )

    # Thumbnails
    thumbs = []
    for idx, img in enumerate(images):
        src = html_mod.escape(img['src'])
        alt = html_mod.escape(img.get('alt', f'Photo {idx + 1}'))
        thumbs.append(
            f'<img src="{src}" alt="{alt}" '
            f'onclick="this.closest(\'.nerf-carousel\').querySelector(\'.nerf-carousel-track\').scrollTo({{left:{idx}*this.closest(\'.nerf-carousel\').querySelector(\'.nerf-carousel-track\').offsetWidth,behavior:\'smooth\'}})" '
            f'style="width:60px;height:60px;object-fit:contain;border:2px solid #e0e0e0;border-radius:6px;cursor:pointer;background:#fff;padding:2px;transition:border-color 0.2s;" '
            f'onmouseover="this.style.borderColor=\'#ff9900\'" '
            f'onmouseout="this.style.borderColor=\'#e0e0e0\'" />'
        )

    thumbs_html = ''
    if len(images) > 1:
        thumbs_html = (
            f'<div style="display:flex;gap:8px;justify-content:center;margin-top:10px;flex-wrap:wrap;">'
            + ''.join(thumbs)
            + '</div>'
        )

    nav_hint = ''
    if len(images) > 1:
        nav_hint = f'<div style="text-align:center;color:#999;font-size:12px;margin-top:6px;">← Faites défiler pour voir les {len(images)} photos · Cliquez pour acheter sur Amazon →</div>'

    return f'''<div class="nerf-carousel" style="margin:1.5em 0;background:#fafafa;border:1px solid #e0e0e0;border-radius:12px;padding:16px;overflow:hidden;">
<div class="nerf-carousel-track" style="display:flex;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;scrollbar-width:none;-ms-overflow-style:none;">
{''.join(slides)}
</div>
{thumbs_html}
{nav_hint}
</div>'''
