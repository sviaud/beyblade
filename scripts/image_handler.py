"""Détection et wrapping des images produit."""
import re
import html as html_mod


IMG_PATTERN = re.compile(r'<img[^>]+>', re.I)
SRC_PATTERN = re.compile(r'src=["\'](.*?)["\']', re.I)
ALT_PATTERN = re.compile(r'alt=["\'](.*?)["\']', re.I)
WIDTH_PATTERN = re.compile(r'width=["\'](\d+)["\']', re.I)
HEIGHT_PATTERN = re.compile(r'height=["\'](\d+)["\']', re.I)


def extract_first_image(content_raw):
    """Extrait la première image d'un contenu WP brut."""
    match = IMG_PATTERN.search(content_raw)
    if not match:
        return None
    img_tag = match.group(0)
    src = SRC_PATTERN.search(img_tag)
    if not src:
        return None
    return {
        'src': src.group(1),
        'alt': (ALT_PATTERN.search(img_tag).group(1) if ALT_PATTERN.search(img_tag) else ''),
        'width': (WIDTH_PATTERN.search(img_tag).group(1) if WIDTH_PATTERN.search(img_tag) else None),
        'height': (HEIGHT_PATTERN.search(img_tag).group(1) if HEIGHT_PATTERN.search(img_tag) else None),
    }


def build_wrapped_figure(image, amazon_url, product_name):
    """Construit un bloc <figure> avec image wrappée dans un lien affilié."""
    if not image:
        return ''
    src = html_mod.escape(image['src'])
    new_alt = html_mod.escape(f"{product_name} — blaster Nerf officiel")
    dims = ''
    if image.get('width') and image.get('height'):
        dims = f' width="{image["width"]}" height="{image["height"]}"'
    caption = html_mod.escape(f"Le {product_name} — disponible sur Amazon")
    return f'''<figure class="wp-block-image size-large aligncenter">
<a href="{amazon_url}" target="_blank" rel="nofollow sponsored noopener">
<img src="{src}" alt="{new_alt}"{dims} />
</a>
<figcaption>{caption}</figcaption>
</figure>'''
