from django.db import models
from profiles.models import Profiles
from quiz.models import Quiz

# Create your models here.
class Greats(models.Model):
    greatId = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profiles, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    photo = models.CharField(max_length=255)
    saying = models.TextField()
    talking = models.BigIntegerField()
    nation = models.CharField(max_length=255)
    field = models.CharField(max_length=255)

    class Meta:
        db_table = 'Greats'