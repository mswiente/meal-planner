<?php
defined('ABSPATH') || exit;
?>

<article id="post-<?php the_ID(); ?>" <?php post_class('post-card card'); ?>>
    <?php if (has_post_thumbnail()): ?>
        <div class="card-image">
            <a href="<?php the_permalink(); ?>" tabindex="-1" aria-hidden="true">
                <?php the_post_thumbnail('card'); ?>
            </a>
        </div>
    <?php endif; ?>

    <div class="card-body">
        <time class="card-date" datetime="<?php echo esc_attr(get_the_date('c')); ?>">
            <?php echo esc_html(get_the_date()); ?>
        </time>

        <h2 class="card-title">
            <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
        </h2>

        <div class="card-excerpt">
            <?php the_excerpt(); ?>
        </div>

        <a href="<?php the_permalink(); ?>" class="btn btn--sm btn--text">
            <?php esc_html_e('Weiterlesen →', 'pusteblume'); ?>
        </a>
    </div>
</article>
