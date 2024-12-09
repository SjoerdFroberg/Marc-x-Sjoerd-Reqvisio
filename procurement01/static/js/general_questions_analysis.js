document.addEventListener('DOMContentLoaded', () => {
    const fullscreenContainer = document.getElementById('analysis-fullscreen');
    const toggleFullscreenButton = document.getElementById('toggle-fullscreen-btn');
    const exitFullscreenButton = document.getElementById('exit-fullscreen-btn');
    const tableFreezeContainer = document.getElementById('table-freeze');

    // Enter Full Screen Mode
    toggleFullscreenButton.addEventListener('click', () => {
        if (!document.fullscreenElement) {
            fullscreenContainer.requestFullscreen().then(() => {
                fullscreenContainer.classList.add('fullscreen');
                document.body.classList.add('fullscreen-active');
                tableFreezeContainer.style.maxHeight = 'calc(100vh - 60px)';

                toggleFullscreenButton.style.display = 'none'; // Hide toggle button
                exitFullscreenButton.classList.remove('d-none'); // Show exit button
            }).catch(err => {
                console.error(`Error enabling full-screen mode: ${err.message}`);
            });
        }
    });

    // Exit Full Screen Mode
    exitFullscreenButton.addEventListener('click', () => {
        if (document.fullscreenElement) {
            document.exitFullscreen().then(() => {
                fullscreenContainer.classList.remove('fullscreen');
                document.body.classList.remove('fullscreen-active');
                tableFreezeContainer.style.maxHeight = 'calc(100vh - 200px)';
                toggleFullscreenButton.style.display = ''; // Show toggle button
                exitFullscreenButton.classList.add('d-none'); // Hide exit button
            }).catch(err => {
                console.error(`Error exiting full-screen mode: ${err.message}`);
            });
        }
    });

    // Handle Full-Screen Changes (For Browser-Specific Events)
    document.addEventListener('fullscreenchange', () => {
        if (!document.fullscreenElement) {
            fullscreenContainer.classList.remove('fullscreen');
            document.body.classList.remove('fullscreen-active');
            toggleFullscreenButton.style.display = ''; // Show toggle button
            exitFullscreenButton.classList.add('d-none'); // Hide exit button
        }
    });
});
