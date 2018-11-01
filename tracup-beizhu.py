# -*- coding: utf-8 -*-
import json
import csv
import re
from pprint import pprint
from tracup import TracupSDK

# 把固定的参数定义成变量, 因为参数会根据接口的不同而变化，但这些固定参数不会
u_key = '414a471ef24654e6b8413416a5048238'
api_key = '6e238511179b6aeadf1e26fed1f6db07'
p_key = 'a6a5891ca82e0ff3b60a2c1fba3cfc98'
sdk = TracupSDK(api_key, u_key)

# 接下来定义一个函数用来过滤HTML标签


def filter_html(content):
    pat = re.compile('(?<=\>).*?(?=\<)')
    after_filter_contents = pat.findall(content)
    return ''.join(after_filter_contents)


# 获得问题所有状态的key
issueStatus = sdk.get_qestion_status(p_key)
status_key = [i['key'] for i in issueStatus.get('status', [])]
all_issues = []

for s in status_key:
    for page in range(1, 9):
        result = sdk.get_qestion_list(p_key, s, page)
        if result['list'] is None:
            continue
        all_issues = all_issues + result['list']

issueNo = []  # 项目全部问题的issuekey

# 现在开始遍历问题拿到备注
for q in all_issues:
    q.pop('projectModuleKey')
    q.pop('assigneeAvator')
    q.pop('projectTypeKey')
    q.pop('userAvator')
    q.pop('issueTypeBackground')
    q.pop('issueStatus')
    q.pop('issueKey')
    q.pop('hasFile')
    q.pop('issueFinished')
    comments = sdk.get_issue_comment(p_key, q['issueNo'])

    q['issue_final_comment'] = ''
    if comments['list'] is None:
        continue
    issue_note_list = []
    for comment in comments['list']:
        issue_note_list.append('[{}]{}'.format(
            comment['userName'], filter_html(comment['issueNote'])))

    q['issue_final_comment'] = '\r\n'.join(issue_note_list)
    pprint('正在载入%s' % (q['issueNo']))

tittle = sorted(all_issues[0].keys())  # 获取所有列名

pprint(all_issues)

# with open('tracup.csv', 'w', newline='') as csvFile:
#     # 表头在这里传入，作为第一行数据
#     writer = csv.DictWriter(csvFile, tittle)
#     writer.writeheader()
#     # 还可以写入多行
#     writer.writerows(all_issues)
