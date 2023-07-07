FROM python:3.8

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--reload", "--port", "5000", "--host", "0.0.0.0"]