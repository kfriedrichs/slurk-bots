FROM python:3.9

RUN mkdir -p /usr/src/golmibot
WORKDIR /usr/src/golmibot

COPY golmibot/requirements.txt /usr/src/golmibot
RUN pip install --no-cache-dir -r requirements.txt

COPY golmibot /usr/src/golmibot

ENTRYPOINT ["python", "golmibot.py"]