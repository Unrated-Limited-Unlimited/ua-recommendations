FROM python:latest

COPY requirements.txt .

COPY src/ .

CMD ["python", "main.py"]

