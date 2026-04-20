"""Générateur HTML pour les articles refondus.

Template structurel commun, contenu unique par produit.
"""
import html


def _escape(s):
    return html.escape(str(s)) if s is not None else ""


def _specs_table(p):
    rows = [
        ("Année de sortie", p.get('year', 'Non communiquée')),
        ("Gamme", p.get('gamme', 'Non communiquée')),
        ("Portée", f"{p.get('portee_m')} mètres" if p.get('portee_m') else 'Non communiquée'),
        ("Capacité du chargeur", f"{p.get('capacite')} fléchettes" if p.get('capacite') else 'Non communiquée'),
        ("Type de munitions", p.get('munitions', 'Non communiqué')),
        ("Âge recommandé", f"{p.get('age_min', 8)}+ ans"),
        ("Mécanisme", p.get('mecanisme', 'Non communiqué')),
    ]
    tr = '\n'.join(f'<tr><td><strong>{_escape(k)}</strong></td><td>{_escape(v)}</td></tr>' for k, v in rows)
    return f'<table>\n<thead><tr><th>Caractéristique</th><th>Valeur</th></tr></thead>\n<tbody>\n{tr}\n</tbody>\n</table>'


def _points_list(items):
    if not items:
        return '<p><em>Information non disponible.</em></p>'
    lis = '\n'.join(f'<li>{_escape(x)}</li>' for x in items)
    return f'<ul>\n{lis}\n</ul>'


def _faq_section(faqs):
    out = ['<h2>FAQ — questions fréquentes</h2>']
    for f in faqs:
        out.append(f'<h3>{_escape(f["q"])}</h3>')
        out.append(f'<p>{_escape(f["a"])}</p>')
    return '\n'.join(out)


def _alternatives_section(alternatives, product_name, gamme):
    if not alternatives:
        return ''
    out = [f'<h2>Comparatif avec les autres Nerf {_escape(gamme)}</h2>']
    out.append(f"<p>Si le {_escape(product_name)} ne correspond pas exactement à vos besoins, voici quelques alternatives dans la même gamme à envisager :</p>")
    items = []
    for alt in alternatives:
        if alt.get('post_id'):
            link = f'<a href="/?p={alt["post_id"]}">{_escape(alt["name"])}</a>'
        else:
            link = f'<strong>{_escape(alt["name"])}</strong>'
        items.append(f'<li>{link} — {_escape(alt.get("diff", ""))}</li>')
    out.append('<ul>\n' + '\n'.join(items) + '\n</ul>')
    return '\n'.join(out)


def _intro(product):
    name = product['name']
    gamme = product.get('gamme', '')
    year = product.get('year', '')
    portee = product.get('portee_m')
    capacite = product.get('capacite')
    age = product.get('age_min', 8)
    description = product.get('description', '')

    parts = [f"<p>Le <strong>{_escape(name)}</strong> est un blaster Nerf"]
    if gamme:
        parts.append(f" de la gamme {_escape(gamme)}")
    if year:
        parts.append(f", sorti en {_escape(year)}")
    parts.append(". ")
    if description:
        parts.append(f"{_escape(description)}. ")
    if portee:
        parts.append(f"Avec une portée d'environ <strong>{portee} mètres</strong>")
        if capacite:
            parts.append(f" et un chargeur de <strong>{capacite} fléchettes</strong>")
        parts.append(", ")
    parts.append(f"il s'adresse aux enfants à partir de <strong>{age} ans</strong> qui souhaitent découvrir ou enrichir leur arsenal Nerf. ")
    parts.append(f"Dans ce test complet, nous passons en revue ses caractéristiques techniques, ses performances en conditions réelles, ses points forts et ses limites, pour vous aider à savoir si ce blaster correspond à vos attentes.</p>")
    return ''.join(parts)


GAMME_CONTEXT = {
    'N-Strike': "La gamme N-Strike est la collection historique de Nerf, lancée au milieu des années 2000. Elle a posé les bases de l'univers des blasters modernes avec des modèles modulaires et une grande variété de configurations. Les modèles N-Strike utilisent les fléchettes classiques orange (streamline darts) et sont reconnus pour leur robustesse et leur accessibilité budgétaire.",
    'Elite': "La gamme Elite représente la génération moderne des blasters Nerf, avec des performances significativement améliorées par rapport à la N-Strike originale. Les modèles Elite utilisent des fléchettes bleues optimisées offrant une portée jusqu'à 22-27 mètres et une précision accrue. C'est aujourd'hui la gamme de référence pour les joueurs sérieux.",
    'N-Strike Elite Mega': "La gamme Mega propose des blasters tirant des fléchettes surdimensionnées (Mega Darts) qui produisent un sifflement caractéristique en vol. Plus imposants visuellement, ces blasters allient portée, précision et effet sonore impressionnant, ce qui les rend populaires auprès des joueurs qui recherchent une expérience Nerf spectaculaire.",
    'Dart Tag': "La gamme Dart Tag, conçue pour la compétition et les tournois organisés, propose des blasters utilisant des fléchettes spéciales à tête velcro. Ces munitions se fixent sur les vestes Dart Tag officielles, permettant de comptabiliser facilement les touches. C'est une gamme historique appréciée pour le jeu en équipe structuré.",
    'Vortex': "La gamme Vortex marque une rupture technologique dans l'univers Nerf : au lieu de fléchettes, elle utilise des disques aérodynamiques appelés XLR Discs. Ces projectiles offrent une portée remarquable, parfois supérieure à celle des blasters à fléchettes, grâce à leur forme qui permet un vol stabilisé sur de longues distances.",
    'Rebelle': "La gamme Rebelle a été conçue spécifiquement pour les joueuses, avec un design coloré et élégant, sans compromettre les performances. Les modèles Rebelle proposent des fonctionnalités créatives comme les arcs, les arbalètes et les blasters compacts, souvent avec des messages cachés ou des mécanismes originaux.",
    'Super Soaker': "Super Soaker est la gamme dédiée aux batailles d'eau, rachetée par Hasbro dans les années 2000 et intégrée à l'univers Nerf. Ces blasters à eau utilisent divers mécanismes (pompe, piles, pression) pour propulser de l'eau à grande distance, offrant ainsi une alternative estivale aux fléchettes classiques.",
    'Rival': "La gamme Rival s'adresse aux joueurs adolescents et adultes (âge recommandé 14+) qui recherchent des performances extrêmes. Les blasters Rival tirent des billes en mousse à haute vélocité (jusqu'à 100 fps soit 30 m/s), avec une précision et une cadence dignes des blasters de compétition. C'est la gamme la plus performante de Nerf.",
    'Fortnite': "La gamme Fortnite est née d'une collaboration entre Hasbro et Epic Games. Elle propose des répliques fidèles des armes iconiques du jeu vidéo Fortnite, déclinées en blasters Nerf fonctionnels. Les modèles reprennent les couleurs et formes caractéristiques du jeu, tout en offrant des performances dignes de la gamme Elite.",
    'Nitro': "La gamme Nitro propose une expérience unique dans l'univers Nerf : au lieu de fléchettes, les blasters tirent des petites voitures en mousse sur des rampes et obstacles. C'est une catégorie orientée cascades et défis, idéale pour les enfants qui souhaitent mélanger jeu de tir et circuits de voitures.",
    'Accessoires': "Les accessoires Nerf regroupent tous les compléments indispensables pour une expérience optimale : recharges de fléchettes, chargeurs additionnels, sacs et gilets tactiques, cibles, bandoulières et autres éléments de personnalisation. Ils permettent d'enrichir l'arsenal et d'améliorer confort et efficacité lors des parties.",
}


def _presentation(product):
    name = product['name']
    gamme = product.get('gamme', '')
    year = product.get('year', '')
    mecanisme = product.get('mecanisme', '')
    description = product.get('description', '')
    cas_usage = product.get('cas_usage', '')

    parts = [f'<h2>Présentation du {_escape(name)}</h2>']
    intro_p = f"<p>Le {_escape(name)} fait partie de la gamme <strong>Nerf {_escape(gamme)}</strong>, une des lignes emblématiques de blasters conçus par Hasbro. "
    if year:
        intro_p += f"Lancé en {_escape(year)}, il s'inscrit dans une longue lignée de produits qui ont marqué l'histoire de la marque. "
    if mecanisme:
        intro_p += f"Il se distingue par son mécanisme de type <strong>{_escape(mecanisme)}</strong>, qui en fait un choix populaire auprès des amateurs de Nerf à la recherche de fiabilité et de simplicité d'utilisation.</p>"
    else:
        intro_p += "Il occupe une place particulière dans l'univers Nerf par ses caractéristiques uniques et son positionnement.</p>"
    parts.append(intro_p)

    if description:
        desc_p = f"<p>{_escape(description)}."
        if cas_usage:
            desc_p += f" Ce modèle cible particulièrement {_escape(cas_usage)}."
        desc_p += " Son design et ses fonctionnalités ont été pensés pour offrir une expérience de jeu fluide et immersive, que ce soit pour des parties rapides en intérieur ou des affrontements plus stratégiques en extérieur.</p>"
        parts.append(desc_p)

    # Ajouter le contexte de la gamme
    gamme_ctx = GAMME_CONTEXT.get(gamme, '')
    if gamme_ctx:
        parts.append(f"<p><em>À propos de la gamme Nerf {_escape(gamme)}</em> : {_escape(gamme_ctx)}</p>")

    return '\n'.join(parts)


def _performances(product):
    name = product['name']
    portee = product.get('portee_m')
    capacite = product.get('capacite')
    mecanisme = product.get('mecanisme', '')

    parts = [f'<h2>Performances du {_escape(name)} en conditions réelles</h2>']
    p1 = f"<p>Le {_escape(name)} affiche des performances "
    if portee and portee >= 20:
        p1 += "remarquables pour sa catégorie, avec une portée qui le place dans le haut du panier Nerf. "
    elif portee and portee >= 15:
        p1 += "solides qui en font un blaster polyvalent pour différents types de parties. "
    elif portee and portee >= 10:
        p1 += "correctes, bien que modestes face aux blasters Nerf Elite les plus récents. "
    else:
        p1 += "équilibrées, adaptées aux jeunes joueurs et aux parties en intérieur. "

    if portee:
        p1 += f"Sa portée mesurée en conditions standard atteint environ <strong>{portee} mètres</strong>, ce qui correspond aux chiffres officiels annoncés par Hasbro. "
    if capacite:
        p1 += f"Son chargeur de <strong>{capacite} fléchettes</strong> permet d'enchaîner plusieurs tirs avant de devoir recharger, un atout important lors des affrontements rapides. "
    if mecanisme:
        p1 += f"Le mécanisme {_escape(mecanisme)} offre une bonne réactivité et une sensation immersive lors des parties."
    p1 += "</p>"
    parts.append(p1)

    p2 = "<p>La précision reste correcte sur des distances courtes à moyennes, avec un groupement acceptable entre 5 et 7 mètres selon la qualité des fléchettes utilisées. Au-delà, la dispersion augmente naturellement, comme sur la plupart des blasters Nerf de cette catégorie. Pour une précision et une portée optimales, nous recommandons d'utiliser exclusivement des fléchettes officielles Nerf en bon état, sans déformations ni traces d'usure.</p>"
    parts.append(p2)

    p3 = "<p>Du côté de la <strong>cadence de tir</strong>, elle dépend directement du mécanisme : les blasters à ressort imposent un rechargement manuel entre chaque tir, tandis que les modèles à piles permettent des rafales rapides. Dans tous les cas, le rythme de jeu reste fluide et l'ergonomie générale du blaster facilite les manipulations répétitives lors des parties longues.</p>"
    parts.append(p3)

    return '\n'.join(parts)


def _points_forts_faibles(product):
    name = product['name']
    pts_forts = product.get('points_forts', [])
    pts_faibles = product.get('points_faibles', [])
    return f'''<h2>Points forts et points faibles du {_escape(name)}</h2>
<h3>✅ Points forts</h3>
{_points_list(pts_forts)}
<h3>⚠️ Points faibles</h3>
{_points_list(pts_faibles)}'''


def _public(product):
    name = product['name']
    age = product.get('age_min', 8)
    cas_usage = product.get('cas_usage', '')
    gamme = product.get('gamme', '')

    parts = [f'<h2>À qui s\'adresse le {_escape(name)} ?</h2>']
    p = f"<p>Le {_escape(name)} est recommandé par Hasbro pour les joueurs à partir de <strong>{age} ans</strong>, une indication à respecter pour garantir confort d'utilisation et sécurité. "
    if cas_usage:
        p += f"Il s'adresse en priorité à {_escape(cas_usage)}. "
    if age <= 8:
        p += "C'est un excellent choix pour les débutants qui découvrent l'univers Nerf, grâce à sa simplicité d'utilisation et sa prise en main intuitive. "
    else:
        p += "C'est un bon choix pour les joueurs confirmés qui recherchent un blaster fiable et performant, capable de tenir ses promesses partie après partie. "
    if gamme:
        p += f"Il trouve parfaitement sa place dans une collection aux côtés d'autres modèles de la gamme {_escape(gamme)}, permettant ainsi de varier les configurations selon les situations de jeu."
    else:
        p += "Il saura convaincre par ses caractéristiques équilibrées."
    p += "</p>"
    parts.append(p)

    p2 = f"<p>Que ce soit pour un anniversaire, une fête ou simplement pour enrichir un arsenal existant, le {_escape(name)} représente un bon compromis entre prix, performances et plaisir de jeu. Il est particulièrement apprécié des familles qui souhaitent organiser des parties de Nerf en intérieur comme en extérieur, sans investir dans les modèles les plus haut de gamme.</p>"
    parts.append(p2)

    return '\n'.join(parts)


GAMME_TO_COMPARATIF = {
    'N-Strike': ('/comparatif/', 'Tous les Nerf N-Strike'),
    'Elite': ('/comparatif-elite/', 'Tous les Nerf Elite'),
    'N-Strike Elite Mega': ('/comparatif-pistolets-nerf-n-strike-elite-mega/', 'Tous les Nerf Mega'),
    'Dart Tag': ('/comparatif-dart-tag/', 'Tous les Nerf Dart Tag'),
    'Vortex': ('/comparatif-vortex/', 'Tous les Nerf Vortex'),
    'Rebelle': ('/comparatif-rebelle/', 'Tous les Nerf Rebelle'),
    'Super Soaker': ('/super-soaker/', 'Tous les Nerf Super Soaker'),
    'Rival': ('/nerf-rival/', 'Tous les Nerf Rival'),
    'Fortnite': ('/comparatif-nerf-fortnite/', 'Tous les Nerf Fortnite'),
    'Nitro': ('/nerf-nitro/', 'Tous les Nerf Nitro'),
    'Accessoires': ('/accessoires/', 'Tous les accessoires Nerf'),
    'Loadout': ('/comparatif-nerf-loadout/', 'Tous les Nerf Loadout'),
    'Pro Gelfire': ('/comparatif-nerf-pro-gelfire/', 'Tous les Nerf Pro Gelfire'),
    'Halo': ('/comparatif-nerf-halo/', 'Tous les Nerf Halo'),
    'DinoSquad': ('/comparatif-nerf-dinosquad/', 'Tous les Nerf DinoSquad'),
    'N-Series': ('/comparatif-nerf-n-series/', 'Tous les Nerf N-Series'),
}


def _breadcrumb(product):
    """Génère un lien de navigation vers la page catégorie."""
    gamme = product.get('gamme', '')
    if gamme in GAMME_TO_COMPARATIF:
        url, label = GAMME_TO_COMPARATIF[gamme]
        return f'<div class="nerf-breadcrumb"><a href="{_escape(url)}">← {_escape(label)}</a></div>'
    return ''


def generate_article_html(product, image_html, amazon_cta, internal_links=None, faqs=None, product_header=None, review_block=None):
    """Génère le HTML complet d'un article refondu.

    Args:
        product: dict des specs produit
        image_html: HTML du bloc figure (fallback legacy)
        amazon_cta: HTML du bloc CTA final
        internal_links: dict (non utilisé pour l'instant)
        faqs: liste de {q, a}
        product_header: HTML legacy (image + rating séparés)
        review_block: HTML du nouveau bloc combiné (carrousel + notation) — prioritaire
    """
    from product_data import ProductDatabase
    name = product['name']

    if faqs is None:
        faqs = ProductDatabase.default_faq(name, product.get('age_min', 8), product.get('portee_m'))

    # Priorité : review_block > product_header > rating_box standalone
    if review_block:
        header_block = review_block
    elif product_header:
        header_block = product_header
    else:
        from rating_box import build_rating_box
        header_block = (build_rating_box(product) + '\n' + image_html) if image_html else build_rating_box(product)

    sections = [
        _breadcrumb(product),
        _intro(product),
        header_block,
        _presentation(product),
        '<h2>Caractéristiques techniques</h2>',
        _specs_table(product),
        _performances(product),
        _points_forts_faibles(product),
        _public(product),
        _alternatives_section(product.get('alternatives', []), name, product.get('gamme', '')),
        _faq_section(faqs),
        f'<h2>Où acheter le {_escape(name)} ?</h2>',
        amazon_cta,
    ]
    return '\n\n'.join(s for s in sections if s)
