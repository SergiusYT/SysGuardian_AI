# Usamos Python como base
FROM python:3.11.9

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos todos los archivos del proyecto al contenedor
COPY . .

# Instalamos las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para ejecutar el asistente
CMD ["python", "sysguardian.py"]
