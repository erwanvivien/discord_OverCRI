FROM python:latest

WORKDIR /app

# RUN mkdir db

COPY [ "src/", "." ]
COPY [ "requirements.txt", "." ]
COPY [ "token", "."]
COPY [ "./db/CMD_MAP", "." ]

RUN pip install -r requirements.txt

CMD [ "python3", "main.py" ]
