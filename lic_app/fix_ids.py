import os
import django
from lic_app.models import Policy  # Adjust the model name and import based on your project structure

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lic_project.settings')
django.setup()

def fix_policy_ids():
    policies = Policy.objects.all().order_by('id')
    for index, policy in enumerate(policies, start=1):
        policy.id = index
        policy.save()

    print("Policy IDs have been fixed successfully!")

if __name__ == "__main__":
    fix_policy_ids()
