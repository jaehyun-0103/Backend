from django.db import models

# Create your models here.

class Users(models.Model):
    userId = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30)
    year = models.IntegerField()
    date = models.DateField()

    class Meta:
        db_table = 'Users'