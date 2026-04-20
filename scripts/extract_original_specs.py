#!/usr/bin/env python3
"""Extrait les specs des contenus originaux et enrichit nerf-products.json.

Parse les anciennes listes ul/li type :
  <li><strong>Portée :</strong> 15 mètres</li>
  <li><strong>Précision :</strong> excellente</li>
  ...

Convertit en scores numériques et override les calculs heuristiques.

Usage: python3 scripts/extract_original_specs.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Oldest backup with original content
ORIGINAL_BACKUP = '2026-04-09-174415'


def extract_value(label, content):
    """Cherche une ligne <li><strong>Label :</strong> value</li> ou variante."""
    # Support variantes : avec accents, casse différente, tirets, etc.
    patterns = [
        rf'<li[^>]*>\s*<strong>\s*{label}\s*:?\s*</strong>\s*([^<]+)</li>',
        rf'<strong>\s*{label}\s*:?\s*</strong>\s*([^<\n]+)',
        rf'{label}\s*:\s*([^<\n]+)',
    ]
    for p in patterns:
        m = re.search(p, content, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def parse_portee(text):
    """Extrait une portée en mètres."""
    if not text:
        return None
    # Recherche "X mètres", "X m", "Xm"
    m = re.search(r'(\d+)(?:\s*[àa-]\s*(\d+))?\s*m(?:è|e)?tres?', text, re.I)
    if m:
        v1 = int(m.group(1))
        v2 = int(m.group(2)) if m.group(2) else v1
        return (v1 + v2) // 2
    # "entre X et Y"
    m = re.search(r'entre\s+(\d+)\s+et\s+(\d+)', text, re.I)
    if m:
        return (int(m.group(1)) + int(m.group(2))) // 2
    m = re.search(r'(\d+)\s*m\b', text)
    if m:
        return int(m.group(1))
    return None


def parse_capacite(text):
    """Extrait une capacité en nombre."""
    if not text:
        return None
    # "X fléchettes", "X disques", "X balles"
    m = re.search(r'(\d+)\s*(?:fl[eé]chettes?|disques?|balles?|munitions?)', text, re.I)
    if m:
        return int(m.group(1))
    # "jusqu'à X"
    m = re.search(r"jusqu['']?\s*[aà]\s*(\d+)", text, re.I)
    if m:
        return int(m.group(1))
    # Premier nombre trouvé
    m = re.search(r'(\d+)', text)
    if m:
        return int(m.group(1))
    return None


def parse_cadence(text):
    """Extrait un score de cadence /10 depuis un texte qualitatif."""
    if not text:
        return None
    t = text.lower()
    # Si mention explicite de tirs/seconde
    m = re.search(r'(\d+)\s*(?:fl[eé]chettes?|disques?|tirs?|projectiles?)\s*(?:par\s*)?(?:/|par\s*)?s(?:econde)?', t, re.I)
    if m:
        rps = int(m.group(1))
        if rps >= 5:
            return 9.5
        if rps >= 4:
            return 9.0
        if rps >= 3:
            return 8.0
        if rps >= 2:
            return 7.0
        return 6.0
    # Mots-clés qualitatifs
    if any(k in t for k in ['meilleure', 'excellent', 'exceptionnel', 'incroyable', 'énorme', 'enorme']):
        return 9.0
    if any(k in t for k in ['très bon', 'tres bon', 'tres bonne', 'très bonne', 'impressionnant']):
        return 8.5
    if any(k in t for k in ['bon', 'bonne', 'correct', 'satisfaisant', 'honorable']):
        return 7.5
    if any(k in t for k in ['moyen', 'moyenne', 'passable']):
        return 6.0
    if any(k in t for k in ['faible', 'mauvais', 'insuffisant', 'lent', 'lente']):
        return 5.0
    return None


def parse_qualitative(text):
    """Parse un score /10 depuis un texte qualitatif générique (précision, fiabilité)."""
    if not text:
        return None
    t = text.lower()
    if any(k in t for k in ['excellent', 'exceptionnel', 'parfait', 'remarquable']):
        return 9.0
    if any(k in t for k in ['très bon', 'tres bon', 'tres bonne', 'très bonne', 'très fiable', 'tres fiable']):
        return 8.5
    if any(k in t for k in ['bon', 'bonne', 'correct', 'satisfaisant', 'honorable', 'solide', 'fiable']):
        return 7.5
    if any(k in t for k in ['moyen', 'moyenne', 'passable', 'modéré', 'modere']):
        return 6.5
    if any(k in t for k in ['faible', 'mauvais', 'insuffisant', 'décevant', 'decevant']):
        return 5.0
    return None


def capacite_to_score(cap):
    """Convertit une capacité numérique en score /10."""
    if cap is None:
        return None
    if cap >= 30:
        return 9.5
    if cap >= 20:
        return 9.0
    if cap >= 15:
        return 8.5
    if cap >= 10:
        return 7.5
    if cap >= 8:
        return 7.0
    if cap >= 6:
        return 6.5
    if cap >= 4:
        return 5.5
    return 5.0


def portee_to_score(p):
    """Convertit une portée numérique en score /10."""
    if p is None:
        return None
    if p >= 27:
        return 9.5
    if p >= 22:
        return 9.0
    if p >= 18:
        return 8.0
    if p >= 14:
        return 7.0
    if p >= 10:
        return 6.0
    if p >= 7:
        return 5.0
    return 4.0


def extract_specs_from_backup(backup_path):
    """Lit un fichier JSON de backup et extrait les specs."""
    with open(backup_path, encoding='utf-8') as f:
        post = json.load(f)

    content = post['content'].get('raw', '')

    # Extraction brute des champs
    raw_portee = extract_value('Port[eé]e', content)
    raw_precision = extract_value('Pr[eé]cision', content)
    raw_fiabilite = extract_value('Fiabilit[eé]', content)
    raw_cadence = extract_value('Fr[eé]quence(?:\\s+de\\s+tir)?', content)
    if not raw_cadence:
        raw_cadence = extract_value('Cadence', content)
    raw_capacite = extract_value('Capacit[eé]', content)

    # Conversions en scores
    portee_num = parse_portee(raw_portee) if raw_portee else None
    capacite_num = parse_capacite(raw_capacite) if raw_capacite else None

    ratings = {}
    if portee_num is not None:
        ratings['portee'] = portee_to_score(portee_num)
    elif raw_portee:
        q = parse_qualitative(raw_portee)
        if q is not None:
            ratings['portee'] = q

    if raw_precision:
        q = parse_qualitative(raw_precision)
        if q is not None:
            ratings['precision'] = q

    if raw_fiabilite:
        q = parse_qualitative(raw_fiabilite)
        if q is not None:
            ratings['fiabilite'] = q

    if raw_cadence:
        c = parse_cadence(raw_cadence)
        if c is not None:
            ratings['cadence'] = c

    if capacite_num is not None:
        ratings['capacite'] = capacite_to_score(capacite_num)
    elif raw_capacite:
        q = parse_qualitative(raw_capacite)
        if q is not None:
            ratings['capacite'] = q

    return {
        'post_id': post['id'],
        'title': post['title'].get('raw', ''),
        'raw_extracted': {
            'portee': raw_portee,
            'precision': raw_precision,
            'fiabilite': raw_fiabilite,
            'cadence': raw_cadence,
            'capacite': raw_capacite,
        },
        'portee_m': portee_num,
        'capacite': capacite_num,
        'ratings': ratings,
    }


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    backup_dir = os.path.join(base, '..', 'backups', ORIGINAL_BACKUP, 'posts')
    products_path = os.path.join(base, '..', 'data', 'nerf-products.json')

    with open(products_path) as f:
        products = json.load(f)

    if not os.path.isdir(backup_dir):
        print(f"ERROR: backup dir {backup_dir} not found")
        sys.exit(1)

    files = sorted(os.listdir(backup_dir))
    json_files = [f for f in files if f.endswith('.json')]
    print(f"Processing {len(json_files)} backup files...")

    enriched = 0
    skipped = 0

    for fname in json_files:
        specs = extract_specs_from_backup(os.path.join(backup_dir, fname))
        pid = str(specs['post_id'])

        if pid not in products:
            skipped += 1
            continue

        product = products[pid]
        # Conserve les specs existantes comme fallback, override avec ce qu'on extrait
        if specs['ratings']:
            product['ratings'] = specs['ratings']
            enriched += 1

        # Override portée et capacité numériques si trouvées
        if specs['portee_m']:
            product['portee_m'] = specs['portee_m']
        if specs['capacite']:
            product['capacite'] = specs['capacite']

        products[pid] = product

    with open(products_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"✅ Enriched {enriched}/{len(json_files)} products with original specs")
    print(f"   Skipped: {skipped}")
    print(f"   Saved to: {products_path}")


if __name__ == '__main__':
    main()
