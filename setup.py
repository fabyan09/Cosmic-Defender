from cx_Freeze import setup, Executable
import sys

# Configuration pour cx_Freeze
build_exe_options = {
    "packages": ["pygame", "numpy", "math", "random", "sys"],
    "excludes": ["tkinter"],
    "include_files": [],
    "zip_include_packages": ["*"],
    "zip_exclude_packages": []
}

# Configuration de l'exécutable
executables = [
    Executable(
        script="cosmic_defender.py",
        base="Win32GUI" if sys.platform == "win32" else None,
        target_name="Cosmic_Defender.exe",
        icon=None
    )
]

setup(
    name="Cosmic Defender",
    version="1.0",
    description="Un jeu de tir spatial épique !",
    options={"build_exe": build_exe_options},
    executables=executables
)