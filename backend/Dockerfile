FROM python:3.12
WORKDIR /backend
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . ./
CMD ["fastapi", "run", "main.py", "--port", "80", "--proxy-headers"]