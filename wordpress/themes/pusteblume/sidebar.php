<?php
defined('ABSPATH') || exit;

if (!is_active_sidebar('sidebar-1')) {
    return;
}
?>

<div class="sidebar-inner">
    <?php dynamic_sidebar('sidebar-1'); ?>
</div>
