import os

env = os.environ.get('DJANGO_SETTINGS_MODULE', 'banner_project.settings.dev')
__all__ = ['env']