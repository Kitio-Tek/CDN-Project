FROM python:3.12.7-alpine3.20

WORKDIR /app

COPY . .

RUN apk add build-base

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "surrogate.py"]