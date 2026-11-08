FROM python:3.14-slim

RUN mkdir /app

WORKDIR /app

COPY app.py ./app.py
COPY requirements.txt ./requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["fastapi", "run"]