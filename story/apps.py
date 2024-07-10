from django.apps import AppConfig
import os

class StoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'story'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) is not None:
            print(' RUN_MAIN :', os.environ.get('RUN_MAIN', None))
            from . import jobs
            jobs.start()