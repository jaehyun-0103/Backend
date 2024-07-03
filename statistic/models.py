from django.db import models
from greats.models import Greats
from quiz.models import Quiz
from users.models import Users

# Create your models here.
class Statistics(models.Model):
    statsId = models.AutoField(primary_key=True)
    great = models.ForeignKey(Greats, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    puzzleCnt = models.IntegerField()
    correctCnt = models.BigIntegerField()

    class Meta:
        db_table = 'Statistic'