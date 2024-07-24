from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.models import DjangoJobExecution
from django_redis import get_redis_connection
from user.models import User
from story.models import Story
from result.models import Result
from django.db.models import Count, Sum
from datetime import date, timedelta
import json
import logging

logger = logging.getLogger(__name__)

def cache_data(key, data):
    try:
        redis_conn = get_redis_connection("default")
        logger.info("Connected to Redis")
        redis_conn.set(key, json.dumps(data))
        logger.info("Data cached successfully")
    except Exception as e:
        logger.error(f"Error caching data: {str(e)}")

def update_date_visits():
    try:
        key = f"dashboard:date:visits"

        today = date.today()
        date_range = [today - timedelta(days=i) for i in range(7)]

        visit_data = User.objects.filter(
            created_at__date__in=date_range
        ).values('created_at__date').annotate(
            visit_total=Count('id')
        ).order_by('created_at__date')

        visit_data_dict = {visit['created_at__date']: visit['visit_total'] for visit in visit_data}

        data_to_cache = [
            {
                'date': day.strftime('%Y-%m-%d'),
                'visit_total': str(visit_data_dict.get(day, 0))
            }
            for day in date_range
        ]

        logger.info(f"Data to cache: {data_to_cache}")

        data_to_cache.reverse()
        cache_data(key, data_to_cache)
    except Exception as e:
        logger.error(f"Error updating date visit data: {str(e)}")

def update_age_visits():
    try:
        key = f"dashboard:age:visits"

        current_year = date.today().year
        all_users = User.objects.all()

        if not all_users.exists():
            logger.warning("No users found.")
            data_to_cache = [
                {
                    'age': None,
                    'visit_total': "0"
                }
            ]
            cache_data(key, data_to_cache)
            return

        sorted_years = sorted([current_year - user.year + 1 for user in all_users])

        age_counts = {}
        for year in sorted_years:
            age_counts[year] = age_counts.get(year, 0) + 1

        data_to_cache = [
            {
                'age': str(year),
                'visit_total': str(count)
            }
            for year, count in age_counts.items()
        ]

        logger.info(f"Data to cache: {data_to_cache}")

        cache_data(key, data_to_cache)
    except Exception as e:
        logger.error(f"Error updating age visit data: {str(e)}")

def update_chat_visits():
    try:
        key = f"dashboard:chat:visits"

        chats_data = Story.objects.values('name', 'access_cnt')

        data_to_cache = [
            {
                'name': chat['name'],
                'access_cnt': str(chat['access_cnt'])
            }
            for chat in chats_data
        ]

        logger.info(f"Data to cache: {data_to_cache}")

        cache_data(key, data_to_cache)
    except Exception as e:
        logger.error(f"Error updating chat visit data: {str(e)}")

def update_correct_rate():
    try:
        key = f"dashboard:correct:rate"

        all_story_ids = Story.objects.values_list('id', flat=True)

        results = Result.objects.values('story').annotate(
            total_correct=Sum('correct_cnt'),
            total_puzzles=Sum('puzzle_cnt')
        ).order_by('story')

        data_to_cache = []

        for story_id in all_story_ids:
            result = results.filter(story=story_id).first()

            if result:
                if result['total_puzzles'] > 0:
                    correct_rate = (result['total_correct'] / (result['total_puzzles'] * 5)) * 100
                else:
                    correct_rate = 0

                story_name = Story.objects.get(id=story_id).name

                data_to_cache.append({
                    'name': story_name,
                    'correct_rate': f"{correct_rate:.0f}%"
                })
            else:
                story_name = Story.objects.get(id=story_id).name
                data_to_cache.append({
                    'name': story_name,
                    'correct_rate': None
                })

        logger.info(f"Data to cache: {data_to_cache}")

        cache_data(key, data_to_cache)
    except Exception as e:
        logger.error(f"Error updating correct rate data: {str(e)}")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        update_date_visits,
        trigger=IntervalTrigger(seconds=1000),
        id="update_date_visits",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        update_age_visits,
        trigger=IntervalTrigger(seconds=1000),
        id="update_age_visits",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        update_chat_visits,
        trigger=IntervalTrigger(seconds=1000),
        id="update_chat_visits",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        update_correct_rate,
        trigger=IntervalTrigger(seconds=1000),
        id="update_correct_rate",
        max_instances=1,
        replace_existing=True,
    )
    register_events(scheduler)
    scheduler.start()
    logger.info("Scheduler started!")

    update_date_visits()
    update_age_visits()
    update_chat_visits()
    update_correct_rate()
