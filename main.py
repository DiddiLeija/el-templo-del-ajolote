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
        draw_x = self.x-64 // 8
        draw_y = self.y-64 // 8
        if self.stage == "o":
            # overworld
            pyxel.bltm(0, 0, 0, draw_x, draw_y, 128, 128)
            pyxel.bltm(0, 0, 2, draw_x, draw_y, 128, 128, 0)
        pyxel.camera(draw_x, draw_y)
        self.draw_player()

    def update_player(self):
        # movement checks
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += 2
            self.player_aspect[0] = "right"
        elif pyxel.btn(pyxel.KEY_LEFT):
            self.x -= 2
            self.player_aspect[0] = "left"
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += 2
        elif pyxel.btn(pyxel.KEY_UP):
            self.y -= 2
            self.player_aspect[0] = "up"
        # aspect checks
        if self._clicking_an_arrow([pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT]):
            self.player_aspect[1] = 1
        else:
            self.player_aspect[1] = 0
        # (x, y) corrections according to a solid blocks list
        # ...

    def draw_player(self):
        img_pick = GAME_SETUP["images"]["axel"][self.player_aspect[0]]
        if self.player_aspect[0] != "default":
            img_pick = img_pick[self.player_aspect[1]]
        #print(img_pick)
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
