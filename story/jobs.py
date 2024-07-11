from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.models import DjangoJobExecution
from django_redis import get_redis_connection
from story.models import Story
import logging

logger = logging.getLogger(__name__)

def update_access_counts():
    try:
        redis_conn = get_redis_connection("default")

        keys = redis_conn.keys("story:*:access_cnt")

        for key in keys:
            story_id = key.split(b':')[1].decode('utf-8')
            access_count = int(redis_conn.get(key))

            story = Story.objects.filter(pk=story_id, is_deleted=False).first()
            if story:
                story.access_cnt += access_count
                story.save()

                redis_conn.delete(key)
                logger.info(f"Access count for story_id {story_id} updated to {story.access_cnt} in the database")
            else:
                logger.error(f"Story with id {story_id} not found.")

    except Exception as e:
        logger.error(f"Failed to update access counts from Redis to the database: {str(e)}")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        update_access_counts,
        trigger=IntervalTrigger(seconds=1000),
        id="update_access_counts",
        max_instances=1,
        replace_existing=True,
    )
    register_events(scheduler)
    scheduler.start()
    logger.info("Scheduler started!")