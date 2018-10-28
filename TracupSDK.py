# -*- coding: utf-8 -*-
import csv
import re
import xlsxwriter
from pprint import pprint
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

issue_status_type = []
issue_status_type1 = []
issue_status_type2 = []
issue_status_type3 = []
issue_status_type4 = []

# 取到各个模块下的问题列表
for issue in all_issues:
    if issue['list'] == None:
        continue
    for q in issue['list']:
        issue_status_type1 = q.get('issueModule'), q.get(
            'issueStatusText', []), q.get('issueType', [])

        issue_status_type.append(issue_status_type1)
        # issue_status_type2[issue_status_type1] = issue_status_type.count(issue_status_type1)
    # pprint(issue_status_type2)

    issue_status_type.sort()
project_type = t.get_qestion_type(p_key)['list']

issue_status_type3 = list(set(issue_status_type))
issue_status_type3.sort()
for i in issue_status_type3:
    issue_status_type2 = ['{}{}'.format(i,issue_status_type.count(i))]
    issue_status_type4.append(issue_status_type2)


pprint(issue_status_type2)


wb = xlsxwriter.Workbook('tracup.xlsx')
sheet = wb.add_worksheet('sheet1')  # 新增一张工作表sheet1

# 生成表头
sheet.write(0, 0, '模块')
sheet.write(0, 1, '状态')
n = 2
for i in project_type:
    sheet.write(0, n, i['projectTypeName'])
    n = n + 1

# 生成表格内容

len_list = len(issue_status_type4)
for i in range(len_list):
    # print(u'正在写入第'+str(i+1)+u'行……')
    row_value = issue_status_type4[i]
    len_row = len(row_value)
    for j in range(len_row):
        sheet.write(i+1, j, row_value[j])


wb.close()
print(u'写入完毕，excel文件已生成！')
