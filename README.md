# Back End | 网站后端

### Pre-request | 前置要求

* Python ≥ 3.7
* Django ≥ 3.0
* Redis
* RabbitMQ `可选`

### Install | 安装

```bash
pip3 install -r requirements.txt
echo $(python3 -c "from django.core.management import utils;print(utils.get_random_secret_key())") > secret.key
```

### Structure | 目录结构

```text
|-oj_problem 题目数据
|-oj_submission 提交数据&评测任务管理
|-oj_user 用户管理
|-media
  |-spj 特殊评测源代码，可以存放于其他位置，需要修改SPJ_ROOT
  |-test-data 评测数据，可以存放于其他位置，需要修改TEST_DATA_ROOT
```