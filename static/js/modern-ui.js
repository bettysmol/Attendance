/* Modern UI/UX JavaScript Enhancements */

document.addEventListener('DOMContentLoaded', function() {
    initializeModernUI();
    setupAnimations();
    setupInteractions();
    setupAccessibility();
});

// Initialize Modern UI
function initializeModernUI() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', createRipple);
    });

    // Animate elements on scroll
    observeElements();

    // Enhance form inputs
    enhanceFormInputs();

    // Setup tooltips
    setupTooltips();

    // Setup notifications
    setupNotifications();
}

// Create ripple effect on button click
function createRipple(e) {
    const button = this;
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');

    // Remove existing ripples
    button.querySelectorAll('.ripple').forEach(r => r.remove());
    
    button.appendChild(ripple);
}

// Observe elements for intersection animations
function observeElements() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card, .stat-card, .feature-card, .course-card').forEach(el => {
        observer.observe(el);
    });
}

// Enhance form inputs with floating labels
function enhanceFormInputs() {
    document.querySelectorAll('.form-control, .form-select').forEach(input => {
        // Add focus class on input
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });

        // Check if input has value on page load
        if (input.value) {
            input.parentElement.classList.add('focused');
        }

        // Real-time validation feedback
        input.addEventListener('input', function() {
            validateInput(this);
        });

        input.addEventListener('blur', function() {
            validateInput(this);
        });
    });
}

// Validate input fields
function validateInput(input) {
    const value = input.value.trim();
    const wrapper = input.closest('.form-group') || input.parentElement;

    // Remove existing feedback
    wrapper.querySelectorAll('.valid-feedback, .invalid-feedback').forEach(el => {
        if (!el.textContent) el.remove();
    });

    if (input.type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (value && !emailRegex.test(value)) {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        } else if (value) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid', 'is-invalid');
        }
    } else if (input.type === 'number') {
        if (value && isNaN(value)) {
            input.classList.add('is-invalid');
        } else if (value) {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
        } else {
            input.classList.remove('is-valid', 'is-invalid');
        }
    } else if (input.required) {
        if (value) {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
        } else {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
        }
    }
}

// Setup animations
function setupAnimations() {
    // Add fade-in animation to alerts
    document.querySelectorAll('.alert').forEach((alert, index) => {
        alert.style.animationDelay = (index * 0.1) + 's';
        alert.classList.add('animated');
    });

    // Stagger animation for table rows
    document.querySelectorAll('tbody tr').forEach((row, index) => {
        row.style.animationDelay = (index * 0.05) + 's';
        row.classList.add('animated');
    });

    // Animate stat cards
    document.querySelectorAll('.stat-card, .stat-box').forEach((card, index) => {
        card.style.animationDelay = (index * 0.15) + 's';
        card.classList.add('animated');
    });
}

// Setup interactive elements
function setupInteractions() {
    // Table row selection
    document.querySelectorAll('tbody tr').forEach(row => {
        row.addEventListener('click', function(e) {
            if (!e.target.closest('a, button, input, select')) {
                this.classList.toggle('table-active');
            }
        });
    });

    // Dropdown hover activation
    document.querySelectorAll('.dropdown').forEach(dropdown => {
        dropdown.addEventListener('mouseenter', function() {
            const menu = this.querySelector('.dropdown-menu');
            if (menu) {
                this.classList.add('show');
                menu.classList.add('show');
            }
        });

        dropdown.addEventListener('mouseleave', function() {
            const menu = this.querySelector('.dropdown-menu');
            if (menu) {
                this.classList.remove('show');
                menu.classList.remove('show');
            }
        });
    });

    // Collapse animations
    document.querySelectorAll('.collapse').forEach(collapse => {
        collapse.addEventListener('show.bs.collapse', function() {
            this.style.maxHeight = this.scrollHeight + 'px';
        });

        collapse.addEventListener('hide.bs.collapse', function() {
            this.style.maxHeight = '0px';
        });
    });
}

// Setup tooltips
function setupTooltips() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        new bootstrap.Tooltip(el);
    });
}

// Setup notifications
function setupNotifications() {
    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add animation to notification appearance
    document.querySelectorAll('.toast').forEach(toast => {
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    });
}

// Setup accessibility improvements
function setupAccessibility() {
    // Keyboard navigation for dropdowns
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Close all dropdowns
            document.querySelectorAll('.dropdown.show').forEach(dropdown => {
                dropdown.classList.remove('show');
                const menu = dropdown.querySelector('.dropdown-menu');
                if (menu) menu.classList.remove('show');
            });
        }
    });

    // Add skip to content link
    if (!document.querySelector('.skip-to-content')) {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-to-content btn btn-primary';
        skipLink.textContent = 'Skip to main content';
        document.body.insertBefore(skipLink, document.body.firstChild);
    }

    // Improve form label associations
    document.querySelectorAll('label').forEach(label => {
        if (!label.getAttribute('for')) {
            const input = label.querySelector('input, select, textarea');
            if (input && !input.id) {
                input.id = 'field-' + Math.random().toString(36).substr(2, 9);
            }
            if (input) {
                label.setAttribute('for', input.id);
            }
        }
    });
}

// Utility: Show loading state
function showLoadingState(element) {
    const originalContent = element.innerHTML;
    element.disabled = true;
    element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    return function hideLoadingState() {
        element.disabled = false;
        element.innerHTML = originalContent;
    };
}

// Utility: Confirm dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Utility: Format date
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Utility: Format time
function formatTime(time) {
    return new Date('2000-01-01T' + time).toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

// Export for use in other scripts
window.UI = {
    showLoadingState,
    confirmAction,
    formatDate,
    formatTime,
    createRipple,
    validateInput
};

// Add CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }

    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }

    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .animated {
        animation: slideUp 0.5s ease-out forwards;
    }

    tbody tr.table-active {
        background-color: var(--primary);
        color: white;
    }

    tbody tr.table-active a {
        color: white;
    }

    .skip-to-content {
        position: absolute;
        top: -40px;
        left: 0;
        background: var(--primary);
        color: white;
        padding: 8px;
        text-decoration: none;
        z-index: 100;
    }

    .skip-to-content:focus {
        top: 0;
    }

    .collapse {
        overflow: hidden;
        transition: max-height 0.3s ease-out;
        max-height: 0;
    }

    .collapse.show {
        max-height: 1000px;
    }

    @media (max-width: 768px) {
        .collapse {
            max-height: none !important;
        }
    }
`;
document.head.appendChild(style);
