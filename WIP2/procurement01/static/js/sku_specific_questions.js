document.addEventListener('DOMContentLoaded', function () {
    
    // Retrieve extra_columns from the hidden <div>
    const extraColumnsElement = document.getElementById('extra-columns-data');
    const extraColumns = JSON.parse(extraColumnsElement.textContent);
    const initialColumnCount = extraColumns.length;
    console.log("Extra Columns:", extraColumns);
    console.log("Initial Column Count:", initialColumnCount);

    const tableHeadRow1 = document.querySelector('#sku-specific-table thead tr:first-child');
    const tableHeadRow2 = document.querySelector('#sku-specific-table thead tr:nth-child(2)');

    // Check that tableHeadRow1 and tableHeadRow2 are being selected correctly
    console.log("Table Head Row 1:", tableHeadRow1);
    console.log("Table Head Row 2:", tableHeadRow2);
    

    // Add new question column
    document.getElementById('add-question-btn').addEventListener('click', function() {
        let tableHeadRow1 = document.querySelector('#sku-specific-table thead tr:first-child');
        let tableHeadRow2 = document.querySelector('#sku-specific-table thead tr:nth-child(2)');
        console.log("Add Question button clicked");

        // Create the question input column in the first header row
        let newTh = document.createElement('th');
        newTh.style.position = 'relative';
        newTh.innerHTML = `
            <input type="text" class="column-input" placeholder="Question">
            <span class="remove-column-x" style="position: absolute; top: 5px; right: 5px; display: none;" onclick="removeColumn(${tableHeadRow1.children.length})">&#10006;</span>
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

        // Show remove button on hover
        newTh.addEventListener('mouseover', function() {
            newTh.querySelector('.remove-column-x').style.display = 'inline';
        });
        newTh.addEventListener('mouseout', function() {
            newTh.querySelector('.remove-column-x').style.display = 'none';
        });
    });

    // Remove a question column
    window.removeColumn = function(index) {
        const headerCells = document.querySelectorAll('#sku-specific-table thead tr:first-child th');
        const typeCells = document.querySelectorAll('#sku-specific-table thead tr:nth-child(2) th');
        const rows = document.querySelectorAll('#sku-specific-table tbody tr');

        if (index < 2 || index >= headerCells.length) {
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

        // Reassign onclick attributes only to header cells that contain .remove-column-x
        document.querySelectorAll('#sku-specific-table thead tr:first-child th .remove-column-x').forEach((span, i) => {
            const actualIndex = Array.from(span.parentNode.parentNode.children).indexOf(span.parentNode); // Recalculate the index
            span.setAttribute('onclick', `removeColumn(${actualIndex})`);
        });
    };

    window.submitForm = function() {
        console.log("submitForm function triggered");
        console.log("initial count:" + initialColumnCount);
    
        
        // Collect question headers (column input values)
        const questionHeaders = Array.from(tableHeadRow1.querySelectorAll('th input.column-input'))
            .map(input => input.value.trim())
            .slice(initialColumnCount+1);

            console.log("question headers:" + questionHeaders);
    
        // Collect question types (select values)
        const questionTypes = Array.from(tableHeadRow2.querySelectorAll('th select.question-type-select'))
            .map(select => select.value);

            console.log("question types:" + questionTypes);
    
        const questionsData = [];
        for (let i = 0; i < questionHeaders.length; i++) {
            if (questionHeaders[i] && questionTypes[i]) {
                questionsData.push({
                    question: questionHeaders[i],
                    question_type: questionTypes[i]
                });
            }
        }
    
        console.log("Questions Data:", questionsData);
    
        // Set the JSON data in the hidden input field
        document.getElementById('sku_specific_data').value = JSON.stringify(questionsData);
        console.log("Hidden input value set:", document.getElementById('sku_specific_data').value);
    
        // Delay form submission by 5 seconds to inspect logs
        setTimeout(() => {
            console.log("Submitting form");
            document.getElementById('rfp-sku-questions-form').submit();
        }, 5000); // 5000ms = 5 seconds delay
    };
    
});
