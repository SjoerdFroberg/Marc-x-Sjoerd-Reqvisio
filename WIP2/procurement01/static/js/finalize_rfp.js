document.addEventListener("DOMContentLoaded", function () {
    // Initialize Tagify on load based on existing selection values
    document.querySelectorAll(".question-type-select").forEach((select) => {
        initializeTagifyIfNeeded(select);
        select.addEventListener("change", handleQuestionTypeChange);
    });

    // Function to initialize or destroy Tagify based on the question type
    function initializeTagifyIfNeeded(select) {
        const row = select.closest("tr");
        const mcInput = row.querySelector(".multiple-choice-input");

        if (!mcInput) return;  // Ensure mcInput exists

        // Initialize Tagify if question type is Multi-select or Single-select
        if (select.value === "Multi-select" || select.value === "Single-select") {
            if (!mcInput._tagify) {  // Only initialize if Tagify isn't already applied
                const savedTags = mcInput.getAttribute("data-saved-tags") || "[]";
                mcInput._tagify = new Tagify(mcInput);
                try {
                    const tagsArray = JSON.parse(savedTags);
                    mcInput._tagify.addTags(tagsArray);
                } catch (error) {
                    console.warn("Could not parse saved tags:", error);
                }
            }
            mcInput.style.display = "block";
        } else {
            // Destroy Tagify if switching away from Multi-select or Single-select
            if (mcInput._tagify) {
                mcInput.setAttribute("data-saved-tags", JSON.stringify(mcInput._tagify.value.map(tag => tag.value)));
                mcInput._tagify.destroy();
                mcInput._tagify = null;
            }
            mcInput.style.display = "none";
        }
    }

    // Handle the change event for question type dropdowns
    function handleQuestionTypeChange(event) {
        initializeTagifyIfNeeded(event.target);
    }

    // Add functionality to add a new question row
    document.getElementById("add-general-question-btn").addEventListener("click", function () {
        const newRow = document.createElement("tr");
        newRow.innerHTML = `
            <td><button type="button" class="btn btn-danger remove-question-btn">Remove</button></td>
            <td><input type="text" name="question_text" class="form-control"></td>
            <td>
                <select class="question-type-select form-control">
                    <option value="text">Text</option>
                    <option value="number">Number</option>
                    <option value="file">File Upload</option>
                    <option value="date">Date</option>
                    <option value="Single-select">Single Select</option>
                    <option value="Multi-select">Multi Select</option>
                </select>
            </td>
            <td><input type="text" class="multiple-choice-input form-control" style="display: none;" data-saved-tags="[]"></td>
        `;
        
        // Append the new row to the questions table body
        document.getElementById("general-questions-table-body").appendChild(newRow);

        // Initialize event listeners for the new row
        const select = newRow.querySelector(".question-type-select");
        initializeTagifyIfNeeded(select);
        select.addEventListener("change", handleQuestionTypeChange);

        // Remove button functionality
        newRow.querySelector(".remove-question-btn").addEventListener("click", function () {
            newRow.remove();
        });
    });

// ---    
    // SKU Search and Add
    const skuSearchInput = document.getElementById("sku-search-input");
    skuSearchInput.addEventListener("input", function () {
        const query = skuSearchInput.value;
        if (query.length > 2) {
            // Mock AJAX call to get SKU results
            fetch(`/api/search_skus/?query=${query}`)
                .then((response) => response.json())
                .then((data) => {
                    const skuSearchResults = document.getElementById("sku-search-results");
                    skuSearchResults.innerHTML = "";
                    data.forEach(function (sku) {
                        const skuElement = document.createElement("div");
                        skuElement.classList.add("sku-result-item");
                        skuElement.textContent = sku.name;
                        skuElement.dataset.skuId = sku.id;
                        skuElement.addEventListener("click", function () {
                            addSkuToTable(sku);
                        });
                        skuSearchResults.appendChild(skuElement);
                    });
                });
        }
    });

    function addSkuToTable(sku) {
        const skuSpecificTableBody = document.querySelector("#sku-specific-table tbody");
        const newRow = skuSpecificTableBody.insertRow();
        newRow.dataset.skuId = sku.id;

        newRow.innerHTML = `
            <td><button type="button" class="remove-sku-btn"><i class="bi bi-x-circle"></i></button></td>
            <td contenteditable="false">${sku.name}</td>
            <td contenteditable="true"></td>
            <td contenteditable="true"></td>
            <td contenteditable="true"></td>
        `;

        newRow.querySelector(".remove-sku-btn").addEventListener("click", function () {
            newRow.remove();
        });
    }

    // Finalize RFP
    const finalizeRfpBtn = document.getElementById("finalize-rfp-btn");
    finalizeRfpBtn.addEventListener("click", function () {
        // Collect data to submit
        const rfpData = {
            title: document.getElementById("id_title").value,
            description: document.getElementById("id_description").value,
            files: Array.from(document.getElementById("new-files").files),
            generalQuestions: [],
            skus: [],
        };

        // Collect General Questions Data
        document.querySelectorAll("#general-questions-table-body tr").forEach(function (row) {
            const questionText = row.querySelector("input[name='question_text']").value;
            const questionType = row.querySelector(".question-type-select").value;
            const multipleChoiceOptions = row.querySelector(".multiple-choice-input").value;
            rfpData.generalQuestions.push({
                questionText,
                questionType,
                multipleChoiceOptions,
            });
        });

        // Collect SKU Data
        document.querySelectorAll("#sku-specific-table tbody tr").forEach(function (row) {
            const skuId = row.dataset.skuId;
            const skuDetails = Array.from(
                row.querySelectorAll("td[contenteditable='true']")
            ).map((td) => td.textContent);
            rfpData.skus.push({ skuId, details: skuDetails });
        });

        // Submit Data (Mock AJAX call)
        fetch(`/api/finalize_rfp/${rfpId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify(rfpData),
        }).then((response) => {
            if (response.ok) {
                alert("RFP finalized successfully!");
                window.location.href = "/procurement01/rfp/list/";
            } else {
                alert("An error occurred while finalizing the RFP.");
            }
        });
    });

    // Utility function to get CSRF token
    function getCsrfToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }
});
