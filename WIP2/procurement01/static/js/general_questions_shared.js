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

        newRow.querySelector(".remove-question-btn").addEventListener("click", () => {
            newRow.remove();
            updateFormIndices();
        });
    }

    function updateFormIndices() {
        const rows = document.querySelectorAll("#question-table-body tr");
        const totalFormsInput = document.querySelector("#id_form-TOTAL_FORMS");

        rows.forEach((row, index) => {
            row.querySelectorAll("input, select").forEach((input) => {
                input.name = input.name.replace(/form-\d+-/, `form-${index}-`);
                input.id = input.id.replace(/form-\d+-/, `form-${index}-`);
            });
        });

        totalFormsInput.value = rows.length;
    }

    document.querySelectorAll("#question-table-body tr").forEach(initializeRow);

    const addQuestionBtn = document.getElementById("add-question-btn");
    if (addQuestionBtn) {
        addQuestionBtn.addEventListener("click", addQuestionRow);
    }

    const removeButtons = document.querySelectorAll(".remove-question-btn");
    removeButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            const row = btn.closest("tr");
            row.remove();
            updateFormIndices();
        });
    });
});
