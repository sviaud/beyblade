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
type: fiche-produit-x
slug: phoenix-wing-9-60gf
name: Phoenix Wing 9-60GF
ref: BX-23
type_toupie: equilibre
year: 2024
asin: B0CMZSRJ3Q
score: 8.8
template: article_dran_sword.html
image: /img/phoenix-wing.webp
image_transparent: true
lore_owner: "Tairyu"
lore_anime: "Beyblade X (saison 1, 2023→)"
lore_key: "Hybride attaque-stamina avec Driver Gear Flat révolutionnaire (régénération de spin via engrenage interne). Une des plus polyvalentes de la gamme X. Iconique du clan Tairyu dans l'anime."
blade: "Phoenix Wing — 9 ailettes asymétriques en couronne"
ratchet: "9-60 — 9 lobes hauteur 6.0mm (équilibre)"
bit: "GF (Gear Flat) — pointe plate avec engrenage interne qui régénère le spin"
priority_reason: "Fiche phare X (8.8/10) avec image transparente disponible — rotation active. Clé pour comparatif X."
```

```yaml
type: fiche-produit-x
slug: knight-shield-3-80n
name: Knight Shield 3-80N
ref: BX-04
type_toupie: defense
year: 2023
asin: B0C52S6SNN
score: 8.2
template: article_dran_sword.html
image: /img/knight-shield.webp
image_transparent: true
lore_owner: "Multi (toupie débutant)"
lore_anime: "Beyblade X (saison 1, 2023→)"
lore_key: "La défense entry-level de la gamme X — recommandée pour débuter. Hasbro l'a renommée Helm Knight en EU. Pardonnante aux erreurs de lancer."
blade: "Knight Shield — forme bouclier rond protecteur"
ratchet: "3-80 — 3 lobes hauteur 8.0mm"
bit: "N (Needle) — pointe acier fine (haute précision)"
priority_reason: "Fiche débutant + image transparente dispo — rotation active. Souvent recherchée."
```

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
type: fiche-produit-x
slug: wizard-arrow-4-80b
name: Wizard Arrow 4-80B
ref: BX-03
type_toupie: stamina
year: 2023
asin: B0C52TTRDX
score: 8.4
template: article_dran_sword.html
image: /img/wizard-arrow.webp
image_transparent: true
lore_owner: "Multi"
lore_anime: "Beyblade X (saison 1, 2023→)"
lore_key: "La 3e du starter trio Beyblade X (avec Dran Sword + Hells Scythe). Stamina pure — la toupie qui tourne le plus longtemps de la gamme. Iconique du sorcier."
blade: "Wizard Arrow — 4 ailettes incurvées en flèche"
ratchet: "4-80 — 4 lobes hauteur 8.0mm"
bit: "B (Ball) — bille stamina premium"
priority_reason: "Fiche starter X + image transparente dispo. Cible 'wizard arrow beyblade x' search."
```

```yaml
type: fiche-produit-mf
slug: ray-unicorno-d125cs
name: Ray Unicorno D125CS
ref: BB-71
type_toupie: attaque
year: 2010
asin: B005ASZ5LE
score: 7.8
template: article_rock_leone.html
lore_owner: "Masamune Kadoya"
lore_anime: "Metal Fight Beyblade : Baku (saison 2, 2010-2011)"
lore_key: "L'attaquante équilibrée par excellence — fan-favorite Hasbro EU. La D125 Defense Track la rend plus stable que la moyenne des attaquantes."
fusion_wheel: "Ray (alliage métallique léger ~24g, 6 lobes pointus)"
energy_ring: "Unicorno (bleu/blanc, motif licorne)"
spin_track: "D125 (Defense Track 12.5mm)"
performance_tip: "CS (Coat Sharp) — pointe acier recouverte plastique"
priority_reason: "4e backlink critique Metal Fusion — active /avis/ray-unicorno/ → /ray-unicorno-d125cs/."
```

```yaml
type: fiche-produit-mf
slug: storm-pegasus-105rf
name: Storm Pegasus 105RF
ref: BB-28
type_toupie: attaque
year: 2010
asin: B004AY8ICE
score: 8.0
template: article_galaxy_pegasus.html
lore_owner: "Ginga Hagane"
lore_anime: "Metal Fight Beyblade (saison 1, 2009-2010)"
lore_key: "LA toupie originelle de Ginga, cultissime. Predécesseure directe de Galaxy Pegasus W105R²F. La 1ère toupie en main de tout fan de l'anime."
fusion_wheel: "Storm (4 lobes asymétriques ~22g)"
energy_ring: "Pegasus (blanc/bleu, motif ailé)"
spin_track: "105 (low height 10.5mm)"
performance_tip: "RF (Rubber Flat) — caoutchouc plat agressif"
priority_reason: "Toupie cultissime, prédécesseure de Galaxy Pegasus déjà testée. Volume search élevé sur 'storm pegasus prix'."
```

```yaml
type: fiche-produit-mf
slug: l-drago-destroy-fs
name: L-Drago Destroy F:S
ref: BB-108
type_toupie: attaque
year: 2011
asin: B005U8KMJM
score: 8.4
template: article_meteo_l_drago.html
lore_owner: "Ryuga"
lore_anime: "Metal Fight Beyblade : 4D (saison 3, 2011-2012)"
lore_key: "Évolution ultime de la lignée L-Drago. Mode Attack/Defense switchable via la pointe F:S (Final Survive). La toupie de Ryuga dans la finale du tournoi mondial."
fusion_wheel: "L-Drago II (gauche, ~25g, design dragon agressif)"
energy_ring: "L-Drago II (rouge/noir)"
spin_track: "MF (Metal Frame — frame métallique additionnelle)"
performance_tip: "F:S (Final Survive — pointe switch attaque/défense)"
priority_reason: "Évolution de Meteo L-Drago déjà testée — maillage interne. Search élevé 'l-drago destroy avis'."
```

```yaml
type: fiche-produit-x
slug: hells-scythe-4-60t
name: Hells Scythe 4-60T
ref: BX-02
type_toupie: stamina
year: 2023
asin: B0C52C4L3T
score: 8.3
template: article_dran_sword.html
lore_owner: "Multi"
lore_anime: "Beyblade X (saison 1, 2023→)"
lore_key: "La 2e toupie du starter trio Beyblade X. Stamina-defense hybride avec Bit Taper unique. Hasbro l'a renommée Hells Size en EU."
blade: "Hells Scythe — faux du diable, 4 lames courbées"
ratchet: "4-60 — 4 lobes 6.0mm"
bit: "T (Taper) — pointe conique progressive (entre stamina et défense)"
priority_reason: "Fiche starter X — complète le trio (Dran Sword + Wizard Arrow + Hells Scythe)."
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
slug: cobalt-dragoon-2-60c
name: Cobalt Dragoon 2-60C
ref: BX-34
type_toupie: attaque
year: 2024
asin: B0D6MZB1VF
score: 8.6
template: article_dran_sword.html
lore_owner: "Kuroda Hyo"
lore_anime: "Beyblade X (saison 2, 2024)"
lore_key: "Attaquante GAUCHE (Left-Spin) — rare dans la gamme X. Concept similaire à Meteo L-Drago. Évolution du dragon. Hasbro l'a renommée Cobalt Drake en EU."
blade: "Cobalt Dragoon — gauche, 2 lobes massifs"
ratchet: "2-60 — 2 lobes 6.0mm (équilibre extrême)"
bit: "C (Cyclone) — pointe rotative"
priority_reason: "Première attaquante gauche Beyblade X — niche search 'cobalt dragoon left spin'."
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
