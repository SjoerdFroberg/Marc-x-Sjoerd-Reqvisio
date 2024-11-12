document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('.remove-sku-btn').forEach(button => {
        button.addEventListener('click', function () {
            const row = button.closest('tr');
            if (row) {
                row.remove();
            }
        });
    });

    // Full-screen toggle functionality
    document.getElementById('full-screen-toggle').addEventListener('click', function () {
        const fullScreenContainer = document.getElementById('full-screen-container');
        const fullScreenButton = document.getElementById('full-screen-toggle');

        if (!document.fullscreenElement) {
            fullScreenContainer.requestFullscreen().then(() => {
                document.body.style.backgroundColor = "white"; // Ensure body background color is set to white
                fullScreenContainer.style.backgroundColor = "white"; // Ensure full-screen container is white
                fullScreenButton.textContent = 'Exit Full Screen';
            }).catch(err => {
                alert(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
            });
        } else {
            document.exitFullscreen().then(() => {
                document.body.style.backgroundColor = ""; // Reset background color
                fullScreenContainer.style.backgroundColor = ""; // Reset container background color
                fullScreenButton.textContent = 'Full Screen';
            }).catch(err => {
                alert(`Error attempting to exit full-screen mode: ${err.message} (${err.name})`);
            });
        }
    });

    // Exit full screen with Esc key
    document.addEventListener('keydown', function (event) {
        if (event.key === "Escape" && document.fullscreenElement) {
            document.exitFullscreen();
        }
    });

    // Retrieve extra_columns from the hidden <div>
    const extraColumnsElement = document.getElementById('extra-columns-data');
    const extraColumns = JSON.parse(extraColumnsElement.textContent);
    const initialColumnCount = extraColumns.length;

    const tableHeadRow1 = document.querySelector('#sku-specific-table thead tr:first-child');
    const tableHeadRow2 = document.querySelector('#sku-specific-table thead tr:nth-child(2)');

    // Add new question column
    document.getElementById('add-question-btn').addEventListener('click', function() {
        // Create the question input column in the first header row
        let newTh = document.createElement('th');
        newTh.style.position = 'relative';
        newTh.innerHTML = `
            <input type="text" class="column-input" placeholder="Question">
            <button type="button" class="remove-column-x">
                <i class="bi bi-x-circle"></i>
            </button>
        `;
        tableHeadRow1.appendChild(newTh);

        // Create the question type selector column in the second header row
        let newThType = document.createElement('th');
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
        document.querySelectorAll('#sku-specific-table tbody tr').forEach(row => {
            let newTd = document.createElement('td');
            newTd.contentEditable = "false";
            row.appendChild(newTd);
        });

        // Rebind remove column functionality
        addRemoveColumnListeners();
    });

    // Remove a question column
    function removeColumn(index) {
        const headerCells = document.querySelectorAll('#sku-specific-table thead tr:first-child th');
        const typeCells = document.querySelectorAll('#sku-specific-table thead tr:nth-child(2) th');
        const rows = document.querySelectorAll('#sku-specific-table tbody tr');

        if (index < initialColumnCount + 1 || index >= headerCells.length) {
            console.warn("Attempted to remove an invalid or non-removable column.");
            return;
        }

        // Remove header cell and type cell
        headerCells[index].remove();
        typeCells[index].remove();

        // Remove each cell in the table body corresponding to this column
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
        removeColumnButtons.forEach(button => {
            button.removeEventListener('click', removeColumnHandler); // Remove previous listeners
            button.addEventListener('click', removeColumnHandler);
        });
    }

    // Remove column handler
    function removeColumnHandler(event) {
        const index = Array.from(event.target.closest('th').parentNode.children).indexOf(event.target.closest('th'));
        removeColumn(index);
    }

    // Add event listeners to initial remove buttons
    addRemoveColumnListeners();

    window.submitForm = function() {
        // Collect question headers (column input values)
        const questionHeaders = Array.from(tableHeadRow1.querySelectorAll('th input.column-input'))
            .map(input => input.value.trim())
            .slice(initialColumnCount+1);

        // Collect question types (select values)
        const questionTypes = Array.from(tableHeadRow2.querySelectorAll('th select.question-type-select'))
            .map(select => select.value);

        const questionsData = [];
        for (let i = 0; i < questionHeaders.length; i++) {
            if (questionHeaders[i] && questionTypes[i]) {
                questionsData.push({
                    question: questionHeaders[i],
                    question_type: questionTypes[i]
                });
            }
        }

        
        // Set the JSON data in the hidden input field
        document.getElementById('sku_specific_data').value = JSON.stringify(questionsData);

        // Delay form submission by 5 seconds to inspect logs
        setTimeout(() => {
            document.getElementById('rfp-sku-questions-form').submit();
        }, 5000); // 5000ms = 5 seconds delay
    };
});
