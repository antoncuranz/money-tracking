FROM python:3.12
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . ./backend
CMD ["gunicorn", "--bind", "0.0.0.0:80", "backend.wsgi"]