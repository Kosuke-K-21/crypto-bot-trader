FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY main.py requirements.txt ./

RUN pip install -r requirements.txt

CMD ["python", "main.py"]