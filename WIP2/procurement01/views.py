from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, inlineformset_factory, formset_factory
from django.http import JsonResponse
from django.template.loader import render_to_string
import json 
from django.db import transaction 
from django.forms.models import model_to_dict
from collections import OrderedDict
from django.http import HttpResponse 
from collections import OrderedDict

from decimal import Decimal, InvalidOperation
from datetime import datetime


from django.views.decorators.http import require_POST

from django.views.decorators.csrf import csrf_exempt

from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.utils import timezone








from .models import SKU, Company, RFP, GeneralQuestion, RFP_SKUs,SKUSpecificQuestion, RFPFile, RFPInvitation, SupplierResponse, SKUSpecificQuestionResponse, GeneralQuestionResponse
from .forms import SKUForm, SupplierForm, RFPBasicForm, SKUSearchForm, GeneralQuestionForm, RFP_SKUForm, RFPForm, SKUSpecificQuestionForm, GeneralQuestionResponseForm, SKUSpecificQuestionResponseForm



def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # If user is already logged in, redirect to dashboard

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to dashboard after login
    else:
        form = AuthenticationForm()

    return render(request, 'procurement01/login.html', {'form': form})



@login_required
def dashboard_view(request):
    return render(request, 'procurement01/dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# View to list all SKUs
@login_required
def sku_list_view(request):
    skus = SKU.objects.all()
    return render(request, 'procurement01/sku_list.html', {'skus': skus})

# View to see details of a single SKU
@login_required
def sku_detail_view(request, sku_id):
    sku = get_object_or_404(SKU, id=sku_id)
    return render(request, 'procurement01/sku_detail.html', {'sku': sku})

# view to create new skus
@login_required
def sku_create_view(request):
    if request.method == 'POST':
        form = SKUForm(request.POST)
        if form.is_valid():
            sku = form.save(commit=False)  # Don't save to the database yet
            sku.company = request.user.company  # Set the company to the logged-in user's company
            sku.save()  # Now save to the database
            return redirect('sku_list')
    else:
        form = SKUForm()

    return render(request, 'procurement01/sku_form.html', {'form': form})

@login_required
def supplier_list_view(request):
    # Ensure the logged-in user is a procurer
    if request.user.is_procurer:
        procurer_company = request.user.company
        suppliers = Company.objects.filter(procurer=procurer_company)
        return render(request, 'procurement01/supplier_list.html', {'suppliers': suppliers})
    else:
        return render(request, 'procurement01/access_denied.html')
    


@login_required
def create_supplier_view(request):
    if not request.user.is_procurer:
        return render(request, 'procurement01/access_denied.html')  # Only procurers can create suppliers

    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save(procurer=request.user.company)  # Assign the supplier to the logged-in procurer's company
            return redirect('supplier_list')  # Redirect to the supplier list page after creating the supplier
    else:
        form = SupplierForm()

    return render(request, 'procurement01/supplier_form.html', {'form': form})


@login_required
# Step 1: Create RFP (Title, Description, and Files)
def create_rfp_step1(request):
    if request.method == 'POST':
        form = RFPBasicForm(request.POST)
        if form.is_valid():
            rfp = form.save()
            # Save each uploaded file
            for file in request.FILES.getlist('files'):
                RFPFile.objects.create(rfp=rfp, file=file)
            return redirect('create_rfp_step2', rfp_id=rfp.id)
    else:
        form = RFPBasicForm()

    return render(request, 'procurement01/create_rfp_step1.html', {'form': form})


@login_required
def search_skus(request):
    query = request.GET.get('query', '')
    company = request.user.company

    # Only proceed with the search if there is a query
    if query:
        skus = SKU.objects.filter(company=company, name__icontains=query)
        sku_data = [{'id': sku.id, 'name': sku.name, 'sku_code': sku.sku_code} for sku in skus]
    else:
        sku_data = []  # Return an empty list if there is no query

    return JsonResponse(sku_data, safe=False)




RFP_SKUFormSet = inlineformset_factory(RFP, RFP_SKUs, fields=('sku',), extra=1)


@login_required
def create_rfp_step2(request, rfp_id):
    rfp = get_object_or_404(RFP, id=rfp_id)

    if request.method == 'POST':
        sku_ids = request.POST.getlist('skus[]')
        extra_columns_data = request.POST.get('extra_columns_data')
        extra_columns_json = json.loads(extra_columns_data) if extra_columns_data else []

        for sku_data in extra_columns_json:
            sku_id = sku_data['sku_id']
            sku = get_object_or_404(SKU, id=sku_id)
            rfp_sku = RFP_SKUs.objects.create(rfp=rfp, sku=sku)

            # Convert dataArray back into a dictionary, maintaining order
            data_ordered = OrderedDict(sku_data['data'])
            rfp_sku.set_extra_data(data_ordered)

            rfp_sku.save()

        return redirect('create_rfp_step3', rfp_id=rfp.id)

    sku_search_form = SKUSearchForm()

    return render(request, 'procurement01/create_rfp_step2.html', {
        'rfp': rfp,
        'sku_search_form': sku_search_form,
    })



@login_required
def create_rfp_step3(request, rfp_id):
    # Get the RFP instance
    rfp = get_object_or_404(RFP, id=rfp_id)

    if GeneralQuestion.objects.filter(rfp=rfp):
        extra_forms = 0
    else:
        extra_forms = 1


    # Create a formset for handling multiple GeneralQuestion instances
    GeneralQuestionFormSet = modelformset_factory(GeneralQuestion, form=GeneralQuestionForm, extra=extra_forms, can_delete=True)

    # If the form is submitted
    if request.method == 'POST':
        formset = GeneralQuestionFormSet(request.POST, queryset=GeneralQuestion.objects.filter(rfp=rfp))

        # Validate the formset
        if formset.is_valid():
            # Process each form in the formset
            instances = formset.save(commit=False)
            for instance in instances:
                # Link the question to the RFP
                instance.rfp = rfp
                instance.save()  # Save the instance to the database
            
            # Delete any questions marked for deletion
            for deleted_instance in formset.deleted_objects:
                deleted_instance.delete()
            
            # After saving, redirect to the next step (Step 4)
            return redirect('create_rfp_step4', rfp_id=rfp.id)
            

    # If the form is not submitted, display the existing questions
    else:
        formset = GeneralQuestionFormSet(queryset=GeneralQuestion.objects.filter(rfp=rfp))

    return render(request, 'procurement01/create_rfp_step3.html', {
        'rfp': rfp,
        'formset': formset,
    })


@login_required
def create_rfp_step4(request, rfp_id):
    # Get the RFP instance
    rfp = get_object_or_404(RFP, id=rfp_id)
    
    # Fetch all RFP_SKUs associated with this RFP
    rfp_skus = RFP_SKUs.objects.filter(rfp=rfp)

    # Process SKUs to pass to the template
    processed_skus = []
    extra_columns = []

    for rfp_sku in rfp_skus:
        extra_data = rfp_sku.get_extra_data()
        if not extra_columns:
            extra_columns = list(extra_data.keys())  # Store the keys only once from the first SKU
            print(extra_data)
            print(extra_columns)
        processed_skus.append({
            'sku_id': rfp_sku.id,
            'sku_name': rfp_sku.sku.name,
            'extra_data': extra_data,
        })
        print(processed_skus)

    # Handle form submission
    if request.method == 'POST':
        # Retrieve the JSON data for sku_specific_data from the form
        sku_specific_data = request.POST.get('sku_specific_data')
        questions_data = json.loads(sku_specific_data) if sku_specific_data else []

        # Clear any existing SKU-specific questions for this RFP to prevent duplicates
        SKUSpecificQuestion.objects.filter(rfp=rfp).delete()

        # Save each question once for this RFP
        for question_data in questions_data:
            SKUSpecificQuestion.objects.create(
                rfp=rfp,
                question=question_data['question'],
                question_type=question_data['question_type']
            )

        # Redirect to the next step
            
        return redirect('create_rfp_step5', rfp_id=rfp.id)

    # Pass context to the template
    context = {
        'rfp': rfp,
        'extra_columns': extra_columns,
        'processed_skus': processed_skus,
        'question_types': SKUSpecificQuestion.QUESTION_TYPES,
    }
    return render(request, 'procurement01/create_rfp_step4.html', context)


@login_required
def view_rfp_skus(request, rfp_id):
    rfp = get_object_or_404(RFP, id=rfp_id)
    rfp_skus = RFP_SKUs.objects.filter(rfp=rfp)
    
    processed_skus = []
    extra_columns = []

    for rfp_sku in rfp_skus:
        extra_data = rfp_sku.get_extra_data()  # This should return the JSON data in the original order
        print(extra_data)
        if not extra_columns:
            # Collect columns based on the first SKU's extra data keys in order
            extra_columns = list(extra_data.keys())
            print(extra_columns)
        processed_skus.append({
            'sku_name': rfp_sku.sku.name,
            'extra_data': extra_data,
        })
        print(processed_skus)
    
    context = {
        'rfp': rfp,
        'extra_columns': extra_columns,
        'processed_skus': processed_skus,
    }
    print(context)
    return render(request, 'procurement01/view_rfp_skus.html', context)


    

@login_required
def rfp_list_view(request):
    rfps = RFP.objects.all()  # You might want to filter by the user's company if needed
    return render(request, 'procurement01/rfp_list.html', {'rfps': rfps})




@login_required
def create_rfp_step2a(request, rfp_id):
    rfp = get_object_or_404(RFP, id=rfp_id)

    if request.method == 'POST':
        sku_ids = request.POST.getlist('skus[]')
        extra_columns_data = request.POST.get('extra_columns_data')
        extra_columns_json = json.loads(extra_columns_data) if extra_columns_data else []

        for sku_data in extra_columns_json:
            sku_id = sku_data['sku_id']
            sku = get_object_or_404(SKU, id=sku_id)
            rfp_sku = RFP_SKUs.objects.create(rfp=rfp, sku=sku)

            # Convert dataArray back into a dictionary, maintaining order
            data_ordered = OrderedDict(sku_data['data'])
            rfp_sku.set_extra_data(data_ordered)

            rfp_sku.save()

        return redirect('create_rfp_step3', rfp_id=rfp.id)

    sku_search_form = SKUSearchForm()

    return render(request, 'procurement01/create_rfp_step2a.html', {
        'rfp': rfp,
        'sku_search_form': sku_search_form,
    })


from django.views.decorators.http import require_POST

@login_required
@csrf_exempt  # Note: CSRF is disabled here since we are handling API calls, but keep in mind the security implications.
@require_POST
def create_sku(request):
    try:
        # Get the current user
        user = request.user
        if not user.is_procurer:
            return JsonResponse({'success': False, 'error': 'Only procurers can create SKUs.'}, status=403)

        # Parse the request data
        data = json.loads(request.body.decode('utf-8'))
        sku_name = data.get('name', '').strip()

        if not sku_name:
            return JsonResponse({'success': False, 'error': 'SKU name cannot be empty.'}, status=400)

        # Check if SKU with the same name exists for the company
        company = user.company
        if SKU.objects.filter(name=sku_name, company=company).exists():
            return JsonResponse({'success': False, 'error': 'SKU with this name already exists.'}, status=400)

        # Create a new SKU
        new_sku = SKU.objects.create(name=sku_name, company=company, sku_code=f'{sku_name.upper()}-{company.id}')
        
        return JsonResponse({'success': True, 'sku_id': new_sku.id, 'sku_name': new_sku.name})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@login_required
def create_rfp_step5(request, rfp_id):
    rfp = get_object_or_404(RFP, id=rfp_id)

    # Initialize the GeneralQuestionFormSet
    GeneralQuestionFormSet = modelformset_factory(
        GeneralQuestion, form=GeneralQuestionForm, extra=0, can_delete=True
    )

    if request.method == 'POST':
        with transaction.atomic():
            # Process RFP Basic Information Form
            rfp_form = RFPBasicForm(request.POST, instance=rfp)
            rfp_form_valid = rfp_form.is_valid()

            # Process General Questions FormSet
            general_questions_formset = GeneralQuestionFormSet(
                request.POST, queryset=GeneralQuestion.objects.filter(rfp=rfp)
            )
            general_questions_formset_valid = general_questions_formset.is_valid()

            if rfp_form_valid and general_questions_formset_valid:
                # Save RFP Basic Information
                rfp = rfp_form.save()

                # Handle file deletions
                files_to_delete = request.POST.getlist('delete_files')
                if files_to_delete:
                    RFPFile.objects.filter(id__in=files_to_delete, rfp=rfp).delete()

                # Handle new file uploads
                for file in request.FILES.getlist('new_files'):
                    RFPFile.objects.create(rfp=rfp, file=file)

                # Save General Questions
                general_questions = general_questions_formset.save(commit=False)
                for question in general_questions:
                    question.rfp = rfp
                    question.save()
                # Delete any questions marked for deletion
                for deleted_question in general_questions_formset.deleted_objects:
                    deleted_question.delete()

                # Process SKUs and Extra Data
                # Get existing SKUs associated with the RFP
                existing_sku_ids = set(
                    RFP_SKUs.objects.filter(rfp=rfp).values_list('sku_id', flat=True)
                )

                # Get SKU IDs from the form
                sku_ids = request.POST.getlist('skus[]')
                submitted_sku_ids = set(int(sku_id) for sku_id in sku_ids)

                # Remove SKUs that are no longer in the form
                skus_to_remove = existing_sku_ids - submitted_sku_ids
                RFP_SKUs.objects.filter(rfp=rfp, sku_id__in=skus_to_remove).delete()

                # Update or create RFP_SKUs and their extra data
                extra_columns_data = request.POST.get('extra_columns_data')
                extra_columns_json = json.loads(extra_columns_data) if extra_columns_data else []

                for sku_data in extra_columns_json:
                    sku_id = sku_data['sku_id']
                    sku = get_object_or_404(SKU, id=sku_id)
                    rfp_sku, _ = RFP_SKUs.objects.get_or_create(rfp=rfp, sku=sku)
                    # Convert dataArray back into an ordered dictionary
                    data_ordered = OrderedDict(sku_data['data'])
                    rfp_sku.set_extra_data(data_ordered)
                    rfp_sku.save()

                # Process SKU-Specific Questions
                # Remove existing SKU-specific questions
                SKUSpecificQuestion.objects.filter(rfp=rfp).delete()

                # Add new SKU-specific questions
                sku_specific_data = request.POST.get('sku_specific_data')
                sku_specific_json = json.loads(sku_specific_data) if sku_specific_data else []

                for question_data in sku_specific_json:
                    SKUSpecificQuestion.objects.create(
                        rfp=rfp,
                        question=question_data['question'],
                        question_type=question_data['question_type']
                    )

                # Finalize RFP and redirect to RFP list or a success page
                return redirect('invite_suppliers', rfp_id=rfp.id)

            else:
                # If forms are invalid, re-render the page with errors
                existing_files = rfp.files.all()
                rfp_skus = RFP_SKUs.objects.filter(rfp=rfp)
                processed_skus = []
                extra_columns = []

                for rfp_sku in rfp_skus:
                    extra_data = rfp_sku.get_extra_data()
                    if not extra_columns:
                        extra_columns = list(extra_data.keys())
                    processed_skus.append({
                        'sku_id': rfp_sku.sku.id,
                        'sku_name': rfp_sku.sku.name,
                        'extra_data': extra_data,
                    })

                sku_specific_questions = SKUSpecificQuestion.objects.filter(rfp=rfp)

                context = {
                    'rfp': rfp,
                    'rfp_form': rfp_form,
                    'existing_files': existing_files,
                    'general_questions_formset': general_questions_formset,
                    'extra_columns': extra_columns,
                    'processed_skus': processed_skus,
                    'sku_specific_questions': sku_specific_questions,
                }

                return render(request, 'procurement01/create_rfp_step5.html', context)

    else:
        # Handle GET request
        rfp_form = RFPBasicForm(instance=rfp)
        existing_files = rfp.files.all()

        # Initialize the General Questions FormSet with existing questions
        general_questions_formset = GeneralQuestionFormSet(
            queryset=GeneralQuestion.objects.filter(rfp=rfp)
        )

        # Prepare SKUs and Extra Data for the template
        rfp_skus = RFP_SKUs.objects.filter(rfp=rfp)
        processed_skus = []
        extra_columns = []

        for rfp_sku in rfp_skus:
            extra_data = rfp_sku.get_extra_data()
            if not extra_columns and extra_data:
                extra_columns = list(extra_data.keys())
            processed_skus.append({
                'sku_id': rfp_sku.sku.id,
                'sku_name': rfp_sku.sku.name,
                'extra_data': extra_data,
            })

        # Get existing SKU-specific questions
        sku_specific_questions = SKUSpecificQuestion.objects.filter(rfp=rfp)

        context = {
            'rfp': rfp,
            'rfp_form': rfp_form,
            'existing_files': existing_files,
            'general_questions_formset': general_questions_formset,
            'extra_columns': extra_columns,
            'processed_skus': processed_skus,
            'sku_specific_questions': sku_specific_questions,
        }

        return render(request, 'procurement01/create_rfp_step5.html', context)



def send_invitation_email(invitation):
    subject = f"Invitation to respond to RFP: {invitation.rfp.title}"
    invitation_link = settings.SITE_URL + reverse('supplier_rfp_response', args=[invitation.token])
    message = f"""
    Dear {invitation.supplier.name},

    You have been invited to respond to the RFP titled "{invitation.rfp.title}".

    Please click the link below to view the RFP and submit your response:

    {invitation_link}

    Best regards,
    {invitation.rfp.title}
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [invitation.supplier.email],
        fail_silently=False,
    )


@login_required
def invite_suppliers(request, rfp_id):
    rfp = get_object_or_404(RFP, id=rfp_id)

    if not request.user.is_procurer:
        return render(request, 'procurement01/access_denied.html')

    if request.method == 'POST':
        supplier_ids = request.POST.getlist('suppliers')
        for supplier_id in supplier_ids:
            supplier = Company.objects.get(id=supplier_id)
            # Create an invitation for each supplier
            invitation, created = RFPInvitation.objects.get_or_create(rfp=rfp, supplier=supplier)
            if created:
                # Send invitation email
                print('sending email')
                send_invitation_email(invitation)
                print('sent email')
        return redirect('rfp_list')  # Redirect to the RFP list or appropriate page

    else:
        # Get suppliers associated with this procurer
        procurer_company = request.user.company
        suppliers = Company.objects.filter(procurer=procurer_company, company_type='Supplier')
        return render(request, 'procurement01/invite_suppliers.html', {
            'rfp': rfp,
            'suppliers': suppliers,
        })



def supplier_rfp_response(request, token):
    invitation = get_object_or_404(RFPInvitation, token=token)

    if invitation.expires_at and timezone.now() > invitation.expires_at:
        return render(request, 'procurement01/expired_invitation.html')

    if invitation.responded_at:
        return render(request, 'procurement01/already_responded.html')

    rfp = invitation.rfp
    general_questions = GeneralQuestion.objects.filter(rfp=rfp)
    sku_specific_questions = SKUSpecificQuestion.objects.filter(rfp=rfp)
    rfp_skus = RFP_SKUs.objects.filter(rfp=rfp)

    processed_skus = []
    extra_columns = []

    for rfp_sku in rfp_skus:
        extra_data = rfp_sku.get_extra_data()
        if extra_data:
            extra_columns = list(extra_data.keys())
        processed_skus.append({
            'sku_id': rfp_sku.sku.id,
            'sku_name': rfp_sku.sku.name,
            'extra_data': extra_data,
        })

    # Prepare options lists for questions
    for question in general_questions:
        if question.question_type in ['Single-select', 'Multi-select']:
            question.options_list = [option.strip() for option in question.multiple_choice_options.split(',')]

    for sku_question in sku_specific_questions:
        if sku_question.question_type in ['Single-select', 'Multi-select']:
            sku_question.options_list = [option.strip() for option in sku_question.multiple_choice_options.split(',')]

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create SupplierResponse record
                supplier_response = SupplierResponse.objects.create(
                    rfp=rfp,
                    supplier=invitation.supplier,
                    is_finalized=True
                )

                # Save general question responses
                for question in general_questions:
                    field_name = f'general_{question.id}'
                    file = request.FILES.get(field_name)

                    if question.question_type == 'text':
                        answer_text = request.POST.get(field_name)
                        answer_choice = None
                    elif question.question_type == 'Single-select':
                        answer_choice = request.POST.get(field_name)
                        answer_text = None
                    elif question.question_type == 'Multi-select':
                        selected_options = request.POST.getlist(field_name)
                        answer_choice = ','.join(selected_options)
                        answer_text = None
                    elif question.question_type == 'File upload':
                        answer_text = None
                        answer_choice = None
                    else:
                        answer_text = None
                        answer_choice = None

                    GeneralQuestionResponse.objects.create(
                        response=supplier_response,
                        question=question,
                        invitation=invitation,
                        answer_text=answer_text,
                        answer_choice=answer_choice,
                        answer_file=file if question.question_type == 'File upload' else None
                    )

                # Save SKU-specific question responses
                for sku in processed_skus:
                    for sku_question in sku_specific_questions:
                        field_name = f'sku_{sku["sku_id"]}_{sku_question.id}'
                        file = request.FILES.get(field_name)
                        answer = request.POST.get(field_name)

                        if sku_question.question_type == 'text':
                            answer_text = answer
                            answer_number = None
                            answer_date = None
                            answer_file = None
                            answer_choice = None
                        elif sku_question.question_type == 'number':
                            try:
                                answer_number = Decimal(answer)
                            except (InvalidOperation, TypeError):
                                answer_number = None
                            answer_text = None
                            answer_date = None
                            answer_file = None
                            answer_choice = None
                        elif sku_question.question_type == 'date':
                            try:
                                answer_date = datetime.strptime(answer, '%Y-%m-%d').date()
                            except (ValueError, TypeError):
                                answer_date = None
                            answer_text = None
                            answer_number = None
                            answer_file = None
                            answer_choice = None
                        elif sku_question.question_type == 'file':
                            answer_file = file
                            answer_text = None
                            answer_number = None
                            answer_date = None
                            answer_choice = None
                        elif sku_question.question_type == 'Single-select':
                            answer_choice = request.POST.get(field_name)
                            answer_text = None
                            answer_number = None
                            answer_date = None
                            answer_file = None
                        elif sku_question.question_type == 'Multi-select':
                            selected_options = request.POST.getlist(field_name)
                            answer_choice = ','.join(selected_options)
                            answer_text = None
                            answer_number = None
                            answer_date = None
                            answer_file = None
                        else:
                            answer_text = None
                            answer_number = None
                            answer_date = None
                            answer_file = None
                            answer_choice = None

                        SKUSpecificQuestionResponse.objects.create(
                            response=supplier_response,
                            rfp_sku=RFP_SKUs.objects.get(rfp=rfp, sku__id=sku["sku_id"]),
                            question=sku_question,
                            answer_text=answer_text,
                            answer_number=answer_number,
                            answer_file=answer_file,
                            answer_date=answer_date,
                            answer_choice=answer_choice,
                        )

                # Mark the invitation as responded
                invitation.responded_at = timezone.now()
                invitation.is_accepted = True
                invitation.save()

                return redirect('supplier_thank_you')
        except Exception as e:
            print("Exception occurred:", e)
            return render(request, 'procurement01/error.html', {'message': str(e)})

    return render(request, 'procurement01/supplier_rfp_response.html', {
        'rfp': rfp,
        'invitation': invitation,
        'general_questions': general_questions,
        'sku_specific_questions': sku_specific_questions,
        'extra_columns': extra_columns,
        'processed_skus': processed_skus,
    })


def supplier_thank_you(request):
    # Retrieve the RFP title from the session if it's been passed through.
    rfp_title = request.session.get('rfp_title', 'the RFP')

    # Clear the RFP title from the session after displaying it
    if 'rfp_title' in request.session:
        del request.session['rfp_title']

    return render(request, 'procurement01/supplier_thank_you.html', {'rfp_title': rfp_title})




@login_required
def general_question_analysis(request, rfp_id):
    rfp = get_object_or_404(RFP, id=rfp_id)
    # Get all general questions for the RFP
    general_questions = GeneralQuestion.objects.filter(rfp=rfp)
    
    # Get all supplier responses for the RFP
    supplier_responses = SupplierResponse.objects.filter(rfp=rfp)
    
    # Get all general question responses for these supplier responses
    general_question_responses = GeneralQuestionResponse.objects.filter(
        response__in=supplier_responses
    )

     # Build a dictionary of responses: {question_id: {supplier_response_id: response}}
    responses_dict = {}
    for gq_response in general_question_responses:
        question_id = gq_response.question.id
        supplier_response_id = gq_response.response.id
        if question_id not in responses_dict:
            responses_dict[question_id] = {}
        responses_dict[question_id][supplier_response_id] = gq_response

    context = {
        "rfp": rfp,
        "general_questions": general_questions,
        "supplier_responses": supplier_responses,
        "responses_dict": responses_dict,
    }

    return render(request, 'procurement01/general_question_analysis.html', context)

