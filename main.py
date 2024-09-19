import io, json

import pyxel

VERSION = "0.0.1dev1"


def get_data(fname: str) -> dict:
    """
    Tuve la loca idea de meter todos los datos relevantes del
    resource y los dialogos mientras hacia mods para minecraft,
    resulta muy practico en casos como este...
    
    TODO: Eventualmente migrar a un mejor sistema???
    """
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
        self.stage = "o"
        pyxel.run(self.update, self.draw)

    def update(self):
        self.update_player()

    def draw(self):
        pyxel.cls(0)
        pyxel.camera()
        if self.stage == "o":
            # overworld
            draw_x = self.x-64 // 8
            draw_y = self.y-64 // 8
            # print(draw_x, draw_y)
            pyxel.bltm(0, 0, 0, draw_x, draw_y, 128, 128)  # TODO: Fixme!
            pyxel.bltm(0, 0, 2, draw_x, draw_y, 128, 128, 0)

    def update_player(self):
        pass


if __name__ == "__main__":
    pyxel.init(128, 128, title=f"El Templo del Ajolote v{VERSION}", capture_scale=120)
    pyxel.load("resource.pyxres")
    main = Main()
