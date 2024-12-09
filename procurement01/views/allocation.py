from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from ..models import RFX, RFX_SKUs, SKUSpecificQuestion, SupplierResponse


@login_required
def sku_allocation(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)
    rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)

    all_in_price_q = SKUSpecificQuestion.objects.get(
        rfx=rfx, question="All-In Price / Unit"
    )
    quantity_offered_q = SKUSpecificQuestion.objects.get(
        rfx=rfx, question="Quantity Offered"
    )
    lead_time_q = SKUSpecificQuestion.objects.get(rfx=rfx, question="Lead Time in Days")

    supplier_responses = SupplierResponse.objects.filter(rfx=rfx)
    assignment_data = []

    for rfx_sku in rfx_skus:
        specification_data = rfx_sku.get_specification_data()

        sku_name = rfx_sku.sku.name
        oem = specification_data.get("OEM", "")
        sku_code = specification_data.get("SKU Code", "")
        quantity_required_str = specification_data.get("Quantity Required", "0")
        quantity_required = (
            int(quantity_required_str) if quantity_required_str.isdigit() else 0
        )
        max_lead_time = specification_data.get("Maximum Lead Time", "")

        response_items = []
        for s_response in supplier_responses:
            sku_responses = s_response.sku_specific_responses.filter(rfx_sku=rfx_sku)
            answer_map = {res.question_id: res for res in sku_responses}

            if (
                all_in_price_q.id in answer_map
                and quantity_offered_q.id in answer_map
                and lead_time_q.id in answer_map
            ):
                supplier_name = s_response.supplier.name
                try:
                    price = float(answer_map[all_in_price_q.id].answer_number or 0)
                except (ValueError, TypeError):
                    price = 0.0
                try:
                    q_offered = int(
                        answer_map[quantity_offered_q.id].answer_number or 0
                    )
                except (ValueError, TypeError):
                    q_offered = 0
                lead_time = answer_map[lead_time_q.id].answer_number or 0

                response_items.append(
                    {
                        "supplier": supplier_name,
                        "price": price,
                        "quantity_offered": q_offered,
                        "lead_time": lead_time,
                    }
                )

        response_items.sort(key=lambda x: x["price"])

        total_assigned_quantity = 0
        total_cost = 0
        assigned_suppliers = []
        detailed_response_items = []

        for resp in response_items:
            supplier = resp["supplier"]
            q_offered = resp["quantity_offered"]
            price = resp["price"]
            lead_time = resp["lead_time"]

            quantity_to_assign = (
                min(quantity_required - total_assigned_quantity, q_offered)
                if total_assigned_quantity < quantity_required
                else 0
            )

            if quantity_to_assign > 0:
                assigned_suppliers.append(supplier)
                total_assigned_quantity += quantity_to_assign
                total_cost += quantity_to_assign * price

            detailed_response_items.append(
                {
                    "sku": sku_name,
                    "oem": oem,
                    "sku_code": sku_code,
                    "quantity_required": quantity_required,
                    "maximum_lead_time": max_lead_time,
                    "supplier": supplier,
                    "quantity_offered": q_offered,
                    "price": price,
                    "lead_time": lead_time,
                    "quantity_assigned": quantity_to_assign,
                    "total_cost": (
                        quantity_to_assign * price if quantity_to_assign > 0 else 0
                    ),
                }
            )

        average_price = (
            total_cost / total_assigned_quantity if total_assigned_quantity > 0 else 0
        )

        assignment_data.append(
            {
                "sku": sku_name,
                "oem": oem,
                "sku_code": sku_code,
                "quantity_required": quantity_required,
                "maximum_lead_time": max_lead_time,
                "suppliers": ", ".join(assigned_suppliers),
                "quantity_offered": sum(
                    item["quantity_offered"] for item in detailed_response_items
                ),
                "price": average_price,
                "quantity_assigned": total_assigned_quantity,
                "total_cost": total_cost,
                "detailed_response_items": detailed_response_items,
            }
        )

    total_cost_all_rows = sum(row["total_cost"] for row in assignment_data)
    total_quantity_required = sum(row["quantity_required"] for row in assignment_data)
    total_quantity_assigned = sum(row["quantity_assigned"] for row in assignment_data)

    unique_oems = len(set(row["oem"] for row in assignment_data))
    unique_suppliers = len(
        set(
            supplier
            for row in assignment_data
            for supplier in row["suppliers"].split(", ")
            if supplier
        )
    )

    allocation_percentage = (
        total_quantity_assigned / total_quantity_required * 100
        if total_quantity_required > 0
        else 0
    )

    context = {
        "rfx": rfx,
        "assignment_data": assignment_data,
        "total_cost_all_rows": total_cost_all_rows,
        "total_quantity_required": total_quantity_required,
        "total_quantity_assigned": total_quantity_assigned,
        "unique_oems": unique_oems,
        "unique_suppliers": unique_suppliers,
        "allocation_percentage": allocation_percentage,
    }

    return render(request, "procurement01/sku_allocation.html", context)
