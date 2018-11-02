from tracup import TracupSDK
from pprint import pprint
import xlsxwriter
import xlrd
import datetime
import numpy as np 
import pandas as pd
from collections import Counter
from xlsxwriter.utility import xl_rowcol_to_cell

u_key = '414a471ef24654e6b8413416a5048238'
api_key = '6e238511179b6aeadf1e26fed1f6db07'

sdk = TracupSDK(api_key, u_key)

projects = sdk.get_all_project()
all_project = projects.get('participantProjectList', []) + \
    projects.get('createdProjectList', [])
for i, p in enumerate(all_project):
    print('[{}].{}'.format(i, p.get('projectName')))

project_seleced = int(input('请选择需要导出的项目：'))

if not all_project[project_seleced]:
    print('项目不存在，拜拜👋')
    exit

exist_project = all_project[project_seleced]
p_key = exist_project.get('projectKey', '')
p_name = exist_project.get('projectName', '')

project_question_status = sdk.get_qestion_status(p_key)['status']
# print(project_question_status)

all_issues = []
for status in project_question_status:
    status_questions = sdk.get_qestion_list(p_key, status.get('key'))
    if status_questions is None:
        continue
    all_issues = all_issues + status_questions

statistics = {}
for issue in all_issues:
    key = '{}.{}'.format(
        issue.get('issueModule'),
        issue.get('issueType'),
    )
    if key not in statistics.keys():
        statistics[key] = {}
    if issue.get('issueStatusText') not in statistics[key]:
        statistics[key][issue.get('issueStatusText')] = 0
    statistics[key][issue.get('issueStatusText')] += 1

project_type = sdk.get_qestion_type(p_key)
project_type_map = {}
# project_type_names = [project['projectTypeName'] for project in project_type.get('list', [])]

filename = '{}({}).xlsx'.format(p_name, datetime.date.today())
wb = xlsxwriter.Workbook(filename)
sheet = wb.add_worksheet('sheet1')  # 新增一张工作表sheet1

header_cell_format = wb.add_format({
    'align': 'center',
    'bold': True,
    'font_size': 14,
    'border': 1
})
# 表头
sheet.write(0, 0, '模块', header_cell_format)
sheet.write(0, 1, '类型', header_cell_format)

header_cursor = 2

for status in project_question_status:
    sheet.write(0, header_cursor, status['label'], header_cell_format)
    header_cursor = header_cursor + 1
after_sored_result = sorted(statistics.items(), key=lambda item: item[0])

cell_format = wb.add_format({
    'align': 'center',
    'valign': 'vcenter',
    'bold': True,
    'bg_color': 'yellow',
    'border': 1
})
cell_format_value = wb.add_format({
    'align': 'center',
    'valign': 'vcenter',
    'border': 1
})
# 表数据
start_row_index = 1
col_index = 2
module_list = []
for item in after_sored_result:
    key, item = item
    module_name, status_name = key.split('.')
    module_list.append(module_name)
    sheet.write(start_row_index, 0, module_name, cell_format)
    sheet.write(start_row_index, 1, status_name, cell_format)

    for i, status in enumerate(project_question_status):
        value = 0
        status_text = status['label']
        if status_text in item:
            value = item[status_text]
        sheet.write(start_row_index, col_index + i, value, cell_format_value)
    start_row_index += 1

# 合并单元格
merge_first_row = 1
after_sored_result1 = sorted(
    Counter(module_list).items(), key=lambda item: item[0])
for value in after_sored_result1:
    module, value = value
    if value < 2:
        sheet.write(merge_first_row + value - 1, 0, module, cell_format)
        continue
    end_row = merge_first_row + value - 1
    sheet.merge_range(merge_first_row, 0, end_row, 0, module, cell_format)
    merge_first_row = end_row + 1
weizhi_col = len(project_question_status) + 2
weizhi_row = 0
sheet.write(weizhi_row,weizhi_col,'汇总')
sheet.write(weizhi_row,weizhi_col+1,'模块BUG总数')

while True:
    if weizhi_row == len(statistics):
        break  
    cell_begin = xl_rowcol_to_cell(weizhi_row+1, 3)
    cell_end = xl_rowcol_to_cell(weizhi_row+1, weizhi_col)
    weizhi_row = weizhi_row + 1
wb.close()

df = xlrd.open_workbook(filename)
table = df.sheet_by_name(u'sheet1')


print(sum(table.row_valus(2)))