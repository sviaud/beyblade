# Stratégie de récupération des backlinks toupiebeyblade.fr

## Contexte

L'URL **toupiebeyblade.fr** a hébergé un blog WordPress sur les Beyblade Metal Fusion entre 2011 et ~2013. **305 backlinks survivants** pointent encore vers d'anciennes URLs. Source la plus autoritaire : **sudouest.fr** (ascore 18).

Le site est aujourd'hui vide. Sans redirections 301, **toute la link equity est perdue**. Avec des redirections bien faites, on récupère immédiatement un boost SEO substantiel + on évite que Google indexe 305 erreurs 404.

## Inventaire des URLs cibles à rediriger

| Pattern URL | Volume backlinks | Action |
|---|---|---|
| `/avis/{slug}/` | 23 | → `/{slug}/` (créer la fiche correspondante quand possible) |
| `/saison/metal-master/` | 5 | → `/beyblade-metal-fusion/` |
| `/categorie/attaque/` | 2 | → `/comparatif-beyblade-burst/?type=attaque` |
| `/categorie/defense/` | 2 | → `/comparatif-beyblade-burst/?type=defense` |
| `/roue-fusion/{nom}/` | 4 | → `/beyblade-metal-fusion/` |
| `/facebolt/{nom}/` | 4 | → `/beyblade-metal-fusion/` |
| `/axe-rotation/{nom}/` | 4 | → `/beyblade-metal-fusion/` |
| `/anneau-energie/{nom}/` | 4 | → `/beyblade-metal-fusion/` |
| `/pointe-performance/{nom}/` | 4 | → `/beyblade-metal-fusion/` |
| `/tests` (et `/tests/`) | 2 | → `/comparatifs/` |
| `/boutique/` | 2 | → `/` (homepage avec CTA Amazon) |
| `/wp-content/uploads/...jpg` | 13 | Laisser en 404 (images, peu de valeur SEO) |

**Total : ~280 URLs récupérables.**

## Anciennes fiches `/avis/{slug}/` à recréer en priorité

Ces 4 toupies Metal Fusion ont des backlinks dédiés ET un volume de recherche actuel. **Recréer ces 4 fiches en priorité** = double gain (backlink + SEO).

| Ancienne URL | Nouvelle URL | Volume search/mois | Action |
|---|---|---|---|
| `/avis/ray-unicorno/` | `/ray-unicorno/` | ~50 | Créer fiche Ray Unicorno D125 CS |
| `/avis/rock-leone/` | `/rock-leone/` | ~80 | Créer fiche Rock Leone 145WB |
| `/avis/meteo-l-drago/` | `/meteo-l-drago/` | ~70 | Créer fiche Meteo L-Drago LW105LRF |
| `/avis/beyblade-bounce/` | `/beyblade-bounce/` | <10 | Redirection vers `/beyblade-metal-fusion/` |

Anciennes pièces référencées (Galaxy Pegasus, Striker, Ketos, Giraffe, Grand) → on les couvre via la création de fiches Metal Fusion classiques (déjà 8 prévues dans le BRIEF, on s'aligne).

## Implémentation technique

### Option A — mu-plugin PHP (recommandé)

Créer `/wp-content/mu-plugins/beyblade-redirects.php` :

```php
<?php
/**
 * Plugin Name: Beyblade — Redirections legacy
 * Description: Redirige les anciennes URLs toupiebeyblade.fr (2011-2013) vers les nouvelles fiches
 */

add_action('init', function() {
    if (is_admin()) return;
    
    $request_uri = $_SERVER['REQUEST_URI'] ?? '';
    $path = strtok($request_uri, '?');
    
    $redirects = [
        // Saison
        '#^/saison/metal-master/?$#'           => '/beyblade-metal-fusion/',
        
        // Catégories
        '#^/categorie/attaque/?$#'             => '/comparatif-beyblade-burst/?type=attaque',
        '#^/categorie/defense/?$#'             => '/comparatif-beyblade-burst/?type=defense',
        
        // Pièces génériques → catégorie Metal Fusion
        '#^/(roue-fusion|facebolt|axe-rotation|anneau-energie|pointe-performance)/[^/]+/?$#' => '/beyblade-metal-fusion/',
        
        // Avis spécifiques → fiches recréées si dispo
        '#^/avis/ray-unicorno/?#'              => '/ray-unicorno/',
        '#^/avis/rock-leone/?#'                => '/rock-leone/',
        '#^/avis/meteo-l-drago/?#'             => '/meteo-l-drago/',
        
        // Avis génériques → catégorie Metal Fusion
        '#^/avis/[^/]+/?$#'                    => '/beyblade-metal-fusion/',
        
        // Pages génériques
        '#^/tests/?$#'                         => '/comparatifs/',
        '#^/boutique/?$#'                      => '/',
    ];
    
    foreach ($redirects as $pattern => $target) {
        if (preg_match($pattern, $path)) {
            wp_redirect(home_url($target), 301);
            exit;
        }
    }
});
```

Avantages : facile à maintenir, géré au niveau PHP (= avant le rendu WordPress), pas de tâche dans le panneau admin.

### Option B — `.htaccess` (plus rapide mais moins flexible)

Ajouter dans le `.htaccess` racine :

```apache
RewriteEngine On
RewriteRule ^saison/metal-master/?$ /beyblade-metal-fusion/ [R=301,L]
RewriteRule ^categorie/attaque/?$ /comparatif-beyblade-burst/?type=attaque [R=301,L]
RewriteRule ^categorie/defense/?$ /comparatif-beyblade-burst/?type=defense [R=301,L]
RewriteRule ^(roue-fusion|facebolt|axe-rotation|anneau-energie|pointe-performance)/.+ /beyblade-metal-fusion/ [R=301,L]
RewriteRule ^avis/ray-unicorno/?$ /ray-unicorno/ [R=301,L]
RewriteRule ^avis/rock-leone/?$ /rock-leone/ [R=301,L]
RewriteRule ^avis/meteo-l-drago/?$ /meteo-l-drago/ [R=301,L]
RewriteRule ^avis/.+ /beyblade-metal-fusion/ [R=301,L]
RewriteRule ^tests/?$ /comparatifs/ [R=301,L]
RewriteRule ^boutique/?$ / [R=301,L]
```

Risque sur o2switch : le `.htaccess` peut être écrasé par WordPress lors d'une mise à jour de permaliens. **Préférer l'option A.**

## Vérification après déploiement

Une fois le mu-plugin actif, valider avec :

```bash
for url in \
  "https://toupiebeyblade.fr/avis/rock-leone/" \
  "https://toupiebeyblade.fr/saison/metal-master/" \
  "https://toupiebeyblade.fr/categorie/attaque/" \
  "https://toupiebeyblade.fr/roue-fusion/galaxy-2/" ; do
  echo "=== $url ===" 
  curl -sI -o /dev/null -w "%{http_code} → %{redirect_url}\n" "$url"
done
```

Réponse attendue : `301 → https://toupiebeyblade.fr/beyblade-metal-fusion/` (ou autre cible selon mapping).

## Bonus SEO

Une fois les redirections actives :
1. Soumettre la nouvelle sitemap à Google Search Console
2. Demander une réindexation des anciennes URLs (forcer Google à re-crawler et voir le 301)
3. Surveiller dans GSC l'évolution des "couverture URL" : on doit voir les 404 disparaître au fil des semaines
4. Surveiller les positions de mot-clés "rock leone", "meteo l drago", "ray unicorno" → potentiel de Top 10 rapide grâce aux backlinks préservés
