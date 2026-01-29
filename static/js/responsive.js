/* ============================================
   RESPONSIVE ENHANCEMENTS - JAVASCRIPT
   Mobile-First Responsive Functions
   ============================================ */

(function() {
    'use strict';

    // ============================================
    // Viewport/Breakpoint Detection
    // ============================================
    const ResponsiveManager = {
        breakpoints: {
            xs: 0,
            sm: 576,
            md: 768,
            lg: 992,
            xl: 1200,
            xxl: 1400
        },

        /**
         * Get current breakpoint
         */
        getCurrentBreakpoint() {
            const width = window.innerWidth;
            if (width >= this.breakpoints.xxl) return 'xxl';
            if (width >= this.breakpoints.xl) return 'xl';
            if (width >= this.breakpoints.lg) return 'lg';
            if (width >= this.breakpoints.md) return 'md';
            if (width >= this.breakpoints.sm) return 'sm';
            return 'xs';
        },

        /**
         * Check if device is mobile
         */
        isMobile() {
            return this.getCurrentBreakpoint() === 'xs';
        },

        /**
         * Check if device is tablet
         */
        isTablet() {
            const bp = this.getCurrentBreakpoint();
            return bp === 'sm' || bp === 'md';
        },

        /**
         * Check if device is desktop
         */
        isDesktop() {
            const bp = this.getCurrentBreakpoint();
            return bp === 'lg' || bp === 'xl' || bp === 'xxl';
        },

        /**
         * Check if breakpoint is at least a certain size
         */
        isAtLeast(breakpoint) {
            return window.innerWidth >= this.breakpoints[breakpoint];
        }
    };

    // ============================================
    // Touch Device Detection
    // ============================================
    const TouchHelper = {
        /**
         * Detect if device supports touch
         */
        isTouchDevice() {
            return (('ontouchstart' in window) ||
                    (navigator.maxTouchPoints > 0) ||
                    (navigator.msMaxTouchPoints > 0));
        },

        /**
         * Add touch class to body if touch device
         */
        init() {
            if (this.isTouchDevice()) {
                document.body.classList.add('touch-device');
            } else {
                document.body.classList.add('no-touch-device');
            }
        }
    };

    // ============================================
    // Responsive Table Enhancements
    // ============================================
    const ResponsiveTable = {
        /**
         * Initialize responsive table
         */
        init() {
            const tables = document.querySelectorAll('table');
            tables.forEach(table => {
                if (ResponsiveManager.isMobile()) {
                    this.makeTableStacked(table);
                }
            });

            // Re-apply on resize
            window.addEventListener('resize', this.handleResize.bind(this));
        },

        /**
         * Convert table to stacked layout on mobile
         */
        makeTableStacked(table) {
            if (!table.classList.contains('table-stacked')) {
                // Get headers
                const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());

                // Add data-label to cells
                table.querySelectorAll('tbody td').forEach((td, index) => {
                    const headerIndex = index % headers.length;
                    if (headerIndex < headers.length) {
                        td.setAttribute('data-label', headers[headerIndex]);
                    }
                });

                table.classList.add('table-stacked');
            }
        },

        /**
         * Handle window resize
         */
        handleResize() {
            const tables = document.querySelectorAll('table');
            tables.forEach(table => {
                if (ResponsiveManager.isMobile() && !table.classList.contains('table-stacked')) {
                    this.makeTableStacked(table);
                } else if (!ResponsiveManager.isMobile()) {
                    table.classList.remove('table-stacked');
                }
            });
        }
    };

    // ============================================
    // Responsive Navigation
    // ============================================
    const ResponsiveNav = {
        /**
         * Initialize responsive navigation
         */
        init() {
            const navbar = document.querySelector('.navbar');
            if (navbar) {
                this.setupMobileMenu();
                window.addEventListener('resize', this.handleResize.bind(this));
            }
        },

        /**
         * Setup mobile menu behaviors
         */
        setupMobileMenu() {
            const navToggler = document.querySelector('.navbar-toggler');
            const navCollapse = document.querySelector('.navbar-collapse');

            if (navToggler && navCollapse) {
                navToggler.addEventListener('click', () => {
                    navCollapse.classList.toggle('show');
                });

                // Close menu when clicking on a link
                navCollapse.querySelectorAll('.nav-link').forEach(link => {
                    link.addEventListener('click', () => {
                        if (ResponsiveManager.isMobile()) {
                            navCollapse.classList.remove('show');
                        }
                    });
                });
            }
        },

        /**
         * Handle resize
         */
        handleResize() {
            if (!ResponsiveManager.isMobile()) {
                const navCollapse = document.querySelector('.navbar-collapse');
                if (navCollapse) {
                    navCollapse.classList.remove('show');
                }
            }
        }
    };

    // ============================================
    // Responsive Modal
    // ============================================
    const ResponsiveModal = {
        /**
         * Initialize responsive modals
         */
        init() {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                this.setupModal(modal);
            });
        },

        /**
         * Setup individual modal
         */
        setupModal(modal) {
            const dialog = modal.querySelector('.modal-dialog');
            if (dialog) {
                if (ResponsiveManager.isMobile()) {
                    dialog.style.margin = '0.5rem';
                }
            }
        }
    };

    // ============================================
    // Responsive Form
    // ============================================
    const ResponsiveForm = {
        /**
         * Initialize responsive forms
         */
        init() {
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                this.setupForm(form);
            });
        },

        /**
         * Setup form inputs for mobile
         */
        setupForm(form) {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                // Ensure min-height of 44px for touch targets on mobile
                if (ResponsiveManager.isMobile()) {
                    input.style.minHeight = '44px';
                }
            });
        }
    };

    // ============================================
    // Responsive Images
    // ============================================
    const ResponsiveImage = {
        /**
         * Initialize responsive image optimization
         */
        init() {
            this.optimizeImages();
            window.addEventListener('resize', this.optimizeImages.bind(this));
        },

        /**
         * Optimize images based on device
         */
        optimizeImages() {
            const images = document.querySelectorAll('img:not([data-responsive-done])');
            images.forEach(img => {
                if (ResponsiveManager.isMobile()) {
                    img.style.maxWidth = '100%';
                    img.style.height = 'auto';
                    img.style.display = 'block';
                }
                img.setAttribute('data-responsive-done', 'true');
            });
        }
    };

    // ============================================
    // Responsive Layout Utilities
    // ============================================
    const ResponsiveLayout = {
        /**
         * Manage layout based on screen size
         */
        init() {
            this.setupLayoutClasses();
            window.addEventListener('resize', this.setupLayoutClasses.bind(this));
        },

        /**
         * Add/remove layout classes based on breakpoint
         */
        setupLayoutClasses() {
            const body = document.body;
            const breakpoint = ResponsiveManager.getCurrentBreakpoint();

            // Remove all breakpoint classes
            ['xs', 'sm', 'md', 'lg', 'xl', 'xxl'].forEach(bp => {
                body.classList.remove(`breakpoint-${bp}`);
            });

            // Add current breakpoint class
            body.classList.add(`breakpoint-${breakpoint}`);

            // Add layout type classes
            body.classList.remove('is-mobile', 'is-tablet', 'is-desktop');
            if (ResponsiveManager.isMobile()) {
                body.classList.add('is-mobile');
            } else if (ResponsiveManager.isTablet()) {
                body.classList.add('is-tablet');
            } else {
                body.classList.add('is-desktop');
            }
        }
    };

    // ============================================
    // Responsive Visibility Handler
    // ============================================
    const ResponsiveVisibility = {
        /**
         * Initialize visibility handling
         */
        init() {
            this.updateVisibility();
            window.addEventListener('resize', this.updateVisibility.bind(this));
        },

        /**
         * Update visibility of elements
         */
        updateVisibility() {
            const breakpoint = ResponsiveManager.getCurrentBreakpoint();

            // Hide/show mobile elements
            document.querySelectorAll('.show-mobile').forEach(el => {
                el.style.display = ResponsiveManager.isMobile() ? '' : 'none';
            });

            document.querySelectorAll('.hide-mobile').forEach(el => {
                el.style.display = ResponsiveManager.isMobile() ? 'none' : '';
            });

            // Hide/show tablet elements
            document.querySelectorAll('.show-tablet').forEach(el => {
                el.style.display = ResponsiveManager.isTablet() ? '' : 'none';
            });

            document.querySelectorAll('.hide-tablet').forEach(el => {
                el.style.display = ResponsiveManager.isTablet() ? 'none' : '';
            });

            // Hide/show desktop elements
            document.querySelectorAll('.show-desktop').forEach(el => {
                el.style.display = ResponsiveManager.isDesktop() ? '' : 'none';
            });

            document.querySelectorAll('.hide-desktop').forEach(el => {
                el.style.display = ResponsiveManager.isDesktop() ? 'none' : '';
            });
        }
    };

    // ============================================
    // Responsive Click Handler for Touch
    // ============================================
    const ResponsiveClick = {
        /**
         * Initialize click handlers for touch devices
         */
        init() {
            if (TouchHelper.isTouchDevice()) {
                this.setupTouchHandlers();
            }
        },

        /**
         * Setup touch event handlers
         */
        setupTouchHandlers() {
            document.addEventListener('touchstart', function(e) {
                if (e.target.matches('button, .btn, a.btn, .nav-link')) {
                    e.target.classList.add('touch-active');
                }
            });

            document.addEventListener('touchend', function(e) {
                document.querySelectorAll('.touch-active').forEach(el => {
                    el.classList.remove('touch-active');
                });
            });
        }
    };

    // ============================================
    // Responsive Performance Monitor
    // ============================================
    const ResponsivePerformance = {
        /**
         * Monitor and report responsive issues
         */
        init() {
            this.monitorViewportChanges();
        },

        /**
         * Monitor viewport changes
         */
        monitorViewportChanges() {
            let currentBreakpoint = ResponsiveManager.getCurrentBreakpoint();

            window.addEventListener('resize', () => {
                const newBreakpoint = ResponsiveManager.getCurrentBreakpoint();
                if (newBreakpoint !== currentBreakpoint) {
                    currentBreakpoint = newBreakpoint;
                    // Dispatch custom event when breakpoint changes
                    window.dispatchEvent(new CustomEvent('breakpointchange', {
                        detail: { breakpoint: newBreakpoint }
                    }));
                }
            });
        }
    };

    // ============================================
    // Initialize All Responsive Features
    // ============================================
    function initializeResponsive() {
        // Initialize in order of dependency
        TouchHelper.init();
        ResponsiveLayout.init();
        ResponsiveManager.getCurrentBreakpoint(); // Cache initial breakpoint
        ResponsiveNav.init();
        ResponsiveTable.init();
        ResponsiveForm.init();
        ResponsiveImage.init();
        ResponsiveVisibility.init();
        ResponsiveClick.init();
        ResponsivePerformance.init();

        // Expose to global scope for debugging
        window.ResponsiveManager = ResponsiveManager;
        window.TouchHelper = TouchHelper;
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeResponsive);
    } else {
        initializeResponsive();
    }

    // Re-initialize on dynamic content load
    const observer = new MutationObserver(() => {
        ResponsiveTable.init();
        ResponsiveForm.init();
        ResponsiveImage.init();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

})();
