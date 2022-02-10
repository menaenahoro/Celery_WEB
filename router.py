from fastapi import APIRouter
from models import RequestData, Task, Result
from commenta.tasks import get_comments
from celery.result import AsyncResult
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get('/')
def touch():
    return 'API is running'

@router.get('/train', response_model=Task, status_code=202)
async def run_training(tweet_id):
    tweet_id = [tweet_id]
    task_id = get_comments.delay(tweet_id)
    return {'task_id': str(task_id), 'status': 'Processing'}

@router.get('/result/{task_id}', response_model=Result, status_code=200,
            responses={202: {'model': Task, 'description': 'Accepted: Not Ready'}})
async def fetch_result(task_id):
    # Fetch result for task_id
    task = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()
    return {'task_id': task_id, 'status': {result}}