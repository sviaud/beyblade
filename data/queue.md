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
type: page-comparatif
slug: comparatif-beyblade-burst
title: "Comparatif Beyblade Burst 2026 : Quad Drive, Quad Strike et Pro Series"
description: "Comparatif des meilleures Beyblade Burst (Quad Drive, Quad Strike, Pro Series). Cyclone Roktavor, Stellar Hyperion, Vanish Fafnir et plus — notes et recommandations."
gamme_label: "Beyblade Burst"
gamme_slug: beyblade-burst
gamme_year: "Saison 2016-2023"
gamme_intro: |
  Beyblade Burst (sortie 2016, dernière sous-série Quad Strike en 2023) est la 2ème génération moderne de la franchise.
  Système Layer/Disc/Driver avec mécanique d'éclatement (Burst Finish). Catalogue le plus large de la franchise — 200+ toupies sorties au total.
seo_volume: 480
seo_keywords:
  - "comparatif beyblade burst"
  - "meilleur beyblade burst"
priority_reason: "Active redirects /categorie/attaque/, /categorie/defense/ + cible 480 recherches/mois. Permet de se positionner sur Burst sans avoir 11 fiches."
toupies_testees: []
toupies_a_venir:
  - {ref: F4067, name: "Cyclone Roktavor R7", type: attaque}
  - {ref: F6809, name: "Stellar Hyperion H8", type: attaque}
  - {ref: F3966, name: "Vanish Fafnir F7", type: stamina}
  - {ref: F2334, name: "Lord Spryzen S5 (Pro Series)", type: equilibre}
```

```yaml
type: fiche-produit-mf
slug: earth-eagle-145wd
name: Earth Eagle 145WD
ref: BB-47
type_toupie: defense
year: 2010
asin: B0050OMBU8
score: 7.6
template: article_rock_leone.html
lore_owner: "Tsubasa Otori"
lore_anime: "Metal Fight Beyblade (saison 1, 2009-2010)"
lore_key: "Defense ailée — Hasbro l'a renommée Earth Aquila en EU. La rivale historique de Rock Leone en gamme défense."
fusion_wheel: "Earth (alliage lourd ~28g, motif aigle)"
energy_ring: "Eagle (vert/jaune, motif rapace)"
spin_track: "145 (high 14.5mm pour défense)"
performance_tip: "WD (Wide Defense) — semi-bille large"
priority_reason: "2e défenseuse Metal Fusion (après Rock Leone) — étoffe la gamme."
```

```yaml
type: fiche-produit-x
slug: dran-buster-1-60a
name: Dran Buster 1-60A
ref: UX-01
type_toupie: attaque
year: 2024
asin: B0CV7HF3W6
score: 9.0
template: article_dran_sword.html
lore_owner: "Bird Maru"
lore_anime: "Beyblade X (saison 2, 2024)"
lore_key: "Évolution Unique-X (UX) de Dran Sword. Blade en alliage métallique (vs plastique pour Dran Sword). La toupie la plus puissante de Bird en saison 2."
blade: "Dran Buster — 1 lobe massif métal"
ratchet: "1-60 — 1 lobe 6.0mm (extrême attaque)"
bit: "A (Accel) — pointe accélérante"
priority_reason: "Évolution de Dran Sword (notre 1ère fiche) — maillage interne fort. Note 9.0/10."
```

```yaml
type: fiche-produit-burst
slug: cyclone-roktavor-r7
name: Cyclone Roktavor R7
ref: F4067
type_toupie: attaque
year: 2022
asin: B09TGD75BP
score: 8.0
template: article_dran_sword.html
lore_owner: "Aiger Akabane"
lore_anime: "Beyblade Burst Quad Drive (saison 6, 2022)"
lore_key: "Quad Drive — système Driver à 4 modes interchangeables. Roktavor est le bey signature d'Aiger en saison 6."
layer: "Cyclone Roktavor — 3 lames Burst"
disc: "M (Metal disc 7 lobes)"
driver: "R (Revolve — Quad Drive 4 modes)"
priority_reason: "Première fiche Burst — étoffe le comparatif Burst déjà créé."
```

```yaml
type: fiche-produit-burst
slug: vanish-fafnir-f7
name: Vanish Fafnir F7
ref: F3966
type_toupie: stamina
year: 2022
asin: B09H17H8CD
score: 8.2
template: article_dran_sword.html
lore_owner: "Free de la Hoya"
lore_anime: "Beyblade Burst Quad Drive (saison 6, 2022)"
lore_key: "Stamina iconique — Fafnir est la lignée stamina la plus aboutie de Burst. Capacité de Spin Steal en collision (vole l'énergie adverse)."
layer: "Vanish Fafnir — 3 lames stamina"
disc: "Q (Quad)"
driver: "Revolve (rotation aimantée)"
priority_reason: "Fafnir est culte — fan favorite Burst, fort search 'fafnir beyblade'."
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
