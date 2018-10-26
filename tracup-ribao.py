# -*- coding: utf-8 -*-
import csv
import re
from pprint import pprint
import xlwt
from collections import Counter
from tracup import TracupSDK, flatten

# 把固定的参数定义成变量, 因为参数会根据接口的不同而变化，但这些固定参数不会
u_key = '414a471ef24654e6b8413416a5048238'
api_key = '6e238511179b6aeadf1e26fed1f6db07'
p_key = '9df58763ae346255c4f3667bd8adf5bb'

t = TracupSDK(api_key, u_key)
# 获得问题所有状态的key
issueStatus = t.get_qestion_status(p_key)
status_key = [i['key'] for i in issueStatus['status']]
# 获取所有问题列表
all_issues = []
for s in status_key:
    result = t.get_qestion_list(p_key, s)
    if result is None:
        continue
    all_issues.append(result)

all_issues = list(flatten(all_issues))

all_projet_module = t.get_project_modules(p_key)['list']

#项目模块名称列表
project_modules = [i['projectModuleName'] for i in all_projet_module]


for module in project_modules:
    
    issue_status_type = []
    project_result = []
    
    # 取到各个模块下的问题列表
    for issue in all_issues:
        if issue['list'] == None:
           continue

        for q in issue['list']:
            if q['issueModule'] == module:
                # issue_status_type.append('{},{}'.format(q.get('issueStatusText', []), q.get('issueType', [])))
                issue_status_type.append('{},{},{}'.format(module,q.get('issueStatusText', []), q.get('issueType', [])))

    project_result = Counter(issue_status_type)
    pprint(project_result)
    pprint(issue_status_type)