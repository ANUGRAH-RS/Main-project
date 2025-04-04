from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login ,logout
from .models import CustomUser, AgentProfile, UserProfile
from django.contrib import messages

# Check if username exists (AJAX)
def check_username(request):
    username = request.GET.get('username', None)
    exists = CustomUser.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

# Check if email exists (AJAX)
def check_email(request):
    email = request.GET.get('email', None)
    exists = CustomUser.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})

# Agent Registration
def register_agent(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register_agent')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register_agent')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register_agent')

        user = CustomUser.objects.create_user(username=username, email=email, password=password1, role=2)
        agent_profile = AgentProfile.objects.create(user=user, address=address, mobile=mobile)

        messages.success(request, "Agent registered successfully! Wait for admin approval.")
        return redirect('login')

    return render(request, "agent/register_agent.html")


# User Registration
def register_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register_user')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register_user')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register_user')

        user = CustomUser.objects.create_user(username=username, email=email, password=password1, role=3)
        user_profile = UserProfile.objects.create(user=user, address=address, mobile=mobile)

        messages.success(request, "User registered successfully! Please login.")
        return redirect('login')

    return render(request, "user/register_user.html")


def my_home(req):
    policies = MainHead_policy.objects.prefetch_related('sub_policies').all()
    return render(req, 'common/my_home.html', {'policies':policies})


# Forgot and Reste Password 

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(f"/reset_password/{uid}/{token}/")

            # Send reset email
            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_url}",
                from_email=None,  # Use DEFAULT_FROM_EMAIL
                recipient_list=[email],
            )

            messages.success(request, "A password reset link has been sent to your email.")
            return render(request, 'common/forgot_password.html', {'success_message': "A password reset link has been sent to your email."})
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
            return render(request, 'common/forgot_password.html', {'error_message': "No account found with that email."})

    return render(request, 'common/forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password has been reset successfully.")
                return redirect('login')
            else:
                messages.error(request, "Passwords do not match.")
                return redirect(request.path)

        return render(request, 'common/reset_password.html')
    else:
        messages.error(request, "Invalid or expired token.")
        return redirect('forgot_password')


# Login View
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            print(f"Logged in user: {user.username}, Role: {user.role}")  # Debugging line

            if user.role == 2 and not user.agent_profile.approved:
                messages.error(request, "Admin has not approved your account yet.")
                return redirect('login')

            login(request, user)

            # Debugging role-based redirection
            if user.role == 1:
                print("Redirecting to admin_home")
                return redirect('admin_home')
            elif user.role == 2:
                print("Redirecting to agent_home")
                return redirect('agent_home')
            elif user.role == 3:
                print("Redirecting to user_home")
                return redirect('user_home')

        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, "common/login.html")



def admin_home(request):
    return render(request,'admin/admin_home.html')

def agent_home(request):
    return render(request,'agent/agent_home.html')

def user_home(request):
    policies = MainHead_policy.objects.prefetch_related('sub_policies').all()
    return render(request,'user/user_home.html', {'policies': policies})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AgentProfile, UserProfile

@login_required
def agent_list(request):
    agents = AgentProfile.objects.all()
    return render(request, 'admin/agent_list.html', {'agents': agents})

@login_required
def user_list(request):
    users = UserProfile.objects.all()
    return render(request, 'admin/user_list.html', {'users': users})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import AgentProfile

@login_required
def toggle_approval(request, agent_id):
    agent = get_object_or_404(AgentProfile, id=agent_id)
    agent.approved = not agent.approved  # Toggle the approval status
    agent.save()

    if agent.approved:
        messages.success(request, f"Agent {agent.user.username} approved successfully!")
    else:
        messages.warning(request, f"Agent {agent.user.username} unapproved!")

    return redirect('agent_list')  # Redirect back to agent list



#######################################################################


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserData

@login_required
def create_profile(request):
    if request.method == "POST":
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        city = request.POST.get('city')
        country = request.POST.get('country')
        profile_picture = request.FILES.get('profile_picture')

        profile = UserData.objects.create(
            fk_user=request.user,
            location=address,
            phone=mobile,
            city=city,
            country=country,
            profile_picture=profile_picture
        )
        return redirect('user_home')

    return render(request, 'user/create_profile.html')

@login_required
def edit_profile(request):
    user_data, created = UserData.objects.get_or_create(fk_user=request.user)

    print(f"User Data in View: {user_data}")  # Check if user_data exists
    print(f"Address: {user_data.location}, Phone: {user_data.phone}, City: {user_data.city}, Country: {user_data.country}")

    if request.method == "POST":
        user_data.location = request.POST.get('address')
        user_data.phone = request.POST.get('mobile')
        user_data.city = request.POST.get('city')
        user_data.country = request.POST.get('country')

        if 'profile_picture' in request.FILES:
            user_data.profile_picture = request.FILES['profile_picture']

        user_data.save()
        return redirect('user_home')

    return render(request, 'user/edit_profile.html', {'user_data': user_data})


def user_logout(request):
    logout(request)  # Logs out the user and clears the session
    return redirect('login')  # Redirect to the login page or homepage








##############################################################################################




# User Registration
def add_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register_user')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register_user')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register_user')

        user = CustomUser.objects.create_user(username=username, email=email, password=password1, role=3)
        user_profile = UserProfile.objects.create(user=user, address=address, mobile=mobile)

        messages.success(request, "User registered successfully! Please login.")
        return redirect('list_user')

    return render(request, "agent/add_user.html")


from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q
from .models import CustomUser  # Ensure this matches your model import

def list_user(request):
    query = request.GET.get('q')
    users = CustomUser.objects.filter(role=3)

    # Search functionality
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))

    # Pagination
    paginator = Paginator(users, 5)  # Show 5 users per page
    page_number = request.GET.get('page')
    page_users = paginator.get_page(page_number)

    return render(request, 'agent/list_user.html', {'users': page_users, 'query': query})


from .models import *

def create_policy(request):
    if request.method == "POST":
        name = request.POST.get('name')
        policy_type = request.POST.get('policy_type')
        description = request.POST.get('description')
        premium_amount = request.POST.get('premium_amount')
        duration_months = request.POST.get('duration_months')

        InsurancePolicy.objects.create(
            name=name,
            policy_type=policy_type,
            description=description,
            premium_amount=premium_amount,
            duration_months=duration_months,
            fk_user=request.user
        )
        return redirect('list_policy')
    return render(request,'agent/create_policy.html')
    

def list_policy(request):
    policies = InsurancePolicy.objects.filter(fk_user=request.user)  # Fetch only policies of logged-in agent
    return render(request, 'agent/list_policy.html', {'policies': policies})


#####################################################################

from django.shortcuts import render
from .models import InsurancePolicy, PurchasedPolicy

from django.shortcuts import render
from .models import InsurancePolicy, PurchasedPolicy

def purchase_policy_page(request):
    """ Fetch only non-purchased policies for the logged-in user """

    # Get purchased policies as a list of IDs (workaround for Djongo issues)
    purchased_policies = list(PurchasedPolicy.objects.filter(customer=request.user).values_list('policy_id', flat=True))

    # Fetch policies and exclude purchased ones manually
    policies = InsurancePolicy.objects.all()
    available_policies = [policy for policy in policies if policy.id not in purchased_policies]

    return render(request, 'user/purchase_page.html', {
        'policies': available_policies  # ✅ Now only non-purchased policies are passed
    })


def purchase_policy(request):
    if request.method == "POST":
        policy_id = request.POST.get('policy_id')
        amount_paid = request.POST.get('amount_paid')

        policy = get_object_or_404(InsurancePolicy, id=policy_id)
        
        if PurchasedPolicy.objects.filter(customer=request.user, policy=policy).exists():
            return JsonResponse({'error': 'Policy already purchased'}, status=400)

        PurchasedPolicy.objects.create(
            customer=request.user,
            policy=policy,
            amount_paid=amount_paid
        )

        return redirect('user_home')  # ✅ Redirect after purchase

    # **Handle GET request to display policy details**
    policy_id = request.GET.get('policy_id')  # Get policy_id from URL
    policy = None
    if policy_id:
        policy = get_object_or_404(InsurancePolicy, id=policy_id)

    return render(request, 'user/purchase_policy.html', {'policy': policy})  # ✅ Pass policy to template

def purchased_policies_page(request):
    """ Fetch policies purchased by the logged-in user """
    purchased_policies = PurchasedPolicy.objects.filter(customer=request.user)

    return render(request, 'user/purchased_policies.html', {
        'purchased_policies': purchased_policies  # ✅ Pass purchased policies to the template
    })



import requests
from django.shortcuts import render

from django.shortcuts import render



###################################################################################################

def create_head_policy(request):
    head_policies = MainHead_policy.objects.all()  # Move this line outside the if block
    
    if request.method == "POST":
        policy_name = request.POST.get('policy_name')
        MainHead_policy.objects.create(
            customer=request.user,
            polcy_name=policy_name
        )
        return redirect('create_head_policy')  # Ensure redirection happens correctly

    return render(request, 'agent/create_head_policy.html', {'head_policies': head_policies})


def create_subhead_policy(request):
    head_policies = MainHead_policy.objects.all()
    sub_policies = SubHead_Policy.objects.all()
    
    if request.method == "POST":
        sub_policy_name = request.POST.get('sub_policy_name')
        head_policy_id = request.POST.get('head_policy')
        head_policy = MainHead_policy.objects.get(id=head_policy_id)

        # Create Sub Policy linked to the selected Head Policy
        SubHead_Policy.objects.create(
            customer=request.user,
            polcy_name=sub_policy_name,
            head_policy=head_policy  # Assuming a ForeignKey relationship
        )

        return redirect('create_subhead_policy')

    return render(request, 'agent/create_subhead_policy.html', {
        'head_policies': head_policies,
        'sub_policies': sub_policies
    })

########################################################################################




@login_required
def add_policy_detail(request):
    sub_policies = SubHead_Policy.objects.all()
    policies = SubHead_Policy_Details.objects.all()  # Fetch all policy details

    if request.method == 'POST':
        plan_no = request.POST.get('plan_no')
        uin_no = request.POST.get('uin_no')
        sub_policy_id = request.POST.get('sub_policy')
        pdf = request.FILES.get('pdf')

        try:
            sub_policy = SubHead_Policy.objects.get(id=sub_policy_id)

            SubHead_Policy_Details.objects.create(
                plan_no=plan_no,
                uin_no=uin_no,
                pdf=pdf,
                sub_policy=sub_policy
            )

            messages.success(request, "Policy detail added successfully!")
            return redirect('add_policy_detail')

        except SubHead_Policy.DoesNotExist:
            messages.error(request, "Selected sub-policy does not exist.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, 'agent/create_subhead_policy_details.html', {
        'sub_policies': sub_policies,
        'policies': policies  # Pass policies to the template
    })


################################################################

def pol(request):
    policies = MainHead_policy.objects.all()
    return render(request, 'user/pol.html', {'policies': policies})

def sub_policy_details(request, sub_id):
    try:
        sub_policy = SubHead_Policy.objects.get(id=sub_id)
        details = sub_policy.details.all()  # Fetch related details
        policy_plans = PolicyPlan.objects.filter(policy=sub_policy)  # Fetch policy plans

        return render(request, 'user/sub_policy_details.html', {
            'sub_policy': sub_policy,
            'details': details,
            'policy_plans': policy_plans  # Pass plans to the template
        })
    except SubHead_Policy.DoesNotExist:
        messages.error(request, "Sub Policy not found.")
        return redirect('pol')  # Redirect to the main policies page


##########################################################################################

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SubHead_Policy, PolicyPlan

def manage_policy_plans(request):
    if request.method == "POST":
        policy_id = request.POST.get("sub_policy")
        duration_years = request.POST.get("duration")
        total_amount = request.POST.get("total_amount")
        monthly_premium = request.POST.get("monthly_premium")

        if policy_id and duration_years and total_amount and monthly_premium:
            policy = SubHead_Policy.objects.get(id=policy_id)
            PolicyPlan.objects.create(
                policy=policy,
                duration_years=duration_years,
                total_amount=total_amount,
                monthly_premium=monthly_premium
            )
            messages.success(request, "Policy plan added successfully!")
        else:
            messages.error(request, "All fields are required!")

        return redirect("manage_policy_plans")

    sub_policies = SubHead_Policy.objects.all()
    policy_plans = PolicyPlan.objects.all()
    return render(request, "agent/manage_policy_plans.html", {
        "sub_policies": sub_policies,
        "policy_plans": policy_plans
    })




################################################################################################

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SubHead_Policy, PurchasedPolicy

from datetime import timedelta, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserPolicyPurchase, SubHead_Policy, PolicyPlan



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import SubHead_Policy, PolicyPlan, UserPolicyPurchase

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import qrcode
import io
import base64
from .models import SubHead_Policy, PolicyPlan, UserPolicyPurchase
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import qrcode
import io
import base64
from .models import SubHead_Policy, PolicyPlan, UserPolicyPurchase

from decimal import Decimal

from decimal import Decimal
from bson import Decimal128  # Import MongoDB Decimal128


import uuid
import qrcode
import io
import base64
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import UserPolicyPurchase, SubHead_Policy, PolicyPlan
from bson.decimal128 import Decimal128

from decimal import Decimal
from bson import Decimal128  # Ensure this import for MongoDB Decimal

from decimal import Decimal
from bson.decimal128 import Decimal128



def to_decimal(value):
    """Convert MongoDB Decimal128 or string to Python Decimal safely."""
    if isinstance(value, Decimal):
        return value  # Already a Decimal
    if isinstance(value, Decimal128):  
        return Decimal(str(value.to_decimal()))  # Convert from MongoDB's Decimal128
    try:
        return Decimal(str(value).strip().replace(",", ""))  # Strip spaces and convert
    except (ValueError, TypeError):
        return Decimal("0.00")  # Fallback for invalid values


def buy_policy(request, sub_id):
    sub_policy = get_object_or_404(SubHead_Policy, id=sub_id)
    policy_plan = PolicyPlan.objects.filter(policy=sub_policy).first()

    if not policy_plan:
        messages.error(request, "No policy plan available for this sub-policy.")
        return redirect('pol')  

    if request.method == "POST":
        # Collect Data
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        address = request.POST.get("address")
        nominee_name = request.POST.get("nominee_name")
        nominee_relation = request.POST.get("nominee_relation")
        payment_method = request.POST.get("payment_method")

        # Generate Unique Transaction ID
        transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"

        # Ensure Decimal conversion before saving
        total_amount_decimal = to_decimal(policy_plan.total_amount)
        monthly_premium_decimal = to_decimal(policy_plan.monthly_premium)

        purchase = UserPolicyPurchase.objects.create(
            user=request.user,
            policy=sub_policy,
            duration_years=policy_plan.duration_years,
            total_amount=to_decimal(policy_plan.total_amount),  # Ensure Decimal
            monthly_premium=to_decimal(policy_plan.monthly_premium),  # Ensure Decimal
            nominee_name=nominee_name,
            nominee_relation=nominee_relation,
            address=address,
            phone_number=phone,
            payment_method=payment_method,
            transaction_id=transaction_id,  # Auto-generated
            payment_status=False,
        )
        # Debugging to check the logged-in user
        print("Logged-in user:", request.user)  # ✅ Correct way to print user
        print("User assigned to purchase:", purchase.user)

        messages.success(request, "Policy purchased successfully! Scan the QR to complete payment.")
        return redirect('generate_qr', purchase_id=purchase.id)  # Redirect to QR Page

    return render(request, 'user/buy_policy.html', {'sub_policy': sub_policy, 'policy_plan': policy_plan})

def generate_qr_code(request, purchase_id):
    purchase = get_object_or_404(UserPolicyPurchase, id=purchase_id)

    # Check available fields in `SubHead_Policy`
    policy_display_name = getattr(purchase.policy, "name", "Insurance Policy")

    payment_text = f"Paid for {policy_display_name} - Amount: {purchase.total_amount}"

    # Generate QR Code
    qr = qrcode.make(payment_text)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_image = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'user/payment_qr.html', {'qr_image': qr_image, 'purchase': purchase})

from decimal import Decimal

from decimal import Decimal


from decimal import Decimal
from django.shortcuts import get_object_or_404

def confirm_payment(request, purchase_id):
    purchase = get_object_or_404(UserPolicyPurchase, id=purchase_id)

    # Print all fields before update
    print("\n=== Before Payment Update ===")
    print(f"Purchase ID: {purchase.id}")
    print(f"User: {purchase.user}")
    print(f"Policy: {purchase.policy}")
    print(f"Duration (Years): {purchase.duration_years}")
    print(f"Total Amount: {purchase.total_amount} (Type: {type(purchase.total_amount)})")
    print(f"Monthly Premium: {purchase.monthly_premium}")
    print(f"Nominee Name: {purchase.nominee_name}")
    print(f"Nominee Relation: {purchase.nominee_relation}")
    print(f"Address: {purchase.address}")
    print(f"Phone Number: {purchase.phone_number}")
    print(f"Payment Method: {purchase.payment_method}")
    print(f"Transaction ID: {purchase.transaction_id}")
    print(f"Payment Status: {purchase.payment_status}")

    # ✅ Convert MongoDB Decimal128 to Python Decimal
    if isinstance(purchase.total_amount, Decimal128):
        purchase.total_amount = Decimal(str(purchase.total_amount.to_decimal()))
    elif isinstance(purchase.total_amount, str):
        purchase.total_amount = Decimal(purchase.total_amount.replace(",", ""))
    elif isinstance(purchase.total_amount, float):
        purchase.total_amount = Decimal(str(purchase.total_amount))
    else:
        purchase.total_amount = Decimal(purchase.total_amount)

    # ✅ Update the payment status
    purchase.payment_status = True

    # ✅ Force save the update properly
    purchase.save(update_fields=["payment_status"])

    # ✅ Print after update
    purchase.refresh_from_db()
    print("\n=== After Payment Update ===")
    print(f"Payment Status (Updated): {purchase.payment_status}")

    if purchase.payment_status:
        print("✅ Payment status successfully updated!")
    else:
        print("❌ Payment status update failed!")

    messages.success(request, "Payment successful! Your policy is now active.")
    return redirect('user_home')



#################################################################


def purchase_list(request):
    query = request.GET.get("q", "")
    if query:
        purchases = UserPolicyPurchase.objects.filter(user__username__icontains=query)
    else:
        purchases = UserPolicyPurchase.objects.all()

    return render(request, "agent/purchase.html", {"purchases": purchases, "query": query})

######################################################################################################

@login_required
def purchase_list_user(request):
    purchases = UserPolicyPurchase.objects.filter(user=request.user).select_related(
        'policy'  # Only direct FK
    ).prefetch_related(
        'policy__details'  # Reverse relation
    )

    # Add details manually in context
    for purchase in purchases:
        purchase.policy_details = purchase.policy.details.first()  # Get first related details

    return render(request, "user/purchase_list.html", {"purchases": purchases})


@login_required
def policy_details(request, policy_id):
    policy = get_object_or_404(UserPolicyPurchase, id=policy_id, user=request.user)
    return render(request, "user/policy_details.html", {"policy": policy})

##############################################################

from django.utils import timezone
from datetime import timedelta
import uuid

@login_required
def renew_policy(request, purchase_id):
    old_purchase = get_object_or_404(UserPolicyPurchase, id=purchase_id, user=request.user)
    
    if not old_purchase.is_active or not old_purchase.payment_status:
        messages.error(request, "This policy cannot be renewed.")
        return redirect('purchase_list_user')
    
    if request.method == 'POST':
        try:
            # Generate Unique Transaction ID
            transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
            
            # Create new purchase with same details but new dates
            new_purchase = UserPolicyPurchase(
                user=request.user,
                policy=old_purchase.policy,
                duration_years=old_purchase.duration_years,
                total_amount=old_purchase.total_amount,
                monthly_premium=old_purchase.monthly_premium,
                start_date=timezone.now().date(),
                expiry_date=timezone.now().date() + timedelta(days=365*old_purchase.duration_years),
                nominee_name=old_purchase.nominee_name,
                nominee_relation=old_purchase.nominee_relation,
                address=old_purchase.address,
                phone_number=old_purchase.phone_number,
                payment_method=old_purchase.payment_method,
                transaction_id=transaction_id,
                payment_status=False
            )
            new_purchase.save()
            old_purchase.is_active = False
            old_purchase.save()
            
            messages.success(request, "Policy renewal request submitted successfully! Scan the QR to complete payment.")
            return redirect('generate_qr', purchase_id=new_purchase.id)
            
        except Exception as e:
            messages.error(request, f"Error renewing policy: {str(e)}")
            return redirect('purchase_list_user')
    
    # For GET request, show confirmation page
    return render(request, 'user/renew_policy.html', {
        'old_purchase': old_purchase,
        'new_start_date': timezone.now().date(),
        'new_expiry_date': timezone.now().date() + timedelta(days=365*old_purchase.duration_years)
    })

################################################################################################

import json  # Add this at the top of your views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import UserPolicyPurchase, User_InsuranceClaim

import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import UserPolicyPurchase, User_InsuranceClaim

import json
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import UserPolicyPurchase, User_InsuranceClaim

@login_required
def submit_claim(request, policy_id):
    policy_purchase = get_object_or_404(UserPolicyPurchase, id=policy_id, user=request.user)
    policy_details = policy_purchase.policy.details.first() if policy_purchase.policy else None

    print(f"Request method: {request.method}")
    print(f"Content-Type: {request.content_type}")

    if request.method == "POST":
        try:
            # Check if request body is JSON
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST

            print(f"Received Data: {data}")

            # Extract required fields
            reason = data.get("reason")
            additional_info = data.get("additional_info")
            bank_details = data.get("bank_details")

            if not reason or not bank_details:
                raise ValueError("Reason and bank details are required.")

            # Convert amounts to Decimal if they're strings
            claim_amount = Decimal(str(policy_purchase.total_amount))
            monthly_premium = Decimal(str(policy_purchase.monthly_premium))

            # Create new insurance claim
            claim = User_InsuranceClaim.objects.create(
                user=request.user,
                policy=policy_purchase,
                plan_no=policy_details.plan_no if policy_details else "N/A",
                uin_no=policy_details.uin_no if policy_details else "N/A",
                claim_amount=claim_amount,
                monthly_premium=monthly_premium,
                reason=reason,
                additional_info=additional_info,
                bank_details=bank_details,
            )

            print(f"Claim Created: {claim.id}")

            return JsonResponse({"message": "Claim submitted successfully!", "status": "success"})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": str(e), "status": "error"}, status=400)

    # Render claim submission form
    return render(request, "user/submit_claim.html", {
        "policy_id": policy_id,
        "plan_no": policy_details.plan_no if policy_details else "N/A",
        "uin_no": policy_details.uin_no if policy_details else "N/A",
        "amount": policy_purchase.total_amount,
        "monthly_premium": policy_purchase.monthly_premium,
    })



#########################################################################################

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import User_InsuranceClaim

def claimlist_admin(request):
    claims = User_InsuranceClaim.objects.all().order_by('-created_at')
    
    # Debugging: Print claim amounts
    for claim in claims:
        print(f"Claim ID: {claim.id}, Amount: {claim.claim_amount}, Monthly: {claim.monthly_premium}")

    return render(request, 'agent/claim_list.html', {'claims': claims})

from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import User_InsuranceClaim

def update_claim_status(request, claim_id):
    claim = get_object_or_404(User_InsuranceClaim, id=claim_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        # Ensure status is valid
        if new_status in ["Pending", "Approved", "Rejected"]:
            claim.status = new_status

            # Convert claim_amount and monthly_premium to Decimal
            try:
                claim.claim_amount = Decimal(str(claim.claim_amount))
                claim.monthly_premium = Decimal(str(claim.monthly_premium))
            except:
                return HttpResponse("Invalid decimal format", status=400)

            claim.save()
            return redirect('claimlist_admin')
    
    return HttpResponse("Invalid Request", status=400)


def my_claim_report(request):
    user_claims = User_InsuranceClaim.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user/my_claim_report.html', {'claims': user_claims})



###########################################################################################


@login_required
def admin_complaints(request):
    if request.user.role != 1:  # Check if the user is an admin (role=1)
        return redirect('home')  # Adjust this based on your project's home URL

    all_complaints = Complaint.objects.all()

    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")
        reply = request.POST.get("reply")
        if complaint_id and reply:
            complaint = Complaint.objects.get(id=complaint_id)
            complaint.reply = reply
            complaint.save()
            return redirect('admin_complaints')

    return render(request, "admin/complaints.html", {"complaints": all_complaints})


@login_required
def complaints_register(request):
    # Fetch complaints of the logged-in user
    complaints = Complaint.objects.filter(user=request.user)

    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            Complaint.objects.create(user=request.user, message=message)
            return redirect('complaints_register')  # Adjust this based on your URL pattern

    return render(request, "user/user_complaint.html", {"complaints": complaints})


########################################################################

from django.shortcuts import render
from .models import UserPolicyPurchase, User_InsuranceClaim
from bson.decimal128 import Decimal128

def convert_decimal128(value):
    """Convert MongoDB Decimal128 to float"""
    if isinstance(value, Decimal128):
        return float(value.to_decimal())
    return float(value or 0)

def financial_report(request):
    # Total premium collected
    total_premium_collected = sum(convert_decimal128(p.total_amount) for p in UserPolicyPurchase.objects.all())

    # Total number of claims
    total_claims = User_InsuranceClaim.objects.count()

    # Approved claims total amount
    approved_claims = User_InsuranceClaim.objects.filter(status="Approved")
    approved_claims_amount = sum(convert_decimal128(c.claim_amount) for c in approved_claims)

    # Pending claims count
    pending_claims_count = User_InsuranceClaim.objects.filter(status="Pending").count()

    # Rejected claims count
    rejected_claims_count = User_InsuranceClaim.objects.filter(status="Rejected").count()

    context = {
        'total_premium_collected': total_premium_collected,
        'total_claims': total_claims,
        'approved_claims_amount': approved_claims_amount,
        'pending_claims_count': pending_claims_count,
        'rejected_claims_count': rejected_claims_count,
    }
    
    return render(request, 'admin/financial_report.html', context)


############################################################


def analytics(request):
    if request.user.role == 1:  # Admin
        total_policies = UserPolicyPurchase.objects.count()
        total_claims = User_InsuranceClaim.objects.count()
        approved_claims = User_InsuranceClaim.objects.filter(status="Approved").count()
        claim_approval_rate = (approved_claims / total_claims) * 100 if total_claims else 0

        context = {
            "total_policies": total_policies,
            "total_claims": total_claims,
            "claim_approval_rate": claim_approval_rate,
        }
        return render(request, "admin/analytics.html", context)

    elif request.user.role == 3:  # Customer
        user_policies = UserPolicyPurchase.objects.filter(user=request.user).count()
        user_claims = User_InsuranceClaim.objects.filter(user=request.user).count()

        context = {
            "user_policies": user_policies,
            "user_claims": user_claims,
        }
        return render(request, "admin/analytics.html", context)

    return render(request, "unauthorized.html")
