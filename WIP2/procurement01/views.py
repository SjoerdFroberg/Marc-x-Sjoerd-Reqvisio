from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, inlineformset_factory, formset_factory
from django.http import JsonResponse, HttpResponseForbidden
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


from django.core.serializers.json import DjangoJSONEncoder






from .models import SKU, Project, Company, RFX, GeneralQuestion, RFX_SKUs,SKUSpecificQuestion, RFXFile, RFXInvitation, SupplierResponse, SKUSpecificQuestionResponse, GeneralQuestionResponse
from .forms import SKUForm, ProjectForm, SupplierForm, RFXBasicForm, SKUSearchForm, GeneralQuestionForm, RFX_SKUForm, RFXForm, SKUSpecificQuestionForm, GeneralQuestionResponseForm, SKUSpecificQuestionResponseForm



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
def project_list_view(request):
    # Get the user's company
    user_company = request.user.company

    # Fetch projects associated with the user's company
    projects = Project.objects.filter(company=user_company)

    context = {
        'projects': projects,
    }
    return render(request, 'procurement01/project_list.html', context)






@login_required
def create_project(request):
    # Ensure the logged-in user has a company
    if not request.user.company:
        return HttpResponseForbidden("You must belong to a company to create a project.")

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # Save the project with the user's company
            project = form.save(commit=False)
            project.company = request.user.company
            project.save()
            # Redirect to the project detail page after creation
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()

    context = {
        'form': form,
    }
    return render(request, 'procurement01/create_project.html', context)


@login_required
def project_detail(request, project_id):
    # Get the project, ensuring it belongs to the user's company
    project = get_object_or_404(Project, id=project_id, company=request.user.company)

    # Get all RFXs associated with this project
    rfxs = RFX.objects.filter(project=project)

    context = {
        'project': project,
        'rfxs': rfxs,
    }
    return render(request, 'procurement01/project_detail.html', context)




@login_required
def create_rfx_step1(request, rfx_id=None):
    if rfx_id:
        rfx = get_object_or_404(RFX, id=rfx_id)
        existing_files = rfx.files.all()  # Fetch existing files
    else:
        rfx = None
        existing_files = None  # Initialize for new RFX


    # Check if there's a project_id in the query parameters
    project_id = request.GET.get('project_id')
    initial_data = {}
    if project_id:
        try:
            # Check if the project belongs to the user's company
            initial_project = Project.objects.get(id=project_id, company=request.user.company)
            initial_data['project'] = initial_project
        except Project.DoesNotExist:
            pass

    

    if request.method == 'POST':
        with transaction.atomic():

            if rfx:
                form = RFXBasicForm(request.POST, request.FILES, instance=rfx, user=request.user, initial=initial_data)
            else:
                form = RFXBasicForm(request.POST, request.FILES, user=request.user, initial=initial_data)

            rfx_form_valid = form.is_valid()

        if rfx_form_valid:
            rfx = form.save()

            # Handle file deletions
            files_to_delete = request.POST.getlist('delete_files')
            if files_to_delete:
                RFXFile.objects.filter(id__in=files_to_delete, rfx=rfx).delete()

            # Handle new file uploads
            for file in request.FILES.getlist('new_files'):
                RFXFile.objects.create(rfx=rfx, file=file)

            return redirect('create_rfx_step2', rfx_id=rfx.id)
        
    else:
        if rfx:
            form = RFXBasicForm(instance=rfx, user=request.user, initial=initial_data)
            existing_files = rfx.files.all()
        else:
            form = RFXBasicForm(user=request.user, initial=initial_data)
            existing_files = None

    return render(request, 'procurement01/create_rfx_step1.html', {
        'form': form,
        'existing_files': existing_files,
        'rfx': rfx,  # Include if needed in the template
    })


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




RFX_SKUFormSet = inlineformset_factory(RFX, RFX_SKUs, fields=('sku',), extra=1)





@login_required
def create_rfx_step2(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)

    if request.method == 'POST':
        with transaction.atomic():
            # Get existing SKUs associated with the RFX
            existing_sku_ids = set(
                RFX_SKUs.objects.filter(rfx=rfx).values_list('sku_id', flat=True)
            )

            # Get SKU IDs from the form
            sku_ids = request.POST.getlist('skus[]')
            submitted_sku_ids = set(int(sku_id) for sku_id in sku_ids)

            # Remove SKUs that are no longer in the form
            skus_to_remove = existing_sku_ids - submitted_sku_ids
            if skus_to_remove:
                RFX_SKUs.objects.filter(rfx=rfx, sku_id__in=skus_to_remove).delete()


            # Update or create RFX_SKUs and their extra data
            extra_columns_data = request.POST.get('extra_columns_data')
            extra_columns_json = json.loads(extra_columns_data) if extra_columns_data else []


            for sku_data in extra_columns_json:
                sku_id = sku_data['sku_id']
                sku = get_object_or_404(SKU, id=sku_id)
                rfx_sku, _ = RFX_SKUs.objects.get_or_create(rfx=rfx, sku=sku)
                data_ordered = OrderedDict(sku_data['data'])
                rfx_sku.set_specification_data(OrderedDict(data_ordered))

            # Get the navigation destination and dynamically construct the redirect URL name
            navigation_destination = request.POST.get('navigation_destination')
            return redirect(f'create_rfx_{navigation_destination}', rfx_id=rfx.id)
    else:
        # Handle GET request: Retrieve existing SKUs
        # Prepare SKUs and Extra Data for the template
        rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)
        processed_skus = []
        extra_columns = []

        for rfx_sku in rfx_skus:
            extra_data = rfx_sku.get_specification_data()
            if not extra_columns and extra_data:
                extra_columns = list(extra_data.keys())
            processed_skus.append({
                'sku_id': rfx_sku.sku.id,
                'sku_name': rfx_sku.sku.name,
                'extra_data': extra_data,
                'extra_columns': extra_columns,

            })
        sku_search_form = SKUSearchForm()

        step = "step2"

        current_step = 2 

        context = {
            'rfx': rfx,
            'sku_search_form': sku_search_form,
            'processed_skus': processed_skus,
            'extra_columns': extra_columns,
            'step': step,
            'current_step': current_step,
        }

        return render(request, 'procurement01/create_rfx_step2.html', context)



@login_required
def create_rfx_step3(request, rfx_id):
    # Get the RFX instance
    rfx = get_object_or_404(RFX, id=rfx_id)

    if GeneralQuestion.objects.filter(rfx=rfx):
        extra_forms = 0
    else:
        extra_forms = 1

    # Initialize the GeneralQuestionFormSet
    GeneralQuestionFormSet = modelformset_factory(
        GeneralQuestion, form=GeneralQuestionForm, extra=extra_forms, can_delete=True
    )

    if request.method == 'POST':
        with transaction.atomic():
            general_questions_formset = GeneralQuestionFormSet(
                request.POST, queryset=GeneralQuestion.objects.filter(rfx=rfx)
            )


            general_questions_formset_valid = general_questions_formset.is_valid()

            

            if general_questions_formset.is_valid():
                # Save the formset (updates and additions)
                general_questions = general_questions_formset.save(commit=False)
                for question in general_questions:
                    print(question)
                    question.rfx = rfx
                    question.save()

                # Handle deletions
                for deleted_question in general_questions_formset.deleted_objects:
                    print(deleted_question)
                    deleted_question.delete()  # This removes the marked object from the DB


            # Get the navigation destination and dynamically construct the redirect URL name
            navigation_destination = request.POST.get('navigation_destination')
            return redirect(f'create_rfx_{navigation_destination}', rfx_id=rfx.id)
    
    else:

        # Initialize the General Questions FormSet with existing questions
        general_questions_formset = GeneralQuestionFormSet(
            queryset=GeneralQuestion.objects.filter(rfx=rfx)
        )
         
        step = "step3"

        context = {
            'rfx': rfx,
            'general_questions_formset': general_questions_formset,
            'step': step

        }

        return render(request, 'procurement01/create_rfx_step3.html', context)

            

@login_required
def create_rfx_step4(request, rfx_id):
    # Get the RFX instance
    rfx = get_object_or_404(RFX, id=rfx_id)

    if request.method == 'POST':
        with transaction.atomic():

            # Process SKUs and Extra Data
            # Get existing SKUs associated with the RFX
            existing_sku_ids = set(
                RFX_SKUs.objects.filter(rfx=rfx).values_list('sku_id', flat=True)
            )

            # Get SKU IDs from the form
            sku_ids = request.POST.getlist('skus[]')
            submitted_sku_ids = set(int(sku_id) for sku_id in sku_ids)

            # Remove SKUs that are no longer in the form
            skus_to_remove = existing_sku_ids - submitted_sku_ids
            RFX_SKUs.objects.filter(rfx=rfx, sku_id__in=skus_to_remove).delete()

            # Update or create RFX_SKUs and their extra data
            extra_columns_data = request.POST.get('extra_columns_data')
            extra_columns_json = json.loads(extra_columns_data) if extra_columns_data else []

            for sku_data in extra_columns_json:
                sku_id = sku_data['sku_id']
                sku = get_object_or_404(SKU, id=sku_id)
                rfx_sku, _ = RFX_SKUs.objects.get_or_create(rfx=rfx, sku=sku)
                # Convert dataArray back into an ordered dictionary
                data_ordered = OrderedDict(sku_data['data'])
                rfx_sku.set_specification_data(OrderedDict(data_ordered))

            # Process SKU-Specific Questions
            # Remove existing SKU-specific questions
            SKUSpecificQuestion.objects.filter(rfx=rfx).delete()

            # Add new SKU-specific questions
            sku_specific_data = request.POST.get('sku_specific_data')
            sku_specific_json = json.loads(sku_specific_data) if sku_specific_data else []

            for question_data in sku_specific_json:
                SKUSpecificQuestion.objects.create(
                    rfx=rfx,
                    question=question_data['question'],
                    question_type=question_data['question_type']
                )
            
            # Get the navigation destination and dynamically construct the redirect URL name
            navigation_destination = request.POST.get('navigation_destination')
            return redirect(f'create_rfx_{navigation_destination}', rfx_id=rfx.id)
    else:
        # Prepare SKUs and Extra Data for the template
        rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)
        processed_skus = []
        extra_columns = []

        for rfx_sku in rfx_skus:
            extra_data = rfx_sku.get_specification_data()

            if not extra_columns and extra_data:
                extra_columns = list(extra_data.keys())
            processed_skus.append({
                'sku_id': rfx_sku.sku.id,
                'sku_name': rfx_sku.sku.name,
                'extra_data': extra_data,
            })

        # Get existing SKU-specific questions
        sku_specific_questions = SKUSpecificQuestion.objects.filter(rfx=rfx)

        step= "step4"

        context = {
            'rfx': rfx,
            'extra_columns': extra_columns,
            'processed_skus': processed_skus,
            'sku_specific_questions': sku_specific_questions,
            'step': step,
        }

        return render(request, 'procurement01/create_rfx_step4.html', context)






@login_required
def create_rfx_step4a(request, rfx_id):
    # Get the RFX instance
    rfx = get_object_or_404(RFX, id=rfx_id)
    
    # Fetch all RFX_SKUs associated with this RFX
    rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)

    # Process SKUs to pass to the template
    processed_skus = []
    extra_columns = []

    for rfx_sku in rfx_skus:
        extra_data = rfx_sku.get_extra_data()
        if not extra_columns:
            extra_columns = list(extra_data.keys())  # Store the keys only once from the first SKU
            print(extra_data)
            print(extra_columns)
        processed_skus.append({
            'sku_id': rfx_sku.id,
            'sku_name': rfx_sku.sku.name,
            'extra_data': extra_data,
        })
        print(processed_skus)

    # Handle form submission
    if request.method == 'POST':
        # Retrieve the JSON data for sku_specific_data from the form
        sku_specific_data = request.POST.get('sku_specific_data')
        questions_data = json.loads(sku_specific_data) if sku_specific_data else []

        # Clear any existing SKU-specific questions for this RFX to prevent duplicates
        SKUSpecificQuestion.objects.filter(rfx=rfx).delete()

        # Save each question once for this RFX
        for question_data in questions_data:
            SKUSpecificQuestion.objects.create(
                rfx=rfx,
                question=question_data['question'],
                question_type=question_data['question_type']
            )

        # Redirect to the next step
            
        return redirect('create_rfx_step5', rfx_id=rfx.id)

    # Pass context to the template
    context = {
        'rfx': rfx,
        'extra_columns': extra_columns,
        'processed_skus': processed_skus,
        'question_types': SKUSpecificQuestion.QUESTION_TYPES,
    }
    return render(request, 'procurement01/create_rfx_step4.html', context)


    
@login_required
def rfx_list_view(request):
    user = request.user  # Get the currently logged-in user
    company = user.company  # Get the user's company

    if company.company_type == 'Procurer':
        # Procurer should see only their own RFXs
        rfxs = RFX.objects.filter(rfx_skus__sku__company=company).distinct()
    
    else:
        # If the user's company type is unknown, show nothing
        rfxs = RFX.objects.none()

    return render(request, 'procurement01/rfx_list.html', {'rfxs': rfxs})


@login_required
def create_rfx_step2a(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)

    if request.method == 'POST':
        sku_ids = request.POST.getlist('skus[]')
        extra_columns_data = request.POST.get('extra_columns_data')
        extra_columns_json = json.loads(extra_columns_data) if extra_columns_data else []

        for sku_data in extra_columns_json:
            sku_id = sku_data['sku_id']
            sku = get_object_or_404(SKU, id=sku_id)
            rfx_sku = RFX_SKUs.objects.create(rfx=rfx, sku=sku)

            # Convert dataArray back into a dictionary, maintaining order
            data_ordered = OrderedDict(sku_data['data'])
            rfx_sku.set_extra_data(data_ordered)

            rfx_sku.save()

        return redirect('create_rfx_step3', rfx_id=rfx.id)

    sku_search_form = SKUSearchForm()

    return render(request, 'procurement01/create_rfx_step2a.html', {
        'rfx': rfx,
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
def create_rfx_step5(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)

    # Initialize the GeneralQuestionFormSet
    GeneralQuestionFormSet = modelformset_factory(
        GeneralQuestion, form=GeneralQuestionForm, extra=0, can_delete=True
    )

    if request.method == 'POST':
        with transaction.atomic():
            # Process RFX Basic Information Form
            rfx_form = RFXBasicForm(request.POST, instance=rfx)
            rfx_form_valid = rfx_form.is_valid()

            # Process General Questions FormSet
            general_questions_formset = GeneralQuestionFormSet(
                request.POST, queryset=GeneralQuestion.objects.filter(rfx=rfx)
            )
            general_questions_formset_valid = general_questions_formset.is_valid()

            if rfx_form_valid and general_questions_formset_valid:
                # Save RFX Basic Information
                rfx = rfx_form.save()

                # Handle file deletions
                files_to_delete = request.POST.getlist('delete_files')
                if files_to_delete:
                    RFXFile.objects.filter(id__in=files_to_delete, rfx=rfx).delete()

                # Handle new file uploads
                for file in request.FILES.getlist('new_files'):
                    RFXFile.objects.create(rfx=rfx, file=file)

                # Save General Questions
                general_questions = general_questions_formset.save(commit=False)
                for question in general_questions:
                    question.rfx = rfx
                    question.save()
                # Delete any questions marked for deletion
                for deleted_question in general_questions_formset.deleted_objects:
                    deleted_question.delete()
                    print('deleted')

                # Process SKUs and Extra Data
                # Get existing SKUs associated with the RFX
                existing_sku_ids = set(
                    RFX_SKUs.objects.filter(rfx=rfx).values_list('sku_id', flat=True)
                )

                # Get SKU IDs from the form
                sku_ids = request.POST.getlist('skus[]')
                submitted_sku_ids = set(int(sku_id) for sku_id in sku_ids)

                # Remove SKUs that are no longer in the form
                skus_to_remove = existing_sku_ids - submitted_sku_ids
                RFX_SKUs.objects.filter(rfx=rfx, sku_id__in=skus_to_remove).delete()

                
                # Update or create RFX_SKUs and their extra data
                extra_columns_data = request.POST.get('extra_columns_data')
                extra_columns_json = json.loads(extra_columns_data) if extra_columns_data else []

                for sku_data in extra_columns_json:
                    sku_id = sku_data['sku_id']
                    sku = get_object_or_404(SKU, id=sku_id)
                    rfx_sku, _ = RFX_SKUs.objects.get_or_create(rfx=rfx, sku=sku)
                    # Convert dataArray back into an ordered dictionary
                    data_ordered = OrderedDict(sku_data['data'])
                    rfx_sku.set_specification_data(OrderedDict(data_ordered))


                # Process SKU-Specific Questions
                # Remove existing SKU-specific questions
                SKUSpecificQuestion.objects.filter(rfx=rfx).delete()

                # Add new SKU-specific questions
                sku_specific_data = request.POST.get('sku_specific_data')
                sku_specific_json = json.loads(sku_specific_data) if sku_specific_data else []

                for question_data in sku_specific_json:
                    SKUSpecificQuestion.objects.create(
                        rfx=rfx,
                        question=question_data['question'],
                        question_type=question_data['question_type']
                )

                    
                # Finalize RFX and redirect to RFX list or a success page
                navigation_destination = request.POST.get('navigation_destination')
                if navigation_destination == 'step4':
                    return redirect(f'create_rfx_{navigation_destination}', rfx_id=rfx.id)
                else:
                    return redirect( 'invite_suppliers', rfx_id=rfx.id)

            else:
                # If forms are invalid, re-render the page with errors
                existing_files = rfx.files.all()
                rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)
                processed_skus = []
                extra_columns = []

                

                for rfx_sku in rfx_skus:
                    # Retrieve specification data using the `get_specification_data` method
                    specification_data = rfx_sku.get_specification_data()
                    
                    if not extra_columns and specification_data:
                        # Populate extra_columns only if it's empty and specification data exists
                        extra_columns = list(specification_data.keys())
                    
                    # Append the SKU data and its specification data
                    processed_skus.append({
                        'sku_id': rfx_sku.sku.id,
                        'sku_name': rfx_sku.sku.name,
                        'extra_data': specification_data,  # Ensure the same key is used as in Step 4
                    })

                sku_specific_questions = SKUSpecificQuestion.objects.filter(rfx=rfx)

                context = {
                    'rfx': rfx,
                    'rfx_form': rfx_form,
                    'existing_files': existing_files,
                    'general_questions_formset': general_questions_formset,
                    'extra_columns': extra_columns,
                    'processed_skus': processed_skus,
                    'sku_specific_questions': sku_specific_questions,
                }

                return render(request, 'procurement01/create_rfx_step5.html', context)

    else:
        # Handle GET request
        rfx_form = RFXBasicForm(instance=rfx)
        existing_files = rfx.files.all()

        # Initialize the General Questions FormSet with existing questions
        general_questions_formset = GeneralQuestionFormSet(
            queryset=GeneralQuestion.objects.filter(rfx=rfx)
        )

        # Prepare SKUs and Extra Data for the template
        rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)
        processed_skus = []
        extra_columns = []

        
        for rfx_sku in rfx_skus:
            # Retrieve specification data using the `get_specification_data` method
            specification_data = rfx_sku.get_specification_data()
            
            if not extra_columns and specification_data:
                # Populate extra_columns only if it's empty and specification data exists
                extra_columns = list(specification_data.keys())
            
            # Append the SKU data and its specification data
            processed_skus.append({
                'sku_id': rfx_sku.sku.id,
                'sku_name': rfx_sku.sku.name,
                'extra_data': specification_data,  # Ensure the same key is used as in Step 4
            })


        # Get existing SKU-specific questions
        sku_specific_questions = SKUSpecificQuestion.objects.filter(rfx=rfx)

        context = {
            'rfx': rfx,
            'rfx_form': rfx_form,
            'existing_files': existing_files,
            'general_questions_formset': general_questions_formset,
            'extra_columns': extra_columns,
            'processed_skus': processed_skus,
            'sku_specific_questions': sku_specific_questions,
        }

        return render(request, 'procurement01/create_rfx_step5.html', context)



def send_invitation_email(invitation):
    subject = f"Invitation to respond to RFX: {invitation.rfx.title}"
    invitation_link = settings.SITE_URL + reverse('supplier_rfx_response', args=[invitation.token])
    message = f"""
    Dear {invitation.supplier.name},

    You have been invited to respond to the RFX titled "{invitation.rfx.title}".

    Please click the link below to view the RFX and submit your response:

    {invitation_link}

    Best regards,
    {invitation.rfx.title}
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [invitation.supplier.email],
        fail_silently=False,
    )


@login_required
def invite_suppliers(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)

    if not request.user.is_procurer:
        return render(request, 'procurement01/access_denied.html')

    if request.method == 'POST':
        supplier_ids = request.POST.getlist('suppliers')
        for supplier_id in supplier_ids:
            supplier = Company.objects.get(id=supplier_id)
            # Create an invitation for each supplier
            invitation, created = RFXInvitation.objects.get_or_create(rfx=rfx, supplier=supplier)
            if created:
                # Send invitation email
                print('sending email')
                send_invitation_email(invitation)
                print('sent email')
        return redirect('rfx_list')  # Redirect to the RFX list or appropriate page

    else:
        # Get suppliers associated with this procurer
        procurer_company = request.user.company
        suppliers = Company.objects.filter(procurer=procurer_company, company_type='Supplier')
        return render(request, 'procurement01/invite_suppliers.html', {
            'rfx': rfx,
            'suppliers': suppliers,
        })



def supplier_rfx_response(request, token):
    invitation = get_object_or_404(RFXInvitation, token=token)

    if invitation.expires_at and timezone.now() > invitation.expires_at:
        return render(request, 'procurement01/expired_invitation.html')

    if invitation.responded_at:
        return render(request, 'procurement01/already_responded.html')

    rfx = invitation.rfx
    general_questions = GeneralQuestion.objects.filter(rfx=rfx)
    sku_specific_questions = SKUSpecificQuestion.objects.filter(rfx=rfx)
    rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)

    processed_skus = []
    extra_columns = []

    for rfx_sku in rfx_skus:
        # Retrieve specification data using the `get_specification_data` method
        specification_data = rfx_sku.get_specification_data()
        
        if not extra_columns and specification_data:
            # Populate extra_columns only if it's empty and specification data exists
            extra_columns = list(specification_data.keys())
        
        # Append the SKU data and its specification data
        processed_skus.append({
            'sku_id': rfx_sku.sku.id,
            'sku_name': rfx_sku.sku.name,
            'extra_data': specification_data,  # Ensure the same key is used as in Step 4
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
                    rfx=rfx,
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
                            rfx_sku=RFX_SKUs.objects.get(rfx=rfx, sku__id=sku["sku_id"]),
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

    return render(request, 'procurement01/supplier_rfx_response.html', {
        'rfx': rfx,
        'invitation': invitation,
        'general_questions': general_questions,
        'sku_specific_questions': sku_specific_questions,
        'extra_columns': extra_columns,
        'processed_skus': processed_skus,
    })


def supplier_thank_you(request):
    # Retrieve the RFX title from the session if it's been passed through.
    rfx_title = request.session.get('rfx_title', 'the RFX')

    # Clear the RFX title from the session after displaying it
    if 'rfx_title' in request.session:
        del request.session['rfx_title']

    return render(request, 'procurement01/supplier_thank_you.html', {'rfx_title': rfx_title})






def general_question_table_view(request, rfx_id):
    rfx = get_object_or_404(RFX, id=rfx_id)
    general_questions = GeneralQuestion.objects.filter(rfx=rfx)
    supplier_responses = SupplierResponse.objects.filter(rfx=rfx)
    response_data = {}

    for response in supplier_responses:
        for gq_response in response.general_responses.all():
            question_id = gq_response.question.id
            supplier_id = response.supplier.id
            if question_id not in response_data:
                response_data[question_id] = {}
            response_data[question_id][supplier_id] = gq_response

    context = {
        "rfx": rfx,
        "general_questions": general_questions,
        "supplier_responses": supplier_responses,
        "response_data": response_data,
        "multi_choice_types": ['Single-select', 'Multi-select'],  # Add this
    }
    print(response_data)

    return render(request, 'procurement01/general_question_table.html', context)




@login_required
def sku_specific_question_responses_analysis(request, rfx_id):
    # Step 1: Fetch the RFX instance
    rfx = get_object_or_404(RFX, id=rfx_id)

    # Step 2: Retrieve RFX_SKUs with extra data
    rfx_skus = RFX_SKUs.objects.filter(rfx=rfx)
    processed_skus = []
    extra_columns = []

    for rfx_sku in rfx_skus:
        # Retrieve specification data using the `get_specification_data` method
        specification_data = rfx_sku.get_specification_data()
        
        if not extra_columns and specification_data:
            # Populate extra_columns only if it's empty and specification data exists
            extra_columns = list(specification_data.keys())
        
        # Append the SKU data and its specification data
        processed_skus.append({
            'sku_id': rfx_sku.sku.id,
            'sku_name': rfx_sku.sku.name,
            'extra_data': specification_data,  
        })

    # Step 3: Retrieve SKU-specific questions for the RFX
    sku_specific_questions = SKUSpecificQuestion.objects.filter(rfx=rfx)

    # Step 4: Retrieve supplier responses for SKU-specific questions
    supplier_responses = SupplierResponse.objects.filter(rfx=rfx)
    sku_question_responses = SKUSpecificQuestionResponse.objects.filter(
        response__in=supplier_responses
    )

    # Step 5: Build a response mapping: {(supplier_id, sku_id, question_id): response_data}
    response_lookup = {}
    for response in sku_question_responses:
        key = f"{response.response.supplier.id}_{response.rfx_sku.sku.id}_{response.question.id}"
        response_lookup[key] = {
            'text': response.answer_text,
            'number': response.answer_number,
            'file': response.answer_file.url if response.answer_file else None,
            'date': response.answer_date,
            'choice': response.answer_choice,
        }

    # **Updated Step 6: Handle selected questions**
    selected_question_ids = request.GET.getlist('question_ids[]')

    if 'question_ids[]' not in request.GET:
        # Default to all questions when parameter is not present (initial page load)
        selected_question_ids = [str(q.id) for q in sku_specific_questions]
    else:
        # Remove any empty strings from the list (e.g., when deselecting all)
        selected_question_ids = [qid for qid in selected_question_ids if qid]

    selected_questions = sku_specific_questions.filter(id__in=selected_question_ids)

    # Prepare data for the modal checkboxes (if needed)
    sku_specific_questions_data = [
        {
            "value": str(question.id),
            "label": question.question.replace('"', '\\"').replace('\\\\"', '"'),  # Escape double quotes for JSON
            "selected": str(question.id) in selected_question_ids
        }
        for question in sku_specific_questions
    ]

    # Prepare context for the template
    context = {
        'rfx': rfx,
        'processed_skus': processed_skus,
        'extra_columns': extra_columns,
        'sku_specific_questions': sku_specific_questions,
        'selected_questions': selected_questions,
        'selected_question_ids': selected_question_ids,  # For template
        'supplier_responses': supplier_responses,
        'response_lookup': response_lookup,
        "multi_choice_types": ['Single-select', 'Multi-select'],  # For handling response types
        "sku_specific_questions_json": json.dumps(sku_specific_questions_data, cls=DjangoJSONEncoder),
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Render only the table
        table_html = render_to_string('procurement01/sku_specific_question_table.html', context, request=request)
        return JsonResponse({'table_html': table_html})
    else:
        # Render the full page
        return render(request, 'procurement01/sku_specific_question_responses_analysis.html', context)


@login_required
def rfx_detail(request, rfx_id):
    # Fetch the RFX instance
    rfx = get_object_or_404(RFX, id=rfx_id)

    # Count the number of invitations sent for this RFX
    invitations_sent = rfx.invitations.count()

    # Count the number of responses received for this RFX
    responses_received = rfx.responses.filter(is_finalized=True).count()

    # Pass the data to the template
    context = {
        'rfx': rfx,
        'invitations_sent': invitations_sent,
        'responses_received': responses_received,
    }

    return render(request, 'procurement01/rfx_detail.html', context)