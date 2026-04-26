"""Source unique de vérité pour le catalogue des toupies Beyblade.

Chaque entrée représente une toupie (testée ou à venir) référencée sur le site.
- Les toupies "testées" ont un `slug` interne pointant vers leur fiche.
- Les toupies "à venir" ont `slug=None` et sont reliées à une recherche/dp Amazon.

Lu par :
- scripts/build.py → /tous-les-beyblade/ (catalogue complet sortable + filterable)
- (futur) refonte des comparatifs MF/X/Burst pour qu'ils lisent depuis cette source unique

Quand une toupie "à venir" est testée, mettre à jour : slug, score, image (si dispo).
"""

# ============ Métadonnées de référence ============

GAMMES = {
    'beyblade-x': {
        'label': 'Beyblade X',
        'short': 'X',
        'years': '2023→',
        'comparatif_url': '/comparatif-beyblade-x/',
    },
    'beyblade-burst': {
        'label': 'Beyblade Burst',
        'short': 'Burst',
        'years': '2016-2023',
        'comparatif_url': '/comparatif-beyblade-burst/',
    },
    'beyblade-metal-fusion': {
        'label': 'Metal Fusion',
        'short': 'MF',
        'years': '2010-2013',
        'comparatif_url': '/comparatif-beyblade-metal-fusion/',
    },
}

TYPES = {
    'attaque':         {'label': 'Attaque',           'badge_class': 'type-attack',   'filter_key': 'attaque'},
    'attaque-gauche':  {'label': 'Attaque (gauche)',  'badge_class': 'type-attack',   'filter_key': 'attaque'},
    'defense':         {'label': 'Défense',           'badge_class': 'type-defense',  'filter_key': 'defense'},
    'stamina':         {'label': 'Stamina',           'badge_class': 'type-stamina',  'filter_key': 'stamina'},
    'stamina-gauche':  {'label': 'Stamina (gauche)',  'badge_class': 'type-stamina',  'filter_key': 'stamina'},
    'equilibre':       {'label': 'Équilibre',         'badge_class': 'type-balance',  'filter_key': 'equilibre'},
}

# ============ Catalogue ============
#
# Champs obligatoires :
#   name (str)        — nom complet "Cobalt Dragoon 2-60C"
#   ref (str)         — référence officielle "BX-34" / "F3966" / "BB-30"
#   gamme (str)       — clé de GAMMES
#   type (str)        — clé de TYPES
#   year (int)        — année de sortie
#
# Champs optionnels :
#   slug (str|None)   — slug de la fiche interne, ou None si non testée
#   score (float|None)— note /10 si testée
#   image (str|None)  — fichier dans /static/img/ si dispo (ex: 'cobalt-dragoon.webp')
#   asin (str|None)   — ASIN Amazon pour /dp/{asin}, sinon recherche par nom
#   owner (str)       — perso anime (Bird Maru, Free de la Hoya, Ryuga…)
#   tagline (str)     — ligne courte descriptive

CATALOGUE = [
    # ============ Beyblade X — testées (7) ============
    {'slug': 'dran-sword-3-60f',      'name': 'Dran Sword 3-60F',       'ref': 'BX-01',  'gamme': 'beyblade-x', 'type': 'attaque',         'year': 2023, 'score': 8.5, 'image': 'dran-sword.webp',     'asin': 'B0C2HP6XCM', 'owner': 'Bird Maru',         'tagline': "L'inaugurale de la gamme Beyblade X"},
    {'slug': 'phoenix-wing-9-60gf',   'name': 'Phoenix Wing 9-60GF',    'ref': 'BX-23',  'gamme': 'beyblade-x', 'type': 'defense',         'year': 2024, 'score': 8.8, 'image': 'phoenix-wing.webp',   'asin': 'B0CGW3GCDF', 'owner': 'Multi',             'tagline': "Défenseuse n°1 du metagame X"},
    {'slug': 'knight-shield-3-80n',   'name': 'Knight Shield 3-80N',    'ref': 'BX-04',  'gamme': 'beyblade-x', 'type': 'defense',         'year': 2023, 'score': 8.2, 'image': 'knight-shield.webp',  'asin': 'B0C9JX9D4Y', 'owner': 'Multi',             'tagline': "Défense du quatuor inaugural"},
    {'slug': 'wizard-arrow-4-80b',    'name': 'Wizard Arrow 4-80B',     'ref': 'BX-03',  'gamme': 'beyblade-x', 'type': 'stamina',         'year': 2023, 'score': 8.4, 'image': 'wizard-arrow.webp',   'asin': 'B0C9JZ9N7L', 'owner': 'Multi',             'tagline': "Stamina pure du quatuor inaugural"},
    {'slug': 'hells-scythe-4-60t',    'name': 'Hells Scythe 4-60T',     'ref': 'BX-02',  'gamme': 'beyblade-x', 'type': 'stamina',         'year': 2023, 'score': 8.3, 'image': 'hells-scythe.webp',   'asin': 'B0C52C4L3T', 'owner': 'Multi',             'tagline': "Stamina-defense hybride du quatuor inaugural"},
    {'slug': 'cobalt-dragoon-2-60c',  'name': 'Cobalt Dragoon 2-60C',   'ref': 'BX-34',  'gamme': 'beyblade-x', 'type': 'attaque-gauche',  'year': 2024, 'score': 8.6, 'image': 'cobalt-dragoon.webp', 'asin': 'B0D6MZB1VF', 'owner': 'Kuroda Hyo',        'tagline': "1ʳᵉ left-spin Beyblade X (Spin Steal)"},
    {'slug': 'dran-buster-1-60a',     'name': 'Dran Buster 1-60A',      'ref': 'UX-01',  'gamme': 'beyblade-x', 'type': 'attaque',         'year': 2024, 'score': 9.0, 'image': None,                  'asin': 'B0CV7HF3W6', 'owner': 'Bird Maru',         'tagline': "Évolution Unique-X de Dran Sword (alliage métal)"},

    # ============ Beyblade X — à venir (5) ============
    {'slug': None, 'name': 'Sphinx Cowl 9-80B',      'ref': 'BX-15',  'gamme': 'beyblade-x', 'type': 'defense',         'year': 2023, 'score': None, 'image': 'sphinx-cowl.webp', 'asin': None,         'owner': 'Multi',           'tagline': "Défenseuse Bit Ball du Starter Pack"},
    {'slug': None, 'name': 'Knight Lance 4-80HN',    'ref': 'BX-13',  'gamme': 'beyblade-x', 'type': 'defense',         'year': 2024, 'score': None, 'image': None,               'asin': None,         'owner': 'Multi',           'tagline': "Défense gauche compagnon de Cobalt Dragoon"},
    {'slug': None, 'name': 'Tyranno Beat 4-80F',     'ref': 'BX-22',  'gamme': 'beyblade-x', 'type': 'attaque',         'year': 2024, 'score': None, 'image': None,               'asin': None,         'owner': 'Mei Davies',      'tagline': "Attaque massive du second arc anime"},
    {'slug': None, 'name': 'Shark Edge 3-60LF',      'ref': 'BX-21',  'gamme': 'beyblade-x', 'type': 'attaque',         'year': 2024, 'score': None, 'image': None,               'asin': None,         'owner': 'Akira Ashindo',   'tagline': "Attaque Low Flat redoutée en tournoi"},
    {'slug': None, 'name': 'Viper Tail 5-80O',       'ref': 'BX-19',  'gamme': 'beyblade-x', 'type': 'stamina',         'year': 2024, 'score': None, 'image': None,               'asin': None,         'owner': 'Multi',           'tagline': "Stamina à Disc pentagonal lourd"},

    # ============ Beyblade Burst — testées (3) ============
    {'slug': 'cyclone-roktavor-r7',   'name': 'Cyclone Roktavor R7',    'ref': 'F4067', 'gamme': 'beyblade-burst', 'type': 'attaque',        'year': 2022, 'score': 8.0, 'image': None, 'asin': 'B09TGD75BP', 'owner': 'Aiger Akabane',  'tagline': "Attaquante Quad Drive 4 modes interchangeables"},
    {'slug': 'vanish-fafnir-f7',      'name': 'Vanish Fafnir F7',       'ref': 'F3966', 'gamme': 'beyblade-burst', 'type': 'stamina-gauche', 'year': 2022, 'score': 8.2, 'image': None, 'asin': 'B09H17H8CD', 'owner': 'Free de la Hoya', 'tagline': "Stamina culte Spin Steal de la lignée Fafnir"},
    {'slug': 'stellar-hyperion-h8',   'name': 'Stellar Hyperion H8',    'ref': 'F6809', 'gamme': 'beyblade-burst', 'type': 'attaque',        'year': 2023, 'score': 8.5, 'image': None, 'asin': None,         'owner': 'Lui Shirosagi',  'tagline': "Attaquante brutale Quad Strike (Hasbro EU/US)"},

    # ============ Beyblade Burst — à venir (6) ============
    {'slug': None, 'name': 'Lord Spryzen S5 (Pro Series)', 'ref': 'F2334', 'gamme': 'beyblade-burst', 'type': 'equilibre', 'year': 2021, 'score': None, 'image': None, 'asin': None, 'owner': 'Shu Kurenai',    'tagline': "Équilibre premium métal collector"},
    {'slug': None, 'name': 'Brave Valtryek V6',            'ref': 'F4736', 'gamme': 'beyblade-burst', 'type': 'attaque',   'year': 2021, 'score': None, 'image': None, 'asin': None, 'owner': 'Valt Aoi',       'tagline': "Lignée Valtryek = LA toupie iconique de Burst"},
    {'slug': None, 'name': 'Ace Dragon S5',                'ref': 'E7536', 'gamme': 'beyblade-burst', 'type': 'attaque',   'year': 2020, 'score': None, 'image': None, 'asin': None, 'owner': 'Dante Koryu',    'tagline': "Attaque Burst Surge / Speedstorm"},
    {'slug': None, 'name': 'Z Achilles A4',                'ref': 'E4747', 'gamme': 'beyblade-burst', 'type': 'attaque',   'year': 2018, 'score': None, 'image': None, 'asin': None, 'owner': 'Aiger Akabane',  'tagline': "Première toupie d'Aiger (saison 5 Turbo)"},
    {'slug': None, 'name': 'Spryzen Requiem S3',           'ref': 'E1043', 'gamme': 'beyblade-burst', 'type': 'equilibre', 'year': 2018, 'score': None, 'image': None, 'asin': None, 'owner': 'Shu Kurenai',    'tagline': "Équilibre culte saison 3 Burst Evolution"},
    {'slug': None, 'name': 'Air Knight K4',                'ref': 'E7708', 'gamme': 'beyblade-burst', 'type': 'defense',   'year': 2019, 'score': None, 'image': None, 'asin': None, 'owner': 'Hyuga Hizashi',  'tagline': "Défense aérienne saison 5 Burst Turbo"},

    # ============ Metal Fusion — testées (7) ============
    {'slug': 'rock-leone-145wb',         'name': 'Rock Leone 145WB',         'ref': 'BB-30',  'gamme': 'beyblade-metal-fusion', 'type': 'defense',         'year': 2010, 'score': 8.1, 'image': 'rock-leone.webp',      'asin': 'B003AYZ5O8', 'owner': 'Kyoya Tategami', 'tagline': "Défense iconique de Kyoya"},
    {'slug': 'galaxy-pegasus-w105r2f',   'name': 'Galaxy Pegasus W105R²F',   'ref': 'BB-70',  'gamme': 'beyblade-metal-fusion', 'type': 'attaque',         'year': 2010, 'score': 7.7, 'image': 'galaxy-pegasus.webp',  'asin': 'B005ASZ5LE', 'owner': 'Ginga Hagane',   'tagline': "Évolution saison 2 de la Pegasus de Ginga"},
    {'slug': 'meteo-l-drago-lw105lrf',   'name': 'Meteo L-Drago LW105LRF',   'ref': 'BB-88',  'gamme': 'beyblade-metal-fusion', 'type': 'attaque-gauche',  'year': 2011, 'score': 7.5, 'image': 'meteo-l-drago.jpg',    'asin': None,         'owner': 'Ryuga',          'tagline': "Attaque gauche du dragon empereur (Hybrid Wheel)"},
    {'slug': 'storm-pegasus-105rf',      'name': 'Storm Pegasus 105RF',      'ref': 'BB-28',  'gamme': 'beyblade-metal-fusion', 'type': 'attaque',         'year': 2009, 'score': 8.0, 'image': 'storm-pegasus.webp',   'asin': 'B004AY8ICE', 'owner': 'Ginga Hagane',   'tagline': "L'originelle de Ginga, inaugurale de la gamme"},
    {'slug': 'ray-unicorno-d125cs',      'name': 'Ray Unicorno D125CS',      'ref': 'BB-71',  'gamme': 'beyblade-metal-fusion', 'type': 'attaque',         'year': 2010, 'score': 7.8, 'image': 'ray-unicorno.webp',    'asin': None,         'owner': 'Masamune Kadoya','tagline': "Attaque équilibrée (Ray Striker chez Hasbro EU)"},
    {'slug': 'l-drago-destroy-fs',       'name': 'L-Drago Destroy F:S',      'ref': 'BB-108', 'gamme': 'beyblade-metal-fusion', 'type': 'attaque-gauche',  'year': 2011, 'score': 8.4, 'image': 'l-drago-destroy.webp', 'asin': 'B005U8KMJM', 'owner': 'Ryuga',          'tagline': "Évolution 4D ultime de la lignée L-Drago"},
    {'slug': 'earth-eagle-145wd',        'name': 'Earth Eagle 145WD',        'ref': 'BB-47',  'gamme': 'beyblade-metal-fusion', 'type': 'defense',         'year': 2010, 'score': 7.6, 'image': None,                   'asin': 'B0050OMBU8', 'owner': 'Tsubasa Otori',  'tagline': "Défense endurance (Earth Aquila chez Hasbro EU)"},

    # ============ Metal Fusion — à venir (4) ============
    {'slug': None, 'name': 'Hell Kerbecs BD145DS',       'ref': 'BB-99',  'gamme': 'beyblade-metal-fusion', 'type': 'stamina',         'year': 2011, 'score': None, 'image': None, 'asin': None, 'owner': 'Damian Hart',  'tagline': "Stamina Cerbère, Metal Masters"},
    {'slug': None, 'name': 'Cosmic Pegasus F:D',         'ref': 'BB-105', 'gamme': 'beyblade-metal-fusion', 'type': 'attaque',         'year': 2012, 'score': None, 'image': None, 'asin': None, 'owner': 'Ginga Hagane', 'tagline': "Évolution 4D ultime de la Pegasus de Ginga"},
    {'slug': None, 'name': 'Phantom Orion B:D',          'ref': 'BB-118', 'gamme': 'beyblade-metal-fusion', 'type': 'stamina',         'year': 2012, 'score': None, 'image': None, 'asin': None, 'owner': 'Chris',        'tagline': "Stamina 4D légendaire (Métal Fury)"},
    {'slug': None, 'name': 'Diablo Nemesis X:D',         'ref': 'BB-122', 'gamme': 'beyblade-metal-fusion', 'type': 'equilibre',       'year': 2012, 'score': None, 'image': None, 'asin': None, 'owner': 'Rago',         'tagline': "Toupie ultime de l'antagoniste de Metal Fury"},
]


# ============ Helpers ============

def amazon_url(entry: dict, tag: str = 'beyblade0a-21') -> str:
    """Build the Amazon FR URL for an entry: /dp/{asin} if asin known, else search by name."""
    if entry.get('asin'):
        return f"https://www.amazon.fr/dp/{entry['asin']}?tag={tag}"
    # fallback search
    query = entry['name'].lower().replace(' ', '+').replace(':', '').replace('(', '').replace(')', '')
    return f"https://www.amazon.fr/s?k={query}+beyblade&tag={tag}"


def stats() -> dict:
    """Aggregate stats for the catalogue (used in hero section)."""
    total = len(CATALOGUE)
    tested = sum(1 for e in CATALOGUE if e.get('slug'))
    by_gamme = {}
    for e in CATALOGUE:
        g = e['gamme']
        by_gamme[g] = by_gamme.get(g, 0) + 1
    return {
        'total': total,
        'tested': tested,
        'gammes_count': len(by_gamme),
        'by_gamme': by_gamme,
    }


if __name__ == '__main__':
    s = stats()
    print(f"Catalogue : {s['total']} toupies au total ({s['tested']} testées) sur {s['gammes_count']} gammes")
    for g, count in s['by_gamme'].items():
        print(f"  - {GAMMES[g]['label']:25} : {count}")
