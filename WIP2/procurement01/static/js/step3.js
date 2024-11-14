document.addEventListener('DOMContentLoaded', function() {

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
                console.log(multipleChoiceInput.value);
                // Destroy Tagify instance if exists
                if (tagify) {
                    tagify.destroy();
                    tagify = null;
                }
                // Clear the hidden input
                hiddenMultipleChoiceInput.value = '';
            }
        }

        // Bind the change event to the question type select
        questionTypeSelect.addEventListener('change', toggleMultipleChoiceInput);

        // Initialize the multiple choice input based on the initial value
        toggleMultipleChoiceInput();
    }

    // Initialize all existing rows
    var rows = document.querySelectorAll('#question-table-body tr');
    rows.forEach(function(row) {
        initializeRow(row);
    });

    // Add functionality to the 'Add Another Question' button
    var addQuestionBtn = document.getElementById('add-question-btn');
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
            var totalFormsInput = document.querySelector('#id_form-TOTAL_FORMS');
            totalFormsInput.value = document.querySelectorAll('#question-table-body tr').length;
            updateFormIndices();
        });
    });

    // Function to update form indices after adding/removing rows
    function updateFormIndices() {
        var forms = document.querySelectorAll('#question-table-body tr');
        forms.forEach(function(row, index) {
            // Update the names and ids of the input fields
            var questionTextInput = row.querySelector('input[name^="form-"][name$="-question_text"]');
            var questionTypeSelect = row.querySelector('select[name^="form-"][name$="-question_type"]');
            var multipleChoiceInput = row.querySelector('.multiple-choice-input');
            var hiddenMultipleChoiceInput = row.querySelector('input[name^="form-"][name$="-multiple_choice_options"]');

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
    }

    // Add event listeners to existing remove buttons
    var removeBtns = document.querySelectorAll('.remove-question-btn');
    removeBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var row = btn.closest('tr');
            row.remove();
            // Update the total forms count and re-index the form fields
            var totalFormsInput = document.querySelector('#id_form-TOTAL_FORMS');
            totalFormsInput.value = document.querySelectorAll('#question-table-body tr').length;
            updateFormIndices();
        });
    });

});
