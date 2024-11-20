FROM python:3.10-alpine3.20

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "surrogate.py"]