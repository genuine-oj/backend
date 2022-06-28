# Back End | 网站后端

[![Crowdin](https://badges.crowdin.net/genuine-oj-backend/localized.svg)](https://crowdin.com/project/genuine-oj-backend)
[![GitHub license](https://img.shields.io/github/license/genuine-oj/backend)](https://github.com/genuine-oj/backend/blob/master/LICENSE.md)

### Pre-request | 前置要求

* Python ≥ 3.7
* Django ≥ 3.0
* Redis
* RabbitMQ `可选`

### Install | 安装

```bash
pip3 install -r requirements.txt
echo $(python3 -c "from django.core.management import utils;print(utils.get_random_secret_key())") > secret.key
python3 manage.py makemigrations oj_user
python3 manage.py migrate
python3 manage.py makemigrations oj_problem oj_submission
python3 manage.py migrate
```

### API document | 接口文档
[API Fox (Simplified Chinese)](https://www.apifox.cn/apidoc/project-931688)

### Structure | 目录结构

```text
|-oj_problem 题目数据
|-oj_submission 提交数据&评测任务管理
|-oj_user 用户管理
|-media
  |-spj 特殊评测源代码，可以存放于其他位置，需要修改SPJ_ROOT
  |-test-data 评测数据，可以存放于其他位置，需要修改TEST_DATA_ROOT
```
