document.addEventListener('DOMContentLoaded', function() {
    const flipbook = document.getElementById('flipbook');
    let currentZoom = 1;

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

    // Sharing functionality
    document.getElementById('copyShareLink').addEventListener('click', function() {
        const shareUrl = this.getAttribute('data-share-url');
        navigator.clipboard.writeText(shareUrl).then(() => {
            showToast('Share link copied to clipboard!');
        });
    });

    document.getElementById('copyEmbedCode').addEventListener('click', function() {
        const embedCode = document.getElementById('embedCode');
        embedCode.select();
        navigator.clipboard.writeText(embedCode.value).then(() => {
            showToast('Embed code copied to clipboard!');
        });
    });

    // Toast notification
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0 position-fixed bottom-0 end-0 m-3';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        toast.addEventListener('hidden.bs.toast', () => toast.remove());
    }

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') {
            $(flipbook).turn('previous');
        } else if (e.key === 'ArrowRight') {
            $(flipbook).turn('next');
        }
    });
});
