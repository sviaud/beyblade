"""Générateur de tableaux comparatifs par catégorie.

Remplace l'ancien plugin SuperChartBoy cassé. Les lignes sont triées
par note globale décroissante.
"""
import html as html_mod

from rating_box import compute_ratings


def _progress_bar(score, max_score=10):
    """Mini barre de progression HTML inline, colorée selon le score."""
    pct = (score / max_score) * 100
    # Couleur selon le score : rouge < 6, orange < 7.5, vert clair < 8.5, vert foncé >= 8.5
    if score >= 8.5:
        color = '#2e7d32'
    elif score >= 7.5:
        color = '#7cb342'
    elif score >= 6.5:
        color = '#fbc02d'
    elif score >= 5.5:
        color = '#fb8c00'
    else:
        color = '#e53935'
    return (
        f'<div style="background:#eee;border-radius:4px;height:8px;overflow:hidden;min-width:60px;">'
        f'<div style="background:{color};height:100%;width:{pct:.0f}%;"></div>'
        f'</div>'
    )


def _score_badge(score):
    """Badge de note globale avec fond coloré."""
    if score >= 8.5:
        bg = '#2e7d32'
    elif score >= 7.5:
        bg = '#7cb342'
    elif score >= 6.5:
        bg = '#fbc02d'
    elif score >= 5.5:
        bg = '#fb8c00'
    else:
        bg = '#e53935'
    return (
        f'<div style="display:inline-block;background:{bg};color:#fff;border-radius:6px;'
        f'padding:8px 12px;font-weight:bold;font-size:18px;min-width:48px;text-align:center;">'
        f'{score:.1f}</div>'
    )


def build_comparison_row(entry, rank):
    """Construit une ligne de comparaison pour un produit."""
    product = entry['product']
    scores = compute_ratings(product)
    name = html_mod.escape(product['name'])
    image_src = entry.get('image_src') or ''
    permalink = entry.get('permalink') or '#'
    permalink_escaped = html_mod.escape(permalink)
    amazon_url = entry.get('amazon_url') or ''
    amazon_url_escaped = html_mod.escape(amazon_url)

    image_cell = ''
    if image_src:
        image_cell = (
            f'<a href="{permalink_escaped}" style="display:block;">'
            f'<img src="{html_mod.escape(image_src)}" alt="{name}" '
            f'style="width:90px;height:90px;object-fit:contain;background:#fff;border-radius:6px;" />'
            f'</a>'
        )
    else:
        image_cell = (
            f'<div style="width:90px;height:90px;background:#f5f5f5;border-radius:6px;'
            f'display:flex;align-items:center;justify-content:center;color:#ccc;">—</div>'
        )

    rank_badge = (
        f'<span style="display:inline-block;background:#333;color:#fff;border-radius:50%;'
        f'width:28px;height:28px;line-height:28px;text-align:center;font-size:13px;font-weight:bold;">'
        f'{rank}</span>'
    )

    criteria_rows = []
    labels = [('Portée', 'portee'), ('Précision', 'precision'), ('Fiabilité', 'fiabilite'), ('Cadence', 'cadence'), ('Capacité', 'capacite')]
    for label, key in labels:
        s = scores[key]
        criteria_rows.append(
            f'<tr>'
            f'<td style="padding:2px 6px 2px 0;color:#666;font-size:12px;white-space:nowrap;">{label}</td>'
            f'<td style="padding:2px 6px;width:100%;">{_progress_bar(s)}</td>'
            f'<td style="padding:2px 0;font-size:12px;color:#333;text-align:right;white-space:nowrap;"><strong>{s:.1f}</strong></td>'
            f'</tr>'
        )
    criteria_table = (
        '<table style="width:100%;border-collapse:collapse;">'
        + ''.join(criteria_rows)
        + '</table>'
    )

    amazon_btn = ''
    if amazon_url:
        amazon_btn = (
            f'<a href="{amazon_url_escaped}" target="_blank" rel="nofollow sponsored noopener" '
            f'style="display:inline-block;background:#ff9900;color:#fff;padding:8px 14px;'
            f'text-decoration:none;border-radius:4px;font-weight:bold;font-size:13px;margin-top:6px;">'
            f'Voir sur Amazon →</a>'
        )

    title_link = (
        f'<a href="{permalink_escaped}" style="color:#222;text-decoration:none;font-weight:bold;font-size:16px;">'
        f'{name}</a>'
    )

    return f'''<div class="nerf-compare-row" style="display:flex;flex-wrap:wrap;gap:16px;align-items:center;padding:16px;background:#fff;border:1px solid #e0e0e0;border-radius:8px;margin-bottom:12px;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
<div style="flex:0 0 auto;display:flex;align-items:center;gap:12px;">{rank_badge}{image_cell}</div>
<div style="flex:1 1 260px;min-width:220px;">
<div style="margin-bottom:6px;">{title_link}</div>
<div style="color:#888;font-size:12px;">{html_mod.escape(product.get('gamme', ''))}{(" · " + str(product.get('year'))) if product.get('year') else ''}</div>
{amazon_btn}
</div>
<div style="flex:1 1 280px;min-width:240px;">{criteria_table}</div>
<div style="flex:0 0 auto;text-align:center;">
<div style="font-size:11px;color:#888;text-transform:uppercase;margin-bottom:4px;">Note globale</div>
{_score_badge(scores['global'])}
</div>
</div>'''


def build_intro(gamme_name, gamme_ctx, count):
    return f'''<p>Bienvenue sur le <strong>comparatif complet des Nerf {html_mod.escape(gamme_name)}</strong>. Nous avons testé et noté <strong>{count} modèles</strong> de cette gamme pour vous aider à trouver celui qui correspond le mieux à vos besoins. Le classement ci-dessous est établi selon notre note globale, calculée à partir de cinq critères : portée, précision, fiabilité, fréquence de tir et capacité.</p>

<p>{html_mod.escape(gamme_ctx)}</p>

<p>Cliquez sur le nom d'un blaster pour accéder à son test complet, ou sur le bouton « Voir sur Amazon » pour consulter son prix actuel.</p>'''


def build_comparison_page(gamme_name, gamme_ctx, entries):
    """Génère le HTML complet d'une page comparatif.

    Args:
        gamme_name: nom de la gamme (ex: "Vortex")
        gamme_ctx: paragraphe de contexte sur la gamme
        entries: liste de {product, image_src, permalink, amazon_url, scores}
                 triée par score global décroissant
    """
    if not entries:
        return '<p>Aucun modèle disponible dans cette catégorie pour le moment.</p>'

    rows_html = '\n'.join(build_comparison_row(e, rank=i + 1) for i, e in enumerate(entries))

    intro = build_intro(gamme_name, gamme_ctx, len(entries))

    return f'''{intro}

<h2>Classement des Nerf {html_mod.escape(gamme_name)}</h2>

<div class="nerf-comparison-table" style="margin:2em 0;">
{rows_html}
</div>

<h2>Comment choisir son Nerf {html_mod.escape(gamme_name)} ?</h2>
<p>Pour bien choisir votre blaster Nerf, gardez à l'esprit les critères suivants :</p>
<ul>
<li><strong>L'âge du joueur</strong> : certains modèles sont recommandés à partir de 6 ans, d'autres à partir de 14 ans (gamme Rival).</li>
<li><strong>L'environnement de jeu</strong> : pour l'intérieur, privilégiez les modèles compacts avec une portée courte ; pour l'extérieur, optez pour les modèles longue portée.</li>
<li><strong>La cadence de tir</strong> : les blasters motorisés (à piles) permettent des tirs en rafale, les modèles à ressort sont plus précis et économes.</li>
<li><strong>La capacité du chargeur</strong> : un chargeur plus grand permet d'enchaîner plus de tirs avant de recharger, ce qui est un avantage certain en pleine partie.</li>
<li><strong>Le type de munitions</strong> : fléchettes classiques, Elite, Mega, Rival, disques Vortex... chacune a ses spécificités.</li>
</ul>

<h2>FAQ — Nerf {html_mod.escape(gamme_name)}</h2>
<h3>Quel est le meilleur Nerf {html_mod.escape(gamme_name)} ?</h3>
<p>D'après notre classement, le <strong>{html_mod.escape(entries[0]['product']['name'])}</strong> obtient la meilleure note globale ({compute_ratings(entries[0]['product'])['global']:.1f}/10) dans la gamme {html_mod.escape(gamme_name)}. Consultez son test complet pour découvrir ses atouts et limites en détail.</p>

<h3>Les Nerf {html_mod.escape(gamme_name)} sont-ils compatibles entre eux ?</h3>
<p>En règle générale, les blasters d'une même gamme Nerf partagent les mêmes munitions et accessoires. Vérifiez cependant les spécifications de chaque modèle avant d'acheter des recharges.</p>

<h3>Où acheter un Nerf {html_mod.escape(gamme_name)} ?</h3>
<p>Tous les modèles présentés dans ce comparatif sont disponibles sur Amazon.fr. Cliquez sur le bouton « Voir sur Amazon » à côté de chaque produit pour accéder directement à son offre et comparer les prix.</p>'''
