// Handle progress bars with data-width attribute
document.addEventListener('DOMContentLoaded', function() {
    const progressBars = document.querySelectorAll('[data-width]');
    progressBars.forEach(bar => {
        const width = bar.getAttribute('data-width');
        if (width !== null) {
            bar.style.width = width + '%';
        }
    });
});
