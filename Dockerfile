FROM python:latest

WORKDIR /app

RUN [ "mkdir", "db" ]
RUN [ "mkdir", "assets" ]

COPY [ "src/", "." ]
COPY [ "requirements.txt", "." ]
COPY [ "token", "." ]
COPY [ "epita_pass", "." ]
COPY [ "epita_user", "."]
COPY [ "./db/CMD_MAP", "." ]
COPY [ "./assets/____choffix.png", "." ]

RUN [ "pip3", "install", "-r", "requirements.txt" ]

CMD [ "python3", "main.py" ]
