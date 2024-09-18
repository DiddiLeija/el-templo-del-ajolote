import io, json

import pyxel

VERSION = "0.0.1dev1"


def get_data(fname: str) -> dict | list:
    """
    Tuve la loca idea de meter todos los datos relevantes del
    resource y los dialogos mientras hacia mods para minecraft,
    resulta muy practico en casos como este...
    
    TODO: Eventualmente migrar a un mejor sistema???
    """
    final = dict()
    with io.open(fname) as dfile:
        final = json.loads(dfile.read())
    return final


GAME_SETUP = get_data("data.json")


class Axel:
    "a very normal axolotl."


class Main:

    def __init__(self):
        self.player = Axel()


if __name__ == "__main__":
    # NOTE: All bltm() and blt calls should have at least the 200%-scale treatment!
    pyxel.init(128, 128, title=f"El Templo del Ajolote v{VERSION}", capture_scale=120)
    main = Main()
