from django.db import models

# Create your models here.
class Profiles(models.Model):
    profileId = models.AutoField(primary_key=True)
    silhouette = models.CharField(max_length=255)
    video = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    life = models.CharField(max_length=255)

    class Meta:
        db_table = 'Profiles'