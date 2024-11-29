// static/js/shared_sku.js





document.addEventListener('DOMContentLoaded', () => {
    let currentIndex = -1;

    // SKU Search Elements
    const searchInput = document.getElementById('sku-search-input');
    const searchResults = document.getElementById('sku-search-results');
    const tableWrapper = document.querySelector('.table-wrapper');
    const skuTable = document.getElementById('sku-table');

    // Full Screen Elements
    const fullScreenContainer = document.getElementById('full-screen-container');
    const fullScreenButton = document.getElementById('full-screen-toggle');

    // Control Buttons
    const addExtraColumnButton = document.getElementById('add-extra-column');
    const addSkuQuestionButton = document.getElementById('add-sku-question-btn');

    const continueToStep3Button = document.getElementById('continue-to-step-3-btn');
    const continueToStep5Button = document.getElementById('continue-to-step-5-btn');
    const backToStep1Button = document.getElementById('back-to-step-1-btn');
    const backToStep3Button = document.getElementById('back-to-step-3-btn');
    const backToStep4Button = document.getElementById('back-to-step-4-btn');
    const finalizeRFPButton = document.getElementById('finalize-rfp-btn')




    // Hidden Inputs
    const extraColumnsDataInput = document.getElementById('extra_columns_data');
    const skuSpecificDataInput = document.getElementById('sku_specific_data');
    const step = document.getElementById('step_number');

    // Determine if SKU-specific questions are present
    const hasSkuSpecificQuestions = !!addSkuQuestionButton;

    // Initialize event listeners
    initEventListeners();

    function initEventListeners() {

        applyCellNavigation();
        // SKU Search Input
        if (searchInput) {
            searchInput.addEventListener('input', handleSkuSearchInput);
            searchInput.addEventListener('keydown', handleSkuSearchNavigation);
        }

        // Full Screen Toggle
        if (fullScreenButton) {
            fullScreenButton.addEventListener('click', toggleFullScreen);
            document.addEventListener('fullscreenchange', handleFullScreenChange);
        }


        if (addExtraColumnButton) {
            addExtraColumnButton.addEventListener('click', () => {
                addNewExtraDataColumn();
            });
        }

        // Add SKU-specific Question
        if (addSkuQuestionButton) {
            addSkuQuestionButton.addEventListener('click', addSkuSpecificQuestion);
        }

        // Continue to Step 3
        if (continueToStep3Button) {
            continueToStep3Button.addEventListener('click', function(event){
                // Update the navigation destination to Step 1
                document.getElementById('navigation_destination').value = 'step3';
                // Submit the form
                submitForm(event);

            });
        }

        // Continue to Step 5
        if (continueToStep5Button) {
            continueToStep5Button.addEventListener('click', function(event){
                // Update the navigation destination to Step 5
                document.getElementById('navigation_destination').value = 'step5';
                // Submit the form
                submitFormStep4(event);

            });
        }

        // Back to step 1
        if(backToStep1Button){
            backToStep1Button.addEventListener('click', function(event){
                // Update the navigation destination to Step 1
                document.getElementById('navigation_destination').value = 'step1';
                // Submit the form
                submitForm(event);

            });

        }

        // Back to step 3
        if(backToStep3Button){
            backToStep3Button.addEventListener('click', function(event){
                // Update the navigation destination to Step 3
                document.getElementById('navigation_destination').value = 'step3';
                // Submit the form
                submitFormStep4(event);

            });

        }

        // Back to step 4
        if(backToStep4Button){
            backToStep4Button.addEventListener('click', function(event){
                // Update the navigation destination to Step 4
                document.getElementById('navigation_destination').value = 'step4';
                // Submit the form
                finalizeRFP(event);

            });

        }

        // finalize rfp

        if(finalizeRFPButton){
            finalizeRFPButton.addEventListener('click', function(event){
                document.getElementById('navigation_destination').value = 'invite_suppliers';
                // Submit the form
                finalizeRFP(event);
            })
        }

        
        
        

        

        // Initialize Remove SKU Buttons
        document.querySelectorAll('.remove-sku-btn').forEach(button => {
            button.addEventListener('click', removeSkuRow);
        });

        // Initialize Remove Column Buttons
        addRemoveColumnListeners();

        // Initialize existing SKU rows
        if (skuTable) {
            skuTable.querySelectorAll('tbody tr').forEach(row => {
                applyListenersToRow(row);
            });
        }
 
    }

    // SKU Search Functions
    async function handleSkuSearchInput() {
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
    }
    

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

    function handleSkuSearchNavigation(event) {
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
    }

    function updateActiveResult(results) {
        results.forEach((result, idx) => {
            result.classList.toggle('active', idx === currentIndex);
        });
    }

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

    function addSkuToTable(skuId, skuName, skuCode) {
        const tableBody = skuTable.querySelector('tbody');
        const existingRow = Array.from(tableBody.querySelectorAll('input[name="skus[]"]')).find(input => input.value === String(skuId));
        if (existingRow) {
            alert("This SKU is already added.");
            return;
        }

        const row = document.createElement('tr');
        row.setAttribute('data-sku-id', skuId);
        row.innerHTML = `<td><button type="button" class="remove-sku-btn"><i class="bi bi-x-circle"></i></button></td>
                         <td contenteditable="false">${skuName}<input type="hidden" name="skus[]" value="${skuId}"></td>`;

        const headerCells = skuTable.querySelectorAll('thead tr:first-child th');
        for (let i = 2; i < headerCells.length; i++) {
            const newTd = document.createElement('td');
            const isSkuSpecificQuestion = headerCells[i].classList.contains('sku-specific-question');

            if (isSkuSpecificQuestion) {
                newTd.contentEditable = "false";
            } else {
                newTd.contentEditable = "true";
                newTd.addEventListener('paste', handlePaste);
                newTd.addEventListener('keydown', handleCellNavigation);
            }
            row.appendChild(newTd);
        }
        tableBody.appendChild(row);

        row.querySelector('.remove-sku-btn').addEventListener('click', removeSkuRow);
        applyListenersToRow(row);
    }

    function removeSkuRow(event) {
        const row = event.target.closest('tr');
        if (row) {
            row.remove();
        }
    }

    // Full Screen Functions
    function toggleFullScreen() {
        if (!document.fullscreenElement) {
            fullScreenContainer.requestFullscreen().then(() => {
                document.body.style.backgroundColor = "white";
                fullScreenContainer.style.backgroundColor = "white";
                fullScreenButton.textContent = 'Exit Full Screen';
            }).catch(err => {
                alert(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
            });
        } else {
            document.exitFullscreen().then(() => {
                document.body.style.backgroundColor = "";
                fullScreenContainer.style.backgroundColor = "";
                fullScreenButton.textContent = 'Full Screen';
            }).catch(err => {
                alert(`Error attempting to exit full-screen mode: ${err.message} (${err.name})`);
            });
        }
    }

    function handleFullScreenChange() {
        if (!document.fullscreenElement) {
            fullScreenButton.textContent = 'Full Screen';
            document.body.style.backgroundColor = "";
            fullScreenContainer.style.backgroundColor = "";
        }
    }

    
   

    // Add SKU-specific Question (Step 5)
    function addSkuSpecificQuestion() {
        const tableHeadRow1 = skuTable.querySelector('thead tr:first-child');
        const tableHeadRow2 = skuTable.querySelector('thead tr:nth-child(2)');

        // Create the question input column in the first header row
        let newTh = document.createElement('th');
        newTh.classList.add('sku-specific-question');
        newTh.innerHTML = `
            <input type="text" class="column-input" placeholder="Question">
            <button type="button" class="remove-column-x">
                <i class="bi bi-x-circle"></i>
            </button>
        `;
        tableHeadRow1.appendChild(newTh);

        // For the second header row
        let newThType = document.createElement('th');
        newThType.classList.add('sku-specific-question');
        newThType.innerHTML = `
            <select class="form-control question-type-select">
                <option value="" disabled selected>Select question type</option>
                <option value="text">Text</option>
                <option value="number">Number</option>
                <option value="file">File Upload</option>
                <option value="date">Date</option>
            </select>
        `;
        tableHeadRow2.appendChild(newThType);

        // Add an empty cell to each row in the table body
        skuTable.querySelectorAll('tbody tr').forEach(row => {
            let newTd = document.createElement('td');
            newTd.contentEditable = "false";
            row.appendChild(newTd);
        });

        // Rebind remove column functionality
        addRemoveColumnListeners();
    }

    // Remove Column Functionality
    function addRemoveColumnListeners() {
        const removeColumnButtons = skuTable.querySelectorAll('.remove-column-x');
        removeColumnButtons.forEach((button) => {
            button.removeEventListener('click', removeColumnHandler);
            button.addEventListener('click', removeColumnHandler);
        });
    }

    function removeColumnHandler(event) {
        const th = event.target.closest('th');
        const index = Array.from(th.parentNode.children).indexOf(th);
        removeColumn(index);
    }

    function removeColumn(index) {
        const table = skuTable;
        const headerCellsRow1 = table.querySelectorAll('thead tr:first-child th');
        const headerCellsRow2 = table.querySelectorAll('thead tr:nth-child(2) th');
        const rows = table.querySelectorAll('tbody tr');

        if (index < 2 || index >= headerCellsRow1.length) return;

        // Remove the column header
        headerCellsRow1[index].remove();

        // Check if the second header row exists before trying to remove its cell
        if (headerCellsRow2.length > 0 && headerCellsRow2[index]) {
            headerCellsRow2[index].remove();
        }

        // Remove the corresponding cells from each row in the table body
        rows.forEach(row => {
            const cell = row.children[index];
            if (cell) {
                cell.remove();
            }
        });
    }

    // Apply listeners to each row
    function applyListenersToRow(row) {
        row.querySelectorAll('td[contenteditable="true"]').forEach(cell => {
            cell.addEventListener('paste', handlePaste);
            cell.addEventListener('keydown', handleCellNavigation);
            cell.addEventListener('input', handleEmptyCell); // Add listener for input events
        });
    }

    function handleEmptyCell(event) {
        const cell = event.target;
    
        // Check if the cell is empty after content deletion
        if (!cell.textContent.trim()) {
            console.log('trimming');
            cell.textContent = ''; // Ensure it's explicitly empty
        }
    }
    

    // Handle Paste Function
    function handlePaste(event) {
        event.preventDefault();

        const pasteData = (event.clipboardData || window.clipboardData).getData('text');
        const rows = pasteData.trim().split('\n').map(row => row.split('\t'));

        const startRow = event.target.parentNode.rowIndex - 1;
        const startCol = event.target.cellIndex;
        console.log(startRow);
        console.log(startCol);

        rows.forEach((rowData, rowIndex) => {
            
            let tableRow = document.querySelector(`#sku-table tbody`).rows[startRow + rowIndex];
            if (tableRow) console.log(tableRow);
            if (!tableRow) tableRow = addNewRow(); console.log('added new row');

            rowData.forEach((cellData, colIndex) => {
                if (startCol + colIndex >= document.querySelectorAll('#sku-table thead th').length) {
                    addNewExtraDataColumn();
                    console.log('added new col')
                }
                const cell = tableRow.cells[startCol + colIndex];
                if (cell && cell.contentEditable === "true") cell.textContent = cellData.trim();
            });
        });
    }

    function addNewExtraDataColumn() {
        const tableHeadRow1 = skuTable.querySelector('thead tr:first-child');
        const tableHeadRow2 = skuTable.querySelector('thead tr:nth-child(2)');
        
        let newTh = document.createElement('th');
        newTh.innerHTML = `<input type="text" class="column-input" placeholder="Column Name">
                        <button type="button" class="remove-column-x">
                            <i class="bi bi-x-circle"></i>
                        </button>`;
        tableHeadRow1.appendChild(newTh);

        if (tableHeadRow2) {
            let newThTypeRow = document.createElement('th');
            tableHeadRow2.appendChild(newThTypeRow);
        } 


        // Add new cells to each row in the table body
        document.querySelectorAll('#sku-table tbody tr').forEach(row => {
            const newTd = document.createElement('td');
            newTd.contentEditable = "true";
            newTd.addEventListener('paste', handlePaste);
            newTd.addEventListener('input', handleEmptyCell); // Add listener for input events
            row.appendChild(newTd);
        });

        // Rebind the remove column event after adding the new column
        addRemoveColumnListeners();
        // Reapply cell navigation after adding new columns
        applyCellNavigation();


    }


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

    // Handle Cell Navigation
    function handleCellNavigation(event) {
        const cell = event.target;
        let targetCell;

        // Handle navigation for header cells
        if (cell.tagName === 'INPUT') {
            console.log('hit enter');
            const currentCellIndex = Array.from(cell.parentNode.parentNode.children).indexOf(cell.parentNode);

            if (event.key === "ArrowDown" || event.key === "Enter") {
                event.preventDefault();
                const firstBodyRow = skuTable.querySelector('tbody tr');
                if (firstBodyRow) {
                    targetCell = firstBodyRow.children[currentCellIndex];
                }
            }


        } else {
            // Handle navigation for body cells
            const currentRow = cell.parentNode;
            const currentCellIndex = Array.from(currentRow.children).indexOf(cell);

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

    // Add New Row Function
    function addNewRow() {
        const tableBody = skuTable.querySelector('tbody');
        const newRow = document.createElement('tr');

        const numColumns = skuTable.querySelectorAll('thead tr:first-child th').length;
        for (let i = 0; i < numColumns; i++) {
            const newCell = document.createElement('td');
            if (i === 0) {
                newCell.innerHTML = `<button type="button" class="remove-sku-btn"><i class="bi bi-x-circle"></i></button>`;
            } else if (i === 1) {
                newCell.contentEditable = "false";
                newCell.innerHTML = `New SKU <input type="hidden" name="skus[]" value="">`;
            } else {
                const isSkuSpecificQuestion = skuTable.querySelectorAll('thead tr:first-child th')[i].classList.contains('sku-specific-question');
                if (isSkuSpecificQuestion) {
                    newCell.contentEditable = "false";
                } else {
                    newCell.contentEditable = "true";
                    newCell.addEventListener('paste', handlePaste);
                    newCell.addEventListener('keydown', handleCellNavigation);
                }
            }
            newRow.appendChild(newCell);
        }
        tableBody.appendChild(newRow);

        newRow.querySelector('.remove-sku-btn').addEventListener('click', removeSkuRow);
        applyListenersToRow(newRow);
        applyCellNavigation(); // Rebind cell navigation listeners
        return newRow;
    }

    // Submit Form Function (Step 2)
    function submitForm(event) {
        // Prevent the default form submission to handle it manually
        event.preventDefault();

        const form = document.getElementById('rfp-skus-form');
        const tableBody = skuTable.querySelector('tbody');
        const skuData = [];


        // Get the headers in the exact order they appear in the table
        const allColumnHeaders = Array.from(skuTable.querySelectorAll('thead tr:first-child th'))
            .map(th => th.querySelector('.column-input') ? th.querySelector('.column-input').value.toString() : th.textContent.trim());


        tableBody.querySelectorAll('tr').forEach(row => {
            const skuId = row.querySelector('input[name="skus[]"]').value;
            const rowValues = Array.from(row.querySelectorAll('td'))
                .slice(2) // Skip the first two columns (Remove SKU and SKU Name)
                .map(td => td.innerText.trim());

            // Use an array to store key-value pairs for consistent ordering
            const dataArray = [];
            allColumnHeaders.slice(2).forEach((header, index) => { // Skip first two columns
                dataArray.push([header, rowValues[index]]);
            });

            skuData.push({
                sku_id: skuId,
                data: dataArray
            });
        });


        // Add SKU data to the hidden input field
        extraColumnsDataInput.value = JSON.stringify(skuData);

        // Submit the form
        form.submit();
    }

    // submit form step 4

    function submitFormStep4(){
        const skuData = [];
        const tableBody = skuTable.querySelector('tbody');

        // Collect Extra Data Column Indices and Headers
        const extraDataColumns = [];
        skuTable.querySelectorAll('thead tr:first-child th').forEach((th, index) => {
            if (!th.classList.contains('sku-specific-question') && index >= 2) {
                const header = th.querySelector('.column-input') ? th.querySelector('.column-input').value.trim() : th.textContent.trim();
                extraDataColumns.push({ index: index, header: header });
            }
        });

        // Collect SKU-specific Question Column Indices, Headers, and Types
        const skuSpecificColumns = [];
        skuTable.querySelectorAll('thead tr:first-child th').forEach((th, index) => {
            if (th.classList.contains('sku-specific-question')) {
                const header = th.querySelector('.column-input') ? th.querySelector('.column-input').value.trim() : '';
                const typeSelect = skuTable.querySelector(`thead tr:nth-child(2) th:nth-child(${index + 1}) select.question-type-select`);
                const questionType = typeSelect ? typeSelect.value : '';
                skuSpecificColumns.push({ index: index, header: header, question_type: questionType });
            }
        });

        // Collect SKU Data
        tableBody.querySelectorAll('tr').forEach(row => {
            const skuId = row.querySelector('input[name="skus[]"]').value;
            const cells = row.querySelectorAll('td');

            // Extract Extra Data Values
            const dataArray = [];
            extraDataColumns.forEach(col => {
                const cell = cells[col.index];
                const value = cell ? cell.innerText.trim() : '';
                dataArray.push([col.header, value]);
            });

            skuData.push({
                sku_id: skuId,
                data: dataArray
            });
        });

        // Set the SKU Data in Hidden Input
        extraColumnsDataInput.value = JSON.stringify(skuData);

        // Collect SKU-specific Questions Data
        const questionsData = [];
        skuSpecificColumns.forEach(col => {
            const question = col.header;
            const questionType = col.question_type;
            if (question && questionType) {
                questionsData.push({
                    question: question,
                    question_type: questionType
                });
            }
        });

        // Set the SKU-specific Questions Data in Hidden Input
        if (skuSpecificDataInput) {
            skuSpecificDataInput.value = JSON.stringify(questionsData);
        }


        document.getElementById('rfp-sku-questions-form').submit();

    }


    // Finalize RFP Function (Step 5)
    function finalizeRFP() {

        // process general questions before submit
        processGeneralQuestionsBeforeSubmit('finalize-rfp-form');
            
        const skuData = [];
        const tableBody = skuTable.querySelector('tbody');

        // Collect Extra Data Column Indices and Headers
        const extraDataColumns = [];
        skuTable.querySelectorAll('thead tr:first-child th').forEach((th, index) => {
            if (!th.classList.contains('sku-specific-question') && index >= 2) {
                const header = th.querySelector('.column-input') ? th.querySelector('.column-input').value.trim() : th.textContent.trim();
                extraDataColumns.push({ index: index, header: header });
            }
        });

        // Collect SKU-specific Question Column Indices, Headers, and Types
        const skuSpecificColumns = [];
        skuTable.querySelectorAll('thead tr:first-child th').forEach((th, index) => {
            if (th.classList.contains('sku-specific-question')) {
                const header = th.querySelector('.column-input') ? th.querySelector('.column-input').value.trim() : '';
                const typeSelect = skuTable.querySelector(`thead tr:nth-child(2) th:nth-child(${index + 1}) select.question-type-select`);
                const questionType = typeSelect ? typeSelect.value : '';
                skuSpecificColumns.push({ index: index, header: header, question_type: questionType });
            }
        });

        // Collect SKU Data
        tableBody.querySelectorAll('tr').forEach(row => {
            const skuId = row.querySelector('input[name="skus[]"]').value;
            const cells = row.querySelectorAll('td');

            // Extract Extra Data Values
            const dataArray = [];
            extraDataColumns.forEach(col => {
                const cell = cells[col.index];
                const value = cell ? cell.innerText.trim() : '';
                dataArray.push([col.header, value]);
            });

            skuData.push({
                sku_id: skuId,
                data: dataArray
            });
        });

        // Set the SKU Data in Hidden Input
        extraColumnsDataInput.value = JSON.stringify(skuData);

        // Collect SKU-specific Questions Data
        const questionsData = [];
        skuSpecificColumns.forEach(col => {
            const question = col.header;
            const questionType = col.question_type;
            if (question && questionType) {
                questionsData.push({
                    question: question,
                    question_type: questionType
                });
            }
        });

        // Set the SKU-specific Questions Data in Hidden Input
        if (skuSpecificDataInput) {
            skuSpecificDataInput.value = JSON.stringify(questionsData);
        }

        // Submit the Form
        document.getElementById('finalize-rfp-form').submit();
    }


    // Shared: Add New Row Functionality
    function addNewRow() {
        const tableBody = skuTable.querySelector('tbody');
        const newRow = document.createElement('tr');

        const numColumns = skuTable.querySelectorAll('thead tr:first-child th').length;
        for (let i = 0; i < numColumns; i++) {
            const newCell = document.createElement('td');
            if (i === 0) {
                newCell.innerHTML = `<button type="button" class="remove-sku-btn"><i class="bi bi-x-circle"></i></button>`;
            } else if (i === 1) {
                newCell.contentEditable = "false";
                newCell.innerHTML = `New SKU <input type="hidden" name="skus[]" value="">`;
            } else {
                const isSkuSpecificQuestion = skuTable.querySelectorAll('thead tr:first-child th')[i].classList.contains('sku-specific-question');
                if (isSkuSpecificQuestion) {
                    newCell.contentEditable = "false";
                } else {
                    newCell.contentEditable = "true";
                    newCell.addEventListener('paste', handlePaste);
                    newCell.addEventListener('keydown', handleCellNavigation);
                }
            }
            newRow.appendChild(newCell);
        }
        tableBody.appendChild(newRow);

        newRow.querySelector('.remove-sku-btn').addEventListener('click', removeSkuRow);
        applyListenersToRow(newRow);
        return newRow;
    }

    function processGeneralQuestionsBeforeSubmit(formId) {
        // Select the question table rows within the specified form
        const rows = document.querySelectorAll(`#${formId} #question-table-body tr`);
    
        rows.forEach((row) => {
            const questionTypeSelect = row.querySelector(".question-type-select");
            const hiddenMultipleChoiceInput = row.querySelector(".hidden-multiple-choice-input");
    
            if (
                questionTypeSelect.value !== "Single-select" &&
                questionTypeSelect.value !== "Multi-select"
            ) {
                // Clear the hidden input for non-SS/MS types
                hiddenMultipleChoiceInput.value = "";
            }
        });
    }
    

});
