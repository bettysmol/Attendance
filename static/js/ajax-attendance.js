// Instant mark present via AJAX
document.addEventListener('DOMContentLoaded', function() {
    const markPresentForms = document.querySelectorAll('.mark-present-form');
    
    markPresentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const studentId = this.getAttribute('data-student-id');
            const sessionId = this.getAttribute('data-session-id');
            const csrfToken = this.querySelector('[name="csrfmiddlewaretoken"]').value;
            
            const formData = new FormData();
            formData.append('status_' + studentId, 'present');
            formData.append('remarks_' + studentId, '');
            formData.append('csrfmiddlewaretoken', csrfToken);
            
            // Show loading state
            const btn = this.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Saving...';
            
            fetch(form.getAttribute('action'), {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.ok) {
                    // Show success feedback
                    btn.classList.add('btn-success');
                    btn.classList.remove('btn-primary');
                    btn.innerHTML = '<i class="bi bi-check-circle"></i> Marked Present';
                    
                    // Optional: disable further clicks
                    btn.disabled = true;
                    
                    // Flash green highlight
                    const row = form.closest('tr');
                    if (row) {
                        row.style.backgroundColor = '#d4edda';
                        setTimeout(() => {
                            row.style.backgroundColor = '';
                        }, 1500);
                    }
                } else {
                    throw new Error('Failed to mark attendance');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-exclamation-circle"></i> Error';
                setTimeout(() => {
                    btn.innerHTML = originalText;
                }, 2000);
            });
        });
    });
});
