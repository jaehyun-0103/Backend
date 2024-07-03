from django.db import models
import jsonfield

# Create your models here.
class Quiz(models.Model):
    quizId = models.AutoField(primary_key=True)
    question = jsonfield.JSONField()
    answer = jsonfield.JSONField()
    explanation = jsonfield.JSONField()

    class Meta:
        db_table = 'Quiz'