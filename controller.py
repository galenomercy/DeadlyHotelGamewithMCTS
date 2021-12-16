from model import SQUARE, in_which_room, in_which_square, from_square_to_no, is_box_adjacent, NOT_IN_ROOM

report = list()


# kill or pick
def hurt_or_weapon(killer, weapons, victim, steps):
    # Obtain the original coordinates, not the coordinates on the interface
    killer_index = killer.get_origin_index()
    room1 = in_which_room(killer_index)
    if killer.now_weapon == None:
        for weapon in weapons:
            w_index = weapons[weapon].get_origin_index()
            room2 = in_which_room(w_index)
            if room1 == room2:
                killer.set_weapon(weapon)
                return weapon
    else:
        i = killer.get_origin_index()
        j = victim.get_origin_index()
        room1, room2 = in_which_room(
            i), in_which_room(j)
        #
        if room1 == room2 and room1 != NOT_IN_ROOM:
            square1, square2 = in_which_square(
                i), in_which_square(j)
            if killer.is_good_weapon():
                victim.health = 0
                report.append([victim.get_role(), killer.now_weapon, steps, room1, 1])
            else:
                victim.health -= 1
                if victim.health == 0:
                    report.append([victim.get_role(), killer.now_weapon, steps, room1, 1])
        # room1 room2 both NOT IN ROOM
        else:
            if room1 == room2:
                # whether in one square
                square1, square2 = in_which_square(
                    i), in_which_square(j)
                if is_box_adjacent(SQUARE[square1], SQUARE[square2]):
                    if killer.is_good_weapon():
                        victim.health = 0
                        report.append([victim.get_role(), killer.now_weapon, steps])
                    else:
                        victim.health -= 1
                        if victim.health == 0:
                            report.append([victim.get_role(), killer.now_weapon, steps])

    return None


def adjacent_detection(roles, steps):
    roles_and_index = [[roles[role].get_role(), roles[role].get_origin_index()]
                       for role in roles]
    # print(roles_and_index)
    duplicate_removal = set()
    for i in roles_and_index:
        for j in roles_and_index:
            if i == j or i[0] == 'victim' or j[0] == 'victim':
                continue
            else:
                room1, room2 = in_which_room(
                    i[1]), in_which_room(j[1])
                if room1 == room2 and room1 != NOT_IN_ROOM:
                    if i[0] + j[0] not in duplicate_removal:
                        duplicate_removal.add(i[0] + j[0])
                        duplicate_removal.add(j[0] + i[0])
                        report.append([i[0], j[0], room1 + '/' + room2, steps])

                else:
                    if room1 == room2:
                        square1, square2 = in_which_square(
                            i[1]), in_which_square(j[1])
                        if is_box_adjacent(SQUARE[square1], SQUARE[square2]) and i[0] + j[0] not in duplicate_removal:
                            duplicate_removal.add(i[0] + j[0])
                            duplicate_removal.add(j[0] + i[0])
                            report.append([i[0], j[0], from_square_to_no(
                                square1) + '/' + from_square_to_no(square2), steps])

    # for i in ret:
    #     print("{}/{}, {}, {} round".format(i[0], i[1], i[2], i[3]))
