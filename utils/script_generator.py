import platform
import uuid
import os

def generate_script(task_description: str, os_type=None):
    os_type = os_type or platform.system()
    script_id = str(uuid.uuid4())[:8]

    if os_type == "Linux":
        filename = f"sys_task_{script_id}.sh"
        content = f"""#!/bin/bash
# Script generado automáticamente
# Tarea: {task_description}

echo "Iniciando tarea: {task_description}"
# Aquí puedes personalizar comandos según el prompt

"""
    elif os_type == "Windows":
        filename = f"sys_task_{script_id}.bat"
        content = f"""@echo off
REM Script generado automáticamente
REM Tarea: {task_description}

echo Iniciando tarea: {task_description}
:: Personaliza los comandos aquí

"""
    else:
        return None, "Sistema operativo no soportado."

    path = os.path.join("generated_scripts", filename)
    os.makedirs("generated_scripts", exist_ok=True)
    with open(path, "w") as file:
        file.write(content)

    return path, "Script generado correctamente."
