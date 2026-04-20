#!/usr/bin/env python3
"""Génère data/nerf-products.json pour les 81 articles restants.

Pour chaque article, extraction des infos depuis l'audit + enrichissement
automatique via templates par gamme. Conserve les 2 articles pilotes tels quels.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wp_client import WPClient


# Mapping des IDs de catégorie vers noms de gamme
CATEGORY_TO_GAMME = {
    7: 'Accessoires',
    12: 'Dart Tag',
    46: 'Elite',
    122: 'Fortnite',
    3: 'N-Strike',
    79: 'N-Strike Elite Mega',
    118: 'Nitro',
    64: 'Rebelle',
    109: 'Rival',
    26: 'Super Soaker',
    19: 'Vortex',
    112: 'Blog',
    114: 'Vu sur le web',
}

# Defaults par gamme
GAMME_DEFAULTS = {
    'N-Strike': {
        'portee_m': 10,
        'munitions': 'N-Strike (fléchettes classiques Nerf)',
        'mecanisme': 'piston à ressort',
        'age_min': 8,
        'points_forts': [
            'Mécanisme à ressort fiable et simple à utiliser, sans besoin de piles',
            'Compatible avec les fléchettes Nerf N-Strike et Elite standard',
            'Prise en main accessible aux joueurs débutants',
            'Design robuste résistant aux manipulations intensives des parties Nerf',
            'Prix généralement accessible par rapport aux modèles plus récents',
        ],
        'points_faibles': [
            'Portée inférieure aux modèles Elite récents (10-12m contre 20-27m)',
            'Design vieillissant pour les produits les plus anciens de la gamme',
            'Précision correcte uniquement à courte et moyenne distance',
        ],
        'cas_usage': 'les débutants et les battles Nerf en intérieur',
    },
    'Elite': {
        'portee_m': 22,
        'munitions': 'Elite (fléchettes bleues optimisées)',
        'mecanisme': 'piston à ressort',
        'age_min': 8,
        'points_forts': [
            'Portée remarquable de 22 à 27 mètres grâce aux fléchettes Elite optimisées',
            'Précision nettement améliorée par rapport à la gamme N-Strike classique',
            'Design moderne et ergonomique pensé pour le confort de jeu',
            'Compatibilité avec les accessoires Nerf tactiques (viseurs, chargeurs)',
            'Performance homogène lors des parties longues',
        ],
        'points_faibles': [
            'Tarif légèrement supérieur aux modèles N-Strike originaux',
            'Taille parfois imposante pour les plus jeunes joueurs',
            'Fléchettes Elite spécifiques à privilégier pour des performances optimales',
        ],
        'cas_usage': 'les joueurs confirmés et les battles intérieures comme extérieures',
    },
    'N-Strike Elite Mega': {
        'portee_m': 27,
        'munitions': 'Mega (fléchettes surdimensionnées)',
        'mecanisme': 'piston à ressort',
        'age_min': 8,
        'points_forts': [
            'Fléchettes Mega surdimensionnées qui produisent un sifflement caractéristique en vol',
            'Portée impressionnante allant jusqu\'à 27 mètres',
            'Effet visuel et sonore immersif qui plaît énormément aux enfants',
            'Prise en main généreuse grâce à la taille imposante du blaster',
            'Précision correcte sur distances moyennes',
        ],
        'points_faibles': [
            'Cadence de tir plus lente que les blasters à fléchettes classiques',
            'Capacité de chargeur souvent limitée par la taille des Mega',
            'Recharges Mega plus onéreuses que les fléchettes standard',
            'Encombrement du blaster peu pratique pour les déplacements rapides',
        ],
        'cas_usage': 'les joueurs qui recherchent une expérience Nerf spectaculaire et immersive',
    },
    'Dart Tag': {
        'portee_m': 9,
        'munitions': 'Dart Tag (fléchettes à tête velcro)',
        'mecanisme': 'piston à ressort',
        'age_min': 6,
        'points_forts': [
            'Fléchettes à tête velcro spécialement conçues pour le jeu en équipe Dart Tag',
            'Compatible avec les vestes Dart Tag officielles pour des parties organisées',
            'Cadence de tir rapide adaptée aux tournois et compétitions',
            'Format compact et maniable en pleine action',
            'Idéal pour des parties structurées en équipe',
        ],
        'points_faibles': [
            'Fléchettes Dart Tag spécifiques moins polyvalentes que les classiques',
            'Portée inférieure aux gammes Elite modernes',
            'Gamme Dart Tag moins distribuée aujourd\'hui, fléchettes plus difficiles à trouver',
        ],
        'cas_usage': 'les parties Dart Tag en équipe et les tournois organisés',
    },
    'Vortex': {
        'portee_m': 20,
        'munitions': 'Vortex (disques aérodynamiques XLR)',
        'mecanisme': 'piston à ressort',
        'age_min': 6,
        'points_forts': [
            'Utilise des disques XLR aérodynamiques pour une portée remarquable',
            'Trajectoire stabilisée sur de longues distances',
            'Design futuriste qui démarque la gamme des autres blasters Nerf',
            'Précision correcte sur distances longues',
            'Expérience de tir originale et différente',
        ],
        'points_faibles': [
            'Les disques XLR ne peuvent pas être utilisés avec les autres blasters Nerf',
            'Gamme moins distribuée aujourd\'hui, disques plus difficiles à trouver',
            'Moins polyvalent que les blasters à fléchettes classiques',
        ],
        'cas_usage': 'les joueurs à la recherche d\'une expérience Nerf originale et différente des fléchettes',
    },
    'Rebelle': {
        'portee_m': 22,
        'munitions': 'Elite (fléchettes compatibles)',
        'mecanisme': 'variable selon le modèle',
        'age_min': 8,
        'points_forts': [
            'Design coloré et élégant conçu pour les joueuses',
            'Performances dignes de la gamme Elite (portée 22m)',
            'Fonctionnalités créatives : arcs, arbalètes, messages cachés',
            'Fléchettes compatibles avec les autres gammes Nerf',
            'Esthétique travaillée et packaging premium',
        ],
        'points_faibles': [
            'Gamme parfois moins mise en avant que les autres lignes Nerf',
            'Disponibilité variable selon les modèles',
        ],
        'cas_usage': 'les joueuses qui recherchent un blaster performant avec un design adapté',
    },
    'Super Soaker': {
        'portee_m': 10,
        'munitions': 'Eau',
        'mecanisme': 'variable (pompe, piles, pression)',
        'age_min': 6,
        'points_forts': [
            'Alternative estivale aux blasters à fléchettes classiques',
            'Capacité généreuse pour de longues batailles d\'eau',
            'Portée efficace sur plusieurs mètres',
            'Design robuste conçu pour résister aux jeux extérieurs',
            'Idéal pour les journées chaudes et les fêtes d\'été',
        ],
        'points_faibles': [
            'Utilisation uniquement en extérieur (eau)',
            'Nécessite un remplissage régulier pendant les parties',
            'Saisonnalité marquée (surtout utilisé en été)',
        ],
        'cas_usage': 'les batailles d\'eau en extérieur lors des journées chaudes',
    },
    'Rival': {
        'portee_m': 30,
        'munitions': 'Rival (billes en mousse haute vélocité)',
        'mecanisme': 'variable selon le modèle',
        'age_min': 14,
        'points_forts': [
            'Vélocité extrême jusqu\'à 30 m/s (100 fps), la plus élevée de la gamme Nerf',
            'Utilise des billes en mousse à haute performance',
            'Précision remarquable sur longues distances',
            'Cadence de tir élevée sur les modèles motorisés',
            'Qualité de construction premium, destinée aux adolescents et adultes',
        ],
        'points_faibles': [
            'Âge minimum de 14 ans recommandé, non adapté aux jeunes enfants',
            'Impact plus important des billes, à utiliser avec des protections',
            'Tarif supérieur aux autres gammes Nerf',
        ],
        'cas_usage': 'les joueurs adolescents et adultes recherchant des performances extrêmes',
    },
    'Fortnite': {
        'portee_m': 22,
        'munitions': 'Elite (fléchettes compatibles)',
        'mecanisme': 'variable selon le modèle',
        'age_min': 8,
        'points_forts': [
            'Réplique fidèle des armes emblématiques du jeu vidéo Fortnite',
            'Collaboration officielle entre Hasbro et Epic Games',
            'Design coloré et reconnaissable pour les fans du jeu',
            'Performances dignes de la gamme Elite (portée 22m)',
            'Compatible avec les fléchettes Nerf Elite standard',
        ],
        'points_faibles': [
            'Prix légèrement supérieur en raison de la licence Fortnite',
            'Intérêt limité pour les non-fans du jeu',
        ],
        'cas_usage': 'les fans de Fortnite qui souhaitent retrouver leurs armes préférées dans la vraie vie',
    },
    'Nitro': {
        'portee_m': 5,
        'munitions': 'Voitures en mousse Nitro',
        'mecanisme': 'ressort pneumatique',
        'age_min': 5,
        'points_forts': [
            'Concept original : tire des voitures en mousse sur des rampes',
            'Idéal pour les cascades et les circuits de voitures',
            'Expérience ludique mélangeant tir et voitures',
            'Adapté aux plus jeunes enfants',
            'Permet de créer des parcours créatifs',
        ],
        'points_faibles': [
            'Gamme plus limitée que les blasters à fléchettes',
            'Circuit nécessaire pour tirer le meilleur parti du concept',
            'Portée très courte par rapport aux autres gammes Nerf',
        ],
        'cas_usage': 'les jeunes enfants qui aiment à la fois les voitures et le jeu de tir',
    },
    'Accessoires': {
        'portee_m': None,
        'munitions': 'Varie selon le modèle',
        'mecanisme': None,
        'age_min': 6,
        'points_forts': [
            'Complément indispensable pour enrichir votre arsenal Nerf',
            'Compatibilité avec les différentes gammes de blasters Nerf',
            'Améliore le confort et l\'efficacité lors des parties',
            'Qualité de fabrication Hasbro officielle',
            'Apporte une dimension tactique supplémentaire au jeu',
        ],
        'points_faibles': [
            'Accessoire complémentaire plutôt qu\'essentiel',
            'Compatibilité à vérifier selon le modèle de blaster',
        ],
        'cas_usage': 'les joueurs qui souhaitent optimiser leur setup Nerf avec du matériel dédié',
    },
}

# Templates de description génériques par gamme
DESCRIPTION_TEMPLATES = {
    'N-Strike': "Blaster Nerf classique de la gamme N-Strike, conçu par Hasbro pour les battles en intérieur et les débutants",
    'Elite': "Blaster Nerf moderne de la gamme Elite, offrant une portée et une précision améliorées par rapport aux modèles N-Strike originaux",
    'N-Strike Elite Mega': "Blaster Nerf de la gamme Mega, reconnaissable à ses fléchettes surdimensionnées qui sifflent en vol",
    'Dart Tag': "Blaster Nerf de la gamme Dart Tag, optimisé pour le jeu en équipe avec fléchettes à tête velcro",
    'Vortex': "Blaster Nerf de la gamme Vortex, utilisant des disques aérodynamiques XLR pour une portée exceptionnelle",
    'Rebelle': "Blaster Nerf de la gamme Rebelle, au design coloré et élégant conçu spécialement pour les joueuses",
    'Super Soaker': "Blaster à eau de la gamme Super Soaker, idéal pour les batailles d'été en extérieur",
    'Rival': "Blaster Nerf haut de gamme Rival, tirant des billes en mousse à haute vélocité pour les joueurs confirmés",
    'Fortnite': "Blaster Nerf Fortnite, réplique officielle des armes emblématiques du jeu vidéo Epic Games",
    'Nitro': "Blaster Nerf Nitro, qui tire des voitures en mousse sur des rampes et circuits pour des cascades spectaculaires",
    'Accessoires': "Accessoire Nerf officiel qui complète et améliore votre arsenal de blasters",
}


def clean_title(raw_title):
    """Nettoie un titre brut WordPress."""
    t = html.unescape(raw_title)
    t = t.replace('\u2013', '-').replace('\u2014', '-').replace('\u2019', "'")
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def make_product_from_article(article, content_raw=''):
    """Génère les données produit à partir de l'audit."""
    name = clean_title(article['title'])
    # Si le titre ne commence pas par "Nerf", on le préfixe pour les CTA
    cta_name = name if name.lower().startswith('nerf') else f"Nerf {name}"

    # Extraction gamme depuis catégories
    cat_ids = article['categories']
    gamme = 'N-Strike'  # fallback
    for cid in cat_ids:
        if cid in CATEGORY_TO_GAMME:
            g = CATEGORY_TO_GAMME[cid]
            if g not in ('Blog', 'Vu sur le web'):
                gamme = g
                break

    defaults = GAMME_DEFAULTS.get(gamme, GAMME_DEFAULTS['Elite'])
    description = DESCRIPTION_TEMPLATES.get(gamme, DESCRIPTION_TEMPLATES['Elite'])

    product = {
        'name': cta_name,
        'gamme': gamme,
        'portee_m': defaults['portee_m'],
        'munitions': defaults['munitions'],
        'mecanisme': defaults['mecanisme'],
        'age_min': defaults['age_min'],
        'description': description,
        'points_forts': defaults['points_forts'],
        'points_faibles': defaults['points_faibles'],
        'cas_usage': defaults['cas_usage'],
        'alternatives': [],
        'faq_overrides': [
            {
                'q': f"Où acheter le {cta_name} ?",
                'a': f"Le {cta_name} est disponible sur Amazon.fr. Utilisez le bouton en bas de cet article pour accéder directement aux offres et comparer les prix."
            },
            {
                'q': f"Quelle est la portée du {cta_name} ?" if defaults['portee_m'] else f"Comment utiliser le {cta_name} ?",
                'a': (f"Le {cta_name} affiche une portée d'environ {defaults['portee_m']} mètres dans des conditions normales d'utilisation (tir horizontal, fléchettes officielles Nerf en bon état)."
                      if defaults['portee_m']
                      else f"Le {cta_name} s'utilise comme complément à votre arsenal Nerf existant. Consultez la notice incluse pour des instructions détaillées d'utilisation.")
            },
            {
                'q': f"Le {cta_name} est-il compatible avec les autres Nerf ?",
                'a': f"Le {cta_name} utilise des munitions {defaults['munitions']}. Vérifiez la compatibilité avec vos autres blasters pour mutualiser les recharges et optimiser votre setup."
            },
        ],
    }
    return product


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    audit_path = os.path.join(base, '..', 'data', 'posts-to-update.json')
    products_path = os.path.join(base, '..', 'data', 'nerf-products.json')

    with open(audit_path) as f:
        audit = json.load(f)

    # Charge la base existante (contient les pilotes)
    with open(products_path) as f:
        products = json.load(f)

    existing_ids = set(products.keys())
    print(f"Existing product entries: {len(existing_ids)}")

    generated = 0
    skipped = 0
    for article in audit['posts']:
        pid = str(article['id'])
        if pid in existing_ids:
            skipped += 1
            continue
        product = make_product_from_article(article)
        products[pid] = product
        generated += 1

    with open(products_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated {generated} new entries (skipped {skipped} existing)")
    print(f"   Total: {len(products)}")
    print(f"   Saved to: {products_path}")


if __name__ == '__main__':
    main()
