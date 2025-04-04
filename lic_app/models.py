from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, username=None, password=None,*args,**kwargs):
        if not username:
            raise ValueError("Users must have a username")
        if not password:
            raise ValueError("Users must have a password")
        user= self.model(
            username=username,
            *args,
            **kwargs)
        user.set_password(password)
        user.is_active=True
        user.save()
        return user

    def create_superuser(self, username, password,email):
        user = self.create_user(
            username=username,
            password=password,
            email=email,
            role=1, 
            is_staff=True,
        )
        user.is_superuser = True
        user.save()
        return user

ROLE_CHOICES = (
        (1, 'Admin'),
        (2, 'Agent'),
        (3, 'User'),
    )

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    role = models.IntegerField(choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    # Add unique related_name attributes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='customuser_set',  # Unique related_name
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',  # Unique related_name
        related_query_name='customuser',
    )

    def __str__(self):
        return self.username
    

class AgentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="agent_profile")
    address = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    approved = models.BooleanField(default=False)  # Only admin can approve

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="user_profile")
    address = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)



from django.db import models

class UserData(models.Model):
    fk_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="user_data")
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)



#############################################################


# Insurance Policies
class InsurancePolicy(models.Model):
    POLICY_TYPES = [
        ('Health', 'Health Insurance'),
        ('Life', 'Life Insurance'),
        ('Vehicle', 'Vehicle Insurance'),
        ('Property', 'Property Insurance'),
    ]
    fk_user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="created_policies")
    name = models.CharField(max_length=255)
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES)
    description = models.TextField()
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name




class PurchasedPolicy(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="purchased_policies")
    policy = models.ForeignKey(InsurancePolicy, on_delete=models.CASCADE, related_name="purchased_by_customers")
    purchase_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.customer.username} - {self.policy.name}"



class MainHead_policy(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name="main_head_policies")
    polcy_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.customer.username}"
    

class SubHead_Policy(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name="sub_head_policies")
    polcy_name = models.CharField(max_length=50)
    head_policy = models.ForeignKey(MainHead_policy, on_delete=models.CASCADE,related_name="sub_policies")

    def __str__(self):
        return f"{self.customer.username}"
         
class SubHead_Policy_Details(models.Model):
    plan_no = models.CharField(max_length=50)
    uin_no = models.CharField(max_length=50)
    pdf = models.FileField(upload_to='policy_pdfs/', blank=True, null=True)
    sub_policy = models.ForeignKey(SubHead_Policy, on_delete=models.CASCADE, related_name="details")



# Admin sets duration and pricing
class PolicyPlan(models.Model):
    policy = models.ForeignKey(SubHead_Policy, on_delete=models.CASCADE, related_name="plans")
    duration_years = models.IntegerField()  # 1 year, 2 years, etc.
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Full policy price
    monthly_premium = models.DecimalField(max_digits=10, decimal_places=2)  # Monthly installment

    def __str__(self):
        return f"{self.policy.polcy_name} - {self.duration_years} Year(s) - ₹{self.total_amount}"



#####################################################################
from datetime import timedelta,date


class UserPolicyPurchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="purchased_policies_data")
    policy = models.ForeignKey(SubHead_Policy, on_delete=models.CASCADE, related_name="purchases_data")
    duration_years = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_premium = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    nominee_name = models.CharField(max_length=100)
    nominee_relation = models.CharField(max_length=50)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True) # Payment fields
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.BooleanField(default=False)  # False = Pending, True = Paid



    def save(self, *args, **kwargs):
        if not self.start_date:
            self.start_date = date.today()  # Ensure start_date is set
        if not self.expiry_date:
            self.expiry_date = self.start_date + timedelta(days=365 * self.duration_years)
        super().save(*args, **kwargs)







class User_InsuranceClaim(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="claims")
    policy = models.ForeignKey(UserPolicyPurchase, on_delete=models.CASCADE, related_name="claims")
    plan_no = models.CharField(max_length=50)  # New Field
    uin_no = models.CharField(max_length=50)  # New Field
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Already present
    monthly_premium = models.DecimalField(max_digits=10, decimal_places=2)  # New Field
    reason = models.TextField()
    additional_info = models.TextField(blank=True, null=True)  # Already added
    bank_details = models.CharField(max_length=255, blank=True, null=True)  # Already added
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")], default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)





class Complaint(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"Complaint by {self.user.username}"