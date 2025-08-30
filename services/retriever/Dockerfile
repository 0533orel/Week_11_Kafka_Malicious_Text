FROM python:3.11-slim
WORKDIR /app
COPY services/retriever/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common /app/common
COPY services/retriever /app
# State volume
VOLUME ["/data"]
CMD ["python", "app.py"]
