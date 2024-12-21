FROM python:3.12
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . ./backend
COPY ../root.pem ./
CMD ["gunicorn", "--threads", "2", "--bind", "0.0.0.0:80", "backend.wsgi"]