// consolidated.js

document.addEventListener('DOMContentLoaded', function () {
    setupFullScreenToggle();
    setupRemoveButtons();
    setupAddRowButton();
    setupColumnNavigation();
    setupColumnManagement();
    setupPasteHandler();
    setupSearchHandler();
});

// Full Screen Toggle
toggleFullScreen = () => {
    const fullScreenContainer = document.getElementById('full-screen-container');
    const fullScreenButton = document.getElementById('full-screen-toggle');

    if (!document.fullscreenElement) {
        fullScreenContainer.requestFullscreen().then(() => {
            document.body.style.backgroundColor = 'white';
            fullScreenContainer.style.backgroundColor = 'white';
            fullScreenButton.textContent = 'Exit Full Screen';
        }).catch(err => {
            alert(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
        });
    } else {
        document.exitFullscreen().then(() => {
            document.body.style.backgroundColor = '';
            fullScreenContainer.style.backgroundColor = '';
            fullScreenButton.textContent = 'Full Screen';
        }).catch(err => {
            alert(`Error attempting to exit full-screen mode: ${err.message} (${err.name})`);
        });
    }
};

function setupFullScreenToggle() {
    const fullScreenButton = document.getElementById('full-screen-toggle');
    if (fullScreenButton) {
        fullScreenButton.addEventListener('click', toggleFullScreen);
    }
}

// Remove Button Functionality
function setupRemoveButtons() {
    document.querySelectorAll('.remove-sku-btn').forEach(button => {
        button.addEventListener('click', function () {
            const row = button.closest('tr');
            if (row) row.remove();
        });
    });

    document.querySelectorAll('.remove-column-x').forEach(button => {
        button.addEventListener('click', removeColumnHandler);
    });
}

function removeColumnHandler(event) {
    const index = Array.from(event.target.closest('th').parentNode.children).indexOf(event.target.closest('th'));
    removeColumn(index);
}

// Add Row Button
function setupAddRowButton() {
    const addRowButton = document.getElementById('add-row-btn');
    if (addRowButton) {
        addRowButton.addEventListener('click', addNewRow);
    }
}

// Handle Column Navigation
function setupColumnNavigation() {
    document.querySelectorAll('#sku-table tbody td[contenteditable="true"]').forEach(cell => {
        cell.addEventListener('keydown', handleCellNavigation);
    });
}

// Column Management (Add / Remove Columns)
function setupColumnManagement() {
    const addColumnButton = document.getElementById('add-column');
    if (addColumnButton) {
        addColumnButton.addEventListener('click', addNewColumn);
    }
}

// Paste Handler
function setupPasteHandler() {
    document.querySelectorAll('#sku-table tbody td[contenteditable="true"]').forEach(cell => {
        cell.addEventListener('paste', handlePaste);
    });
}

// SKU Search Functionality
function setupSearchHandler() {
    const searchInput = document.getElementById('sku-search-input');
    const searchResults = document.getElementById('sku-search-results');
    const tableWrapper = document.querySelector('.table-wrapper');

    if (searchInput) {
        searchInput.addEventListener('input', async function () {
            const query = this.value.trim();

            if (query.length > 0) {
                tableWrapper.classList.add('dimmed');
                searchResults.style.display = 'block';
                try {
                    const response = await fetch(`/procurement01/search_skus/?query=${encodeURIComponent(query)}`);
                    const skus = await response.json();
                    renderSearchResults(skus);
                } catch (error) {
                    console.error('Fetch error:', error);
                }
            } else {
                clearSearch();
            }
        });

        searchInput.addEventListener('keydown', function (event) {
            const results = searchResults.querySelectorAll('.search-result-item');
            if (event.key === 'ArrowDown' && results.length) {
                event.preventDefault();
                currentIndex = (currentIndex + 1) % results.length;
                updateActiveResult(results);
            } else if (event.key === 'ArrowUp' && results.length) {
                event.preventDefault();
                currentIndex = (currentIndex - 1 + results.length) % results.length;
                updateActiveResult(results);
            } else if (event.key === 'Enter' && currentIndex >= 0) {
                event.preventDefault();
                results[currentIndex].click();
            }
        });
    }
}

function clearSearch() {
    const searchInput = document.getElementById('sku-search-input');
    const searchResults = document.getElementById('sku-search-results');
    const tableWrapper = document.querySelector('.table-wrapper');

    if (searchInput) searchInput.value = '';
    if (searchResults) {
        searchResults.style.display = 'none';
        searchResults.innerHTML = '';
    }
    if (tableWrapper) tableWrapper.classList.remove('dimmed');
}

function updateActiveResult(results) {
    results.forEach((result, idx) => {
        result.classList.toggle('active', idx === currentIndex);
    });
}

function renderSearchResults(skus) {
    const searchResults = document.getElementById('sku-search-results');
    if (!searchResults) return;

    searchResults.innerHTML = '';
    currentIndex = -1;

    if (skus.length === 0) {
        searchResults.innerHTML = '<p>No SKUs found.</p>';
    } else {
        skus.forEach((sku, index) => {
            const resultItem = document.createElement('div');
            resultItem.className = 'search-result-item';
            resultItem.style.cursor = 'pointer';
            resultItem.innerHTML = `<i class="bi bi-plus-circle"></i><span class="sku-name">${sku.name}</span><span class="sku-code">(${sku.sku_code})</span>`;
            resultItem.addEventListener('click', () => selectSku(sku));
            searchResults.appendChild(resultItem);
        });
    }
}

function selectSku(sku) {
    addSkuToTable(sku.id, sku.name, sku.sku_code);
    clearSearch();
}

// Helper Functions (handleCellNavigation, handlePaste, addNewColumn, addNewRow, addSkuToTable)
function handleCellNavigation(event) {
    const cell = event.target;
    let currentRow, currentCellIndex, targetCell;

    currentRow = cell.parentNode;
    currentCellIndex = Array.from(currentRow.children).indexOf(cell);

    switch (event.key) {
        case "ArrowUp":
            targetCell = currentRow.previousElementSibling?.children[currentCellIndex];
            break;
        case "ArrowDown":
            targetCell = currentRow.nextElementSibling?.children[currentCellIndex];
            break;
        case "ArrowLeft":
            targetCell = cell.previousElementSibling;
            break;
        case "ArrowRight":
            targetCell = cell.nextElementSibling;
            break;
        case "Enter":
            event.preventDefault();
            targetCell = currentRow.nextElementSibling?.children[currentCellIndex];
            break;
    }

    if (targetCell && targetCell.getAttribute("contenteditable") === "true") {
        event.preventDefault();
        targetCell.focus();
    }
}

function handlePaste(event) {
    event.preventDefault();

    const pasteData = (event.clipboardData || window.clipboardData).getData('text');
    const rows = pasteData.trim().split('\n').map(row => row.split('\t'));

    const startRow = event.target.parentNode.rowIndex - 1;
    const startCol = event.target.cellIndex;

    rows.forEach((rowData, rowIndex) => {
        let tableRow = document.querySelector(`#sku-table tbody`).rows[startRow + rowIndex];
        if (!tableRow) tableRow = addNewRow();

        rowData.forEach((cellData, colIndex) => {
            if (startCol + colIndex >= document.querySelectorAll('#sku-table thead th').length) {
                addNewColumn();
            }
            const cell = tableRow.cells[startCol + colIndex];
            if (cell && cell.contentEditable === "true") cell.textContent = cellData.trim();
        });
    });
}

function addNewColumn() {
    const tableHead = document.querySelector('#sku-table thead tr');
    const newTh = document.createElement('th');
    newTh.innerHTML = `<input type="text" class="column-input" placeholder="Column Name">
                       <button type="button" class="remove-column-x">
                           <i class="bi bi-x-circle"></i>
                       </button>`;
    tableHead.appendChild(newTh);

    document.querySelectorAll('#sku-table tbody tr').forEach(row => {
        const newTd = document.createElement('td');
        newTd.contentEditable = "true";
        newTd.addEventListener('paste', handlePaste);
        newTd.addEventListener('keydown', handleCellNavigation);
        row.appendChild(newTd);
    });

    addRemoveColumnListeners();
}

function addRemoveColumnListeners() {
    document.querySelectorAll('.remove-column-x').forEach(button => {
        button.removeEventListener('click', removeColumnHandler);
        button.addEventListener('click', removeColumnHandler);
    });
}

function addNewRow() {
    const tableBody = document.querySelector('#sku-table tbody');
    const newRow = document.createElement('tr');
    document.querySelectorAll('#sku-table thead th').forEach((_, index) => {
        const newCell = document.createElement('td');
        if (index > 0) {
            newCell.contentEditable = "true";
            newCell.addEventListener('paste', handlePaste);
            newCell.addEventListener('keydown', handleCellNavigation);
        } else {
            newCell.innerHTML = `<button type="button" class="remove-sku-btn"><i class="bi bi-x-circle"></i></button>`;
        }
        newRow.appendChild(newCell);
    });
    tableBody.appendChild(newRow);
    newRow.querySelector('.remove-sku-btn').addEventListener('click', () => newRow.remove());
}

function addSkuToTable(skuId, skuName, skuCode) {
    const tableBody = document.querySelector('#sku-table tbody');
    const existingRow = Array.from(tableBody.querySelectorAll('input[name="skus[]"]')).find(input => input.value === String(skuId));
    if (existingRow) {
        alert("This SKU is already added.");
        return;
    }

    const row = document.createElement('tr');
    row.innerHTML = `<td><button type="button" class="remove-sku-btn"><i class="bi bi-x-circle"></i></button></td>
                     <td>${skuName}<input type="hidden" name="skus[]" value="${skuId}"></td>`;
    const headerCells = document.querySelectorAll('#sku-table thead th');
    for (let i = 2; i < headerCells.length; i++) {
        const newTd = document.createElement('td');
        newTd.contentEditable = "true";
        newTd.addEventListener('paste', handlePaste);
        newTd.addEventListener('keydown', handleCellNavigation);
        row.appendChild(newTd);
    }
    tableBody.appendChild(row);
    row.querySelector('.remove-sku-btn').addEventListener('click', () => row.remove());
}
