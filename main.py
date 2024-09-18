import pyxel

VERSION = "0.0.1dev1"


class Main:
    pass


if __name__ == "__main__":
    # NOTE: All bltm() and blt calls should have at least the 200%-scale treatment!
    pyxel.init(128, 128, title=f"El Templo del Ajolote v{VERSION}", capture_scale=120)
    main = Main()
