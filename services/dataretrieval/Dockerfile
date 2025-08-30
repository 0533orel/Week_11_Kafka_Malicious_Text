FROM python:3.11-slim
WORKDIR /app
COPY services/dataretrieval/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/dataretrieval /app
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
