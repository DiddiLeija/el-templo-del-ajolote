import nox
import os

resources = ["data.json", "resource.pyxres"]
main_version = "0.1.0"  # TODO for 1.0: link with main.py


@nox.session(name="package-win32")
def package_win32(session: nox.Session) -> None:
    "Package everything up for win32-based systems."
    session.install("-r", "requirements.txt")
    session.run("python", "setup.py", "build_exe")
    for i in resources:
        session.run(
            "python",
            "-c",
            "import os, shutil; exe_path = os.listdir('./build')[0]; "
            f"shutil.copy2('{i}', "
            "f'./build/{exe_path}/"
            f"{i}')",
        )
    dist_generation = "import os; os.mkdir('./dist')"
    if os.path.exists("./dist"):
        if input(
            "The destination directory ('./dist') already exists. Do you want to remove it? (y/n) "
        ).strip().lower() not in ("y", "yes"):
            session.warn("Aborting...")
            quit()
        dist_generation = (
            "import os, shutil; shutil.rmtree('./dist'); os.mkdir('./dist')"
        )
    session.run("python", "-c", dist_generation)
    session.run(
        "python",
        "-m",
        "zipfile",
        "-c",
        f"./dist/ajolote-{main_version}-win32.zip",
        "./build"
    )

@nox.session
def package(session: nox.Session) -> None:
    "Package everything up on a Pyxel executable version."
    session.install("-r", "requirements.txt")
    # TODO for 1.0

# TODO: lint, format, etc
