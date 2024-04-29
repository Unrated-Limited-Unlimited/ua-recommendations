FROM python:latest

COPY requirements.txt .

COPY src/ .

# Install psycopg2
RUN apt-get update && apt-get install -y \
    python3-psycopg2

# Install gawk and gcc
RUN apt-get update && apt-get install -y \
    gawk \
    gcc

# Install python3-dev
RUN apt-get update && apt-get install -y \
    python3-dev

# Install libpg-dev
RUN apt-get update && apt-get install -y \
    libpq-dev

RUN apt-get install build-essential libpq-dev python3-psycopg2 gawk gcc python3-dev cmake -y
RUN apt install build-essential libpq-dev python3-psycopg2 gawk gcc python3-dev cmake -y

CMD ["python", "pip" "install" "-r" "requirements.txt"]

CMD ["python", "main.py"]

