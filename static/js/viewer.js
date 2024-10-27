document.addEventListener('DOMContentLoaded', function() {
    const flipbook = document.getElementById('flipbook');

    // Add loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-spinner';
    flipbook.parentElement.appendChild(loadingIndicator);

    // Wait for images to load before initialization
    const images = flipbook.getElementsByTagName('img');
    let loadedImages = 0;
    
    function initializeTurnJs() {
        try {
            $(flipbook).turn({
                width: 800,
                height: 600,
                autoCenter: true,
                gradients: true,
                acceleration: true,
                when: {
                    turning: function(e, page) {
                        // Update URL with current page
                        const url = new URL(window.location);
                        url.searchParams.set('page', page);
                        window.history.replaceState({}, '', url);

                        // Track page changes
                        fetch(`/track_page/${window.location.pathname.split('/').pop()}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                page_number: page
                            })
                        });
                    }
                }
            });
            loadingIndicator.style.display = 'none';
        } catch (error) {
            console.error('Error initializing turn.js:', error);
            loadingIndicator.innerHTML = 'Error loading viewer. Please refresh.';
            document.querySelector('.controls').style.display = 'none';
            showToast('Error loading flipbook viewer. Please try refreshing the page.', 'danger');
        }
    }

    // Only initialize after images are loaded
    Array.from(images).forEach(img => {
        if (img.complete) {
            loadedImages++;
            if (loadedImages === images.length) {
                initializeTurnJs();
            }
        } else {
            img.onload = () => {
                loadedImages++;
                if (loadedImages === images.length) {
                    initializeTurnJs();
                }
            };
            img.onerror = () => {
                loadedImages++;
                img.style.display = 'none';
                if (loadedImages === images.length) {
                    initializeTurnJs();
                }
            };
        }
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
