document.addEventListener('DOMContentLoaded', function() {
    const flipbook = document.getElementById('flipbook');
    let currentZoom = 1;

    // Initialize turn.js with error handling
    try {
        $(flipbook).turn({
            width: 800,
            height: 600,
            autoCenter: true,
            gradients: true,
            acceleration: true
        });

        // Track page changes
        $(flipbook).bind('turned', function(event, page) {
            fetch(`/track_page/${window.location.pathname.split('/').pop()}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    page_number: page
                })
            });
        });

        // Navigation controls
        document.getElementById('prev').addEventListener('click', function() {
            $(flipbook).turn('previous');
        });

        document.getElementById('next').addEventListener('click', function() {
            $(flipbook).turn('next');
        });

        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft') {
                $(flipbook).turn('previous');
            } else if (e.key === 'ArrowRight') {
                $(flipbook).turn('next');
            }
        });
    } catch (error) {
        console.error('Error initializing turn.js:', error);
        // Fallback to basic viewer if turn.js fails
        document.querySelector('.controls').style.display = 'none';
        showToast('Error loading flipbook viewer. Please try refreshing the page.', 'danger');
    }

    // Zoom controls
    document.getElementById('zoomIn').addEventListener('click', function() {
        if (currentZoom < 2) {
            currentZoom += 0.2;
            flipbook.style.transform = `scale(${currentZoom})`;
        }
    });

    document.getElementById('zoomOut').addEventListener('click', function() {
        if (currentZoom > 0.5) {
            currentZoom -= 0.2;
            flipbook.style.transform = `scale(${currentZoom})`;
        }
    });

    // Sharing functionality with improved clipboard API
    document.getElementById('copyShareLink')?.addEventListener('click', async function() {
        const shareUrl = this.getAttribute('data-share-url');
        try {
            await navigator.clipboard.writeText(shareUrl);
            showToast('Share link copied to clipboard!', 'success');
        } catch (err) {
            showToast('Failed to copy link. Please try again.', 'danger');
        }
    });

    document.getElementById('copyEmbedCode')?.addEventListener('click', async function() {
        const embedCode = document.getElementById('embedCode');
        try {
            await navigator.clipboard.writeText(embedCode.value);
            showToast('Embed code copied to clipboard!', 'success');
        } catch (err) {
            showToast('Failed to copy embed code. Please try again.', 'danger');
        }
    });

    // Enhanced toast notification system
    function showToast(message, type = 'success') {
        const toastContainer = document.querySelector('.toast-container');
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 3000
        });
        toast.show();
        
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }
});
