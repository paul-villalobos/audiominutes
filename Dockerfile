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

# Instalar dependencias
RUN poetry install --only=main --no-dev

# Copiar código fuente
COPY src/ ./src/

# Crear directorio para archivos estáticos si no existe
RUN mkdir -p src/voxcliente/static

# Agregar el directorio src al PYTHONPATH
ENV PYTHONPATH=/app/src

# Crear directorio para uploads temporales
RUN mkdir -p /app/uploads && chmod 755 /app/uploads

# Exponer puerto 8000
EXPOSE 8000

# Comando para ejecutar la aplicación con logging detallado
CMD ["uvicorn", "voxcliente.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info", "--access-log"]