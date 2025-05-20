# Dockerfile

FROM python:3.11.9-slim

# Instalar dependencias necesarias para eel con Chromium
RUN apt-get update && apt-get install -y \
    libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libgtk-3-0 libdrm2 libgbm1 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxrandr2 libxcursor1 libxinerama1 libglu1-mesa curl unzip \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Script de inicio
ENTRYPOINT ["bash", "SysGuardianIA.sh"]
