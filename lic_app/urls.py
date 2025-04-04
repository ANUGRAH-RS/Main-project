from django.urls import path
from .views import *

urlpatterns = [
    path('', my_home, name='my_home'),
    path('login', login_view, name='login'),
    path('register-agent/', register_agent, name='register_agent'),
    path('register-user/', register_user, name='register_user'),
    path('check-username/', check_username, name='check_username'),
    path('check-email/', check_email, name='check_email'),
    path('admin_home/', admin_home, name='admin_home'),
    path('agent_home/', agent_home, name='agent_home'),
    path('user_home/', user_home, name='user_home'),
    path('agents/', agent_list, name='agent_list'),
    path('users/', user_list, name='user_list'),
    path('toggle_approval/<int:agent_id>/', toggle_approval, name='toggle_approval'),
    path('logout',user_logout, name='user_logout'),
    path('forgot_password/',forgot_password, name='forgot_password'),
    path('reset_password/<uidb64>/<token>/',reset_password, name='reset_password'),


    #########  User ##########

    path('create-profile/', create_profile, name='create_profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),

    path('purchase_policy_page/', purchase_policy_page, name='purchase_policy_page'),
    path('purchase_policy/', purchase_policy, name='purchase_policy'),

    path('purchased_policies_page/', purchased_policies_page, name='purchased_policies_page'),



    #########  Agent ##########    

    path('add_user/', add_user, name='add_user'),
    path('list_user/', list_user, name='list_user'),
    path('create_policy/', create_policy, name='create_policy'),
    path('list_policy/', list_policy, name='list_policy'),


    path('pol',pol,name="pol"),
    path('sub_policy/<int:sub_id>/', sub_policy_details, name='sub_policy_details'),
    path("manage-policy-plans/", manage_policy_plans, name="manage_policy_plans"),
    path('buy-policy/<int:sub_id>/', buy_policy, name='buy_policy'),

    path('create_head_policy',create_head_policy,name="create_head_policy"),
    path('create_subhead_policy',create_subhead_policy,name="create_subhead_policy"),
    path('add-policy-detail/', add_policy_detail, name='add_policy_detail'),

    path('generate_qr/<int:purchase_id>/', generate_qr_code, name='generate_qr'),
    path('confirm_payment/<int:purchase_id>/', confirm_payment, name='confirm_payment'),

    path("purchases/", purchase_list, name="purchase_list"),


    path("purchase_list_user/", purchase_list_user, name="purchase_list_user"),
    path("policy_details/<int:policy_id>/", policy_details, name="policy_details"),
    path("renew-policy/<int:purchase_id>/", renew_policy, name='renew_policy'),

    # Ensure the parameter name matches the view function
    path('submit_claim/<int:policy_id>/', submit_claim, name='submit_claim'),

    path('admin/claims/', claimlist_admin, name='claimlist_admin'),
    path('admin/claims/update/<int:claim_id>/', update_claim_status, name='update_claim_status'),

    path('my_claim_report/', my_claim_report, name='my_claim_report'),



    path('admin_complaints/', admin_complaints, name='admin_complaints'),
    path('complaints_register/', complaints_register, name='complaints_register'),


    #################################################

    path('financial_report/', financial_report, name='financial_report'),

    path('analytics/', analytics, name='analytics'),

    
]  
