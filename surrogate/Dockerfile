FROM alpine:3.20.3

WORKDIR /app

COPY . .

# Install Python 3
RUN apk add --update --no-cache python3

RUN apk add --update --no-cache py3-pip

RUN mv /usr/lib/python3.12/EXTERNALLY-MANAGED /usr/lib/python3.12/EXTERNALLY-MANAGED.old

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python", "surrogate.py"]