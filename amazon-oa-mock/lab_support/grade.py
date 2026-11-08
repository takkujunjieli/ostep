"""Load acceptance tests outside the candidate repository, against its app."""
import os
import sys

workspace, grader = sys.argv[1:3]
sys.path.insert(0, workspace)
sys.path.insert(0, grader)
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
import django

django.setup()
from django.test.runner import DiscoverRunner

sys.exit(bool(DiscoverRunner(verbosity=2, interactive=False).run_tests(["test_acceptance"])))
