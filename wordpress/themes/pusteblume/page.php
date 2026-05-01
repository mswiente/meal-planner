<?php
defined('ABSPATH') || exit;
get_header();
?>

<div class="page-hero page-hero--small">
    <div class="container">
        <h1 class="page-hero-title"><?php the_title(); ?></h1>
        <?php
        if (function_exists('bcn_display')) {
            echo '<nav class="breadcrumb" aria-label="Breadcrumb">';
            bcn_display();
            echo '</nav>';
        }
        ?>
    </div>
</div>

<main id="primary" class="site-main">
    <div class="container">
        <div class="content-sidebar-grid">
            <div class="content-area">
                <?php while (have_posts()): the_post(); ?>
                    <article id="post-<?php the_ID(); ?>" <?php post_class('page-content'); ?>>
                        <?php if (has_post_thumbnail()): ?>
                            <div class="page-featured-image">
                                <?php the_post_thumbnail('large'); ?>
                            </div>
                        <?php endif; ?>
                        <div class="entry-content">
                            <?php
                            the_content();
                            wp_link_pages(['before' => '<nav class="page-links">', 'after' => '</nav>']);
                            ?>
                        </div>
                    </article>
                <?php endwhile; ?>
            </div>

            <aside class="sidebar" id="secondary">
                <?php get_sidebar(); ?>
            </aside>
        </div>
    </div>
</main>

<?php get_footer(); ?>
