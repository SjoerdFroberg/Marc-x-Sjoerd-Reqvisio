{% extends 'procurement01/layout.html' %}

{% load dict_access %} <!-- Add this line to load custom filters -->

{% block title %}Create RFX - Step 4{% endblock %}

{% block content %}
<h2>Create RFX - Step 4: Define SKU-specific Questions for "{{ rfx.title }}"</h2>

<form id="rfx-sku-specific-questions-form" method="POST">
    {% csrf_token %}

    <div class="table-wrapper">
        <table class="table sheet-table" id="sku-specific-questions-table">
            <thead>
                <tr>
                    <th>SKU</th>
                    {% for question in sku_questions %}
                        <th>
                            <input type="text" name="questions[{{ question.id }}][question]" value="{{ question.question }}" placeholder="Enter question" class="column-input" />
                            <span class="remove-column-x" onclick="removeQuestionColumn({{ question.id }})">&#10006;</span>
                        </th>
                    {% endfor %}
                    <th class="add-question-placeholder">
                        <button type="button" onclick="addQuestionColumn()">Add New Question</button>
                    </th>
                </tr>
                <tr>
                    <th>Type</th>
                    {% for question in sku_questions %}
                        <th>
                            <select name="questions[{{ question.id }}][question_type]" class="question-type-select">
                                <option value="text" {% if question.question_type == 'text' %}selected{% endif %}>Text</option>
                                <option value="number" {% if question.question_type == 'number' %}selected{% endif %}>Number</option>
                                <option value="file" {% if question.question_type == 'file' %}selected{% endif %}>File Upload</option>
                                <option value="date" {% if question.question_type == 'date' %}selected{% endif %}>Date</option>
                            </select>
                        </th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for data in context_data %}
                    <tr>
                        <td>{{ data.rfx_sku.sku.name }}</td>
                        {% for column in extra_columns %}
                            <td>{{ data.extra_data|get_item:column }}</td>
                        {% endfor %}
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <button type="submit" class="btn btn-primary">Continue to Step 5</button>
</form>
{% endblock %}

{% block scripts %}
<script>
    let questionCounter = {{ sku_questions|length }};

    function addQuestionColumn() {
        questionCounter++;
        const tableHead = document.querySelector('#sku-specific-questions-table thead tr:first-child');
        const tableTypeRow = document.querySelector('#sku-specific-questions-table thead tr:nth-child(2)');

        let newQuestionTh = document.createElement('th');
        newQuestionTh.innerHTML = `
            <input type="text" name="questions[new_${questionCounter}][question]" placeholder="Enter question" class="column-input" />
            <span class="remove-column-x" onclick="removeQuestionColumn('new_${questionCounter}')">&#10006;</span>
        `;
        tableHead.insertBefore(newQuestionTh, tableHead.querySelector('.add-question-placeholder'));

        let newTypeTh = document.createElement('th');
        newTypeTh.innerHTML = `
            <select name="questions[new_${questionCounter}][question_type]" class="question-type-select">
                <option value="text">Text</option>
                <option value="number">Number</option>
                <option value="file">File Upload</option>
                <option value="date">Date</option>
            </select>
        `;
        tableTypeRow.insertBefore(newTypeTh, tableTypeRow.querySelector('.add-question-placeholder'));

        document.querySelectorAll('#sku-specific-questions-table tbody tr').forEach(row => {
            let newTd = document.createElement('td');
            newTd.contentEditable = "true";
            row.appendChild(newTd);
        });
    }

    function removeQuestionColumn(id) {
        const tableHead = document.querySelector('#sku-specific-questions-table thead tr:first-child');
        const tableTypeRow = document.querySelector('#sku-specific-questions-table thead tr:nth-child(2)');
        const questionIndex = Array.from(tableHead.children).findIndex(th => th.querySelector(`input[name="questions[${id}][question]"]`));

        if (questionIndex > -1) {
            tableHead.deleteCell(questionIndex);
            tableTypeRow.deleteCell(questionIndex);

            document.querySelectorAll('#sku-specific-questions-table tbody tr').forEach(row => {
                row.deleteCell(questionIndex);
            });
        }
    }
</script>
{% endblock %}

{% block styles %}
<style>
    .table-wrapper {
        overflow-x: auto;
        overflow-y: auto;
        white-space: nowrap;
        width: 100%;
        max-height: 400px;
        border: 1px solid #ddd;
    }

    .sheet-table {
        border-collapse: collapse;
        min-width: 800px;
        table-layout: auto;
    }
    
    .sheet-table th, .sheet-table td {
        border: 1px solid #d3d3d3;
        padding: 8px;
        text-align: left;
        min-width: 150px;
    }
    
    .sheet-table th {
        background-color: #f3f3f3;
        font-weight: bold;
        position: relative;
    }
    
    .sheet-table td[contenteditable="true"]:focus {
        outline: none;
        background-color: #e8f0fe;
    }
    
    .column-input {
        width: 100%;
        border: none;
        font-weight: bold;
    }

    .remove-column-x {
        position: absolute;
        top: 5px;
        right: 5px;
        cursor: pointer;
        display: none;
    }

    th:hover .remove-column-x {
        display: inline;
    }

    .question-type-select {
        width: 100%;
    }
</style>
{% endblock %}
