import pygame
import pygame.freetype
import os
from controller import adjacent_detection, hurt_or_weapon, report
from pygame.constants import KEYDOWN
from model import Role, ROLE, WEAPON, ROLE_WEAPON, Weapon
import random

# img path
IMG_FLODER = os.path.join('.', 'img')
BG = os.path.join(IMG_FLODER, 'bg.png')
CLEANER = os.path.join(IMG_FLODER, 'cleaner.png')
KNIFE = os.path.join(IMG_FLODER, 'knife.png')
POISON = os.path.join(IMG_FLODER, 'poison.png')
ROPE = os.path.join(IMG_FLODER, 'rope.png')
VICTIM = os.path.join(IMG_FLODER, 'victim.png')
WAITRESS = os.path.join(IMG_FLODER, 'waitress.png')
WRITER = os.path.join(IMG_FLODER, 'writer.png')
VICTIM_BEING_KILLED = os.path.join(IMG_FLODER, 'victim_being_killed.png')
MARK = os.path.join(IMG_FLODER, 'mark.png')
# WSAD keyboard
KEY_MAP = {
    pygame.K_w: [0, -1],
    pygame.K_a: [-1, 0],
    pygame.K_s: [0, 1],
    pygame.K_d: [1, 0]
}
# roles  dict，key，value
roles = {}
# weapon dict
weapons = {}
WHERE_WEAPON = {
    'knife': 'Kitchen',
    'poison': 'Dining Room',
    'rope': 'warehouse'
}
TIPS = 'RULES: Use WSAD to move up down left and right. Press SPACE to pick the weapon or start the murder. One press is one turn, game ends in 50 turns.\n' \
       "1. You are a {}, you are good at using {}, which allows you kill the VICTIM in one turn, other weapons will take two turns.\n" \
       "2. Find a weapon in room G, H or I. (You do not have to stick to {} in the {}) \n" \
       "3. Then go commit the murder (Click Space to start the murder. if you use {}, you can move out of the room next turn; otherwise you have to press Space one more tiem to finish the murder,this means you need to stay in the room for one more turn)\n" \
       "4.One Witness report will be created once your character is next to another or in the same grid/room. Witness report will be used for further deduction in the second phase of the game, which is not relevant now" \
       ""


# load img


def load_img():
    cleaner = pygame.image.load(CLEANER)
    knife = pygame.image.load(KNIFE)
    poison = pygame.image.load(POISON)
    rope = pygame.image.load(ROPE)
    victim = pygame.image.load(VICTIM)
    waitress = pygame.image.load(WAITRESS)
    writer = pygame.image.load(WRITER)
    roles['cleaner'].py_img = cleaner
    roles['waitress'].py_img = waitress
    roles['writer'].py_img = writer
    roles['victim'].py_img = victim
    weapons['knife'].py_img = knife
    weapons['poison'].py_img = poison
    weapons['rope'].py_img = rope


# init role


def load_role(killer):
    for role_name in ROLE:
        role = Role(role_name, ROLE_WEAPON[role_name], role_name == killer)
        roles[role_name] = role


# init weapon


def load_weapon():
    for weapon_name in WEAPON:
        weapon = Weapon(weapon_name)
        weapons[weapon_name] = weapon


# paint


def draw_point(screen: pygame.Surface):
    for role in roles.values():
        screen.blit(role.get_py_img(), role.get_index())
    for weapon in weapons.values():
        screen.blit(weapon.get_py_img(), weapon.get_index())


def word_wrap(surf, text, font, color=(0, 0, 0)):
    font.origin = True
    words = text.split(' ')
    width, height = surf.get_size()
    line_spacing = font.get_sized_height() + 2
    x, y = 0, line_spacing
    space = font.get_rect(' ')
    for word in words:
        bounds = font.get_rect(word)
        if x + bounds.width + bounds.x >= width:
            x, y = 0, y + line_spacing
        if x + bounds.width + bounds.x >= width:
            raise ValueError("word too wide for the surface")
        if y + bounds.height - bounds.y >= height:
            raise ValueError("text to long for the surface")
        if word.isupper():
            font.render_to(surf, (x, y), None, (255, 0, 0))
        else:
            font.render_to(surf, (x, y), None, color)
        x += bounds.width + space.width
    return x, y


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 800), flags=pygame.RESIZABLE)
    screen.fill((255, 255, 255))
    pygame.display.set_caption('Deadly Hotel')
    bg = pygame.image.load(BG)
    mark = pygame.image.load(MARK)
    # random choose killer
    killer = random.randint(0, len(ROLE) - 2)
    killer = ROLE[killer]
    load_role(killer)
    load_weapon()
    load_img()
    killer = roles[killer]
    good_weapon = killer.nice_weapon
    tips = TIPS.format(killer.get_role().upper(), good_weapon.upper(),
                       good_weapon.upper(), WHERE_WEAPON[good_weapon].upper(), good_weapon.upper())
    # tips_font = pygame.font.Font(None, 30)
    pygame.freetype.init()
    font = pygame.freetype.SysFont('Arial', 18)
    font_ = pygame.font.Font(None, 30)
    running = 50
    # function of witness
    adjacent_detection(roles, running)
    while running >= 1:
        # draw
        screen.fill((255, 255, 255))
        word_wrap(screen, tips, font)
        screen.blit(mark, (0, 205))
        surface = font_.render('{} rounds'.format(50 - running), False, (255, 200, 10))
        screen.blit(surface, (700, 230))
        screen.blit(bg, (0, 263))
        draw_point(screen)
        # event type
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # kill or pick
                    weapon_killer_get = hurt_or_weapon(
                        killer, weapons, roles['victim'], running)
                    # pick the weapon
                    if weapon_killer_get is not None:
                        weapons.pop(weapon_killer_get)
                    # check victim
                    if roles['victim'].health == 0:
                        roles['victim'].py_img = pygame.image.load(
                            VICTIM_BEING_KILLED)
                    for role in roles.values():
                        role.update_index_based_path()
                    running -= 1
                    adjacent_detection(roles, running)
                    break
                if event.key in KEY_MAP:
                    # unsuccessful move
                    ret = killer.update_index_based_keyboard(
                        KEY_MAP[event.key])
                    if ret:
                        for role in roles.values():
                            role.update_index_based_path()
                        running -= 1
                        adjacent_detection(roles, running)
                        break
        pygame.display.update()

    # print report
    for i in report:
        if len(i) == 4:
            print("{}/{}, {}, {} round".format(i[0], i[1], i[2], 50 - i[3]))
        else:
            print("{} was killed by {} in {} at {} round".format(i[0], i[1], i[3], 51 - i[2]))
