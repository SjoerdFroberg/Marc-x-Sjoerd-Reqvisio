document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('sku-allocation-table');

    // Handle toggling supplier rows
    table.addEventListener('click', (e) => {
        if (e.target.closest('.toggle-suppliers')) {
            const button = e.target.closest('.toggle-suppliers');
            const skuCode = button.getAttribute('data-sku');
            toggleSupplierRows(skuCode, button);
        }
    });

    // Handle changes to allocated quantity inputs
    table.addEventListener('input', (e) => {
        if (e.target.classList.contains('allocated-qty-input')) {
            recalculateForSKU(e.target.getAttribute('data-sku'));
        }
    });

    function toggleSupplierRows(skuCode, button) {
        const detailRows = table.querySelectorAll(`.sku-detail-row[data-parent-sku="${skuCode}"]`);
        let isCollapsed = true;
        detailRows.forEach(row => {
            if (row.classList.contains('d-none')) {
                row.classList.remove('d-none');
                isCollapsed = false;
            } else {
                row.classList.add('d-none');
            }
        });

        // Update icon
        const icon = button.querySelector('i');
        if (!isCollapsed) {
            icon.classList.remove('bi-caret-down-square');
            icon.classList.add('bi-caret-up-square');
        } else {
            icon.classList.remove('bi-caret-up-square');
            icon.classList.add('bi-caret-down-square');
        }
    }

    function recalculateForSKU(skuCode) {
        const summaryRow = table.querySelector(`.sku-summary-row[data-sku="${skuCode}"]`);
        const detailRows = table.querySelectorAll(`.sku-detail-row[data-parent-sku="${skuCode}"]`);
        
        let totalAllocatedQty = 0;
        let totalCost = 0;
        let suppliersWithAllocations = [];
        
        detailRows.forEach(row => {
            const input = row.querySelector('.allocated-qty-input');
            const qty = parseFloat(input.value) || 0;
            const price = parseFloat(input.getAttribute('data-price')) || 0;
            const supplier = input.getAttribute('data-supplier');

            const rowTotalCost = qty * price;
            totalAllocatedQty += qty;
            totalCost += rowTotalCost;

            // Update row's total cost cell
            const detailCostCell = row.querySelector('.detail-total-cost');
            detailCostCell.textContent = rowTotalCost.toFixed(2);

            if (qty > 0) {
                suppliersWithAllocations.push(supplier);
            }
        });

        const quantityRequiredCell = summaryRow.cells[3]; // Assuming fixed column positions
        const quantityRequired = parseFloat(quantityRequiredCell.textContent) || 0;
        
        // Recalculate average price
        let avgPrice = (totalAllocatedQty > 0) ? (totalCost / totalAllocatedQty) : 0;

        // Update summary row fields
        const suppliersCell = summaryRow.querySelector('.summary-suppliers');
        const totalQtyAssignedCell = summaryRow.querySelector('.summary-quantity-assigned');
        const avgPriceCell = summaryRow.querySelector('.summary-price');
        const totalCostCell = summaryRow.querySelector('.summary-total-cost');

        suppliersCell.textContent = suppliersWithAllocations.join(', ');
        totalQtyAssignedCell.textContent = totalAllocatedQty;
        avgPriceCell.textContent = avgPrice.toFixed(2);
        totalCostCell.textContent = totalCost.toFixed(2);

       
    }
});
