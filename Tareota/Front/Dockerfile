# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requisitos e instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto en el que corre Flet (por defecto, Flet usa el puerto 8550)
EXPOSE 8550

# Comando para ejecutar la aplicación Flet
CMD ["python", "mainfront.py"]