from django.conf import settings
import json
import base64
from pathlib import Path
from websocket import create_connection
import enum

from .models import StatusChoices


class JudgeResult(enum.IntEnum):
    COMPILE_ERROR = -2
    WRONG_ANSWER = -1
    ACCEPTED = 0
    TIME_LIMIT_EXCEEDED = 1
    MEMORY_LIMIT_EXCEEDED = 2
    RUNTIME_ERROR = 3
    SYSTEM_ERROR = 4


ResultMapping = {
    JudgeResult.COMPILE_ERROR: StatusChoices.COMPILE_ERROR,
    JudgeResult.WRONG_ANSWER: StatusChoices.WRONG_ANSWER,
    JudgeResult.ACCEPTED: StatusChoices.ACCEPTED,
    JudgeResult.TIME_LIMIT_EXCEEDED: StatusChoices.TIME_LIMIT_EXCEEDED,
    JudgeResult.MEMORY_LIMIT_EXCEEDED: StatusChoices.MEMORY_LIMIT_EXCEEDED,
    JudgeResult.RUNTIME_ERROR: StatusChoices.RUNTIME_ERROR,
    JudgeResult.SYSTEM_ERROR: StatusChoices.SYSTEM_ERROR
}


class JudgeClient(object):

    def __init__(self):
        self.client = create_connection(f'ws://{settings.JUDGE_SERVER}/')

    def recv(self):
        try:
            data = json.loads(self.client.recv())
        except json.decoder.JSONDecodeError:
            return {
                'type': 'final',
                'status': JudgeResult.SYSTEM_ERROR,
                'score': 0,
                'statistics': {
                    'max_time': 0,
                    'max_memory': 0
                },
                'log': 'Failed to decode judge server result',
                'detail': []
            }
        return data

    def judge(self, task_id, case_id, spj_id, test_case_config,
              subcheck_config, lang, code, limit):
        task_data = {
            'task_id': str(task_id),
            'case_id': str(case_id),
            'spj_id': spj_id and str(spj_id),
            'test_case_config': test_case_config,
            'subcheck_config': subcheck_config,
            'lang': lang,
            'code': code,
            'limit': limit
        }
        self.client.send(json.dumps(task_data))
        detail_path = Path(f'{settings.SUBMISSION_ROOT}/{task_id}')
        while True:
            result = self.recv()
            if result['type'] == 'compile':
                # print(f'Compile log: {result["data"]}')
                detail_path.mkdir(exist_ok=True)
            elif result['type'] == 'part':
                detail_file = detail_path / f'{result["test_case"]}.out'
                output = base64.b64decode(result['output'])
                detail_file.write_bytes(output)
                # print(f'{result["test_case"]}: {output}')
            elif result['type'] == 'final':
                break
        self.client.close()
        return result
