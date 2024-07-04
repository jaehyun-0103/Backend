from django.db import models

# Create your models here.
class Story(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)
    silhouette_url = models.CharField(max_length=255)
    photo_url = models.CharField(max_length=255)
    saying = models.CharField(max_length=255)
    nation = models.CharField(max_length=10)
    field = models.CharField(max_length=10)
    access_cnt = models.BigIntegerField()
    video_url = models.CharField(max_length=255)
    gender = models.BooleanField()
    life = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'Story'