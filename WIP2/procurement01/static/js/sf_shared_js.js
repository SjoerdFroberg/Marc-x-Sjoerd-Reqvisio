document.addEventListener('DOMContentLoaded', () => {
    let currentIndex = -1;

    const searchInput = document.getElementById('sku-search-input');
    const searchResults = document.getElementById('sku-search-results');
    const tableWrapper = document.querySelector('.table-wrapper');
    const skuTable = document.getElementById('sku-table');

    document.getElementById('continue-to-step-3').addEventListener('click', submitForm);

    // Handle search input
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

    // Render search results with arrow navigation support
    function renderSearchResults(skus) {
        searchResults.innerHTML = '';
        currentIndex = -1;

        if (skus.length === 0) {
            searchResults.innerHTML = '<p>No SKUs found.</p>';
        } else {
            skus.forEach((sku, index) => {
                const resultItem = document.createElement('div');
                resultItem.className = 'search-result-item';
                resultItem.style.cursor = 'pointer';
                resultItem.innerHTML = `<i class="bi bi-plus-circle"></i>
                                        <span class="sku-name">${sku.name}</span> 
                                        <span class="sku-code">(${sku.sku_code})</span>`;
                resultItem.addEventListener('click', () => selectSku(sku));
                searchResults.appendChild(resultItem);
            });
        }
    }

    // Handle arrow navigation and Enter key for selecting SKUs
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

    function updateActiveResult(results) {
        results.forEach((result, idx) => {
            result.classList.toggle('active', idx === currentIndex);
        });
    }

    // Select SKU and add it to the table
    function selectSku(sku) {
        addSkuToTable(sku.id, sku.name, sku.sku_code);
        clearSearch();
    }

    function clearSearch() {
        searchInput.value = '';
        searchResults.style.display = 'none';
        searchResults.innerHTML = '';
        tableWrapper.classList.remove('dimmed');
    }


    // Add SKU to the table with duplication check
    function addSkuToTable(skuId, skuName, skuCode) {
        const tableBody = skuTable.querySelector('tbody');
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
            row.appendChild(newTd);
        }
        tableBody.appendChild(row);

        row.querySelector('.remove-sku-btn').addEventListener('click', () => row.remove());
        applyListenersToRow(row);
    }

    // Apply paste and navigation listeners to each cell in the row
    function applyListenersToRow(row) {
        row.querySelectorAll('td[contenteditable="true"]').forEach(cell => {
            cell.addEventListener('paste', handlePaste);
            cell.addEventListener('keydown', handleCellNavigation);
        });
    }

    // Function to handle pasting data
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

     // Add new column
     document.getElementById('add-column').addEventListener('click', addNewColumn);

     function addNewColumn() {
         const tableHead = document.querySelector('#sku-table thead tr');
         const newTh = document.createElement('th');
         newTh.innerHTML = `<input type="text" class="column-input" placeholder="Column Name">
                            <button type="button" class="remove-column-x">
                                <i class="bi bi-x-circle"></i>
                            </button>`;
         tableHead.appendChild(newTh);
 
         // Add new cells to each row in the table body
         document.querySelectorAll('#sku-table tbody tr').forEach(row => {
             const newTd = document.createElement('td');
             newTd.contentEditable = "true";
             newTd.addEventListener('paste', handlePaste);
             row.appendChild(newTd);
         });
 
         // Rebind the remove column event after adding the new column
         addRemoveColumnListeners();
         // Reapply cell navigation after adding new columns
     applyCellNavigation();
 
 
     }
 
     // Function to remove a column
     function removeColumn(index) {
         const table = document.getElementById('sku-table');
         const headerCells = table.querySelectorAll('thead th');
         const rows = table.querySelectorAll('tbody tr');
 
         // Check if the column is removable (i.e., it's not the first column or invalid index)
         if (index < 1 || index >= headerCells.length) return;
 
         // Remove the column header
         headerCells[index].remove();
 
         // Remove the corresponding cells from each row in the table body
         rows.forEach(row => {
             const cell = row.children[index];
             if (cell) {
                 cell.remove();
             }
         });
     }
 
     // Add event listeners to column remove buttons
     function addRemoveColumnListeners() {
         const removeColumnButtons = document.querySelectorAll('.remove-column-x');
         removeColumnButtons.forEach((button, index) => {
             button.removeEventListener('click', removeColumnHandler); // Remove previous listeners
             button.addEventListener('click', removeColumnHandler);
         });
     }
 
     // Remove column handler to be used by both initial and dynamic buttons
     function removeColumnHandler(event) {
         const index = Array.from(event.target.closest('th').parentNode.children).indexOf(event.target.closest('th'));
         removeColumn(index);
     }
 
     
 
     // Handle column name placeholder behavior
     document.querySelectorAll('.column-input').forEach(input => handlePlaceholder(input));
 
     // Function to handle column name placeholder behavior
     function handlePlaceholder(input) {
         input.addEventListener('focus', function () {
             this.setAttribute('data-placeholder', this.placeholder); // Store the current placeholder
             this.placeholder = ''; // Clear the placeholder on focus
         });
 
         input.addEventListener('blur', function () {
             if (this.value === '') {
                 this.placeholder = this.getAttribute('data-placeholder'); // Restore placeholder if empty
             }
         });
     }
 
     // Initialize column header placeholders
     document.querySelectorAll('#sku-table thead .column-input').forEach(input => handlePlaceholder(input));
 
     // Apply cell navigation listeners to headers and body cells
     function applyCellNavigation() {
         // Apply to header cells
         document.querySelectorAll('#sku-table thead .column-input').forEach(input => {
             input.addEventListener('keydown', handleCellNavigation);
         });
 
         // Apply to body cells
         document.querySelectorAll('#sku-table tbody td[contenteditable="true"]').forEach(cell => {
             cell.addEventListener('keydown', handleCellNavigation);
         });
     }
 
     // Function to handle cell navigation
     function handleCellNavigation(event) {
         const cell = event.target;
         let currentRow, currentCellIndex, targetCell;
 
         // Handle navigation for header cells
         if (cell.tagName === 'INPUT') {
             currentCellIndex = Array.from(cell.parentNode.parentNode.children).indexOf(cell.parentNode);
 
             switch (event.key) {
                 case "ArrowDown":
                 case "Enter": // Handle Enter to go to the first row cell below
                     event.preventDefault();
                     const firstBodyRow = skuTable.querySelector('tbody tr');
                     if (firstBodyRow) {
                         targetCell = firstBodyRow.children[currentCellIndex];
                     }
                     break;
             }
         } else {
             // Handle navigation for body cells
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
         }
 
         if (targetCell && targetCell.getAttribute("contenteditable") === "true") {
             event.preventDefault();
             targetCell.focus();
         }
     }
 
 
 
     // Add new row
     function addNewRow() {
         const tableBody = document.querySelector('#sku-table tbody');
         const newRow = document.createElement('tr');
         document.querySelectorAll('#sku-table thead th').forEach((_, index) => {
             const newCell = document.createElement('td');
             if (index > 0) {
                 newCell.contentEditable = "true";
                 newCell.addEventListener('paste', handlePaste);
             } else {
                 newCell.innerHTML = `<button type="button" class="remove-sku-btn"><i class="bi bi-x-circle"></i></button>`;
             }
             newRow.appendChild(newCell);
         });
         tableBody.appendChild(newRow);
         newRow.querySelector('.remove-sku-btn').addEventListener('click', () => newRow.remove());
         applyListenersToRow(newRow);
         return newRow;
     }


     // Full-screen toggle functionality
    document.getElementById('full-screen-toggle').addEventListener('click', function () {
        const fullScreenContainer = document.getElementById('full-screen-container');

        if (!document.fullscreenElement) {
            fullScreenContainer.requestFullscreen().then(() => {
                document.body.style.backgroundColor = "white"; // Ensure body background color is set to white
                fullScreenContainer.style.backgroundColor = "white"; // Ensure full-screen container is white
            }).catch(err => {
                alert(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
            });
            this.textContent = 'Exit Full Screen';
        } else {
            document.exitFullscreen().then(() => {
                document.body.style.backgroundColor = ""; // Reset background color
                fullScreenContainer.style.backgroundColor = ""; // Reset container background color
            }).catch(err => {
                alert(`Error attempting to exit full-screen mode: ${err.message} (${err.name})`);
            });
            this.textContent = 'Full Screen';
        }
    });

    // Event listener for fullscreenchange to handle Esc key exit
    document.addEventListener('fullscreenchange', function () {
        const fullScreenButton = document.getElementById('full-screen-toggle');

        if (!document.fullscreenElement) {
            fullScreenButton.textContent = 'Full Screen';
            document.body.style.backgroundColor = ""; // Reset background color
            const fullScreenContainer = document.getElementById('full-screen-container');
            fullScreenContainer.style.backgroundColor = ""; // Reset container background color
        }
    });

    
    function submitForm(event) {
    // Prevent the default form submission to handle it manually
    event.preventDefault();
    
    const form = document.getElementById('rfp-skus-form');
    const tableBody = document.querySelector('#sku-table tbody');
    const skuData = [];

    // Get the headers in the exact order they appear in the table
    const allColumnHeaders = Array.from(document.querySelectorAll('#sku-table thead th'))
        .map(th => th.querySelector('.column-input') ? th.querySelector('.column-input').value.toString() : th.textContent.trim());

    tableBody.querySelectorAll('tr').forEach(row => {
        const skuId = row.querySelector('input[name="skus[]"]').value;
        const rowValues = Array.from(row.querySelectorAll('td'))
            .slice(2) // Skip the first two columns (Remove SKU and SKU Name)
            .map(td => td.innerText.trim());

        // Use an array to store key-value pairs for consistent ordering
        const dataArray = [];
        allColumnHeaders.slice(2).forEach((header, index) => { // Skip first two columns (Remove SKU and SKU Name)
            dataArray.push([header, rowValues[index]]);
        });

        skuData.push({
            sku_id: skuId,
            data: dataArray
        });
    });

    // Add SKU data to the hidden input field
    document.getElementById('extra_columns_data').value = JSON.stringify(skuData);

    // Submit the form
    form.submit();
    }



    
    // Apply paste listeners to rows and initialize cell navigation
    document.querySelectorAll('#sku-table tbody tr').forEach(row => applyListenersToRow(row));
    applyCellNavigation();

    // Bind the event listeners to the initial remove column buttons
    addRemoveColumnListeners();


    document.querySelectorAll('.remove-sku-btn').forEach(button => {
        button.addEventListener('click', function () {
            const row = button.closest('tr');
            if (row) {
                row.remove();
            }
        });
    });
 



});
