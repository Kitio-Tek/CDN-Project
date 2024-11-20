# origin_server/Dockerfile
# Use Python 3.13-slim image
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose necessary ports
EXPOSE 5000 8468

CMD ["python3", "api.py"]
