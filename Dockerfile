FROM tiangolo/uvicorn-gunicorn:python3.8

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt --upgrade

COPY ./app /app

RUN python /app/server.py

EXPOSE 5042

CMD ["python", "/app/server.py", "serve"]