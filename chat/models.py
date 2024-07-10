#models.py
from django.db import models
from story.models import Story
from user.models import User
from result.models import Result

class Talk(models.Model):
    id = models.AutoField(primary_key=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        db_table = 'Talk'
