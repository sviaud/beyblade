<?php
/**
 * Plugin Name: Beyblade — Redirections legacy
 * Description: Redirige les anciennes URLs toupiebeyblade.fr (2011-2013) vers les nouvelles fiches pour préserver les 305 backlinks survivants
 * Version: 1.0.0
 * Author: toupiebeyblade.fr
 *
 * Déployer dans /wp-content/mu-plugins/ — actif automatiquement.
 * Aucune action admin nécessaire.
 *
 * Test : curl -sI https://toupiebeyblade.fr/avis/rock-leone/ doit renvoyer 301 → /rock-leone/
 */

if (!defined('ABSPATH')) exit;

add_action('init', function () {
    if (is_admin() || wp_doing_ajax() || wp_doing_cron()) return;
    if (defined('DOING_AJAX') && DOING_AJAX) return;

    $request_uri = $_SERVER['REQUEST_URI'] ?? '';
    $path = strtok($request_uri, '?');

    // Ne pas intercepter les fichiers statiques (images, CSS, JS, sitemaps...)
    if (preg_match('#\.(jpg|jpeg|png|gif|webp|svg|css|js|xml|txt|pdf|ico)$#i', $path)) return;

    /**
     * Mapping ordonné : la première règle qui matche gagne.
     * Les règles spécifiques DOIVENT être avant les règles génériques.
     */
    $redirects = [
        // ===== Anciennes fiches /avis/{slug}/ — règles spécifiques d'abord =====
        // Ces 4 toupies ont des backlinks dédiés ET un volume de recherche actuel
        '#^/avis/ray-unicorno/?#i'                  => '/ray-unicorno/',
        '#^/avis/rock-leone/?#i'                    => '/rock-leone/',
        '#^/avis/meteo-l-drago/?#i'                 => '/meteo-l-drago/',
        '#^/avis/galaxy-pegasus/?#i'                => '/galaxy-pegasus/',

        // ===== Catégories de saisons =====
        '#^/saison/metal-master/?$#i'               => '/beyblade-metal-fusion/',
        '#^/saison/metal-fusion/?$#i'               => '/beyblade-metal-fusion/',
        '#^/saison/metal-fight/?$#i'                => '/beyblade-metal-fusion/',

        // ===== Catégories par type =====
        '#^/categorie/attaque/?#i'                  => '/comparatif-beyblade-burst/?type=attaque',
        '#^/categorie/defense/?#i'                  => '/comparatif-beyblade-burst/?type=defense',
        '#^/categorie/endurance/?#i'                => '/comparatif-beyblade-burst/?type=stamina',
        '#^/categorie/equilibre/?#i'                => '/comparatif-beyblade-burst/?type=equilibre',

        // ===== Pièces génériques (Burst Layer system, Metal Fusion 4-part system) =====
        '#^/(roue-fusion|facebolt|axe-rotation|anneau-energie|pointe-performance)/.+#i' => '/beyblade-metal-fusion/',
        '#^/(layer|disc|driver)/.+#i'               => '/beyblade-burst/',

        // ===== Avis génériques (toutes autres fiches non recréées) =====
        '#^/avis/.+#i'                              => '/beyblade-metal-fusion/',

        // ===== Pages éditoriales =====
        '#^/tests/?$#i'                             => '/comparatifs/',
        '#^/test/?$#i'                              => '/comparatifs/',
        '#^/boutique/?$#i'                          => '/',
        '#^/shop/?$#i'                              => '/',
    ];

    foreach ($redirects as $pattern => $target) {
        if (preg_match($pattern, $path)) {
            $url = home_url($target);
            // Log discret pour debug (1ère semaine après déploiement)
            if (defined('WP_DEBUG') && WP_DEBUG) {
                error_log("[beyblade-redirects] $path → $url");
            }
            wp_redirect($url, 301);
            exit;
        }
    }
});

/**
 * Bonus : log d'audit des hits redirigés (à activer/désactiver selon le besoin).
 * Décommenter si vous voulez compter les redirections par jour pendant le 1er mois.
 */
/*
add_action('init', function () {
    if (is_admin()) return;
    $path = strtok($_SERVER['REQUEST_URI'] ?? '', '?');
    if (preg_match('#^/(avis|saison|categorie|roue-fusion|facebolt|axe-rotation|anneau-energie|pointe-performance|tests|boutique)/?#i', $path)) {
        $log_file = WP_CONTENT_DIR . '/beyblade-redirects.log';
        $line = date('Y-m-d H:i:s') . " | $path | " . ($_SERVER['HTTP_REFERER'] ?? '-') . "\n";
        @file_put_contents($log_file, $line, FILE_APPEND);
    }
}, 5); // priorité 5 = avant la redirection
*/
