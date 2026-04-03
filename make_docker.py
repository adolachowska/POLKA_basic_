# make_docker.py

dockerignore_content = """__pycache__
*.pyc
.venv
venv/
*.db
*.sqlite3
.git
"""

dockerfile_content = """FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y curl gnupg unixodbc-dev apt-transport-https
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

docker_compose_content = """version: '3.8'

services:
  azurite:
    image: mcr.microsoft.com/azure-storage/azurite
    container_name: polka_azurite
    ports:
      - "10000:10000"
    volumes:
      - azurite_data:/data

  api:
    build: .
    container_name: polka_api
    ports:
      - "8000:8000"
    depends_on:
      - azurite
    environment:
      - DATABASE_URL=mssql+pyodbc://xx:xxx@host.docker.internal:1433/polka_db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes

volumes:
  azurite_data:
"""

with open(".dockerignore", "w", encoding="utf-8") as f:
    f.write(dockerignore_content)

with open("Dockerfile", "w", encoding="utf-8") as f:
    f.write(dockerfile_content)

with open("docker-compose.yml", "w", encoding="utf-8") as f:
    f.write(docker_compose_content)

print("✅ Pliki .dockerignore, Dockerfile i docker-compose.yml zostały utworzone pomyślnie!")


import os
print("Docker installing")
os.system("docker-compose up --build")
