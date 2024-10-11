import io, json

import pyxel

VERSION = "0.1.0"


def get_data(fname: str) -> dict:
    # TODO: get a better system
    final = dict()
    try:
        with io.open(fname) as dfile:
            final = json.loads(dfile.read())
    except Exception:
        print("Warning, could not load file:", fname)
        print("All your game data / DLCs may be corrupted.")
    return final


GAME_SETUP = get_data("data.json")
BACKGROUND_1 = 1
BACKGROUND_2 = 4

# BACKGROUND_* data
# =================
# 1, 4 - indoors, overworld
# 0, 2 - outdoors, overworld
# 5, 6 - underworld
# 3 - locked-mode fences (?)
# 7 - wildcard (?)

def get_tile(tile_x, tile_y, to_list=False):
    if to_list:
        return list(pyxel.tilemaps[BACKGROUND_1].pget(tile_x, tile_y))
    return pyxel.tilemaps[BACKGROUND_1].pget(tile_x, tile_y)


def detect_collision(x, y):
    solids = GAME_SETUP["solid_block_tiles"]
    ns = []
    for t in solids:
        ns.append([t[0] // 8, t[1] // 8])
    solids = ns[:]
    x1 = x // 8
    y1 = y // 8
    x2 = (x + 16 - 1) // 8
    y2 = (y + 16 - 1) // 8
    for yi in range(y1, y2+1):
        for xi in range(x1, x2+1):
            if get_tile(xi, yi, True) in solids:
                return True
    return False


def fix_collision(x, y, dx, dy, fl=2):
    abs_dx = abs(dx)
    abs_dy = abs(dy)
    sign = fl if dx > 0 else -(fl)
    for _ in range(abs_dx):
        if detect_collision(x + sign, y):
            break
        x += sign
    sign = fl if dy > 0 else -(fl)
    for _ in range(abs_dy):
        if detect_collision(x, y + sign):
            break
        y += sign
    return x, y


def pretty_text(txt, x, y, col1=1, col2=7):
    "draw a pretty text with customizable colors."
    # FIXME: Unicode characters are not working, at least on certain
    # devices. This affects the rendering of non-ASCII languages.
    # Here, I'm using Spanish, so it doesn't work on my main device.
    # TODO: determine if this is a Pyxel issue or my problem...
    pyxel.text(x, y, txt, col1)
    pyxel.text(x+1, y, txt, col2)


class MobBase:
    "Mob base."
    vertical = False
    size = 16
    name = ""
    imgbank = 1
    imgtype = ""
    aspect = "default"
    harmful = True
    speed = 1
    sign = 1
    colkey = 0  # in case we don't use the traditional colkey (0)
    update_sleeper = 1  # only update if pyxel.frame_count % self.update_sleeper == 0... B)

    def __init__(self, x, y, vertical):
        self.x, self.y = x, y
        self.vertical = vertical
        self.imgtype = "images" if self.size > 8 else "images-8"

    def update(self):
        if pyxel.frame_count % self.update_sleeper != 0:
            return
        dx, dy = 0, 0
        if self.vertical:
            dy = self.speed * self.sign
            self.aspect = "down" if dy > 0 else "up"
        else:
            dx = self.speed * self.sign
            self.aspect = "right" if dx > 0 else "left"
        self._check_sign()
        self.x, self.y = fix_collision(self.x, self.y, dx, dy)

    def draw(self):
        img = GAME_SETUP[self.imgtype][self.name][self.aspect]
        if self.aspect != "default":
            img = img[0] if pyxel.frame_count % 2 == 0 else img[1]
        pyxel.blt(self.x, self.y, self.imgbank, img[0], img[1], self.size, self.size, self.colkey)

    def _check_sign(self):
        # FIXME: this is not working on 8x8-sized mobs
        cx, cy = self.x - 1, self.y - 1
        if self.vertical:
            if self.sign > 0:
                cy += 4 if self.size > 8 else 2  # FIXME: 2 is not working!?
            cx += 1
        else:
            if self.sign > 0:
                cx += 4 if self.size > 8 else 2
            cy += 1
        if detect_collision(cx, cy):
            self.sign *= -1


class Monster(MobBase):
    # undocumented, removed from final gameplay
    size = 8
    name = "monster"


class MonsterFast(Monster):
    # undocumented, removed from final gameplay
    speed = 2


class Iguana(MobBase):
    name = "iguana"
    update_sleeper = 2  # so the Iguana is the slowest mob ;)


class IguanaFast(Iguana):
    update_sleeper = 1


class IguanaSlow(Iguana):
    update_sleeper = 4  # much, MUCH slower iguana


class Main:
    """
    ########################
    #####  MAIN CLASS  #####
    ########################
    """

    def __init__(self):
        self.x, self.y = 1016, 992  # 127, 124 -- x8?
        self.respawn_coords = [0, 0, 0, 2]  # [x, y, BACKGROUND_*] -- modified during the game
        self.player_aspect = ["default", 0]
        self.stage = "o"
        self.open_mode = False
        self.menu = True
        self.plot_index = 0
        self.should_update_player = True
        self.mob_map = self._generate_mob_map()
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.menu:
            self.update_menu()
            return
        if not self.open_mode:
            self.update_story(0)
            if self.plot_index < 0:
                # finish flag
                self.open_mode = True
                self.should_update_player = True
                return
        else:
            # run extra feats through "open mode"
            self.update_open()
        for m in self.mob_map[str(BACKGROUND_1)]:
            m.update()
        if self.should_update_player:
            self.update_player()
        if self.should_update_player is None:
            # None means here "one time negative", so we make it positive now.
            self.should_update_player = True

    def draw(self):
        if self.menu is not False:
            self.draw_menu()
            return
        self.draw_general()
        if not self.open_mode:
            self.draw_story(0)

    def draw_general(self):
        draw_a, draw_b = BACKGROUND_1, BACKGROUND_2  # TODO: use BACKGROUND_* directly?
        pyxel.cls(0)
        pyxel.camera()  # global camera fix
        draw_x = self.x-448 // 8
        draw_y = self.y-448 // 8
        pyxel.bltm(0, 0, draw_a, draw_x, draw_y, 128, 128)  # background
        pyxel.camera(draw_x, draw_y)  # camera fix 1
        for m in self.mob_map[str(BACKGROUND_1)]:
            m.draw()
        self.draw_player()
        self.draw_npc()
        pyxel.camera()  # camera fix 2
        pyxel.bltm(0, 0, draw_b, draw_x, draw_y, 128, 128, 0)  # backgound additions

    def update_player(self):
        # movement checks
        dx, dy = 0, 0
        if pyxel.btn(pyxel.KEY_DOWN):
            self.player_aspect[0] = "down"
            dy = 1
        elif pyxel.btn(pyxel.KEY_UP):
            dy = -1
            self.player_aspect[0] = "up"
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_aspect[0] = "right"
            dx = 1
        elif pyxel.btn(pyxel.KEY_LEFT):
            dx = -1
            self.player_aspect[0] = "left"
        # aspect checks
        if self._clicking_an_arrow([pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT]):
            self.player_aspect[1] = 1
        else:
            self.player_aspect[1] = 0
        # (x, y) corrections according to a solid blocks list
        self.x, self.y = fix_collision(self.x, self.y, dx, dy)

    def draw_player(self):
        img_pick = GAME_SETUP["images"]["axel"][self.player_aspect[0]]
        if self.player_aspect[0] != "default":
            img_pick = img_pick[self.player_aspect[1]]
        pyxel.blt(self.x, self.y, 1, img_pick[0], img_pick[1], 16, 16, 0)

    def draw_npc(self):
        # draw all the non-playable-characters available.
        npcs = GAME_SETUP["npc_locations"][str(BACKGROUND_1)]  # TODO: Make sure this works anytime!
        for c in npcs:
            sz = 0
            if c[0] in GAME_SETUP["images"].keys():
                # 16x16
                sz = 16
            elif c[0] in GAME_SETUP["images-8"].keys():
                # 8x8
                sz = 8
            if sz != 0 and self._in_the_map(c[2], c[3], sz):
                tp = "images-8" if sz == 8 else "images"
                bnk = 0 if sz == 8 else 1
                npc_u, npc_v = GAME_SETUP[tp][c[0]][c[1]]
                pyxel.blt(c[2], c[3], bnk, npc_u, npc_v, sz, sz, 0)

    def update_open(self):
        "once the main mission's done, open tasks are unlocked."

    def update_story(self, id=0):
        "tell a story."
        global BACKGROUND_1, BACKGROUND_2
        plot = GAME_SETUP["stories"][id]
        if self.plot_index >= len(plot):
            self.plot_index = -1  # a flag that means the story is over
            return
        ptype = plot[self.plot_index][0]
        pdata = plot[self.plot_index][1:]
        self.should_update_player = False  # just remember to fix this once the story ends
        if ptype == "set":
            # set the player to a certain position
            BACKGROUND_1, BACKGROUND_2, self.x, self.y = pdata[0], pdata[1], pdata[2], pdata[3]
            self.plot_index += 1
        elif ptype == "dialog":
            # let's chat!
            if self.should_update_player is not False:
                self.should_update_player = False
            if pyxel.btnp(pyxel.KEY_SPACE):
                # TODO: include keypad space key too
                self.plot_index += 1
                self.should_update_player = None
        elif ptype == "task":
            # you must get somewhere.
            self.should_update_player = True  # in this case it should be true
            if pdata[0][0] in range(self.x + 2, self.x + 15):
                if pdata[0][1] in range(self.y + 2, self.y + 15):
                    self.plot_index += 1
        elif ptype == "set_facing":
            # change Axel's facing.
            self.player_aspect[0] = pdata[0]
            self.player_aspect[1] = 0
            self.plot_index += 1
        elif ptype == "respawn_point":
            # set the respawn point for Axel.
            self.respawn_coords = pdata[0]
            self.plot_index += 1

    def draw_story(self, id=0):
        global BACKGROUND_1, BACKGROUND_2
        plot = GAME_SETUP["stories"][id]
        if self.plot_index >= len(plot):
            # no direct fixes to the variable -- update_story() should do it
            return
        ptype = plot[self.plot_index][0]
        pdata = plot[self.plot_index][1:]
        if ptype in ("set", "set_facing", "respawn_point"):
            pass  # NOTE: we're doin' nothing now... but... should we? ¯\_(ツ)_/¯
        elif ptype == "dialog":
            if pdata[0] is not None:
                pyxel.rect(111, 74, 16, 16, 0)
                pyxel.rectb(110, 73, 18, 18, 7)
            pyxel.rect(0, 91, 128, 37, 0)
            pyxel.rect(0, 90, 128, 1, 7)
            # draw the "skip" text and the dialog
            if pyxel.frame_count % 2 == 0:
                # ticking every 2 frames
                pretty_text(">", 119, 120)
            pretty_text(pdata[1], 0, 92)
            # add a close-up of the talking character
            if pdata[0] is not None:
                character_img = GAME_SETUP["images"][pdata[0]]["chat"][pdata[2]]
                pyxel.blt(111, 74, 1, character_img[0], character_img[1], 16, 16, 0)
        elif ptype == "task":
            # point to the desired location
            if pyxel.frame_count % 2 == 0 or pyxel.frame_count % 3 == 0:
                pyxel.camera(self.x-448 // 8, self.y-448 // 8)  # borrowed from draw_general()
                pyxel.circb(pdata[0][0]+4, pdata[0][1]+4, 4, 14)
                pyxel.circb(pdata[0][0]+5, pdata[0][1]+4, 4, 7)
                pyxel.camera()
            # make the task verbose
            pyxel.rect(0, 111, 128, 17, 0)
            pyxel.rect(0, 110, 128, 1, 7)
            pretty_text(pdata[1], 0, 112, col2=9)

    def update_menu(self):
        # nothing happening here at all.
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.menu = None

    def draw_menu(self):
        if self.menu is None:
            self.menu = False  # MAGIC!!
        pyxel.cls(0)
        pretty_text("<<  El Templo del Ajolote  >>", 6, 8, col1=2, col2=15)
        pretty_text("Mover: Flechas", 25, 40, col2=13)
        pretty_text("Aceptar: Espacio", 25, 48, col2=13)
        pretty_text("Salir: ESC", 25, 56, col2=13)
        pretty_text("Presiona Espacio para comenzar\n     o ESC para abandonar", 4, 90)

    def _respawn_player(self):
        # return the character to the right place
        global BACKGROUND_1, BACKGROUND_2
        self.x, self.y = self.respawn_coords[0], self.respawn_coords[1]
        BACKGROUND_1, BACKGROUND_2 = self.respawn_coords[2], self.respawn_coords[3]

    def _generate_mob_map(self):
        # deep-level generation of mobs.
        mob_template = GAME_SETUP["mob_locations"]
        final = dict()
        for l in mob_template.keys():
            final[l] = list()
            for m in mob_template[l]:
                if m[2] == "iguana":
                    final[l].append(Iguana(m[0], m[1], m[3]))
                elif m[2] == "monster":
                    final[l].append(Monster(m[0], m[1], m[3]))
                elif m[2] == "monster-fast":
                    final[l].append(MonsterFast(m[0], m[1], m[3]))
                elif m[2] == "iguana-slow":
                    final[l].append(IguanaSlow(m[0], m[1], m[3]))
                elif m[2] == "iguana-fast":
                    final[l].append(IguanaFast(m[0], m[1], m[3]))
        return final

    def _clicking_an_arrow(self, keys: list):
        # checks if any of a given key list has been pressed
        for k in keys:
            if pyxel.btn(k):
                return True
        return False

    def _in_the_map(self, cx, cy, size):
        # check if (x, y) is on the screen
        if size < 1:
            # can't check over 0-sized items, return False
            return False
        for xi in range(cx, cx + size + 1):
            for yi in range(cy, cy + size + 1):
                if xi in range(self.x - 64, self.x + 65) and yi in range(self.y - 64, self.y + 65):
                    return True
        return False


if __name__ == "__main__":
    pyxel.init(128, 128, title=f"El Templo del Ajolote v{VERSION}", capture_sec=120)
    pyxel.load("resource.pyxres")
    main = Main()
