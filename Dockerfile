FROM python:latest

WORKDIR /app

RUN [ "mkdir", "db" ]
RUN [ "mkdir", "assets" ]

COPY [ "requirements.txt", "." ]
RUN [ "pip3", "install", "-r", "requirements.txt" ]

COPY [ "src/", "." ]
COPY [ "token", "." ]
COPY [ "epita_pass", "." ]
COPY [ "epita_user", "."]
COPY [ "./db/CMD_MAP", "." ]
COPY [ "./assets/____choffix.png", "." ]

CMD [ "python3", "main.py" ]
