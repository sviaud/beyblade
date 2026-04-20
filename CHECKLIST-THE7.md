# Checklist configuration The7 — toupiebeyblade.fr

> **À exécuter une seule fois** dans le back-office WP avant le déploiement des articles. Compter ~30 min.

## Préalables (en parallèle)

- [ ] **Permaliens** déjà activés (✅ vérifié : "Nom de l'article")
- [ ] **Désactiver Bot Fight Mode Cloudflare** pour `/wp-json/*` (Dashboard Cloudflare → Security → Bots → exclude `/wp-json/*` from Bot Fight)
- [ ] **Vérifier WAF Tiger Protect (o2switch)** : tester un POST sur l'API depuis ton terminal :
  ```bash
  source config.env  # charge WP_USER + WP_APP_PASSWORD depuis config.env (gitignored)
  curl -X POST -u "$WP_USER:$WP_APP_PASSWORD" \
    -H "Content-Type: application/json" \
    -d '{"title":"test","status":"draft"}' \
    "$WP_BASE_URL/wp-json/wp/v2/posts"
  ```
  Si réponse `307` ou `403` → ouvrir cPanel → Sécurité → Tiger Protect → whitelister `/wp-json/*`

## 1. The7 → Theme Options → General

- [ ] **Layout** :
  - Site layout : `Wide` (full width)
  - Boxed shadow : `Off`
- [ ] **Color scheme** :
  - Primary accent color : `#0099ff`
  - Secondary accent : `#00e5ff`
  - Background : `#070b14`
  - Text color : `#e9eef7`

## 2. The7 → Theme Options → Header

- [ ] **Header style** : `Classic` (logo gauche, menu droite)
- [ ] **Header background** : `#070b14`
- [ ] **Sticky header** : `On` (smart sticky)
- [ ] **Header height** : `76px` (desktop) / `60px` (mobile)
- [ ] **Logo** : uploader le logo SVG/PNG (240×60 desktop / 120×40 mobile)

## 3. The7 → Theme Options → Typography

- [ ] **Body font** : `Manrope` (importer via Google Fonts dans The7 → Custom Fonts)
- [ ] **Headings font** : `Big Shoulders Display` (poids 900)
- [ ] **Font weight default** : 400
- [ ] **Headings transform** : `uppercase`

## 4. The7 → Theme Options → Footer

- [ ] **Footer style** : `4 columns`
- [ ] **Footer background** : `#0d1628`
- [ ] **Footer top border** : 2px solid `#0099ff`
- [ ] **Bottom bar** : centré + texte affiliation Amazon

## 5. The7 → Theme Options → Single Post

- [ ] **Sidebar position** : `Right` (par défaut, on overridera par article via meta)
- [ ] **Featured image** : `Hidden by default` (on l'affichera ailleurs)
- [ ] **Comments** : `Disabled` (à débattre — sinon installer Disqus)
- [ ] **Post format** : `Standard`

## 6. WordPress → Réglages → Discussion

- [ ] **Désactiver les commentaires** par défaut (Settings → Discussion → décocher "Allow people to submit comments")
- [ ] **Désactiver les pingbacks/trackbacks**

## 7. WordPress → Réglages → Lecture

- [ ] **Page d'accueil** : `Une page statique` → sélectionner "Accueil" (à créer)
- [ ] **Page d'articles** : `Blog` (à créer)
- [ ] **Articles par page** : 12

## 8. WordPress → Réglages → Médias

- [ ] **Tailles d'images** :
  - Vignette : 300×300 (recadré)
  - Moyenne : 600×600
  - Large : 1200×1200
- [ ] **Désactiver l'organisation par mois/année** (décocher "Organize my uploads")

## 9. Catégories à créer (Articles → Catégories)

| Slug | Nom | Description |
|------|-----|-------------|
| `beyblade-x` | Beyblade X | Gamme actuelle 2024-2026 |
| `beyblade-burst` | Beyblade Burst | Gamme 2016-2023 |
| `beyblade-metal-fusion` | Metal Fusion | Classiques 2010-2013 |
| `arenes` | Arènes Beyblade | Stadiums |
| `lanceurs` | Lanceurs Beyblade | Launchers + accessoires |
| `guides` | Guides d'achat | Guides éditoriaux |
| `actus` | Actus | Blog news |

## 10. Pages à créer (vides pour l'instant)

| Slug | Titre |
|------|-------|
| `accueil` | Accueil |
| `tous-les-beyblade` | Tous les Beyblade |
| `comparatif-beyblade-x` | Comparatif Beyblade X |
| `comparatif-beyblade-burst` | Comparatif Beyblade Burst |
| `comparatif-beyblade-metal-fusion` | Comparatif Metal Fusion |
| `comparatif-arenes` | Comparatif Arènes |
| `comparatif-lanceurs` | Comparatif Lanceurs |
| `comparatifs` | Tous les comparatifs |
| `meilleur-toupie-beyblade` | Meilleur toupie Beyblade |
| `toupie-beyblade-la-plus-forte` | La toupie Beyblade la plus forte |
| `contact` | Contact |

## 11. Menu principal (Apparence → Menus)

Créer un menu nommé "Principal" avec :
- Accueil
- Toutes les toupies → `/tous-les-beyblade/`
- Comparatifs (avec sous-menu) :
  - Beyblade X
  - Beyblade Burst
  - Metal Fusion
  - Arènes
  - Lanceurs
- Guides
- Blog
- Contact

L'assigner à `Primary menu`.

## 12. Plugins à installer (essentiels)

- [ ] **Yoast SEO** (free) — meta descriptions + sitemaps
- [ ] **LiteSpeed Cache** (déjà inclus o2switch ?) — performance
- [ ] **Wordfence** ou **All-In-One Security** — sécurité
- [ ] (optionnel) **Disqus** si commentaires souhaités

## 13. Déploiement initial via FTP

Une fois le back-office configuré, déposer dans `/wp-content/mu-plugins/` :
- [ ] `beyblade-redirects.php` (déjà prêt dans `beyblade-blog/mu-plugins/`)
- [ ] `beyblade-custom.php` (à créer — CSS responsive, JS, REST endpoint The7)
- [ ] `beyblade-mobile-menu.php` (à créer — hamburger flottant + drawer)

## ✅ Confirmation finale

Une fois ces 13 étapes faites, me prévenir → on lance Phase 2 (génération du premier article pilote).
