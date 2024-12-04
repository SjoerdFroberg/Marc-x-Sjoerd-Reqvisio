from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('skus/', views.sku_list_view, name='sku_list'),
    path('skus/<int:sku_id>/', views.sku_detail_view, name='sku_detail'),
    path('skus/new/', views.sku_create_view, name='sku_create'),

    path('suppliers/', views.supplier_list_view, name='supplier_list'),
    path('suppliers/create/', views.create_supplier_view, name='create_supplier'),

    path('rfx/create/step1/', views.create_rfx_step1, name='create_rfx_step1'),
    path('rfx/create/step1/<int:rfx_id>/', views.create_rfx_step1, name='create_rfx_step1'),  # Optional rfx_id

    path('rfx/create/step2/<int:rfx_id>/', views.create_rfx_step2, name='create_rfx_step2'),
    path('search_skus/', views.search_skus, name='search_skus'),  # Add this line
    
    path('rfx/create/step3/<int:rfx_id>/', views.create_rfx_step3, name='create_rfx_step3'),
    path('rfx/create/step4/<int:rfx_id>/', views.create_rfx_step4, name='create_rfx_step4'),   

    path('rfxs/', views.rfx_list_view, name='rfx_list'),
    path('rfx_detail/<int:rfx_id>/', views.rfx_detail, name = 'rfx_detail'),
    




    path('create_rfx_step2a/<int:rfx_id>/', views.create_rfx_step2a, name='create_rfx_step2a'),
    path('create_sku/', views.create_sku, name='create_sku'),

    path('rfx/create/step5/<int:rfx_id>/', views.create_rfx_step5, name='create_rfx_step5'),  # New step 5 URL
    
    path('rfx/<int:rfx_id>/invite_suppliers/', views.invite_suppliers, name='invite_suppliers'),
    path('respond_rfx/<str:token>/', views.supplier_rfx_response, name='supplier_rfx_response'),
    path('supplierthankyou', views.supplier_thank_you, name = 'supplier_thank_you'),

    path('rfx/<int:rfx_id>/general_question_table/', views.general_question_table_view, name='general_question_table'),
    path('rfx/<int:rfx_id>/sku_specific_question_responses_analysis/', views.sku_specific_question_responses_analysis, name = 'sku_specific_question_responses_analysis'),







]

