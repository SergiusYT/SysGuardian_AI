import eel
import markdown
import re
from openai import OpenAI
import uuid 
import getpass
import platform
import subprocess

from utils import script_generator
from utils import system_monitor
import random

mensajes_estado = {
    "escribiendo": [
        "🧠 Pensando intensamente",
        "⌨️ Teclado a toda marcha",
        "✍️ Armando una genialidad",
        "🤔 Dándole forma a la respuesta",
        "💭 En busca de las mejores palabras",
        "📡 Comunicando con el núcleo de la IA",
        "🔍 Analizando tus palabras",
        "🪄 Preparando algo mágico",
        "📘 Consultando la enciclopedia universal",
        "🧬 Ordenando ideas"
    ],
    "generando": [
        "🧩 Ensamblando la respuesta final",
        "🛠️ Ajustando los detalles",
        "📊 Dando forma al conocimiento",
        "🖼️ Poniendo los toques finales",
        "🚀 Últimos retoques a la respuesta",
        "📦 Empaquetando sabiduría",
        "📍 Alineando datos y contexto",
        "🧪 Cocinando datos con estilo",
        "🔧 Afinando detalles",
        "⚙️ Sincronizando sinapsis artificial"
    ],
    "recolectando": [
        "📡 Escaneando el sistema",
        "🔍 Reuniendo datos frescos",
        "🖥️ Explorando tu equipo",
        "🧾 Tomando nota del estado del sistema",
        "🧭 Navegando por el hardware",
        "🧱 Revisando las entrañas del sistema",
        "⚡ Capturando métricas clave",
        "📈 Analizando rendimiento",
        "🔬 Observando procesos en tiempo real",
        "💻 Desentrañando secretos técnicos"
    ]
}

def obtener_mensaje_estado(tipo):
    return random.choice(mensajes_estado.get(tipo, ["Procesando..."]))



client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

historial = ""

# Función para detectar si el prompt requiere información del sistema
def necesita_datos_sistema(prompt):
    palabras_clave = [
        # Hardware y uso general
        "cpu", "procesador", "memoria", "ram", "swap", "disco", "espacio", "almacenamiento","modelo",
        "temperatura", "gpu", "tarjeta gráfica", "rendimiento", "consumo", "batería", "ventilador",
        "hardware", "equipo", "sistema", "ordenador", "computadora", "pc", "notebook","computador",

        # Recursos y rendimiento
        "uso", "estado", "carga", "recursos", "saturación", "rendimiento", "latencia", "ciclo",
        "bloqueo", "colapso", "sobrecalentamiento", "rendimiento bajo", "ralentización",

        # Procesos y tareas
        "procesos", "programas activos", "servicios", "hilos", "tareas", "ejecución", "zombie",
        "malware", "actividad sospechosa", "análisis de procesos", "procesos en segundo plano",

        # Sistema operativo y kernel
        "kernel", "os", "sistema operativo", "versión del sistema", "uptime", "tiempo encendido",
        "reinicio", "información del sistema", "plataforma", "host", "arquitectura",

        # Red y conexiones
        "red", "conexión", "puertos", "ip", "latencia", "tráfico", "ancho de banda", "uso de red",
        "descarga", "subida", "ethernet", "wifi", "vpn", "firewall", "puertos abiertos",

        # Seguridad
        "seguridad", "auditoría", "firewall", "logs", "syslog", "bitácora", "eventos",
        "permisos inseguros", "archivos peligrosos", "usuario root", "sudoers", "sudo",

        # Usuarios y cuentas
        "usuarios", "cuentas", "sesiones", "login", "conectados", "usuarios activos",
        "inicio de sesión", "actividad del usuario", "privilegios",

        # Integridad y actualizaciones
        "actualizaciones", "paquetes", "repositorios", "checksum", "integridad", "hash",
        "archivos modificados", "verificación del sistema",

        # General
        "monitor", "monitoreo", "status", "diagnóstico", "inspección", "supervisión",
        "estado del sistema", "informe del sistema"
    ]
    return any(palabra in prompt.lower() for palabra in palabras_clave)



@eel.expose
def enviar_mensaje_stream(prompt):
    try:
        if not prompt or not prompt.strip():
            eel.actualizar_respuesta_ai('<span style="color:red;">❌ El mensaje no puede estar vacío.</span>', "respuesta-error")
            eel.finalizar_respuesta_ai("</div>", "respuesta-error")
            return

        eel.nuevo_mensaje_usuario(f'<div><b>Tú:</b><br>{prompt}</div>')

        # ID único para la burbuja de respuesta
        id_burbuja = "respuesta-" + str(uuid.uuid4()).replace("-", "")[:8]
        eel.iniciar_respuesta_ai(id_burbuja)
        eel.actualizar_mensaje_estado(obtener_mensaje_estado("escribiendo"), id_burbuja)


        prompt_final = prompt

        # Verificamos si es necesario ejecutar el monitoreo
        if necesita_datos_sistema(prompt):
            eel.actualizar_mensaje_estado(obtener_mensaje_estado("recolectando"), id_burbuja)
            info = system_monitor.monitor_system()
            info_texto = "\n".join([f"{k}:\n{v}" for k, v in info.items()])
            eel.actualizar_mensaje_estado(obtener_mensaje_estado("generando"), id_burbuja)
            prompt_final = f"""🖥️ Información actual del sistema:\n{info_texto}\n\nUsuario: {username}\n\nPregunta del usuario:\n{prompt}"""

        # Inicia el streaming
        stream = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {"role": "system", "content": "Responde siempre en español."},
                {"role": "user", "content": prompt_final}
            ],
            stream=True
        )

        respuesta_raw = ""
        stream_vacio = True

        for chunk in stream:
            if hasattr(chunk.choices[0].delta, "content"):
                nuevo = chunk.choices[0].delta.content
                if nuevo.strip():
                    stream_vacio = False
                respuesta_raw += nuevo
                eel.actualizar_respuesta_ai(convertir_markdown_a_html(respuesta_raw), id_burbuja)

        if stream_vacio:
            eel.actualizar_respuesta_ai('<span style="color:red;">⚠️ No se recibió contenido de la IA. Intenta reformular tu pregunta.</span>', id_burbuja)

        eel.hide_typing_bubble()
        eel.finalizar_respuesta_ai("</div>", id_burbuja)

    except Exception as e:
        mensaje_error = str(e)

        if "quota" in mensaje_error.lower():
            mensaje_amigable = "❌ Has superado tu límite de tokens o cuota en OpenRouter."
        elif "Invalid API key" in mensaje_error or "401" in mensaje_error:
            mensaje_amigable = "❌ Tu clave API de OpenRouter no es válida o ha caducado."
        elif "model" in mensaje_error and "not found" in mensaje_error:
            mensaje_amigable = "❌ El modelo solicitado no está disponible actualmente."
        else:
            mensaje_amigable = f"❌ Error inesperado: {mensaje_error}"

        eel.actualizar_respuesta_ai(f'<span style="color:red;">{mensaje_amigable}</span>', id_burbuja)
        eel.finalizar_respuesta_ai("</div>", id_burbuja)

    return historial


@eel.expose
def obtener_historial():
    return historial

def convertir_markdown_a_html(texto):
    html = markdown.markdown(texto, extensions=["tables"])
    html = re.sub(r"<table>", '<table border="1" cellpadding="8" cellspacing="0" width="100%">', html)
    html = re.sub(r"<th>", '<th bgcolor="#bebcbb"><font color="#000000"><b>', html)
    html = re.sub(r"</th>", '</b></font></th>', html)
    html = re.sub(r"<td>", '<td align="center">', html)
    return html


def get_real_user_name():
    system = platform.system()

    try:
        if system == 'Windows':
            username = getpass.getuser()
            result = subprocess.check_output(
                f'wmic useraccount where name="{username}" get fullname /value',
                shell=True, encoding='utf-8', stderr=subprocess.DEVNULL
            )
            for line in result.strip().splitlines():
                if line.lower().startswith("fullname="):
                    full_name = line.split("=", 1)[1].strip()
                    return full_name if full_name else username
            return username
        elif system in ['Linux', 'Darwin']:
            import pwd
            full_name = pwd.getpwnam(getpass.getuser()).pw_gecos.split(',')[0]
            return full_name if full_name else getpass.getuser()
        else:
            return getpass.getuser()
    except Exception as e:
        return getpass.getuser()

username = get_real_user_name()


# Lanzar la app
eel.init("web")
@eel.expose
def get_username():
    return username

eel.start("index.html", size=(900, 700))