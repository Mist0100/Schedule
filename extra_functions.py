import re
import pandas as pd


def find_group(string: str, mode: str = 'simple') -> bool | dict:
    """
    Проверка принадлежности строки к группам обучения
    :param string: строка для проверки
    :param mode: режим вывода. 'simple' -> bool, 'mid' -> dict{keys = [branch, group_num, group_postfix,
     year_of_admission]}, 'full' -> dict{keys = [branch, institute, form_of_education, group_num, group_postfix,
      year_of_admission]}

    :return: bool | dict
    """
    nums = '1234567890'
    if string[-1] in nums and string[-2] in nums and string[-3] == '-':
        if mode == 'simple':
            return True

        elif mode == 'mid':
            first = string.find('-')
            second = string.find('-', first + 1)
            branch = string[0:first]
            group_num = re.sub(r'\D', '', string[first + 1:second])
            group_postfix = re.sub(r'\d', '', string[first + 1:second])
            year_of_admission = string[second + 1: len(string)]

            out = {
                'branch': branch,
                'group_num': group_num,
                'group_postfix': group_postfix,
                'year_of_admission': year_of_admission
            }

            return out

        elif mode == 'full':
            first = string.find('-')
            second = string.find('-', first + 1)
            n_list = re.findall(r'\d+', string)
            if len(n_list) > 2:
                institute = n_list[0]
                form_of_education = string[string.find(institute) + len(institute):first]
                branch = string[0: string.find(institute)]
                group_num = n_list[1]
                year_of_admission = n_list[2]
                group_postfix = string[string.find(group_num) + len(group_num):second]
            else:
                branch = string[0]
                form_of_education = string[first - 1]
                institute = string[1: first - 1]
                group_num = n_list[0]
                year_of_admission = n_list[1]
                group_postfix = string[string.find(group_num) + len(group_num):second]

            out = {
                'branch': branch,
                'institute': institute,
                'form_of_education': form_of_education,
                'group_num': group_num,
                'group_postfix': group_postfix,
                'year_of_admission': year_of_admission
            }

            return out
    else:
        return False


def check_flow(group1: str, group2: str) -> bool:
    """
    Проверка принадлежности двух груп к одному и тому же потоку
    :param group1: группа для проверки
    :param group2: группа для проверки
    :return: bool
    """
    group1 = find_group(group1, mode='mid')
    group2 = find_group(group2, mode='mid')
    if group1 and group2:
        if (group1['branch'] == group2['branch'] and
                group1['group_num'] != group2['group_num'] and group1['group_postfix'] == group2['group_postfix'] and
                group1['year_of_admission'] == group2['year_of_admission']):
            return True
        else:
            return False


def flow_distribution(groups: list, hpg: list) -> dict:
    """
    Распределяет группы по потокам по номеру групп
    :param groups: массив групп
    :param hpg: массив словарей hours_per_group
    :return: dict{keys=[flows, hours_per_flow]} для встраивания
    """
    out = {'flows': [], 'hours_per_flow': []}
    groups_bool = [False for _ in groups]

    while False in groups_bool:
        ind = groups_bool.index(False)
        out['flows'].append([groups[ind]])
        groups_bool[ind] = True
        out['hours_per_flow'].append([hpg[ind]])

        for i, group in enumerate(groups):
            if not groups_bool[i]:
                if check_flow(group, out['flows'][-1][-1]):
                    out['flows'][-1].append(group)
                    out['hours_per_flow'][-1].append(hpg[i])
                    groups_bool[i] = True

    return out


def schedule_table_load(path: str) -> tuple:
    """
    Загрузка расписания из excel таблицы
    :param path: путь к файлу
    :return: turple(disciplines, errors, [header, kaf, year])
    """
    table = pd.read_excel(path)
    table = table.map(lambda x: x.replace('\n', '') if isinstance(x, str) else x)
    table = table.replace({float('nan'): None})

    group_bools = [False for _ in range(table.shape[0])]
    disciplines = []
    errors = []
    none_titles_rows = []

    header = 'Н/н'
    kaf = 'Н/н'
    year = 'Н/н'

    n = 0

    sem = None
    prev = None
    labs_base = None
    discipline = {'title': None, 'flows': [], 'hours_per_flow': [], 'groups': [], 'hours_per_group': [], 'sem': ''}
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
                if 'семестр' in row[0].lower():
                    if 'осен' in row[0].lower():
                        sem = 'autumn'
                    elif 'весен' in row[0].lower():
                        sem = 'summer'

                if find_group(row[0]):
                    group_bools[i] = True
                    if row[14] >= 20 and row[23] and row[23] != 2:
                        errors.append(['W', f'Строка {i + 1}: кол-во часов по ЛР не умножено на два'])
                    if row[25] and row[25] != row[14] * 2:
                        errors.append(f'Строка {i + 1}: неверное кол-во часов по КР')

                else:
                    labs_base = None
                if 'руководство кафедрой' in row[0].lower():
                    disciplines.append({'title': row[0], 'flows': [None],
                                        'hours_per_flow': [row[48]], 'groups': [None],
                                        'hours_per_group': [row[48]], 'sem': sem})

            if group_bools[i] and not group_bools[i - 1]:
                discipline = {'title': prev[0], 'flows': [], 'hours_per_flow': [], 'groups': [], 'hours_per_group': [],
                              'sem': sem}
                if not prev[0]:
                    none_titles_rows.append([i - 1, len(disciplines)])

                if row[24] and row[23]:
                    labs_base = row[24] / row[23]
            elif group_bools[i] and group_bools[i - 1]:
                if not check_flow(prev[0], row[0]) and not row[18] and row[11]:
                    errors.append(['W', f'Строка {i + 1}: неверное распределение групп по потокам'])
                elif not check_flow(prev[0], row[0]) and row[18]:
                    if row[24] and row[23]:
                        labs_base = row[24] / row[23]
                elif check_flow(prev[0], row[0]):
                    if (bool(prev[24]) and not bool(row[24]) and
                            (f'Строка {i + 1}: пропущенные ячейки ЛР у групп одного потока' not in errors)):
                        errors.append(['E', f'Строка {i + 2}: пропущенные ячейки ЛР у групп одного потока'])
                    if labs_base and prev[24] and prev[23] and labs_base != prev[24] / prev[23]:
                        errors.append(['W', f'Строка {i + 1}: неверное кол-во часов по ЛР у групп одного потока'])
                    if row[11] and prev[11] and row[18] and prev[18] and row[18] != prev[18]:
                        errors.append(['W', f'Строка {i + 1}: неверное распределение групп по потокам'])

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

                    discipline['hours_per_group'].append({'LK': prev[16],
                                                          'PZ': prev[21],
                                                          'LR': prev[24],
                                                          'KR': prev[25],
                                                          'Other': other
                                                          })

            if group_bools[i - 1] and not group_bools[i]:
                fd = flow_distribution(discipline['groups'], discipline['hours_per_group'])
                discipline.update(fd)
                disciplines.append(discipline)

        prev = row

    if none_titles_rows:
        col = table[table.columns[0]].to_list()
        col.reverse()
        col_l = len(col)
        for ntr in none_titles_rows:
            for cell in col[col_l - ntr[0]:col_l]:
                if cell and not find_group(cell):
                    disciplines[ntr[1]]['title'] = cell
                    break

    return disciplines, errors, [header, kaf, year]


if __name__ == '__main__':
    print(check_flow('М1О-413Бки-21', 'М1О-442Бки-21'))
