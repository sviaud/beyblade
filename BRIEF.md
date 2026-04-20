# Brief — Création d'un blog Toupies Beyblade (réplique du workflow pistoletnerf.fr)

## Objectif

Construire un blog WordPress dédié aux toupies Beyblade, optimisé SEO/GEO et monétisé via Amazon Associates, en réutilisant l'intégralité du workflow développé pour **pistoletnerf.fr**.

## Ce qui existe
- Un WordPress **vierge** (site à configurer)
- Un fichier CSV de recherches Semrush : `/Users/svm2/Downloads/toupie-beyblade_broad-match_fr_2026-04-19.csv`
- Le **projet pistoletnerf-refonte** à `/Users/svm2/Dropbox/Mi4/projets/Claude/pistoletnerf-refonte/` (code source Python à réutiliser)

## Ce dont j'ai besoin de l'utilisateur AVANT de commencer
1. URL du site WordPress Beyblade (ex: `https://toupie-beyblade.fr/`)
2. Identifiant WordPress (username)
3. Clé d'application WordPress (WP Admin → Profil → Mots de passe d'application)
4. Tag Amazon Associates (ex: `toupiebey-21`)
5. Accès SSH (hébergeur, dossier `/wp-content/mu-plugins/`)
6. Confirmer que le thème est installé (recommandation : **The7** comme pistoletnerf, ou un thème moderne type GeneratePress/Kadence)

---

## 🎯 Analyse SEO (à partir du CSV Semrush)

### Mot-clé principal
- **`toupie beyblade`** : 22 200 recherches/mois, KD 35, CPC 0,12€
- Intent : Informational (pas transactional direct → besoin de guide d'achat)

### Gammes de produits (à créer comme catégories WP)
| Gamme | Volume search | KD | Notes |
|---|---|---|---|
| **Beyblade X** (2024+) | 12 100 + 1 300 + 590 | 20-31 | Gamme actuelle, la plus cherchée |
| **Beyblade Burst** | 2 400 + 1 000 + 480 + 320 | 21-34 | Gamme mature |
| **Beyblade Metal Fusion** | 1 600 + 1 300 + 720 + 590 + 210 | 14-30 | Gamme classique (2010-2013) |
| **Beyblade Burst Turbo** | 390 + 320 | 18-24 | Sous-gamme Burst |

### Accessoires (catégorie à créer)
| Accessoire | Volume | KD |
|---|---|---|
| **Arènes Beyblade** (`arene toupie beyblade`) | 1 600 + 1 000 + 880 + 720 + 480 + 260 + 210 | 17-29 |
| **Lanceurs Beyblade** (`lanceur toupie beyblade`) | 720 + 480 + 210 | 17-23 |

### Toupies individuelles (fiches produit prioritaires)
| Toupie | Volume total | Notes |
|---|---|---|
| **Pegasus** | 320 + 260 = 580 | Toupie iconique Metal Fusion |
| **Valtryek** | 320 | Burst héros |
| **Phoenix** | 260 + 210 = 470 | Burst/X |
| **Dragon** | 260 + 210 = 470 | X |

### Pages SEO stratégiques à créer
1. **"Meilleur toupie beyblade"** (320 searches) + **"Meilleur toupie beyblade X"** (480) → article de comparatif/guide d'achat
2. **"Toupie beyblade la plus forte du monde"** (210, Featured snippet disponible) → article listicle SEO à cibler
3. **"Toupie beyblade rare"** (210) → article collectionneurs
4. **"Amazon toupie beyblade"** (390 + 390) → pages optimisées avec CTA Amazon
5. **"Leclerc toupie beyblade"** + **"King Jouet toupie beyblade"** (210 chacun) → guide comparatif revendeurs
6. **Coloriages / Dessins Beyblade** (590 + 480 + 320 + 260 + 210 = 1 860 recherches cumulées) → **pages à fort trafic non-monétisable** mais excellentes pour le SEO et les backlinks

---

## 🏗️ Architecture proposée du site

### Catégories WordPress
```
- Beyblade X (NOUVEAU)
- Beyblade Burst
  - Burst Turbo (sous-cat optionnelle)
- Beyblade Metal Fusion
- Arènes Beyblade
- Lanceurs Beyblade
- Coloriages & Dessins (trafic SEO)
- Guides d'achat
- Blog (actus Beyblade)
```

### Pages stratégiques
- **Accueil** : hero + bannières par gamme (comme homepage Nerf)
- **Tous les Beyblade** : catalogue complet groupé par gamme
- **Comparatifs** :
  - `/comparatif-beyblade-x/` (priorité #1)
  - `/comparatif-beyblade-burst/`
  - `/comparatif-beyblade-metal-fusion/`
  - `/comparatif-arenes-beyblade/`
  - `/comparatif-lanceurs-beyblade/`
- **Guide d'achat** : `/meilleur-toupie-beyblade/` (optimisé pour le KW 320/mois)
- **Top classement** : `/toupie-beyblade-la-plus-forte/` (featured snippet)
- **Coloriages** : `/coloriage-toupie-beyblade/` (1 860+ recherches cumulées)
- **À propos / Contact** : classiques

### Menu principal
```
Accueil | Toutes les toupies | Comparatifs ▼ | Coloriages | Blog | Contact
                              ├─ Beyblade X
                              ├─ Beyblade Burst
                              ├─ Beyblade Metal Fusion
                              ├─ Arènes
                              └─ Lanceurs
```

---

## 📄 Template d'article (à répliquer de pistoletnerf)

Chaque fiche toupie = **article de 900-1300 mots** avec :

1. **Breadcrumb** : `← Toutes les Beyblade [Gamme]`
2. **Intro GEO-friendly** (120-180 mots, réponse citable par les LLMs)
3. **Bloc "Notre avis" 2 colonnes** (carrousel d'images Amazon à gauche + notation à droite) :
   - Photo principale + vignettes cliquables vers Amazon
   - Note globale /10
   - Sous-notes : **Puissance**, **Précision**, **Durabilité**, **Design**, **Rapport qualité-prix**
   - Bouton CTA "Voir le prix sur Amazon →"
4. **H2 Présentation** (histoire, gamme, année)
5. **H2 Caractéristiques techniques** (tableau HTML) :
   - Gamme, Année, Type (attaque/défense/endurance/stamina), Layer, Disc, Driver, Lanceur inclus, Âge recommandé
6. **H2 Performances en combat** (puissance d'attaque, stabilité, durabilité)
7. **H2 Points forts & points faibles** (listes ul/li)
8. **H2 À qui s'adresse cette toupie** (niveau débutant/confirmé, type de combat)
9. **H2 Comparatif avec d'autres Beyblade [gamme]** (maillage interne vers 2-3 cousins)
10. **H2 FAQ** (5-8 questions type : compatibilité, où acheter, rareté, personnalisation)
11. **H2 Où acheter** + bouton CTA Amazon final

### Différences avec le template Nerf
- **Critères de notation adaptés** : au lieu de Portée/Cadence/Capacité, utiliser :
  - **Puissance** (attaque)
  - **Endurance** (stamina)
  - **Défense**
  - **Précision** (tir)
  - **Durabilité**
- **Tableau de specs** spécifique aux Beyblade (Layer, Disc, Driver pour Burst ; Blade/Ratchet/Bit pour Beyblade X)
- **Concept de "type"** : Attaque / Défense / Endurance / Équilibre (à intégrer dans le bloc de notation)

---

## 🔧 Modules Python à réutiliser (depuis `pistoletnerf-refonte/scripts/`)

| Fichier source | À adapter | Usage |
|---|---|---|
| `wp_client.py` | Minimal (juste changer les credentials) | Client API REST WordPress |
| `amazon_link.py` | Changer tag d'affiliation | Construction liens Amazon |
| `amazon_images.py` | Inchangé | Upload images sur WP + download via curl |
| `content_generator.py` | **Adapter** : nouveau vocabulaire (toupie au lieu de blaster), nouveau contexte par gamme, nouvelles sections | Génération HTML de l'article |
| `rating_box.py` | **Refonte complète** : nouveaux critères (Puissance/Endurance/Défense/Précision/Durabilité) | Bloc de notation + carrousel |
| `carousel.py` | Inchangé | Carrousel WP en CSS pur |
| `comparison_table.py` | Adapter critères de notation | Tableau comparatif par gamme |
| `product_data.py` | Inchangé | Accès base produits |
| `image_handler.py` | Inchangé | Extraction images existantes |
| `02_pilot.py` / `03_batch.py` | Adapter IDs pilotes et catégories | Scripts de pilote / batch |
| `04_comparatifs.py` | Adapter mapping catégories → gammes | Génération pages comparatif |
| `05_new_articles.py` | Inchangé (générique) | Création d'articles avec images Chrome |
| `06_internal_linking.py` | Inchangé (générique) | Maillage interne automatique |

---

## 🔌 mu-plugins à reproduire

Créer dans `/wp-content/mu-plugins/` :

### 1. `beyblade-custom.php` (équivalent pistoletnerf-custom.php)
- CSS responsive (sidebar, header, title band, carrousel, breadcrumb)
- JS pour la recherche (fix toggle)
- Register REST meta pour The7
- Endpoint custom REST `/beyblade/v1/postmeta/{id}` pour écrire les meta The7 privées

### 2. `beyblade-mobile-menu.php` (équivalent pistoletnerf-mobile-menu.php)
- Hamburger flottant orange/rouge
- Menu slide-in latéral
- Auto-fermeture au clic sur un lien

### 3. Fix potentiel VigLink/Disqus
Si Disqus est installé → ajouter `window.vglnk = true` pour bloquer le tracking VigLink qui remplace les tags Amazon.

---

## 🚀 Plan d'exécution (à suivre pas à pas)

### Phase 0 — Setup (1h)
- [ ] Recevoir les credentials WP de l'utilisateur
- [ ] Tester l'API REST WP (GET `/wp/v2/users/me`)
- [ ] Installer le thème (The7 ou équivalent moderne)
- [ ] Créer la structure de catégories
- [ ] Créer les pages vides (Accueil, Tous les Beyblade, Comparatifs, Contact)
- [ ] Déployer les mu-plugins via SSH
- [ ] Vérifier qu'il n'y a pas de WAF type **Tiger Protect** (o2switch) qui bloque les POST API — si oui, whitelister `/wp-json/*` ou désactiver le temps du setup
- [ ] Tester l'extraction d'images via Chrome + Claude in Chrome MCP

### Phase 1 — Recherche produit & brainstorming (2h)
- [ ] Lancer un agent general-purpose pour **cartographier le catalogue Beyblade 2024-2026** (Beyblade X, Burst récents, Metal Fusion classiques)
- [ ] Identifier **~30 toupies prioritaires** à couvrir (avec ASINs Amazon.fr)
- [ ] Identifier **~10 arènes** + **~5 lanceurs**
- [ ] Cibler les **4-5 toupies "hero"** du CSV : Pegasus, Valtryek, Phoenix, Dragon + 1 Beyblade X populaire
- [ ] Utiliser le skill `superpowers:brainstorming` pour valider l'architecture finale

### Phase 2 — Adaptation du code (3h)
- [ ] Copier `pistoletnerf-refonte/` → `beyblade-blog/`
- [ ] Mettre à jour `config.env` (URL, user, password, tag Amazon)
- [ ] Réécrire `rating_box.py` avec les nouveaux critères (Puissance/Endurance/Défense/Précision/Durabilité + Type attaque/défense/stamina/équilibre)
- [ ] Réécrire `content_generator.py` :
  - Nouveau vocabulaire (toupie, combat, stadium au lieu de blaster, battle)
  - Nouvelle section H2 "Type de toupie" (Attaque/Défense/Endurance/Équilibre)
  - Nouvelle description par gamme (Beyblade X, Burst, Metal Fusion)
  - Nouvelle FAQ par défaut adaptée
- [ ] Adapter `comparison_table.py` pour les nouveaux critères
- [ ] Adapter le mapping gamme → URL dans le breadcrumb (`GAMME_TO_COMPARATIF`)

### Phase 3 — Pilote (2h)
- [ ] Créer **2 articles pilotes** (ex: 1 Beyblade X récent + 1 Beyblade Burst populaire)
- [ ] Extraction images via Chrome (8-10 photos par toupie)
- [ ] Génération contenu long-form
- [ ] Publication + vérification visuelle
- [ ] Validation utilisateur avant passage au batch

### Phase 4 — Batch principal (1 journée)
- [ ] **30-40 articles produit** en 3-4 batches de ~10
- [ ] Chaque batch :
  1. Recherche ASINs sur Amazon.fr via Chrome
  2. Extraction images (8 par produit)
  3. Upload sur WP
  4. Génération articles avec meta The7
  5. Application du maillage interne
- [ ] Création des **5 pages comparatif** (Beyblade X, Burst, Metal Fusion, Arènes, Lanceurs)
- [ ] Création de la **homepage avec bannières par gamme**
- [ ] Création de la page **"Tous les Beyblade"** groupée par gamme

### Phase 5 — Pages SEO spéciales (3h)
- [ ] **"Meilleur toupie beyblade"** (article guide d'achat, ~2000 mots, comparatif top 10)
- [ ] **"Toupie Beyblade la plus forte du monde"** (article featured snippet ciblé)
- [ ] **"Toupie Beyblade rare"** (article collectionneurs)
- [ ] **Coloriages Beyblade** (page avec images téléchargeables — utiliser des générations AI ou ressources libres)

### Phase 6 — Maillage interne & optimisation (1h)
- [ ] Générer les `alternatives` pour chaque produit (lancer `06_internal_linking.py`)
- [ ] Régénérer tous les articles pour injecter les liens
- [ ] Vérifier les breadcrumbs sur toutes les catégories
- [ ] Ajouter les catégories au menu principal (sous-menu "Comparatifs")
- [ ] Mise à jour Tous les Beyblade + Homepage

### Phase 7 — Mobile & finitions (1h)
- [ ] Tester responsive mobile (sidebar cachée, menu hamburger, review block stacké)
- [ ] Ajuster le CSS du mu-plugin au besoin
- [ ] Purge cache (LiteSpeed ou équivalent)
- [ ] Vérification croisée (desktop + mobile)

---

## ⚠️ Pièges connus (appris sur pistoletnerf)

1. **WordPress `wpautop`** casse les `<a>` contenant du HTML block-level → **utiliser `<div onclick="...">` à la place** + wrapper tout dans `<!-- wp:html -->...<!-- /wp:html -->`
2. **LiteSpeed Cache** défère le JS inline → ajouter `data-no-optimize="1"` sur les scripts critiques (ex: recherche)
3. **Tiger Protect (o2switch)** renvoie 307 sur les POST API → whitelist `/wp-json/*` ou désactiver pendant le batch
4. **Amazon bloque le scraping** → toujours extraire les images via **Chrome + MCP `Claude_in_Chrome`**, jamais via curl/WebFetch
5. **Images PNG transparentes** invisibles sur fond sombre → toujours encadrer les photos produit dans un fond blanc arrondi
6. **The7 meta privées** (`_dt_sidebar_position`, `_dt_post_options_hide_thumbnail`, etc.) non exposées par défaut → passer par un endpoint REST custom (`/beyblade/v1/postmeta/{id}`)
7. **Image Amazon téléchargée** via urllib → utiliser `curl -L` (subprocess) à cause des redirects 307
8. **Disqus + VigLink** réécrivent les liens Amazon au clic → bloquer avec `window.vglnk = true` dans wp_head
9. **Featured image** affichée en grand en haut par The7 → définir `_dt_post_options_hide_thumbnail: "1"` mais garder `featured_media` (pour les widgets / Search)

---

## 🎨 Design à reproduire

### Bloc "Notre avis" (2 colonnes, full-width)
- Fond `#fafafa` + bordure 2px orange (`#ff9900` pour Nerf, à choisir pour Beyblade)
- Gauche : photo principale + 4-8 vignettes cliquables
- Droite : nom + note globale (badge coloré), table de sous-notes avec étoiles ½
- Responsive : stack vertical sur mobile (`flex-wrap: wrap`)

### Bannières homepage
- Fond sombre `#1a1a2e` + photo produit en filigrane (opacity 0.2)
- Overlay gradient sombre → transparent
- Gauche : nom gamme (28px blanc) + tagline + tag "NOUVEAU 2025" + bouton CTA
- Droite : photo produit nette sur fond blanc arrondi
- Bouton CTA couleur accent (orange/rouge) avec hover élévation

### Délimiteurs "Tous les Beyblade"
- Bandeau coloré par gamme (couleur distinctive pour chaque)
- Titre H2 gamme + année "depuis 2024" à gauche
- Badge "X toupies" à droite
- Grille de cartes en dessous (barre de couleur assortie sous chaque carte)

---

## 📊 KPIs à suivre

- Nombre d'articles produit publiés (objectif : 30-50)
- Volume cumulé de mots-clés ciblés (objectif : 60 000+ recherches/mois)
- Nombre de liens internes créés (objectif : 100+)
- Couverture des gammes (objectif : 4 gammes actives + accessoires)

---

## ✅ Critères de succès

1. [ ] Site WordPress fonctionnel avec thème + mu-plugins
2. [ ] 30+ articles produit Beyblade avec carrousel d'images Amazon + notation + FAQ
3. [ ] 5+ pages comparatif par gamme
4. [ ] Homepage avec bannières gamme
5. [ ] Page "Tous les Beyblade" groupée par gamme (ordre : nouveauté → classique)
6. [ ] Menu principal avec toutes les gammes
7. [ ] Maillage interne (alternatives) sur chaque article
8. [ ] Mobile responsive (menu hamburger, sidebar cachée, review block stacké)
9. [ ] Liens Amazon avec tag d'affiliation vérifié (test en navigation privée)
10. [ ] Article "Meilleur toupie Beyblade" (guide d'achat) publié
11. [ ] Article "Toupie Beyblade la plus forte" (featured snippet target)
12. [ ] Page coloriages (trafic SEO bonus)

---

## 💬 Comment démarrer la nouvelle session Claude Code

**Prompt à coller dans la nouvelle session** :

```
Lis le fichier /Users/svm2/Dropbox/Mi4/projets/Claude/beyblade-blog/BRIEF.md qui contient
le brief complet pour créer un blog WordPress sur les toupies Beyblade.

Le projet de référence à réutiliser se trouve dans
/Users/svm2/Dropbox/Mi4/projets/Claude/pistoletnerf-refonte/

Commence par :
1. Lire le BRIEF.md en entier
2. Lire le CSV de mots-clés Semrush :
   /Users/svm2/Downloads/toupie-beyblade_broad-match_fr_2026-04-19.csv
3. Me poser les questions de Phase 0 (credentials WordPress, tag Amazon, etc.)
4. Lancer la Phase 1 (brainstorming et cartographie du catalogue Beyblade 2024-2026)
   avec la skill superpowers:brainstorming

Utilise les modules Python de pistoletnerf-refonte/scripts/ en les adaptant
au vocabulaire Beyblade (voir section "Modules Python à réutiliser" du BRIEF).

Travaille en sessions courtes et demande-moi validation après chaque phase.
Garde Chrome ouvert pour l'extraction d'images Amazon via MCP Claude_in_Chrome.
```

---

## 🔄 Inspirations concrètes depuis pistoletnerf.fr

Aller voir ces URLs pour s'inspirer du rendu final à reproduire :

- **Homepage** : https://www.pistoletnerf.fr/
- **Article produit** : https://www.pistoletnerf.fr/elite/nerf-elite-2-0-commander-rd-6/
- **Page comparatif** : https://www.pistoletnerf.fr/comparatif-elite/
- **Page catalogue** : https://www.pistoletnerf.fr/tous/
- **Menu mobile** : à tester sur mobile
