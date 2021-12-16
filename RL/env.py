import gym
from gym import Env
from controller import adjacent_detection, hurt_or_weapon, report
from model import Role, ROLE, WEAPON, ROLE_WEAPON, Weapon, in_which_square, SQUARE_NUM_MAP, ROOM
from detective import detect
import random
from gym.wrappers.time_limit import TimeLimit


class DeadlyHotelEnv(Env):
    WHERE_WEAPON = {
        'knife': 'Kitchen',
        'poison': 'Dining Room',
        'rope': 'warehouse'
    }
    ACTION_MAP = {
        0: "SPACE",  # stay
        1: [0, -1],  # up
        2: [-1, 0],  # left
        3: [0, 1],   # down
        4: [1, 0]    # right
    }
    ROOM_MAP = {
        'A': 0,
        'B': 1,
        'C': 2,
        'D': 3,
        'E': 4,
        'F': 5,
        'G': 6,
        'H': 7,
        'I': 8,
    }

    def __init__(self):
        self.killer = None
        # roles  dict，key，value
        self.roles = {}
        # weapon dict
        self.weapons = {}
        self.good_weapon = None
        self.running = None

        self.is_weapon_pickup = False

        self.kill_success = False

        self.action_space = gym.spaces.Discrete(5)
        # cleaner: 45
        # writer: 45
        # waitress: 45
        # victim: 6
        # knife: 2
        # rope: 2
        # poison: 2
        # die: 3
        self.observation_space = gym.spaces.MultiDiscrete([45, 45, 45, 6, 2, 2, 2, 3])

        # self.reset()

    def load_role(self, killer):
        for role_name in ROLE:
            role = Role(role_name, ROLE_WEAPON[role_name], role_name == killer)
            self.roles[role_name] = role

    def load_weapon(self):
        for weapon_name in WEAPON:
            weapon = Weapon(weapon_name)
            self.weapons[weapon_name] = weapon

    def reset(self):
        global report

        killer_no = random.randint(0, len(ROLE) - 2)

        print('-'*36)
        print(killer_no)
        print('-' * 36)

        killer_name = ROLE[killer_no]
        self.load_role(killer_name)
        self.load_weapon()
        self.killer = self.roles[killer_name]
        self.good_weapon = self.killer.nice_weapon

        self.kill_success = False
        self.is_weapon_pickup = False

        self.running = 50
        adjacent_detection(self.roles, self.running)
        report.clear()

        return self._get_state()

    def step(self, action):
        action = self.ACTION_MAP[action]
        """
        reward
        1. pick up the weapon
        2. kill
        3. escape
        4. effective action
        """
        reward = 0
        if action == "SPACE":
            weapon_backup = self.killer.now_weapon
            victim_health_backup = self.roles['victim'].health

            # kill or pick
            weapon_killer_get = hurt_or_weapon(
                self.killer, self.weapons, self.roles['victim'], self.running)
            # pick the weapon
            if weapon_killer_get is not None:
                self.weapons.pop(weapon_killer_get)
            for role in self.roles.values():
                role.update_index_based_path()
            self.running -= 1
            adjacent_detection(self.roles, self.running)

            hurt = victim_health_backup - self.roles['victim'].health

            if weapon_backup == self.killer.now_weapon and victim_health_backup == self.roles['victim'].health:
                reward -= 1
            else:
                if weapon_killer_get is not None:      # 1
                    reward += 10

                elif hurt == 1 and self.roles['victim'].health==1:        # 2
                    reward += 10

                elif hurt == 1 and self.roles['victim'].health==0:
                    reward += 10
                    # print('kill done with normal weapon')
                elif hurt == 2 and self.roles['victim'].health==0:
                    reward += 20
                    # print('kill done with good_at_weapon')

            if self.roles['victim'].health == 0:
                self.kill_success = True



        else:
            # unsuccessful move
            is_effective = self.killer.update_index_based_keyboard(action)
            if is_effective:
                for role in self.roles.values():
                    role.update_index_based_path()
                self.running -= 1
                adjacent_detection(self.roles, self.running)
            else:           # 4
                reward -= 20


        done = self.running < 1
        if done:        # 4
            if self.kill_success == False:
                reward -= 20
            if self.kill_success:
                report_text = self.gen_report()
                rank = detect(report_text)
                if rank[2][0] == self.killer.role:    # 3
                    reward -= 20
                    # print('kill done but be arrested')
        return self._get_state(), reward, done, {}

    def render(self, mode="console"):

        global state
        if mode == "console":
            invert_map = dict([(v, k) for k, v in self.ROOM_MAP.items()])
            console_obs = []
            for i, states in enumerate(self._get_state()):
                if i < 3:
                    if states < 36:
                        console_obs.append(states + 1)
                    else:
                        console_obs.append(invert_map[states - 36])
                elif i == 3:
                    console_obs.append(invert_map[states])
                else:
                    console_obs.append(states)


            print(console_obs)
            if self.kill_success and self.running == 1:
                report_text = self.gen_report()
                rank = detect(report_text)
                if rank[2][0] == self.killer.role:  # 3
                    print(rank)
                    print('kill done but be arrested')

                else:

                    print(rank)
                    print(self.killer.role)
                    print('kill done and not be arrested')

        pass


    def gen_report(self):
        text = ""
        for i in report:
            if len(i) == 4:
                text += "{}/{}, {}, {} round\n".format(i[0], i[1], i[2], 50 - i[3])
            else:
                text += "{} was killed by {} in {} at {} round\n".format(i[0], i[1], i[3], 51 - i[2])
        return text

    def _get_state(self):
        state = []
        #
        for role in list(self.roles.values())[:3]:
            origin_index = role.get_origin_index()
            index = in_which_square(origin_index)
            if index in SQUARE_NUM_MAP:
                pos = SQUARE_NUM_MAP[index] - 1
            else:
                for room_index in ROOM:
                    if index in ROOM[room_index]:
                        pos = self.ROOM_MAP[room_index] + 36
                        break
            state.append(pos)
        # victim
        victim = list(self.roles.values())[3]
        victim_origin_index = victim.get_origin_index()
        victim_index = in_which_square(victim_origin_index)
        for room_index in list(ROOM.keys())[:6]:
            if victim_index in ROOM[room_index]:
                pos = self.ROOM_MAP[room_index]
                state.append(pos)

        for weapon in WEAPON:
            if self.killer.now_weapon is None:
                state.append(0)
            else:
                state.append(int(weapon == self.killer.now_weapon))

        health = 0 if victim.health < 0 else victim.health
        state.append(health)

        if self.kill_success and self.running == 0:
            report_text = self.gen_report()
            rank = detect(report_text)
            if rank[2][0] == self.killer.role:
                pass
            else:
                state.append('not arrested')

        return state


if __name__ == '__main__':
    env = DeadlyHotelEnv()
    print('1')
    obs = env.reset()


    while True:
        # action = agent(obs)
        env.render()
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)

        if done:

            obs = env.reset()

