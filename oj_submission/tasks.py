from celery import shared_task
from .judger import JudgeClient, ResultMapping
from .models import Submission, StatusChoices
from oj_problem.models import ProblemSolve


@shared_task
def judge(task_id, case_id, spj_id, test_case_config, subcheck_config, lang,
          code, limit):
    submission = Submission.objects.get(id=task_id)
    judger = JudgeClient()
    submission.status = StatusChoices.JUDGING
    submission.allow_download = submission.problem.test_case.allow_download
    submission.save(update_fields=['status', 'allow_download'])
    result = judger.judge(task_id, case_id, spj_id, test_case_config,
                          subcheck_config, lang, code, limit)
    submission.status = ResultMapping[result['status']]
    submission.score = result['score']
    submission.execute_time = result['statistics']['max_time']
    submission.execute_memory = result['statistics']['max_memory']
    submission.detail = result['detail']
    submission.log = result['log']
    submission.save(update_fields=[
        'status', 'score', 'execute_time', 'execute_memory', 'detail', 'log'
    ])
    if submission.status == StatusChoices.ACCEPTED:
        submission.problem.accepted_count += 1
        submission.problem.save(update_fields=['accepted_count'])
        ProblemSolve.objects.get_or_create(user=submission.user,
                                           problem=submission.problem)
