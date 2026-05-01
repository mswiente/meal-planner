<?php
defined('ABSPATH') || exit;
get_header();
?>

<main id="primary" class="site-main front-page">

    <!-- Hero Section -->
    <section class="hero-section">
        <?php if (has_post_thumbnail(get_option('page_on_front'))): ?>
            <div class="hero-image">
                <?php echo get_the_post_thumbnail(get_option('page_on_front'), 'hero'); ?>
            </div>
        <?php else: ?>
            <div class="hero-image hero-image--placeholder"></div>
        <?php endif; ?>
        <div class="hero-content">
            <div class="container">
                <h1 class="hero-title"><?php echo esc_html(get_theme_mod('hero_title', get_bloginfo('name'))); ?></h1>
                <p class="hero-subtitle"><?php echo esc_html(get_theme_mod('hero_subtitle', get_bloginfo('description'))); ?></p>
                <?php if ($cta_url = get_theme_mod('hero_cta_url')): ?>
                    <a href="<?php echo esc_url($cta_url); ?>" class="btn btn--primary btn--large">
                        <?php echo esc_html(get_theme_mod('hero_cta_text', __('Mehr erfahren', 'pusteblume'))); ?>
                    </a>
                <?php endif; ?>
            </div>
        </div>
    </section>

    <!-- Welcome Section -->
    <section class="welcome-section section">
        <div class="container">
            <div class="welcome-grid">
                <div class="welcome-text">
                    <span class="section-label"><?php esc_html_e('Willkommen', 'pusteblume'); ?></span>
                    <h2><?php echo esc_html(get_theme_mod('welcome_title', __('Herzlich willkommen im Kindergarten Pusteblume', 'pusteblume'))); ?></h2>
                    <div class="welcome-body">
                        <?php echo wp_kses_post(get_theme_mod('welcome_text', __('Unser Kindergarten ist ein Ort, an dem Kinder spielen, lernen und wachsen können. Wir bieten eine liebevolle und förderliche Umgebung für alle Kinder.', 'pusteblume'))); ?>
                    </div>
                    <?php if ($welcome_page = get_theme_mod('welcome_page')): ?>
                        <a href="<?php echo esc_url(get_permalink($welcome_page)); ?>" class="btn btn--outline">
                            <?php esc_html_e('Über uns', 'pusteblume'); ?>
                        </a>
                    <?php endif; ?>
                </div>
                <div class="welcome-features">
                    <div class="feature-card">
                        <span class="feature-icon">🌱</span>
                        <h3><?php esc_html_e('Naturnah', 'pusteblume'); ?></h3>
                        <p><?php esc_html_e('Wir fördern die Verbindung zur Natur durch regelmäßige Ausflüge und Naturerlebnisse.', 'pusteblume'); ?></p>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">🎨</span>
                        <h3><?php esc_html_e('Kreativ', 'pusteblume'); ?></h3>
                        <p><?php esc_html_e('Durch Malen, Basteln und Musik fördern wir die Kreativität jedes Kindes.', 'pusteblume'); ?></p>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">🤝</span>
                        <h3><?php esc_html_e('Gemeinschaft', 'pusteblume'); ?></h3>
                        <p><?php esc_html_e('Soziales Lernen und ein respektvoller Umgang miteinander stehen bei uns im Mittelpunkt.', 'pusteblume'); ?></p>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">📚</span>
                        <h3><?php esc_html_e('Bildung', 'pusteblume'); ?></h3>
                        <p><?php esc_html_e('Spielerisches Lernen bereitet unsere Kinder optimal auf die Schule vor.', 'pusteblume'); ?></p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Groups Section -->
    <?php
    $gruppen = new WP_Query([
        'post_type'      => 'gruppe',
        'posts_per_page' => 3,
        'orderby'        => 'menu_order',
        'order'          => 'ASC',
    ]);
    if ($gruppen->have_posts()):
    ?>
    <section class="groups-section section section--bg">
        <div class="container">
            <div class="section-header">
                <span class="section-label"><?php esc_html_e('Unsere Gruppen', 'pusteblume'); ?></span>
                <h2><?php esc_html_e('Entdecke unsere Kindergartengruppen', 'pusteblume'); ?></h2>
            </div>
            <div class="cards-grid">
                <?php while ($gruppen->have_posts()): $gruppen->the_post(); ?>
                    <article class="group-card card">
                        <?php if (has_post_thumbnail()): ?>
                            <div class="card-image">
                                <a href="<?php the_permalink(); ?>">
                                    <?php the_post_thumbnail('card'); ?>
                                </a>
                            </div>
                        <?php endif; ?>
                        <div class="card-body">
                            <h3 class="card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
                            <p class="card-excerpt"><?php the_excerpt(); ?></p>
                            <a href="<?php the_permalink(); ?>" class="btn btn--sm btn--outline"><?php esc_html_e('Mehr erfahren', 'pusteblume'); ?></a>
                        </div>
                    </article>
                <?php endwhile; wp_reset_postdata(); ?>
            </div>
        </div>
    </section>
    <?php endif; ?>

    <!-- News Section -->
    <?php
    $news = new WP_Query([
        'post_type'      => 'post',
        'posts_per_page' => 3,
    ]);
    if ($news->have_posts()):
    ?>
    <section class="news-section section">
        <div class="container">
            <div class="section-header">
                <span class="section-label"><?php esc_html_e('Aktuelles', 'pusteblume'); ?></span>
                <h2><?php esc_html_e('Neuigkeiten aus dem Kindergarten', 'pusteblume'); ?></h2>
            </div>
            <div class="cards-grid">
                <?php while ($news->have_posts()): $news->the_post(); ?>
                    <article class="news-card card">
                        <?php if (has_post_thumbnail()): ?>
                            <div class="card-image">
                                <a href="<?php the_permalink(); ?>">
                                    <?php the_post_thumbnail('card'); ?>
                                </a>
                            </div>
                        <?php endif; ?>
                        <div class="card-body">
                            <time class="card-date" datetime="<?php echo esc_attr(get_the_date('c')); ?>">
                                <?php echo esc_html(get_the_date()); ?>
                            </time>
                            <h3 class="card-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
                            <p class="card-excerpt"><?php the_excerpt(); ?></p>
                            <a href="<?php the_permalink(); ?>" class="btn btn--sm btn--text"><?php esc_html_e('Weiterlesen →', 'pusteblume'); ?></a>
                        </div>
                    </article>
                <?php endwhile; wp_reset_postdata(); ?>
            </div>
            <div class="section-footer">
                <a href="<?php echo esc_url(get_permalink(get_option('page_for_posts'))); ?>" class="btn btn--outline">
                    <?php esc_html_e('Alle Neuigkeiten', 'pusteblume'); ?>
                </a>
            </div>
        </div>
    </section>
    <?php endif; ?>

    <!-- Contact Teaser -->
    <section class="contact-teaser section section--green">
        <div class="container">
            <div class="contact-teaser-inner">
                <div class="contact-teaser-text">
                    <h2><?php esc_html_e('Interesse an unserem Kindergarten?', 'pusteblume'); ?></h2>
                    <p><?php esc_html_e('Wir freuen uns auf Ihre Anfrage und beantworten gerne alle Fragen rund um unsere Einrichtung.', 'pusteblume'); ?></p>
                </div>
                <div class="contact-teaser-actions">
                    <?php if ($contact_page = get_page_by_path('kontakt')): ?>
                        <a href="<?php echo esc_url(get_permalink($contact_page)); ?>" class="btn btn--white btn--large">
                            <?php esc_html_e('Kontakt aufnehmen', 'pusteblume'); ?>
                        </a>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </section>

</main>

<?php get_footer(); ?>
