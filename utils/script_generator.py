import platform
import uuid
import os
import time
import re
import eel

def buscar_script_existente(prompt, carpeta="generated_scripts"):
    for archivo in os.listdir(carpeta):
        if prompt.replace(" ", "_") in archivo:
            return os.path.join(carpeta, archivo)
    return None



def guardar_script_si_existe(respuesta_raw):
        # Guardar el script si se detecta un bloque de código
        bloques_codigo = re.findall(r"```(\w+)?\n(.*?)```", respuesta_raw, re.DOTALL)

        if bloques_codigo:
            for i, (lenguaje, codigo) in enumerate(bloques_codigo):
                lenguaje = (lenguaje or "").strip().lower()

                extensiones = {
                    "python": "py",
                    "bash": "sh",
                    "shell": "sh",
                    "sh": "sh",
                    "batch": "bat",
                    "bat": "bat",
                    "powershell": "ps1",
                    "ps1": "ps1",
                    "cmd": "bat",
                    "json": "json",
                    "yaml": "yaml",
                    "yml": "yml",
                    "xml": "xml",
                    "html": "html",
                    "js": "js",
                    "javascript": "js",
                    "ts": "ts",
                    "typescript": "ts",
                    "java": "java",
                    "c": "c",
                    "cpp": "cpp",
                    "c++": "cpp",
                    "cs": "cs",
                    "go": "go",
                    "rust": "rs",
                    "php": "php",
                    "sql": "sql",
                    "dockerfile": "dockerfile",
                    "makefile": "makefile",
                    "ini": "ini",
                    "config": "conf",
                }

                ext = extensiones.get(lenguaje, "txt")
                filename = f"script_generado_{i+1}.{ext}"
                ruta = os.path.join("scripts_generados", filename)
                os.makedirs("scripts_generados", exist_ok=True)

                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(codigo.strip())

                eel.mostrar_consola_comando(f"✅ Script guardado como: {filename}")
