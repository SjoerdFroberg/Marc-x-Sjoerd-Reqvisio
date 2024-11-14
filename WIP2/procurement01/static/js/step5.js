// step5.js

document.addEventListener('DOMContentLoaded', () => {
    // Variables to keep track of current index in SKU search
    let currentIndex = -1;

    // SKU Search Elements
    const searchInput = document.getElementById('sku-search-input');
    const searchResults = document.getElementById('sku-search-results');
    const tableWrapper = document.querySelector('.table-wrapper');
    const skuTable = document.getElementById('sku-table');

    // Full Screen Elements
    const fullScreenContainer = document.getElementById('full-screen-container');
    const fullScreenButton = document.getElementById('full-screen-toggle');

    // Other Elements
    const addExtraColumnButton = document.getElementById('add-extra-column');
    const addSkuQuestionButton = document.getElementById('add-sku-question-btn');
    const finalizeRFPButton = document.querySelector('button[onclick="finalizeRFP()"]');

    // Initialize event listeners
    initEventListeners();

    function initEventListeners() {
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

        // Add Extra Data Column
        if (addExtraColumnButton) {
            addExtraColumnButton.addEventListener('click', addExtraDataColumn);
        }

        // Add SKU-specific Question
        if (addSkuQuestionButton) {
            addSkuQuestionButton.addEventListener('click', addSkuSpecificQuestion);
        }

        // Finalize RFP Button
        if (finalizeRFPButton) {
            finalizeRFPButton.addEventListener('click', finalizeRFP);
        }

        // Initialize Remove SKU Buttons
        document.querySelectorAll('.remove-sku-btn').forEach(button => {
            button.addEventListener('click', removeSkuRow);
        });

        // Initialize Remove Column Buttons
        addRemoveColumnListeners();

        // Initialize General Questions Formset
        initializeGeneralQuestions();

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

        const headerCells = document.querySelectorAll('#sku-table thead tr:first-child th');
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

    // Extra Data Column Functions
    function addExtraDataColumn() {
        const tableHeadRow1 = document.querySelector('#sku-table thead tr:first-child');
        const tableHeadRow2 = document.querySelector('#sku-table thead tr:nth-child(2)');

        const newTh = document.createElement('th');
        newTh.innerHTML = `<input type="text" class="column-input" placeholder="Column Name">
                           <button type="button" class="remove-column-x">
                               <i class="bi bi-x-circle"></i>
                           </button>`;
        tableHeadRow1.appendChild(newTh);

        const newThType = document.createElement('th');
        newThType.innerHTML = `<th></th>`;
        tableHeadRow2.appendChild(newThType);

        // Add new cells to each row in the table body
        document.querySelectorAll('#sku-table tbody tr').forEach(row => {
            const newTd = document.createElement('td');
            newTd.contentEditable = "true";
            newTd.addEventListener('paste', handlePaste);
            newTd.addEventListener('keydown', handleCellNavigation);
            row.appendChild(newTd);
        });

        // Rebind remove column listeners
        addRemoveColumnListeners();
    }

    function addRemoveColumnListeners() {
        const removeColumnButtons = document.querySelectorAll('.remove-column-x');
        removeColumnButtons.forEach((button) => {
            button.removeEventListener('click', removeColumnHandler);
            button.addEventListener('click', removeColumnHandler);
        });
    }

    function removeColumnHandler(event) {
        const index = Array.from(event.target.closest('th').parentNode.children).indexOf(event.target.closest('th'));
        removeColumn(index);
    }

    function removeColumn(index) {
        const table = document.getElementById('sku-table');
        const headerCellsRow1 = table.querySelectorAll('thead tr:first-child th');
        const headerCellsRow2 = table.querySelectorAll('thead tr:nth-child(2) th');
        const rows = table.querySelectorAll('tbody tr');

        if (index < 2 || index >= headerCellsRow1.length) return;

        headerCellsRow1[index].remove();
        headerCellsRow2[index].remove();

        rows.forEach(row => {
            const cell = row.children[index];
            if (cell) {
                cell.remove();
            }
        });
    }

    // SKU-specific Questions Functions
    function addSkuSpecificQuestion() {
        const tableHeadRow1 = document.querySelector('#sku-table thead tr:first-child');
        const tableHeadRow2 = document.querySelector('#sku-table thead tr:nth-child(2)');

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
        document.querySelectorAll('#sku-table tbody tr').forEach(row => {
            let newTd = document.createElement('td');
            newTd.contentEditable = "false";
            row.appendChild(newTd);
        });

        // Rebind remove column functionality
        addRemoveColumnListeners();
    }

    // Apply listeners to each row
    function applyListenersToRow(row) {
        row.querySelectorAll('td[contenteditable="true"]').forEach(cell => {
            cell.addEventListener('paste', handlePaste);
            cell.addEventListener('keydown', handleCellNavigation);
        });
    }

    // Handle Paste Function
    function handlePaste(event) {
        event.preventDefault();

        const pasteData = (event.clipboardData || window.clipboardData).getData('text');
        const rows = pasteData.trim().split('\n').map(row => row.split('\t'));

        const startRow = event.target.parentNode.rowIndex - 2; // Adjusted for header rows
        const startCol = event.target.cellIndex;

        rows.forEach((rowData, rowIndex) => {
            let tableRow = skuTable.querySelector('tbody').rows[startRow + rowIndex];
            if (!tableRow) {
                tableRow = addNewRow();
            }

            rowData.forEach((cellData, colIndex) => {
                if (startCol + colIndex >= skuTable.querySelectorAll('thead tr:first-child th').length) {
                    addExtraDataColumn();
                }
                const cell = tableRow.cells[startCol + colIndex];
                if (cell && cell.getAttribute('contenteditable') === "true") cell.textContent = cellData.trim();
            });
        });
    }

    // Add New Row (if needed during paste)
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
            } else {
                newCell.contentEditable = "true";
                newCell.addEventListener('paste', handlePaste);
                newCell.addEventListener('keydown', handleCellNavigation);
            }
            newRow.appendChild(newCell);
        }
        tableBody.appendChild(newRow);

        newRow.querySelector('.remove-sku-btn').addEventListener('click', removeSkuRow);
        applyListenersToRow(newRow);
        return newRow;
    }

    // Handle Cell Navigation
    function handleCellNavigation(event) {
        const cell = event.target;
        let currentRow, currentCellIndex, targetCell;

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

        if (targetCell && targetCell.getAttribute("contenteditable") === "true") {
            event.preventDefault();
            targetCell.focus();
            }
        }

        // Finalize RFP Function
        function finalizeRFP() {
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
            document.getElementById('extra_columns_data').value = JSON.stringify(skuData);
        
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
            document.getElementById('sku_specific_data').value = JSON.stringify(questionsData);
        
            // Submit the Form
            document.getElementById('finalize-rfp-form').submit();
        }
        


        
    // Initialize General Questions Formset
    function initializeGeneralQuestions() {
        // Function to initialize Tagify and show/hide logic for a row
        function initializeRow(row) {
            var questionTypeSelect = row.querySelector('.question-type-select');
            var multipleChoiceInput = row.querySelector('.multiple-choice-input');
            var hiddenMultipleChoiceInput = row.querySelector('.hidden-multiple-choice-input');

            var tagify;

            function toggleMultipleChoiceInput() {
                var selectedType = questionTypeSelect.value;
                if (selectedType === 'Single-select' || selectedType === 'Multi-select') {
                    multipleChoiceInput.style.display = 'block';
                    // Initialize Tagify if not already initialized
                    if (!tagify) {
                        tagify = new Tagify(multipleChoiceInput);
                        // Load existing tags from the hidden input value
                        if (hiddenMultipleChoiceInput.value) {
                            tagify.addTags(hiddenMultipleChoiceInput.value.split(','));
                        }
                        // When tags change, update the hidden input
                        tagify.on('change', function() {
                            hiddenMultipleChoiceInput.value = tagify.value.map(item => item.value).join(',');
                        });
                    }
                } else {
                    multipleChoiceInput.style.display = 'none';
                    // Destroy Tagify instance if exists
                    if (tagify) {
                        tagify.destroy();
                        tagify = null;
                    }
                    // Clear the hidden input
                    hiddenMultipleChoiceInput.value = '';
                }
            }

            if (questionTypeSelect) {
                // Bind the change event to the question type select
                questionTypeSelect.addEventListener('change', toggleMultipleChoiceInput);
                // Initialize the multiple choice input based on the initial value
                toggleMultipleChoiceInput();
            }
        }

        // Initialize all existing rows
        var rows = document.querySelectorAll('#question-table-body tr');
        rows.forEach(function(row) {
            initializeRow(row);
        });

        // Add functionality to the 'Add Another Question' button
        var addQuestionBtn = document.getElementById('add-question-btn');
        if (addQuestionBtn) {
            addQuestionBtn.addEventListener('click', function() {
                // Get the total number of forms from the management form
                var totalFormsInput = document.querySelector('#id_form-TOTAL_FORMS');
                var totalForms = parseInt(totalFormsInput.value);

                // Create a new row
                var newRow = document.createElement('tr');

                newRow.innerHTML = `
                    <td>
                    <button type="button" class="btn btn-danger remove-question-btn">Remove</button>
                    </td>
                    <td><input type="text" name="form-${totalForms}-question_text" class="form-control"></td>
                    <td>
                        <select name="form-${totalForms}-question_type" class="form-control question-type-select">
                            <option value="text">Text</option>
                            <option value="Single-select">Single-select</option>
                            <option value="Multi-select">Multi-select</option>
                            <option value="File upload">File upload</option>
                        </select>
                    </td>
                    <td>
                        <!-- Tagify input -->
                        <input type="text" class="multiple-choice-input form-control" placeholder="Type and press Enter to add options" style="display: none;">
                        <!-- Hidden input to store the options -->
                        <input type="hidden" name="form-${totalForms}-multiple_choice_options" class="hidden-multiple-choice-input">
                    </td>
                `;

                // Append the new row to the table body
                document.getElementById('question-table-body').appendChild(newRow);

                // Update the total number of forms
                totalFormsInput.value = totalForms + 1;

                // Initialize the new row
                initializeRow(newRow);

                // Add event listener to the remove button
                var removeBtn = newRow.querySelector('.remove-question-btn');
                removeBtn.addEventListener('click', function() {
                    newRow.remove();
                    // Update the total forms count and re-index the form fields
                    updateFormIndices();
                });

                // Update form indices after adding a new form
                updateFormIndices();
            });
        }

        // Function to update form indices after adding/removing rows
        function updateFormIndices() {
            var forms = document.querySelectorAll('#question-table-body tr');
            var totalFormsInput = document.querySelector('#id_form-TOTAL_FORMS');
            forms.forEach(function(row, index) {
                // Update the names and ids of the input fields
                var idInput = row.querySelector('input[name^="form-"][name$="-id"]');
                var questionTextInput = row.querySelector('input[name^="form-"][name$="-question_text"]');
                var questionTypeSelect = row.querySelector('select[name^="form-"][name$="-question_type"]');
                var multipleChoiceInput = row.querySelector('.multiple-choice-input');
                var hiddenMultipleChoiceInput = row.querySelector('input[name^="form-"][name$="-multiple_choice_options"]');
        
                if (idInput) {
                    idInput.name = `form-${index}-id`;
                    idInput.id = `id_form-${index}-id`;
                }
                if (questionTextInput) {
                    questionTextInput.name = `form-${index}-question_text`;
                    questionTextInput.id = `id_form-${index}-question_text`;
                }
                if (questionTypeSelect) {
                    questionTypeSelect.name = `form-${index}-question_type`;
                    questionTypeSelect.id = `id_form-${index}-question_type`;
                }
                if (multipleChoiceInput) {
                    multipleChoiceInput.id = `id_form-${index}-multiple_choice_options_tagify`;
                }
                if (hiddenMultipleChoiceInput) {
                    hiddenMultipleChoiceInput.name = `form-${index}-multiple_choice_options`;
                    hiddenMultipleChoiceInput.id = `id_form-${index}-multiple_choice_options`;
                }
            });
            // Update TOTAL_FORMS after re-indexing
            totalFormsInput.value = forms.length;
        }
        

        // Add event listeners to existing remove buttons
        var removeBtns = document.querySelectorAll('.remove-question-btn');
        removeBtns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                var row = btn.closest('tr');
                row.remove();
                // Update the total forms count and re-index the form fields
                updateFormIndices();
            });
        });
    }

    //-

    // Handle remove file buttons for existing files
    document.querySelectorAll('.file-icon:not(.new-file) .remove-file-btn').forEach(function(button) {
        button.addEventListener('click', function() {
            var fileIcon = this.closest('.file-icon');
            var deleteInput = fileIcon.querySelector('input[name="delete_files"]');
            deleteInput.disabled = false; // Enable the input to mark for deletion
            fileIcon.style.display = 'none'; // Hide the file icon
        });
    });

    // File Upload Handling
    document.getElementById('upload-files-button').addEventListener('click', function() {
        document.getElementById('id_new_files').click();
    });

    // Initialize an array to keep track of new files
    let newFilesArray = [];

    // Handle file input change event
    document.getElementById('id_new_files').addEventListener('change', function() {
        var files = this.files;
        var filesContainer = document.getElementById('files-container');

        // Iterate over selected files
        for (var i = 0; i < files.length; i++) {
            var file = files[i];

            // Add the file to the newFilesArray if not already added
            if (!newFilesArray.some(f => f.name === file.name && f.lastModified === file.lastModified)) {
                newFilesArray.push(file);

                // Create file icon element
                var fileIcon = document.createElement('div');
                fileIcon.className = 'file-icon new-file';
                fileIcon.setAttribute('data-file-name', file.name);

                fileIcon.innerHTML = `
                    <button type="button" class="remove-file-btn">
                        <i class="bi bi-x-circle-fill"></i>
                    </button>
                    <div>
                        <i class="bi bi-file-earmark"></i>
                        <span>${file.name}</span>
                    </div>
                `;

                // Append the file icon to the container
                filesContainer.appendChild(fileIcon);

                // Add event listener to the remove button
                fileIcon.querySelector('.remove-file-btn').addEventListener('click', function() {
                    // Remove the file from newFilesArray
                    newFilesArray = newFilesArray.filter(f => !(f.name === file.name && f.lastModified === file.lastModified));
                    // Remove the file icon from the UI
                    fileIcon.remove();
                    // Update the file input's files property
                    updateFileInput();
                });
            }
        }

        // Update the file input's files property
        updateFileInput();
    });

    // Function to update the file input's files property
    function updateFileInput() {
        const dataTransfer = new DataTransfer();
        newFilesArray.forEach(file => {
            dataTransfer.items.add(file);
        });
        document.getElementById('id_new_files').files = dataTransfer.files;
    }



    //-


   
    
});
