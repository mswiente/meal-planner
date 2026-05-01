    <footer id="colophon" class="site-footer">
        <div class="footer-widgets">
            <div class="container">
                <div class="footer-widgets-grid">
                    <div class="footer-widget-area footer-about">
                        <div class="footer-logo">
                            <span class="logo-icon">🌼</span>
                            <strong><?php bloginfo('name'); ?></strong>
                        </div>
                        <p><?php esc_html_e('Ein Ort des Lernens, Spielens und Wachsens für Ihre Kinder.', 'pusteblume'); ?></p>
                    </div>

                    <?php if (is_active_sidebar('footer-1')): ?>
                        <div class="footer-widget-area">
                            <?php dynamic_sidebar('footer-1'); ?>
                        </div>
                    <?php endif; ?>

                    <?php if (is_active_sidebar('footer-2')): ?>
                        <div class="footer-widget-area">
                            <?php dynamic_sidebar('footer-2'); ?>
                        </div>
                    <?php endif; ?>

                    <?php if (is_active_sidebar('footer-3')): ?>
                        <div class="footer-widget-area">
                            <?php dynamic_sidebar('footer-3'); ?>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>

        <div class="footer-bottom">
            <div class="container">
                <div class="footer-bottom-inner">
                    <p class="copyright">
                        &copy; <?php echo esc_html(date('Y')); ?>
                        <a href="<?php echo esc_url(home_url('/')); ?>"><?php bloginfo('name'); ?></a>
                    </p>
                    <nav class="footer-navigation" aria-label="<?php esc_attr_e('Footer-Navigation', 'pusteblume'); ?>">
                        <?php
                        wp_nav_menu([
                            'theme_location' => 'footer',
                            'menu_id'        => 'footer-menu',
                            'container'      => false,
                            'depth'          => 1,
                            'fallback_cb'    => '__return_false',
                        ]);
                        ?>
                    </nav>
                </div>
            </div>
        </div>
    </footer>
</div>

<?php wp_footer(); ?>
</body>
</html>
