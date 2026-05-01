<?php
defined('ABSPATH') || exit;

function pusteblume_setup(): void {
    load_theme_textdomain('pusteblume', get_template_directory() . '/languages');

    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', ['search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script']);
    add_theme_support('customize-selective-refresh-widgets');
    add_theme_support('wp-block-styles');
    add_theme_support('responsive-embeds');

    add_image_size('hero', 1920, 800, true);
    add_image_size('card', 600, 400, true);
    add_image_size('team', 400, 400, true);

    register_nav_menus([
        'primary' => __('Hauptnavigation', 'pusteblume'),
        'footer'  => __('Footer-Navigation', 'pusteblume'),
    ]);
}
add_action('after_setup_theme', 'pusteblume_setup');

function pusteblume_enqueue_assets(): void {
    $ver = wp_get_theme()->get('Version');

    wp_enqueue_style('pusteblume-fonts', 'https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Lato:wght@400;700&display=swap', [], null);
    wp_enqueue_style('pusteblume-main', get_template_directory_uri() . '/assets/css/main.css', ['pusteblume-fonts'], $ver);

    wp_enqueue_script('pusteblume-main', get_template_directory_uri() . '/assets/js/main.js', [], $ver, true);
}
add_action('wp_enqueue_scripts', 'pusteblume_enqueue_assets');

function pusteblume_widgets_init(): void {
    $defaults = [
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ];

    register_sidebar(array_merge($defaults, [
        'name' => __('Sidebar', 'pusteblume'),
        'id'   => 'sidebar-1',
    ]));

    register_sidebar(array_merge($defaults, [
        'name' => __('Footer Spalte 1', 'pusteblume'),
        'id'   => 'footer-1',
    ]));

    register_sidebar(array_merge($defaults, [
        'name' => __('Footer Spalte 2', 'pusteblume'),
        'id'   => 'footer-2',
    ]));

    register_sidebar(array_merge($defaults, [
        'name' => __('Footer Spalte 3', 'pusteblume'),
        'id'   => 'footer-3',
    ]));
}
add_action('widgets_init', 'pusteblume_widgets_init');

function pusteblume_custom_post_types(): void {
    register_post_type('team', [
        'labels' => [
            'name'          => __('Team', 'pusteblume'),
            'singular_name' => __('Teammitglied', 'pusteblume'),
            'add_new_item'  => __('Teammitglied hinzufügen', 'pusteblume'),
            'edit_item'     => __('Teammitglied bearbeiten', 'pusteblume'),
        ],
        'public'       => true,
        'show_in_rest' => true,
        'supports'     => ['title', 'editor', 'thumbnail', 'excerpt'],
        'menu_icon'    => 'dashicons-groups',
        'has_archive'  => true,
        'rewrite'      => ['slug' => 'team'],
    ]);

    register_post_type('gruppe', [
        'labels' => [
            'name'          => __('Gruppen', 'pusteblume'),
            'singular_name' => __('Gruppe', 'pusteblume'),
            'add_new_item'  => __('Gruppe hinzufügen', 'pusteblume'),
            'edit_item'     => __('Gruppe bearbeiten', 'pusteblume'),
        ],
        'public'       => true,
        'show_in_rest' => true,
        'supports'     => ['title', 'editor', 'thumbnail', 'excerpt'],
        'menu_icon'    => 'dashicons-smiley',
        'has_archive'  => true,
        'rewrite'      => ['slug' => 'gruppen'],
    ]);
}
add_action('init', 'pusteblume_custom_post_types');

function pusteblume_excerpt_length(): int {
    return 20;
}
add_filter('excerpt_length', 'pusteblume_excerpt_length');

function pusteblume_excerpt_more(): string {
    return ' …';
}
add_filter('excerpt_more', 'pusteblume_excerpt_more');
