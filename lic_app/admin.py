from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)


from django.contrib import admin
from .models import SubHead_Policy_Details

@admin.register(SubHead_Policy_Details)
class SubHeadPolicyDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan_no', 'uin_no', 'sub_policy', 'pdf')
    search_fields = ('plan_no', 'uin_no', 'sub_policy__polcy_name')
    list_filter = ('sub_policy',)


from django.contrib import admin
from .models import UserPolicyPurchase

@admin.register(UserPolicyPurchase)
class UserPolicyPurchaseAdmin(admin.ModelAdmin):
    list_display = [
        "id", "user", "policy", "duration_years", "total_amount", "monthly_premium",
        "start_date", "expiry_date", "nominee_name", "nominee_relation", "address",
        "phone_number", "is_active", "payment_method", "transaction_id", "payment_status"
    ]  # 👈 **All fields listed here**
    
    list_filter = ["payment_status", "is_active", "start_date", "expiry_date"]
    search_fields = ["user__username", "policy__name", "transaction_id", "phone_number", "nominee_name"]
    ordering = ["-start_date"]


from django.contrib import admin
from .models import User_InsuranceClaim

@admin.register(User_InsuranceClaim)
class UserInsuranceClaimAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "policy", "plan_no", "uin_no", "claim_amount", "monthly_premium", "status", "created_at")
    list_filter = ("status", "created_at")  # Filters for easy navigation
    search_fields = ("user__email", "plan_no", "uin_no")  # Searchable fields
    ordering = ("-created_at",)  # Orders by latest claims
