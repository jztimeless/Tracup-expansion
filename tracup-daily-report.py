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
for status in status_key:
    issues = t.get_qestion_list(p_key,status)
    if issues is None:
        continue

    all_issues = all_issues + issues

# 取到全部模块、状态类型
issue_module_type = []
for issue in all_issues:
    issue_module_type.append([issue.get('issueModule'), issue.get(
        'issueType', [])])

# 去除重复
issue_module_type = list(set([tuple(t) for t in issue_module_type]))
issue_module_type = [list(v) for v in issue_module_type]
issue_module_type.sort()

for issue in all_issues:
    for i in issue_module_type:
        if issue.get('issueModule') == i[0] and issue.get('issueType') == i[1]:
            i.append(issue.get('issueStatusText'))


project_status = t.get_qestion_status(p_key)

result = []
for issue1 in issue_module_type:
    prefix = issue1[0:2]
    for b in project_status['status']:
        prefix.append(issue1.count(b['label']))
    result.append(prefix)

wb = xlsxwriter.Workbook('tracup.xlsx')
sheet = wb.add_worksheet('sheet1')  # 新增一张工作表sheet1

header_cell_format = wb.add_format({
    'align': 'center',
    'bold': True,
    'font_size': 14,
    'border': 1
})

# 生成表头
project_status = t.get_qestion_status(p_key)['status']
sheet.write(0, 0, '模块', header_cell_format)
sheet.write(0, 1, '状态', header_cell_format)

n = 2
for i in project_status:
    sheet.write(0, n, i['label'], header_cell_format)
    n = n + 1

start_row_index = 1
col_index = 1
summary = {}

# for item in after_sored_result:
#     key, item = item
#     module_name, status_name = key.split('.')
#     sheet.write(start_row_index, 0, module_name)
#     sheet.write(start_row_index, 1, status_name)

#     for i, status in enumerate(project_question_status.get('status', [])):
#         value = 0
#         status_text = status['label']
#         if status_text in item:
#             value = item[status_text]
#         sheet.write(start_row_index, col_index + i, value)
#     start_row_index += 1

# wb.close()

# 生成表格内容
len_list = len(result)
module_list = []

for i in range(len_list):
    print(u'正在写入第'+str(i+1)+u'行……')
    row_value = result[i]
    module_list.append(row_value[0])

    len_row = len(row_value)
    for j in range(len_row):
        sheet.write(start_row_index, col_index + i, row_value[j])
    start_row_index += 1

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
