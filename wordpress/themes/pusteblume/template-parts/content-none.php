<?php
defined('ABSPATH') || exit;
?>

<section class="no-results">
    <h2><?php esc_html_e('Nichts gefunden', 'pusteblume'); ?></h2>
    <p><?php esc_html_e('Leider wurden keine Inhalte gefunden. Versuche eine Suche.', 'pusteblume'); ?></p>
    <?php get_search_form(); ?>
</section>
