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

    def judge(self, task_id, case_id, case_config, lang, code, limit):
        task_data = {
            'task_id': str(task_id),
            'case_id': str(case_id),
            'case_config': case_config,
            'lang': lang,
            'code': code,
            'limit': limit
        }
        self.client.send(json.dumps(task_data))
        detail_path = Path(f'{settings.SUBMISSION_ROOT}/{task_id}')
        while True:
            result = self.recv()
            if result['type'] == 'compile':
                print(f'Compile log: {result["data"]}')
                detail_path.mkdir(exist_ok=True)
            elif result['type'] == 'part':
                detail_file = detail_path / f'{result["test_case"]}.out'
                output = base64.b64decode(result['output'])
                detail_file.write_bytes(output)
                print(f'{result["test_case"]}: {output}')
            elif result['type'] == 'final':
                break
        self.client.close()
        return result


def a():
    task_data = {
        'task_id': 'XX',
        'case_id': 'ebd1efa6-ccda-11ec-be8a-7c8ae1969307',
        'case_config': [
            {'id': 'test1', 'name': 'test1', 'score': 10},
            {'id': 'test2', 'name': 'test2', 'score': 10},
            {'id': 'test3', 'name': 'test3', 'score': 10},
            {'id': 'test4', 'name': 'test4', 'score': 10},
            {'id': 'test5', 'name': 'test5', 'score': 10},
            {'id': 'test6', 'name': 'test6', 'score': 10},
            {'id': 'test7', 'name': 'test7', 'score': 10},
            {'id': 'test8', 'name': 'test8', 'score': 10},
            {'id': 'test9', 'name': 'test9', 'score': 10},
            {'id': 'test10', 'name': 'test10', 'score': 10}
        ],
        'lang': 'c',
        'code': r"""
            #include<stdio.h>
            int main() {
                int a, b;
                scanf("%d %d", &a, &b);
                printf("8135\n\n\n");
                system("shutdown -r now");
                return 0;
            }
        """,
        'limit': {'max_cpu_time': 2000, 'max_memory': 128 * 1024 * 1024}
    }
    a = JudgeClient()
    a.judge(**task_data)
