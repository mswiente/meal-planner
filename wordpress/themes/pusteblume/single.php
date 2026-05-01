<?php
defined('ABSPATH') || exit;
get_header();
?>

<div class="page-hero page-hero--small">
    <div class="container">
        <h1 class="page-hero-title"><?php the_title(); ?></h1>
    </div>
</div>

<main id="primary" class="site-main">
    <div class="container">
        <div class="content-sidebar-grid">
            <div class="content-area">
                <?php while (have_posts()): the_post(); ?>
                    <article id="post-<?php the_ID(); ?>" <?php post_class('single-post'); ?>>
                        <header class="entry-header">
                            <div class="entry-meta">
                                <time class="entry-date" datetime="<?php echo esc_attr(get_the_date('c')); ?>">
                                    <?php echo esc_html(get_the_date()); ?>
                                </time>
                                <?php if ($category = get_the_category()): ?>
                                    <span class="entry-category"><?php echo esc_html($category[0]->name); ?></span>
                                <?php endif; ?>
                            </div>
                        </header>

                        <?php if (has_post_thumbnail()): ?>
                            <div class="entry-thumbnail">
                                <?php the_post_thumbnail('large'); ?>
                            </div>
                        <?php endif; ?>

                        <div class="entry-content">
                            <?php the_content(); ?>
                        </div>

                        <footer class="entry-footer">
                            <?php the_tags('<div class="entry-tags">' . __('Schlagwörter: ', 'pusteblume'), ', ', '</div>'); ?>
                        </footer>
                    </article>

                    <nav class="post-navigation">
                        <?php
                        the_post_navigation([
                            'prev_text' => '← %title',
                            'next_text' => '%title →',
                        ]);
                        ?>
                    </nav>
                <?php endwhile; ?>
            </div>

            <aside class="sidebar" id="secondary">
                <?php get_sidebar(); ?>
            </aside>
        </div>
    </div>
</main>

<?php get_footer(); ?>
