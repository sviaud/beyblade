# Queue de production — toupiebeyblade.fr

> **Fonctionnement** : un agent autonome lit ce fichier chaque jour, prend la première entrée de la section `## TODO`, produit la page, et la déplace en `## DONE` après push réussi.
>
> **Format** : YAML par entrée (entre `` ```yaml `` et `` ``` ``). Champ `type` détermine le workflow.
>
> **Types supportés** :
> - `fiche-produit-mf` → fiche Metal Fusion (template `article_rock_leone.html`)
> - `fiche-produit-x` → fiche Beyblade X (template `article_dran_sword.html`)
> - `fiche-produit-burst` → fiche Burst (template `article_dran_sword.html` adapté)
> - `page-comparatif` → page hub gamme (template `page_comparatif_metal_fusion.html`)
>
> **Si type non reconnu** : l'agent skip l'entrée et la déplace en `## BACKLOG` (production manuelle requise).

---

## TODO (par ordre de priorité SEO — l'agent prend toujours le 1er)

```yaml
type: fiche-produit-burst
slug: lord-spryzen-s5-pro-series
name: Lord Spryzen S5 (Pro Series)
ref: F2334
type_toupie: equilibre
year: 2021
score: 8.5
template: article_cyclone_roktavor_r7.html
lore_owner: "Shu Kurenai (lignée Spryzen)"
lore_anime: "Beyblade Burst (saisons 1 à 6)"
lore_key: "Pro Series version premium métal pour collectionneurs adultes — la lignée Spryzen est l'une des plus iconiques (Wyvron, Wyvern, Salamander, Spriggan, Requiem, Lord). Lord Spryzen S5 = aboutissement collector."
priority_reason: "Étoffe le comparatif Burst déjà existant — 4ème fiche Burst, ouverture sur la sous-série Pro Series collector."
```

```yaml
type: fiche-produit-burst
slug: brave-valtryek-v6
name: Brave Valtryek V6
ref: F4736
type_toupie: attaque
year: 2021
score: 8.3
template: article_cyclone_roktavor_r7.html
lore_owner: "Valt Aoi"
lore_anime: "Beyblade Burst Surge / Rise (saisons 4-5)"
lore_key: "Lignée Valtryek = LA toupie iconique de Burst, équivalent de Pegasus pour Metal Fight. Brave Valtryek V6 = dernière itération principale (Driver Brave à transformations)."
priority_reason: "Valt Aoi est le héros principal de Burst (saisons 1 à 6) — lignée Valtryek = #1 search 'valtryek beyblade' (15k/mois). Indispensable pour étoffer le comparatif Burst."
```

---

## BACKLOG (production manuelle requise — pas de template auto)

Pages stratégiques à fort impact SEO mais qui demandent une production éditoriale spécifique (long-form curaté). À produire manuellement avec Claude Code en session interactive.

```yaml
type: page-guide-achat
slug: meilleur-toupie-beyblade
title: "Meilleur toupie Beyblade 2026 : notre guide d'achat complet"
seo_volume: 320
seo_intent: commercial
notes: "Guide d'achat top 10 par budget/profil. Long-form 2500+ mots. Comparatif tableau + recommandations par usage. Très haut potentiel conversion."
```

```yaml
type: page-listicle-snippet
slug: toupie-beyblade-la-plus-forte
title: "Toupie Beyblade la plus forte du monde en 2026 : le classement"
seo_volume: 210
seo_features: "Featured snippet (position 0) déjà visible sur cette query → opportunité"
notes: "Listicle Top 5 avec critères de force objectifs (poids, couple, KOs en tournoi). Format optimisé featured snippet : intro 50 mots + liste à puces."
```

```yaml
type: page-catalogue
slug: tous-les-beyblade
title: "Tous les Beyblade : catalogue complet 2026"
notes: "Page d'aiguillage avec grille de toutes les toupies par gamme. Version live de data/queue.md (TODO + DONE). Possible auto-génération depuis le data file."
```

```yaml
type: page-coloriages
slug: coloriage-toupie-beyblade
seo_volume: 590
seo_intent: informational (kids)
notes: "1 860 recherches cumulées /mois (toutes variantes). Volume très élevé, monétisation faible mais excellent backlink potentiel. À produire avec ressources d'images dédiées."
```

---

## DONE (pages déjà produites, par ordre chronologique)

```yaml
slug: index
type: homepage
date_published: 2026-04-20
note: "Homepage avec ItemList Top 4 + FAQPage 5 Q&A + about-intro citable AIO"
```

```yaml
slug: dran-sword-3-60f
name: Dran Sword 3-60F
type: fiche-produit-x
gamme: beyblade-x
ref: BX-01
score: 8.5
date_published: 2026-04-19
template: article_dran_sword.html
```

```yaml
slug: rock-leone-145wb
name: Rock Leone 145WB
type: fiche-produit-mf
gamme: beyblade-metal-fusion
ref: BB-30
score: 8.1
date_published: 2026-04-20
template: article_rock_leone.html
```

```yaml
slug: meteo-l-drago-lw105lrf
name: Meteo L-Drago LW105LRF
type: fiche-produit-mf
gamme: beyblade-metal-fusion
ref: BB-88
score: 7.5
date_published: 2026-04-20
template: article_meteo_l_drago.html
```

```yaml
slug: galaxy-pegasus-w105r2f
name: Galaxy Pegasus W105R²F
type: fiche-produit-mf
gamme: beyblade-metal-fusion
ref: BB-70
score: 7.7
date_published: 2026-04-20
template: article_galaxy_pegasus.html
```

```yaml
slug: comparatif-beyblade-metal-fusion
type: page-comparatif
gamme_slug: beyblade-metal-fusion
date_published: 2026-04-20
template: page_comparatif_metal_fusion.html
```

```yaml
slug: comparatif-beyblade-x
type: page-comparatif
gamme_slug: beyblade-x
date_published: 2026-04-21
template: page_comparatif_beyblade_x.html
note: "Production manuelle (agent remote bloqué par auth git push). Repo passé en public pour fix futur."
```

```yaml
slug: phoenix-wing-9-60gf
name: Phoenix Wing 9-60GF
type: fiche-produit-x
gamme: beyblade-x
ref: BX-23
score: 8.8
date_published: 2026-04-22
template: article_phoenix_wing_9_60gf.html
note: "Production manuelle. Image transparente déjà dispo donc rotation active. Internal links updated: homepage cards now linkable + comparatif X table marked Testée."
```

```yaml
slug: knight-shield-3-80n
name: Knight Shield 3-80N
type: fiche-produit-x
gamme: beyblade-x
ref: BX-04
score: 8.2
date_published: 2026-04-22
template: article_knight_shield_3_80n.html
note: "Production manuelle (batch x2 avec Wizard Arrow). Image transparente, rotation active. Comparatif X mis à jour (4 toupies testées)."
```

```yaml
slug: wizard-arrow-4-80b
name: Wizard Arrow 4-80B
type: fiche-produit-x
gamme: beyblade-x
ref: BX-03
score: 8.4
date_published: 2026-04-22
template: article_wizard_arrow_4_80b.html
note: "Production manuelle (batch x2 avec Knight Shield). Image transparente, rotation active. Stamina pure du starter trio."
```

```yaml
slug: storm-pegasus-105rf
name: Storm Pegasus 105RF
type: fiche-produit-mf
gamme: beyblade-metal-fusion
ref: BB-28
score: 8.0
date_published: 2026-04-22
template: article_storm_pegasus_105rf.html
note: "Production manuelle. SVG placeholder (pas d'image transparente trouvée — Amazon n'a qu'un packshot boîte). Image transparente à fournir manuellement par l'utilisateur."
```

```yaml
slug: ray-unicorno-d125cs
name: Ray Unicorno D125CS
type: fiche-produit-mf
gamme: beyblade-metal-fusion
ref: BB-71
score: 7.8
date_published: 2026-04-22
template: article_ray_unicorno_d125cs.html
note: "Production manuelle. SVG placeholder (Amazon ASIN B005ASZ5LE = page introuvable). Active la 4e redirection backlink legacy /avis/ray-unicorno/. Image transparente à fournir."
```

```yaml
slug: l-drago-destroy-fs
name: L-Drago Destroy F:S
type: fiche-produit-mf
gamme: beyblade-metal-fusion
ref: BB-108
score: 8.4
date_published: 2026-04-22
template: article_l_drago_destroy_fs.html
note: "Production manuelle (batch x3 avec Hells Scythe + Cobalt Dragoon). SVG placeholder (rouge). Évolution 4D ultime de Ryuga. Comparatif MF mis à jour (6 toupies testées)."
```

```yaml
slug: hells-scythe-4-60t
name: Hells Scythe 4-60T
type: fiche-produit-x
gamme: beyblade-x
ref: BX-02
score: 8.3
date_published: 2026-04-22
template: article_hells_scythe_4_60t.html
note: "Production manuelle (batch x3 avec L-Drago Destroy + Cobalt Dragoon). SVG placeholder (vert). Stamina-defense hybride du quatuor inaugural Beyblade X."
```

```yaml
slug: cobalt-dragoon-2-60c
name: Cobalt Dragoon 2-60C
type: fiche-produit-x
gamme: beyblade-x
ref: BX-34
score: 8.6
date_published: 2026-04-22
template: article_cobalt_dragoon_2_60c.html
note: "Production manuelle (batch x3 avec L-Drago Destroy + Hells Scythe). SVG placeholder (bleu). Première left-spin Beyblade X — Spin Steal. Comparatif X mis à jour (6 toupies testées)."
```

```yaml
slug: earth-eagle-145wd
name: Earth Eagle 145WD
type: fiche-produit-mf
gamme: beyblade-metal-fusion
ref: BB-47
score: 7.6
date_published: 2026-04-23
template: article_earth_eagle_145wd.html
note: "Production manuelle (batch x3 avec Dran Buster + Cyclone Roktavor). SVG placeholder (vert). 2e défenseuse MF de Tsubasa Otori (Earth Aquila chez Hasbro EU). Comparatif MF mis à jour (7 toupies testées)."
```

```yaml
slug: dran-buster-1-60a
name: Dran Buster 1-60A
type: fiche-produit-x
gamme: beyblade-x
ref: UX-01
score: 9.0
date_published: 2026-04-23
template: article_dran_buster_1_60a.html
note: "Production manuelle (batch x3 avec Earth Eagle + Cyclone Roktavor). SVG placeholder (bleu). Première Unique-X (UX) Beyblade X — Blade métal + 1-lobe Ratchet + Bit Accel. Comparatif X mis à jour (7 toupies testées)."
```

```yaml
slug: cyclone-roktavor-r7
name: Cyclone Roktavor R7
type: fiche-produit-burst
gamme: beyblade-burst
ref: F4067
score: 8.0
date_published: 2026-04-23
template: article_cyclone_roktavor_r7.html
note: "Production manuelle (batch x3 avec Earth Eagle + Dran Buster). SVG placeholder (rouge énergie). 1ère fiche Burst — toupie d'Aiger Akabane saison 6 Quad Drive. Breadcrumb /comparatif-beyblade-burst/ encore 404 (à venir au prochain batch)."
```

```yaml
slug: comparatif-beyblade-burst
type: page-comparatif
gamme_slug: beyblade-burst
date_published: 2026-04-23
template: page_comparatif_beyblade_burst.html
note: "Production manuelle (batch x3 avec Vanish Fafnir + Stellar Hyperion). Hub Burst gamme 2016-2023. 3 toupies testées (Cyclone Roktavor + Vanish Fafnir + Stellar Hyperion) + 6 références à venir (Lord Spryzen, Brave Valtryek, Ace Dragon, Z Achilles, Spryzen Requiem, Air Knight). Résout le 404 du breadcrumb Cyclone Roktavor."
```

```yaml
slug: vanish-fafnir-f7
name: Vanish Fafnir F7
type: fiche-produit-burst
gamme: beyblade-burst
ref: F3966
score: 8.2
date_published: 2026-04-23
template: article_vanish_fafnir_f7.html
note: "Production manuelle (batch x3 avec comparatif Burst + Stellar Hyperion). SVG placeholder (vert). Stamina culte de Free de la Hoya — rotation gauche + Spin Steal. 4e itération de la lignée Fafnir."
```

```yaml
slug: stellar-hyperion-h8
name: Stellar Hyperion H8
type: fiche-produit-burst
gamme: beyblade-burst
ref: F6809
score: 8.5
date_published: 2026-04-23
template: article_stellar_hyperion_h8.html
note: "Production manuelle (batch x3 avec comparatif Burst + Vanish Fafnir). SVG placeholder (bleu acier). Attaquante de Lui Shirosagi, sub-série Quad Strike (exclusivité Hasbro EU/US, jamais sortie au Japon). ASIN B0BLNY6Q2K à confirmer."
```
