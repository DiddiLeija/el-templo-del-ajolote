import io, json

import pyxel

VERSION = "0.0.1dev1"


def get_data(fname: str) -> dict:
    # TODO: get a better system
    final = dict()
    try:
        with io.open(fname) as dfile:
            final = json.loads(dfile.read())
    except Exception:
        print("Warning, could not load file:", fname)
    return final

def get_tile(tile_x, tile_y, to_list=False):
    if to_list:
        return list(pyxel.tilemaps[0].pget(tile_x, tile_y))
    return pyxel.tilemaps[0].pget(tile_x, tile_y)

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

def fix_collision(x, y, dx, dy):
    # after some failed attempts to run a standalone method,
    # we've designed this func as a modified version of those
    # used by "Diddi and Eli" and "Abandon the ship!", along with
    # "detect_collision" (which went through several modifications too)
    #abs_dx = abs(dx)
    #abs_dy = abs(dy)
    #if abs_dx > abs_dy:
    #    sign = 1 if dx > 0 else -1
    #    for _ in range(abs_dx):
    #        if detect_collision(x + sign, y):
    #            break
    #        x += sign
    #    sign = 1 if dy > 0 else -1
    #    for _ in range(abs_dy):
    #        if detect_collision(x, y + sign):
    #            break
    #        y += sign
    #else:
    #    sign = 1 if dy > 0 else -1
    #    for _ in range(abs_dy):
    #        if detect_collision(x, y + sign):
    #            break
    #        y += sign
    #    sign = 1 if dx > 0 else -1
    #    for _ in range(abs_dx):
    #        if detect_collision(x + sign, y):
    #            break
    #        x += sign
    return x, y
    # TODO: fixme!!!


GAME_SETUP = get_data("data.json")


class Main:

    def __init__(self):
        self.x = 960  # 120, 112 -- x8?
        self.y = 896
        self.player_aspect = ["default", 0]
        self.stage = "o"
        pyxel.run(self.update, self.draw)

    def update(self):
        self.update_player()

    def draw(self):
        pyxel.cls(0)
        pyxel.camera()
        draw_x = self.x-448 // 8
        draw_y = self.y-448 // 8
        if self.stage == "o":
            # overworld
            pyxel.bltm(0, 0, 0, draw_x, draw_y, 128, 128)
            pyxel.bltm(0, 0, 2, draw_x, draw_y, 128, 128, 0)
        pyxel.camera(draw_x, draw_y)
        self.draw_player()

    def update_player(self):
        # movement checks
        dx, dy = 2, 2
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += 2
            self.player_aspect[0] = "down"
        elif pyxel.btn(pyxel.KEY_UP):
            self.y -= 2
            dy = -2
            self.player_aspect[0] = "up"
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += 2
            self.player_aspect[0] = "right"
        elif pyxel.btn(pyxel.KEY_LEFT):
            self.x -= 2
            dx = -2
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

    def _clicking_an_arrow(self, keys: list):
        # checks if any of a given key list has
        # been pressed, for internal purposes.
        for k in keys:
            if pyxel.btn(k):
                return True
        return False

if __name__ == "__main__":
    pyxel.init(128, 128, title=f"El Templo del Ajolote v{VERSION}", capture_sec=120)
    pyxel.load("resource.pyxres")
    main = Main()
