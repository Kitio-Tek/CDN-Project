# client_app/Dockerfile
# Use Python 3.13-slim image
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y vlc && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# No ports to expose for client_app unless required

CMD ["python3", "request_content.py"]
