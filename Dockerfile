# Usar imagen oficial de Python 3.13 slim
FROM python:3.13-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar Poetry
RUN pip install poetry==1.8.3

# Configurar Poetry para no crear entorno virtual (usar el del contenedor)
RUN poetry config virtualenvs.create false

# Copiar archivos de configuración de Poetry
COPY pyproject.toml poetry.lock ./

# Copiar código fuente
COPY src/ ./src/

# Regenerar lock file si es necesario e instalar dependencias
RUN poetry lock --no-update && poetry install --only=main

# Exponer puerto 8000
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "voxcliente.main:app", "--host", "0.0.0.0", "--port", "8000"]
