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
p_key = 'a6a5891ca82e0ff3b60a2c1fba3cfc98'

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

# 取到全部模块、状态类型
issue_module_status = []
for issue in all_issues:
    if issue['list'] is None:
        continue
    for q in issue['list']:
        issue_module_status.append([q.get('issueModule'), q.get(
            'issueStatusText', [])])

# 去除重复
issue_module_status = list(set([tuple(t) for t in issue_module_status]))
issue_module_status = [list(v) for v in issue_module_status]
issue_module_status.sort()


for issue in all_issues:
    if issue['list'] is None:
        continue
    for q in issue['list']:
        for i in issue_module_status:
            if q.get('issueModule') == i[0] and q.get('issueStatusText') == i[1]:
                i.append(q.get('issueType'))
# pprint(issue_module_status)
project_type = t.get_qestion_type(p_key)['list']

result = []
for issue1 in issue_module_status:
    prefix = issue1[0:2]
    for b in project_type:
        prefix.append(issue1.count(b['projectTypeName']))
        # issue1 = issue1.count(b['projectTypeName'])
    result.append(prefix)

    # print()

wb = xlsxwriter.Workbook('tracup.xlsx')
sheet = wb.add_worksheet('sheet1')  # 新增一张工作表sheet1

header_cell_format = wb.add_format({
    'align': 'center',
    'bold': True,
    'font_size': 14,
    'border': 1
})

# 生成表头
project_type = t.get_qestion_type(p_key)['list']
sheet.write(0, 0, '模块', header_cell_format)
sheet.write(0, 1, '状态', header_cell_format)
n = 2
for i in project_type:
    sheet.write(0, n, i['projectTypeName'], header_cell_format)
    n = n + 1

# 生成表格内容


len_list = len(result)

module_list = []

for i in range(len_list):
    # print(u'正在写入第'+str(i+1)+u'行……')
    row_value = result[i]
    module_list.append(row_value[0])

    len_row = len(row_value)
    for j in range(len_row):
        sheet.write(i+1, j, row_value[j],)

merge_first_row = 1

cell_format = wb.add_format({
    'align': 'center',
    'valign': 'vcenter',
    'bold': True,
    'bg_color': 'yellow',
    'border': 1
})

for key, value in Counter(module_list).items():
    if value < 2:
        sheet.write(merge_first_row + value - 1, 0, key, cell_format)
        continue
    end_row = merge_first_row + value - 1
    sheet.merge_range(merge_first_row, 0, end_row, 0, key, cell_format)
    merge_first_row = end_row + 1

wb.close()
print(u'写入完毕，excel文件已生成！')
