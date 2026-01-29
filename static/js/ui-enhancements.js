// UI Enhancements - Animations, Tooltips, and Interactivity

document.addEventListener('DOMContentLoaded', function() {
    // ========== Tooltip Support ==========
    // Add tooltips functionality for elements with data-tooltip attribute
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.style.cursor = 'help';
        element.classList.add('tooltip-text');
    });

    // ========== Form Enhancements ==========
    // Add visual feedback on form submission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                // Store original content
                const originalContent = submitButton.innerHTML;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';
                
                // Reset after 3 seconds if form doesn't process
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalContent;
                }, 3000);
            }
        });
    });

    // ========== Table Row Interactivity ==========
    // Highlight table rows on hover for better UX
    const tableRows = document.querySelectorAll('table tbody tr');
    tableRows.forEach(row => {
        row.style.cursor = 'pointer';
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f0f0f0';
        });
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });

    // ========== Status Select Styling ==========
    // Color-code attendance status selects
    const statusSelects = document.querySelectorAll('.status-select');
    statusSelects.forEach(select => {
        // Update styling on change
        function updateStatusStyle() {
            const selectedOption = select.options[select.selectedIndex];
            const value = select.value;
            
            // Remove all badge classes
            select.classList.remove('badge-present', 'badge-late', 'badge-absent', 'badge-excused');
            
            // Add appropriate badge class
            if (value === 'present') {
                select.style.borderColor = '#28a745';
                select.style.color = '#28a745';
            } else if (value === 'late') {
                select.style.borderColor = '#ffc107';
                select.style.color = '#333';
            } else if (value === 'absent') {
                select.style.borderColor = '#dc3545';
                select.style.color = '#dc3545';
            } else if (value === 'excused') {
                select.style.borderColor = '#17a2b8';
                select.style.color = '#17a2b8';
            }
        }
        
        updateStatusStyle();
        select.addEventListener('change', updateStatusStyle);
    });

    // ========== Progress Bar Animation ==========
    // Animate progress bars on page load
    const progressBars = document.querySelectorAll('.progress-bar-inner > div');
    progressBars.forEach(bar => {
        const width = bar.style.width || '0%';
        bar.style.width = '0%';
        
        // Trigger animation
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-out';
            bar.style.width = width;
        }, 100);
    });

    // ========== Card Entry Animation ==========
    // Stagger card animations on page load
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.animation = `slideUp 0.5s ease-out ${index * 0.1}s forwards`;
    });

    // ========== Empty State Animations ==========
    const emptyStates = document.querySelectorAll('.empty-state');
    emptyStates.forEach(state => {
        state.style.animation = 'fadeIn 0.5s ease-out';
    });

    // ========== Button Ripple Effect ==========
    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            // Only add ripple on left click
            if (e.button !== 0) return;
            
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            // Remove any existing ripple
            const existingRipple = this.querySelector('.ripple');
            if (existingRipple) existingRipple.remove();
            
            this.appendChild(ripple);
        });
    });

    // ========== Alert Auto-Dismiss ==========
    // Auto-dismiss success alerts after 5 seconds
    document.querySelectorAll('.alert-success').forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // ========== Search Bar Focus Animation ==========
    const searchBars = document.querySelectorAll('input[type="search"], input[placeholder*="search"]');
    searchBars.forEach(bar => {
        bar.addEventListener('focus', function() {
            this.style.transform = 'scale(1.02)';
        });
        bar.addEventListener('blur', function() {
            this.style.transform = 'scale(1)';
        });
    });
});

// CSS for ripple effect (add to stylesheet)
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
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
`;
document.head.appendChild(rippleStyle);
