<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="profile" href="https://gmpg.org/xfn/11">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<div id="page" class="site">
    <a class="skip-link screen-reader-text" href="#primary"><?php esc_html_e('Zum Inhalt springen', 'pusteblume'); ?></a>

    <header id="masthead" class="site-header">
        <div class="header-top">
            <div class="container">
                <div class="header-contact">
                    <?php if ($phone = get_theme_mod('contact_phone')): ?>
                        <span class="header-phone">
                            <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1-9.4 0-17-7.6-17-17 0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/></svg>
                            <a href="tel:<?php echo esc_attr(preg_replace('/\s+/', '', $phone)); ?>"><?php echo esc_html($phone); ?></a>
                        </span>
                    <?php endif; ?>
                    <?php if ($email = get_theme_mod('contact_email')): ?>
                        <span class="header-email">
                            <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
                            <a href="mailto:<?php echo esc_attr($email); ?>"><?php echo esc_html($email); ?></a>
                        </span>
                    <?php endif; ?>
                </div>
            </div>
        </div>

        <div class="header-main">
            <div class="container">
                <div class="site-branding">
                    <?php if (has_custom_logo()): ?>
                        <div class="site-logo"><?php the_custom_logo(); ?></div>
                    <?php else: ?>
                        <div class="site-logo-text">
                            <a href="<?php echo esc_url(home_url('/')); ?>" rel="home">
                                <span class="logo-icon">🌼</span>
                                <span class="logo-text">
                                    <span class="logo-name"><?php bloginfo('name'); ?></span>
                                    <span class="logo-tagline"><?php bloginfo('description'); ?></span>
                                </span>
                            </a>
                        </div>
                    <?php endif; ?>
                </div>

                <button class="menu-toggle" aria-controls="primary-menu" aria-expanded="false">
                    <span class="menu-toggle-bar"></span>
                    <span class="menu-toggle-bar"></span>
                    <span class="menu-toggle-bar"></span>
                    <span class="screen-reader-text"><?php esc_html_e('Menü', 'pusteblume'); ?></span>
                </button>

                <nav id="site-navigation" class="main-navigation" aria-label="<?php esc_attr_e('Hauptnavigation', 'pusteblume'); ?>">
                    <?php
                    wp_nav_menu([
                        'theme_location' => 'primary',
                        'menu_id'        => 'primary-menu',
                        'container'      => false,
                        'fallback_cb'    => '__return_false',
                    ]);
                    ?>
                </nav>
            </div>
        </div>
    </header>
