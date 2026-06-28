# Imagen base con Python 3.12
FROM python:3.12-slim

# Evita que Python genere archivos temporales .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Hace que los mensajes de Django aparezcan inmediatamente en la terminal
ENV PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copia primero la lista de dependencias
COPY requirements.txt .

# Actualiza pip e instala las dependencias
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia el proyecto completo dentro del contenedor
COPY . .

# Documenta que Django utilizará el puerto 8000
EXPOSE 8000

# Comando que se ejecutará al iniciar el contenedor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]