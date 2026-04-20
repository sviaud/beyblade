"""Génération du bloc "Notre avis" Beyblade.

Refonte complète depuis pistoletnerf-refonte/scripts/rating_box.py :
- Nouveaux critères : Puissance / Endurance / Défense / Précision / Durabilité
- Nouveau Type catégoriel : Attaque / Défense / Stamina / Équilibre
- Palette dark mode + accent bleu électrique #0099ff
- Pas d'affichage de prix (décision validée — voir memory beyblade_blog_editorial)
- HTML aligné sur la maquette mockups/02-article-produit.html
"""
import html as html_mod


CRITERIA_LABELS = {
    'puissance':  'Puissance',
    'endurance':  'Endurance',
    'defense':    'Défense',
    'precision':  'Précision',
    'durabilite': 'Durabilité',
}

CRITERIA_ORDER = ('puissance', 'endurance', 'defense', 'precision', 'durabilite')

TYPE_LABELS = {
    'attaque':   'Attaque',
    'defense':   'Défense',
    'stamina':   'Stamina',
    'equilibre': 'Équilibre',
}

TYPE_COLORS = {
    'attaque':   '#ff3d00',  # orange/rouge énergie
    'defense':   '#0099ff',  # bleu accent
    'stamina':   '#00d68f',  # vert
    'equilibre': '#ffb800',  # or champion
}


# ============================================================
#   HEURISTIQUES DE NOTATION (override possible via product['ratings'])
# ============================================================

def _score_puissance(product):
    """Force d'impact : type + poids."""
    t = product.get('type', 'equilibre')
    weight = product.get('weight_g') or 33  # poids moyen par défaut
    base = {
        'attaque':   8.5,
        'equilibre': 7.5,
        'stamina':   6.5,
        'defense':   7.0,
    }.get(t, 7.0)
    # +0.3 par 2g au-dessus de 33g (jusqu'à +1.0)
    bonus = min(1.0, max(0.0, (weight - 33) * 0.15))
    return round(min(9.8, base + bonus), 1)


def _score_endurance(product):
    """Durée de spin : type + bit/driver."""
    t = product.get('type', 'equilibre')
    bit = (product.get('bit') or product.get('driver') or '').upper()
    base = {
        'stamina':   9.0,
        'equilibre': 7.5,
        'defense':   7.0,
        'attaque':   6.5,
    }.get(t, 7.0)
    # Modificateurs par type de pointe
    if any(x in bit for x in ['BALL', 'NEEDLE', 'TAPER']):
        base += 0.5
    elif any(x in bit for x in ['FLAT', 'RUBBER']):
        base -= 0.8
    return round(max(5.0, min(9.8, base)), 1)


def _score_defense(product):
    """Capacité d'encaissement : type + poids + gamme."""
    t = product.get('type', 'equilibre')
    weight = product.get('weight_g') or 33
    base = {
        'defense':   9.0,
        'equilibre': 7.5,
        'stamina':   7.0,
        'attaque':   6.5,
    }.get(t, 7.0)
    bonus = min(1.0, max(0.0, (weight - 33) * 0.12))
    return round(min(9.5, base + bonus), 1)


def _score_precision(product):
    """Reproductibilité de la trajectoire : bit + gamme."""
    gamme = product.get('gamme', '')
    bit = (product.get('bit') or product.get('driver') or '').upper()
    base = {
        'beyblade-x':              8.0,  # nouveau lanceur Xtreme = très précis
        'beyblade-burst':          7.0,
        'beyblade-metal-fusion':   6.5,
    }.get(gamme, 7.0)
    if any(x in bit for x in ['POINT', 'NEEDLE', 'SHARP']):
        base += 1.0
    elif 'FLAT' in bit:
        base += 0.3
    return round(max(5.0, min(9.5, base)), 1)


def _score_durabilite(product):
    """Résistance dans le temps : année + gamme."""
    year = product.get('year')
    gamme = product.get('gamme', '')
    base = {
        'beyblade-x':              8.5,
        'beyblade-burst':          8.0,
        'beyblade-metal-fusion':   8.5,  # parties métalliques très solides
    }.get(gamme, 7.5)
    if year and isinstance(year, int):
        if year >= 2024:
            base += 0.3
        elif year < 2014:
            base -= 0.3
    return round(max(5.0, min(9.5, base)), 1)


def compute_ratings(product):
    """Retourne un dict de scores calculés, écrasables par product['ratings']."""
    overrides = product.get('ratings') or {}
    scores = {
        'puissance':  overrides.get('puissance',  _score_puissance(product)),
        'endurance':  overrides.get('endurance',  _score_endurance(product)),
        'defense':    overrides.get('defense',    _score_defense(product)),
        'precision':  overrides.get('precision',  _score_precision(product)),
        'durabilite': overrides.get('durabilite', _score_durabilite(product)),
    }
    # Note globale : moyenne pondérée selon le type de la toupie
    t = product.get('type', 'equilibre')
    weights = _weights_for_type(t)
    total = sum(scores[k] * weights[k] for k in CRITERIA_ORDER)
    weight_sum = sum(weights[k] for k in CRITERIA_ORDER)
    global_score = round(total / weight_sum * 10) / 10
    scores['global'] = overrides.get('global', global_score)
    return scores


def _weights_for_type(t):
    """Poids des critères selon le type — une attaquante est notée différemment d'une stamina."""
    profiles = {
        'attaque':   {'puissance': 1.5, 'endurance': 0.8, 'defense': 0.9, 'precision': 1.3, 'durabilite': 1.0},
        'defense':   {'puissance': 0.9, 'endurance': 1.1, 'defense': 1.5, 'precision': 1.0, 'durabilite': 1.2},
        'stamina':   {'puissance': 0.8, 'endurance': 1.5, 'defense': 1.0, 'precision': 1.0, 'durabilite': 1.1},
        'equilibre': {'puissance': 1.1, 'endurance': 1.1, 'defense': 1.1, 'precision': 1.1, 'durabilite': 1.0},
    }
    return profiles.get(t, profiles['equilibre'])


def grade_label(global_score):
    """Convertit la note en label court (Excellent / Très bien / Bien / Correct)."""
    if global_score >= 9.0: return 'Excellent'
    if global_score >= 8.0: return 'Très bien'
    if global_score >= 7.0: return 'Bien'
    if global_score >= 6.0: return 'Correct'
    return 'Passable'


# ============================================================
#   GÉNÉRATION HTML
# ============================================================

def _stat_row_html(label, score):
    """Une ligne de stat avec barre + chiffre — match la maquette."""
    pct = max(0, min(100, score * 10))
    return f'''<div class="bb-stat-row">
<span class="bb-stat-label">{label}</span>
<div class="bb-stat-bar"><div class="bb-stat-fill" style="width:{pct}%;"></div></div>
<span class="bb-stat-num">{score:.1f}</span>
</div>'''


def _type_badge_html(type_key):
    """Badge Type (Attaque/Défense/Stamina/Équilibre)."""
    label = TYPE_LABELS.get(type_key, 'Équilibre')
    color = TYPE_COLORS.get(type_key, '#ffb800')
    return f'<span class="bb-type-badge" style="--bb-type-color:{color};">{label}</span>'


def _carousel_html(carousel_images, fallback_image, product_name, amazon_url):
    """Carrousel : photo principale (qui tourne) + vignettes."""
    images = carousel_images or []
    if not images and fallback_image:
        images = [{'src': fallback_image['src'], 'alt': f'{product_name} — toupie Beyblade officielle'}]
    if not images:
        return ''

    main_src = html_mod.escape(images[0]['src'])
    main_alt = html_mod.escape(images[0].get('alt', product_name))
    url_esc = html_mod.escape(amazon_url)

    main = (
        f'<a href="{url_esc}" target="_blank" rel="nofollow sponsored noopener">'
        f'<div class="bb-carousel-main">'
        f'<div class="bb-photo-spinner">'
        f'<img id="bb-main-img" src="{main_src}" alt="{main_alt}" />'
        f'</div>'
        f'</div></a>'
    )

    thumbs_html = ''
    if len(images) > 1:
        thumbs = []
        for idx, img in enumerate(images):
            src = html_mod.escape(img['src'])
            alt = html_mod.escape(img.get('alt', f'Photo {idx+1}'))
            active_cls = ' active' if idx == 0 else ''
            thumbs.append(
                f'<div class="bb-thumb{active_cls}" '
                f'onclick="(function(t){{'
                f'  var box=t.closest(\'.bb-carousel\');'
                f'  box.querySelector(\'#bb-main-img\').src=t.querySelector(\'img\').src;'
                f'  box.querySelectorAll(\'.bb-thumb\').forEach(function(x){{x.classList.remove(\'active\')}});'
                f'  t.classList.add(\'active\');'
                f'}})(this)">'
                f'<img src="{src}" alt="{alt}" />'
                f'</div>'
            )
        thumbs_html = f'<div class="bb-thumbs">{"".join(thumbs)}</div>'

    return f'<div class="bb-carousel">{main}{thumbs_html}</div>'


def _stats_html(scores):
    return ''.join(
        _stat_row_html(CRITERIA_LABELS[k], scores[k])
        for k in CRITERIA_ORDER
    )


def build_review_block(product, carousel_images, amazon_url, fallback_image=None):
    """Bloc "Notre avis" full-width : carrousel + stats + CTA Amazon.

    Args:
        product: dict — clés attendues : name, reference, gamme, type, year,
                 weight_g (opt), bit/driver (opt), ratings (opt overrides)
        carousel_images: list[dict] — [{'src': url, 'alt': text}, ...]
        amazon_url: str — lien d'affiliation Amazon
        fallback_image: dict|None — {'src': url} si pas d'images carousel
    """
    scores = compute_ratings(product)
    name = html_mod.escape(product['name'])
    reference = html_mod.escape(product.get('reference', ''))
    gamme_label = {
        'beyblade-x':            'Beyblade X',
        'beyblade-burst':        'Beyblade Burst',
        'beyblade-metal-fusion': 'Metal Fusion',
    }.get(product.get('gamme'), 'Beyblade')
    year = product.get('year', '')
    type_key = product.get('type', 'equilibre')
    label = grade_label(scores['global'])
    url_esc = html_mod.escape(amazon_url)

    meta_line = f'{gamme_label} · {reference} · {year}' if reference else f'{gamme_label} · {year}'

    return f'''<div class="bb-review-block">
<div class="bb-review-header">
<div class="bb-review-title">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="12 2 15 8.5 22 9.3 17 14 18.5 21 12 17.7 5.5 21 7 14 2 9.3 9 8.5"/></svg>
Notre verdict
</div>
<div class="bb-review-grade">
<div>
<span class="bb-grade-label">{label}</span>
<div class="bb-grade-meta">Note globale</div>
</div>
<div class="bb-grade-num">{scores['global']:.1f}<small>/10</small></div>
</div>
</div>
<div class="bb-review-body">
{_carousel_html(carousel_images, fallback_image, product['name'], amazon_url)}
<div class="bb-rating-side">
<h3 class="bb-product-name">{name}</h3>
<div class="bb-product-meta">{html_mod.escape(meta_line)}</div>
{_type_badge_html(type_key)}
<div class="bb-stats">{_stats_html(scores)}</div>
<div class="bb-availability">
<span class="bb-dot"></span>
<span>En stock sur Amazon FR</span>
</div>
<a href="{url_esc}" target="_blank" rel="nofollow sponsored noopener" class="bb-cta">
▶ Voir le prix sur Amazon
</a>
<div class="bb-disclaimer">Lien d'affiliation · Achat sans surcoût pour vous</div>
</div>
</div>
</div>'''


def build_rating_box_compact(product):
    """Version compacte (sans carrousel) — pour intégration en sidebar ou cards."""
    scores = compute_ratings(product)
    name = html_mod.escape(product['name'])
    type_key = product.get('type', 'equilibre')

    return f'''<div class="bb-rating-box-compact">
<div class="bb-rb-header">
<span class="bb-rb-name">{name}</span>
<div class="bb-rb-grade">{scores['global']:.1f}<small>/10</small></div>
</div>
{_type_badge_html(type_key)}
<div class="bb-stats">{_stats_html(scores)}</div>
</div>'''


# ============================================================
#   DEBUG / DRY-RUN
# ============================================================
if __name__ == '__main__':
    sample_product = {
        'name': 'Dranzer Spiral 3-60P',
        'reference': 'BX-42',
        'gamme': 'beyblade-x',
        'type': 'attaque',
        'year': 2026,
        'weight_g': 34,
        'blade': 'Helical',
        'ratchet': '3-60',
        'bit': 'P',
    }
    scores = compute_ratings(sample_product)
    print(f"Scores Dranzer Spiral : {scores}")
    print(f"Label : {grade_label(scores['global'])}")
    print()
    sample_url = 'https://www.amazon.fr/s?k=Dranzer+Spiral+3-60P&tag=beyblade0a-21'
    print("--- HTML output (first 600 chars) ---")
    print(build_review_block(sample_product, [], sample_url)[:600])
