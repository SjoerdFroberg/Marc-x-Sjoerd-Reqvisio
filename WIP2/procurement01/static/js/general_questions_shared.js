document.addEventListener("DOMContentLoaded", function () {
    function initializeRow(row) {
        const questionTypeSelect = row.querySelector(".question-type-select");
        const multipleChoiceInput = row.querySelector(".multiple-choice-input");
        const hiddenMultipleChoiceInput = row.querySelector(".hidden-multiple-choice-input");

        let tagify;

        function toggleMultipleChoiceInput() {
            const selectedType = questionTypeSelect.value;
            if (selectedType === "Single-select" || selectedType === "Multi-select") {
                multipleChoiceInput.style.display = "block";
                if (!tagify) {
                    tagify = new Tagify(multipleChoiceInput);
                    if (hiddenMultipleChoiceInput.value) {
                        tagify.addTags(
                            hiddenMultipleChoiceInput.value
                                .split(",")
                                .map((item) => ({ value: item }))
                        );
                    }
                    tagify.on("change", () => {
                        hiddenMultipleChoiceInput.value = tagify.value
                            .map((tag) => tag.value)
                            .join(",");
                    });
                }
            } else {
                multipleChoiceInput.style.display = "none";
                if (tagify) {
                    tagify.destroy();
                    tagify = null;
                }
                hiddenMultipleChoiceInput.value = "";
            }
        }

        questionTypeSelect.addEventListener("change", toggleMultipleChoiceInput);
        toggleMultipleChoiceInput();
    }

    function addQuestionRow() {
        const totalFormsInput = document.querySelector("#id_form-TOTAL_FORMS");
        const newFormIndex = parseInt(totalFormsInput.value, 10);
        const tableBody = document.getElementById("question-table-body");

        const newRow = document.createElement("tr");
        newRow.innerHTML = `
            <td>
                <button type="button" class="btn btn-danger remove-question-btn">Remove</button>
                <input type="hidden" name="form-${newFormIndex}-id" id="id_form-${newFormIndex}-id">
                <input type="hidden" name="form-${newFormIndex}-DELETE" id="id_form-${newFormIndex}-DELETE">
            </td>
            <td><input type="text" name="form-${newFormIndex}-question_text" class="form-control"></td>
            <td>
                <select name="form-${newFormIndex}-question_type" class="form-control question-type-select">
                    <option value="text">Text</option>
                    <option value="Single-select">Single-select</option>
                    <option value="Multi-select">Multi-select</option>
                    <option value="File upload">File upload</option>
                </select>
            </td>
            <td>
                <input type="text" class="multiple-choice-input form-control" style="display: none;">
                <input type="hidden" name="form-${newFormIndex}-multiple_choice_options" class="hidden-multiple-choice-input">
            </td>
        `;

        tableBody.appendChild(newRow);
        totalFormsInput.value = newFormIndex + 1;

        initializeRow(newRow);

        const removeBtn = newRow.querySelector(".remove-question-btn");
        removeBtn.addEventListener("click", function() {
            removeQuestionRow(removeBtn);
        });
    }

    function updateFormIndices() {
        const rows = document.querySelectorAll("#question-table-body tr");
        const totalFormsInput = document.querySelector("#id_form-TOTAL_FORMS");
    
        rows.forEach((row, index) => {
            row.querySelectorAll("input, select").forEach((input) => {
                if (input.name) {
                    input.name = input.name.replace(/form-\d+-/, `form-${index}-`);
                }
                if (input.id) {
                    input.id = input.id.replace(/form-\d+-/, `form-${index}-`);
                }
            });
        });
    
        totalFormsInput.value = rows.length;
    }

    document.querySelectorAll("#question-table-body tr").forEach(initializeRow);

    const addQuestionBtn = document.getElementById("add-question-btn");
    if (addQuestionBtn) {
        addQuestionBtn.addEventListener("click", addQuestionRow);
    }



        function removeQuestionRow(btn) {
            const row = btn.closest("tr");
            const idInput = row.querySelector('input[name$="-id"]');
            const deleteInput = row.querySelector('input[name$="-DELETE"]');
    
            if (idInput && idInput.value) {
                // Existing form, set DELETE field and hide row
                if (deleteInput) {
                    deleteInput.value = 'on';  // Mark the form for deletion
                }
                row.style.display = 'none';
            } else {
                // New form, remove from DOM and update indices
                row.remove();
                updateFormIndices();
            }
    }

        // Update event listeners for remove buttons
    const removeButtons = document.querySelectorAll(".remove-question-btn");
    removeButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            removeQuestionRow(btn);
        });
    });





    const continueToStep4Button = document.getElementById('continue-to-step-4-btn');
    const backToStep2Button = document.getElementById('back-to-step-2-btn');

    // Continue to Step 4
    if (continueToStep4Button) {
        continueToStep4Button.addEventListener('click', function(event){
            // Update the navigation destination to Step 4
            document.getElementById('navigation_destination').value = 'step4';
            

        });
    }

    // Back to Step 2
    if (backToStep2Button) {
        backToStep2Button.addEventListener('click', function(event){
            // Update the navigation destination to Step 2
            document.getElementById('navigation_destination').value = 'step2';
            

        });
    }

});
