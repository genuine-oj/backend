from celery import shared_task
from .judger import JudgeClient, ResultMapping
from .models import Submission, StatusChoices


@shared_task
def judge(task_id, case_id, case_config, lang, code, limit):
    submission = Submission.objects.get(id=task_id)
    judger = JudgeClient()
    submission.status = StatusChoices.JUDGING
    submission.save(update_fields=['status'])
    result = judger.judge(task_id, case_id, case_config, lang, code, limit)
    submission.status = ResultMapping[result['status']]
    submission.score = result['score']
    submission.execute_time = result['statistics']['max_time']
    submission.execute_memory = result['statistics']['max_memory']
    submission.detail = result['detail']
    submission.log = result['log']
    submission.save(update_fields=['status', 'score', 'execute_time', 'execute_memory', 'detail', 'log'])
