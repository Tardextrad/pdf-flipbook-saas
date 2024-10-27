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

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') {
            $(flipbook).turn('previous');
        } else if (e.key === 'ArrowRight') {
            $(flipbook).turn('next');
        }
    });
});
