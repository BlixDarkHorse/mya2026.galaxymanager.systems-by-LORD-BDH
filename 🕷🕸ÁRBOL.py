# -*- coding: utf-8 -*-
"""
🕷 Generador simbólico BDH: estructura de carpetas con ramificación visual.
Versión VTHA-PY 🛸
Autor: Lord BDH & Galaxy Vyoleta 💜
"""

import os

# Configuración de emojis para visualización jerárquica
EMOJI_BRANCH = "➡️"     # rama
EMOJI_FOLDER = "📁"      # carpeta
EMOJI_FILE = "📄"        # archivo
EMOJI_SUB = "↳"          # subrama

# Ruta base (directorio actual)
base_dir = os.getcwd()
output_file = "estructura_de_carpetas.txt"

def generar_estructura(ruta, nivel=0, salida=[]):
    elementos = sorted(os.listdir(ruta))
    for elemento in elementos:
        ruta_completa = os.path.join(ruta, elemento)
        indentacion = "    " * nivel
        if os.path.isdir(ruta_completa):
            salida.append(f"{indentacion}{EMOJI_FOLDER} {elemento}/")
            generar_estructura(ruta_completa, nivel + 1, salida)
        else:
            salida.append(f"{indentacion}{EMOJI_SUB} {EMOJI_FILE} {elemento}")
    return salida

if __name__ == "__main__":
    print("🕷 Generando estructura visual simbólica BDH...\n")
    estructura = generar_estructura(base_dir)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("🌐 ESTRUCTURA DE DIRECTORIOS - UNIVERSO BDH\n")
        f.write("🖤🔥🚀\n\n")
        for linea in estructura:
            f.write(f"{EMOJI_BRANCH} {linea}\n")
        f.write("\n🕸 Generación completada con éxito. 👁‍🗨\n")

    print(f"✅ Archivo '{output_file}' generado correctamente.")
    input("Presiona Enter para salir... ")
