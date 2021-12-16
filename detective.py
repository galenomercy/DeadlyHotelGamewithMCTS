from copy import deepcopy
import os
from random import randint
import numpy as np
from model import find_short_path, ROOM_CENTER, get_square_position, ROLE_WEAPON, SQUARE

roles = ['writer', 'waitress', 'cleaner']
weapon_room = {
    'knife': 'G',
    'poison': 'H',
    'rope': 'I'
}
# max = 100
doubt = {role: 0 for role in roles}
'''
1. At the time of the murder, or before and after the murder, 
if the distance between the witnessed position of the other two characters AB 
and the murder room is too far for AB to reach the murder room, then C must be the murderer

2. Repeatedly enter one room, increase the value of suspicious

3. Before the murder, who was witnessed to enter the murder weapon room, increased the suspicious value

4. Who has never been witnessed, and the suspicious value is increased

5. Enter the murder weapon room, and the recorded position before and after the murder is 
enough to reach the murder room, increasing the suspicious value



'''


def time_required_for_murder(role, weapon):
    if weapon == ROLE_WEAPON[role]:
        return 1
    else:
        return 2


class Witness:
    def __init__(self, roles, room_or_position, round) -> None:
        self.roles = roles
        self.room_or_position = room_or_position
        self.is_room = False
        self.is_num = False
        if room_or_position[0].isalpha():
            self.is_room = True
        else:
            self.is_num = True
        self.round = int(round)

    def get_roles(self):
        return self.roles[0], self.roles[1]

    def is_in_room(self):
        return self.is_room

    def get_room(self):
        return self.room_or_position[0]

    def get_square(self, role):
        if role == self.roles[0]:
            return self.room_or_position[0]
        else:
            return self.room_or_position[1]

    def get_round(self):
        return self.round


class DeadInfo:
    def __init__(self, weapon, position, round) -> None:
        self.weapon = weapon
        self.position = position
        self.round = int(round)

    def get_weapon(self):
        return self.weapon

    def get_round(self):
        return self.round

    def get_room(self):
        return self.position


def remove_symbols(line):
    import string
    del_estr = string.punctuation
    replace = " " * len(del_estr)
    tran_tab = str.maketrans(del_estr, replace)
    line = line.translate(tran_tab)
    return line


def process_data(report):
    result = []
    for i in report:
        if len(i) == 0:
            continue
        i = str(i)
        l = remove_symbols(i)
        l = l.split()
        if l[0] == 'victim':
            dead_info = DeadInfo(l[4], l[6], l[8])
            continue
        result.append(Witness([l[0], l[1]], [l[2], l[3]], l[4]))
    result.sort(key=lambda x: x.get_round())
    result = {
        'witness': result,
        'dead_info': dead_info
    }
    return result


def deal_with_the_two_witnesses_closest_to_death(report):
    dead_info = report['dead_info']
    dead_round = dead_info.get_round()
    witness_reports = report['witness']
    before_witness = None
    after_witness = None
    for witness_report in witness_reports:
        round = witness_report.get_round()
        if round < dead_round:
            before_witness = witness_report
        if round >= dead_round:
            after_witness = witness_report
            break
    if before_witness == after_witness and before_witness.is_in_room() and before_witness.get_room() != dead_info.get_room():
        r1, r2 = before_witness.get_roles()
        for i in doubt:
            if i == r1 or i == r2:
                continue
            else:
                doubt[i] += 100
        return
    if before_witness == after_witness and before_witness.is_in_room() and before_witness.get_room() == dead_info.get_room():
        r1, r2 = before_witness.get_roles()
        doubt[r1] += 60
        doubt[r2] += 60
        return
    judge_short_path_using_round(before_witness, dead_info, True)
    judge_short_path_using_round(after_witness, dead_info, False)


def judge_short_path_using_round(witness, dead_info, need_murder):
    if witness == None:
        return
    dead_round = dead_info.get_round()
    r1, r2 = witness.get_roles()
    delta_round = abs(int(dead_round) - int(witness.get_round()))
    position = 0
    if witness.is_in_room():
        position = ROOM_CENTER[witness.get_room()][0]
        position = SQUARE[position]
        position = deepcopy(position)
        position.pop(2)
        path = find_short_path(position, dead_info.get_room())
        if len(path) > delta_round:
            for i in doubt:
                if i == r1 or i == r2:
                    continue
                else:
                    if witness.get_round() < dead_round:
                        doubt[i] += 100
    else:
        position1 = witness.get_square(r1)
        position1 = get_square_position(int(position1))
        path1 = find_short_path(position1, dead_info.get_room())
        position2 = witness.get_square(r2)
        position2 = get_square_position(int(position2))
        path2 = find_short_path(position2, dead_info.get_room())
        if need_murder:
            flag1 = 0
            flag2 = 0
            if len(path1) + time_required_for_murder(r1, dead_info.get_weapon()) <= delta_round:
                doubt[r1] += 30
                flag1 = 1
            if len(path2) + time_required_for_murder(r2, dead_info.get_weapon()) <= delta_round:
                doubt[r2] += 30
                flag2 = 1
            if flag1 == 0 and flag2 == 0:
                for i in doubt:
                    if i == r1 or i == r2:
                        continue
                    doubt[i] += 100
        else:
            if len(path1) <= delta_round:
                doubt[r1] += 15
            if len(path2) <= delta_round:
                doubt[r2] += 15


def repeat_entry_into_the_same_room(witness_reports):
    enter_count = {role: 0 for role in roles}
    enter = {role: set() for role in roles}
    for witness_report in witness_reports:
        r1, r2 = witness_report.get_roles()
        if witness_report.is_in_room():
            room = witness_report.get_room()
            if room in enter[r1]:
                enter_count[r1] += 1
            if room in enter[r2]:
                enter_count[r2] += 1
    for i in enter_count:
        if enter_count[i] > 2:
            # 可以使用指数函数/分段函数
            doubt[i] += 2


def enter_the_murder_weapon_room(report):
    weapon = report['dead_info'].get_weapon()
    dead_room = report['dead_info'].get_round()
    room = weapon_room[weapon]
    witness_reports = report['witness']
    for witness_report in witness_reports:
        if witness_report.is_in_room():
            witness_room = witness_report.get_room()
            if room == witness_room and witness_report.get_round() < dead_room:
                r1, r2 = witness_report.get_roles()
                doubt[r1] += 8
                doubt[r2] += 8


def not_witnessed(witness_reports):
    witness_count = {role: 0 for role in roles}
    for witness_report in witness_reports:
        r1, r2 = witness_report.get_roles()
        witness_count[r1] += 1
        witness_count[r2] += 1
    for i in witness_count:
        if witness_count[i] == 0:
            doubt[i] += 5


def job(report_dir):
    result = []
    for report_file in os.listdir(report_dir):
        if not report_file.endswith('.txt') or report_file.find('answer') != -1:
            continue
        report_path = os.path.join(report_dir, report_file)
        report = open(report_path, 'r').read().split('\n')
        report = process_data(report)
        deal_with_the_two_witnesses_closest_to_death(report)
        repeat_entry_into_the_same_room(report['witness'])
        enter_the_murder_weapon_room(report)
        not_witnessed(report['witness'])
        rank = []
        for i in doubt:
            rank.append([i, doubt[i]])
        rank.sort(key=lambda x: x[1])
        result.append([report_file, rank])
        for i in doubt:
            doubt[i] = 0
    result.sort(key=lambda x: x[0])
    for i in result:
        print(i[0], i[1][2][0])


def detect(report):
    for i in doubt:
        doubt[i] = 0

    report = process_data(report.split('\n'))
    deal_with_the_two_witnesses_closest_to_death(report)
    repeat_entry_into_the_same_room(report['witness'])
    enter_the_murder_weapon_room(report)
    not_witnessed(report['witness'])
    rank = []
    for i in doubt:
        rank.append([i, doubt[i]])
    rank.sort(key=lambda x: x[1])
    return rank


if __name__ == '__main__':
    job('report')
