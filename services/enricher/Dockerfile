FROM python:3.11-slim
WORKDIR /app
COPY services/enricher/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common /app/common
COPY services/enricher /app
CMD ["python", "app.py"]
