# toupiebeyblade.fr

Blog SEO/affiliation Amazon dédié aux toupies Beyblade — site **statique** déployé sur **Cloudflare Pages**.

## Stack

- **Build** : Python 3 (stdlib uniquement, pas de framework)
- **Templating** : f-strings
- **Hosting** : Cloudflare Pages (gratuit, CDN global)
- **CI** : GitHub Actions (build automatique à chaque push)
- **Domain** : toupiebeyblade.fr (DNS Cloudflare)

## Quick start

```bash
# Build local
python3 scripts/build.py

# Preview
python3 -m http.server 3000 --directory dist
# → http://localhost:3000/
```

## Architecture

```
.
├── src/
│   ├── static/          # CSS, images, fonts (copiés tels quels)
│   └── _redirects       # Redirections 301 Cloudflare Pages
├── data/
│   └── catalogue.md     # 40+ produits sourcés (X, Burst, Metal Fusion)
├── scripts/             # Modules Python
│   ├── build.py         # Orchestrateur principal
│   ├── file_writer.py   # Écriture HTML dans /dist
│   ├── seo_meta.py      # Meta tags + JSON-LD
│   ├── sitemap.py       # sitemap.xml + robots.txt
│   ├── rating_box.py    # Bloc "Notre avis" (5 critères Beyblade)
│   ├── amazon_link.py   # Liens d'affiliation
│   ├── content_generator.py    # Génération HTML article (à adapter)
│   └── ...
├── mockups/             # Maquettes design (référence — pas de build)
├── dist/                # Build output (gitignored, déployé sur CF Pages)
└── config.env           # Credentials (gitignored)
```

## SEO

Le module `seo_meta.py` génère sur chaque page :

- title + meta description
- Canonical URL
- Open Graph (Facebook/LinkedIn) + Twitter Cards
- JSON-LD structured data : WebSite, Organization, BreadcrumbList, Product, Review, Article, FAQPage

Plus rapide et plus contrôlable que Yoast SEO (génère exactement ce qu'on veut, dans l'ordre qu'on veut).

## Décisions éditoriales

- ❌ **Pas d'affichage de prix** dans les articles (politique conformité Amazon + risque MAJ)
- ❌ **Pas d'auteur affiché** (voix collective)
- ❌ **Pas de commentaires** (héritage VigLink/Disqus problématique sur l'ancien site → on perdait les liens d'affiliation)
- ✅ Newsletter signup + boutons share comme alternative engagement
- ✅ Couleur d'accent : bleu électrique `#0099ff`
- ✅ 5 critères de notation Beyblade : Puissance / Endurance / Défense / Précision / Durabilité
- ✅ 4 types catégoriels : Attaque / Défense / Stamina / Équilibre

## Backlinks legacy (305 redirections)

Le site `toupiebeyblade.fr` a hébergé un blog Beyblade Metal Fusion entre 2011 et 2013. **305 backlinks survivants** sont préservés via le fichier `src/_redirects` (Cloudflare Pages 301).

Voir `REDIRECTIONS.md` pour le détail de la stratégie.

## Déploiement

1. Push vers GitHub (branche `main`)
2. Cloudflare Pages détecte le push
3. Build automatique : `python3 scripts/build.py`
4. Déploiement sur `toupiebeyblade.fr`

Configuration CF Pages :
- **Build command** : `python3 scripts/build.py`
- **Output directory** : `dist`
- **Python version** : 3.9+
