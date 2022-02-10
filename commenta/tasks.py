from .worker import app
from celery.utils.log import get_task_logger
from .comments_func import reply_thread_maker

# Create logger - enable to display messages on task logger
celery_log = get_task_logger(__name__)

@app.task(name='commenta.get_comments')
def get_comments(tweet_id):
    result = tweet_id
    results = reply_thread_maker(result)
    celery_log.info(f"Celery task completed!")
    return results