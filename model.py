import random
import copy

# good at which weapon
ROLE_WEAPON = {
    'cleaner': 'knife',
    'writer': 'rope',
    'waitress': 'poison',
    'victim': None
}
# all roles
ROLE = [
    'cleaner',
    'writer',
    'waitress',
    'victim'
]
# all weapons
WEAPON = [
    'knife',
    'rope',
    'poison'
]
# X-axis
MAX_X = 12
# Y-axis
MAX_Y = 8
# every square in interface
SQUARE = [[x, y, 0] for x in range(MAX_X) for y in range(MAX_Y)]
# roles' original position
# victim need to be in guest rooms
RANGE = {
    'victim': [2, 18, 34, 50, 66, 82],
    'knife': [5, 6, 7, 13, 14, 15, 21, 22, 23],
    'poison': [45, 46, 47, 53, 54, 55, 61, 62, 63],
    'rope': [85, 86, 87, 93, 94, 95]
}
# length of square
LENGTH = 66
# center the img
FIX = [10, 10 + 263]
# room square
ROOM = {
    'A': [0, 1, 2, 8, 9, 10],
    'B': [16, 17, 18, 24, 25, 26],
    'C': [32, 33, 34, 40, 41, 42],
    'D': [48, 49, 50, 56, 57, 58],
    'E': [64, 65, 66, 72, 73, 74],
    'F': [80, 81, 82, 88, 89, 90],
    'G': [5, 6, 7, 13, 14, 15, 21, 22, 23],
    'H': [45, 46, 47, 53, 54, 55, 61, 62, 63],
    'I': [85, 86, 87, 93, 94, 95]
}
# make room only one square
ROOM_CANT_GO = {
    'A': [0, 1, 8, 9, 10],
    'B': [16, 17, 24, 25, 26],
    'C': [32, 33, 40, 41, 42],
    'D': [48, 49, 56, 57, 58],
    'E': [64, 65, 72, 73, 74],
    'F': [80, 81, 88, 89, 90],
    'G': [5, 6, 7, 15, 21, 23],
    'H': [45, 47, 55, 61, 63],
    'I': [85, 87, 95]
}
# all rooms
ROOM_LIST = list(ROOM.keys())
ROOM_ENTRANCE = {
    'A': [2],
    'B': [18],
    'C': [34],
    'D': [50],
    'E': [66],
    'F': [82],
    'G': [13, 22],
    'H': [46, 53, 62],
    'I': [86, 93]
}
# accessible part of rooms
ROOM_CENTER = {
    'A': [2],
    'B': [18],
    'C': [34],
    'D': [50],
    'E': [66],
    'F': [82],
    'G': [14],
    'H': [54],
    'I': [94]
}
# out of the room
ROOM_OUT = {
    'A': [  # roomA
        [[0, 1]],
        [3]
    ],
    'B': [
        [[0, 1]],
        [19]
    ],
    'C': [
        [[0, 1]],
        [35]
    ],
    'D': [
        [[0, 1]],
        [51]
    ],
    'E': [
        [[0, 1]],
        [67]
    ],
    'F': [
        [[0, 1]],
        [83]
    ],
    'G': [
        [[1, 0], [0, -1]],  # right or up
        [30, 12]  # go to 30/12
    ],
    'H': [
        [[-1, 0], [0, -1], [1, 0]],
        [38, 52, 70]
    ],
    'I': [
        [[-1, 0], [0, -1]],
        [78, 92]
    ]
}
# square number of report
SQUARE_NUM_MAP = {3: 1, 4: 2, 11: 3, 12: 4, 19: 5, 20: 6, 27: 7, 28: 8, 29: 9, 30: 10, 31: 11, 35: 12, 36: 13, 37: 14,
                  38: 15, 39: 16, 43: 17, 44: 18,
                  51: 19, 52: 20, 59: 21, 60: 22, 67: 23, 68: 24, 69: 25, 70: 26, 71: 27, 75: 28, 76: 29, 77: 30,
                  78: 31, 79: 32, 83: 33, 84: 34, 91: 35, 92: 36}

# print('{', end='')
# j = 1
# for i in range(len(SQUARE)):
#     if SQUARE[i][1] == 3 or SQUARE[i][1] == 4 or (SQUARE[i][1] >= 5 and SQUARE[i][0] in [3, 4, 8, 9]):
#         print(str(i)+':'+str(j), end=',')
#         j += 1
# print('}')

# print('[', end='')
# for i in range(len(SQUARE)):
#     if SQUARE[i][0] >= 10 and SQUARE[i][0] <= 11 and SQUARE[i][1] >= 0 and SQUARE[i][1] <= 2:
#         print(i, end=',')
# print(']')

NOT_IN_ROOM = '@'


# square


def in_which_square(box):
    x = box[0]
    y = box[1]
    for i in SQUARE:
        if i[0] == x and i[1] == y:
            index = SQUARE.index(i)
            return index


# room


def in_room_helper(box, room_data):
    index = in_which_square(box)
    for i in room_data:
        if index in room_data[i]:
            return i
    return NOT_IN_ROOM


def in_which_room(box):
    return in_room_helper(box, ROOM)


def is_in_the_room_center(box):
    return in_room_helper(box, ROOM_ENTRANCE)


# if meet


def is_box_adjacent(box1, box2):
    x1 = box1[0]
    y1 = box1[1]
    x2 = box2[0]
    y2 = box2[1]
    if x1 == x2 and y1 == y2:
        return True
    if x1 == x2 and (y1 == y2 - 1 or y1 - 1 == y2):
        return True
    if (x1 - 1 == x2 or x1 == x2 - 1) and y1 == y2:
        return True


def from_square_to_no(square):
    return str(SQUARE_NUM_MAP[square])


# define accessible room square
def can_go(source, destination):
    if in_room_helper(source, ROOM) == NOT_IN_ROOM and in_room_helper(destination, ROOM_CANT_GO) != NOT_IN_ROOM:
        return False

    if in_room_helper(source, ROOM_CENTER) != NOT_IN_ROOM and in_room_helper(destination, ROOM_CANT_GO) != NOT_IN_ROOM:
        return False
    return True


# random path
def get_random_path(start):
    room = in_which_room(start)
    rooms = ROOM_LIST.copy()
    rooms.remove(room)
    # shuffle
    random.shuffle(rooms)
    all_paths = []
    for i in rooms:
        p = find_short_path(start, i)
        all_paths = all_paths + p
        start = all_paths[-1]
    return all_paths


# shortest path
def find_short_path(source, des_room):
    if in_room_helper(source, ROOM_CENTER) == des_room:
        return []
    queue = list()
    source_ = source.copy()
    source_.append(-1)
    queue.append(source_)
    direction = [
        [-1, 0],
        [0, -1],
        [1, 0],
        [0, 1]
    ]
    visited = copy.deepcopy(SQUARE)
    # using BFS
    while len(queue) != 0:
        head = queue.pop(0)
        if in_room_helper(head, ROOM_CENTER) == des_room:
            break
        for i in direction:
            room = in_room_helper(head, ROOM_CENTER)
            next_ = [head[0] + i[0], head[1] + i[1]]
            # if can go or not
            if 0 <= next_[0] and next_[0] < MAX_X and 0 <= next_[1] and next_[1] < MAX_Y:
                pass
            else:
                continue
            # if the old step
            if visited[in_which_square(next_)][2] == 1:
                continue
            # if in room
            if room != NOT_IN_ROOM:
                directions = ROOM_OUT[room][0]
                next_index = None
                # whether can go out
                for d in directions:
                    if d == i:
                        next_index = ROOM_OUT[room][1][directions.index(d)]
                        break
                # can't go out，wrong direction
                if next_index is None:
                    continue
                # out，update to queue
                next_ = SQUARE[next_index].copy()
                next_.pop()
                # record last step
                next_.append(head)
                queue.append(next_)
                visited[in_which_square(next_)][2] = 1
                continue
            # not in room
            if can_go(head, next_):
                # in room or not
                room = in_room_helper(next_, ROOM_ENTRANCE)
                # update to room center
                if room != NOT_IN_ROOM:
                    next_ = SQUARE[ROOM_CENTER[room][0]].copy()
                    next_.pop()
                next_.append(head)
                queue.append(next_)
                visited[in_which_square(next_)][2] = 1
    path = []
    while True:
        # get path
        path.append([head[0], head[1]])
        head = head[2]
        if head == -1:
            break
    path.pop()
    path.reverse()
    return path


# get_random_path([0,2])
# find_short_path([2,2], 'H')

# get random birth room
def get_random_index(name, is_killer):
    while True:
        if name in RANGE:
            index = random.randint(0, len(RANGE[name]) - 1)
            index = RANGE[name][index]
        else:
            if is_killer:
                # only guests rooms
                room = random.randint(0, 5)
                index = ROOM_CENTER[ROOM_LIST[room]][0]
            else:
                room = random.randint(0, len(ROOM_LIST) - 1)
                index = ROOM_CENTER[ROOM_LIST[room]][random.randint(
                    0, len(ROOM_CENTER[ROOM_LIST[room]]) - 1)]
        box = SQUARE[index]
        break
    return box.copy()


class Point:
    def __init__(self):
        self.index = []
        self.py_img = None

    # get index on gui
    def get_index(self):
        draw_index = (self.index[0] * LENGTH + FIX[0],
                      self.index[1] * LENGTH + FIX[1])
        return draw_index

    # get img
    def get_py_img(self):
        return self.py_img

    # get original index
    def get_origin_index(self):
        return self.index


class Weapon(Point):
    def __init__(self, weapon_name) -> None:
        Point.__init__(self)
        self.weapon_name = weapon_name
        self.index = get_random_index(weapon_name, False)

    # get weapon
    def get_weapon_name(self):
        return self.weapon_name


class Role(Point):
    def __init__(self, role, nice_weapon, is_killer) -> None:
        Point.__init__(self)
        self.role = role
        self.nice_weapon = nice_weapon
        self.now_weapon = None
        self.is_killer = is_killer
        self.index = get_random_index(role, self.is_killer)
        self.path = []
        self.health = 2

    # get weapon
    def set_weapon(self, weapon):
        self.now_weapon = weapon

    # get role
    def get_role(self):
        return self.role

    def is_good_weapon(self):
        return self.nice_weapon == self.now_weapon

    # update index
    def update_index_based_keyboard(self, direction):
        room = in_room_helper(self.index, ROOM_CENTER)
        if room != NOT_IN_ROOM:
            directions = ROOM_OUT[room][0]
            next_index = None
            for d in directions:
                if d == direction:
                    next_index = ROOM_OUT[room][1][directions.index(d)]
                    break
            if next_index is None:
                return False
            self.index = SQUARE[next_index].copy()
            return True
        n_x = self.index[0] + direction[0]
        n_y = self.index[1] + direction[1]
        if 0 <= n_x and n_x < MAX_X and 0 <= n_y and n_y < MAX_Y:
            if can_go(self.index, [n_x, n_y]):
                self.index[0] = n_x
                self.index[1] = n_y
                room = in_room_helper(self.index, ROOM_ENTRANCE)
                if room != NOT_IN_ROOM:
                    self.index = SQUARE[ROOM_CENTER[room][0]]
                return True
            else:
                return False

    # update index
    def update_index_based_path(self):
        if self.is_killer or self.role == 'victim':
            return
        else:
            if len(self.path) == 0:
                self.path = get_random_path(self.index[:2])
            self.index[0] = self.path[0][0]
            self.index[1] = self.path[0][1]
            self.path.pop(0)


def get_square_position(position):
    for i in SQUARE_NUM_MAP:
        if SQUARE_NUM_MAP[i] == position:
            break

    result = copy.deepcopy(SQUARE[i])
    result.pop(2)
    return result


if __name__ == '__main__':
    print(111)
