import re
import pandas as pd
from extra_functions import find_group, check_flow

table = pd.read_excel(r'resources/Нагрузка кафедра.xlsx')
table = table.map(lambda x: x.replace('\n', '') if isinstance(x, str) else x)
table = table.replace({float('nan'): None})

group_bools = [False for _ in range(table.shape[0])]
disciplines = []
errors = []

header = 'Н/н'
kaf = 'Н/н'
year = 'Н/н'

prev = None
labs_base = None
discipline = {'title': None, 'flows': [], 'hours_by_flow': [], 'groups': [], 'hours_by_group': []}
for i, row in enumerate(table.iloc):
    row = row.to_list()
    if i == 0:
        try:
            header = next(item for item in row if item is not None).lower()
            ind = header.find('кафедр')
            ind2 = header.find(' ', ind + 8)
            kaf = re.sub(r'\D', '', header[ind + 8: ind2])
            year = header[ind2 + 1: ind2 + 8]
        except StopIteration:
            pass

    else:
        if row[0]:
            if find_group(row[0]):
                group_bools[i] = True
                if row[14] >= 20 and row[23] and row[23] != 2:
                    errors.append(f'Строка {i + 1}: кол-во часов по ЛР не умножено на два')
                if row[25] and row[25] != row[14]*2:
                    errors.append(f'Строка {i + 1}: неверное кол-во часов по КР')

            else:
                labs_base = None
            if 'Руководство кафедрой' in row[0]:
                disciplines.append(row[0]) # TODO сделать нормально

        if group_bools[i] and not group_bools[i-1]:
            discipline = {'title': prev[0], 'flows': [], 'hours_by_flow': [], 'groups': [], 'hours_by_group': []}
            if row[24] and row[23]:
                labs_base = row[24] / row[23]
        elif group_bools[i] and group_bools[i-1]:
            if not check_flow(prev[0], row[0]) and not row[18] and row[11]:
                errors.append(f'Строка {i + 1}: неверное распределение групп по потокам')
            elif not check_flow(prev[0], row[0]) and row[18]:
                if row[24] and row[23]:
                    labs_base = row[24]/row[23]
            elif check_flow(prev[0], row[0]):
                if (bool(prev[24]) and not bool(row[24]) and
                        (f'Строка {i + 1}: пропущенные ячейки ЛР у групп одного потока' not in errors)):
                    errors.append(f'Строка {i + 2}: пропущенные ячейки ЛР у групп одного потока')
                if labs_base and prev[24] and prev[23] and labs_base != prev[24]/prev[23]:
                    errors.append(f'Строка {i + 1}: неверное кол-во часов по ЛР у групп одного потока')
                if row[11] and prev[11] and row[18] and prev[18] and row[18] != prev[18]:
                    errors.append(f'Строка {i + 1}: неверное распределение групп по потокам')

        if prev[0] and find_group(prev[0]):
            if prev[0] not in discipline['groups']:
                discipline['groups'].append(prev[0])
                other = 0
                if prev[32]:
                    other += prev[32]
                if prev[36]:
                    other += prev[36]
                if prev[37]:
                    other += prev[37]
                if prev[42]:
                    other += prev[42]
                if prev[38]:
                    other += prev[38]

                discipline['hours_by_group'].append({'LK': prev[16],
                                                     'PZ': prev[21],
                                                     'LR': prev[24],
                                                     'KR': prev[25],
                                                     'Other': other
                                                     })

        if group_bools[i-1] and not group_bools[i]:
            disciplines.append(discipline)

    prev = row

    # print(row)

print(table.iloc[-2])
print(disciplines[0])
print(errors, len(errors))
