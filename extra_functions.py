import re


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


if __name__ == '__main__':
    print(check_flow('М1О-413Бки-21', 'М1О-442Бки-21'))
