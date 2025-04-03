from cx_Freeze import setup, Executable

# Configuración de opciones (ajusta según tus necesidades)
build_exe_options = {
    "packages": ["os", "praw", "csv", "tkinter", "matplotlib", "json"] # Si deseas incluir el archivo de configuración
}

setup(
    name="RedditTracker",
    version="1.0",
    description="Aplicación para extraer y visualizar posts de Reddit",
    options={"build_exe": build_exe_options},
    executables=[Executable("Reddit.py")]  # Usa "Win32GUI" para aplicaciones sin consola en Windows
)
