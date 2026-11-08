"""Seed local demo accounts; does not reset existing business records."""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from app.demo import seed

seed()
print("Demo ready: alice / bob / admin; password: DemoPass123!")
