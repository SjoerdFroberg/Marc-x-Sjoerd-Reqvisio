document.addEventListener('DOMContentLoaded', () => {
    const tableContainer = document.getElementById('table-container');

    const fullscreenContainer = document.getElementById('analysis-fullscreen');
    const toggleFullscreenButton = document.getElementById('toggle-fullscreen-btn');
    const exitFullscreenButton = document.getElementById('exit-fullscreen-btn');
    const tableFreezeContainer = document.getElementById('table-freeze');

    // Get references to elements for column visibility
    const columnVisibilityBtn = document.getElementById('column-visibility-btn');
    const columnVisibilityModalElement = document.getElementById('columnVisibilityModal');
    const columnVisibilityModal = new bootstrap.Modal(columnVisibilityModalElement);
    const selectAllBtn = document.getElementById('select-all-btn');
    const deselectAllBtn = document.getElementById('deselect-all-btn');
    const applyColumnVisibilityBtn = document.getElementById('apply-column-visibility-btn');
    const columnVisibilityForm = document.getElementById('column-visibility-form');

    // Open the modal when the button is clicked
    columnVisibilityBtn.addEventListener('click', () => {
        columnVisibilityModal.show();
    });

    // Select all checkboxes
    selectAllBtn.addEventListener('click', () => {
        const checkboxes = columnVisibilityForm.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => checkbox.checked = true);
    });

    // Deselect all checkboxes
    deselectAllBtn.addEventListener('click', () => {
        const checkboxes = columnVisibilityForm.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => checkbox.checked = false);
    });

    // Apply the selected columns and fetch updated table
    applyColumnVisibilityBtn.addEventListener('click', () => {
        const selectedQuestionIds = [];
        const checkboxes = columnVisibilityForm.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                selectedQuestionIds.push(checkbox.value);
            }
        });

        fetchTableData(selectedQuestionIds);

        columnVisibilityModal.hide();
    });

    // Fetch and update the table data
    const fetchTableData = (selectedQuestionIds = null) => {
        const params = new URLSearchParams();
        if (selectedQuestionIds && selectedQuestionIds.length > 0) {
            selectedQuestionIds.forEach(id => params.append('question_ids[]', id));
        } else {
            // Append 'question_ids[]' with an empty string to indicate no selections
            params.append('question_ids[]', '');
        }

        fetch(window.location.pathname + '?' + params.toString(), {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                tableContainer.innerHTML = data.table_html;
            })
            .catch(error => console.error('Error fetching table data', error));
    };


    
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

    // Select the first and second header rows
    const firstHeaderRow = document.querySelector('.styled-table thead tr:nth-child(1)');
    const secondHeaderRow = document.querySelector('.styled-table thead tr:nth-child(2)');

    if (firstHeaderRow && secondHeaderRow) {
        // Get the height of the first header row
        const firstHeaderHeight = firstHeaderRow.offsetHeight;

        // Apply the height dynamically as the 'top' value for the second row
        const secondHeaderCells = secondHeaderRow.querySelectorAll('th');
        secondHeaderCells.forEach(cell => {
            cell.style.top = `${firstHeaderHeight}px`;
        });
    }

    
});
