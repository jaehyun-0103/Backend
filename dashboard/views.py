from rest_framework.views import APIView
from rest_framework.response import Response
from user.models import User
from story.models import Story
from result.models import Result
from django.db.models import Count, F, Sum
from datetime import date, timedelta

class DateVisitsAPIView(APIView):

    def get(self, request, format=None):
        today = date.today()

        date_range = [today - timedelta(days=i) for i in range(7)]

        visit_data = User.objects.filter(
            created_at__date__in=date_range
        ).values('created_at__date').annotate(
            visit_total=Count('id')
        ).order_by('created_at__date')

        response_data = [
            {
                'created_at': visit['created_at__date'].strftime('%y-%m-%d'),
                'visit_total': str(visit['visit_total'])
            }
            for visit in visit_data
        ]

        return Response(response_data)


class AgeVisitsAPIView(APIView):

    def get(self, request, format=None):
        current_year = date.today().year

        all_users = User.objects.all()

        sorted_years = sorted([current_year - user.year + 1 for user in all_users])

        age_counts = {}
        for year in sorted_years:
            age_counts[year] = age_counts.get(year, 0) + 1

        response_data = [
            {
                'year': str(year),
                'visit_total': str(count)
            }
            for year, count in age_counts.items()
        ]

        return Response(response_data)

class ChatVisitsAPIView(APIView):
    def get(self, request, format=None):
        chats_data = Story.objects.values('name', 'access_cnt')

        response_data = [
            {
                'name': chat['name'],
                'access_cnt': str(chat['access_cnt'])
            }
            for chat in chats_data
        ]

        return Response(response_data)

class CorrectRateAPIView(APIView):

    def get(self, request, format=None):
        all_story_ids = Story.objects.values_list('id', flat=True)

        results = Result.objects.values('story').annotate(
            total_correct=Sum('correct_cnt'),
            total_puzzles=Sum('puzzle_cnt')
        ).order_by('story')

        response_data = []
        for story_id in all_story_ids:
            result = results.filter(story=story_id).first()

            if result:
                if result['total_puzzles'] > 0:
                    correct_rate = (result['total_correct'] / (result['total_puzzles'] * 5)) * 100
                else:
                    correct_rate = 0

                story_name = Story.objects.get(id=story_id).name

                response_data.append({
                    'name': story_name,
                    'correct_rate': f"{correct_rate:.0f}%"  # 백분율 형태로 포맷팅
                })
            else:
                story_name = Story.objects.get(id=story_id).name
                response_data.append({
                    'name': story_name,
                    'correct_rate': None
                })

        return Response(response_data)