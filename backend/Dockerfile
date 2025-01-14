FROM python:3.12
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . ./backend
COPY ./root.pem ./
CMD ["fastapi", "run", "backend/main.py", "--port", "80", "--proxy-headers", "--workers", "4"]